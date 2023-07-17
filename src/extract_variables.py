import re,sys,os

this_dir = os.path.abspath(os.path.dirname(__file__))
addr_re = "\$[0-9A-F]{4}"
min_ram = 0x8800
max_ram = 0x8FF2

var_dict = {}
comment_re = ";.*"
var_re = "\w+_[0-9A-F]{4}"
missing = 0
anon = set()

with open(os.path.join(this_dir,"pengo_z80.asm"),"rb") as f:
    for line in f:
        line = line.decode(errors="ignore")
        line = re.sub(comment_re,"",line)
        occs = re.findall(addr_re,line)
        for o in occs:
            oval = int(o[1:],16)
            if min_ram <= oval < max_ram:
                # ram
                if oval not in anon:
                    anon.add(oval)
        occs = re.findall(var_re,line)
        for o in occs:
            oval = int(o[-4:],16)
            if min_ram <= oval < max_ram:
                var_dict[oval] = o




with open(os.path.join(this_dir,"pengo_game_ram.68k"),"w") as f:
    prev_address = None

    for address,name in sorted(var_dict.items()):
        f.write(f"\t.global\t{name}\n")
    f.write("\n")
    for address,name in sorted(var_dict.items()):
        if prev_address is not None:
            size = address-prev_address
            f.write(f"\tds.b\t0x{size:02x}\n")
        # write label
        f.write(f"{name}:\n")

        prev_address = address

    size = max_ram-prev_address
    f.write(f"\tds.b\t0x{size:02x}\n")

print(f"{len(anon)} anonymous vars")
print([f"${x:04x}" for x in sorted(anon)])
