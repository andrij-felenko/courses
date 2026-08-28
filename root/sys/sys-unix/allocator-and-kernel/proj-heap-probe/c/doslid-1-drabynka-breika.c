static void probe_ladder(void)
{
    static const size_t sizes[7] = { 32, 102400, 102400, 102400, 102400, 102400, 102400 };
    void *keep[7];
    void *prev = brk_now();
    int i;

    printf("[1] драбинка брейка\n");
    printf("      старт: брейк = %p\n", prev);

    for (i = 0; i < 7; i++) {
        void *b;
        keep[i] = xmalloc(sizes[i]);
        memset(keep[i], 0, sizes[i]);
        b = brk_now();
        printf("      malloc(%6zu) = %p   брейк = %p  %+5ld КіБ\n",
               sizes[i], keep[i], b, ((char *) b - (char *) prev) / (long) KiB);
        prev = b;
    }
    for (i = 0; i < 7; i++)
        free(keep[i]);
    printf("      після free() усіх сімох: брейк = %p\n", brk_now());
}
