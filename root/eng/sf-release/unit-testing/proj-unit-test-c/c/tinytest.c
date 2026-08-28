/* tinytest.c */
#include "tinytest.h"
#include <stdlib.h>

#if defined(_WIN32)
#  include <windows.h>
static double now_us(void) {
    static LARGE_INTEGER f;
    LARGE_INTEGER t;
    if (f.QuadPart == 0) QueryPerformanceFrequency(&f);
    QueryPerformanceCounter(&t);
    return (double)t.QuadPart * 1e6 / (double)f.QuadPart;
}
#else
#  include <time.h>
static double now_us(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (double)ts.tv_sec * 1e6 + (double)ts.tv_nsec / 1e3;
}
#endif

jmp_buf     tt_abort;
const char *tt_file;
int         tt_line;
char        tt_msg[192];

_Noreturn void tt_fail(const char *file, int line) {
    tt_file = file;
    tt_line = line;
    longjmp(tt_abort, 1);
}

/* Власний генератор, а не rand(): те саме зерно мусить давати той самий
   порядок на будь-якій машині, інакше «відтвори падіння» не працює. */
static uint32_t rnd(uint32_t *s) {
    uint32_t x = *s;
    x ^= x << 13;
    x ^= x >> 17;
    x ^= x << 5;
    return *s = x;
}

/* Єдине місце з setjmp — і воно навмисно крихітне: тут немає жодної
   локальної змінної, яка міняється між стрибком і поверненням, тож
   питання «чи вціліло її значення» просто не виникає. */
static int run_one(const tt_case *c, double *us) {
    double t0 = now_us();
    int    bad;
    if (setjmp(tt_abort) == 0) { c->body(); bad = 0; }
    else                       {            bad = 1; }
    *us = now_us() - t0;
    return bad;
}

/* printf рахує байти, а не літери: кирилична літера — два байти, тож
   "%-44s" пустив би стовпчики врозтіч. Рахуємо початки літер самі. */
static void print_padded(const char *s, int width) {
    const unsigned char *p = (const unsigned char *)s;
    int chars = 0;
    fputs(s, stdout);
    for (; *p; p++)
        if ((*p & 0xC0) != 0x80) chars++;
    for (; chars < width; chars++) putchar(' ');
}

int tt_run(const tt_case *cases, size_t n, uint32_t seed) {
    size_t *order = malloc(n * sizeof *order);
    size_t  i, k, failed = 0;
    double  total = 0.0;

    if (order == NULL) return 2;
    for (i = 0; i < n; i++) order[i] = i;

    if (seed != 0) {                          /* перемішування Фішера — Єйтса */
        uint32_t s = seed;
        for (i = n; i > 1; i--) {
            size_t j = (size_t)(rnd(&s) % (uint32_t)i);
            size_t t = order[i - 1];
            order[i - 1] = order[j];
            order[j] = t;
        }
    }

    for (k = 0; k < n; k++) {
        const tt_case *c = &cases[order[k]];
        double us;
        int    bad = run_one(c, &us);

        fputs(bad ? "[FAIL] " : "[ OK ] ", stdout);
        print_padded(c->promise, 44);
        printf("%7.1f мкс\n", us);
        if (bad) {
            printf("        %s:%d: %s\n", tt_file, tt_line, tt_msg);
            failed++;
        }
        total += us;
    }

    printf("\n%zu тестів, %zu провалів, %.1f мкс усього, %.2f мкс на тест\n",
           n, failed, total, total / (double)n);
    free(order);
    return failed != 0;                       /* код виходу побачить складач */
}
