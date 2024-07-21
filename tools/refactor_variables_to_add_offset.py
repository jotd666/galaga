
import csv,re,os
with open("variables.csv","r",newline="") as f:
    variables = {x[0] for x in csv.reader(f,delimiter=";")}


def f_add_offset(m):
    v = m.group(1)
    if v in variables:
        return f"o_{v}(a6)"
    else:
        return v

##for source in ["galaga.68k","galaga_sub.68k"]:
##    with open(os.path.join("../src",source)) as f:
##        contents = f.read()
##    contents = re.sub(r"\b(\w+)\b",f_add_offset,contents)
##    with open(os.path.join("../src",source),"w") as f:
##        f.write(contents)

with open(os.path.join("../src","variables.inc"),"w") as f:
    for v in sorted(variables,key=lambda x:x[-4:]):
        offset = int(re.match("\w+_(\w{4})",v).group(1),16)
        f.write(f"o_{v} = 0x{offset-0x8000:04x}\n")