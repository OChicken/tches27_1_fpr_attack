
build-stm32f4/obj/fpr.o:     file format elf32-littlearm


Disassembly of section .text.FPR:

Disassembly of section .text.fpr_trunc:

Disassembly of section .text.PQCLEAN_FALCON512_CLEAN_fpr_scaled:

Disassembly of section .text.PQCLEAN_FALCON512_CLEAN_fpr_add:

Disassembly of section .text.PQCLEAN_FALCON512_CLEAN_fpr_mul:

00000000 <PQCLEAN_FALCON512_CLEAN_fpr_mul>:
   0:	push	{r4, r5, r6, r7, lr}
   2:	mov	r5, r1
   4:	ubfx	r1, r1, #0, #20
   8:	mov	r6, r3
   a:	orr.w	r1, r1, #1048576	@ 0x100000
   e:	lsrs	r7, r0, #25
  10:	ubfx	r3, r3, #0, #20
  14:	orr.w	r7, r7, r1, lsl #7
  18:	orr.w	r3, r3, #1048576	@ 0x100000
  1c:	lsrs	r1, r2, #25
  1e:	bic.w	r0, r0, #4261412864	@ 0xfe000000
  22:	bic.w	r2, r2, #4261412864	@ 0xfe000000
  26:	orr.w	r1, r1, r3, lsl #7
  2a:	umull	ip, r3, r0, r2
  2e:	mov.w	lr, ip, lsr #25
  32:	umull	r4, r0, r1, r0
  36:	orr.w	lr, lr, r3, lsl #7
  3a:	bic.w	r3, r4, #4261412864	@ 0xfe000000
  3e:	add	r3, lr
  40:	lsrs	r4, r4, #25
  42:	umull	r2, lr, r7, r2
  46:	orr.w	r4, r4, r0, lsl #7
  4a:	bic.w	r0, r2, #4261412864	@ 0xfe000000
  4e:	lsrs	r2, r2, #25
  50:	add	r0, r3
  52:	orr.w	r2, r2, lr, lsl #7
  56:	add	r4, r2
  58:	orr.w	r2, r0, ip
  5c:	bic.w	r2, r2, #4261412864	@ 0xfe000000
  60:	add.w	r4, r4, r0, lsr #25
  64:	mov.w	lr, #0
  68:	add.w	r2, r2, #33554432	@ 0x2000000
  6c:	umlal	r4, lr, r7, r1
  70:	subs	r2, #1
  72:	orr.w	r3, r4, r2, lsr #25
  76:	lsrs	r4, r4, #1
  78:	orr.w	r4, r4, lr, lsl #31
  7c:	and.w	r1, r3, #1
  80:	orrs	r4, r1
  82:	ubfx	r0, r6, #20, #11
  86:	mov.w	r2, lr, lsr #1
  8a:	tst.w	lr, #8388608	@ 0x800000
  8e:	ubfx	r1, r5, #20, #11
  92:	mov.w	r7, lr, lsr #23
  96:	ite	eq
  98:	moveq	r4, r3
  9a:	movne	lr, r2
  9c:	addw	r3, r1, #2047	@ 0x7ff
  a0:	addw	r2, r0, #2047	@ 0x7ff
  a4:	ands	r3, r2
  a6:	asrs	r2, r3, #11
  a8:	mul.w	lr, r2, lr
  ac:	asrs	r3, r3, #31
  ae:	add	r1, r0
  b0:	mla	lr, r4, r3, lr
  b4:	eor.w	r0, r5, r6
  b8:	umull	r2, r3, r2, r4
  bc:	subw	r1, r1, #2100	@ 0x834
  c0:	add	r3, lr
  c2:	add	r1, r7
  c4:	lsrs	r0, r0, #31
  c6:	ldmia.w	sp!, {r4, r5, r6, r7, lr}
  ca:	b.w	0 <PQCLEAN_FALCON512_CLEAN_fpr_mul>

Disassembly of section .text.PQCLEAN_FALCON512_CLEAN_fpr_div:

Disassembly of section .text.PQCLEAN_FALCON512_CLEAN_fpr_sqrt:

Disassembly of section .text.PQCLEAN_FALCON512_CLEAN_fpr_expm_p63:
