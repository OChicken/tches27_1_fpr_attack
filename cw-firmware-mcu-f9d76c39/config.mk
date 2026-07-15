# SPDX-License-Identifier: Apache-2.0 or CC0-1.0

# Flag to enable verbose output.
VERBOSE ?=

# Build files directory
BUILD = build-$(TARGET)

# Object files directory
#     To put object files in current directory, use a dot (.), do NOT make
#     this an empty or blank macro!
OBJDIR = $(BUILD)/obj

# Define all object files.
OBJ += $(addprefix $(OBJDIR)/,$(SRC:.c=.o))
OBJ += $(addprefix $(OBJDIR)/,$(CPPSRC:.cpp=.o))
OBJ += $(addprefix $(OBJDIR)/,$(ASRC:.S=.o))

# List C source files here. (C dependencies are automatically generated.)
SRC +=

# List C++ source files here. (C dependencies are automatically generated.)
CPPSRC +=


# List Assembler source files here.
#     Make them always end in a capital .S.  Files ending in a lowercase .s
#     will not be considered source files but generated files (assembler
#     output from the compiler), and will be deleted upon "make clean"!
#     Even though the DOS/Win* filesystem matches both .s and .S the same,
#     it will preserve the spelling of the filenames, and gcc itself does
#     care about how the name is spelled on its command-line.
ASRC +=

ifeq ($(CPPSRC),)
  LD=$(CC)
else
  LD=$(CXX)
endif

# Optimization level, can be [0, 1, 2, 3, s].
#     0 = turn off optimization. s = optimize for size.
#     (Note: 3 is not always the best optimization level. See avr-libc FAQ.)
OPT ?= -Os
CFLAGS += $(OPT)

# Debugging format.
#     Native formats for AVR-GCC's -g are dwarf-2 [default] or stabs.
#     AVR Studio 4.10 requires dwarf-2.
#     AVR [Extended] COFF format requires stabs, plus an avr-objcopy run.
DEBUG = dwarf-2


# THIS FLAG IS OUTDATED!
# List any extra directories to look for include files here.
#     Each directory must be seperated by a space.
#     Use forward slashes for directory separators.
#     For a directory that has spaces, enclose it in quotes.
# EXTRAINCDIRS +=


# Compiler flag to set the C Standard level.
#     c89   = "ANSI" C
#     gnu89 = c89 plus GCC extensions
#     c99   = ISO C99 standard (not yet fully implemented)
#     gnu99 = c99 plus GCC extensions
ifeq ($(CPPSRC),)
  CFLAGS += -std=gnu99
endif

# Place -D or -U options here for C sources
CDEFS += -DF_CPU=$(F_CPU)UL -DSS_VER_2_0=2 -DSS_VER_2_1=3 -DSS_VER_1_1=1 -DSS_VER_1_0=0
CDEFS += $(EXTRA_CDEFS)

ifneq ($(filter $(SS_VER), SS_VER_1_0 SS_VER_1_1 SS_VER_2_1),)
  CDEFS += -DSS_VER=$(SS_VER)
else
  $(error Empty or unsupported SS_VER. Known SS_VER: SS_VER_1_0, SS_VER_1_1, SS_VER_2_1)
endif

# Place -D or -U options here for ASM sources
ADEFS += -DF_CPU=$(F_CPU)


# Place -D or -U options here for C++ sources
CPPDEFS += -DF_CPU=$(F_CPU)UL
#CPPDEFS += -D__STDC_LIMIT_MACROS
#CPPDEFS += -D__STDC_CONSTANT_MACROS



#---------------- Compiler Options C ----------------
#  -g*:          generate debugging information
#  -O*:          optimization level
#  -f...:        tuning, see GCC manual and avr-libc documentation
#  -Wall...:     warning level
#  -Wa,...:      tell GCC to pass this to the assembler.
#    -adhlns...: create assembler listing
CFLAGS += -g$(DEBUG)
CFLAGS += $(CDEFS)
CFLAGS += -funsigned-char
CFLAGS += -funsigned-bitfields
# Note: -fpack-struct is dangerous! This is only included in XMEGA/AVR HAL
#CFLAGS += -fpack-struct
CFLAGS += -fshort-enums
CFLAGS += -Wall
#CFLAGS += -mshort-calls
#CFLAGS += -fno-unit-at-a-time
#CFLAGS += -Wundef
#CFLAGS += -Wunreachable-code
#CFLAGS += -Wsign-compare
# CFLAGS += $(patsubst %,-I%,$(EXTRAINCDIRS))
ifeq ($(CPPSRC),)
  CFLAGS += -Wstrict-prototypes -Wno-strict-prototypes
  CFLAGS += -Wno-discarded-qualifiers -Wno-missing-prototypes
  CFLAGS += -Wno-pointer-sign
endif
CFLAGS +=  -Wno-unused-function -Wno-unused-variable
CFLAGS += -Wno-unused-value
CFLAGS += -fdiagnostics-color=always
#CFLAGS += -fno-strict-aliasing


#Flags that must come at end of list can be specified with CFLAGS_LAST
CFLAGS += $(CFLAGS_LAST)

# has to come after we hijack for CPP flags


#---------------- Assembler Options ----------------
#  -Wa,...:   tell GCC to pass this to the assembler.
#  -adhlns:   create listing
#  -gstabs:   have the assembler create line number information; note that
#             for use in COFF files, additional information about filenames
#             and function names needs to be present in the assembler source
#             files -- see avr-libc docs [FIXME: not yet described there]
#  -listing-cont-lines: Sets the maximum number of continuation lines of hex
#       dump that will be displayed for a given single line of source input.

#-adhlns=$(<:%.S=$(OBJDIR)/%.lst),
#,--listing-cont-lines=100

ASFLAGS += $(ADEFS) -Wa,-gstabs,-adhlns=$(addprefix $(OBJDIR)/,$(notdir $(<:%.S=%.lst)))
# ASFLAGS += $(patsubst %,-I%,$(EXTRAINCDIRS))


#---------------- Library Options ----------------
# Minimalistic printf version
PRINTF_LIB_MIN = -Wl,-u,vfprintf -lprintf_min

# Floating point printf version (requires MATH_LIB = -lm below)
PRINTF_LIB_FLOAT = -Wl,-u,vfprintf -lprintf_flt

# If this is left blank, then it will use the Standard printf version.
PRINTF_LIB =
#PRINTF_LIB = $(PRINTF_LIB_MIN)
#PRINTF_LIB = $(PRINTF_LIB_FLOAT)


# Minimalistic scanf version
SCANF_LIB_MIN = -Wl,-u,vfscanf -lscanf_min

# Floating point + %[ scanf version (requires MATH_LIB = -lm below)
SCANF_LIB_FLOAT = -Wl,-u,vfscanf -lscanf_flt

# If this is left blank, then it will use the Standard scanf version.
SCANF_LIB =
#SCANF_LIB = $(SCANF_LIB_MIN)
#SCANF_LIB = $(SCANF_LIB_FLOAT)

# List any extra directories to look for libraries here.
#     Each directory must be seperated by a space.
#     Use forward slashes for directory separators.
#     For a directory that has spaces, enclose it in quotes.
EXTRALIBDIRS =

#---------------- Linker Options ----------------
#  -Wl,...:     tell GCC to pass this to linker.
#    -Map:      create map file
#    --cref:    add cross reference to  map file
LDFLAGS += -Wl,-Map=$(BUILD)/$(TESTFILE).map,--cref
LDFLAGS += $(EXTMEMOPTS)
LDFLAGS += $(patsubst %,-L%,$(EXTRALIBDIRS))
LDFLAGS += -lm
LDFLAGS += $(PRINTF_LIB) $(SCANF_LIB)
LDFLAGS += --specs=nosys.specs
LDFLAGS += -Wl,--gc-sections
LDFLAGS += -Wl,--print-memory-usage
LDFLAGS += -T $(BUILD)/ldscript.ld
#LDFLAGS += -T linker_script.x

#---------------- External Memory Options ----------------

# 64 KB of external RAM, starting after internal RAM (ATmega128!),
# used for variables (.data/.bss) and heap (malloc()).
#EXTMEMOPTS = -Wl,-Tdata=0x801100,--defsym=__heap_end=0x80ffff

# 64 KB of external RAM, starting after internal RAM (ATmega128!),
# only used for heap (malloc()).
#EXTMEMOPTS = -Wl,--section-start,.data=0x801100,--defsym=__heap_end=0x80ffff

EXTMEMOPTS =

# Combine all necessary flags and optional flags.
# Add target processor to flags.
ALL_CFLAGS = $(MCU_FLAGS) -I. $(CFLAGS)
ALL_ASFLAGS = $(MCU_FLAGS) -I. -x assembler-with-cpp $(ASFLAGS)

###############################################################################
#                                   Commands                                  #
###############################################################################

CC = arm-none-eabi-gcc
CXX = arm-none-eabi-g++
OBJCOPY = arm-none-eabi-objcopy
OBJDUMP = arm-none-eabi-objdump
SIZE = arm-none-eabi-size
AR = arm-none-eabi-ar rcs
NM = arm-none-eabi-nm
RM = rm -f

###############################################################################
#                            PQClean/test/Makefile                            #
###############################################################################

# You should specify 3 variables: TEST, SCHEME, IMPLEMENTATION

# the tested binary name format (functest, nistkat, printparams, testvectors, etc)
TESTFILE ?= $(TEST)_$(SCHEME)_$(IMPLEMENTATION)
# line 10-11
SCHEME_UPPERCASE=$(shell echo $(SCHEME) | tr a-z A-Z | sed 's/-//g')
IMPLEMENTATION_UPPERCASE=$(shell echo $(IMPLEMENTATION) | tr a-z A-Z | sed 's/-//g')
# 4 occurrences
CFLAGS+=-I$(SCHEME_DIR) -I$(COMMON_DIR)
CDEFS+=-DPQCLEAN_NAMESPACE=PQCLEAN_$(SCHEME_UPPERCASE)_$(IMPLEMENTATION_UPPERCASE)

###############################################################################
#                                     hal                                     #
###############################################################################

include $(FIRMWAREPATH)/hal/hal.mk
