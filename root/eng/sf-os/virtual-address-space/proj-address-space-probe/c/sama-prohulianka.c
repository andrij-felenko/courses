int main(void)
{
    PAGE = (unsigned long) sysconf(_SC_PAGESIZE);
    const unsigned long LEN = 1024 * MIB;

    struct sigaction sa;
    memset(&sa, 0, sizeof sa);
    sa.sa_sigaction = on_segv;
    sa.sa_flags = SA_SIGINFO;        /* хочемо siginfo_t, а не самий номер */
    sigemptyset(&sa.sa_mask);
    sigaction(SIGSEGV, &sa, NULL);

    show("старт");

    char *p = mmap(NULL, LEN, PROT_READ | PROT_WRITE,
                   MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (p == MAP_FAILED) { perror("mmap"); return 1; }
    show("mmap 1 ГіБ");

    volatile unsigned long acc = 0;
    for (unsigned long i = 0; i < 256 * MIB; i += PAGE) acc += p[i];
    show("прочитано 65536 сторінок");

    for (unsigned long i = 0; i < 256 * MIB; i += PAGE) p[i] = 0x5a;
    show("записано в 65536 сторінок");

    memset(p + 300 * MIB, 0x5a, 1000);          /* 1000 байтів ПОСПІЛЬ */
    show("записано 1000 байтів поспіль");

    char *hole = p + 64 * MIB;
    maps("до mprotect", p, p + LEN);
    mprotect(hole, 64 * MIB, PROT_NONE);
    show("mprotect PROT_NONE на 64 МіБ");
    maps("після mprotect", p, p + LEN);
    probe(hole + 8);

    madvise(p, 64 * MIB, MADV_DONTNEED);
    show("madvise MADV_DONTNEED на 64 МіБ");
    printf("  p[0] = %d (записували 0x5a)\n", p[0]);
    show("після читання з відданої частини");

    munmap(hole, 64 * MIB);
    show("munmap 64 МіБ");
    maps("після munmap", p, p + LEN);
    probe(hole + 8);                            /* та сама адреса — інша причина */

    p[0] = 1;
    p[900 * MIB] = 1;
    show("торкнулися решти ділянки");

    mprotect(p + 700 * MIB, PAGE, PROT_NONE);
    repair = 1;
    p[700 * MIB] = 7;               /* впаде, полагодиться й виконається знову */
    printf("  p[700 МіБ] = %d\n", p[700 * MIB]);

    munmap(p, LEN);                 /* решта — одним махом, разом із дірою */
    show("munmap решти");
    return 0;
}
