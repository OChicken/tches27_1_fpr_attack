#!/usr/bin/python

"""
Usage:
    python run.py <filename> [-s 1.1 -f 7363636 -p True]
where [program] if is some char (no matter what), would write to target;
                if it's not given, it will read from target.
"""

import os
import sys
import argparse
import re
from datetime import datetime
from setup_generic import hardware_setup, scope_reset, clkgen_freq_setup


def str_to_bool(program):
    """Convert a string to a boolean value."""
    if program.lower() in ('true', '1'):
        return True
    elif program.lower() in ('false', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError(
            f"Invalid boolean value: {program}. Use 'True' or 'False'.")


def set_ss_version(ss_ver):
    """Set simple serial version."""
    if ss_ver == '1.0':
        return "SS_VER_1_0"
    elif ss_ver == '1.1':
        return "SS_VER_1_1"
    elif ss_ver == '2.1':
        return "SS_VER_2_1"
    else:
        print(f"Invalid ss_ver value: {ss_ver}. "
              f"Only 1.0 or 1.1 or 2.1 are accepted.")
        sys.exit(1)


def parse_arg():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="cw-firmware-mcu run")
    parser.add_argument(
        'filename', type=str, help='The hex file to be programmed.')
    parser.add_argument(
        '-p', '--program',
        type=str_to_bool, default=True, help='Program flag (default: True)')
    parser.add_argument(
        '-s', '--ss_ver',
        type=set_ss_version, default='SS_VER_1_1', help='SS version to be set')
    parser.add_argument(
        '-f', '--freq',
        type=int, default=30000000, help='MCU frequency.')
    args = parser.parse_args()
    filename = args.filename
    platform = re.match(r'.*build-(.*?)/.*\.hex', filename).group(1)
    program = args.program
    ss_ver = args.ss_ver
    freq = args.freq

    if not os.path.exists(filename):
        print(f"File '{filename}' does not exist. Exiting.")
        sys.exit(1)

    return filename, platform, program, ss_ver, freq


if __name__ == '__main__':
    filename, platform, program, ss_ver, freq = parse_arg()
    scope, target = hardware_setup(filename, platform, ss_ver, program)
    if freq:
        clkgen_freq_setup(scope, target, freq)
    print(datetime.now().strftime("%H:%M:%S.%f"))

    target.flush()
    scope_reset(scope, platform)
    data = ''
    it = 0
    while 'z00\n' not in data:
        it += 1
        data = target.read(num_char=0xffff)
        if data:
            print(data[:-1])
    print("How many times to call target.read()?:", it)
    print(datetime.now().strftime("%H:%M:%S.%f"))

    scope.dis()
    target.dis()
