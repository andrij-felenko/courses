/* позиція й прапорці опису з погляду дескриптора fd процесу pid */
static int fdinfo(pid_t pid, int fd, long long *pos, unsigned *flags)
{
    char name[64], buf[512];
    snprintf(name, sizeof name, "/proc/%d/fdinfo/%d", (int)pid, fd);
    int f = open(name, O_RDONLY);
    if (f < 0) return -1;
    ssize_t n = read(f, buf, sizeof buf - 1);
    close(f);
    if (n <= 0) return -1;
    buf[n] = '\0';
    return sscanf(buf, "pos: %lld flags: %o", pos, flags) == 2 ? 0 : -1;
}

/* вердикт ядра: 1 — той самий опис, 0 — різні, -1 — вердикту немає.
   glibc обгортки для kcmp не має, тому йдемо через syscall() */
static int same_ofd(pid_t p1, int fd1, pid_t p2, int fd2)
{
    long r = syscall(SYS_kcmp, p1, p2, KCMP_FILE,
                     (unsigned long)fd1, (unsigned long)fd2);
    if (r < 0) return -1;
    return r == 0;
}

/* що з усього цього вийшло на диску */
static void on_disk(void)
{
    char buf[64] = "";
    struct stat st;
    st.st_size = 0;
    int fd = open(PROBE, O_RDONLY);
    if (fd >= 0) {
        fstat(fd, &st);
        ssize_t n = read(fd, buf, sizeof buf - 1);
        if (n > 0) buf[n] = '\0';
        close(fd);
    }
    printf("    файл: %lld Б, «%s»\n", (long long)st.st_size, buf);
}
