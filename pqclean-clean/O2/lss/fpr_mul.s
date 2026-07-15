
build-stm32f4/obj/fpr.o:     file format elf32-littlearm


Disassembly of section .text.PQCLEAN_FALCON512_CLEAN_fpr_scaled:

Disassembly of section .text.PQCLEAN_FALCON512_CLEAN_fpr_add:

Disassembly of section .text.PQCLEAN_FALCON512_CLEAN_fpr_mul:

00000000 <PQCLEAN_FALCON512_CLEAN_fpr_mul>:
   0:	stmdb	sp!, {r4, r5, r6, r7, r8, r9, lr}
   4:	ubfx	r4, r1, #0, #20
   8:	orr.w	r4, r4, #1048576	@ 0x100000
   c:	ubfx	r5, r3, #0, #20
  10:	lsrs	r7, r0, #25
  12:	orr.w	r7, r7, r4, lsl #7
  16:	orr.w	r5, r5, #1048576	@ 0x100000
  1a:	bic.w	ip, r0, #4261412864	@ 0xfe000000
  1e:	bic.w	r4, r2, #4261412864	@ 0xfe000000
  22:	lsrs	r6, r2, #25
  24:	orr.w	r6, r6, r5, lsl #7
  28:	umull	r0, r2, ip, r4
  2c:	mov.w	r9, r0, lsr #25
  30:	umull	ip, r5, r6, ip
  34:	umull	r4, r8, r7, r4
  38:	orr.w	r9, r9, r2, lsl #7
  3c:	bic.w	r2, ip, #4261412864	@ 0xfe000000
  40:	mov.w	ip, ip, lsr #25
  44:	add	r2, r9
  46:	orr.w	ip, ip, r5, lsl #7
  4a:	bic.w	r5, r4, #4261412864	@ 0xfe000000
  4e:	add	r5, r2
  50:	lsrs	r4, r4, #25
  52:	orr.w	r4, r4, r8, lsl #7
  56:	orrs	r0, r5
  58:	add.w	r2, ip, r4
  5c:	bic.w	r0, r0, #4261412864	@ 0xfe000000
  60:	add.w	r2, r2, r5, lsr #25
  64:	mov.w	lr, #0
  68:	add.w	r0, r0, #33554432	@ 0x2000000
  6c:	umlal	r2, lr, r7, r6
  70:	subs	r0, #1
  72:	orr.w	r0, r2, r0, lsr #25
  76:	lsrs	r2, r2, #1
  78:	tst.w	lr, #8388608	@ 0x800000
  7c:	orr.w	r2, r2, lr, lsl #31
  80:	and.w	r4, r0, #1
  84:	orr.w	r2, r2, r4
  88:	ubfx	ip, r1, #20, #11
  8c:	it	eq
  8e:	moveq	r2, r0
  90:	ubfx	r0, r3, #20, #11
  94:	eor.w	r1, r1, r3
  98:	addw	r3, ip, #2047	@ 0x7ff
  9c:	add	ip, r0
  9e:	addw	r0, r0, #2047	@ 0x7ff
  a2:	mov.w	r4, lr, lsr #23
  a6:	and.w	r3, r3, r0
  aa:	it	ne
  ac:	movne.w	r5, lr, lsr #1
  b0:	add	ip, r4
  b2:	mov.w	r0, r3, asr #11
  b6:	sub.w	ip, ip, #1024	@ 0x400
  ba:	it	ne
  bc:	movne	lr, r5
  be:	asrs	r3, r3, #31
  c0:	negs	r0, r0
  c2:	and.w	r0, r0, r2
  c6:	sbc.w	r3, r3, r3, lsl #1
  ca:	mov.w	r2, ip, lsr #31
  ce:	cmp.w	ip, #0
  d2:	and.w	r3, r3, lr
  d6:	add.w	r2, r2, #4294967295	@ 0xffffffff
  da:	and.w	r3, r3, r2
  de:	mov.w	r2, #4294967295	@ 0xffffffff
  e2:	it	lt
  e4:	movlt	r2, #0
  e6:	ands	r0, r2
  e8:	and.w	r4, r0, #7
  ec:	and.w	r1, r1, #2147483648	@ 0x80000000
  f0:	lsrs	r0, r0, #2
  f2:	movs	r2, #200	@ 0xc8
  f4:	orr.w	r1, r1, r3, lsr #2
  f8:	orr.w	r0, r0, r3, lsl #30
  fc:	lsrs	r2, r4
  fe:	lsrs	r3, r3, #22
 100:	and.w	r2, r2, #1
 104:	negs	r3, r3
 106:	and.w	r3, r3, ip
 10a:	adds	r0, r0, r2
 10c:	adc.w	r1, r1, r3, lsl #20
 110:	ldmia.w	sp!, {r4, r5, r6, r7, r8, r9, pc}

Disassembly of section .text.PQCLEAN_FALCON512_CLEAN_fpr_div:

Disassembly of section .text.PQCLEAN_FALCON512_CLEAN_fpr_sqrt:

Disassembly of section .text.PQCLEAN_FALCON512_CLEAN_fpr_expm_p63:
