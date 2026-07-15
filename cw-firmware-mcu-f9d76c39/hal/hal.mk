# SPDX-License-Identifier: Apache-2.0 or CC0-1.0

# Processor frequency (external freq-in)
ifndef F_CPU
F_CPU = 7372800
endif

ifeq ($(DEMO),SECCAN)
	CFLAGS += -DSECCAN
endif

ifeq ($(MCU_CLK), INT)
  CFLAGS += -DUSE_INTERNAL_CLK
endif

VPATH += $(FIRMWAREPATH)/hal
VPATH += $(FIRMWAREPATH)/hal/$(TARGET)
VPATH += $(FIRMWAREPATH)/hal/driver/$(TARGET)/Src

# Default stuff
CFLAGS += -I$(HOME)/arm/CMSIS_6/CMSIS/Core/Include/
CFLAGS += -I$(FIRMWAREPATH)/hal
CFLAGS += -I$(FIRMWAREPATH)/hal/$(TARGET)
CFLAGS += -I$(FIRMWAREPATH)/hal/driver/$(TARGET)/Inc

SRC += hal.c
include $(FIRMWAREPATH)/hal/$(TARGET)/$(TARGET).mk
CDEFS += -DHAL_TYPE=HAL_$(TARGET) -DTARGET=$(TARGET)

#ifneq ($(filter $(PLATFORM), $(FAMILY_ARM)),)
CFLAGS += -DPLATFORM_ARM
LDFLAGS += \
	-Wl,--wrap=_sbrk \
	-Wl,--wrap=_open
#endif
