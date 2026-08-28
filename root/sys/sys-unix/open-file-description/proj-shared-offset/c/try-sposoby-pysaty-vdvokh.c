static void case_append(void)
{
    int a = fresh(O_APPEND);
    int b = open(PROBE, O_WRONLY | O_APPEND);
    write(a, "AAAAA", 5);
    write(b, "BBBBB", 5);
    witness("open + open, O_APPEND", getpid(), a, getpid(), b);
    close(a); close(b);
}

static void case_pwrite(void)
{
    int a = fresh(0);
    int b = open(PROBE, O_WRONLY);
    pwrite(a, "AAAAA", 5, 0);
    pwrite(b, "BBBBB", 5, 5);       /* зсув — аргумент, позиція не рухається */
    witness("open + open, pwrite", getpid(), a, getpid(), b);
    close(a); close(b);
}

static void case_pwrite_append(void)          /* пастка, специфічна для Linux */
{
    int a = fresh(O_APPEND);
    pwrite(a, "AAAAA", 5, 0);
    pwrite(a, "BBBBB", 5, 0);       /* обидва рази зсув 0 */
    long long pos = -1; unsigned fl = 0;
    fdinfo(getpid(), a, &pos, &fl);
    printf("  %-22s pos %lld  flags %o  (POSIX дав би 5 Б «BBBBB»)\n",
           "pwrite + O_APPEND", pos, fl);
    on_disk();
    close(a);
}
