"""Trace pre-processing."""

import math
import numpy as np
import scipy as sp
import itertools
import pickle
import collections
import threading
from sklearn.model_selection import train_test_split

SEED = 42

###############################################################################
#                 class-coeffs map and their checker functions                #
###############################################################################

class_coeffs_map_scaled = {
    0:  [0],
    1:  [1],
    2:  [-1],
    3:  [2, 3],
    4:  [-3, -2],
    5:  [4, 5, 6, 7],
    6:  [-7, -6, -5, -4],
    7:  list(range(8, 16)),     # [8, ..., 15]
    8:  list(range(-15, -7)),   # [-15, ..., -8]
    9:  list(range(16, 23)),    # [16, ..., 22]
    10: list(range(-22, -15)),  # [-22, ..., -16]
}


class_coeffs_map_shift55 = {
    0: [2, 4, 5, 8, 9, 10, 11, 16, 17, 18, 19, 20, 21, 22],  # make zu<2^55
    1: [3, 6, 7, 12, 13, 14, 15],  # make zu>=2^55
    # 1: [3, 6, 7, 12, 13, 14, 15, 23, 24, 25, 26, 27, 28, 29, 30, 31]
}


class_coeffs_map_mul_4_5 = {
    0: [4],
    1: [5],
}
class_coeffs_map_mul_6_7 = {
    0: [6],
    1: [7],
}
class_coeffs_map_mul_8_11 = {
    0: [8],
    1: [9],
    2: [10],
    3: [11],
}
class_coeffs_map_mul_12_15 = {
    0: [12],
    1: [13],
    2: [14],
    3: [15],
}
class_coeffs_map_mul_16_22 = {
    0: [16],
    1: [17],
    2: [18],
    3: [19],
    4: [20],
    5: [21],
    6: [22],
}
class_coeffs_map_mul_2_3 = {
    0: [2],
    1: [3],
}
class_coeffs_map_mul_4_7 = {
    0: [4],
    1: [5],
    2: [6],
    3: [7]
}


def solve_imbalance_label(class_coeffs_map):
    lst = []
    for coeffs in class_coeffs_map.values():
        lst.append(len(coeffs))
    gcd = math.gcd(*lst)
    lcm = math.lcm(*(x // gcd for x in lst))
    reduced_len = {}
    for cls, coeffs in class_coeffs_map.items():
        reduced_len[cls] = len(coeffs) // gcd
    return lcm, reduced_len


def select_traces_accto_class(traces_dict, class_coeffs_map):
    """
    Pool traces from raw-key dict into class-labelled arrays.

    Parameters
    ----------
    traces_dict : dict[int -> np.ndarray]
        Maps coefficient value -> traces of shape (#trace, #sample).
    class_coeffs_map : dict[int -> list[int]]
        Maps class id -> list of coefficient values belonging to that class,
        e.g. {0: [0], 1: [1], 2: [-1], 3: [2, 3], ...}.
    N_TRACE : int or None
        If given, subsample each class to exactly N_TRACE traces (without
        replacement).  Use this for TVLA/t-test so that all classes have equal
        sample size and the t-statistic is comparable across pairs.
        If None, all available traces for each class are used.

    Returns
    -------
    traces : np.ndarray
        Shape (total_traces, #sample).
    label : np.ndarray
        Shape (total_traces,), integer class id per trace.
    """
    np.random.seed(SEED)
    final_traces = []
    label = []
    lcm, reduced_len = solve_imbalance_label(class_coeffs_map)
    # n_traces_per_label = traces_dict[0].shape[0]  # should be the same for all keys in this dict
    for cls, coeffs in class_coeffs_map.items():
        combined = np.concatenate([traces_dict[c] for c in coeffs], axis=0)
        # default: proportional to set size
        # n_trace_to_pick = combined.shape[0]
        # To solve imbalanced classes issue, random pick #trace from it
        # if class_coeffs_map == class_coeffs_map_scaled:
        #     # manually make it imbalance: 0 more, 10 less
        #     m = n_traces_per_label // lcm
        #     n_trace_to_pick = m * lcm // reduced_len[cls]
        #     n_trace_to_pick = n_traces_per_label
        # print(cls, coeffs, n_trace_to_pick)
        # idx = np.random.choice(combined.shape[0], n_trace_to_pick, replace=False)
        # combined = combined[idx]
        final_traces.append(combined)
        label += [cls] * combined.shape[0]
    traces = np.vstack(final_traces)  # shape (#trace/class x #class, #sample)
    label = np.array(label)  # (#trace/class x #class,)
    return traces, label


def trace_categorize(traces, cls):
    """
    Categorize traces into groups based on their corresponding class.

    Parameters
    ----------
    traces : np.ndarray
        Shape (#trace/class x #class, #sample).
    cls : np.ndarray
        Shape (#trace/class x #class,).

    Returns
    -------
    traces_dict : dict[int: np.ndarray]
        Maps label (int) → traces (#trace, #sample):
        {
            cls_1: np.ndarray,  # shape (#trace/cls_1, #sample)
            cls_2: np.ndarray,  # shape (#trace/cls_2, #sample)
            ...,
            cls_n: np.ndarray   # shape (#trace/cls_n, #sample)
        }
    """
    traces_dict = collections.defaultdict(list)
    for trace, c in zip(traces, cls):
        traces_dict[c].append(trace)
    traces_dict = {k: np.stack(v) for k, v in traces_dict.items()}
    return traces_dict


def select_and_split(traces_dict, class_coeffs_map, test_split):
    # select traces in class
    np.random.seed(SEED)
    traces, label = select_traces_accto_class(traces_dict, class_coeffs_map)
    # traces_dict = trace_categorize(traces, label)
    print(f"traces.shape: {traces.shape}")
    print(f"label.shape: {label.shape}")

    # train/test split
    traces_train, traces_test, label_train, label_test = \
        train_test_split(traces, label,
                         test_size=test_split,
                         stratify=label,
                         shuffle=True,
                         random_state=SEED)
    print(f"traces_train.shape: {traces_train.shape}")
    print(f"traces_test.shape: {traces_test.shape}")

    return traces_train, traces_test, label_train, label_test


###############################################################################
#                                   Filters                                   #
###############################################################################

def trace_fft(trace, sample_freq):
    """Perform FFT to trace."""
    N = len(trace)
    # Apply FFT
    fft_vals = np.fft.fft(trace)
    fft_freqs = np.fft.fftfreq(N, d=1/sample_freq)
    # Take the first half, due to symmetry
    half_N = N // 2
    fft_magnitude = np.abs(fft_vals[:half_N])
    fft_freqs = fft_freqs[:half_N]
    return fft_freqs, fft_magnitude


def trace_butter_lpf(trace, sample_freq, cutoff_freq, order=4):
    """
    Apply low passed filter to trace to rm high freq noise.

    Parameters
    ----------
    trace : np.ndarray
        Shape (#label x #trace, #sample), signal to be filtered.
    sample_freq : float
        The sampling rate of the input signal in Hz, E.g. 30MHz.
    cutoff_freq : float
        The cutoff frequency for the low pass filter in Hz.
    order : int, optional
        The order of the Butterworth filter (default is 4).

    Returns
    -------
    trace_lpf : np.ndarray
        Shape (#label x #trace, #sample), filtered signal.
    """
    nyquist = 0.5 * sample_freq
    normal_cutoff = cutoff_freq / nyquist
    b, a = sp.signal.butter(order, normal_cutoff, btype='low', analog=False)
    # apply to every trace along the sample axis
    trace_lpf = sp.signal.filtfilt(b, a, trace, axis=1)
    return trace_lpf


def calc_trace_snr(traces):
    signal = traces.mean(axis=0)        # mean trace
    noise  = traces.std(axis=0)         # per-sample std across signings
    return 20 * np.log10(np.mean(np.abs(signal)) / np.mean(noise))


###############################################################################
#                                    ANOVA                                    #
###############################################################################

def ttest_table(trace_dict):
    """
    Print pairwise leakage tables for all class pairs.

    Two symmetric N_cls x N_cls tables are printed:
      1. max |t| : the peak Welch t-statistic over all samples.  It answers
         "do the class means differ?" -- but it grows with sqrt(n), so with the
         large, correlated per-class counts here it lands in the hundreds and is
         NOT comparable across experiments nor predictive of per-trace
         classification.  Marked '*' when |t| < T_THRESHOLD (no detectable
         difference of means).
      2. Cohen's d : the sample-size-free effect size
             d_ij = |t|max_ij * sqrt(1/n_i + 1/n_j),
         where n_i = trace_dict[classes[i]].shape[0].  d answers "can I label a
         single trace?" -- it is comparable across experiments and predicts the
         classifier (a pair with small d is exactly one the profiler confuses).
         Marked '*' when d < D_THRESHOLD (indistinguishable per-trace).
    """
    classes = sorted(trace_dict.keys())  # [0, 1, ..., 10]
    N_cls = len(classes)
    T_THRESHOLD = 4.5   # |t| detectability threshold (difference of means)
    D_THRESHOLD = 0.5   # Cohen's d per-trace separability threshold

    # Pairwise max |t| and Cohen's d (symmetric, compute upper triangle only)
    tmat = np.full((N_cls, N_cls), np.nan)
    dmat = np.full((N_cls, N_cls), np.nan)
    for i, j in itertools.combinations(range(N_cls), 2):
        t_vals, _ = sp.stats.ttest_ind(
            trace_dict[classes[i]],
            trace_dict[classes[j]],
            equal_var=False)
        tmax = np.max(np.abs(t_vals))
        n_i = trace_dict[classes[i]].shape[0]
        n_j = trace_dict[classes[j]].shape[0]
        d = tmax * np.sqrt(1.0 / n_i + 1.0 / n_j)
        tmat[i, j] = tmat[j, i] = tmax
        dmat[i, j] = dmat[j, i] = d

    def print_matrix(mat, prec, threshold):
        # numeric field of width `col_w` plus a 1-char marker slot, which holds
        # '*' when the value < threshold and a space otherwise, so the '*' never
        # disturbs the column alignment.
        col_w = 6
        header = " " * 4 + "".join(f"{c:>{col_w}} " for c in classes)
        print(header)
        for i, c in enumerate(classes):
            row = f"{c:>3} "
            for j in range(N_cls):
                if i == j:
                    row += f"{'-':>{col_w}} "
                else:
                    v = mat[i, j]
                    mark = "*" if v <= threshold else " "
                    row += f"{v:{col_w}.{prec}f}{mark}"
            print(row)

    print(f"max |t|  ('*' if ≤ {T_THRESHOLD}, no detectable mean difference):")
    print_matrix(tmat, 1, T_THRESHOLD)
    print(f"Cohen's d  ('*' if ≤ {D_THRESHOLD}, indistinguishable per-trace):")
    print_matrix(dmat, 2, D_THRESHOLD)


def ftest(trace_dict):
    """
    One-way ANOVA F-statistic and its N-free effect size, per sample.

    Si Gao & Elisabeth Oswald EUROCRYPT2022.pdf:
      ESS: explained sum of squares = SS_between (B, signal)
      RSS: residual sum of squares  = SS_within  (W, noise)
      TSS: total sum of squares
      R2 = ESS/TSS = 1 - RSS/TSS = NICV

    SNR = ESS/RSS = R2 / (1-R2)
    R2  = SNR / (1+SNR)
    dfb = G-1  (dof of "between"/"signal")
    dfw = N-G  (dof of "within"/"noise")

    F  = MS_between / MS_within             (MS: mean square)
       = [SS_between/(G-1)]/[SS_within/(N-G)]
       = [SS_between/dfb]/[SS_within/dfw]
       = (ESS/dfb) / (RSS/dfw)
       = ESS/RSS x dfw/dfb
       =   SNR   x dfw/dfb
    R2 = (F*dfb) / (F*dfb + dfw)

    F grows with N (detectability, like max|t| / SOST); R2 does not
    (exploitability, like Cohen's d / SNR).
    """
    groups = [trace_dict[k] for k in sorted(trace_dict)]
    zf = len(groups)
    zr = 1
    q  = sum(g.shape[0] for g in groups)
    dfb, dfw = zf - zr, q - zf               # between-group, within-group
    F, _ = sp.stats.f_oneway(*groups)        # per-sample F, shape (#sample,)
    dof = (dfb, dfw)
    return F, dof


def calc_Fcrit(F, dof, alpha=1e-3):
    # Bonferroni correction, α = 1e-3
    dfb, dfw = dof
    n_cycle = len(F)
    F_crit = sp.stats.f.ppf(1 - alpha / n_cycle, dfb, dfw)
    print(f"F crit = {F_crit:.6f} (Bonferroni correction: alpha={alpha}/{n_cycle})")
    return F_crit


def calc_R2(F, dof):
    """
    Per-sample R² (= η² = NICV), the N-free effect size, from the F-statistic.

        R² = ESS/TSS = SS_between/SS_total
           = (F·dfb) / (F·dfb + dfw)
           = SNR / (1 + SNR)

    R² ∈ [0, 1] and, unlike F itself, does not grow with N -- it measures
    exploitability (how much of the variance is class-dependent signal), not
    detectability.

    Parameters
    ----------
    F : np.ndarray
        Shape (#sample,), per-sample F-statistic from ftest().
    dof : tuple[int, int]
        (dfb, dfw) = (G-1, N-G), the between-/within-group degrees of freedom.

    Returns
    -------
    R2 : np.ndarray
        Shape (#sample,), per-sample R² in [0, 1].
    """
    dfb, dfw = dof
    R2 = (F * dfb) / (F * dfb + dfw)
    print(f"Max R2: {np.max(R2):.4f}")
    return R2


def calc_snr(F, dof):
    """
    Per-sample SNR (size-weighted, Mangard) from the F-statistic.

        SNR = ESS/RSS = SS_between/SS_within
            = F·dfb/dfw
            = R² / (1 - R²)

    Equivalently F = SNR · dfw/dfb.  This matches the size-weighted SNR computed
    directly from the grouped traces, and like R² it is N-free (exploitability).

    Parameters
    ----------
    F : np.ndarray
        Shape (#sample,), per-sample F-statistic from ftest().
    dof : tuple[int, int]
        (dfb, dfw) = (G-1, N-G), the between-/within-group degrees of freedom.

    Returns
    -------
    snr : np.ndarray
        Shape (#sample,), per-sample signal-to-noise ratio.
    """
    dfb, dfw = dof
    snr = F * dfb / dfw
    print(f"Max SNR: {np.max(snr):.4f}")
    return snr


###############################################################################
#                               t-test, SOD, SNR                              #
###############################################################################

def calc_ttest(traces_dict):
    """
    Calculate sample-wise t-test scores between all class pairs.

    This function computes the Welch t-statistics for all unique pairs of
    groups from the input data (traces) at each sample point. It uses 2-sample
    t-test, assuming unequal variances (Welch t-test). The resulting t-scores
    are accumulated for all combinations of groups.

    Parameters
    ----------
    traces_dict : dict[int: np.ndarray]
        Maps label (int) → traces (#trace, #sample):
        {
            label_1: np.ndarray,  # shape (#trace/label_1, #sample)
            label_2: np.ndarray,  # shape (#trace/label_2, #sample)
            ...,
            label_n: np.ndarray   # shape (#trace/label_n, #sample)
        }

    Returns
    -------
    t_score : np.ndarray
        Shape (#sample,), t-statistic values.
    """
    label = sorted(traces_dict.keys())
    N_sample = traces_dict[label[0]].shape[1]

    t_score = np.zeros(N_sample)
    for l1, l2 in itertools.combinations(label, 2):  # iterate  all label pairs
        t_vals, _ = sp.stats.ttest_ind(traces_dict[l1],
                                       traces_dict[l2], equal_var=False)
        # t_vals = np.abs(t_vals)
        if np.isnan(t_vals).any():
            print(f"NaNs detected in t-test between label {l1} and {l2}")
        # t_vals = np.nan_to_num(np.abs(t_vals))  # replae NaN to 0
        t_score += t_vals**2  # accumulate t-val for each combination
    print(f"Max t-score: {np.max(t_score):.4f}")
    return t_score


def calc_sod(traces_dict):
    """
    Calculate Sum of Differences (SOD) across class means.

    Parameters
    ----------
    traces_dict : dict[int: np.ndarray]
        Maps label (int) → traces (#trace, #sample):
        {
            label_1: np.ndarray,  # shape (#trace/label_1, #sample)
            label_2: np.ndarray,  # shape (#trace/label_2, #sample)
            ...,
            label_n: np.ndarray   # shape (#trace/label_n, #sample)
        }

    Returns
    -------
    sod : np.ndarray
        Shape (#sample,), sum of absolute differences of class means.
    """
    label = sorted(traces_dict.keys())
    N_sample = traces_dict[label[0]].shape[1]

    mean = {}
    for i in label:
        mean[i] = np.mean(traces_dict[i], axis=0)

    sod = np.zeros(N_sample)
    for l1, l2 in itertools.combinations(label, 2):  # iterate  all label pairs
        sod += np.abs(mean[l1] - mean[l2])
    print(f"Max SOD: {np.max(sod):.4f}")
    return sod


###############################################################################
#                                 select POIs                                 #
###############################################################################

def select_poi_max_rank(array, N_poi, poi_space):
    """
    Select POI from the array acc.to. max rank.

    Parameters
    ----------
    array : ndarray
        Shape (#sample,), the t-score or SNR or SOD.
    N_poi : int
        The maximum number of POIs to select from the array.
    poi_space : int
        The number of adjacent indices (before and after) that should not be
        selected once a POI has been specified.
        This parameter addresses the tendency for maximum values in the array
        to cluster together.
        By setting 'poi_space' to a positive integer (e.g., 3), one can
        mitigate the over-concentration of selected points and ensure diversity
        in the selection. The following illustration depicts this concept:

               |
              ||
              |||
              ||||      |
              ||||      ||
        |     ||||     |||
        ||    ||||     ||||

        It's recommended to adjust 'poi_space' based on empirical observations.

    Returns
    -------
    poi : list[int]
        A list of indices representing the selected POIs. All entries are
        integers within the range of #sample.
    """
    array_tmp = array.copy()

    poi = []

    for i in range(N_poi):
        nextPOI = np.argmax(array_tmp)
        poi.append(int(nextPOI))
        poiMin = max(0, nextPOI - poi_space)
        poiMax = min(nextPOI + poi_space, len(array_tmp) - 1)
        for j in range(poiMin, poiMax+1):
            array_tmp[j] = 0
    return poi


def select_poi_threshold(array, threshold):
    """
    Select POI from the array if larger than threshold.

    Parameters
    ----------
    array : np.ndarray
        Shape (#sample,), the t-score or SNR or SOD.
    threshold: np.ndarray or int
        Could be const array [0.001]*#sample or t-score.

    Returns
    -------
    poi : list[int]
        A list of indices representing the selected POIs. All entries are
        integers within the range of #sample.
    """
    return np.where(array > threshold)[0]


def _clusters(idx, gap):
    """Group sorted indices into runs; split where the gap exceeds `gap`."""
    out = [[idx[0]]]
    for i in idx[1:]:
        (out.append([i]) if i - out[-1][-1] > gap else out[-1].append(i))
    return out


def leakage_markers_fp(snr, height_frac=0.03, distance=4,
                       gap_peak=25, gap_rect=45, pad=4):
    """
    find_peaks-based variant of leakage_markers: keeps the low cycle-0 Sign peak.
       cand   -- local maxima ≥ height_frac*max, ≥ distance apart;
       peaks  -- fine clusters' argmax  -> dashed vertical lines;
       rects  -- coarse clusters, padded -> red rectangles.
    """
    snr = np.asarray(snr); n = len(snr)
    cand, _ = sp.signal.find_peaks(snr, height=height_frac * snr.max(), distance=distance)
    if len(cand) == 0:
        return [], []
    peaks = [int(c[int(np.argmax(snr[c]))]) for c in _clusters(cand, gap_peak)]
    rects = [(max(0, c[0] - pad), min(n - 1, c[-1] + pad)) for c in _clusters(cand, gap_rect)]
    return peaks, rects


def print_peaks(peaks, addr_cycloc, SNR):
    peak = {}
    for cycloc in peaks:  # pick the first 6 peaks
        for k, v in addr_cycloc.items():
            if cycloc in v:
                peak[k] = cycloc
    rows = sorted(peak.items(), key=lambda kv: SNR[kv[1]], reverse=True)
    addr_w = max(len(k) for k, _ in rows)
    cyc_w = max(len(str(cycloc)) for _, cycloc in rows)
    snr_w = max(len(f"{SNR[cycloc]:.4f}") for _, cycloc in rows)
    for k, cycloc in rows:
        print(f"{k:<{addr_w}} {cycloc:>{cyc_w}} {SNR[cycloc]:>{snr_w}.4f}")


###############################################################################
#                               Template Attack                               #
###############################################################################


def gaussian_profile(traces_dict, poi, template_name):
    """
    Build mean and covariance templates per class at selected POIs.

    Parameters
    ----------
    traces_dict : dict[int: np.ndarray]
        Maps label (int) → traces (#trace, #sample):
        {
            label_1: np.ndarray,  # shape (#trace/label_1, #sample)
            label_2: np.ndarray,  # shape (#trace/label_2, #sample)
            ...,
            label_n: np.ndarray   # shape (#trace/label_n, #sample)
        }
    poi : list[int]
        List of sample indices to extract as POIs

    Returns
    -------
    template : tuple
        A tuple of (f, poi), where:
        - f : dict[int: sp.stats.multivariate_normal]
            Maps label (int) → f(x|theta), where theta = (mean, cov)
        - poi : list[int]
            The POI indices.
    Notes
    -----
    'f' is mathematically f(x|theta), where theta = (mean, cov), constructed by
        f[c] = sp.stats.multivariate_normal(mean[c], cov[c])
    where
    mean : dict[int: np.ndarray]
        Maps label (int) → poi mean (#poi,)
        {
            label_1: np.ndarray,  # shape (#poi,)
            label_2: np.ndarray,  # shape (#poi,)
            ...,
            label_n: np.ndarray,  # shape (#poi,)
        }
    cov: dict[int: np.ndarray]
        Maps label (int) → poi cov (#poi, #poi)
        {
            label_1: np.ndarray,  # shape (#poi, #poi)
            label_2: np.ndarray,  # shape (#poi, #poi)
            ...,
            label_n: np.ndarray,  # shape (#poi, #poi)
        }

    Therefore we can extract mean and cov via
    - mean = {k: v.mean for k, v in f.items()}
    - cov = {k: v.cov for k, v in f.items()}
    """
    label = sorted(traces_dict.keys())
    N_poi = len(poi)

    trace_mean = {}
    mean = {}
    cov = {}
    f = {}
    for c in label:
        trace_mean[c] = np.mean(traces_dict[c], axis=0)
        mean[c] = np.zeros((N_poi))
        cov[c] = np.zeros((N_poi, N_poi))
        for i in range(N_poi):
            mean[c][i] = trace_mean[c][poi[i]]
            for j in range(N_poi):
                xi = traces_dict[c][:, poi[i]]
                xj = traces_dict[c][:, poi[j]]
                cov[c][i, j] = np.cov(xi, xj)[0, 1]
        # f(x|theta[c]), theta[c] = (mean, cov)
        f[c] = sp.stats.multivariate_normal(mean[c], cov[c])
    template = (f, poi)
    with open(template_name, 'wb') as fp:
        pickle.dump(template, fp)
    return template


def gaussian_inference(traces_test, template_name):
    """
    Gaussian-template inference returning per-class posterior PROBABILITIES.

    This returns the full normalized probability vector per trace.  It is
    (a) faithful to the Gaussian template idea --- it uses the pdf, not a hard
        decision --- and
    (b) drop-in compatible with the MLE machinery (mle_distribution /
        mle_choose_value), exactly like a softmax classifier's output.

    Parameters
    ----------
    traces_test : np.ndarray
        Shape (#trace, #sample), the traces to classify.
    template_name : str
        Path to the pickled (f, poi) template written by gaussian_profile, where
        f is dict[class -> sp.stats.multivariate_normal] and poi is the POI list.

    Returns
    -------
    prob : np.ndarray
        Shape (#trace, #class), per-class posterior probability under a uniform
        prior (softmax over the per-class Gaussian log-likelihoods).
    """
    with open(template_name, 'rb') as fp:
        f, poi = pickle.load(fp)
    n_class = len(f)
    X = np.asarray(traces_test)[:, poi]
    logp = np.empty((X.shape[0], n_class))
    for c in range(n_class):
        logp[:, c] = f[c].logpdf(X)                 # log f(x|theta_c)
    # posterior under a uniform prior = softmax over per-class log-likelihoods
    logp -= logp.max(axis=1, keepdims=True)
    prob = np.exp(logp)
    prob /= prob.sum(axis=1, keepdims=True)
    return prob


def gaussian_guess(prob):
    """
    Hard label (argmax) from per-class posterior probabilities.

    This is the *decision* half of the Gaussian template attack; the
    *probability* half is gaussian_inference, which turns traces into the per-class
    posterior.  Splitting them this way lets the posterior feed the MLE
    machinery (mle_distribution / mle_choose_value), while gaussian_guess is just
    the final argmax over the classes.

    Parameters
    ----------
    prob : np.ndarray
        Shape (#trace, #class), per-class posterior probability, as returned by
        gaussian_inference.

    Returns
    -------
    guess : np.ndarray
        Shape (#trace,), the argmax class id per trace.
    """
    return np.argmax(prob, axis=1)


def naive_report(guess, label_test):
    """
    Check the success rate and error guess of the template attack.

    Parameters
    ----------
    guess : np.ndarray
        Shape (#label x #trace,), the guess label
    label_test : np.ndarray
        Shape (#label x #trace,), the label of the attacked traces

    Returns
    -------
    None
    """
    total = len(label_test)  # #label x #trace
    success = 0
    error_guess = []

    for i in range(total):
        if guess[i] == label_test[i]:
            success += 1
        else:
            error_guess.append(int(label_test[i]))

    print(f"#Success: {success}")
    print(f"%Success: {success / total:.2%}")
    print(f"Error guess: {error_guess}")
    print(f"Counter: {collections.Counter(error_guess)}")
    return success / total


###############################################################################
#                        Stage Stats Correctness Report                       #
###############################################################################

def _true_scaled_label(coeff):
    for c, vals in class_coeffs_map_scaled.items():
        if coeff in vals:
            return c
    return None  # |v| > 22 → outside the modelled range


def _true_shift55_label(coeff):
    """
    Notes
    -----
    Return None if:
    - coeff = 0
    - coeff = ±1
    - abs(coeff) is either in set0 not set1
    """
    set0 = set(class_coeffs_map_shift55[0])
    set1 = set(class_coeffs_map_shift55[1])
    a = abs(coeff)
    if a in set0:
        return 0
    if a in set1:
        return 1
    return None


def stats_init():
    return collections.defaultdict(lambda:
                                   {"ok": 0,
                                    "total": 0,
                                    "misroute": 0,
                                    "counter": {},
                                    "error_guess": []})


def report_sr(key_type, leakage, key, stage_stats, item_dict, truth_fn):
    """
    Report success rate of key guess.

    key_type: "profile" or "f" or "g"
    leakage: "scaled", "shift55", "mul45", "mul67"  (or "mul23", "mul47" when SKIP_SHIFT55)

    "ok" a.k.a. "correct"
    "misroute" a.k.a. "skipped"

    Print, and store (by overwrite) into stage_stats[leakage], the per-stage correctness
    of one attacked key row against its ground-truth coefficients.
      scaled : all 512 coeffs, no routing dependency → the clean O3-vs-Os number.
      shift55/mul : conditioned on upstream routing; "mis-routed here" counts the
                    coeffs that landed in the stage due to an upstream (scaled) error
                    (their true value does not even belong to the stage's domain).

    Parameters
    ----------
    key_type : str
        "profile", "f", or "g" --- which key is being reported (the profiling key,
        or the f / g half of an attacked key). Identifies the key in the printed line.
    leakage : str
        Stage name, and the key into stage_stats: "scaled", "shift55", "mul45",
        "mul67", or the skip-shift55 stages "mul23", "mul47".
    key : array-like of int
        Ground-truth coefficient row (length FALCON_N) of the attacked key half,
        e.g. Falcon512_f_1000[key_id]. Indexed by the coefficient indices of item_dict.
    stage_stats : dict
        Per-stage accumulator; stage_stats[leakage] → {"ok", "total", "misroute",
        "error_guess"}. One is kept per key_type --- stage_stats_f, stage_stats_g,
        stage_stats_profile. Written by OVERWRITE (not +=) with this key's snapshot,
        so it holds only the most recent key and error_guess stays scoped to that key
        for debugging; cross-key totals are folded elsewhere (the Main loop).
    item_dict : dict
        {coeff_index: predicted_label} from this stage's classifier (argmax / MLE).
    truth_fn : callable
        int(coeff value) → expected label, or None when the value is outside this
        stage's domain. A None marks the coefficient as mis-routed by an upstream
        stage: it is excluded from ok/total and counted under "misroute".

    Returns
    -------
    None
        Side effects only: prints one "[key_type] [leakage] ok/total = acc" line and
        stores the snapshot in stage_stats[leakage]; each error_guess entry is the
        tuple (idx, true_value, pred, true_label).
    """
    ok = total = misroute = 0
    error_guess = []
    for idx, pred in item_dict.items():
        true = truth_fn(int(key[idx]))
        if true is None:                          # true value not in this stage's domain
            misroute += 1
            continue
        total += 1
        pred = int(pred)
        if pred == true:
            ok += 1
        else:
            error_guess.append((idx, int(key[idx]), pred, true))
    counter = collections.Counter(true for *_, true in error_guess)
    if total:
        line = f"[{key_type}] [{leakage:>10}] {ok}/{total} = {ok/total:.4f}"
    else:
        line = f"[{key_type}] [{leakage:>10}] n/a"
    if misroute:
        line += f"   (mis-routed here: {misroute})"
    print(line)
    s = stage_stats[leakage]
    s["ok"] = ok
    s["total"]  = total
    s["misroute"] = misroute
    s["counter"] = counter
    s["error_guess"] = error_guess


def report_error(leakage, stage_stats, class_coeffs_map):
    s = stage_stats[leakage]
    print("error count per class  (class = labels: count):")
    for c, cnt in dict(s["counter"]).items():
        print(f"  class {c} = {class_coeffs_map[c]}: {cnt}")
    print("error guesses  (coeff idx: true → pred):")
    for idx, _, pred, true in s["error_guess"]:
        print(f"  key[{idx:4d}]: class {true} {class_coeffs_map[true]} → class {pred} {class_coeffs_map[pred]}")


###############################################################################
#                                    Attack                                   #
###############################################################################

def mle_choose_value(prob_dict):
    mle_tmp_f_dict={}
    for k, prob_array in prob_dict.items():
        log_prob_array = np.log(prob_array)
        col_sum = np.sum(log_prob_array, axis=0)
        max_index = np.argmax(col_sum)
        mle_tmp_f_dict[k]=max_index
    return mle_tmp_f_dict


def mle_distribution(prob_dict):
    prob_dict_mle = {}
    epsilon = 1e-12
    for k, prob_array in prob_dict.items():
        log_prob_array = np.log(prob_array + epsilon)
        col_sum = np.sum(log_prob_array, axis=0)
        max_val = np.max(col_sum)
        exp_array = np.exp(col_sum - max_val)
        final_prob = exp_array / np.sum(exp_array)
        prob_dict_mle[k] = final_prob
    return prob_dict_mle


def record_sign(guess_attack_scaled,drop_list,falcon_n):
    sign_dict = {}
    tmp_idx_list = [i for i in range(falcon_n) if i not in drop_list]
    for i in tmp_idx_list:
        ele = guess_attack_scaled[i]
        if class_coeffs_map_scaled[ele][0] == 0:
            sign_dict[i] = 0
        elif class_coeffs_map_scaled[ele][0] > 0:
            sign_dict[i] = 1
        elif class_coeffs_map_scaled[ele][0] < 0:
            sign_dict[i] = -1
    return sign_dict


def record_sign_origin(guess_attack_scaled, falcon_n):
    sign_dict = {}
    # tmp_idx_list = [i for i in range(falcon_n) if i not in drop_list]
    for i in range(falcon_n):
        ele = guess_attack_scaled[i]
        if class_coeffs_map_scaled[ele][0] == 0:
            sign_dict[i] = 0
        elif class_coeffs_map_scaled[ele][0] > 0:
            sign_dict[i] = 1
        elif class_coeffs_map_scaled[ele][0] < 0:
            sign_dict[i] = -1
    return sign_dict


def record_abs_table_index(guess_attack_scaled, drop_list, falcon_n):
    abs_dict = {}
    tmp_idx_list = [i for i in range(falcon_n) if i not in drop_list]
    for i in tmp_idx_list:
        ele = guess_attack_scaled[i]
        if ele == 0:
            abs_dict[i] = 0
        elif ele == 1 or ele == 2:
            abs_dict[i] = 1
        elif ele == 3 or ele == 4:
            abs_dict[i] = 2
        elif ele == 5 or ele == 6:
            abs_dict[i] = 3
        elif ele == 7 or ele == 8:
            abs_dict[i] = 4
        elif ele == 9 or ele == 10:
            abs_dict[i] = 5
    return abs_dict


def record_abs_table_index_origin(guess_attack_scaled, falcon_n):
    abs_dict = {}
    # tmp_idx_list = [i for i in range(falcon_n) if i not in drop_list]
    for i in range(falcon_n):
        ele = guess_attack_scaled[i]
        if ele == 0:
            abs_dict[i] = 0
        elif ele == 1 or ele == 2:
            abs_dict[i] = 1
        elif ele == 3 or ele == 4:
            abs_dict[i] = 2
        elif ele == 5 or ele == 6:
            abs_dict[i] = 3
        elif ele == 7 or ele == 8:
            abs_dict[i] = 4
        elif ele == 9 or ele == 10:
            abs_dict[i] = 5
    return abs_dict


def reorder_traces(A):
    """
    Adjust the row order of A from [128,384,128,384,...] to [128,128,129,129,...,511,511]
    """
    small = A[0::2, :]
    large = A[1::2, :]
    A_new = np.vstack([small, large])
    return A_new


def generate_diffset_label(co_labels, target_filtered, set0):
    label_diffset = []
    for c in target_filtered:
        if co_labels[c] in set0 or -co_labels[c] in set0:
            label_diffset.append(0)
        else:
            label_diffset.append(1)
    label_diffset = np.array(label_diffset)
    return label_diffset


def select_rows_by_labels(M, labels, subset):
    """
    Select rows from a 2D array M, with row labels provided by `labels`.

    Parameters:
    M: numpy.array, shape = (n, m)
    labels: list or array, length = n, the labels for each row in M
    subset: list or set, the desired subset of labels

    Returns:
    N: numpy.array, shape = (len(subset), m),
    The row order is the same as in the subset.
    """
    labels = np.array(labels)
    subset = list(subset)
    idx = [np.where(labels == s)[0][0] for s in subset]
    N = M[idx, :]
    return N


def fill_dict(to_fill_dict, prob_dict):
    for kk, prob_list in prob_dict.items():
        if kk not in to_fill_dict:
            to_fill_dict[kk] = prob_list
        else:
            to_fill_dict[kk] = np.vstack([to_fill_dict[kk], prob_list])


def dict_process(fpr_diffset_mle_prob_list):
    fpr_diffset_mle_prob_list = dict(fpr_diffset_mle_prob_list)
    fpr_diffset_mle_prob_list = {key_coeff: np.array(val_list) for key_coeff, val_list in fpr_diffset_mle_prob_list.items()}
    return fpr_diffset_mle_prob_list


###############################################################################
#                                 Multi-thread                                #
###############################################################################

class _ThreadRouter:
    """
    Per-thread stdout capture

    print() lives deep inside attack.py, so to buffer each key's output on its
    own we route sys.stdout to a PER-THREAD buffer (a plain redirect_stdout is
    a single global and would clobber across threads).  A thread with no buffer
    set (e.g. the main thread) falls through to the real stdout.
    """
    def __init__(self, real):
        self._real = real
        self._local = threading.local()

    def set_buffer(self, buf):
        self._local.buf = buf

    def clear_buffer(self):
        self._local.buf = None

    def _target(self):
        buf = getattr(self._local, "buf", None)
        return buf if buf is not None else self._real

    def write(self, s):
        self._target().write(s)

    def flush(self):
        self._target().flush()
