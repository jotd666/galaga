	* compute d6 index reg from a0 base to reapply
	* to other bases (when only h is loaded)
	.macro	COMPUTE_LSB_A0_D6	base
	move.l	a0,d6
	sub.l	#\base,d6
	.ifndef		RELEASE
	jpl		0f
	lea		\base,a1
	jbsr	osd_break
	illegal
0:
	cmp.w	#0x100,d6
	jcs		0f
	lea		\base,a2
	jbsr	osd_break
	illegal
0:
	.endif
	.endm

	.macro	COMPUTE_LSB_A1_D4	base
	move.l	a1,d4
	sub.l	#\base,d4
	.ifndef		RELEASE
	jpl		0f
	lea		\base,a2
	jbsr	osd_break
	illegal
0:
	cmp.w	#0x100,d4
	jcs		0f
	lea		\base,a2
	jbsr	osd_break
	illegal
0:
	.endif
	.endm

	* read register to var, little endian
	.macro	MOVE_TO_VAR	reg,var
	move.b	\reg,\var
	ror.w	#8,\reg
	move.b	\reg,\var+1
	ror.w	#8,\reg	
	.endm
	
	* read var to register, little endian
	.macro	MOVE_TO_REG	var,reg
	move.b	\var+1,\reg	
	ror.w	#8,\reg
	move.b	\var,\reg
	.endm
	
	.macro CLEAR_XC_FLAGS
	move.w	d7,-(a7)
	moveq	#0,d7
	roxl.b	#1,d7
	movem.w	(a7)+,d7
	.endm
	.macro SET_XC_FLAGS
	move.w	d7,-(a7)
	st	d7
	roxl.b	#1,d7
	movem.w	(a7)+,d7
	.endm
	.macro	INVERT_XC_FLAGS
	jcs	0f
	SET_XC_FLAGS
	bra.b	1f
0:
	CLEAR_XC_FLAGS
1:
	.endm
	.macro	SET_X_FROM_C
	jcc	0f
	SET_XC_FLAGS
	bra.b	1f
0:
	CLEAR_XC_FLAGS
1:
	.endm

	
	.macro	SET_C_FROM_X
	move.w	d7,-(a7)
	roxl.b	#1,d7
	roxr.b	#1,d7
	movem.w	(a7)+,d7
    .endm


	.macro	LOAD_D1_16_FROM_D1D2
	and.l	#0xFFFF,d1
	lsl.w	#8,d1
	move.b	d2,d1
	.endm
	
	.macro	LOAD_D3_16_FROM_D3D4
	and.l	#0xFFFF,d3
	lsl.w	#8,d3
	move.b	d4,d3
	.endm
	.macro	LOAD_D5_16_FROM_D5D6
	and.l	#0xFFFF,d5
	lsl.w	#8,d5
	move.b	d6,d5
	.endm
	.macro	LOAD_D1D2_FROM_D1_16
	move.b	d1,d2
	lsr.w	#8,d1
	.endm
	.macro	LOAD_D5D6_FROM_D5_16
	move.b	d5,d6
	lsr.w	#8,d5
	.endm
	.macro	LOAD_D3D4_FROM_D3_16
	move.b	d3,d4
	lsr.w	#8,d3
	.endm
