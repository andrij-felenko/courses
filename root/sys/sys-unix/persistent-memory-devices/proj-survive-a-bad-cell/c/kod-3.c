int main(int argc, char **argv)
{
    char bb[192], *map, *buf;
    unsigned long long part = 0;
    struct stat st;
    off_t off, bad_off, aligned;
    size_t gran, win = 4096;
    long long good = 0, healed = 0, lost = 0;
    int fd, rc = 0;

    if (argc != 2) { fprintf(stderr, "вжиток: %s файл\n", argv[0]); return 2; }
    if (arm_sigbus() < 0) { perror("sigaction"); return 1; }

    fd = open(argv[1], O_RDWR);
    if (fd < 0) { perror(argv[1]); return 1; }
    if (fstat(fd, &st) < 0) { perror("fstat"); return 1; }
    if (find_device(fd, bb, sizeof bb, &part) < 0) { perror("sysfs"); return 1; }

    map = mmap(NULL, (size_t)st.st_size, PROT_READ, MAP_SHARED, fd, 0);
    if (map == MAP_FAILED) { perror("mmap"); return 1; }
    buf = malloc(win);
    if (!buf) { fprintf(stderr, "бракує пам'яті\n"); return 1; }

    for (off = 0; off < st.st_size; off += (off_t)win) {
        size_t n = win;
        if ((off_t)n > st.st_size - off) n = (size_t)(st.st_size - off);

        if (pm_copy(buf, map + off, n) == 0) { good += (long long)n; continue; }

        /* Сюди керування приходить лише стрибком з обробника. */
        bad_off = (off_t)((char *)f_addr - map);
        gran    = (size_t)1 << f_lsb;
        aligned = bad_off & ~(off_t)(gran - 1);

        fprintf(stderr, "збій: адреса %p, зсув у файлі %lld, ділянка %zu Б, %s\n",
                f_addr, (long long)bad_off, gran,
                f_code == BUS_MCEERR_AR ? "BUS_MCEERR_AR (спожито)" :
                f_code == BUS_MCEERR_AO ? "BUS_MCEERR_AO (виявлено фоном)" :
                                          "BUS_ADRERR (ядро до 6.5 або інша причина)");

        uint64_t phys;
        if (file_off_to_phys(fd, aligned, &phys) == 0) {
            unsigned long long sec = phys / 512 + part, s0, len;
            int hit = in_badblocks(bb, sec, &s0, &len);
            fprintf(stderr, "  сектор пристрою %llu — %s\n", sec,
                    hit == 1 ? "у списку badblocks" :
                    hit == 0 ? "у списку немає (свіжа помилка чи інший носій)"
                             : "список недоступний");
            if (hit == 1)
                fprintf(stderr, "  запис списку: %llu %llu\n", s0, len);
        }

        if (repair(fd, aligned, gran) < 0) {
            perror("  розчищення"); rc = 1;
        } else if (pm_copy(buf, map + off, n) == 0) {
            healed++; lost += (long long)gran;
        } else {
            fprintf(stderr, "  ділянка не піддалася\n"); rc = 1;
        }
    }

    printf("прочитано без збоїв %lld Б\n", good);
    printf("розчищено ділянок   %lld (втрачено %lld Б — брати з копії)\n",
           healed, lost);
    free(buf);
    munmap(map, (size_t)st.st_size);
    close(fd);
    return rc;
}
