import os,struct

# save log like S log $100 $4000
with open(r"C:\Users\Public\Documents\Amiga Files\WinUAE\log","rb") as f:
    contents = f.read()

pcs = set()
# generated using LOG_REGS
"""
    .macro    LOG_REGS    z80pc
    move.w    sr,-(a7)
    move.l    a6,-(a7)
    move.l    log_ptr,a6
    move.w    #\z80pc,(a6)+
    move.b    d0,(a6)+
    move.b    d1,(a6)+
    move.b    d2,(a6)+
    move.b    d3,(a6)+
    move.b    d4,(a6)+
    move.b    d5,(a6)+
    move.b    d6,(a6)+
    move.b    d7,(a6)+
    move.w    #0xDEAD,(a6)+
    move.l    a6,log_ptr
    move.l    (a7)+,a6
    move.w    (a7)+,sr
    .endm
"""

len_block = 12

with open("amiga.tr","w") as f:
    for i in range(0,len(contents),len_block):
        chunk = contents[i:i+len_block]
        if len(chunk)<len_block:
            break
        pc,a,b,c,d,e,h,l,d7,end = struct.unpack_from(">HBBBBBBBBH",chunk)
        if end==0xCCCC:
            break
        pcs.add(pc)
        out = f"{pc:04X}: A={a:02X}, B={b:02X}, C={c:02X}, D={d:02X}, E={e:02X}, H={h:02X}, L={l:02X}\n"
        f.write(out)

# generated using log: trace galaga.tr,sub,,{tracelog "A=%02X, B=%02X, C=%02X, D=%02X, E=%02X, H=%02X, L=%02X, IX=%04X ",a,b,c,d,e,h,l,ix}

with open(r"K:\Emulation\MAME\galaga.tr") as f, open("mame.tr","w") as fw:
    l = len("A=01, B=00, C=3F, D=93, E=81, H=93, L=01, ")
    for line in f:
        if line.startswith("A="):
            pc = line[l+8:l+12]
            if int(pc,16) in pcs:
                rest = line[:l-2]
                fw.write(f"{pc}: {rest}\n")