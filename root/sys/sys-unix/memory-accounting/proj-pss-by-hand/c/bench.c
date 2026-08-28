/* bench.c — ціна одного open+read+close. cc -O2 -o bench bench.c */
struct timespec t0, t1;
clock_gettime(CLOCK_MONOTONIC, &t0);
for (long i = 0; i < n; i++) {
    int fd = open(path, O_RDONLY);
    while (read(fd, buf, cap) > 0) { }      /* дочитуємо до кінця */
    close(fd);
}
clock_gettime(CLOCK_MONOTONIC, &t1);
printf("%.1f мкс\n", ((t1.tv_sec - t0.tv_sec) * 1e9 +
                      (t1.tv_nsec - t0.tv_nsec)) / n / 1e3);
