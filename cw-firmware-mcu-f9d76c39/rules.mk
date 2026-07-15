# SPDX-License-Identifier: Apache-2.0 or CC0-1.0

# Hey Emacs, this is a -*- makefile -*-
#----------------------------------------------------------------------------
#
# Makefile for ChipWhisperer Victims
#
#----------------------------------------------------------------------------
# On command line:
#
# make all = Make software.
#
# make clean = Clean out built project files.
#
# make program = Download the hex file to the device, using avrdude.
#                Please customize the avrdude settings below first!
#
# make debug = Start either simulavr or avarice as specified for debugging,
#              with avr-gdb or avr-insight as the front end for debugging.
#
# make filename.s = Just compile filename.c into the assembler code only.
#
# make filename.i = Create a preprocessed source file for use in submitting
#                   bug reports to the GCC project.
#
# To rebuild project do "make clean" then "make all".
#----------------------------------------------------------------------------

$(OBJDIR):
	mkdir -p $(OBJDIR)

# PQClean/test/Makefile, line 58-59
$(SCHEME_LIBRARY): $(SCHEME_FILES)
	cd $(SCHEME_DIR) && $(MAKE)

# Create preprocessed source for use in sending a bug report.
%.i : %.c
	@echo "   CC    $@ $<"
	$(CC) -E $(MCU_FLAGS) -I. $(CFLAGS) $< -o $@

# Compile: create assembler files from C source files.
%.s : %.c
	@echo "   CC    $@ $<"
	$(CC) -S $(ALL_CFLAGS) $< -o $@

# Create ld script
$(BUILD)/ldscript.ld: $(LDSCRIPT)
	@echo "LDSCRIPT $@"
	@[ -d $(@D) ] || mkdir -p $(@D)
	@$(CC) -x assembler-with-cpp -E -Wp,-P $(ASFLAGS) $< -o $@

# Compile: create object files from C source files.
$(OBJDIR)/%.o: CFLAGS += -Wa,-adhlns=$(@:.o=.lst)
ifeq ($(CPPSRC),)  # if this is a C project, then use gcc
$(OBJDIR)/%.o : %.c | $(OBJDIR)
	@echo "   CC    $@ $<"
	@[ -d $(@D) ] || mkdir -p $(@D)
	@$(CC) -c $(ALL_CFLAGS) $< -o $@
else  # if this is a C++ project, then use g++
$(OBJDIR)/%.o : %.c | $(OBJDIR)
	@echo "   CPP   $@ $<"
	@[ -d $(@D) ] || mkdir -p $(@D)
	@$(CXX) -c $(ALL_CFLAGS) $< -o $@
endif

# Compile: create object files from C++ source files.
$(OBJDIR)/%.o : %.cpp | $(OBJDIR)
	@echo "   CPP   $@ $<"
	@[ -d $(@D) ] || mkdir -p $(@D)
	@$(CXX) -c $(ALL_CFLAGS) $< -o $@

# Assemble: create object files from assembler source files.
$(OBJDIR)/%.o: ASFLAGS += -Wa,-adhlns=$(@:.o=.lst)
$(OBJDIR)/%.o : %.S | $(OBJDIR)
	@echo "   AS    $@ $<"
	@[ -d $(@D) ] || mkdir -p $(@D)
	@$(CC) -c $(ALL_ASFLAGS) $< -o $@

# Link: create ELF output file from object files.
$(BUILD)/%.elf: $(OBJ)
	@echo "   LD    $@ $(OBJDIR)/*.o $(if $(VERBOSE), $(LDFLAGS),)"
	@$(LD) $(ALL_CFLAGS) $^ --output $@ $(LDFLAGS)

# Create load hex file for Flash from ELF output file.
$(BUILD)/%.hex: $(BUILD)/%.elf
	@echo "OBJCOPY  $@ $<"
	@$(OBJCOPY) -O ihex -R .eeprom -R .fuse -R .lock -R .signature $< $@

# Create load bin file for Flash from ELF output file.
$(BUILD)/%.bin: $(BUILD)/%.elf
	@echo "OBJCOPY  $@ $<"
	@$(OBJCOPY) -O binary -R .eeprom -R .fuse -R .lock -R .signature $< $@

# Create load file for EEPROM from ELF output file.
$(BUILD)/%.eep: $(BUILD)/%.elf
	@echo "OBJCOPY  $@ $<"
	@$(OBJCOPY) -j .eeprom --set-section-flags=.eeprom="alloc,load" \
	--change-section-lma .eeprom=0 --no-change-warnings -O ihex $< $@

# Create extended listing file from ELF output file.
$(BUILD)/%.lss: $(BUILD)/%.elf
	@echo "OBJDUMP  $@ -h -S -z $<"
	@$(OBJDUMP) -hSz $< > $@

# Create a symbol table from ELF output file.
$(BUILD)/%.sym: $(BUILD)/%.elf
	@echo "   NM    $@ -n $<"
	@$(NM) -n -l $< > $@

# Change the build target to build a HEX file or a library.
build: ldscript elf hex bin eep lss sym sizeafter
ldscript: $(BUILD)/ldscript.ld
elf: $(BUILD)/$(TESTFILE).elf
hex: $(BUILD)/$(TESTFILE).hex
bin: $(BUILD)/$(TESTFILE).bin
eep: $(BUILD)/$(TESTFILE).eep
lss: $(BUILD)/$(TESTFILE).lss
sym: $(BUILD)/$(TESTFILE).sym
#build: lib

sizeafter:
	@echo Size after:
	@$(SIZE) $(BUILD)/$(TESTFILE).elf
	@$(SIZE) --target=ihex $(BUILD)/$(TESTFILE).hex

# Target: clean project.
clean:
	@echo Cleaning project
	@$(foreach suffix, .hex .eep .bin .cof .elf .map .sym .lss, \
		$(RM) $(BUILD)/$(TESTFILE)$(suffix);)
	@$(RM) $(BUILD)/ldscript.ld
	@$(RM) $(BUILD)/*.a
	@$(RM) -r $(OBJDIR)/*.o
	@$(RM) -r $(OBJDIR)/*.lst
	@$(RM) -r $(OBJDIR)/$(SCHEME_PATH)/*.o
	@$(RM) -r $(OBJDIR)/$(SCHEME_PATH)/*.lst

# Listing of phony targets.
.PHONY : all sizeafter build ldscript elf hex bin eep lss sym clean

$(TESTFILE_BUILD):
	@$(MAKE) build \
	    TARGET=$(TARGET) \
	    SCHEME=$(word 1,$(subst -, ,$@)) \
	    IMPL=$(word 2,$(subst -, ,$@)) \
	    TEST=$(word 3,$(subst -, ,$@))

$(TESTFILE_CLEAN):
	@$(MAKE) clean \
	    TARGET=$(TARGET) \
	    SCHEME=$(word 1,$(subst -, ,$@)) \
	    IMPL=$(word 2,$(subst -, ,$@)) \
	    TEST=$(word 3,$(subst -, ,$@))

$(info +--------------------------------------------------------)
$(info + target: $(TARGET))
$(info + test file: $(TESTFILE))
$(info + simple serial version: $(SS_VER))
$(info + optimization level: $(OPT))
$(info + scheme dir: $(SCHEME_DIR))
$(info +--------------------------------------------------------)

platform-family-filter:  # there is only one left: CW308_AURIX
	$(info $(filter-out $(FAMILY_XMEGA), \
		$(filter-out $(FAMILY_RISCV), \
		$(filter-out $(FAMILY_ARM), $(PLATFORM_LIST)))))
