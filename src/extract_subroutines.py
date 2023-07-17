import re,sys,os,collections

this_dir = os.path.abspath(os.path.dirname(__file__))
addr_re = "call.*\$([0-9A-F]{4})"
comment_re = ";.*"
calls = collections.Counter()

with open(os.path.join(this_dir,"galaga_z80.asm")) as f:
    for line in f:
        line = re.sub(comment_re,"",line)
        occs = re.findall(addr_re,line)
        if occs:
            for o in occs:
                calls[o] += 1

print(calls)