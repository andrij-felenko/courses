/* НАЇВНО — так робити не варто. */
static unsigned long long du_naive(const char *dir)
{
    unsigned long long total = 0;
    DIR *dp = opendir(dir);
    if (!dp)
        return 0;

    struct dirent *e;
    while ((e = readdir(dp)) != NULL) {
        if (!strcmp(e->d_name, ".") || !strcmp(e->d_name, ".."))
            continue;

        char child[PATH_MAX];
        snprintf(child, sizeof child, "%s/%s", dir, e->d_name);

        struct stat st;
        if (stat(child, &st) < 0)
            continue;

        total += (unsigned long long)st.st_blocks * 512;
        if (S_ISDIR(st.st_mode))
            total += du_naive(child);
    }
    closedir(dp);
    return total;
}
