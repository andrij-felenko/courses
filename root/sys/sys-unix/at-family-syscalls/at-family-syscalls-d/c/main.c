int walk_down(int dirfd, char *const comps[], int n)
{
    int d = dirfd;
    for (int i = 0; i < n; i++) {
        int next = openat(d, comps[i],
                          O_RDONLY | O_DIRECTORY | O_NOFOLLOW | O_CLOEXEC);
        if (d != dirfd) close(d);
        if (next < 0) return -1;      /* ELOOP — підмінили на посилання
                                         ENOTDIR — підмінили на файл */
        d = next;
    }
    return d;
}
