#!/bin/python

"""Helper scripts generic setup."""

import chipwhisperer as cw
import time
import subprocess
from pathlib import Path

###############################################################################
#                                ChipWhisperer                                #
###############################################################################

def target_set(scope, SS_VER):
    """Set target according to SS version (SS_VER)."""
    try:
        if SS_VER == "SS_VER_2_1":
            target_type = cw.targets.SimpleSerial2
        elif SS_VER == "SS_VER_2_0":
            raise OSError("SS_VER_2_0 is deprecated. Use SS_VER_2_1")
        else:
            target_type = cw.targets.SimpleSerial
    except Exception:
        SS_VER = "SS_VER_1_1"
        target_type = cw.targets.SimpleSerial
    try:
        target = cw.target(scope, target_type)
    except Exception:
        print("INFO: Caught exception on reconnecting to target - attempting "
              "to reconnect to scope first.")
        print("INFO: This is a work-around when USB has died without Python "
              "knowing. Ignore errors above this line.")
        scope = cw.scope()
        target = cw.target(scope, target_type)
    print("INFO: Found ChipWhisperer 😍")
    return target


def prog_set(platform):
    """Set program according to platform."""
    if "stm" in platform or platform in ("CWLITEARM" "CWNANO"):
        return cw.programmers.STM32FProgrammer
    elif platform == "xmega" or platform in ("CW303" "CWLITEXMEGA"):
        return cw.programmers.XMEGAProgrammer
    elif "neorv32" in platform.lower():
        return cw.programmers.NEORV32Programmer
    elif platform in ("CW312_SAM4S" "CWHUSKY"):
        return cw.programmers.SAM4SProgrammer
    else:
        return None


def scope_reset(scope, platform="stm32f4"):
    """Reset target."""
    if platform in ("CW303" "CWLITEXMEGA"):
        scope.io.pdic = 'low'
        time.sleep(0.1)
        scope.io.pdic = 'high_z'  # XMEGA doesn't like pdic driven high
        time.sleep(0.1)  # xmega needs more startup time
    elif "neorv32" in platform.lower():
        raise IOError("Default iCE40 neorv32 build does not have external "
                      "reset - reprogram device to reset")
    elif platform in ("CW312_SAM4S" "CWHUSKY"):
        scope.io.nrst = 'low'
        time.sleep(0.25)
        scope.io.nrst = 'high_z'
        time.sleep(0.25)
    else:
        scope.io.nrst = 'low'
        time.sleep(0.05)
        scope.io.nrst = 'high_z'
        time.sleep(0.05)


def hardware_setup(filename, platform, ss_ver, program):
    """Set up the MCU."""
    scope = cw.scope()

    if not scope.connectStatus:
        scope.con()
    time.sleep(0.05)
    scope.default_setup()
    if scope.latest_fw_str > scope.fw_version_str:
        scope.upgrade_firmware()
        scope.dis()
        time.sleep(3)
        scope = cw.scope()
        scope.con()
        scope.default_setup()

    print("target:", platform)
    print("SS_VER:", ss_ver)
    scope_reset(scope, platform)
    target = target_set(scope, ss_ver)
    prog = prog_set(platform)
    if program:
        cw.program_target(scope, prog, filename)
        print("Program the target success 🎉")
    else:
        print("The target is NOT programmed; it's original setting is kept 😗")
    ring_bell()

    return scope, target


def ring_bell():
    """Play the notification sound; warn (don't crash) if it fails."""
    bell_file = Path(__file__).resolve().with_name("ura.mp3")
    if not bell_file.exists():
        print(f"🔔 bell: file not found: {bell_file}")
        return
    try:
        r = subprocess.run(["paplay", str(bell_file)],
                           capture_output=True, text=True)
    except FileNotFoundError as e:
        print(f"🔔 bell: player not found: {e}")
        return
    if r.returncode != 0:
        print(f"🔔 bell: paplay exited {r.returncode}: {r.stderr.strip()}")


def clkgen_freq_setup(scope, target, mcu_freq):
    """Set clkgen_freq to mcu_freq and adjust target.baud accordingly."""
    clkgen_freq0 = scope.clock.clkgen_freq
    scope.clock.clkgen_freq = mcu_freq
    print(f"scope.clock.clkgen_freq changed from {clkgen_freq0} "
          f"to {scope.clock.clkgen_freq}")
    target_baud0 = target.baud
    target.baud = int(target_baud0 *
                      (scope.clock.clkgen_freq / clkgen_freq0))
    print(f"target.baud changed from {target_baud0} to {target.baud}")


def tracewhisperer_husky_setup(scope, target):
    """Set up the TraceWhisperer on Husky."""
    scope.trace.target = target
    trace = scope.trace
    trace.enabled = True
    # SWO
    trace.clock.fe_clock_src = 'target_clock'  # default: usb_clock
    assert trace.clock.fe_clock_alive, \
           "Hmm, the clock you chose doesn't seem to be active."
    trace.trace_mode = 'SWO'  # default: 'parallel'
    trace.jtag_to_swd()  # switch target into SWO mode
    # Now the complicated bit:
    acpr = 0
    trigger_freq_mul = 8
    trace.clock.swo_clock_freq = scope.clock.clkgen_freq * trigger_freq_mul
    trace.target_registers.TPI_ACPR = acpr
    trace.swo_div = trigger_freq_mul * (acpr + 1)
    assert trace.clock.swo_clock_locked, "Trigger/UART clock not locked"
    assert scope.userio.status & 0x4, "SWO line not high"
    # Disable sync frames for SWO
    trace.target_registers.DWT_CTRL = 0x40000021
    # Trigger trace capture from target FW
    trace.capture.trigger_source = 'firmware trigger'
    # What to capture
    trace.capture.raw = False
    # match on any PC match (isync) trace packet
    trace.set_pattern_match(0, [3, 8, 32])
    # enable matching rule:
    trace.capture.rules_enabled = [0]
    assert trace.capture.trigger_source == 'firmware trigger'
    assert trace.capture.mode == 'while_trig'
    # Set PC addresses to match on
    # trace.set_isync_matches(addr0=ADDR0, addr1=ADDR1, match='both')
    # Enable or disable periodic PC sampling
    trace.set_periodic_pc_sampling(enable=0)
    return trace


def input2hex(x):
    """Return hex representation of input x."""
    if isinstance(x, str):
        return bytes.hex(x.encode())
    elif isinstance(x, (int, float)):
        return f"{int(x) & 0xffffffff:08x}"  # = WORDSIZ * 2. Check WORDSIZ in the *.c file.
    elif isinstance(x, bytes):
        return bytes.hex(x)
    elif isinstance(x, (list, tuple)):
        # Handle int8/uint8 array - convert to bytes then hex
        byte_values = [val & 0xff for val in x]
        return bytes(byte_values).hex()
    else:
        raise TypeError("Input must be a string, number, byte string, or int8/uint8 array.")


def cw_core_routine(cmd, text, scope, target, tracewhisperer=None,
                    addr_global=None, rel_start=None, rel_end=None,
                    match=None, verbose=False):
    """Core routine for ChipWhisperer trace capture with optional TraceWhisperer.

    Sends a command to the target, captures a power trace, and optionally
    records cycle-accurate timing information via TraceWhisperer.

    Args:
        cmd: SimpleSerial command character (e.g., 'k', 'l')
        text: Data to send (will be converted to hex via input2hex)
        scope: ChipWhisperer scope object
        target: ChipWhisperer target object
        tracewhisperer: Optional TraceWhisperer object for cycle timing
        addr_global: Global address offset in executable (required if tracewhisperer)
        rel_start: Relative start address in object file (required if tracewhisperer)
        rel_end: Relative end address in object file (required if tracewhisperer)
        match: Match mode for TraceWhisperer, e.g., 'both' (required if tracewhisperer)

    Returns:
        tuple: (wave, cycle_loc)
            - wave: numpy array of power trace samples
            - cycle_loc: List of [cycle, rule] pairs if tracewhisperer, else None

    Note:
        The ordering is critical: scope.arm() and scope.capture() MUST be called
        BEFORE tracewhisperer.read_capture_data(), even though TraceWhisperer
        doesn't directly interact with the scope's trace capture.
    """
    if tracewhisperer is not None and \
       (addr_global is None or
            rel_start is None or rel_end is None or match is None):
        raise ValueError("If 'tracewhisperer' is provided, "
                         "you should specified the rest parameters.")
    if tracewhisperer is not None:
        tracewhisperer.set_isync_matches(addr_global + rel_start,
                                         addr_global + rel_end, match=match)
        # buf = target.read(num_char=0xffff)
        # print(buf)  # TW does write('s'+...), which produce "z00\n"
        target.flush()
        tracewhisperer.arm_trace()
    scope.arm()
    target.write(cmd + input2hex(text) + '\n')
    ret = scope.capture()
    if ret:
        print('Timeout happened during acquisition')
    wave = scope.get_last_trace()
    if tracewhisperer is not None:
        raw = tracewhisperer.read_capture_data()
        cycle_loc = tracewhisperer.get_rule_match_times(raw,
                                                        rawtimes=False,
                                                        verbose=verbose)
    else:
        cycle_loc = None
    return wave, cycle_loc


###############################################################################
#                       AES Model & Hamming Weight Setup                      #
###############################################################################

SBOX = [
    # 0    1    2    3    4    5    6    7    8    9    a    b    c    d    e    f
    0x63,0x7c,0x77,0x7b,0xf2,0x6b,0x6f,0xc5,0x30,0x01,0x67,0x2b,0xfe,0xd7,0xab,0x76,  # 0
    0xca,0x82,0xc9,0x7d,0xfa,0x59,0x47,0xf0,0xad,0xd4,0xa2,0xaf,0x9c,0xa4,0x72,0xc0,  # 1
    0xb7,0xfd,0x93,0x26,0x36,0x3f,0xf7,0xcc,0x34,0xa5,0xe5,0xf1,0x71,0xd8,0x31,0x15,  # 2
    0x04,0xc7,0x23,0xc3,0x18,0x96,0x05,0x9a,0x07,0x12,0x80,0xe2,0xeb,0x27,0xb2,0x75,  # 3
    0x09,0x83,0x2c,0x1a,0x1b,0x6e,0x5a,0xa0,0x52,0x3b,0xd6,0xb3,0x29,0xe3,0x2f,0x84,  # 4
    0x53,0xd1,0x00,0xed,0x20,0xfc,0xb1,0x5b,0x6a,0xcb,0xbe,0x39,0x4a,0x4c,0x58,0xcf,  # 5
    0xd0,0xef,0xaa,0xfb,0x43,0x4d,0x33,0x85,0x45,0xf9,0x02,0x7f,0x50,0x3c,0x9f,0xa8,  # 6
    0x51,0xa3,0x40,0x8f,0x92,0x9d,0x38,0xf5,0xbc,0xb6,0xda,0x21,0x10,0xff,0xf3,0xd2,  # 7
    0xcd,0x0c,0x13,0xec,0x5f,0x97,0x44,0x17,0xc4,0xa7,0x7e,0x3d,0x64,0x5d,0x19,0x73,  # 8
    0x60,0x81,0x4f,0xdc,0x22,0x2a,0x90,0x88,0x46,0xee,0xb8,0x14,0xde,0x5e,0x0b,0xdb,  # 9
    0xe0,0x32,0x3a,0x0a,0x49,0x06,0x24,0x5c,0xc2,0xd3,0xac,0x62,0x91,0x95,0xe4,0x79,  # a
    0xe7,0xc8,0x37,0x6d,0x8d,0xd5,0x4e,0xa9,0x6c,0x56,0xf4,0xea,0x65,0x7a,0xae,0x08,  # b
    0xba,0x78,0x25,0x2e,0x1c,0xa6,0xb4,0xc6,0xe8,0xdd,0x74,0x1f,0x4b,0xbd,0x8b,0x8a,  # c
    0x70,0x3e,0xb5,0x66,0x48,0x03,0xf6,0x0e,0x61,0x35,0x57,0xb9,0x86,0xc1,0x1d,0x9e,  # d
    0xe1,0xf8,0x98,0x11,0x69,0xd9,0x8e,0x94,0x9b,0x1e,0x87,0xe9,0xce,0x55,0x28,0xdf,  # e
    0x8c,0xa1,0x89,0x0d,0xbf,0xe6,0x42,0x68,0x41,0x99,0x2d,0x0f,0xb0,0x54,0xbb,0x16   # f
]


def aes_internal(indata, key):
    """SBOX[indata ^ key]."""
    return SBOX[indata ^ key]


def hw8(a):
    """Hamming weight of 8-bit integer a."""
    a = (a & 0x55) + ((a >> 1) & 0x55)
    a = (a & 0x33) + ((a >> 2) & 0x33)
    a = (a & 0x0F) + ((a >> 4) & 0x0F)
    return a


HW = [hw8(n) for n in range(256)]
