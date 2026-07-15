
build-stm32f4/obj/fpr.o:     file format elf32-littlearm


Disassembly of section .text.fpr_ursh:

Disassembly of section .text.fpr_ulsh:

Disassembly of section .text.FPR:

Disassembly of section .text.fpr_trunc:

Disassembly of section .text.PQCLEAN_FALCON512_CLEAN_fpr_scaled:

Disassembly of section .text.PQCLEAN_FALCON512_CLEAN_fpr_add:

Disassembly of section .text.PQCLEAN_FALCON512_CLEAN_fpr_mul:

00000000 <PQCLEAN_FALCON512_CLEAN_fpr_mul>:
   0:	stmdb	sp!, {r4, r5, r7, r8, r9, sl, fp, lr}
   4:	sub	sp, #328	@ 0x148
   6:	add	r7, sp, #0
   8:	strd	r0, r1, [r7, #224]	@ 0xe0
   c:	strd	r2, r3, [r7, #216]	@ 0xd8
  10:	ldrd	r2, r3, [r7, #224]	@ 0xe0
  14:	mov	r4, r2
  16:	ubfx	r5, r3, #0, #20
  1a:	mov	sl, r4
  1c:	orr.w	fp, r5, #1048576	@ 0x100000
  20:	strd	sl, fp, [r7, #320]	@ 0x140
  24:	ldrd	r2, r3, [r7, #216]	@ 0xd8
  28:	mov	r8, r2
  2a:	ubfx	r9, r3, #0, #20
  2e:	str.w	r8, [r7, #40]	@ 0x28
  32:	orr.w	r3, r9, #1048576	@ 0x100000
  36:	str	r3, [r7, #44]	@ 0x2c
  38:	ldrd	r3, r4, [r7, #40]	@ 0x28
  3c:	strd	r3, r4, [r7, #312]	@ 0x138
  40:	ldr.w	r3, [r7, #320]	@ 0x140
  44:	bic.w	r3, r3, #4261412864	@ 0xfe000000
  48:	str.w	r3, [r7, #308]	@ 0x134
  4c:	ldrd	r2, r3, [r7, #320]	@ 0x140
  50:	mov.w	r0, #0
  54:	mov.w	r1, #0
  58:	lsrs	r0, r2, #25
  5a:	orr.w	r0, r0, r3, lsl #7
  5e:	lsrs	r1, r3, #25
  60:	mov	r3, r0
  62:	str.w	r3, [r7, #304]	@ 0x130
  66:	ldr.w	r3, [r7, #312]	@ 0x138
  6a:	bic.w	r3, r3, #4261412864	@ 0xfe000000
  6e:	str.w	r3, [r7, #300]	@ 0x12c
  72:	ldrd	r2, r3, [r7, #312]	@ 0x138
  76:	mov.w	r0, #0
  7a:	mov.w	r1, #0
  7e:	lsrs	r0, r2, #25
  80:	orr.w	r0, r0, r3, lsl #7
  84:	lsrs	r1, r3, #25
  86:	mov	r3, r0
  88:	str.w	r3, [r7, #296]	@ 0x128
  8c:	ldr.w	r3, [r7, #308]	@ 0x134
  90:	movs	r2, #0
  92:	str.w	r3, [r7, #176]	@ 0xb0
  96:	str.w	r2, [r7, #180]	@ 0xb4
  9a:	ldr.w	r3, [r7, #300]	@ 0x12c
  9e:	movs	r2, #0
  a0:	str.w	r3, [r7, #168]	@ 0xa8
  a4:	str.w	r2, [r7, #172]	@ 0xac
  a8:	ldrd	r3, r4, [r7, #176]	@ 0xb0
  ac:	mov	r2, r4
  ae:	ldrd	r8, r9, [r7, #168]	@ 0xa8
  b2:	mov	r1, r8
  b4:	mul.w	r2, r1, r2
  b8:	mov	r5, r9
  ba:	mov	r0, r3
  bc:	mov	r1, r4
  be:	mov	r3, r0
  c0:	mul.w	r3, r3, r5
  c4:	add	r3, r2
  c6:	mov	r2, r0
  c8:	mov	r1, r8
  ca:	umull	r2, r1, r2, r1
  ce:	str.w	r1, [r7, #212]	@ 0xd4
  d2:	str.w	r2, [r7, #208]	@ 0xd0
  d6:	ldr.w	r2, [r7, #212]	@ 0xd4
  da:	add	r3, r2
  dc:	str.w	r3, [r7, #212]	@ 0xd4
  e0:	ldrd	r3, r4, [r7, #208]	@ 0xd0
  e4:	strd	r3, r4, [r7, #288]	@ 0x120
  e8:	strd	r3, r4, [r7, #288]	@ 0x120
  ec:	ldr.w	r3, [r7, #288]	@ 0x120
  f0:	bic.w	r3, r3, #4261412864	@ 0xfe000000
  f4:	str.w	r3, [r7, #284]	@ 0x11c
  f8:	ldrd	r2, r3, [r7, #288]	@ 0x120
  fc:	mov.w	r0, #0
 100:	mov.w	r1, #0
 104:	lsrs	r0, r2, #25
 106:	orr.w	r0, r0, r3, lsl #7
 10a:	lsrs	r1, r3, #25
 10c:	mov	r3, r0
 10e:	str.w	r3, [r7, #280]	@ 0x118
 112:	ldr.w	r3, [r7, #308]	@ 0x134
 116:	movs	r2, #0
 118:	str.w	r3, [r7, #160]	@ 0xa0
 11c:	str.w	r2, [r7, #164]	@ 0xa4
 120:	ldr.w	r3, [r7, #296]	@ 0x128
 124:	movs	r2, #0
 126:	str.w	r3, [r7, #152]	@ 0x98
 12a:	str.w	r2, [r7, #156]	@ 0x9c
 12e:	ldrd	r3, r4, [r7, #160]	@ 0xa0
 132:	mov	r2, r4
 134:	ldrd	r8, r9, [r7, #152]	@ 0x98
 138:	mov	r1, r8
 13a:	mul.w	r2, r1, r2
 13e:	mov	r5, r9
 140:	mov	r0, r3
 142:	mov	r1, r4
 144:	mov	r3, r0
 146:	mul.w	r3, r3, r5
 14a:	add	r3, r2
 14c:	mov	r2, r0
 14e:	mov	r1, r8
 150:	umull	r2, r1, r2, r1
 154:	str.w	r1, [r7, #204]	@ 0xcc
 158:	str.w	r2, [r7, #200]	@ 0xc8
 15c:	ldr.w	r2, [r7, #204]	@ 0xcc
 160:	add	r3, r2
 162:	str.w	r3, [r7, #204]	@ 0xcc
 166:	ldrd	r3, r4, [r7, #200]	@ 0xc8
 16a:	strd	r3, r4, [r7, #288]	@ 0x120
 16e:	strd	r3, r4, [r7, #288]	@ 0x120
 172:	ldr.w	r3, [r7, #288]	@ 0x120
 176:	bic.w	r2, r3, #4261412864	@ 0xfe000000
 17a:	ldr.w	r3, [r7, #280]	@ 0x118
 17e:	add	r3, r2
 180:	str.w	r3, [r7, #280]	@ 0x118
 184:	ldrd	r2, r3, [r7, #288]	@ 0x120
 188:	mov.w	r0, #0
 18c:	mov.w	r1, #0
 190:	lsrs	r0, r2, #25
 192:	orr.w	r0, r0, r3, lsl #7
 196:	lsrs	r1, r3, #25
 198:	mov	r3, r0
 19a:	str.w	r3, [r7, #276]	@ 0x114
 19e:	ldr.w	r3, [r7, #304]	@ 0x130
 1a2:	movs	r2, #0
 1a4:	str.w	r3, [r7, #144]	@ 0x90
 1a8:	str.w	r2, [r7, #148]	@ 0x94
 1ac:	ldr.w	r3, [r7, #300]	@ 0x12c
 1b0:	movs	r2, #0
 1b2:	str.w	r3, [r7, #136]	@ 0x88
 1b6:	str.w	r2, [r7, #140]	@ 0x8c
 1ba:	ldrd	r3, r4, [r7, #144]	@ 0x90
 1be:	mov	r2, r4
 1c0:	ldrd	r8, r9, [r7, #136]	@ 0x88
 1c4:	mov	r1, r8
 1c6:	mul.w	r2, r1, r2
 1ca:	mov	r5, r9
 1cc:	mov	r0, r3
 1ce:	mov	r1, r4
 1d0:	mov	r3, r0
 1d2:	mul.w	r3, r3, r5
 1d6:	add	r3, r2
 1d8:	mov	r2, r0
 1da:	mov	r1, r8
 1dc:	umull	r2, r1, r2, r1
 1e0:	str.w	r1, [r7, #196]	@ 0xc4
 1e4:	str.w	r2, [r7, #192]	@ 0xc0
 1e8:	ldr.w	r2, [r7, #196]	@ 0xc4
 1ec:	add	r3, r2
 1ee:	str.w	r3, [r7, #196]	@ 0xc4
 1f2:	ldrd	r3, r4, [r7, #192]	@ 0xc0
 1f6:	strd	r3, r4, [r7, #288]	@ 0x120
 1fa:	strd	r3, r4, [r7, #288]	@ 0x120
 1fe:	ldr.w	r3, [r7, #288]	@ 0x120
 202:	bic.w	r2, r3, #4261412864	@ 0xfe000000
 206:	ldr.w	r3, [r7, #280]	@ 0x118
 20a:	add	r3, r2
 20c:	str.w	r3, [r7, #280]	@ 0x118
 210:	ldrd	r2, r3, [r7, #288]	@ 0x120
 214:	mov.w	r0, #0
 218:	mov.w	r1, #0
 21c:	lsrs	r0, r2, #25
 21e:	orr.w	r0, r0, r3, lsl #7
 222:	lsrs	r1, r3, #25
 224:	mov	r2, r0
 226:	ldr.w	r3, [r7, #276]	@ 0x114
 22a:	add	r3, r2
 22c:	str.w	r3, [r7, #276]	@ 0x114
 230:	ldr.w	r3, [r7, #304]	@ 0x130
 234:	movs	r2, #0
 236:	str.w	r3, [r7, #128]	@ 0x80
 23a:	str.w	r2, [r7, #132]	@ 0x84
 23e:	ldr.w	r3, [r7, #296]	@ 0x128
 242:	movs	r2, #0
 244:	str	r3, [r7, #120]	@ 0x78
 246:	str	r2, [r7, #124]	@ 0x7c
 248:	ldrd	r3, r4, [r7, #128]	@ 0x80
 24c:	mov	r2, r4
 24e:	ldrd	r8, r9, [r7, #120]	@ 0x78
 252:	mov	r1, r8
 254:	mul.w	r2, r1, r2
 258:	mov	r5, r9
 25a:	mov	r0, r3
 25c:	mov	r1, r4
 25e:	mov	r3, r0
 260:	mul.w	r3, r3, r5
 264:	add	r3, r2
 266:	mov	r2, r0
 268:	mov	r1, r8
 26a:	umull	r2, r1, r2, r1
 26e:	str.w	r1, [r7, #188]	@ 0xbc
 272:	str.w	r2, [r7, #184]	@ 0xb8
 276:	ldr.w	r2, [r7, #188]	@ 0xbc
 27a:	add	r3, r2
 27c:	str.w	r3, [r7, #188]	@ 0xbc
 280:	ldrd	r3, r4, [r7, #184]	@ 0xb8
 284:	strd	r3, r4, [r7, #264]	@ 0x108
 288:	strd	r3, r4, [r7, #264]	@ 0x108
 28c:	ldr.w	r3, [r7, #280]	@ 0x118
 290:	lsrs	r2, r3, #25
 292:	ldr.w	r3, [r7, #276]	@ 0x114
 296:	add	r3, r2
 298:	str.w	r3, [r7, #276]	@ 0x114
 29c:	ldr.w	r3, [r7, #280]	@ 0x118
 2a0:	bic.w	r3, r3, #4261412864	@ 0xfe000000
 2a4:	str.w	r3, [r7, #280]	@ 0x118
 2a8:	ldr.w	r3, [r7, #276]	@ 0x114
 2ac:	movs	r2, #0
 2ae:	str	r3, [r7, #112]	@ 0x70
 2b0:	str	r2, [r7, #116]	@ 0x74
 2b2:	ldrd	r2, r3, [r7, #264]	@ 0x108
 2b6:	ldrd	r4, r5, [r7, #112]	@ 0x70
 2ba:	mov	r1, r4
 2bc:	adds	r1, r2, r1
 2be:	str	r1, [r7, #32]
 2c0:	mov	r1, r5
 2c2:	adc.w	r1, r3, r1
 2c6:	str	r1, [r7, #36]	@ 0x24
 2c8:	ldrd	r3, r4, [r7, #32]
 2cc:	strd	r3, r4, [r7, #264]	@ 0x108
 2d0:	ldr.w	r2, [r7, #284]	@ 0x11c
 2d4:	ldr.w	r3, [r7, #280]	@ 0x118
 2d8:	orrs	r3, r2
 2da:	add.w	r3, r3, #33554432	@ 0x2000000
 2de:	subs	r3, #1
 2e0:	lsrs	r3, r3, #25
 2e2:	movs	r2, #0
 2e4:	str	r3, [r7, #104]	@ 0x68
 2e6:	str	r2, [r7, #108]	@ 0x6c
 2e8:	ldrd	r2, r3, [r7, #264]	@ 0x108
 2ec:	ldrd	r0, r1, [r7, #104]	@ 0x68
 2f0:	mov	r4, r0
 2f2:	orrs	r4, r2
 2f4:	str	r4, [r7, #24]
 2f6:	orrs	r1, r3
 2f8:	str	r1, [r7, #28]
 2fa:	ldrd	r3, r4, [r7, #24]
 2fe:	strd	r3, r4, [r7, #264]	@ 0x108
 302:	ldrd	r2, r3, [r7, #264]	@ 0x108
 306:	mov.w	r0, #0
 30a:	mov.w	r1, #0
 30e:	lsrs	r0, r2, #1
 310:	orr.w	r0, r0, r3, lsl #31
 314:	lsrs	r1, r3, #1
 316:	ldrd	r2, r3, [r7, #264]	@ 0x108
 31a:	and.w	r3, r2, #1
 31e:	str	r3, [r7, #96]	@ 0x60
 320:	movs	r3, #0
 322:	str	r3, [r7, #100]	@ 0x64
 324:	ldrd	r3, r4, [r7, #96]	@ 0x60
 328:	mov	r2, r3
 32a:	orrs	r2, r0
 32c:	str	r2, [r7, #16]
 32e:	mov	r3, r4
 330:	orrs	r3, r1
 332:	str	r3, [r7, #20]
 334:	ldrd	r3, r4, [r7, #16]
 338:	strd	r3, r4, [r7, #256]	@ 0x100
 33c:	ldrd	r2, r3, [r7, #264]	@ 0x108
 340:	mov.w	r0, #0
 344:	mov.w	r1, #0
 348:	lsrs	r0, r3, #23
 34a:	movs	r1, #0
 34c:	strd	r0, r1, [r7, #288]	@ 0x120
 350:	ldrd	r0, r1, [r7, #264]	@ 0x108
 354:	ldrd	r2, r3, [r7, #256]	@ 0x100
 358:	eor.w	r4, r0, r2
 35c:	str	r4, [r7, #88]	@ 0x58
 35e:	eors	r3, r1
 360:	str	r3, [r7, #92]	@ 0x5c
 362:	ldrd	r2, r3, [r7, #288]	@ 0x120
 366:	movs	r1, #0
 368:	negs	r0, r2
 36a:	str	r0, [r7, #80]	@ 0x50
 36c:	sbc.w	r3, r1, r3
 370:	str	r3, [r7, #84]	@ 0x54
 372:	ldrd	r3, r4, [r7, #88]	@ 0x58
 376:	mov	r0, r3
 378:	ldrd	r1, r2, [r7, #80]	@ 0x50
 37c:	mov	r5, r1
 37e:	ands	r0, r5
 380:	str	r0, [r7, #72]	@ 0x48
 382:	mov	r3, r4
 384:	ands	r3, r2
 386:	str	r3, [r7, #76]	@ 0x4c
 388:	ldrd	r2, r3, [r7, #264]	@ 0x108
 38c:	ldrd	r0, r1, [r7, #72]	@ 0x48
 390:	mov	r4, r0
 392:	eors	r4, r2
 394:	str	r4, [r7, #8]
 396:	eors	r1, r3
 398:	str	r1, [r7, #12]
 39a:	ldrd	r3, r4, [r7, #8]
 39e:	strd	r3, r4, [r7, #264]	@ 0x108
 3a2:	ldrd	r0, r1, [r7, #224]	@ 0xe0
 3a6:	mov.w	r2, #0
 3aa:	mov.w	r3, #0
 3ae:	lsrs	r2, r1, #20
 3b0:	movs	r3, #0
 3b2:	mov	r3, r2
 3b4:	ubfx	r3, r3, #0, #11
 3b8:	str.w	r3, [r7, #252]	@ 0xfc
 3bc:	ldrd	r0, r1, [r7, #216]	@ 0xd8
 3c0:	mov.w	r2, #0
 3c4:	mov.w	r3, #0
 3c8:	lsrs	r2, r1, #20
 3ca:	movs	r3, #0
 3cc:	mov	r3, r2
 3ce:	ubfx	r3, r3, #0, #11
 3d2:	str.w	r3, [r7, #248]	@ 0xf8
 3d6:	ldr.w	r2, [r7, #252]	@ 0xfc
 3da:	ldr.w	r3, [r7, #248]	@ 0xf8
 3de:	add	r3, r2
 3e0:	subw	r2, r3, #2100	@ 0x834
 3e4:	ldr.w	r3, [r7, #288]	@ 0x120
 3e8:	add	r3, r2
 3ea:	str.w	r3, [r7, #244]	@ 0xf4
 3ee:	ldrd	r0, r1, [r7, #224]	@ 0xe0
 3f2:	ldrd	r2, r3, [r7, #216]	@ 0xd8
 3f6:	eor.w	r4, r0, r2
 3fa:	str	r4, [r7, #64]	@ 0x40
 3fc:	eors	r3, r1
 3fe:	str	r3, [r7, #68]	@ 0x44
 400:	mov.w	r2, #0
 404:	mov.w	r3, #0
 408:	ldr	r1, [r7, #68]	@ 0x44
 40a:	lsrs	r2, r1, #31
 40c:	movs	r3, #0
 40e:	mov	r3, r2
 410:	str.w	r3, [r7, #240]	@ 0xf0
 414:	ldr.w	r3, [r7, #252]	@ 0xfc
 418:	addw	r2, r3, #2047	@ 0x7ff
 41c:	ldr.w	r3, [r7, #248]	@ 0xf8
 420:	addw	r3, r3, #2047	@ 0x7ff
 424:	ands	r3, r2
 426:	asrs	r3, r3, #11
 428:	str.w	r3, [r7, #236]	@ 0xec
 42c:	ldr.w	r3, [r7, #236]	@ 0xec
 430:	asrs	r2, r3, #31
 432:	str	r3, [r7, #56]	@ 0x38
 434:	str	r2, [r7, #60]	@ 0x3c
 436:	movs	r3, #0
 438:	ldrd	r0, r1, [r7, #56]	@ 0x38
 43c:	mov	r2, r0
 43e:	negs	r2, r2
 440:	str	r2, [r7, #48]	@ 0x30
 442:	mov	r2, r1
 444:	sbc.w	r3, r3, r2
 448:	str	r3, [r7, #52]	@ 0x34
 44a:	ldrd	r2, r3, [r7, #264]	@ 0x108
 44e:	ldrd	r0, r1, [r7, #48]	@ 0x30
 452:	mov	r4, r0
 454:	ands	r4, r2
 456:	str	r4, [r7, #0]
 458:	ands	r1, r3
 45a:	str	r1, [r7, #4]
 45c:	ldrd	r3, r4, [r7]
 460:	strd	r3, r4, [r7, #264]	@ 0x108
 464:	ldrd	r2, r3, [r7, #264]	@ 0x108
 468:	ldr.w	r1, [r7, #244]	@ 0xf4
 46c:	ldr.w	r0, [r7, #240]	@ 0xf0
 470:	bl	0 <PQCLEAN_FALCON512_CLEAN_fpr_mul>
 474:	mov	r2, r0
 476:	mov	r3, r1
 478:	mov	r0, r2
 47a:	mov	r1, r3
 47c:	add.w	r7, r7, #328	@ 0x148
 480:	mov	sp, r7
 482:	ldmia.w	sp!, {r4, r5, r7, r8, r9, sl, fp, pc}

Disassembly of section .text.PQCLEAN_FALCON512_CLEAN_fpr_div:

Disassembly of section .text.PQCLEAN_FALCON512_CLEAN_fpr_sqrt:

Disassembly of section .text.PQCLEAN_FALCON512_CLEAN_fpr_expm_p63:
