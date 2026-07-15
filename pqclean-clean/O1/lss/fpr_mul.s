
build-stm32f4/obj/fpr.o:     file format elf32-littlearm


Disassembly of section .text.PQCLEAN_FALCON512_CLEAN_fpr_scaled:

Disassembly of section .text.PQCLEAN_FALCON512_CLEAN_fpr_add:

Disassembly of section .text.PQCLEAN_FALCON512_CLEAN_fpr_mul:

00000000 <PQCLEAN_FALCON512_CLEAN_fpr_mul>:
   0:	push	{r4, r5, r6, r7, lr}
   2:	ubfx	r6, r1, #0, #20
   6:	orr.w	r6, r6, #1048576	@ 0x100000
   a:	ubfx	r5, r3, #0, #20
   e:	orr.w	r5, r5, #1048576	@ 0x100000
  12:	lsrs	r4, r0, #25
  14:	orr.w	r4, r4, r6, lsl #7
  18:	mov.w	lr, r2, lsr #25
  1c:	orr.w	lr, lr, r5, lsl #7
  20:	bic.w	r0, r0, #4261412864	@ 0xfe000000
  24:	bic.w	r2, r2, #4261412864	@ 0xfe000000
  28:	umull	ip, r6, r0, r2
  2c:	mov.w	r5, ip, lsr #25
  30:	orr.w	r5, r5, r6, lsl #7
  34:	umull	r0, r7, lr, r0
  38:	bic.w	r6, r0, #4261412864	@ 0xfe000000
  3c:	add	r6, r5
  3e:	lsrs	r0, r0, #25
  40:	orr.w	r0, r0, r7, lsl #7
  44:	umull	r2, r7, r4, r2
  48:	bic.w	r5, r2, #4261412864	@ 0xfe000000
  4c:	add	r5, r6
  4e:	lsrs	r2, r2, #25
  50:	orr.w	r2, r2, r7, lsl #7
  54:	add	r2, r0
  56:	umull	r4, r0, r4, lr
  5a:	add.w	r2, r2, r5, lsr #25
  5e:	adds	r2, r2, r4
  60:	adc.w	r0, r0, #0
  64:	orr.w	ip, r5, ip
  68:	bic.w	ip, ip, #4261412864	@ 0xfe000000
  6c:	add.w	ip, ip, #33554432	@ 0x2000000
  70:	add.w	ip, ip, #4294967295	@ 0xffffffff
  74:	orr.w	ip, r2, ip, lsr #25
  78:	lsrs	r2, r2, #1
  7a:	orr.w	r2, r2, r0, lsl #31
  7e:	and.w	r4, ip, #1
  82:	orrs	r2, r4
  84:	lsrs	r6, r0, #23
  86:	tst.w	r0, #8388608	@ 0x800000
  8a:	beq.n	92 <PQCLEAN_FALCON512_CLEAN_fpr_mul+0x92>
  8c:	lsrs	r5, r0, #1
  8e:	mov	ip, r2
  90:	mov	r0, r5
  92:	ubfx	r2, r1, #20, #11
  96:	ubfx	r5, r3, #20, #11
  9a:	adds	r4, r2, r5
  9c:	add	r4, r6
  9e:	sub.w	r4, r4, #1024	@ 0x400
  a2:	addw	r2, r2, #2047	@ 0x7ff
  a6:	addw	r5, r5, #2047	@ 0x7ff
  aa:	ands	r2, r5
  ac:	asrs	r5, r2, #11
  ae:	asrs	r2, r2, #31
  b0:	negs	r5, r5
  b2:	sbc.w	r2, r2, r2, lsl #1
  b6:	and.w	ip, r5, ip
  ba:	ands	r2, r0
  bc:	lsrs	r0, r4, #31
  be:	cmp	r4, #0
  c0:	mov.w	r5, #4294967295	@ 0xffffffff
  c4:	it	lt
  c6:	movlt	r5, #0
  c8:	subs	r0, #1
  ca:	and.w	ip, ip, r5
  ce:	ands	r2, r0
  d0:	eors	r1, r3
  d2:	and.w	r1, r1, #2147483648	@ 0x80000000
  d6:	mov.w	r0, ip, lsr #2
  da:	orr.w	r0, r0, r2, lsl #30
  de:	orr.w	r1, r1, r2, lsr #2
  e2:	and.w	ip, ip, #7
  e6:	movs	r3, #200	@ 0xc8
  e8:	lsr.w	r3, r3, ip
  ec:	and.w	r3, r3, #1
  f0:	adds	r0, r0, r3
  f2:	mov.w	r2, r2, lsr #22
  f6:	rsb	r2, r2, #0
  fa:	and.w	r2, r2, r4
  fe:	adc.w	r1, r1, r2, lsl #20
 102:	pop	{r4, r5, r6, r7, pc}

Disassembly of section .text.PQCLEAN_FALCON512_CLEAN_fpr_div:

Disassembly of section .text.PQCLEAN_FALCON512_CLEAN_fpr_sqrt:

Disassembly of section .text.PQCLEAN_FALCON512_CLEAN_fpr_expm_p63:
