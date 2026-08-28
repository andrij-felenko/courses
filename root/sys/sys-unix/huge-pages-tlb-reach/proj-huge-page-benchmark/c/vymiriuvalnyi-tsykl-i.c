static void *volatile sink;

static double chase(char *buf, size_t steps)
{
        uintptr_t p = (uintptr_t)(buf + node_off(0));
        struct timespec a, b;

        clock_gettime(CLOCK_MONOTONIC, &a);
        for (size_t i = 0; i < steps; i++)
                p = *(uintptr_t *)p;
        clock_gettime(CLOCK_MONOTONIC, &b);

        sink = (void *)p;               /* без цього рядка циклу не буде */
        return ((b.tv_sec - a.tv_sec) * 1e9 + (b.tv_nsec - a.tv_nsec))
               / (double)steps;
}
