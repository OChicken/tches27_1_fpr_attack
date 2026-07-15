"""
Collect ETM cycle-location traces for three leakage targets in Falcon's FFT.

The address (addr_global, rel_start, rel_end) and expected_delta of each leakage
target vary with OPT, so they all live in cycloc_params.json, keyed as
OPT -> leakage -> {addr_global, rel_start, rel_end, expected_delta -> FALCON_N}.
The values below are for OPT=O0:

  leakage   addr_global  rel_start  rel_end
  --------  -----------  ---------  -------
  scaled    0x08000e00   0x00       0x80
  mul       0x08000fc0   0x28       0x50
  shift55   0x08000fc0   0x5c       0x8a

  expected_delta (addr1-addr0 period of ETM events):
  leakage   Falcon512              Falcon1024
  --------  ---------------------  ----------------------
  scaled    [134]                  [134]
  mul       [100, 282, 100, 1095]  [100, 282, 100, 1095]
  shift55   [100, 282, 100, 1095]  [100, 282, 100, 1095]

For each key and each leakage target, two ETM breakpoints are set via
TraceWhisperer (rule 0 = rel_start, rule 1 = rel_end).

The collected data is a dict:
{
  key_0: [[start_0, end_0], ..., [start_{N-1}, end_{N-1}]],
  key_1: [[start_0, end_0], ..., [start_{N-1}, end_{N-1}]],
  ...,
  key_n: [[start_0, end_0], ..., [start_{N-1}, end_{N-1}]]
}
Here, n=100. We attack 100 key-pair.

For profiling keys, the data dict is:
{
  -22: [[start_0, end_0], ..., [start_{N-1}, end_{N-1}]],
  -21: [[start_0, end_0], ..., [start_{N-1}, end_{N-1}]],
  ...,
   -1: [[start_0, end_0], ..., [start_{N-1}, end_{N-1}]],
    0: [[start_0, end_0], ..., [start_{N-1}, end_{N-1}]],
    1: [[start_0, end_0], ..., [start_{N-1}, end_{N-1}]],
  ...,
   21: [[start_0, end_0], ..., [start_{N-1}, end_{N-1}]],
   22: [[start_0, end_0], ..., [start_{N-1}, end_{N-1}]]
}

saved as a pickle under

data-falcon512/
├── attack/
│   ├── loc_mul_f.pkl
│   ├── loc_mul_g.pkl
│   ├── loc_scaled_f.pkl
│   ├── loc_scaled_g.pkl
│   ├── loc_shift55_f.pkl
│   └── loc_shift55_g.pkl
└── profile/
    ├── loc_mul.pkl
    ├── loc_scaled.pkl
    └── loc_shift55.pkl

ETM occasionally drops an event; rm_etm_abnormal() detects and repairs this. If
it fails (unrecognized delta), the loop breaks and partial results are saved,
allowing the next run to resume from where it left off.

Usage:
  python cycloc.py OPT LEAKAGE FALCON_N KEY_TYPE KEY_ID_LB KEY_ID_UB
"""

import sys
import json
import os
import time
import math
import numpy as np
import pickle
from setup_generic import hardware_setup, clkgen_freq_setup, scope_reset, \
    tracewhisperer_husky_setup
from setup_generic import input2hex, cw_core_routine

MCU_FREQ = 25_000_000
PPC = 8
HUSKY_MAX_SAMPLES = 131070
PROGRAM = True

def rm_etm_abnormal(loc, expected_deltas, tol=10):
    """
    Fix ETM missing-event anomalies in loc.

    When ETM misses one event, its delta is absorbed into the next,
    giving delta ≈ expected[pos] + expected[pos+1].
    Detects this and inserts a synthetic entry to repair it.

    loc:             list of [cycle, rule] from cw_core_routine
    expected_deltas: cyclic list of expected inter-event deltas
    tol:             matching tolerance
    """
    n = len(expected_deltas)
    result = [loc[0]]
    pos = 0  # current position in the expected_deltas cycle

    for i in range(1, len(loc)):
        delta    = loc[i][0] - result[-1][0]
        exp      = expected_deltas[ pos      % n]
        exp_next = expected_deltas[(pos + 1) % n]

        if abs(delta - exp) <= tol:  # >
            result.append(loc[i])
            pos += 1
        elif abs(delta - (exp + exp_next)) <= tol:  # >
            # one event was missed: insert the synthetic entry, then snap the
            # real event onto the grid (discard the A-sync timing jitter)
            result.append([result[-1][0] + exp, 0])
            result.append([result[-1][0] + exp_next, loc[i][1]])
            pos += 2
        else:
            raise ValueError(
                f"index {i}: delta={delta}, "
                f"expected {exp} (normal) or {exp + exp_next} (anomaly)"
            )

    return result


def cycloc_pair(cmd, text, addr_global, rel_start, rel_end,
                scope, target, tracewhisperer):
    while True:
        _, loc0 = cw_core_routine(cmd, text, scope, target, tracewhisperer,
                                  addr_global, rel_start, rel_end, 0)
        data = ''
        while 'z00\n' not in data:
            data += target.read(num_char=0xffff)
        target.flush()
        if len(loc0) == 0:
            print("Detect len(loc0) = 0, retry.")
            continue
        break
    while True:
        _, loc1 = cw_core_routine(cmd, text, scope, target, tracewhisperer,
                                  addr_global, rel_start, rel_end, 1)
        data = ''
        while 'z00\n' not in data:
            data += target.read(num_char=0xffff)
        target.flush()
        if len(loc1) == 0:
            print("Detect len(loc1) = 0, retry.")
            continue
        break
    return loc0, loc1


def cycloc(addr_global, rel_start, rel_end, expected_delta,
           scope, target, tracewhisperer):
    if os.path.exists(LOC_FILE):
        with open(LOC_FILE, 'rb') as f:
            loc = pickle.load(f)
    else:
        loc = {}
    logn = int(math.log2(FALCON_N))
    logn = logn.to_bytes(1, byteorder='little')
    for key_id in range(KEY_ID_LB, KEY_ID_UB):
        print(f"key {key_id:2}")
        key = key_list[key_id]
        if type(key) is not list:
            key = key.tolist()
        target.write('k' + input2hex(key) + '\n')
        data = target.read(num_char=0xffff)
        print(data[:-5])
        target.flush()
        loc0, loc1 = cycloc_pair('p', logn, addr_global, rel_start, rel_end,
                                 scope, target, tracewhisperer)
        try:
            loc0 = rm_etm_abnormal(loc0, expected_delta)
            loc1 = rm_etm_abnormal(loc1, expected_delta, tol=15)
        except ValueError as e:
            print(f"  ETM error at key {key_id}: {e}")
            print(f"  Saving {len(loc)} keys collected so far...")
            break
        loc[key_id] = [[loc0[i][0], loc1[i][0]] for i in range(FALCON_N)]
    with open(LOC_FILE, 'wb') as f:
        pickle.dump(dict(sorted(loc.items())), f)


if __name__ == '__main__':
    OPT         =     sys.argv[1]
    LEAKAGE     =     sys.argv[2]
    FALCON_N    = int(sys.argv[3])
    KEY_TYPE    =     sys.argv[4]
    KEY_ID_LB   = int(sys.argv[5])
    KEY_ID_UB   = int(sys.argv[6])
    print(LEAKAGE)

    # Address and expected_delta vary with OPT, so they live in
    # cycloc_params.json keyed as OPT -> LEAKAGE -> {addr_global, rel_start,
    # rel_end, expected_delta -> FALCON_N}.
    with open("cycloc_params.json") as f:
        json_file = json.load(f)
        name = json_file["name"]
        cfg = json_file[OPT][LEAKAGE]
    addr_global    = int(cfg["addr_global"], 0)
    rel_start      = int(cfg["rel_start"], 0)
    rel_end        = int(cfg["rel_end"], 0)
    expected_delta = cfg["expected_delta"][str(FALCON_N)]

    # loc_file ################################################################
    if KEY_TYPE == 'profile':
        LOC_FILE = f"{OPT}-falcon{FALCON_N}/traces_profile/loc_{LEAKAGE}.pkl"
    else:
        LOC_FILE = f"{OPT}-falcon{FALCON_N}/traces_attack/loc_{LEAKAGE}_{KEY_TYPE}.pkl"

    # load keys ###############################################################
    if KEY_TYPE == 'profile':
        KEY_FILE = f"keys/Falcon{FALCON_N}_profile.pkl"
        with open(KEY_FILE, 'rb') as f:
            key_list = pickle.load(f)  # dict: coeff -> [coeff]*FALCON_N
    else:
        KEY_FILE = f"keys/Falcon{FALCON_N}_{KEY_TYPE}_1000.npy"
        key_list = np.load(KEY_FILE, allow_pickle=True)
    print(KEY_FILE)

    # set CW ##################################################################
    scope, target = hardware_setup(f"{OPT}-falcon{FALCON_N}/build-stm32f4/{name}",
                                   'stm32f4', "SS_VER_1_0", PROGRAM)
    scope_reset(scope)
    tracewhisperer = tracewhisperer_husky_setup(scope, target)
    scope_reset(scope)
    clkgen_freq_setup(scope, target, MCU_FREQ)

    target.flush()
    scope_reset(scope)
    print("HELLO?", target.read())
    scope.clock.adc_mul = PPC
    scope.adc.samples = HUSKY_MAX_SAMPLES
    scope.gain.db = 12
    time.sleep(1)

    cycloc(addr_global, rel_start, rel_end, expected_delta,
           scope, target, tracewhisperer)

    print("Close CW.")
    target.dis()
    scope.dis()
