int durable = 1;
void *p = mmap(NULL, len, PROT_READ | PROT_WRITE,
               MAP_SHARED_VALIDATE | MAP_SYNC, fd, 0);
if (p == MAP_FAILED && (errno == EOPNOTSUPP || errno == EINVAL)) {
    /* EOPNOTSUPP — файлова система без DAX або ядро не знає MAP_SYNC;
       EINVAL     — ядро старіше за 4.15: значення 3 у полі типу для нього
                    просто «і SHARED, і PRIVATE», тобто нісенітниця.       */
    p = mmap(NULL, len, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
    durable = 0;                    /* тепер довговічність — тільки через msync */
}
