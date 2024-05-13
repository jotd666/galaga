import os,re,bitplanelib,ast
from PIL import Image,ImageOps

gamename = "galaga"

import collections

# ripped from MAME, Mark version is not correct or I just don't get the logic
ripped_palette = """222,222,222,255
255,0,0,255
255,255,0,255
255,151,0,255
255,184,0,255
255,0,222,255
0,255,222,255
184,184,222,255
222,71,0,255
0,255,0,255
33,151,0,255
0,104,222,255
151,0,222,255
0,0,222,255
0,151,151,255
0,0,0,255
222,222,222,255
255,0,0,255
255,255,0,255
255,151,0,255
0,0,0,255
255,0,222,255
0,255,222,255
0,184,222,255
0,0,0,255
0,255,0,255
0,0,0,255
0,104,222,255
184,0,222,255
0,0,222,255
0,0,0,255
0,0,0,255
""".splitlines()


black = (0,0,0)
# only 1 4 color palette, all rows use 4 colors per row
# those colors can't be found in palette
# we also need to put those colors at specific locations on the 32 color range
# (colors that hardware sprites don't use)
fake_4_color_palette = [(12,12,12)]*32
for i,c in zip([16,20,24],[(0xE0,0,0),(0,0xE0,0),(0,0,0xE0)]):
    fake_4_color_palette[i] = c
fake_4_color_palette[0] = black

index_conv = {0:0,1:24,2:20,3:16}

ST_NONE = 0
ST_BOB = 1
ST_HW_SPRITE = 2


this_dir = os.path.dirname(__file__)
src_dir = os.path.join(this_dir,"../../src/amiga")
dump_dir = os.path.join(this_dir,"dumps")
dump_tiles_dir = os.path.join(dump_dir,"tiles")
dump_palettes_dir = os.path.join(dump_dir,"palettes")
dump_sprites_dir = os.path.join(dump_dir,"sprites")
uncategorized_dump_sprites_dir = os.path.join(dump_sprites_dir,"__uncategorized")
def ensure_empty(sd):
    if os.path.exists(sd):
        for p in os.listdir(sd):
            n = os.path.join(sd,p)
            if os.path.isfile(n):
                os.remove(n)
    else:
        os.mkdir(sd)

dump_tiles = True
dump_sprites = True
dump_palettes = False

if dump_palettes:
    ensure_empty(dump_dir)
    ensure_empty(dump_palettes_dir)

if dump_tiles:
    ensure_empty(dump_dir)
    ensure_empty(dump_tiles_dir)

if dump_sprites:
    ensure_empty(dump_dir)
    ensure_empty(dump_sprites_dir)
    ensure_empty(uncategorized_dump_sprites_dir)


NB_POSSIBLE_SPRITES = 128
NB_BOB_PLANES = 4


def dump_asm_bytes(*args,**kwargs):
    bitplanelib.dump_asm_bytes(*args,**kwargs,mit_format=True)


sprite_config = dict()

def add_sprite_block(start,end,prefix,cluts,sprite_type=ST_BOB,mirror=False,
flip=False):

    if isinstance(cluts,int):
        cluts = [cluts]
    for i in range(start,end):
        if i in sprite_config:
            # merge
            sprite_config[i]["cluts"].extend(cluts)
        else:
            sprite_config[i] = {"name":f"{prefix}_{i:02x}","cluts":cluts,
                                "sprite_type":sprite_type,
                                "mirror":mirror,
                                "flip":flip  # only relevant for HW sprites, else it's handled by blitter
                                }

def add_sprite(code,prefix,cluts,sprite_type=ST_BOB,mirror=False,flip=False):
    add_sprite_block(code,code+1,prefix,cluts,sprite_type,mirror,flip=flip)

add_sprite_block(0x8,0x10,"boss_ship",[0,1,10])   # 10: yellow when about to explode
# I'd like to hack player ship into a sprite only for clut 2
# but use a BOB for clut 9 (captured)
#add_sprite_block(0,0x8,"ship",[2,9])
add_sprite_block(0,0x8,"ship",9) #,sprite_type=ST_HW_SPRITE)
add_sprite_block(0,0x8,"ship",2)
add_sprite_block(0x10,0x18,"red_bee",2)
add_sprite_block(0x18,0x20,"blue_bee",3)
add_sprite_block(0x50,0x57,"mutant_galaxian_boss",4,sprite_type=ST_HW_SPRITE)
add_sprite_block(0x58,0x5F,"mutant_scorpion",5,sprite_type=ST_HW_SPRITE)
add_sprite_block(0x60,0x67,"mutant_green",6,sprite_type=ST_HW_SPRITE)
add_sprite_block(0x68,0x6F,"challenge_butterfly",2) # or 7?
add_sprite_block(0x70,0x77,"challenge_ship",7)
add_sprite_block(0x78,0x7F,"challenge_rocket",7)
add_sprite_block(0x30,0x34,"bomb",[0x9,0xB])
add_sprite(0x34,"score_150",0)  # wrong clut
add_sprite(0x35,"score_400",0)  # wrong clut
add_sprite(0x36,"score_500",0)  # wrong clut
add_sprite(0x37,"score_800",0)  # wrong clut
add_sprite(0x38,"score_1000",0)  # wrong clut
add_sprite(0x39,"score_1500",0)  # wrong clut
add_sprite(0x3A,"score_1600",0)  # wrong clut
add_sprite_block(0x20,0x30,"explosion",0)  # wrong clut


block_dict = {}

# hackish convert of c gfx table to dict of lists
# (Thanks to Mark Mc Dougall for providing the ripped gfx as C tables)
with open(os.path.join(this_dir,"..",f"{gamename}_gfx.c")) as f:
    block = []
    block_name = ""
    start_block = False

    for line in f:
        if "uint8" in line:
            # start group
            start_block = True
            if block:
                txt = "".join(block).strip().strip(";")
                block_dict[block_name] = {"size":size,"data":ast.literal_eval(txt)}
                block = []
            block_name = line.split()[1].split("[")[0]
            try:
                size = int(line.split("[")[-1].split("]")[0])
            except ValueError:
                size = 0
        elif start_block:
            line = re.sub("//.*","",line)
            line = line.replace("{","[").replace("}","]")
            block.append(line)

    if block:
        txt = "".join(block).strip().strip(";")
        block_dict[block_name] = {"size":size,"data":ast.literal_eval(txt)}

### add the fake sprites to be able to switch from sprites to BOBs for barrels
##bd = block_dict["sprite"]["data"]
##
##for i in range(0x15,0x18):
##    bd[i+0x50] = bd[i]

# block_dict structure is as follows:
# dict_keys(['fg_tile', 'sprite', 'palette', 'fg_tile_clut', 'sprite_clut'])

def tile_rgb(x):
    r,b,g = tiles_palette[x]  # in Mark rips, green & blue are swapped, like in some other games (Pengo)
    return (r,g,b)

# palette looks ok for tiles, thanks Mark!!
tiles_palette = [tuple(x) for x in block_dict["palette"]["data"]]
# palette is wrong for sprites. MAME gfxsave to the rescue!
palette = [tuple(int(x) for x in line.split(",")[0:3]) for line in ripped_palette]
sprite_clut = [[tuple(palette[x]) for x in clut] for clut in block_dict["sprite_clut"]["data"]]
fg_tile_clut = [[tile_rgb(x) for x in clut] for clut in block_dict["fg_tile_clut"]["data"]]


def replace_color(img,color,replacement_color):
    rval = Image.new("RGB",img.size)
    for x in range(img.size[0]):
        for y in range(img.size[1]):
            c = (x,y)
            rgb = img.getpixel(c)
            if rgb == color:
                rgb = replacement_color
            rval.putpixel(c,rgb)
    return rval

def swap(a,i,j):
    a[j],a[i] = a[i],a[j]

def get_sprite_clut(clut_index):
    # simple slice of global palette
    rval = sprite_clut[clut_index]

    return rval


# creating the sprite configuration in the code is more flexible than with a config file


bobs_used_colors = collections.Counter()
sprites_used_colors = collections.Counter()
hsize = 16

def generate_16x16_image(cidx,sprdat,sprconf):
    img = Image.new("RGB",(16,hsize))
    spritepal = get_sprite_clut(cidx)

    is_sprite = sprconf and sprconf["sprite_type"] & ST_HW_SPRITE
    d = iter(sprdat)
    for j in range(16):
        for i in range(16):
            v = next(d)
            color = spritepal[v]
            if sprconf:
                (sprites_used_colors if is_sprite else bobs_used_colors)[color] += 1
            img.putpixel((i,j),color)
    return img

def switch_values(t,a,b):
    t[a],t[b] = t[b],t[a]



# if palette is taken as-is, we need 32 colors to display the full game, even less than that
# but using 32 colors has a lot of disadvantages:
# - this is super slow on real hardware! (Smooth on WinUAE but smooth on MAME too...)
# - we can't use hardware sprites properly as there could be palette conflicts

# first pass: compute each level palette knowing the sprites that can be used in it
# and only them. This saves just enough colors to have 4 tile colors (variable)
# and 12 bob colors so we can use only 4 bitplanes (plus hw sprites as bonus colors
# but even without hardware sprites we have enough colors which is really
# a chance!!)


colors = set()
for k,sprdat in enumerate(block_dict["sprite"]["data"]):
    sprconf = sprite_config.get(k)
    if sprconf:
        is_sprite = sprconf["sprite_type"] == ST_HW_SPRITE  # pure hardware sprite!
        if not is_sprite:
            clut_range = sprconf["cluts"]
            name = sprconf["name"]
            for clut in clut_range:
                img = generate_16x16_image(clut,sprdat,sprconf)
                for x in range(img.size[0]):
                    for y in range(img.size[1]):
                        colors.add(img.getpixel((x,y)))

# rebuild the reduced palette from used sprites (& tiles!). Should not exceed 16
# ATM we have 6 spare colors and we could probably gain more with dynamic copper shit for tiles
# if required
palette = sorted(colors)

palette = palette + [(0x10,0x20,0x30)]*(16-len(palette))



# dump cluts as RGB4 for sprites
with open(os.path.join(src_dir,"palette_cluts.68k"),"w") as f:
    for clut_index in range(16):
        clut = get_sprite_clut(clut_index)   # simple slice of palette
##        if clut_index==3:
##            # kludge for moving ladders (clut looks wrong and ladders are green)
##            clut[3] = (255,255,255)
##            clut[1] = (0xe0,0x30,0x90) #,0x0800,0x01ff
        rgb4 = [bitplanelib.to_rgb4_color(x) for x in clut]
        bitplanelib.dump_asm_bytes(rgb4,f,mit_format=True,size=2)




with open(os.path.join(src_dir,"palette.68k"),"w") as f:
    f.write("palette:\n")
    bitplanelib.palette_dump(palette,f,pformat=bitplanelib.PALETTE_FORMAT_ASMGNU)
with open(os.path.join(src_dir,"tile_cluts.68k"),"w") as f:

    for c in fg_tile_clut:
        bitplanelib.palette_dump(c,f,pformat=bitplanelib.PALETTE_FORMAT_ASMGNU)

bitplanelib.palette_dump(palette,os.path.join(dump_dir,"colors.png"),pformat=bitplanelib.PALETTE_FORMAT_PNG)

tile_plane_cache = {bytes(8):0}  # so empty line has index 0

character_codes = []
tile_index = 1

if True:
    for k,chardat in enumerate(block_dict["fg_tile"]["data"]):
        if k==128:
            break   # no need for symmetry, cocktail mode crap
        img = Image.new('RGB',(8,8))

        d = iter(chardat)
        for i in range(8):
            for j in range(8):
                v = index_conv[next(d)]   # 0-3 to real index in 32 color palette
                img.putpixel((j,i),fake_4_color_palette[v])
        data = bitplanelib.palette_image2raw(img,None,fake_4_color_palette)
        chunk_len,remainder = divmod(len(data),5)
        if remainder:
            raise Exception("tile bitmap not a multiple of 5!")

        plane_list = []
        for i in range(0,len(data),chunk_len):
            plane = data[i:i+chunk_len]
            idx = tile_plane_cache.get(plane)
            if idx is None:
                idx = tile_index
                tile_plane_cache[plane] = tile_index
                tile_index += 1
            plane_list.append(idx)

        character_codes.append(plane_list)

        if dump_tiles:
            scaled = ImageOps.scale(img,5,0)
            scaled.save(os.path.join(dump_tiles_dir,f"char_{k:02x}.png"))



sprites = dict()
bitplane_cache = dict()
plane_next_index = 0

if True:
    for k,sprdat in enumerate(block_dict["sprite"]["data"]):
        sprconf = sprite_config.get(k)
        if sprconf:
            clut_range = sprconf["cluts"]
            name = sprconf["name"]
            sprite_type = sprconf["sprite_type"]
        else:
            clut_range = [0]
            name = f"unknown_{k:02x}"
            sprite_type = ST_NONE
            continue

        for cidx in clut_range:
            img = generate_16x16_image(cidx,sprdat,sprconf)
            if dump_sprites:
                scaled = ImageOps.scale(img,2,0)
                if sprconf:
                    scaled.save(os.path.join(dump_sprites_dir,f"{name}_{cidx}.png"))
                else:
                    scaled.save(os.path.join(uncategorized_dump_sprites_dir,f"sprites_{k:02x}_{cidx}.png"))

            # only consider sprites/cluts which are pre-registered
            if sprconf:
                if k not in sprites:
                    sprites[k] = {"sprite_type":sprite_type,"name":name,"hsize":hsize,
                    "mirror":sprconf["mirror"],"flip":sprconf["flip"]}

                cs = sprites[k]

                if sprconf["sprite_type"] & ST_HW_SPRITE:
                    # hardware sprites only need one bitmap data, copied 8 times to be able
                    # to be assigned several times. Doesn't happen a lot in this game for now
                    # but at least wheels have more than 1 instance
                    if "sprmap" not in cs:
                        # create entry only if not already created (multiple cluts)
                        # we must not introduce a all black or missing colors palette in here
                        # (even if the CLUT may be used for this sprite) else base image will miss colors!
                        #
                        # example: pengo all-black enemies. If this case occurs, just omit this dummy config
                        # the amiga engine will manage anyway
                        #

                        spritepal = get_sprite_clut(cidx)

                        cs["sprmap"] = [bitplanelib.palette_image2sprite(img,None,spritepal,
                                 palette_precision_mask=0xFF,sprite_fmode=0,with_control_words=True)]

                        if cs["mirror"]:
                            # we need do re-iterate with opposite Y-flip image (donkey kong)
                            cs["sprmap"].append(bitplanelib.palette_image2sprite(ImageOps.mirror(img),None,spritepal,
                             palette_precision_mask=0xFF,sprite_fmode=0,with_control_words=True))
                        else:
                            cs["sprmap"].append(None)
                        if cs["flip"]:
                            # we need do re-iterate with opposite Y-flip image (donkey kong)
                            flipped = ImageOps.flip(img)
                            cs["sprmap"].append(bitplanelib.palette_image2sprite(flipped,None,spritepal,
                             palette_precision_mask=0xFF,sprite_fmode=0,with_control_words=True))
                            cs["sprmap"].append(bitplanelib.palette_image2sprite(ImageOps.mirror(flipped),None,spritepal,
                             palette_precision_mask=0xFF,sprite_fmode=0,with_control_words=True))


                if sprconf["sprite_type"] & ST_BOB:
                    # software sprites (bobs) need one copy of bitmaps per palette setup. There are 3 or 4 planes
                    # (4 ATM but will switch to dual playfield)
                    # but not all planes are active as game sprites have max 3 colors (+ transparent)
                    if "bitmap" not in cs:
                        cs["bitmap"] = dict()

                    bobs_palette = palette  # take first palette even if several screens
                    csb = cs["bitmap"]

                    # prior to dump the image to amiga bitplanes, don't forget to replace brown by blue
                    # as we forcefully removed it from the palette to make it fit to 16 colors, don't worry, the
                    # copper will put the proper color back again
                    img_to_raw = img

                    plane_list = []
                    print(f"converting {name}, code {k}, clut {cidx}, {[[hex(c) for c in x]for x in sprite_clut[cidx] ]}")

                    for mirrored in range(2):
                        bitplanes = bitplanelib.palette_image2raw(img_to_raw,None,bobs_palette,forced_nb_planes=NB_BOB_PLANES,
                            palette_precision_mask=0xFF,generate_mask=True,blit_pad=True)
                        bitplane_size = len(bitplanes)//(NB_BOB_PLANES+1)  # don't forget bob mask!


                        for ci in range(0,len(bitplanes),bitplane_size):
                            plane = bitplanes[ci:ci+bitplane_size]
                            if not any(plane):
                                # only zeroes: null pointer so engine is able to optimize
                                # by not reading the zeroed data
                                plane_list.append(None)
                            else:
                                plane_index = bitplane_cache.get(plane)
                                if plane_index is None:
                                    bitplane_cache[plane] = plane_next_index
                                    plane_index = plane_next_index
                                    plane_next_index += 1
                                plane_list.append(plane_index)
                        if cs["mirror"] and mirrored==0:
                            # we need do re-iterate with opposite Y-flip image (donkey kong)
                            img_to_raw = ImageOps.mirror(img_to_raw)
                        else:
                            # no mirror: don't do it once more
                            break

                    # plane list size varies depending on mirror or not
                    # we allow to mask as only in some special cases there are clut indexes > 16
                    # (but seen as masked in sprite dumps. Never mind, we can make them look correct
                    # just by masking after having used the proper CLUT when creating the bitmap)
                    # all sprites have a clut under 0x10
                    # except for those 2 (which conveniently are sprites!)
                    # - moving ladder: seems to be 0x13
                    # - elevator: seems to be 0x23

                    csb[cidx] = plane_list


hw_sprite_flag = [0]*256
for k,v in sprite_config.items():
    sprite_type = v["sprite_type"]
    if sprite_type & ST_HW_SPRITE:
        hw_sprite_flag[k] = 1
        hw_sprite_flag[k+128] = 1
    elif sprite_type == ST_NONE:
        hw_sprite_flag[k] = 255
        hw_sprite_flag[k+128] = 255  # mirror code



with open(os.path.join(src_dir,"graphics.68k"),"w") as f:
    f.write("\t.global\tcharacter_table\n")
    f.write("\t.global\tsprite_table\n")
    f.write("\t.global\tbob_table\n")
    f.write("\t.global\thardware_sprite_flag_table\n")
    f.write("\t.global\tfour_barrels_bitmap\n")

    f.write("\nhardware_sprite_flag_table:")
    bitplanelib.dump_asm_bytes(hw_sprite_flag,f,mit_format=True)

    f.write("\ncharacter_table:\n")
    for i,_ in enumerate(character_codes):
        f.write(f"\t.long\tchar_{i}\n")

    for i,plane_list in enumerate(character_codes):
        # now find the last (first) zero plane
        for j,p in enumerate(plane_list):
            if p:
                break
            else:
                plane_list[j] = -1   # no more non-empty bitplanes

        f.write(f"char_{i}:\n")
        for p in reversed(plane_list):
            f.write("\t.long\t")
            if p == 0 or p == -1:
                f.write(str(p))
            else:
                f.write(f"tile_plane_{p}")
            f.write("\n")

        #
    tile_plane_cache.pop(bytes(8))  # array of zeroes isn't referenced

    for k,idx in tile_plane_cache.items():
        f.write(f"tile_plane_{idx}:")
        bitplanelib.dump_asm_bytes(k,f,mit_format=True)

    f.write("sprite_table:\n")

    # hardware sprites
    sprite_names = [None]*NB_POSSIBLE_SPRITES
    for i in range(NB_POSSIBLE_SPRITES):
        sprite = sprites.get(i)
        f.write("\t.long\t")
        if sprite:
            if sprite == True:
                f.write("-1")  # not displayed but legal
            else:
                if sprite["sprite_type"] & ST_HW_SPRITE:
                    name = sprite['name']
                    sprite_names[i] = name
                    f.write(name+"_spr")
                else:
                    f.write("0")
        else:
            f.write("0")
        f.write("\n")

    for i in range(NB_POSSIBLE_SPRITES):
        name = sprite_names[i]
        if name:
            f.write(f"{name}_spr:\n")
            for j in range(8):
                f.write("\t.long\t")
                f.write(f"{name}_spr_{j}")
                f.write("\n")

    f.write("bob_table:\n")

    bob_names = [None]*NB_POSSIBLE_SPRITES
    for i in range(NB_POSSIBLE_SPRITES):
        sprite = sprites.get(i)
        f.write("\t.long\t")
        if sprite:
            if sprite == True or not sprite["sprite_type"] & ST_BOB:
                f.write("-1")  # hardware sprite or blank: ignore
            else:
                name = sprite["name"]
                bob_names[i] = name
                f.write(name)

        else:
            f.write("0")
        f.write("\n")

    for i in range(NB_POSSIBLE_SPRITES):
        name = bob_names[i]
        if name:
            sprite = sprites.get(i)
            f.write(f"{name}:\n")
            csb = sprite["bitmap"]

            for j in range(16):
                b = csb.get(j)
                f.write("\t.long\t")
                if b:
                    f.write(f"{name}_{j}")
                else:
                    f.write("0")   # clut not active
                f.write("\n")

    # blitter objects (bitplanes refs, can be in fastmem)
    for i in range(NB_POSSIBLE_SPRITES):
        name = bob_names[i]
        if name:
            sprite = sprites.get(i)
            bitmap = sprite["bitmap"]
            for j in range(16):
                bm = bitmap.get(j)
                if bm:
                    sprite_label = f"{name}_{j}"
                    f.write(f"{sprite_label}:\n")
                    for plane_id in bm:
                        f.write("\t.long\t")
                        if plane_id is None:
                            f.write("0")
                        else:
                            f.write(f"plane_{plane_id}")
                        f.write("\n")

    # hardware sprites
    sprite_flip_type = ["normal","mirrored","flipped","flipped_mirrored"]
    for i in range(NB_POSSIBLE_SPRITES):
        name = sprite_names[i]
        if name:
            sprite = sprites.get(i)
            for j in range(8):
                # clut is valid for this sprite
                bitmap = sprite["sprmap"]
                sprite_label = f"{name}_spr_{j}"
                f.write(f"{sprite_label}:\n")  # all sprites are of height 16 in this game
                sprite["sprmap"] = bitmap + [None]*(4-len(bitmap))

                for i,bm in zip(sprite_flip_type,sprite["sprmap"]):
                    if bm:
                        f.write(f"\t.long\t{sprite_label}_{i}\n")
                    else:
                        f.write(f"\t.long\t0\n")




    f.write("\n\t.section\t.datachip\n\n")



    # sprites
    for i in range(NB_POSSIBLE_SPRITES):
        name = sprite_names[i]
        if name:
            sprite = sprites.get(i)
            for j in range(8):
                # clut is valid for this sprite
                bitmap = sprite["sprmap"]
                sprite_label = f"{name}_spr_{j}"
                for i,bm in zip(sprite_flip_type,bitmap):
                    if bm:
                        f.write(f"{sprite_label}_{i}:")
                        bitplanelib.dump_asm_bytes(bm,f,mit_format=True)

    f.write("\n* bitplanes\n")
    # dump bitplanes
    for k,v in bitplane_cache.items():
        f.write(f"plane_{v}:")
        bitplanelib.dump_asm_bytes(k,f,mit_format=True)
