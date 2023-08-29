with open("src/galaga.68k") as f:
    prev = False
    for i,line in enumerate(f):
        if "clr." in line or "move." in line:
            prev = True
            prev_line = line
        elif prev:
            prev = False
            if line.startswith(("\tj","\tb")):
                if all(x not in line for x in ("btst","bset","bchg","bclr","bra","jra","bsr","jbsr")):
                    print(i,prev_line,line)