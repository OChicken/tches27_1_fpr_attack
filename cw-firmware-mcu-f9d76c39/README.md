# ChipWhisperer firmware mcu

The hal facilities of https://github.com/newaetech/chipwhisperer/firmware/mcu

Currently only guarantee support stm32f4.

Some function interfaces are heavily modified. Use it at your own risk.

## Features

### Improvements over pqm4 ([mupq/pqm4](https://github.com/mupq/pqm4))

- **Familiar printf support**: Use the standard `printf()` function directly in your code, instead of the custom `hal_send_str()` required by pqm4
- **ChipWhisperer compatibility**: Full ChipWhisperer integration, whereas pqm4 uses libopencm3 which is not suitable for porting ChipWhisperer functionality

### Improvements over ChipWhisperer

- **Simplified SimpleSerial 1.0 interface**: Improved version of CW's SimpleSerial 1.1 and 1.2, providing a familiar C function interface:
  ```c
  uint8_t func(uint8_t *in, uint32_t len)
  ```
  Just like standard C function interfaces you're already familiar with.

- **No transfer length limitations**: SimpleSerial 1.1 and 1.2 limit data transfers to 64 bytes per transaction. SimpleSerial 1.0 has no such restriction - you can transfer 1000+ bytes to the device in a single transaction, which is sufficient for most research purposes. (Note: extremely long transfers have not been extensively tested but are not typically needed for practical research use cases)

- **Modern ARM HAL**: Uses CMSIS_6, the current ARM hardware abstraction layer, in contrast to ChipWhisperer's use of the outdated CMSIS_4

- **Simplified Makefile**: Easier to use and understand build system

### Three Ways to Run Your Code

This project provides flexibility in how you develop and test your firmware:

1. **MPS2 support** (adapted from pqm4): Perform initial debugging on your PC without needing to flash the chip, saving significant development time by avoiding the lengthy chip programming process

2. **Standalone test with run.py**: Simply use `run.py script.py` to test cycle usage on the chip - similar to running a "hello world" C program

3. **ChipWhisperer Jupyter notebook**: Interactive chip communication using SimpleSerial 1.0 protocol via ipynb scripts

## How to Use

_Note: This section is under development. Full documentation and demos will be added to this repository._

### Step 1: Prepare your own CMSIS

```shell
cd
mkdir arm && cd $_
git clone https://github.com/ARM-software/CMSIS_6.git
git clone https://github.com/STMicroelectronics/cmsis-device-f3.git
git clone https://github.com/STMicroelectronics/cmsis-device-f4.git
```

### Step 2: Continue the build

Read `demo/README.org` for more details.
