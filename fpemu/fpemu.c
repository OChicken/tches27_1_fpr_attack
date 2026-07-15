#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <inttypes.h>
#include <string.h>

/* experiment settings *******************************************************/
#include "hal.h"
#include "simpleserial.h"
#include "tracewhisperer.h"

/* Falcon ********************************************************************/

#define FALCON_LOGN 9
#define FALCON_N (1 << FALCON_LOGN)
int8_t f[FALCON_N];
int8_t g[FALCON_N];
int8_t F[FALCON_N];
int8_t G[FALCON_N];
int8_t sk[FALCON_N];

#include "inner.h"

/* BELOW are from sign.c line 36-39, 183-196, resp. **************************/

/*
 * Compute degree N from logarithm 'logn'.
 */
#define MKN(logn)   ((size_t)1 << (logn))

/*
 * Convert an integer polynomial (with small values) into the
 * representation with complex numbers.
 */
static void
smallints_to_fpr(fpr *r, const int8_t *t, unsigned logn)
{
	size_t n, u;

	n = MKN(logn);
	for (u = 0; u < n; u ++) {
		r[u] = fpr_of(t[u]);
	}
}

/* ABOVE are from sign.c line 36-39, 183-196, resp. **************************/

/* BELOW are from fft.c, line 34-86 and line 145-300, resp.
 * Attention: in function Zf(FFT) we modified "u < logn" in line 179, to
 * "u < 2", since we only consider the 1st layer. ***************/

/*
 * Rules for complex number macros:
 * --------------------------------
 *
 * Operand order is: destination, source1, source2...
 *
 * Each operand is a real and an imaginary part.
 *
 * All overlaps are allowed.
 */

/*
 * Addition of two complex numbers (d = a + b).
 */
#define FPC_ADD(d_re, d_im, a_re, a_im, b_re, b_im)   do { \
		fpr fpct_re, fpct_im; \
		fpct_re = fpr_add(a_re, b_re); \
		fpct_im = fpr_add(a_im, b_im); \
		(d_re) = fpct_re; \
		(d_im) = fpct_im; \
	} while (0)

/*
 * Subtraction of two complex numbers (d = a - b).
 */
#define FPC_SUB(d_re, d_im, a_re, a_im, b_re, b_im)   do { \
		fpr fpct_re, fpct_im; \
		fpct_re = fpr_sub(a_re, b_re); \
		fpct_im = fpr_sub(a_im, b_im); \
		(d_re) = fpct_re; \
		(d_im) = fpct_im; \
	} while (0)

/*
 * Multplication of two complex numbers (d = a * b).
 */
#define FPC_MUL(d_re, d_im, a_re, a_im, b_re, b_im)   do { \
		fpr fpct_a_re, fpct_a_im; \
		fpr fpct_b_re, fpct_b_im; \
		fpr fpct_d_re, fpct_d_im; \
		fpct_a_re = (a_re); \
		fpct_a_im = (a_im); \
		fpct_b_re = (b_re); \
		fpct_b_im = (b_im); \
		fpct_d_re = fpr_sub( \
			fpr_mul(fpct_a_re, fpct_b_re), \
			fpr_mul(fpct_a_im, fpct_b_im)); \
		fpct_d_im = fpr_add( \
			fpr_mul(fpct_a_re, fpct_b_im), \
			fpr_mul(fpct_a_im, fpct_b_re)); \
		(d_re) = fpct_d_re; \
		(d_im) = fpct_d_im; \
	} while (0)

/*
 * Let w = exp(i*pi/N); w is a primitive 2N-th root of 1. We define the
 * values w_j = w^(2j+1) for all j from 0 to N-1: these are the roots
 * of X^N+1 in the field of complex numbers. A crucial property is that
 * w_{N-1-j} = conj(w_j) = 1/w_j for all j.
 *
 * FFT representation of a polynomial f (taken modulo X^N+1) is the
 * set of values f(w_j). Since f is real, conj(f(w_j)) = f(conj(w_j)),
 * thus f(w_{N-1-j}) = conj(f(w_j)). We thus store only half the values,
 * for j = 0 to N/2-1; the other half can be recomputed easily when (if)
 * needed. A consequence is that FFT representation has the same size
 * as normal representation: N/2 complex numbers use N real numbers (each
 * complex number is the combination of a real and an imaginary part).
 *
 * We use a specific ordering which makes computations easier. Let rev()
 * be the bit-reversal function over log(N) bits. For j in 0..N/2-1, we
 * store the real and imaginary parts of f(w_j) in slots:
 *
 *    Re(f(w_j)) -> slot rev(j)/2
 *    Im(f(w_j)) -> slot rev(j)/2+N/2
 *
 * (Note that rev(j) is even for j < N/2.)
 */

/* see inner.h */
TARGET_AVX2
void
Zf(FFT)(fpr *f, unsigned logn)
{
	/*
	 * FFT algorithm in bit-reversal order uses the following
	 * iterative algorithm:
	 *
	 *   t = N
	 *   for m = 1; m < N; m *= 2:
	 *       ht = t/2
	 *       for i1 = 0; i1 < m; i1 ++:
	 *           j1 = i1 * t
	 *           s = GM[m + i1]
	 *           for j = j1; j < (j1 + ht); j ++:
	 *               x = f[j]
	 *               y = s * f[j + ht]
	 *               f[j] = x + y
	 *               f[j + ht] = x - y
	 *       t = ht
	 *
	 * GM[k] contains w^rev(k) for primitive root w = exp(i*pi/N).
	 *
	 * In the description above, f[] is supposed to contain complex
	 * numbers. In our in-memory representation, the real and
	 * imaginary parts of f[k] are in array slots k and k+N/2.
	 *
	 * We only keep the first half of the complex numbers. We can
	 * see that after the first iteration, the first and second halves
	 * of the array of complex numbers have separate lives, so we
	 * simply ignore the second part.
	 */

	unsigned u;
	size_t t, n, hn, m;

	/*
	 * First iteration: compute f[j] + i * f[j+N/2] for all j < N/2
	 * (because GM[1] = w^rev(1) = w^(N/2) = i).
	 * In our chosen representation, this is a no-op: everything is
	 * already where it should be.
	 */

	/*
	 * Subsequent iterations are truncated to use only the first
	 * half of values.
	 */
	n = (size_t)1 << logn;
	hn = n >> 1;
	t = hn;
	for (u = 1, m = 2; u < 2; u ++, m <<= 1) { /* HERE: 'u < logn' => 'u < 2'; rm 'm<<=1' */
		size_t ht, hm, i1, j1;

		ht = t >> 1;
		hm = m >> 1;
		for (i1 = 0, j1 = 0; i1 < hm; i1 ++, j1 += t) {
			size_t j, j2;

			j2 = j1 + ht;
#if FALCON_AVX2 // yyyAVX2+1
			if (ht >= 4) {
				__m256d s_re, s_im;

				s_re = _mm256_set1_pd(
					fpr_gm_tab[((m + i1) << 1) + 0].v);
				s_im = _mm256_set1_pd(
					fpr_gm_tab[((m + i1) << 1) + 1].v);
				for (j = j1; j < j2; j += 4) {
					__m256d x_re, x_im, y_re, y_im;
					__m256d z_re, z_im;

					x_re = _mm256_loadu_pd(&f[j].v);
					x_im = _mm256_loadu_pd(&f[j + hn].v);
					z_re = _mm256_loadu_pd(&f[j+ht].v);
					z_im = _mm256_loadu_pd(&f[j+ht + hn].v);
					y_re = FMSUB(z_re, s_re,
						_mm256_mul_pd(z_im, s_im));
					y_im = FMADD(z_re, s_im,
						_mm256_mul_pd(z_im, s_re));
					_mm256_storeu_pd(&f[j].v,
						_mm256_add_pd(x_re, y_re));
					_mm256_storeu_pd(&f[j + hn].v,
						_mm256_add_pd(x_im, y_im));
					_mm256_storeu_pd(&f[j + ht].v,
						_mm256_sub_pd(x_re, y_re));
					_mm256_storeu_pd(&f[j + ht + hn].v,
						_mm256_sub_pd(x_im, y_im));
				}
			} else {
				fpr s_re, s_im;

				s_re = fpr_gm_tab[((m + i1) << 1) + 0];
				s_im = fpr_gm_tab[((m + i1) << 1) + 1];
				for (j = j1; j < j2; j ++) {
					fpr x_re, x_im, y_re, y_im;

					x_re = f[j];
					x_im = f[j + hn];
					y_re = f[j + ht];
					y_im = f[j + ht + hn];
					FPC_MUL(y_re, y_im,
						y_re, y_im, s_re, s_im);
					FPC_ADD(f[j], f[j + hn],
						x_re, x_im, y_re, y_im);
					FPC_SUB(f[j + ht], f[j + ht + hn],
						x_re, x_im, y_re, y_im);
				}
			}
#else // yyyAVX2+0
			fpr s_re, s_im;

			s_re = fpr_gm_tab[((m + i1) << 1) + 0];
			s_im = fpr_gm_tab[((m + i1) << 1) + 1];
			for (j = j1; j < j2; j ++) {
				fpr x_re, x_im, y_re, y_im;

				x_re = f[j];
				x_im = f[j + hn];
				y_re = f[j + ht];
				y_im = f[j + ht + hn];
				FPC_MUL(y_re, y_im, y_re, y_im, s_re, s_im);
				FPC_ADD(f[j], f[j + hn],
					x_re, x_im, y_re, y_im);
				FPC_SUB(f[j + ht], f[j + ht + hn],
					x_re, x_im, y_re, y_im);
			}
#endif // yyyAVX2-
		}
		t = ht;
	}
}

/* ABOVE are from fft.c, line 34-86 and line 145-300, resp.
 * Attention: in function Zf(FFT) we modified "u < logn" in line 179, to
 * "u < 2", since we only consider the 1st layer. ***************/

uint8_t recv_f(uint8_t* x, uint32_t len)
{
	memset(f, 0, FALCON_N);
	memcpy(f, x, len);
	printf("[%2d, %2d, ..., %2d, %2d]\n",
	       f[0], f[1], f[FALCON_N-2], f[FALCON_N-1]);
	return 0;
}

uint8_t recv_g(uint8_t* x, uint32_t len)
{
	memset(g, 0, FALCON_N);
	memcpy(g, x, len);
	printf("[%2d, %2d, ..., %2d, %2d]\n",
	       g[0], g[1], g[FALCON_N-2], g[FALCON_N-1]);
	return 0;
}

uint8_t recv_F(uint8_t* x, uint32_t len)
{
	memset(F, 0, FALCON_N);
	memcpy(F, x, len);
	printf("[%2d, %2d, ..., %2d, %2d]\n",
	       F[0], F[1], F[FALCON_N-2], F[FALCON_N-1]);
	return 0;
}

uint8_t recv_G(uint8_t* x, uint32_t len)
{
	memset(G, 0, FALCON_N);
	memcpy(G, x, len);
	printf("[%2d, %2d, ..., %2d, %2d]\n",
	       G[0], G[1], G[FALCON_N-2], G[FALCON_N-1]);
	return 0;
}

uint8_t recv_sk(uint8_t* x, uint32_t len)
{
	memset(sk, 0, FALCON_N);
	memcpy(sk, x, len);
	printf("[%2d, %2d, ..., %2d, %2d]\n",
	       sk[0], sk[1], sk[FALCON_N-2], sk[FALCON_N-1]);
	return 0;
}

uint8_t do_sign_dyn_trim(uint8_t *x, uint32_t len)
{
	uint32_t t0, t1;
	unsigned logn = FALCON_LOGN;
	size_t n;
	fpr tmp[2 * FALCON_N];
	fpr *b00, *b01;

	n = MKN(logn);

	b00 = tmp;
	b01 = b00 + n;

	trigger_high_pcsamp();
#ifdef TEST_CYCLE
#pragma message "TEST_CYCLE defined"
	t0 = HAL_CYCCNT();
	smallints_to_fpr(b01, sk, logn);
	t1 = HAL_CYCCNT();
	printf("smallints_to_fpr: %" PRIu32 "\n", t1 - t0);
	t0 = HAL_CYCCNT();
	Zf(FFT)(b01, logn);
	t1 = HAL_CYCCNT();
	printf("Zf(FFT): %" PRIu32 "\n", t1 - t0);
#else
	smallints_to_fpr(b01, sk, logn);
	Zf(FFT)(b01, logn);
#endif
	trigger_low_pcsamp();
	return 0;
}

#if (defined __ARM_ARCH_7EM__ && __ARM_ARCH_7EM__) \
	&& (defined __ARM_FEATURE_DSP && __ARM_FEATURE_DSP)
#pragma message "__ARM_ARCH_7EM__ && __ARM_FEATURE_DSP defined"
#endif

#if FALCON_FPEMU  // yyyFPEMU+1 yyyFPNATIVE+0
#pragma message "FALCON_FPEMU defined"
#elif FALCON_FPNATIVE  // yyyFPEMU+0 yyyFPNATIVE+1
#pragma message "FALCON_FPNATIVE defined"
#else  // yyyFPEMU+0 yyyFPNATIVE+0
#error No FP implementation selected
#endif

#if FALCON_ASM_CORTEXM4 // yyyASM_CORTEXM4+1
#pragma message "FALCON_ASM_CORTEXM4 defined"
#else // yyyASM_CORTEXM4+0
#pragma message "FALCON_ASM_CORTEXM4 NOT defined"
#endif

int main(int argc, char *argv[])
{
	hal_setup();

	simpleserial_addcmd('1', recv_f);
	simpleserial_addcmd('2', recv_g);
	simpleserial_addcmd('3', recv_F);
	simpleserial_addcmd('4', recv_G);
	simpleserial_addcmd('k', recv_sk);
	simpleserial_addcmd('p', do_sign_dyn_trim);

	/* TraceWhisperer settings */
	simpleserial_addcmd('c', set_pcsample_params);
	simpleserial_addcmd('s', setreg);
	simpleserial_addcmd('g', getreg);
	/* simpleserial_addcmd('i', info); */
	enable_trace();

	while (1)
		simpleserial_get();
}
