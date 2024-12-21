* register operations that are private to each cpu

* < all registers d1-d4/a0/a1/a4
* > all registers swapped
*: note regscopy must be defined somewhere in RAM
*: with a size of 56
exx:
	move.l	a6,-(a7)
    lea     regscopy+28,a6
    * save current regs in region 1
    movem.l d1-d4/a0/a1/a4,-(a6)
    * restore old regs from region 2
    lea     regscopy+28,a6
    movem.l (a6),d1-d4/a0/a1/a4
    * now copy region 1 to region 2
    movem.l d1-d4/a0/a1/a4,-(a7)
    lea     regscopy,a6
    movem.l (a6)+,d1-d4/a0/a1/a4
    movem.l d1-d4/a0/a1/a4,(a6)
    movem.l (a7)+,d1-d4/a0/a1/a4
	move.l	(a7)+,a6
    rts

* ixl is used as an extra register most of the time
* (unrelated to setting lower byte of ix)
* this routine makes sure word value can be safely added

	.macro	READ_IXL_INTO_D0
	moveq	#0,d0
	move.b	ixl,d0
	.endm
	
	.macro	READ_IXH_INTO_D0
	moveq	#0,d0
	move.b	ixh,d0
	.endm
	
	.ifndef   __amiga__
	.bss
	.endif

regscopy:	
	ds.b	64
	
* fake IXH register
ix:
ixh:
	.byte	0
ixl:
	.byte	0
	