static void run(enum mode m, const char *label, size_t len,
                int huge_log2, size_t steps)
{
        unsigned long fb0, fb1;
        long anon_kb, page_kb;
        double best = 1e18;
        char *buf = take(m, len, huge_log2);

        if (buf == MAP_FAILED) {
                printf("%-13s пропущено: %s\n", label, strerror(errno));
                return;
        }

        fb0 = vmstat("thp_fault_fallback");
        build_cycle(buf, len / PAGE);           /* заразом населює ділянку */
        fb1 = vmstat("thp_fault_fallback");

        vma_pages(buf, &anon_kb, &page_kb);
        if (m == M_THP && anon_kb >= 0 &&
            (size_t)anon_kb * 1024 < len - len / 10) {
                /* дали менше дев'яти десятих — просимо згорнути решту негайно */
                if (madvise(buf, len, MADV_COLLAPSE) != 0)
                        perror("madvise(MADV_COLLAPSE)");
                vma_pages(buf, &anon_kb, &page_kb);
        }

        chase(buf, 2000000);                    /* прогрів */
        for (int r = 0; r < 3; r++) {
                double ns = chase(buf, steps);
                if (ns < best)
                        best = ns;
        }

        printf("%-13s %6.1f нс   AnonHugePages %9ld кБ з %zu   "
               "KernelPageSize %7ld кБ   thp_fault_fallback +%lu\n",
               label, best, anon_kb, len / 1024, page_kb, fb1 - fb0);
        munmap(buf, len);
}

int main(int argc, char **argv)
{
        const char *what = argc > 1 ? argv[1] : "all";
        size_t gib     = argc > 2 ? strtoul(argv[2], NULL, 10) : 16;
        size_t steps   = (argc > 3 ? strtoul(argv[3], NULL, 10) : 20) * 1000000;
        size_t len     = gib << 30;

        printf("буфер %zu ГіБ, %zu вузлів, %zu кроків у колі\n\n",
               gib, len / PAGE, steps);

        if (!strcmp(what, "small")   || !strcmp(what, "all"))
                run(M_SMALL,   "4KiB",         len,  0, steps);
        if (!strcmp(what, "thp")     || !strcmp(what, "all"))
                run(M_THP,     "THP-2MiB",     len,  0, steps);
        if (!strcmp(what, "hugetlb") || !strcmp(what, "all"))
                run(M_HUGETLB, "HUGETLB-2MiB", len, 21, steps);
        if (!strcmp(what, "hugetlb1g"))
                run(M_HUGETLB, "HUGETLB-1GiB", len, 30, steps);
        return 0;
}
