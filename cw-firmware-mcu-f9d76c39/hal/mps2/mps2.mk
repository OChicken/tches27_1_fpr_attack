# SPDX-License-Identifier: Apache-2.0 or CC0-1.0

MPS2_DATA_IN_FLASH = 1
SRC += mps2_hal.c
# EXTRAINCDIRS += $(HALPATH)/mps2

ASRC += mps2_startup.S
LDSCRIPT = mps2.ld

MCU_FLAGS = -mcpu=cortex-m4

#Output Format = Binary for this target
FORMAT = binary

CFLAGS += -mthumb -mfloat-abi=soft -fmessage-length=0 -ffunction-sections
CPPFLAGS += -mthumb -mfloat-abi=soft -fmessage-length=0 -ffunction-sections
ASFLAGS += -mthumb -mfloat-abi=hard -fmessage-length=0 -ffunction-sections -mfpu=fpv4-sp-d16
ASFLAGS += $(if $(MPS2_DATA_IN_FLASH),-DDATA_IN_FLASH)

CDEFS += -DMPS2
CDEFS += -DSTM32F303xC -DSTM32F3 -DSTM32 -DDEBUG
CPPDEFS += -DSTM32F303xC -DSTM32F3 -DSTM32 -DDEBUG


QEMU = qemu-system-arm
QEMUFLAGS = -M mps2-an386 -nographic -semihosting
