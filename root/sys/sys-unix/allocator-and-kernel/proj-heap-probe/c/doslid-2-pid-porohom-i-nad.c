static void probe_two_doors(void)
{
    void *small, *big, *b;

    printf("[2] під порогом і над порогом\n");
    small = xmalloc(64 * KiB);
    big   = xmalloc(1 * MiB);
    memset(small, 0, 64 * KiB);
    memset(big, 0, 1 * MiB);
    b = brk_now();

    printf("      64 КіБ → %p   (брейк = %p)\n", small, b);
    show_map_of(small);
    printf("      1 МіБ  → %p   вище за брейк на %ld ГіБ\n",
           big, ((char *) big - (char *) b) / (long) (1024 * MiB));
    show_map_of(big);

    free(small);
    free(big);
}
