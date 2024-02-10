# run that to create mockup of real screen with a MAME memory dump.
# run "convert_graphics.py" first with "dump" switches at True so "dumps" directory
# is not empty

import bitplanelib

import os
from PIL import Image

tile={}

def add_sprite_block(start,end,name,cluts,*args,**kwargs):
    for i in range(start,end):
        add_sprite(i,name,cluts,*args,**kwargs)
def add_sprite(start,name,cluts,*args,**kwargs):
    tile[start] = name

ST_HW_SPRITE=0

add_sprite_block(0x8,0x10,"boss_ship",[0,1])
# I'd like to hack player ship into a sprite only for clut 2
# but use a BOB for clut 9 (captured)
add_sprite_block(0,0x8,"ship",[2,9])
add_sprite_block(0x10,0x18,"red_bee",2)
add_sprite_block(0x18,0x20,"blue_bee",3)
add_sprite_block(0x50,0x57,"mutant_galaxian_boss",4,sprite_type=ST_HW_SPRITE)
add_sprite_block(0x58,0x5F,"mutant_scorpion",5,sprite_type=ST_HW_SPRITE)
add_sprite_block(0x60,0x67,"mutant_green",6,sprite_type=ST_HW_SPRITE)
add_sprite_block(0x68,0x6F,"challenge_butterfly",2) # or 7?
add_sprite_block(0x70,0x77,"challenge_ship",7)
add_sprite_block(0x78,0x7F,"challenge_rocket",7)
add_sprite_block(0x30,0x34,"bomb",0)  # wrong clut
add_sprite(0x34,"score_150",0)  # wrong clut
add_sprite(0x35,"score_400",0)  # wrong clut
add_sprite(0x36,"score_500",0)  # wrong clut
add_sprite(0x37,"score_800",0)  # wrong clut
add_sprite(0x38,"score_1000",0)  # wrong clut
add_sprite(0x39,"score_1500",0)  # wrong clut
add_sprite(0x3A,"score_1600",0)  # wrong clut
add_sprite_block(0x20,0x30,"explosion",0)  # wrong clut

with open("galaga_dump","rb") as f:  # memory 0=>9000
    contents = f.read()

##        int sx = spriteram_2[offs + 1] - 40 + 0x100*(spriteram_3[offs + 1] & 3);
##        int sy = 256 - spriteram_2[offs] + 1;   // sprites are buffered and delayed by one scanline
##        int flipx = (spriteram_3[offs] & 0x01);
##        int flipy = (spriteram_3[offs] & 0x02) >> 1;
# 64 sprites!

imgcache = dict()

background = Image.new("RGB",(240*2,288*2))

spriteram = contents[0x8B80:0x8B80+0x80]
spriteram_2 = contents[0x9380:0x9380+0x80]
spriteram_3 = contents[0x9b80:0x9b80+0x80]

table_name = ["codes","coords","coords_size"]
with open("../../src/amiga/sprites_conf.68k","w") as f:
    for i,sr in enumerate([spriteram,spriteram_2,spriteram_3]):
        f.write(f"sprconf_{table_name[i]}:")
        bitplanelib.dump_asm_bytes(sr,f,mit_format=True)

for offs in range(0,0x80,2):
    sprite = spriteram[offs] & 0x7f
    color = spriteram[offs + 1] & 0x3f
    sx = spriteram_2[offs + 1] - 40 + 0x100*(spriteram_3[offs + 1] & 3)
    sy = 256 - spriteram_2[offs] + 1  # sprites are buffered and delayed by one scanline
    flipx = (spriteram_3[offs] & 0x01)
    flipy = (spriteram_3[offs] & 0x02) >> 1
    sizex = (spriteram_3[offs] & 0x04) >> 2
    sizey = (spriteram_3[offs] & 0x08) >> 3

    sy -= 16 * sizey
    sy = (sy & 0xff) - 32  # fix wraparound

    ar = (sx,sy,sprite,color)
    if sx > 0 and sy > 0:
        sx,sy = sy,sx
        print("offset=",hex(offs),sx,sy,tile.get(sprite,"")+"_0x{:x}".format(sprite),color,flipy,flipx)
        pic_name = tile.get(sprite,"")+"_{:02x}_{}.png".format(sprite,color)
        pic_path = os.path.join("dumps/sprites",pic_name)
        img = imgcache.get(pic_path)
        if not img:
            img = Image.open(pic_path)
            imgcache[pic_path] = img

        background.paste(img,(sx*2,sy*2))

background.save("out.png")