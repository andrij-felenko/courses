/* потребує #include <time.h> */
static void bench(unsigned n)
{
    struct timespec a, b;
    volatile unsigned i;      /* volatile — бо міняється між sigsetjmp і siglongjmp */

    clock_gettime(CLOCK_MONOTONIC, &a);
    for (i = 0; i < n; i++)
        if (sigsetjmp(resume, 1) == 0)
            __asm__ volatile ("hlt");
    clock_gettime(CLOCK_MONOTONIC, &b);

    printf("одна відмова ≈ %.0f нс\n",
           ((double)(b.tv_sec - a.tv_sec) * 1e9 + (b.tv_nsec - a.tv_nsec)) / n);
}
