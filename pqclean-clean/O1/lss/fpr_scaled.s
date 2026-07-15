
build-stm32f4/obj/fpr.o:     file format elf32-littlearm


Disassembly of section .text.PQCLEAN_FALCON512_CLEAN_fpr_scaled:

00000000 <PQCLEAN_FALCON512_CLEAN_fpr_scaled>:
   0:	stmdb	sp!, {r4, r5, r6, r7, r8, lr}
   4:	lsrs	r4, r1, #31
   6:	mov.w	lr, #0
   a:	negs	r5, r4
   c:	sbc.w	r3, lr, lr, lsl #1
  10:	eors	r0, r5
  12:	eors	r3, r1
  14:	adds	r0, r4, r0
  16:	adc.w	lr, lr, r3
  1a:	sub.w	ip, r2, #54	@ 0x36
  1e:	rsb	r3, lr, #0
  22:	orr.w	r3, r3, lr
  26:	lsrs	r2, r3, #31
  28:	eor.w	r5, r0, lr
  2c:	subs	r4, r2, #1
  2e:	ands	r5, r4
  30:	and.w	r3, r0, r3, asr #31
  34:	eor.w	r5, r5, lr
  38:	add.w	ip, ip, r2, lsl #5
  3c:	lsrs	r4, r5, #16
  3e:	negs	r4, r4
  40:	lsrs	r6, r4, #31
  42:	lsls	r2, r5, #16
  44:	orr.w	r2, r2, r3, lsr #16
  48:	eor.w	r7, r3, r3, lsl #16
  4c:	eors	r2, r5
  4e:	cmp	r4, #0
  50:	mov.w	r4, #4294967295	@ 0xffffffff
  54:	it	lt
  56:	movlt	r4, #0
  58:	add.w	r8, r6, #4294967295	@ 0xffffffff
  5c:	ands	r7, r4
  5e:	and.w	r2, r2, r8
  62:	eors	r7, r3
  64:	eors	r2, r5
  66:	add.w	ip, ip, r6, lsl #4
  6a:	lsrs	r4, r2, #24
  6c:	negs	r4, r4
  6e:	lsrs	r5, r4, #31
  70:	lsls	r3, r2, #8
  72:	orr.w	r3, r3, r7, lsr #24
  76:	eor.w	r6, r7, r7, lsl #8
  7a:	eors	r3, r2
  7c:	cmp	r4, #0
  7e:	mov.w	r4, #4294967295	@ 0xffffffff
  82:	it	lt
  84:	movlt	r4, #0
  86:	add.w	r8, r5, #4294967295	@ 0xffffffff
  8a:	ands	r6, r4
  8c:	and.w	r3, r3, r8
  90:	eors	r6, r7
  92:	eors	r3, r2
  94:	add.w	ip, ip, r5, lsl #3
  98:	lsrs	r5, r3, #28
  9a:	negs	r5, r5
  9c:	lsrs	r7, r5, #31
  9e:	lsls	r2, r3, #4
  a0:	orr.w	r2, r2, r6, lsr #28
  a4:	eor.w	r4, r6, r6, lsl #4
  a8:	eors	r2, r3
  aa:	cmp	r5, #0
  ac:	mov.w	r5, #4294967295	@ 0xffffffff
  b0:	it	lt
  b2:	movlt	r5, #0
  b4:	add.w	r8, r7, #4294967295	@ 0xffffffff
  b8:	ands	r4, r5
  ba:	and.w	r2, r2, r8
  be:	eors	r4, r6
  c0:	eors	r2, r3
  c2:	add.w	r3, ip, r7, lsl #2
  c6:	lsrs	r5, r2, #30
  c8:	negs	r5, r5
  ca:	lsrs	r6, r5, #31
  cc:	mov.w	ip, r2, lsl #2
  d0:	orr.w	ip, ip, r4, lsr #30
  d4:	eor.w	r7, r4, r4, lsl #2
  d8:	eor.w	ip, ip, r2
  dc:	cmp	r5, #0
  de:	mov.w	r5, #4294967295	@ 0xffffffff
  e2:	it	lt
  e4:	movlt	r5, #0
  e6:	add.w	r8, r6, #4294967295	@ 0xffffffff
  ea:	ands	r5, r7
  ec:	and.w	ip, ip, r8
  f0:	eors	r5, r4
  f2:	eor.w	ip, ip, r2
  f6:	add.w	r3, r3, r6, lsl #1
  fa:	mov.w	r6, ip, lsr #31
  fe:	adds	r2, r5, r5
 100:	adc.w	r4, ip, ip
 104:	eors	r2, r5
 106:	eor.w	r4, r4, ip
 10a:	cmp.w	ip, #0
 10e:	mov.w	r8, #4294967295	@ 0xffffffff
 112:	it	lt
 114:	movlt.w	r8, #0
 118:	subs	r7, r6, #1
 11a:	and.w	r2, r2, r8
 11e:	ands	r4, r7
 120:	eors	r2, r5
 122:	eor.w	r4, r4, ip
 126:	add	r3, r6
 128:	ubfx	r6, r2, #0, #9
 12c:	addw	r6, r6, #511	@ 0x1ff
 130:	orrs	r6, r2
 132:	negs	r0, r0
 134:	sbc.w	r5, lr, lr, lsl #1
 138:	orr.w	r5, r5, lr
 13c:	lsrs	r2, r5, #31
 13e:	mul.w	r3, r2, r3
 142:	addw	r3, r3, #1076	@ 0x434
 146:	lsrs	r2, r3, #31
 148:	cmp	r3, #0
 14a:	mov.w	ip, #4294967295	@ 0xffffffff
 14e:	it	lt
 150:	movlt.w	ip, #0
 154:	subs	r2, #1
 156:	and.w	ip, ip, r5, asr #31
 15a:	and.w	r2, r2, r5, asr #31
 15e:	lsrs	r0, r6, #9
 160:	orr.w	r0, r0, r4, lsl #23
 164:	and.w	ip, ip, r0
 168:	and.w	r2, r2, r4, lsr #9
 16c:	and.w	r1, r1, #2147483648	@ 0x80000000
 170:	mov.w	r0, ip, lsr #2
 174:	orr.w	r0, r0, r2, lsl #30
 178:	orr.w	r1, r1, r2, lsr #2
 17c:	and.w	ip, ip, #7
 180:	movs	r4, #200	@ 0xc8
 182:	lsr.w	r4, r4, ip
 186:	and.w	r4, r4, #1
 18a:	adds	r0, r0, r4
 18c:	mov.w	r2, r2, lsr #22
 190:	mul.w	r3, r2, r3
 194:	adc.w	r1, r1, r3, lsl #20
 198:	ldmia.w	sp!, {r4, r5, r6, r7, r8, pc}

Disassembly of section .text.PQCLEAN_FALCON512_CLEAN_fpr_add:

Disassembly of section .text.PQCLEAN_FALCON512_CLEAN_fpr_mul:

Disassembly of section .text.PQCLEAN_FALCON512_CLEAN_fpr_div:

Disassembly of section .text.PQCLEAN_FALCON512_CLEAN_fpr_sqrt:

Disassembly of section .text.PQCLEAN_FALCON512_CLEAN_fpr_expm_p63:
