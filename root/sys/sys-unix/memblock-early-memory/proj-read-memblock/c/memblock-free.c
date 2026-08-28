/* memblock-free.c — повторити розрахунок, який ядро зробило до першої сторінки.
   Читає знімок memblock у debugfs, зливає діапазони, віднімає зайняте,
   друкує вільні вікна й зводить підсумок із /proc/meminfo та журналом ядра.

   Збірка: cc -O2 -std=gnu11 -Wall -o memblock-free memblock-free.c
   Запуск: sudo ./memblock-free [--min РОЗМІР] [--iomem]  */

#define _GNU_SOURCE
#include <ctype.h>
#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAXR 4096

struct rng { uint64_t base, size; };          /* межа напіввідкрита: [base, base+size) */

static struct rng mem[MAXR], res[MAXR];
static int nmem, nres;
static uint64_t nomap_total, g_min;
static int w_count;
static uint64_t w_total, w_biggest;

static const char *human(uint64_t b)
{
	static char buf[4][32];
	static unsigned k;
	char *s = buf[k++ & 3];                   /* чотири комірки: два виклики в одному printf */

	if (b >= 1ULL << 30)      snprintf(s, 32, "%.2f ГіБ", b / (double)(1ULL << 30));
	else if (b >= 1ULL << 20) snprintf(s, 32, "%.2f МіБ", b / (double)(1ULL << 20));
	else                      snprintf(s, 32, "%.2f КіБ", b / 1024.0);
	return s;
}

/* найбільша степінь двійки, на яку ділиться адреса */
static uint64_t align_of(uint64_t base) { return base & (~base + 1); }

static void push(struct rng *v, int *n, uint64_t base, uint64_t size)
{
	if (!size) return;
	if (*n == MAXR) { fprintf(stderr, "діапазонів більше за %d\n", MAXR); exit(1); }
	v[*n].base = base;
	v[*n].size = size;
	(*n)++;
}

static int by_base(const void *A, const void *B)
{
	const struct rng *a = A, *b = B;
	return (a->base > b->base) - (a->base < b->base);
}

/* упорядкувати й зшити все, що перетинається або стикається */
static int merge(struct rng *v, int n)
{
	int i, k = 0;

	if (n < 1) return 0;
	qsort(v, n, sizeof *v, by_base);
	for (i = 1; i < n; i++) {
		uint64_t kend = v[k].base + v[k].size;
		uint64_t iend = v[i].base + v[i].size;

		if (v[i].base <= kend) {
			if (iend > kend) v[k].size = iend - v[k].base;
		} else {
			v[++k] = v[i];
		}
	}
	return k + 1;
}

/* «   3: 0x0000000040000000..0x00000000dfffffff    0 NONE»
   друге число — адреса ОСТАННЬОГО БАЙТА, а не межа;
   вузол і прапорець друкують не всі ядра, тож хвіст читаємо необов'язково */
static int read_memblock(const char *path, struct rng *v, int *n, int catch_nomap)
{
	char ln[256], node[16], flag[16];
	FILE *f = fopen(path, "r");

	if (!f) return 0;
	while (fgets(ln, sizeof ln, f)) {
		uint64_t a, b;
		int used = 0;
		char *p = strchr(ln, ':');

		if (!p) continue;
		if (sscanf(p + 1, " %" SCNx64 " .. %" SCNx64 "%n", &a, &b, &used) != 2 || b < a)
			continue;
		push(v, n, a, b - a + 1);
		if (catch_nomap && sscanf(p + 1 + used, " %15s %15s", node, flag) == 2 &&
		    !strcmp(flag, "NOMAP")) {
			nomap_total += b - a + 1;
			push(res, &nres, a, b - a + 1);   /* NOMAP ядро теж нікому не роздає */
		}
	}
	fclose(f);
	return *n > 0;
}

/* «00001000-0009ffff : System RAM» — верхній рівень; вкладені йдуть з відступом.
   Тут адреса останнього байта теж включна. Без CAP_SYS_ADMIN усі числа — нулі. */
static int read_iomem(void)
{
	char ln[256];
	FILE *f = fopen("/proc/iomem", "r");
	uint64_t sum = 0;
	int in_ram = 0;

	if (!f) return 0;
	while (fgets(ln, sizeof ln, f)) {
		uint64_t a, b;
		int used = 0, depth = 0;
		char *p = ln, *name;

		while (*p == ' ') { p++; depth++; }
		if (sscanf(p, "%" SCNx64 "-%" SCNx64 " :%n", &a, &b, &used) != 2 || b < a)
			continue;
		name = p + used;
		while (*name == ' ') name++;
		name[strcspn(name, "\n")] = '\0';

		if (!depth) {
			in_ram = !strcmp(name, "System RAM");
			if (in_ram) { push(mem, &nmem, a, b - a + 1); sum += b - a + 1; }
		} else if (in_ram) {
			push(res, &nres, a, b - a + 1);
		}
	}
	fclose(f);
	if (nmem && sum <= (uint64_t)nmem) {
		fprintf(stderr, "у /proc/iomem самі нулі — потрібен root\n");
		exit(1);
	}
	return nmem > 0;
}

static uint64_t meminfo(const char *key)      /* байтів, 0 якщо поля немає */
{
	char ln[256];
	FILE *f = fopen("/proc/meminfo", "r");
	size_t klen = strlen(key);
	uint64_t v = 0;

	if (!f) return 0;
	while (fgets(ln, sizeof ln, f))
		if (!strncmp(ln, key, klen) && ln[klen] == ':') {
			v = strtoull(ln + klen + 1, NULL, 10) * 1024;
			break;
		}
	fclose(f);
	return v;
}

/* «Memory: 15925248K/16711680K available (… 524288K reserved, 262144K cma-reserved)» */
static int kernel_memory_line(uint64_t *phys, uint64_t *reserved)
{
	char ln[1024];
	FILE *f = popen("dmesg 2>/dev/null", "r");
	int got = 0;

	if (!f) return 0;
	while (fgets(ln, sizeof ln, f)) {
		unsigned long long freek, physk;
		char *p = strstr(ln, "Memory: "), *q;

		if (!p || sscanf(p, "Memory: %lluK/%lluK available", &freek, &physk) != 2)
			continue;
		*phys = (uint64_t)physk * 1024;
		*reserved = 0;
		q = strstr(p, "K reserved");
		if (q) {                              /* відступаємо назад по цифрах */
			char *s = q;
			while (s > p && isdigit((unsigned char)s[-1])) s--;
			*reserved = strtoull(s, NULL, 10) * 1024;
		}
		got = 1;
	}
	pclose(f);
	return got;
}

static void window(uint64_t base, uint64_t size)
{
	w_count++;
	w_total += size;
	if (size > w_biggest) w_biggest = size;
	if (size < g_min) return;
	printf("  0x%012" PRIx64 "..0x%012" PRIx64 "  %14s  вирівняно на %s\n",
	       base, base + size - 1, human(size),
	       base ? human(align_of(base)) : "будь-що");
}

/* усі одиниці («КіБ», «МіБ», «ГіБ») однакової довжини в байтах,
   тому %14s вирівнює стовпчик і для UTF-8 */
static void show(const char *label, int64_t v)
{
	char val[40];

	snprintf(val, sizeof val, "%s%s", v < 0 ? "-" : "",
		 human((uint64_t)(v < 0 ? -v : v)));
	printf("  %s%14s\n", label, val);
}

int main(int argc, char **argv)
{
	uint64_t memsum = 0, ressum = 0, phys = 0, dres = 0, memtotal, cmatotal;
	int i, j = 0, iomem = 0;

	for (i = 1; i < argc; i++) {
		if (!strcmp(argv[i], "--iomem")) {
			iomem = 1;
		} else if (!strcmp(argv[i], "--min") && i + 1 < argc) {
			char *e;
			g_min = strtoull(argv[++i], &e, 0);
			if (*e == 'K' || *e == 'k') g_min <<= 10;
			else if (*e == 'M' || *e == 'm') g_min <<= 20;
			else if (*e == 'G' || *e == 'g') g_min <<= 30;
		} else {
			fprintf(stderr, "вжиток: %s [--min РОЗМІР] [--iomem]\n", argv[0]);
			return 2;
		}
	}

	if (!iomem &&
	    !(read_memblock("/sys/kernel/debug/memblock/memory", mem, &nmem, 1) &&
	      read_memblock("/sys/kernel/debug/memblock/reserved", res, &nres, 0))) {
		fprintf(stderr, "знімка memblock немає (потрібні root, змонтований debugfs "
				"і ядро з CONFIG_ARCH_KEEP_MEMBLOCK) — беру /proc/iomem\n");
		nmem = nres = 0;
		nomap_total = 0;
		iomem = 1;
	}
	if (iomem && !read_iomem()) { perror("/proc/iomem"); return 1; }

	nmem = merge(mem, nmem);
	nres = merge(res, nres);
	for (i = 0; i < nmem; i++) memsum += mem[i].size;
	for (i = 0; i < nres; i++) ressum += res[i].size;

	printf("джерело         : %s\n", iomem ? "/proc/iomem (наближено)"
					       : "/sys/kernel/debug/memblock");
	printf("наявна пам'ять  : %2d діап.  %14s\n", nmem, human(memsum));
	printf("зайнято         : %2d діап.  %14s", nres, human(ressum));
	if (nomap_total) printf("  (з них NOMAP %s)", human(nomap_total));
	printf("\n\nвільні вікна:\n");

	for (i = 0; i < nmem; i++) {              /* різниця двома покажчиками */
		uint64_t cur = mem[i].base, end = mem[i].base + mem[i].size;
		int k;

		while (j < nres && res[j].base + res[j].size <= cur)
			j++;                              /* зайняте лишилося позаду */
		for (k = j; k < nres && res[k].base < end && cur < end; k++) {
			uint64_t rend = res[k].base + res[k].size;

			if (res[k].base > cur)
				window(cur, res[k].base - cur);
			if (rend > cur) cur = rend;
		}
		if (cur < end) window(cur, end - cur);
	}

	memtotal = meminfo("MemTotal");
	cmatotal = meminfo("CmaTotal");
	printf("\nразом вільного  : %2d вікон  %14s   (найбільше %s)\n",
	       w_count, human(w_total), human(w_biggest));
	printf("MemTotal        :           %14s\n", human(memtotal));
	printf("CmaTotal        :           %14s\n", human(cmatotal));

	if (iomem) return 0;                      /* далі звіряти нема чого */

	printf("\nзвірка:\n");
	show("Σ memory − NOMAP           ", (int64_t)(memsum - nomap_total));
	show("Σ reserved − NOMAP − CMA   ", (int64_t)ressum - (int64_t)nomap_total
					   - (int64_t)cmatotal);
	if (kernel_memory_line(&phys, &dres)) {
		show("те саме з журналу ядра     ", (int64_t)phys);
		show("  і його ж «K reserved»    ", (int64_t)dres);
	} else {
		printf("  рядка «Memory: … available» у журналі немає — кільце перекрутилося\n");
	}
	show("MemTotal − вільне − CMA    ", (int64_t)memtotal - (int64_t)w_total
					  - (int64_t)cmatotal);
	return 0;
}
