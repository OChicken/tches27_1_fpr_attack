# One Fell Swoop: A Single-Trace Key-Recovery Attack on the Falcon Signing Algorithm

This repository contains the code accompanying the paper

> **One Fell Swoop: A Single-Trace Key-Recovery Attack on the Falcon Signing Algorithm**
> Kang Li, Shouran Ma, Haochen Dou and Qian Guo
> IACR Transactions on Cryptographic Hardware and Embedded Systems (TCHES)

## Authors

- [Kang Li](https://github.com/likang175) (0009-0005-4928-4483)
- [Shouran Ma](https://github.com/OChicken) (0009-0003-0472-6458)
- [Haochen Dou](https://github.com/YagamiTakayuki) (0009-0000-0062-5463)
- [Qian Guo](https://sites.google.com/view/qianguo/) (0000-0003-0930-3174)

## Abstract

Falcon, a lattice-based signature scheme selected for NIST post-quantum standardization, is notable for its compact signature size alongside a complex signing procedure involving extensive floating-point arithmetic.
Prior side-channel attacks on Falcon signing, while demonstrating vulnerabilities, have consistently required a large number of power traces for successful key recovery, which limits their real-world practicality.
This paper presents a new single-trace attack on the Falcon signing procedure.
We exploit side-channel leakage in the FP conversion and identify additional leakage in the FP multiplication at the first layer of the Fast Fourier Transform (FFT) during secret key expansion.
By combining these leakages, we progressively partition the secret-key coefficients and establish a linear system to recover the entire key.
Our attack is particularly devastating for the `sign_dyn` design—the memory-efficient implementation widely adopted in cryptographic libraries—which executes key expansion during every signature operation.
We validate our attack on an ARM Cortex-M4 microcontroller, achieving a 100% key recovery success rate with just one power trace for Falcon-512 across the baseline `-O0`, size-optimized `-Os`, and highest `-O3` compilation levels of the PQClean implementation.
Crucially, we also evaluate the Falcon team's highly optimized embedded assembly (ASM) implementation.
Despite its reduced leakage, our adapted multi-trace attack successfully recovers 53 out of 100 test keys with only 10 traces.
This marks the first successful single-trace attack at the `-O3` level and the first practical attack against the embedded ASM Falcon.
Furthermore, our in-depth assembly analysis of these vulnerabilities provides critical guidelines for designing more secure, hardened embedded assembly implementations.
