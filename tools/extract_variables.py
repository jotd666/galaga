import re,sys,os
import simpleeval
import csv

this_dir = os.path.abspath(os.path.dirname(__file__))
addr_re = "\$[0-9A-F]{4}"
min_ram = 0x8000
max_ram = 0x8FF2

var_dict = {}
comment_re = ";.*"
var_re = "\w+_[0-9A-F]{4}"
missing = 0
anon = set()

current_ram = min_ram

missing_offset = []
variables = []

label_re = re.compile("(\w+):")
skip_re = re.compile("\s+\.skip\s+(\S[^\|]+)")
with open(os.path.join(this_dir,os.pardir,"src","galaga_game_ram.68k"),"r") as f:
    for i,line in enumerate(f,1):
        m = label_re.match(line)
        if m:
            # extract offset from name if possible
            label = m.group(1)
            variables.append(label)

            m = re.match("\w+_([0-9a-fA-F]{4})$",label)
            if m:
                offset = m.group(1)
                label_address = int(offset,16)
                if current_ram != label_address:
                    print(f"*** Label {label} not at address {current_ram:04x} : {label_address:04x}")
                    break
            else:
                print(f"label {label}: no offset")
                offset_suffix = f"_{current_ram:04x}"
                newlabel = re.sub(offset_suffix,"",label,flags=re.I)+offset_suffix
                missing_offset.append((label,newlabel))

        else:
            m = skip_re.match(line)
            if m:
                skip_value = m.group(1)
                size = simpleeval.simple_eval(skip_value)
                #print(f"line: {i}, RAM: {current_ram:04x}, size: {size:04x}")
                current_ram += size

if missing_offset:
    print("dumping variables with missing offsets...")
    with open("replacer.csv","w",newline="") as f:
        csv.writer(f,delimiter=";").writerows(missing_offset)
else:
    with open("variables.csv","w",newline="") as f:
        csv.writer(f,delimiter=";").writerows([v] for v in variables)
