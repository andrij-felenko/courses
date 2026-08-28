static void witness(const char *what, pid_t pa, int a, pid_t pb, int b)
{
    long long apos = -1, bpos = -1;
    unsigned af = 0, bf = 0;
    fdinfo(pa, a, &apos, &af);
    fdinfo(pb, b, &bpos, &bf);
    int same = same_ofd(pa, a, pb, b);
    printf("  %-22s pos %2lld/%-3lld flags %o/%o  kcmp: %s\n",
           what, apos, bpos, af, bf,
           same == 1 ? "ОДИН опис" :
           same == 0 ? "ДВА описи" : "немає вердикту");
    on_disk();
}

static int fresh(int extra)   /* порожній файл і перший дескриптор до нього */
{
    int fd = open(PROBE, O_WRONLY | O_CREAT | O_TRUNC | extra, 0644);
    if (fd < 0) { perror("open " PROBE); exit(1); }
    return fd;
}
