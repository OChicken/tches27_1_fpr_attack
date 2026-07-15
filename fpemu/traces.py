"""
Record power traces for the FALCON-N side-channel attack (fpemu, per-OPT build).

Each run loads a batch of keys [KEY_ID_LB, KEY_ID_UB), records N_TRACE power
traces per key via ChipWhisperer Husky, and saves each trace as a .npy file
under {OPT}/data-falcon{N}/{profile,attack}/.

Arguments (positional):
  OPT        -- optimization-level subdir: O0, O1, O2, O3, or Os.
  FALCON_N   -- Falcon parameter set: 512 or 1024.
  KEY_TYPE   -- 'profile', 'f', or 'g'.
  KEY_ID_LB  -- Inclusive lower bound of the key-ID range to record.
                For KEY_TYPE='profile', KEY_ID is the coefficient value
                (e.g. -22); for KEY_TYPE='f'/'g', it is the key index.
  KEY_ID_UB  -- Exclusive upper bound of the key-ID range.

N_TRACE:
  profile (N_TRACE = 2): Each profiling key is a constant-coefficient vector —
    every one of the FALCON_N positions holds the same value c.  Recording
    2 traces therefore yields FALCON_N × 2 single-coefficient observations for
    label c, which is sufficient to build the profile template.  The profiling
    key set covers all distinct coefficient values: [-22, 22] for Falcon-512
    (45 classes) and [-15, 15] for Falcon-1024 (31 classes).
  attack (N_TRACE = 10): Attack keys are real FALCON private keys whose
    coefficients take mixed values.  Post-processing has shown that 10 traces
    per key are sufficient to guarantee full key recovery.

Usage:
  python traces.py OPT FALCON_N KEY_TYPE KEY_ID_LB KEY_ID_UB
"""

import sys
import json
import time
import math
import numpy as np
import pickle
import subprocess
from datetime import datetime
from setup_generic import hardware_setup, clkgen_freq_setup, scope_reset
from setup_generic import input2hex, cw_core_routine

MCU_FREQ = 25_000_000
PPC = 8
HUSKY_MAX_SAMPLES = 131070
PROGRAM = True


def record_one_key(scope, target):
    scope.adc.offset = 0
    seg_wave = []
    logn = int(math.log2(FALCON_N))
    logn = logn.to_bytes(1, byteorder='little')
    for j in range(N_CONCATENATE):
        tmp, _ = cw_core_routine('p', logn, scope, target)
        data = ''
        while 'z00\n' not in data:
            data += target.read(num_char=0xffff)
        target.flush()
        seg_wave.append(tmp)
        scope.adc.offset += scope.adc.samples
    return np.hstack(seg_wave)


if __name__ == '__main__':
    OPT       =     sys.argv[1]
    FALCON_N  = int(sys.argv[2])
    KEY_TYPE  =     sys.argv[3]
    KEY_ID_LB = int(sys.argv[4])
    KEY_ID_UB = int(sys.argv[5])

    # #concatenate ############################################################
    with open("cycloc_params.json") as f:
        json_file = json.load(f)
        name = json_file["name"]
        cfg = json_file[OPT]
    N_CONCATENATE = cfg["n_concatenate"]

    # load keys ###############################################################
    if KEY_TYPE == 'profile':
        DATA_PATH = f"{OPT}-falcon{FALCON_N}/traces_profile"
        N_TRACE = 6
        KEY_FILE = f"keys/Falcon{FALCON_N}_profile.pkl"
        with open(KEY_FILE, 'rb') as f:
            key_list = pickle.load(f)
    else:
        DATA_PATH = f"{OPT}-falcon{FALCON_N}/traces_attack"
        # #trace/signature to guarantee full key recovery
        # currently post-processing can recover within 10
        N_TRACE = 30
        KEY_FILE = f"keys/Falcon{FALCON_N}_{KEY_TYPE}_1000.npy"
        key_list = np.load(KEY_FILE, allow_pickle=True)
    print(KEY_FILE)

    # set CW ##################################################################
    scope, target = hardware_setup(f"{OPT}-falcon{FALCON_N}/build-stm32f4/{name}",
                                   'stm32f4', "SS_VER_1_0", PROGRAM)
    scope_reset(scope)
    clkgen_freq_setup(scope, target, MCU_FREQ)

    target.flush()
    scope_reset(scope)
    print("HELLO?", target.read())
    scope.clock.adc_mul = PPC
    scope.adc.samples = HUSKY_MAX_SAMPLES
    scope.gain.db = 12
    time.sleep(1)

    for key_id in range(KEY_ID_LB, KEY_ID_UB):
        key_str = key_id if KEY_TYPE == 'profile' else f"{key_id:03}"
        trace_path = f"{DATA_PATH}/{KEY_TYPE}_{key_str}"
        subprocess.run(["mkdir", "-p", trace_path])
        key = key_list[key_id]
        if type(key) is not list:
            key = key.tolist()
        target.write('k' + input2hex(key) + '\n')
        data = target.read(num_char=0xffff)
        print(data[:-5])
        T0 = time.time()
        for n in range(N_TRACE):
            t0 = time.time()
            trace = record_one_key(scope, target)
            t1 = time.time()
            print(f"{trace_path}/trace_{n:02}.npy")
            np.save(f"{trace_path}/trace_{n:02}.npy", trace)
            print(f"key{key_id}, N={n} requires {t1-t0:.2f} seconds.")
        T1 = time.time()
        print(f"requires {(T1-T0)/60:.2f} min.")
        print(datetime.now())
        print(f"key {key_id} finished.")

    print("Close CW.")
    target.dis()
    scope.dis()
