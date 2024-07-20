
import csv,re
with open("replacer.csv","r",newline="") as f:
    rows = dict(csv.reader(f,delimiter=";"))

for source in ["galaga.68k","galaga_sub.68k","amiga/amiga.68k","galaga_game_ram.68k"]:
    with open(source) as f:
        contents = f.read()
    contents = re.sub(r"\b(\w+)\b",lambda m:rows.get(m.group(1),m.group(1)),contents)
    with open(source,"w") as f:
        f.write(contents)
