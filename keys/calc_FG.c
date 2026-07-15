#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <math.h>

#include "keygen.c"
#include "falcon.h"

#define FALCON_LOGN 9
#define FALCON_N    (1 << FALCON_LOGN)

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

static FILE *
open_npy(const char *path)
{
	uint8_t buf[10];
	uint16_t header_len;
	FILE *fp;

	fp = fopen(path, "rb");
	if (fp == NULL)
		return NULL;
	if (fread(buf, 1, 10, fp) != 10) {
		fclose(fp);
		return NULL;
	}
	if (memcmp(buf, "\x93NUMPY", 6) != 0) {
		fclose(fp);
		return NULL;
	}
	header_len = buf[8] | ((uint16_t)buf[9] << 8);
	fseek(fp, header_len, SEEK_CUR);
	return fp;
}

static int
read_npy_row(FILE *fp, int8_t *out, int n)
{
	return fread(out, 1, (size_t)n, fp) == (size_t)n;
}

static FILE *
create_npy(const char *path, int n_rows, int n_cols, const char *descr)
{
	char hdr[256];
	uint8_t buf[10];
	int base_len, hdr_len;
	FILE *fp;

	fp = fopen(path, "wb");
	if (fp == NULL)
		return NULL;

	base_len = snprintf(hdr, sizeof hdr,
		"{'descr': '%s', 'fortran_order': False, 'shape': (%d, %d), }",
		descr, n_rows, n_cols);
	/* pad with spaces so (10 + hdr_len) is a multiple of 64, end with \n */
	hdr_len = base_len + 1;
	while ((10 + hdr_len) % 64 != 0) hdr_len++;
	memset(hdr + base_len, ' ', hdr_len - base_len - 1);
	hdr[hdr_len - 1] = '\n';

	buf[0] = 0x93; buf[1] = 'N'; buf[2] = 'U'; buf[3] = 'M';
	buf[4] = 'P';  buf[5] = 'Y'; buf[6] = 1;   buf[7] = 0;
	buf[8] = (uint8_t)(hdr_len & 0xff);
	buf[9] = (uint8_t)((hdr_len >> 8) & 0xff);
	fwrite(buf, 1, 10, fp);
	fwrite(hdr, 1, (size_t)hdr_len, fp);
	return fp;
}

static void
write_npy_row(FILE *fp, const int8_t *in, int n)
{
	fwrite(in, 1, (size_t)n, fp);
}

static void
write_csv_row(FILE *fp, const int8_t *in, int n)
{
	int i;

	for (i = 0; i < n; i++) {
		if (i > 0) fputc(',', fp);
		fprintf(fp, "%d", (int)in[i]);
	}
	fputc('\n', fp);
}

static int
read_csv_row(FILE *fp, int8_t *out, int n)
{
	char line[8192];
	char *p;
	int i;

	if (fgets(line, sizeof line, fp) == NULL)
		return 0;
	p = line;
	for (i = 0; i < n; i++) {
		char *end;
		out[i] = (int8_t)strtol(p, &end, 10);
		p = end;
		if (*p == ',') p ++;
	}
	return 1;
}

/*
 * Compute F and G from f and g by solving the NTRU equation f*G - g*F = q.
 * tmp must be FALCON_TMPSIZE_KEYGEN(logn) bytes, malloc-aligned.
 * Returns 1 on success, 0 if the solver rejects the key pair.
 */
int
ntru_solve(unsigned logn, int8_t *F, int8_t *G,
	const int8_t *f, const int8_t *g, uint8_t *tmp)
{
	int lim;

	lim = (1 << (Zf(max_FG_bits)[logn] - 1)) - 1;
	return solve_NTRU(logn, F, G, f, g, lim, (uint32_t *)(void *)tmp);
}

static void
test_csv_keys(void)
{
	unsigned logn = FALCON_LOGN;
	int n = FALCON_N;
	int i;
	char path[64];
	FILE *fp_f, *fp_g, *fp_F, *fp_G, *fp_F_npy, *fp_G_npy;
	int8_t *f, *g, *F, *G;
	uint8_t *tmp;
	size_t tmp_len;

	printf("Test CSV keys: ");
	fflush(stdout);

	snprintf(path, sizeof path, "../keys/Falcon%d_f_1000.csv", FALCON_N);
	fp_f = fopen(path, "r");
	snprintf(path, sizeof path, "../keys/Falcon%d_g_1000.csv", FALCON_N);
	fp_g = fopen(path, "r");
	snprintf(path, sizeof path, "../keys/Falcon%d_F_1000.csv", FALCON_N);
	fp_F = fopen(path, "w");
	snprintf(path, sizeof path, "../keys/Falcon%d_G_1000.csv", FALCON_N);
	fp_G = fopen(path, "w");
	snprintf(path, sizeof path, "../keys/Falcon%d_F_1000.npy", FALCON_N);
	fp_F_npy = create_npy(path, 1000, n, "|i1");
	snprintf(path, sizeof path, "../keys/Falcon%d_G_1000.npy", FALCON_N);
	fp_G_npy = create_npy(path, 1000, n, "|i1");
	if (fp_f == NULL || fp_g == NULL || fp_F == NULL || fp_G == NULL
		|| fp_F_npy == NULL || fp_G_npy == NULL) {
		fprintf(stderr, "cannot open CSV key files\n");
		exit(EXIT_FAILURE);
	}

	f = xmalloc(n);
	g = xmalloc(n);
	F = xmalloc(n);
	G = xmalloc(n);
	tmp_len = FALCON_TMPSIZE_KEYGEN(logn);
	tmp = xmalloc(tmp_len);

	for (i = 0; i < 1000; i++) {
		if (!read_csv_row(fp_f, f, n) || !read_csv_row(fp_g, g, n)) {
			fprintf(stderr, "CSV read error at row %d\n", i);
			exit(EXIT_FAILURE);
		}
		if (!ntru_solve(logn, F, G, f, g, tmp)) {
			fprintf(stderr, "NTRU solve failed at row %d\n", i);
			exit(EXIT_FAILURE);
		}
		write_csv_row(fp_F, F, n);
		write_csv_row(fp_G, G, n);
		write_npy_row(fp_F_npy, F, n);
		write_npy_row(fp_G_npy, G, n);
		if (i % 100 == 99) {
			printf(".");
			fflush(stdout);
		}
	}

	fclose(fp_f);
	fclose(fp_g);
	fclose(fp_F);
	fclose(fp_G);
	fclose(fp_F_npy);
	fclose(fp_G_npy);
	xfree(f);
	xfree(g);
	xfree(F);
	xfree(G);
	xfree(tmp);
	printf(" done.\n");
	fflush(stdout);
}

static void
test_npy_keys(void)
{
	unsigned logn = FALCON_LOGN;
	int n = FALCON_N;
	int i;
	char path[64];
	FILE *fp_f, *fp_g;
	int8_t *f, *g, *F, *G;
	uint8_t *tmp;
	size_t tmp_len;

	printf("Test NPY keys: ");
	fflush(stdout);

	snprintf(path, sizeof path, "../keys/Falcon%d_f_1000.npy", FALCON_N);
	fp_f = open_npy(path);
	snprintf(path, sizeof path, "../keys/Falcon%d_g_1000.npy", FALCON_N);
	fp_g = open_npy(path);
	if (fp_f == NULL || fp_g == NULL) {
		fprintf(stderr, "cannot open NPY key files\n");
		exit(EXIT_FAILURE);
	}

	f = xmalloc(n);
	g = xmalloc(n);
	F = xmalloc(n);
	G = xmalloc(n);
	tmp_len = FALCON_TMPSIZE_KEYGEN(logn);
	tmp = xmalloc(tmp_len);

	for (i = 0; i < 1000; i++) {
		if (!read_npy_row(fp_f, f, n) || !read_npy_row(fp_g, g, n)) {
			fprintf(stderr, "NPY read error at row %d\n", i);
			exit(EXIT_FAILURE);
		}
		if (!ntru_solve(logn, F, G, f, g, tmp)) {
			fprintf(stderr, "NTRU solve failed at row %d\n", i);
			exit(EXIT_FAILURE);
		}
		if (i % 100 == 99) {
			printf(".");
			fflush(stdout);
		}
	}

	fclose(fp_f);
	fclose(fp_g);
	xfree(f);
	xfree(g);
	xfree(F);
	xfree(G);
	xfree(tmp);
	printf(" done.\n");
	fflush(stdout);
}

int
main(void)
{
	test_csv_keys();
	test_npy_keys();
	return 0;
}
