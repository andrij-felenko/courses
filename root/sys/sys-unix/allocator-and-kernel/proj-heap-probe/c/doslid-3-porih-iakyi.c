static void probe_moving_threshold(void)
{
    int i;

    printf("[3] поріг, який навчається\n");
    for (i = 0; i < 4; i++) {
        void *b0 = brk_now();
        void *p = xmalloc(200 * KiB);
        void *b1;

        memset(p, 0, 200 * KiB);
        b1 = brk_now();
        printf("      ітерація %d: %p   брейк %+5ld КіБ   %s\n",
               i, p, ((char *) b1 - (char *) b0) / (long) KiB,
               (char *) p < (char *) b1 ? "з купи" : "окремий mmap");
        free(p);
    }
}
