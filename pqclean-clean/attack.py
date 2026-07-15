"""
Attack.

Attack with MLE and ISD
"""

import os
import sys
import json
import glob
import pickle
import collections
import random
import numpy as np

# class-coeffs map
from utils import class_coeffs_map_scaled
from utils import class_coeffs_map_shift55

# Pre-processing
from utils import calc_trace_snr
from utils import trace_butter_lpf

# MLE
from utils import mle_choose_value
from utils import mle_distribution
from utils import record_sign_origin
from utils import record_abs_table_index_origin
from utils import reorder_traces
from utils import select_rows_by_labels
from utils import dict_process
from utils import fill_dict

# Gaussian template
from utils import gaussian_inference
# MLP template
from TA_discriminative import classifier_inference
import torch.nn as nn
import torch.nn.functional as F

# Report
from utils import stats_init, report_sr, report_error

# attack.py is symlinked into other project dirs (e.g. pqclean-clean/attack.py
# -> ../fpemu/attack.py), so paths resolve against cwd to track whichever
# project is actually running, matching how the relative `PATH` below already
# resolves per-project.
PREFIX = "."
SKIP_SHIFT55 = True
N_ATTACK_KEYS = 100

MCU_FREQ = 25_000_000
PPC = 8
ADC_FREQ = MCU_FREQ * PPC
CUTOFF_FREQ = MCU_FREQ / 2

# ---- runtime configuration -------------------------------------------------
# classifier_*/crop_traces/load_traces read OPT, FALCON_N, MODEL, PATH and
# TRACES_PATH as module globals.  A function looks its globals up in the module
# where it is DEFINED (attack), so setting these names in an importing notebook
# has NO effect -- call attack.configure(...) there instead.
OPT = FALCON_N = MODEL = PATH = TRACES_PATH = None


def configure(opt="O0", falcon_n=512, model="MLP", skip_shift55=True):
    """Set the module-level config the attack functions rely on.

    Call once before using classifier_*/crop_traces/load_traces/attack_*, from
    either a driver (`__main__`) or a notebook (`import attack; attack.configure(...)`).
    """
    global OPT, FALCON_N, MODEL, PATH, TRACES_PATH, SKIP_SHIFT55
    OPT, FALCON_N, MODEL = opt, falcon_n, model
    SKIP_SHIFT55 = skip_shift55
    PATH        = f"{OPT}-falcon{FALCON_N}"
    TRACES_PATH = f"{PREFIX}/{PATH}/traces_attack"


configure()   # sensible defaults so a bare `import attack` is already usable

new_class_abs_map = {
    0: [0],
    1: [1],
    2: [2, 3],
    3: [4, 5, 6, 7],
    4: list(range(8, 16)),
    5: list(range(16, 32)),
}

# Classifiers #############################################################


class model_mlp(nn.Module):
    def __init__(self, n_class):
        super().__init__()
        self.flatten = nn.Flatten()
        self.bn1 = nn.BatchNorm1d(64)
        self.bn2 = nn.BatchNorm1d(64)
        self.bn3 = nn.BatchNorm1d(n_class)
        self.fc1 = nn.LazyLinear(64)
        self.fc2 = nn.Linear(64, 64)
        self.fc3 = nn.Linear(64, n_class)
        self.relu = nn.ReLU()

    def forward(self, x):
        x = self.flatten(x)
        x = F.selu(self.bn1(self.fc1(x)))
        x = F.selu(self.bn2(self.fc2(x)))
        x = F.selu(self.bn3(self.fc3(x)))
        x = F.relu(x)
        return x


# The MLP checkpoints were saved as whole pickled objects while `model_mlp` lived
# in `__main__` (the 7_ml training script), so torch.load resolves the class via
# `__main__.model_mlp`.  Register it so unpickling works whether attack.py is run
# directly (there __main__ IS attack) or imported into another session (the org).
import __main__ as _main
_main.model_mlp = model_mlp


def classifier_scaled(traces_test):
    if MODEL == "Gaussian":
        return gaussian_inference(traces_test,
            f"{PATH}/gaussian/gaussian_scaled.pkl")
    if MODEL == "MLP":
        return classifier_inference(traces_test,
            f"{PATH}/mlp/mlp_scaled.pth")


def classifier_shift55(traces_test):
    if MODEL == "Gaussian":
        return gaussian_inference(traces_test,
            f"{PATH}/gaussian/gaussian_shift55.pkl")
    if MODEL == "MLP":
        return classifier_inference(traces_test,
            f"{PATH}/mlp/mlp_shift55.pth")


def classifier_mul(traces_test, model_p):
    if MODEL == "Gaussian":
        return gaussian_inference(traces_test,
            f"{PATH}/gaussian/gaussian_mul_{model_p}.pkl")
    if MODEL == "MLP":
        return classifier_inference(traces_test,
            f"{PATH}/mlp/mlp_mul_{model_p}.pth")


def classifier_mul_skip(traces_test, model_p):
    if MODEL == "Gaussian":
        return gaussian_inference(traces_test,
            f"{PATH}/gaussian/gaussian_mul_shift55_{model_p}.pkl")
    if MODEL == "MLP":
        return classifier_inference(traces_test,
            f"{PATH}/mlp/mlp_mul_shift55_{model_p}.pth")


###############################################################################
#                             Load Traces and Crop                            #
###############################################################################

def load_traces(key_type, key_id):
    files = sorted(glob.glob(
        f"{TRACES_PATH}/{key_type}_{key_id:03}/trace_*.npy"))
    trace_raw = np.array([np.load(f, mmap_mode='r') for f in files])
    trace_lpf = trace_butter_lpf(trace_raw, ADC_FREQ, CUTOFF_FREQ)

    snr_raw = calc_trace_snr(trace_raw)
    snr_lpf = calc_trace_snr(trace_lpf)
    print(f"{key_type} key_id={key_id:2}: {snr_raw:.2f} dB → {snr_lpf:.2f} dB")

    return trace_lpf


def crop_traces(trace_lpf, fg, key_id):
    """
    Notes
    -----
    Attack-phase cycle loc are PER attack-key AND per key-half (f, g).
    fpr_scaled timing is data-independent, but fpr_mul (shift55 + multiply) is
    data-dependent, so its segment loc drift with the (unknown) key and MUST
    come from these attack-side loc files, not the constant-key profile ones.
    """
    with open("cycloc_params.json") as f:
        json_file = json.load(f)
        cfg = json_file[OPT]
    CYC_SCALED      = cfg["scaled"]["cycle_usage"]
    CYC_MUL         = cfg["mul"]["cycle_usage"]
    CYC_SHIFT55     = cfg["shift55"]["cycle_usage"]
    CYC_MUL_SHIFT55 = cfg["mul_shift55"]["cycle_usage"]

    with open(f"{TRACES_PATH}/loc_scaled_{fg}.pkl", 'rb') as f:
        loc_scaled  = pickle.load(f)
    with open(f"{TRACES_PATH}/loc_shift55_{fg}.pkl", 'rb') as f:
        loc_shift55 = pickle.load(f)
    with open(f"{TRACES_PATH}/loc_mul_{fg}.pkl", 'rb') as f:
        loc_mul     = pickle.load(f)
    with open(f"{TRACES_PATH}/loc_mul_shift55_{fg}.pkl", 'rb') as f:
        loc_mul_shift55 = pickle.load(f)
    trace_scaled = np.array([
        trace_lpf[:, loc_scaled[key_id][i][0]*PPC:
                  loc_scaled[key_id][i][0]*PPC + CYC_SCALED*PPC]
        for i in range(FALCON_N)
    ]).transpose(1, 0, 2)
    trace_shift55 = np.array([
        trace_lpf[:, loc_shift55[key_id][i][0]*PPC:
                  loc_shift55[key_id][i][0]*PPC + CYC_SHIFT55*PPC]
        for i in range(FALCON_N)
    ]).transpose(1, 0, 2)
    trace_mul = np.array([
        trace_lpf[:, loc_mul[key_id][i][0]*PPC:
                  loc_mul[key_id][i][0]*PPC + CYC_MUL*PPC]
        for i in range(FALCON_N)
    ]).transpose(1, 0, 2)
    trace_mul_shift55 = np.array([
        trace_lpf[:, loc_mul_shift55[key_id][i][0]*PPC:
                  loc_mul_shift55[key_id][i][0]*PPC + CYC_MUL_SHIFT55*PPC]
        for i in range(FALCON_N)
    ]).transpose(1, 0, 2)

    return trace_scaled, trace_shift55, trace_mul, trace_mul_shift55


###############################################################################
#                               Attack Functions                              #
###############################################################################

# fpr scaled ##################################################################

def attack_scaled(trace_scaled, MLE_N):
    #########First, process the data from fpr_scaled.
    fpr_scaled_mle_prob_list = collections.defaultdict(list)
    for i in range(MLE_N):
        prob_fpr_scaled = classifier_scaled(trace_scaled[i,:,:])
        #The dimensions of prob_fpr_scaled are (512, 11). Each coefficient's index is used as a key, and the corresponding prob values
        #for N_attack_trace times are stored in the list corresponding to that key.
        for j in range(FALCON_N):
            fpr_scaled_mle_prob_list[j].append(prob_fpr_scaled[j])
    #A dictionary where key-value pairs correspond to coefficient indices, and each key-value pair contains MLE_N probabilities of 11 categories.
    # the distribution of "scaled" classifier's classification results
    fpr_scaled_mle_prob_list = dict(fpr_scaled_mle_prob_list)
    fpr_scaled_mle_prob_list = {key_coeff: np.array(val_list) for key_coeff, val_list in fpr_scaled_mle_prob_list.items()}
    scaled_table = mle_distribution(fpr_scaled_mle_prob_list)
    scaled_dict  = mle_choose_value(fpr_scaled_mle_prob_list)

    return scaled_dict, scaled_table


def drop_fail_idx(scaled_table, scaled_threshold):
    # store the select the coefficients that are most likely right
    maintain_scaled_coff = {}
    drop_idx = []
    for id_k, vv in scaled_table.items():
        if np.max(vv) >= scaled_threshold:
            maintain_scaled_coff[id_k] = np.argmax(vv)
        else:
            drop_idx.append(id_k)
    print(f"the remaining coff after scaled classifier is {len(maintain_scaled_coff)}")
    return drop_idx


# shift55 (normalization) #####################################################

def attack_shift55(trace_shift55, scaled_dict, MLE_N):
    #f_128~f_255; f_384~f_511 will involve multiplication operations. We need to analyze these coefficients,
    #identifying which are already 0, -1, or 1, and which require further differentiation.
    check_keys = list(range(128, 256)) + list(range(384, 512))
    # check_keys = [k for k in check_keys if k not in drop_idx] #exclude drop_idx
    keys_012 = [k for k in check_keys if scaled_dict[k] in (0, 1, 2)]
    # keys_other = [k for k in check_keys if scaled_dict[k] not in (0, 1, 2)]

    """
    The coefficient indices of traces in `trace_shift55` are:
      Re(f[128]), Re(f[384]), Im(f[128]), Im(f[384]),
      Re(f[129]), Re(f[385]), Im(f[129]), Im(f[385]),
      ...
      Re(f[255]), Re(f[511]), Im(f[255]), Im(f[511]).

    After processing, the coefficient indices of traces in `trace_shift55` are
      Re(f[128]), Im(f[128]), Re(f[129]), Im(f[129]),
      ...
      Re(f[254]), Im(f[254]), Re(f[255]), Im(f[255]),
      Re(f[384]), Im(f[384]), Re(f[385]), Im(f[385]),
      ...
      Re(f[510]), Im(f[510]), Re(f[511]), Im(f[511]),

    At this point, the `MLE_N` observations should be utilized.
    """
    target_order = list(range(128, 256)) + list(range(384, 512))
    # target_filtered = [c for c in target_order if c not in keys_012 + drop_idx] # "+ drop_idx": exclude drop_idx
    # keep_rows = [i for i, c in enumerate(target_order) if c not in keys_012 + drop_idx]
    target_filtered = [c for c in target_order if c not in keys_012] # "+ drop_idx": exclude drop_idx
    keep_rows = [i for i, c in enumerate(target_order) if c not in keys_012]

    fpr_shift_mle_prob_list = collections.defaultdict(list)

    for i in range(MLE_N):
        attack_traces_shift_lpf = reorder_traces(trace_shift55[i,:,:])
        attack_traces_shift_lpf_1 = attack_traces_shift_lpf[0::2]
        attack_traces_shift_lpf_2 = attack_traces_shift_lpf[1::2]

        # Continuing with the processing of attack_traces_shift_lpf, since the coefficient indices in keys_012 are already determined,
        # no further processing is needed; therefore, this part of the data is filtered out.
        attack_traces_shift_filtered_1 = attack_traces_shift_lpf_1[keep_rows, :]
        attack_traces_shift_filtered_2 = attack_traces_shift_lpf_2[keep_rows, :]

        prob_fpr_shift_1 = classifier_shift55(attack_traces_shift_filtered_1)
        # print(prob_fpr_shift_1)
        prob_fpr_shift_2 = classifier_shift55(attack_traces_shift_filtered_2)
        # print(prob_fpr_shift_2)

        for j in range(len(target_filtered)):
            fpr_shift_mle_prob_list[target_filtered[j]].append(prob_fpr_shift_1[j])
            fpr_shift_mle_prob_list[target_filtered[j]].append(prob_fpr_shift_2[j])

    # A dictionary where key-value pairs correspond to coefficient indices, and
    # each key-value pair contains 2*N_attack_trace values representing binary classification probabilities.
    fpr_shift_mle_prob_list = dict(fpr_shift_mle_prob_list)
    fpr_shift_mle_prob_list = {key_coeff: np.array(val_list) for key_coeff, val_list in fpr_shift_mle_prob_list.items()}
    shift_dict = mle_choose_value(fpr_shift_mle_prob_list)  # mle get label val
    shift55_table = mle_distribution(fpr_shift_mle_prob_list)  # used for debug
    # print(shift_dict)

    return shift_dict, target_filtered, shift55_table


# fpr mul #####################################################################

def cal_per_mul_prob(sets_dict, classifier_mul, model_p):
    """
    Concatenates, computes, and splits the dictionary `{key: (2, n) array}` back into a dictionary.
    Parameters:
    `data_dict`: dict[int, np.ndarray]
    Each value is a NumPy array of (2, n) values.
    `func`: callable
    A function that takes (2*m, n) as input and outputs (2*m, k) values.

    Returns:
    `new_dict`: dict[int, np.ndarray]
     Each value is a NumPy array of (2, k) values.
    """
    # 1. Concatenate the keys in order to form a large matrix.
    keys = list(sets_dict.keys())
    big_array = np.vstack([sets_dict[k] for k in keys])

    # 2. calculate
    # tmp_labels = np.repeat(labels,2)
    result = classifier_mul(big_array, model_p)

    # 3. Split back into dictionary
    new_dict = {}
    for idx, key in enumerate(keys):
        start = idx * 2
        end = start + 2
        new_dict[key] = result[start:end, :]

    return new_dict


def attack_mul(trace_mul, target_filtered, abs_dict, shift_dict, MLE_N):
    set0 = set(class_coeffs_map_shift55[0])
    set1 = set(class_coeffs_map_shift55[1])
    # the initial range of values for the partitioning coefficients is determined.
    final_set = {}
    sure_set = []
    insure_set = []

    for key, value in abs_dict.items():
        if value == 0 or value == 1:
            sure_set.append(key)
            final_set[key]=set(new_class_abs_map[value])
        else:
            insure_set.append(key)
    # Taking the intersection of the sets determined by the fpr_scaled and the normalization procedure in fpr_mul
    # can determine the absolute values of 2 and 3, but only for coefficients multiplied by the rotation factor.
    for insure_idx in insure_set:
        if insure_idx in target_filtered:
            # label_choose = guess_attack_diffset[target_filtered_f.index(insure_idx)]
            label_choose = shift_dict[insure_idx]
            if label_choose == 0:
                tmp_set = set0 & set(new_class_abs_map[abs_dict[insure_idx]])
                final_set[insure_idx]=tmp_set
            else:
                tmp_set = set1 & set(new_class_abs_map[abs_dict[insure_idx]])
                final_set[insure_idx]=tmp_set
    # Add the range of coefficients that are not multiplied by the twiddle factor and are not in the range of 0, 1, -1 to f_final_set.
    no_mul_w = list(range(0, 128)) + list(range(256, 384))
    # no_mul_w = [k for k in no_mul_w if k not in drop_idx]
    no_mul_w_insure = [d for d in no_mul_w if d not in sure_set]
    for d in no_mul_w_insure:
        final_set[d] = set(new_class_abs_map[abs_dict[d]])

    #for the drop_idx,just assign {99,98,97} to mark them
    # for d in drop_idx:
    #     final_set[d]=set([99,98,97])

    #########Begin dividing {4, 5} and {6,7}
    fpr_mul_mle_prob_list_45 = collections.defaultdict(list)
    fpr_mul_mle_prob_list_67 = collections.defaultdict(list)
    mul_idx_list=[]
    #Retrieve the indices of coefficients multiplied by w that still do not have a definite value after using fpr_scaled and diffset.
    mul_w = list(range(128, 256)) + list(range(384, 512))
    # mul_w = [k for k in mul_w if k not in drop_idx] #exclude drop_idx
    for d in mul_w:
        if len(final_set[d]) != 1:
            mul_idx_list.append(d)

    for i in range(MLE_N):

        attack_traces_mul = reorder_traces(trace_mul[i,:,:])
        attack_traces_mul_1 = attack_traces_mul[0::2]
        attack_traces_mul_2 = attack_traces_mul[1::2]

        attack_traces_mul_1 = select_rows_by_labels(attack_traces_mul_1, mul_w, mul_idx_list)
        attack_traces_mul_2 = select_rows_by_labels(attack_traces_mul_2, mul_w, mul_idx_list)

        sets_4_5 = collections.defaultdict(list)
        sets_6_7 = collections.defaultdict(list)

        # labels_4_5=[]
        # print(f_final_set)
        #Divide into different sets
        for j in range(len(mul_idx_list)):
            if final_set[mul_idx_list[j]] == {4,5}:
                sets_4_5[mul_idx_list[j]].append(attack_traces_mul_1[j])
                sets_4_5[mul_idx_list[j]].append(attack_traces_mul_2[j])
                # labels_4_5.append(abs(mul_labels[mul_idx_list[j]])-4)
            elif final_set[mul_idx_list[j]] == {6,7}:
                sets_6_7[mul_idx_list[j]].append(attack_traces_mul_1[j])
                sets_6_7[mul_idx_list[j]].append(attack_traces_mul_2[j])

        sets_4_5 = dict_process(sets_4_5)
        sets_6_7 = dict_process(sets_6_7)
        # labels_4_5 = np.array(labels_4_5)

        prob_fpr_mul_4_5 = cal_per_mul_prob(sets_4_5, classifier_mul, "4_5")
        prob_fpr_mul_6_7 = cal_per_mul_prob(sets_6_7, classifier_mul, "6_7")
        # print(prob_fpr_mul_4_5)

        fill_dict(fpr_mul_mle_prob_list_45, prob_fpr_mul_4_5)
        fill_dict(fpr_mul_mle_prob_list_67, prob_fpr_mul_6_7)

    fpr_mul_mle_prob_list_45 = dict_process(fpr_mul_mle_prob_list_45)
    fpr_mul_mle_prob_list_67 = dict_process(fpr_mul_mle_prob_list_67)
    # print(fpr_mul_mle_prob_list_45)

    guess_45 = mle_choose_value(fpr_mul_mle_prob_list_45)
    guess_67 = mle_choose_value(fpr_mul_mle_prob_list_67)
    # print(guess_45)

    part_guess_list = [guess_45, guess_67]
    # part_guess_list = [guess_45]
    return final_set, part_guess_list


def attack_mul_skip_shift55(trace_mul, abs_dict, MLE_N):
    final_set = {}
    sure_set = []
    insure_set = []

    for key, value in abs_dict.items():
        if value == 0 or value == 1:
            # determined by fpr_scaled
            sure_set.append(key)
            final_set[key]=set(new_class_abs_map[value])
        else:
            insure_set.append(key)
            final_set[key] = set(new_class_abs_map[value])

    #########Begin dividing {2, 3} and {4,5,6,7}
    fpr_mul_mle_prob_list_2_3 = collections.defaultdict(list)
    fpr_mul_mle_prob_list_4_7 = collections.defaultdict(list)
    mul_idx_list = []
    mul_w = list(range(128, 256)) + list(range(384, 512))
    for d in mul_w:
        if len(final_set[d]) != 1:
            mul_idx_list.append(d)

    for i in range(MLE_N):

        attack_traces_mul = reorder_traces(trace_mul[i,:,:])
        attack_traces_mul_1 = attack_traces_mul[0::2]
        attack_traces_mul_2 = attack_traces_mul[1::2]

        attack_traces_mul_1 = select_rows_by_labels(attack_traces_mul_1, mul_w, mul_idx_list)
        attack_traces_mul_2 = select_rows_by_labels(attack_traces_mul_2, mul_w, mul_idx_list)

        sets_2_3 = collections.defaultdict(list)
        sets_4_7 = collections.defaultdict(list)

        for j in range(len(mul_idx_list)):
            if final_set[mul_idx_list[j]] == {2,3}:
                sets_2_3[mul_idx_list[j]].append(attack_traces_mul_1[j])
                sets_2_3[mul_idx_list[j]].append(attack_traces_mul_2[j])
                # labels_2_3.append(abs(mul_labels[mul_idx_list[j]])-2)
            elif final_set[mul_idx_list[j]] == {4,5,6,7}:
                sets_4_7[mul_idx_list[j]].append(attack_traces_mul_1[j])
                sets_4_7[mul_idx_list[j]].append(attack_traces_mul_2[j])

        sets_2_3 = dict_process(sets_2_3)
        sets_4_7 = dict_process(sets_4_7)
        # labels_2_3 = np.array(labels_2_3)

        prob_fpr_mul_2_3 = cal_per_mul_prob(sets_2_3, classifier_mul_skip, "2_3")
        prob_fpr_mul_4_7 = cal_per_mul_prob(sets_4_7, classifier_mul_skip, "4_7")
        # print(prob_fpr_mul_4_5)

        fill_dict(fpr_mul_mle_prob_list_2_3, prob_fpr_mul_2_3)
        fill_dict(fpr_mul_mle_prob_list_4_7, prob_fpr_mul_4_7)

    fpr_mul_mle_prob_list_2_3 = dict_process(fpr_mul_mle_prob_list_2_3)
    fpr_mul_mle_prob_list_4_7 = dict_process(fpr_mul_mle_prob_list_4_7)
    # print(fpr_mul_mle_prob_list_4_5)

    guess_2_3 = mle_choose_value(fpr_mul_mle_prob_list_2_3)
    guess_4_7 = mle_choose_value(fpr_mul_mle_prob_list_4_7)
    # print(guess_2_3)

    part_guess_list = [guess_2_3, guess_4_7]
    # part_guess_list = [guess_2_3]
    return final_set, part_guess_list


# Gesamt ######################################################################

# The passed-in `guess_part_list` consists of dictionaries for guessing categories {4,5} and {6,7}, respectively.
def fill_guess_dict(guess_part_list, f_final_set_p, f_sign_dict_p):
    for idx_guess, guess_p in enumerate(guess_part_list):
        for key_, guess_v in guess_p.items():
            if idx_guess == 0:
                f_final_set_p[key_] = {guess_v+4}
            if idx_guess == 1:
                f_final_set_p[key_] = {guess_v+6}
    sorted_f_final_set_p = dict(sorted(f_final_set_p.items()))
    f_guess_dict_p = {}
    for key, val in f_sign_dict_p.items():
        if val >= 0:
            f_guess_dict_p[key] = sorted_f_final_set_p[key]
        else:
            f_guess_dict_p[key] = {-x for x in sorted_f_final_set_p[key]}
    return f_guess_dict_p


def fill_guess_dict_skip(guess_part_list, f_final_set_p, f_sign_dict_p):
    for idx_guess, guess_p in enumerate(guess_part_list):
        for key_, guess_v in guess_p.items():
            if idx_guess == 0:
                f_final_set_p[key_] = {guess_v+2}
            if idx_guess == 1:
                f_final_set_p[key_] = {guess_v+4}
    sorted_f_final_set_p = dict(sorted(f_final_set_p.items()))
    f_guess_dict_p = {}
    for key, val in f_sign_dict_p.items():
        if val >= 0:
            f_guess_dict_p[key] = sorted_f_final_set_p[key]
        else:
            f_guess_dict_p[key] = {-x for x in sorted_f_final_set_p[key]}
    return f_guess_dict_p


## distinguish 4 and 5, and distinguish 6 and 7
def attack_key_repeat(fg, key, key_id, stage_stats, MLE_N, scaled_threshold, only_4_5=False):
    from utils import _true_scaled_label, _true_shift55_label
    trace_lpf = load_traces(fg, key_id)
    # the attack trace segments corresponding to the fpr_scaled, normalization procedure and mantissa multiplication in fpr_mul for the f (or g) key
    trace_scaled, trace_shift55, trace_mul, trace_mul_shift55 = \
        crop_traces(trace_lpf, fg, key_id)
    trace_scaled  = trace_scaled[:MLE_N, :, :]
    trace_shift55 = trace_shift55[:MLE_N, :, :]
    trace_mul     = trace_mul[:MLE_N, :, :]
    trace_mul_shift55 = trace_mul_shift55[:MLE_N, :, :]

    #########First, process the data from fpr_scaled.
    scaled_dict, scaled_table = attack_scaled(trace_scaled, MLE_N)
    drop_idx = drop_fail_idx(scaled_table, scaled_threshold)
    report_sr(fg, "scaled",  key, stage_stats, scaled_dict,
              _true_scaled_label)

    #Record information after attacking fpr_scaled
    # sign_dict = record_sign(maintain_scaled_coff, drop_idx, FALCON_N)
    # abs_dict = record_abs_table_index(maintain_scaled_coff,drop_idx, FALCON_N)
    sign_dict = record_sign_origin(scaled_dict, FALCON_N)
    abs_dict = record_abs_table_index_origin(scaled_dict, FALCON_N)

    if SKIP_SHIFT55:
        final_set, part_guess_list = attack_mul_skip_shift55(trace_mul_shift55, abs_dict, MLE_N)
        guess_23, guess_47 = part_guess_list
        report_sr(fg, "mul_2_3", key, stage_stats, guess_23,
                  lambda v: 0 if abs(v) == 2 else 1 if abs(v) == 3 else None)
        report_sr(fg, "mul_4_7", key, stage_stats, guess_47,
                  lambda v: {4: 0, 5: 1, 6: 2, 7: 3}.get(abs(v)))
        final_guess_dict = fill_guess_dict_skip(part_guess_list,
                                                final_set, sign_dict)
    else:
        ######### Process the trace data corresponding to the normalization procedure in fpr_mul
        shift_dict, target_filtered, shift55_table = \
            attack_shift55(trace_shift55, scaled_dict, MLE_N)
        report_sr(fg, "shift55", key, stage_stats, shift_dict,
                  _true_shift55_label)

        ######Based on the attack results of fpr_scaled and the normalization procedure in fpr_mul,
        final_set, part_guess_list = attack_mul(trace_mul, target_filtered, abs_dict, shift_dict, MLE_N)

        guess_45, guess_67 = part_guess_list
        report_sr(fg, "mul_4_5", key, stage_stats, guess_45,
                  lambda v: 0 if abs(v) == 4 else 1 if abs(v) == 5 else None)
        report_sr(fg, "mul_6_7", key, stage_stats, guess_67,
                  lambda v: 0 if abs(v) == 6 else 1 if abs(v) == 7 else None)

        if only_4_5:
            # {4,5} and {6,7}
            final_guess_dict = fill_guess_dict(part_guess_list[:1], final_set, sign_dict)
        else:
            # {4,5}-only: keep just the {4,5} guesses; {6,7} coefficients stay as a 2-candidate set
            final_guess_dict = fill_guess_dict(part_guess_list,
                                               final_set, sign_dict)

    return final_guess_dict, drop_idx


###############################################################################
#                              Check Correctness                              #
###############################################################################

def ISD_recovery(f_determined, g_determined, key_f, key_g,
                 default_attempts=1e6):
    """
    ISD-style recovery: keep positions that are definitely 0/±1
    (special_positions), then randomly sample the remaining candidates to
    fill out to FALCON_N confirmed positions, checking against the true key
    up to `default_attempts` times.

    Returns
    -------
    (code, total_num)
        code: 2 on success, -3 if there aren't enough candidates to reach
        FALCON_N, -4 if every attempt failed.
    """
    special_positions = []
    for k, v in f_determined.items():
        if v in (0, 1, -1):
            special_positions.append(("f", k, v))
    for k, v in g_determined.items():
        if v in (0, 1, -1):
            special_positions.append(("g", k, v))

    m = len(special_positions)

    candidates = []
    for k, v in f_determined.items():
        if v not in (0, 1, -1):
            candidates.append(("f", k, v))
    for k, v in g_determined.items():
        if v not in (0, 1, -1):
            candidates.append(("g", k, v))

    need = 512 - m
    print(f"need is {need}")
    print(f"len of candidates is {len(candidates)}")
    if need < 0 or len(candidates) < need:
        return -3, 1

    total_num = 0
    for _ in range(default_attempts):
        total_num = total_num + 1
        sample = random.sample(candidates, need)
        positions = special_positions + sample

        ok = True
        for src, k, v in positions:
            if src == "f":
                if key_f[k] != v:
                    ok = False
                    break
            else:  # src == "g"
                if key_g[k] != v:
                    ok = False
                    break
        if ok:
            f_dict_p = {}
            g_dict_p = {}
            for source, k, v in positions:
                if source == "f":
                    f_dict_p[k] = v
                elif source == "g":
                    g_dict_p[k] = v
            # with open(f"./data/data_k_guess_isd/Falcon512/f_{kk_idx}_guess_try.pkl", "wb") as f:
            #     pickle.dump(f_dict_p, f)
            # with open(f"./data/data_k_guess_isd/Falcon512/g_{kk_idx}_guess_try.pkl", "wb") as g:
            #     pickle.dump(g_dict_p, g)
            return 2, total_num

    return -4, default_attempts


def check_key_right(f_guess_dict_p, g_guess_dict_p,
                    key_f, key_g, drop_idx_f_p, drop_idx_g_p, attempts):
    """
    To merge f and g into f||g, first check if the number of currently "determined" coefficients (with only one candidate value) is ⪭ FALCON_N.
      If < FALCON_N, fail directly.
      If = FALCON_N, check if these FALCON_N coefficients are correct.
      If > FALCON_N, set it as num_guess, and randomly select FALCON_N from num_guess each time, continuously checking if they are correct. If none of these attempts succeed, then it's a failure.

    The extraction principle is to prioritize keeping values that are definitely 0 or ±1, followed by ±2 or ±3, then ±4 or ±5, and finally ±6 or ±7.

    Error return code:
      -1: The number of confirmed values is less than 512;
      -2: Exactly 512 values are confirmed, but there are errors;
      -3: len(candidate) < 512 - need;
      -4: Multiple attempts failed.
    Success return code:
      1: Exactly 512 values succeeded;
      2: Success after random sampling;
      3: Success when getting to {4, 5}.
    """
    # --- Step1---
    f_determined = {k: list(v)[0] for k, v in f_guess_dict_p.items()
                    if (len(v) == 1) and (k not in drop_idx_f_p)}
    g_determined = {k: list(v)[0] for k, v in g_guess_dict_p.items()
                    if (len(v) == 1) and (k not in drop_idx_g_p)}
    total_determined = len(f_determined) + len(g_determined)
    print(f"total-determined (remove some after scaled classifier) is {total_determined}")

    if total_determined < 512:
        return -1, 1

    # --- Step2: If there are exactly 512 definite positions ---
    if total_determined == 512:
        for k, v in f_determined.items():
            if key_f[k] != v:
                return -2, 1
        for k, v in g_determined.items():
            if key_g[k] != v:
                return -2, 1
        return 1, 1


    # --- Step2.5: Prioritize checking the position of values in the range {0, ±1, ±2, ±3, ±4, ±5} (all are correct). ---
    # This step is equivalent to the procedure used in the -O0 level experiment.
    f_dict_p = {}
    g_dict_p = {}

    special_values = {0, 1, -1, 2, -2, 3, -3, 4, -4, 5, -5}
    priority_positions = []
    for k, v in f_determined.items():
        if v in special_values:
            priority_positions.append(("f", k, v))
    for k, v in g_determined.items():
        if v in special_values:
            priority_positions.append(("g", k, v))

    if len(priority_positions) >= 512:
        print("jinru")
        ok = True
        for src, k, v in priority_positions:
            if src == "f":
                if key_f[k] != v:
                    ok = False
                    break
            else:  # "g"
                if key_g[k] != v:
                    ok = False
                    break
        if ok:
            for source, k, v in priority_positions:
                if source == "f":
                    f_dict_p[k] = v
                elif source == "g":
                    g_dict_p[k] = v
            # with open(f"./data/data_k_guess_isd/Falcon512/f_{kk_idx}_guess_try.pkl", "wb") as f:
            #     pickle.dump(f_dict_p, f)
            # with open(f"./data/data_k_guess_isd/Falcon512/g_{kk_idx}_guess_try.pkl", "wb") as g:
            #     pickle.dump(g_dict_p, g)
            return (3, 1)

    # If step2.5 fails, continue with random attempts (ISD-style recovery)
    # --- Step3: total_determined > 512 ---
    return ISD_recovery(f_determined, g_determined, key_f, key_g, attempts)


###############################################################################
#                                    Report                                   #
###############################################################################
def report_sr_total(key_type, stage_stats, skip_shift55=False):
    """Print per-stage correctness accumulated (cross-key) in stage_stats.

    Parameters
    ----------
    key_type : str
        Label for the header and every row, e.g. "f", "g", or "f + g".
    stage_stats : dict
        Cross-key accumulated totals; stage_stats[leakage] → {"ok", "total",
        "misroute", ...}, as folded in the Main loop.
    skip_shift55 : bool, optional
        Selects which stages to print: the skip-shift55 path ("scaled", "mul23",
        "mul47") when True, else the full path ("scaled", "shift55", "mul45",
        "mul67"). Must match the branch that filled stage_stats.

    Returns
    -------
    None
        Prints a boxed per-stage table; a stage with total == 0 prints "n/a".
    """
    def report_stage_leakage(leakage):
        s = stage_stats[leakage]
        if s["total"]:
            line = f"[{key_type}] [{leakage:>10}] {s['ok']}/{s['total']} = {s['ok']/s['total']:.4f}"
        else:
            line = f"[{key_type}] [{leakage:>10}] n/a"
        if s["misroute"]:
            line += f"   (mis-routed: {s['misroute']})"
        print(line)
    print("\n#+begin_example")
    print(f"cross-key stage correctness (all attacked keys, {key_type})")
    if skip_shift55 is True:
        for leakage in ("scaled", "mul_2_3", "mul_4_7"):
            report_stage_leakage(leakage)
    else:
        for leakage in ("scaled", "shift55", "mul_4_5", "mul_6_7"):
            report_stage_leakage(leakage)
    print("#+end_example")


if __name__ == '__main__':
    configure(sys.argv[1], int(sys.argv[2]), sys.argv[3])
    KEY_ID_LB = int(sys.argv[4])
    KEY_ID_UB = int(sys.argv[5])

    Falcon512_f_1000 = np.load("keys/Falcon512_f_1000.npy", allow_pickle=True)
    Falcon512_g_1000 = np.load("keys/Falcon512_g_1000.npy", allow_pickle=True)
    random.seed(2025)
    MLE_N = 30
    ONLY_4_5 = False
    try_random_num = 1000000
    # succ_num_count=0
    key_key_idx_list = []
    error_list = []
    # succ_num_list=[]
    succ_num_count = 0
    scaled_threshold = 0.99
    check_num_list = []
    stage_stats_f = stats_init()
    stage_stats_g = stats_init()
    total_stats   = stats_init()

    print("#+begin_example")
    for key_id in range(KEY_ID_LB, KEY_ID_UB):
        print("#" * 80)

        key_f = Falcon512_f_1000[key_id]
        key_g = Falcon512_g_1000[key_id]
        f_guess_dict, drop_re_f = attack_key_repeat(
            'f', key_f, key_id, stage_stats_f,
            MLE_N, scaled_threshold, only_4_5=ONLY_4_5)
        g_guess_dict, drop_re_g = attack_key_repeat(
            'g', key_g, key_id, stage_stats_g,
            MLE_N, scaled_threshold, only_4_5=ONLY_4_5)

        re, check_num = check_key_right(f_guess_dict, g_guess_dict, key_f, key_g,
                                        drop_re_f, drop_re_g, try_random_num)
        print(f"the {key_id}th key guess's state is {re}")  # <
        if re > 0:
            succ_num_count = succ_num_count + 1
            key_key_idx_list.append(key_id)
            check_num_list.append(check_num)
        else:
            error_list.append(key_id)
        if SKIP_SHIFT55 is True:
            for lk in ("scaled", "mul_2_3", "mul_4_7"):     # fold this key into the totals
                for m in ("ok", "total", "misroute"):
                    total_stats[lk][m] += stage_stats_f[lk][m] + stage_stats_g[lk][m]
        else:
            for lk in ("scaled", "shift55", "mul_4_5", "mul_6_7"):     # fold this key into the totals
                for m in ("ok", "total", "misroute"):
                    total_stats[lk][m] += stage_stats_f[lk][m] + stage_stats_g[lk][m]
    print("#" * 80)
    print(f"the succ count is {succ_num_count}")
    # cross-key per-stage correctness summary
    report_sr_total('f + g', total_stats, skip_shift55=SKIP_SHIFT55)
    print("#+end_example")

    # print(len(f_guess_dict))
    # for i, v in f_guess_dict.items():
    #     print(f"{i}: {v}")

    # print(check_num_list)
