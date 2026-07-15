TARGET?=stm32f4
SS_VER?=SS_VER_1_0
TESTFILE?=fpemu

# Root that Falcon-impl-20211101 is relative to. Make resolves relative paths
# against the directory make runs in, not against this file, so when building
# from a subdir (e.g. O3/ via O3/Makefile) override ROOT to add a leading "..".
ROOT?=..

SRC += fpr.c
CFLAGS += -I$(ROOT)/Falcon-impl-20211101/
VPATH += $(ROOT)/Falcon-impl-20211101/

SRC += $(TESTFILE).c

ifeq ($(TEST_CYCLE), 1)
  CFLAGS += -DTEST_CYCLE
endif

FIRMWAREPATH = $(HOME)/sca/cw-firmware-mcu
include $(FIRMWAREPATH)/simpleserial/simpleserial.mk
include $(FIRMWAREPATH)/tracewhisperer/tracewhisperer.mk
include $(FIRMWAREPATH)/config.mk
include $(FIRMWAREPATH)/rules.mk

objdump-scaled:
	arm-none-eabi-objdump \
		--disassemble=falcon_inner_fpr_scaled \
		--no-show-raw-insn \
		build-stm32f4/obj/fpr.o > lss/fpr_scaled.s
	arm-none-eabi-objdump -S \
		--disassemble=falcon_inner_fpr_scaled \
		--no-show-raw-insn \
		build-stm32f4/obj/fpr.o > lss/fpr_scaled.lss
	grep -E falcon_inner_fpr_scaled build-stm32f4/fpemu.sym

objdump-mul:
	arm-none-eabi-objdump \
		--disassemble=falcon_inner_fpr_mul \
		--no-show-raw-insn \
		build-stm32f4/obj/fpr.o > lss/fpr_mul.s
	arm-none-eabi-objdump -S \
		--disassemble=falcon_inner_fpr_mul \
		--no-show-raw-insn \
		build-stm32f4/obj/fpr.o > lss/fpr_mul.lss
	grep -E falcon_inner_fpr_mul build-stm32f4/fpemu.sym
