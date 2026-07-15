TARGET?=stm32f4
SS_VER?=SS_VER_1_0
TESTFILE?=pqclean-clean
FALCON_N=512

# Root that PQClean is relative to. Make resolves relative paths against the
# directory make runs in, not against this file, so when building from a
# subdir (e.g. O3-soft/ via O3-soft.mk) override ROOT to add a leading "..".
ROOT?=..

SRC += fpr.c
CFLAGS += -I$(ROOT)/PQClean/common -I$(ROOT)/PQClean/crypto_sign/falcon-$(FALCON_N)/clean/
VPATH += $(ROOT)/PQClean/crypto_sign/falcon-$(FALCON_N)/clean/

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
		--disassemble=PQCLEAN_FALCON$(FALCON_N)_CLEAN_fpr_scaled \
		--no-show-raw-insn \
		build-stm32f4/obj/fpr.o > lss/fpr_scaled.s
	arm-none-eabi-objdump -S \
		--disassemble=PQCLEAN_FALCON$(FALCON_N)_CLEAN_fpr_scaled \
		--no-show-raw-insn \
		build-stm32f4/obj/fpr.o > lss/fpr_scaled.lss
	grep -E PQCLEAN_FALCON$(FALCON_N)_CLEAN_fpr_scaled build-stm32f4/pqclean-clean.sym

objdump-mul:
	arm-none-eabi-objdump \
		--disassemble=PQCLEAN_FALCON$(FALCON_N)_CLEAN_fpr_mul \
		--no-show-raw-insn \
		build-stm32f4/obj/fpr.o > lss/fpr_mul.s
	arm-none-eabi-objdump -S \
		--disassemble=PQCLEAN_FALCON$(FALCON_N)_CLEAN_fpr_mul \
		--no-show-raw-insn \
		build-stm32f4/obj/fpr.o > lss/fpr_mul.lss
	grep -E PQCLEAN_FALCON$(FALCON_N)_CLEAN_fpr_mul build-stm32f4/pqclean-clean.sym
