enum mode { M_SMALL, M_THP, M_HUGETLB };

static char *take(enum mode m, size_t len, int huge_log2)
{
        char *p;

        switch (m) {
        case M_SMALL:
                p = mmap(NULL, len, PROT_READ | PROT_WRITE,
                         MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
                if (p != MAP_FAILED)
                        madvise(p, len, MADV_NOHUGEPAGE);   /* інакше не контроль */
                return p;

        case M_THP:
                p = mmap_aligned(len, HUGE);
                if (p == MAP_FAILED)
                        return p;
                /* ПОРАДА МУСИТЬ ЛЯГТИ ДО ПЕРШОГО ДОТИКУ: після нього
                   сторінки вже дрібні, і лишається тільки згортання. */
                if (madvise(p, len, MADV_HUGEPAGE) != 0) {
                        perror("madvise(MADV_HUGEPAGE)");
                        munmap(p, len);
                        return MAP_FAILED;
                }
                return p;

        case M_HUGETLB:
                /* ENOMEM тут означає порожній пул, а не брак пам'яті. */
                return mmap(NULL, len, PROT_READ | PROT_WRITE,
                            MAP_PRIVATE | MAP_ANONYMOUS | MAP_HUGETLB |
                            (huge_log2 << MAP_HUGE_SHIFT), -1, 0);
        }
        return MAP_FAILED;
}
