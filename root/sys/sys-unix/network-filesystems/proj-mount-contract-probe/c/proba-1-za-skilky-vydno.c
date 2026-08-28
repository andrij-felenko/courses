static double dir_ttl = -1;        /* результат цієї проби знадобиться далі */

static int in_listing(const char *dir, const char *name)
{
    DIR           *d = opendir(dir);
    struct dirent *e;
    int            found = 0;

    if (!d) return 0;
    while ((e = readdir(d)) != NULL)
        if (strcmp(e->d_name, name) == 0) { found = 1; break; }
    closedir(d);
    return found;
}

static void probe_visibility(void)
{
    char        name[64], path[PATH_MAX];
    struct stat st;
    double      t0, ts = -1, td = -1;

    snprintf(name, sizeof name, "vis-%ld", (long) getpid());
    snprintf(path, sizeof path, "%s/%s", share, name);

    if (stat(path, &st) == 0) { puts("1. ім'я вже зайняте"); return; }
    in_listing(share, name);             /* прогріваємо негативний запис */

    if (rpc("OPEN 0 wx %s", name) < 0) { puts("1. створити не вдалося"); return; }
    rpc("WRITE 0 64");
    rpc("FSYNC 0");
    rpc("CLOSE 0");

    t0 = mono();                         /* ← нуль нашого секундоміра */

    while (mono() - t0 < 180.0 && (ts < 0 || td < 0)) {
        if (ts < 0 && stat(path, &st) == 0)    ts = mono() - t0;
        if (td < 0 && in_listing(share, name)) td = mono() - t0;
        nap_ms(50);
    }

    printf("1a. stat() бачить новий файл через   %s с\n", secs(ts));
    printf("1b. readdir() бачить його через      %s с\n", secs(td));

    dir_ttl = (ts > td) ? ts : td;
    rpc("UNLINK %s", name);
}
