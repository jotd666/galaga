import os,re
import collections

instruction_re = re.compile("(\w{4}): (.*)")

pcs = collections.Counter()



# generated using log:     trace galaga.tr
# note: sub cpu log has a bug: trace won't consider tracelog instruction if "sub" is specified. So instead, break into subcpu
# then use trace on current cpu
lst = []
print("reading MAME trace file...")
with open(r"K:\Emulation\MAME\galaga.tr","r") as f:
    nb_inst = 0
    for line in f:
        m = instruction_re.match(line)
        if m:
            nb_inst += 1
            pcs[m.groups()] += 1
