
build-stm32f4/obj/fpr.o:     file format elf32-littlearm


Disassembly of section .text.fpr_trunc:

Disassembly of section .text.falcon_inner_fpr_scaled:

Disassembly of section .text.falcon_inner_fpr_add:

Disassembly of section .text.falcon_inner_fpr_mul:

00000000 <falcon_inner_fpr_mul>:
   0:	stmdb	sp!, {r4, r5, r6, r7, r8, sl, fp, lr}
   4:	bics.w	r4, r0, #4261412864	@ 0xfe000000
   8:	lsls	r5, r1, #7
   a:	orrs.w	r5, r5, r0, lsr #25
   e:	orrs.w	r5, r5, #134217728	@ 0x8000000
  12:	bics.w	r5, r5, #4026531840	@ 0xf0000000
  16:	bics.w	r6, r2, #4261412864	@ 0xfe000000
  1a:	lsls	r7, r3, #7
  1c:	orrs.w	r7, r7, r2, lsr #25
  20:	orrs.w	r7, r7, #134217728	@ 0x8000000
  24:	bics.w	r7, r7, #4026531840	@ 0xf0000000
  28:	umull	r8, sl, r4, r6
  2c:	movs.w	sl, sl, lsl #7
  30:	orrs.w	sl, sl, r8, lsr #25
  34:	eors.w	fp, fp, fp
  38:	umlal	sl, fp, r4, r7
  3c:	umlal	sl, fp, r5, r6
  40:	orrs.w	r8, r8, sl, lsl #7
  44:	movs.w	sl, sl, lsr #25
  48:	orrs.w	sl, sl, fp, lsl #7
  4c:	eors.w	fp, fp, fp
  50:	umlal	sl, fp, r5, r7
  54:	rsbs	r4, r8, #0
  58:	orrs.w	r8, r8, r4
  5c:	orrs.w	sl, sl, r8, lsr #31
  60:	ands.w	r6, sl, #1
  64:	movs.w	r5, fp, lsr #23
  68:	negs	r5, r5
  6a:	orrs.w	r6, r6, sl, lsr #1
  6e:	orrs.w	r6, r6, fp, lsl #31
  72:	movs.w	r7, fp, lsr #1
  76:	eors.w	sl, sl, r6
  7a:	eors.w	fp, fp, r7
  7e:	bics.w	sl, sl, r5
  82:	bics.w	fp, fp, r5
  86:	eors.w	r6, r6, sl
  8a:	eors.w	r7, r7, fp
  8e:	lsls	r0, r1, #1
  90:	lsls	r2, r3, #1
  92:	lsrs	r0, r0, #21
  94:	addw	r4, r0, #2047	@ 0x7ff
  98:	lsrs	r2, r2, #21
  9a:	addw	r8, r2, #2047	@ 0x7ff
  9e:	adds	r2, r2, r0
  a0:	subw	r2, r2, #1024	@ 0x400
  a4:	subs	r2, r2, r5
  a6:	ands.w	r4, r4, r8
  aa:	mvns	r5, r2
  ac:	ands.w	r5, r5, r4, lsl #20
  b0:	ands.w	r2, r2, r5, asr #31
  b4:	ands.w	r6, r6, r5, asr #31
  b8:	ands.w	r7, r7, r5, asr #31
  bc:	eors	r1, r3
  be:	bfc	r1, #0, #31
  c2:	bfi	r1, r2, #20, #11
  c6:	movs	r4, r6
  c8:	lsrs	r0, r6, #2
  ca:	orrs.w	r0, r0, r7, lsl #30
  ce:	adds.w	r1, r1, r7, lsr #2
  d2:	ands.w	r4, r4, #7
  d6:	movs	r3, #200	@ 0xc8
  d8:	lsrs	r3, r4
  da:	ands.w	r3, r3, #1
  de:	adds	r0, r0, r3
  e0:	adcs.w	r1, r1, #0
  e4:	ldmia.w	sp!, {r4, r5, r6, r7, r8, sl, fp, pc}

Disassembly of section .text.falcon_inner_fpr_div:

Disassembly of section .text.falcon_inner_fpr_sqrt:

Disassembly of section .text.falcon_inner_fpr_expm_p63:
