
build-stm32f4/obj/fpr.o:     file format elf32-littlearm


Disassembly of section .text.PQCLEAN_FALCON512_CLEAN_fpr_scaled:

00000000 <PQCLEAN_FALCON512_CLEAN_fpr_scaled>:
   0:	push	{r4, r5, r6, lr}
   2:	eor.w	r0, r0, r1, asr #31
   6:	lsrs	r5, r1, #31
   8:	adds	r5, r5, r0
   a:	eor.w	r4, r1, r1, asr #31
   e:	adc.w	r4, r4, #0
  12:	negs	r0, r4
  14:	orrs	r0, r4
  16:	lsrs	r6, r0, #31
  18:	sub.w	r3, r2, #54	@ 0x36
  1c:	add.w	r3, r3, r6, lsl #5
  20:	eor.w	r2, r5, r4
  24:	subs	r6, #1
  26:	ands	r6, r2
  28:	eors	r6, r4
  2a:	lsrs	r2, r6, #16
  2c:	and.w	r0, r5, r0, asr #31
  30:	negs	r2, r2
  32:	mov.w	ip, r6, lsl #16
  36:	mov.w	lr, r2, lsr #31
  3a:	orr.w	ip, ip, r0, lsr #16
  3e:	eor.w	ip, ip, r6
  42:	add.w	r3, r3, lr, lsl #4
  46:	add.w	lr, lr, #4294967295	@ 0xffffffff
  4a:	cmp	r2, #0
  4c:	and.w	ip, ip, lr
  50:	eor.w	ip, ip, r6
  54:	mov.w	r2, #4294967295	@ 0xffffffff
  58:	eor.w	r6, r0, r0, lsl #16
  5c:	it	lt
  5e:	movlt	r2, #0
  60:	ands	r6, r2
  62:	eors	r6, r0
  64:	mov.w	r0, ip, lsr #24
  68:	negs	r0, r0
  6a:	mov.w	r2, ip, lsl #8
  6e:	mov.w	lr, r0, lsr #31
  72:	orr.w	r2, r2, r6, lsr #24
  76:	eor.w	r2, r2, ip
  7a:	add.w	r3, r3, lr, lsl #3
  7e:	add.w	lr, lr, #4294967295	@ 0xffffffff
  82:	cmp	r0, #0
  84:	and.w	r2, r2, lr
  88:	eor.w	r2, r2, ip
  8c:	mov.w	r0, #4294967295	@ 0xffffffff
  90:	eor.w	lr, r6, r6, lsl #8
  94:	it	lt
  96:	movlt	r0, #0
  98:	and.w	lr, lr, r0
  9c:	mov.w	ip, r2, lsr #28
  a0:	eor.w	lr, lr, r6
  a4:	rsb	ip, ip, #0
  a8:	lsls	r0, r2, #4
  aa:	mov.w	r6, ip, lsr #31
  ae:	orr.w	r0, r0, lr, lsr #28
  b2:	eors	r0, r2
  b4:	add.w	r3, r3, r6, lsl #2
  b8:	subs	r6, #1
  ba:	cmp.w	ip, #0
  be:	and.w	r0, r0, r6
  c2:	eor.w	r0, r0, r2
  c6:	mov.w	ip, #4294967295	@ 0xffffffff
  ca:	eor.w	r2, lr, lr, lsl #4
  ce:	it	lt
  d0:	movlt.w	ip, #0
  d4:	and.w	ip, r2, ip
  d8:	eor.w	ip, ip, lr
  dc:	mov.w	lr, r0, lsr #30
  e0:	rsb	lr, lr, #0
  e4:	lsls	r2, r0, #2
  e6:	mov.w	r6, lr, lsr #31
  ea:	orr.w	r2, r2, ip, lsr #30
  ee:	eors	r2, r0
  f0:	add.w	r3, r3, r6, lsl #1
  f4:	subs	r6, #1
  f6:	cmp.w	lr, #0
  fa:	and.w	r2, r2, r6
  fe:	eor.w	r2, r2, r0
 102:	mov.w	lr, #4294967295	@ 0xffffffff
 106:	eor.w	r0, ip, ip, lsl #2
 10a:	it	lt
 10c:	movlt.w	lr, #0
 110:	and.w	r0, r0, lr
 114:	eor.w	r0, r0, ip
 118:	adds.w	ip, r0, r0
 11c:	adc.w	lr, r2, r2
 120:	cmp	r2, #0
 122:	mov.w	r6, #4294967295	@ 0xffffffff
 126:	eor.w	ip, ip, r0
 12a:	it	lt
 12c:	movlt	r6, #0
 12e:	and.w	ip, ip, r6
 132:	negs	r5, r5
 134:	eor.w	ip, ip, r0
 138:	sbc.w	r0, r4, r4, lsl #1
 13c:	orrs	r0, r4
 13e:	lsrs	r4, r2, #31
 140:	eor.w	lr, lr, r2
 144:	add	r3, r4
 146:	subs	r4, #1
 148:	and.w	lr, lr, r4
 14c:	lsrs	r4, r0, #31
 14e:	eor.w	lr, lr, r2
 152:	mul.w	r3, r4, r3
 156:	ubfx	r2, ip, #0, #9
 15a:	addw	r3, r3, #1076	@ 0x434
 15e:	addw	r2, r2, #511	@ 0x1ff
 162:	cmp	r3, #0
 164:	orr.w	r2, r2, ip
 168:	mov.w	r2, r2, lsr #9
 16c:	mov.w	ip, #4294967295	@ 0xffffffff
 170:	it	lt
 172:	movlt.w	ip, #0
 176:	orr.w	r2, r2, lr, lsl #23
 17a:	and.w	ip, ip, r0, asr #31
 17e:	and.w	ip, ip, r2
 182:	lsrs	r2, r3, #31
 184:	subs	r2, #1
 186:	and.w	r2, r2, r0, asr #31
 18a:	and.w	r2, r2, lr, lsr #9
 18e:	mov.w	r0, ip, lsr #2
 192:	and.w	r1, r1, #2147483648	@ 0x80000000
 196:	orr.w	r0, r0, r2, lsl #30
 19a:	orr.w	r1, r1, r2, lsr #2
 19e:	lsrs	r2, r2, #22
 1a0:	mul.w	r3, r2, r3
 1a4:	and.w	ip, ip, #7
 1a8:	movs	r2, #200	@ 0xc8
 1aa:	lsr.w	r2, r2, ip
 1ae:	and.w	r2, r2, #1
 1b2:	adds	r0, r0, r2
 1b4:	adc.w	r1, r1, r3, lsl #20
 1b8:	pop	{r4, r5, r6, pc}

Disassembly of section .text.PQCLEAN_FALCON512_CLEAN_fpr_add:

Disassembly of section .text.PQCLEAN_FALCON512_CLEAN_fpr_mul:

Disassembly of section .text.PQCLEAN_FALCON512_CLEAN_fpr_div:

Disassembly of section .text.PQCLEAN_FALCON512_CLEAN_fpr_sqrt:

Disassembly of section .text.PQCLEAN_FALCON512_CLEAN_fpr_expm_p63:
