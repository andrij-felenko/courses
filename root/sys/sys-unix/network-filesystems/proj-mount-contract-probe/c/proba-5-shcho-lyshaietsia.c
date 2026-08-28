static void probe_open_unlink(void)
{
    char aname[64], bname[64], apath[PATH_MAX];
    long n;

    snprintf(aname, sizeof aname, "del-a-%ld", (long) getpid());
    snprintf(bname, sizeof bname, "del-b-%ld", (long) getpid());
    snprintf(apath, sizeof apath, "%s/%s", share, aname);

    /* (а) тримає ЧУЖА машина, ім'я знімаємо МИ */
    if (rpc("OPEN 0 rw %s", aname) < 0) { puts("5. створити не вдалося"); return; }
    rpc("WRITE 0 4096");
    rpc("FSYNC 0");
    if (unlink(apath) < 0) perror("5a. unlink");

    n = rpc("PREAD 0 0 16");
    printf("5a. чужий дескриптор після нашого unlink: %s\n",
           n >= 0        ? "читається далі — сервер утримав відкритий файл" :
           n == -ESTALE  ? "ESTALE — об'єкт зник просто під дескриптором"
                         : "інша помилка читання");
    rpc("CLOSE 0");

    /* (б) та сама машина і тримає, і знімає ім'я */
    if (rpc("OPEN 1 rw %s", bname) < 0) return;
    rpc("WRITE 1 4096");
    rpc("UNLINK %s", bname);
    printf("5b. з боку письменника імен «.nfs» у каталозі: %ld\n", rpc("COUNT .nfs"));

    if (dir_ttl > 0) nap_ms((long) (dir_ttl * 1000) + 1000);   /* чекаємо СВІЙ кеш */
    printf("    з нашого боку:                          %ld\n",
           count_prefix(share, ".nfs"));

    rpc("CLOSE 1");
    if (dir_ttl > 0) nap_ms((long) (dir_ttl * 1000) + 1000);
    printf("5c. після close() письменника лишилося:     %ld\n",
           count_prefix(share, ".nfs"));
}
