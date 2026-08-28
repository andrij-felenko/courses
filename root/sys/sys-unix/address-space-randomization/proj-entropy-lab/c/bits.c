/* bits.c — читає зі stdin рядки «ім'я=0xадреса …» і оцінює, скільки
 * двійкових розрядів насправді рухається в кожного орієнтира.
 *
 *   cc -O2 -Wall -Wextra -o bits bits.c -lm
 *   ./bits < plain.txt
 */
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAXCOL 16
#define MAXROW 50000

static char               name[MAXCOL][32];
static unsigned long long val[MAXCOL][MAXROW];
static int                ncol, nrow;

static int column(const char *n)
{
	for (int i = 0; i < ncol; i++)
		if (strcmp(name[i], n) == 0)
			return i;
	if (ncol == MAXCOL)
		return -1;
	snprintf(name[ncol], sizeof name[0], "%s", n);
	return ncol++;
}

static unsigned long long gcd(unsigned long long a, unsigned long long b)
{
	while (b != 0) {
		unsigned long long t = a % b;
		a = b;
		b = t;
	}
	return a;
}

static int cmp(const void *a, const void *b)
{
	unsigned long long x = *(const unsigned long long *) a;
	unsigned long long y = *(const unsigned long long *) b;
	return (x > y) - (x < y);
}

int main(void)
{
	static char line[4096], key[32];
	static unsigned long long tmp[MAXROW];

	while (nrow < MAXROW && fgets(line, sizeof line, stdin) != NULL) {
		char *tok = strtok(line, " \t\n");
		int got = 0;
		while (tok != NULL) {
			unsigned long long v;
			if (sscanf(tok, "%31[^=]=%llx", key, &v) == 2) {
				int c = column(key);
				if (c >= 0) {
					val[c][nrow] = v;
					got = 1;
				}
			}
			tok = strtok(NULL, " \t\n");
		}
		if (got)
			nrow++;
	}
	if (nrow < 2) {
		fprintf(stderr, "потрібно щонайменше два прогони\n");
		return 1;
	}

	printf("прогонів: %d\n", nrow);
	/* Заголовок окремим рядком, без вирівнювання по стовпчиках: ширина в
	   printf рахується в байтах, а кириличні підписи довші за свій вигляд,
	   і таблиця з ними поїхала б. */
	printf("стовпчики: орієнтир · різних значень · крок · рухомих розрядів ·"
	       " маска рухомих · ΣH(p) · оцінка за розмахом\n\n");

	for (int c = 0; c < ncol; c++) {
		unsigned long long *v = val[c];
		unsigned long long lo = v[0], hi = v[0], step = 0, mask = 0;
		long ones[64] = { 0 };

		for (int r = 0; r < nrow; r++) {
			if (v[r] < lo) lo = v[r];
			if (v[r] > hi) hi = v[r];
			for (int b = 0; b < 64; b++)
				if ((v[r] >> b) & 1ULL)
					ones[b]++;
		}
		for (int r = 0; r < nrow; r++)
			step = gcd(step, v[r] - lo);

		memcpy(tmp, v, (size_t) nrow * sizeof tmp[0]);
		qsort(tmp, (size_t) nrow, sizeof tmp[0], cmp);
		int distinct = 1;
		for (int r = 1; r < nrow; r++)
			if (tmp[r] != tmp[r - 1])
				distinct++;

		double hsum = 0.0;
		int moving = 0;
		for (int b = 0; b < 64; b++) {
			if (ones[b] == 0 || ones[b] == nrow)
				continue;            /* розряд стоїть — нуль ентропії */
			moving++;
			mask |= 1ULL << b;
			double p = (double) ones[b] / nrow;
			hsum += -(p * log2(p) + (1.0 - p) * log2(1.0 - p));
		}

		double span = 0.0;
		if (step != 0) {
			double slots = (double) ((hi - lo) / step) + 1.0;
			slots *= (double) (nrow + 1) / (double) (nrow - 1);
			span = log2(slots);
		}

		printf("%-9s %8d %7llu %7d 0x%016llx %10.1f %10.1f\n",
		       name[c], distinct, step, moving, mask, hsum, span);
	}

	printf("\nвідстані між орієнтирами\n");
	for (int i = 0; i < ncol; i++)
		for (int j = i + 1; j < ncol; j++) {
			long long dlo = (long long) (val[i][0] - val[j][0]), dhi = dlo;
			for (int r = 1; r < nrow; r++) {
				long long d = (long long) (val[i][r] - val[j][r]);
				if (d < dlo) dlo = d;
				if (d > dhi) dhi = d;
			}
			if (dlo == dhi)
				printf("  %-8s − %-8s   СТАЛА  %s0x%llx\n",
				       name[i], name[j], dlo < 0 ? "−" : "",
				       (unsigned long long) (dlo < 0 ? -dlo : dlo));
			else
				printf("  %-8s − %-8s   рухома, розкид 0x%llx\n",
				       name[i], name[j], (unsigned long long) (dhi - dlo));
		}
	return 0;
}
