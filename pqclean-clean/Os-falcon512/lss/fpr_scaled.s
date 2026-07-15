
build-stm32f4/obj/fpr.o:     file format elf32-littlearm


Disassembly of section .text.FPR:

Disassembly of section .text.fpr_trunc:

Disassembly of section .text.PQCLEAN_FALCON512_CLEAN_fpr_scaled:

00000000 <PQCLEAN_FALCON512_CLEAN_fpr_scaled>:
   0:	stmdb	sp!, {r4, r5, r6, r7, r8, lr}
   4:	eor.w	r0, r0, r1, asr #31
   8:	lsrs	r5, r1, #31
   a:	adds	r0, r5, r0
   c:	eor.w	r1, r1, r1, asr #31
  10:	adc.w	r4, r1, #0
  14:	negs	r1, r4
  16:	orrs	r1, r4
  18:	lsrs	r3, r1, #31
  1a:	eor.w	r6, r0, r4
  1e:	subs	r7, r3, #1
  20:	ands	r6, r7
  22:	eors	r6, r4
  24:	subs	r2, #54	@ 0x36
  26:	add.w	ip, r2, r3, lsl #5
  2a:	lsrs	r2, r6, #16
  2c:	and.w	r1, r0, r1, asr #31
  30:	negs	r2, r2
  32:	lsls	r3, r6, #16
  34:	mov.w	lr, r2, lsr #31
  38:	orr.w	r3, r3, r1, lsr #16
  3c:	add.w	r8, lr, #4294967295	@ 0xffffffff
  40:	eors	r3, r6
  42:	cmp	r2, #0
  44:	and.w	r3, r3, r8
  48:	eor.w	r3, r3, r6
  4c:	mov.w	r2, #4294967295	@ 0xffffffff
  50:	eor.w	r7, r1, r1, lsl #16
  54:	it	lt
  56:	movlt	r2, #0
  58:	ands	r7, r2
  5a:	lsrs	r6, r3, #24
  5c:	eors	r7, r1
  5e:	negs	r6, r6
  60:	lsls	r2, r3, #8
  62:	add.w	r1, ip, lr, lsl #4
  66:	orr.w	r2, r2, r7, lsr #24
  6a:	mov.w	lr, r6, lsr #31
  6e:	cmp	r6, #0
  70:	add.w	r8, lr, #4294967295	@ 0xffffffff
  74:	eor.w	r2, r2, r3
  78:	mov.w	r6, #4294967295	@ 0xffffffff
  7c:	eor.w	ip, r7, r7, lsl #8
  80:	it	lt
  82:	movlt	r6, #0
  84:	and.w	r2, r2, r8
  88:	eors	r2, r3
  8a:	and.w	ip, ip, r6
  8e:	eor.w	ip, ip, r7
  92:	lsrs	r7, r2, #28
  94:	negs	r7, r7
  96:	lsls	r3, r2, #4
  98:	add.w	r1, r1, lr, lsl #3
  9c:	orr.w	r3, r3, ip, lsr #28
  a0:	mov.w	lr, r7, lsr #31
  a4:	add.w	r8, lr, #4294967295	@ 0xffffffff
  a8:	eors	r3, r2
  aa:	cmp	r7, #0
  ac:	and.w	r3, r3, r8
  b0:	eor.w	r3, r3, r2
  b4:	mov.w	r7, #4294967295	@ 0xffffffff
  b8:	eor.w	r6, ip, ip, lsl #4
  bc:	it	lt
  be:	movlt	r7, #0
  c0:	ands	r6, r7
  c2:	lsrs	r7, r3, #30
  c4:	negs	r7, r7
  c6:	eor.w	r6, r6, ip
  ca:	cmp	r7, #0
  cc:	mov.w	r2, r3, lsl #2
  d0:	add.w	r1, r1, lr, lsl #2
  d4:	orr.w	r2, r2, r6, lsr #30
  d8:	mov.w	lr, r7, lsr #31
  dc:	eor.w	ip, r6, r6, lsl #2
  e0:	mov.w	r7, #4294967295	@ 0xffffffff
  e4:	it	lt
  e6:	movlt	r7, #0
  e8:	add.w	r8, lr, #4294967295	@ 0xffffffff
  ec:	eors	r2, r3
  ee:	and.w	ip, ip, r7
  f2:	eor.w	ip, ip, r6
  f6:	and.w	r2, r2, r8
  fa:	eors	r2, r3
  fc:	adds.w	r6, ip, ip
 100:	adc.w	r3, r2, r2
 104:	cmp	r2, #0
 106:	mov.w	r7, r2, lsr #31
 10a:	mov.w	r8, #4294967295	@ 0xffffffff
 10e:	eor.w	r6, r6, ip
 112:	it	lt
 114:	movlt.w	r8, #0
 118:	add.w	r1, r1, lr, lsl #1
 11c:	eors	r3, r2
 11e:	add.w	lr, r7, #4294967295	@ 0xffffffff
 122:	and.w	r6, r6, r8
 126:	eor.w	r6, r6, ip
 12a:	and.w	r3, r3, lr
 12e:	eors	r3, r2
 130:	ubfx	r2, r6, #0, #9
 134:	addw	r2, r2, #511	@ 0x1ff
 138:	negs	r0, r0
 13a:	orr.w	r2, r2, r6
 13e:	sbc.w	r0, r4, r4, lsl #1
 142:	orrs	r0, r4
 144:	lsrs	r2, r2, #9
 146:	add	r7, r1
 148:	orr.w	r2, r2, r3, lsl #23
 14c:	lsrs	r1, r0, #31
 14e:	lsrs	r3, r3, #9
 150:	and.w	r2, r2, r0, asr #31
 154:	and.w	r3, r3, r0, asr #31
 158:	muls	r1, r7
 15a:	mov	r0, r5
 15c:	ldmia.w	sp!, {r4, r5, r6, r7, r8, lr}
 160:	b.w	0 <PQCLEAN_FALCON512_CLEAN_fpr_scaled>

Disassembly of section .text.PQCLEAN_FALCON512_CLEAN_fpr_add:

Disassembly of section .text.PQCLEAN_FALCON512_CLEAN_fpr_mul:

Disassembly of section .text.PQCLEAN_FALCON512_CLEAN_fpr_div:

Disassembly of section .text.PQCLEAN_FALCON512_CLEAN_fpr_sqrt:

Disassembly of section .text.PQCLEAN_FALCON512_CLEAN_fpr_expm_p63:
