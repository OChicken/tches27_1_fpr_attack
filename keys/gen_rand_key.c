#include <stdlib.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "keygen.c"
#include "falcon.h"

#define FALCON_LOGN 9
#define FALCON_N (1 << FALCON_LOGN)

static void *
xmalloc(size_t len)
{
	void *buf;

	if (len == 0) {
		return NULL;
	}
	buf = malloc(len);
	if (buf == NULL) {
		fprintf(stderr, "memory allocation error\n");
		exit(EXIT_FAILURE);
	}
	return buf;
}

static void
xfree(void *buf)
{
	if (buf != NULL) {
		free(buf);
	}
}

/*
 * Sample a private-key polynomial f using the given (already flipped) SHAKE
 * PRNG. This calls the project's own Zf(keygen) exactly as falcon.c does, and
 * keeps only f; the companion g and the NTRU solution F are written to scratch
 * buffers and discarded (h is not computed at all). n = 1<<logn coefficients
 * are written to out. Returns n, or -1 on bad logn.
 */
static int
sample_f(inner_shake256_context *rng, int8_t *out, unsigned logn)
{
	size_t n;
	int8_t *g, *F;
	uint8_t *tmp;
	unsigned oldcw;

	if (logn < 1 || logn > 10) {
		return -1;
	}
	n = (size_t)1 << logn;
	g = xmalloc(n);
	F = xmalloc(n);
	tmp = xmalloc(FALCON_TMPSIZE_KEYGEN(logn));

	oldcw = set_fpu_cw(2);
	Zf(keygen)(rng, out, g, F, NULL, NULL, logn, tmp);
	set_fpu_cw(oldcw);

	xfree(g);
	xfree(F);
	xfree(tmp);
	return (int)n;
}

/*
 * Public entry points (external linkage) for use as a shared library from
 * Python via ctypes. out must point to at least (1<<logn) int8_t.
 */

/* Seed from the operating system RNG. Returns n on success, -1 on error. */
int
gen_rand_f(int8_t *out, unsigned logn)
{
	shake256_context rng;

	if (shake256_init_prng_from_system(&rng) != 0) {
		return -1;
	}
	return sample_f((inner_shake256_context *)&rng, out, logn);
}

int
main(void)
{
	int8_t *f;
	int n, i;

	f = xmalloc(FALCON_N);
	n = gen_rand_f(f, FALCON_LOGN);
	if (n < 0) {
		fprintf(stderr, "key generation failed\n");
		exit(EXIT_FAILURE);
	}

	putchar('[');
	for (i = 0; i < n; i ++) {
		if (i > 0) {
			fputs(", ", stdout);
		}
		printf("%d", (int)f[i]);
	}
	puts("]");

	xfree(f);
	return 0;
}
