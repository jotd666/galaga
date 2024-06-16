	* compute d6 index reg from a0 base to reapply
	* to other bases (when only h is loaded)
	.macro	COMPUTE_LSB_A0_D6	base
	move.l	a0,d6
	sub.l	#\base,d6
	.ifndef		RELEASE
	jpl		0f
	move.l	a0,a2
	lea		\base,a1
	lea		compute_lsb_a0_d6_base_mismatch_msg,a0
	jbsr	osd_break
	illegal
0:
	cmp.w	#0x100,d6
	jcs		0f
	move.l	a0,a2
	lea		\base,a1
	lea		compute_lsb_a0_d6_base_mismatch_msg,a0
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
	lea		compute_lsb_a1_d4_base_mismatch_msg,a0
	jbsr	osd_break
	illegal
0:
	cmp.w	#0x100,d4
	jcs		0f
	lea		\base,a2
	lea		compute_lsb_a1_d4_base_mismatch_msg,a0
	jbsr	osd_break
	illegal
0:
	.endif
	.endm

	.macro	COMPUTE_LSB_A2_D0	base
	exg		a3,a2
	COMPUTE_LSB_A3_D0		\base
	exg		a3,a2	
	.endm
	
	.macro	COMPUTE_LSB_A3_D0	base
	move.l	a3,d0
	sub.l	#\base,d0
	.ifndef		RELEASE
	jpl		0f
	lea		\base,a2
	lea		compute_lsb_a3_d0_base_mismatch_msg,a0
	jbsr	osd_break
	illegal
0:
	cmp.w	#0x100,d0
	jcs		0f
	lea		\base,a2
	lea		compute_lsb_a3_d0_base_mismatch_msg,a0
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

	.ifdef	RELEASE
	.macro  CHECK_D0W_UPPER_BOUND	max
	.endm
	.else
	.macro  CHECK_D0W_UPPER_BOUND	max
	cmp.w	#\max,d0
	bcs.b	0f
	lea		check_d0w_upper_bound_error,a1
	move.w	d0,d1
	move.w	#\max,d2
	jbsr	osd_break
	illegal
0:	
	.endm
	.endif
	
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


	
	.ifndef	RELEASE
	.macro	LOG_REGS	z80pc
	move.w	sr,-(a7)
	move.l	a6,-(a7)
	move.l	log_ptr,a6
	move.w	#0x\z80pc,(a6)+
	move.b	d0,(a6)+
	move.b	d1,(a6)+
	move.b	d2,(a6)+
	move.b	d3,(a6)+
	move.b	d4,(a6)+
	move.b	d5,(a6)+
	move.b	d6,(a6)+
	move.b	d7,(a6)+
	move.b	ixh,(a6)+
	move.b	ixl,(a6)+
	move.w	#0xDEAD,(a6)+
	move.l	a6,log_ptr
	move.l	(a7)+,a6
	move.w	(a7)+,sr
	.endm

check_d0w_upper_bound_error:
	.asciz	"jump table index too high D1 >= D2!"
compute_lsb_a0_d6_base_mismatch_msg:
	.asciz	"compute_lsb_a0_d6_base_mismatch"
compute_lsb_a1_d4_base_mismatch_msg:
	.asciz	"compute_lsb_a1_d4_base_mismatch"
compute_lsb_a3_d0_base_mismatch_msg:
	.asciz	"compute_lsb_a3_d0_base_mismatch"
	.endif
	