static long long count_extents(int fd, unsigned req_flags)
{
    struct fiemap fm;
    memset(&fm, 0, sizeof fm);
    fm.fm_start        = 0;
    fm.fm_length       = FIEMAP_MAX_OFFSET;
    fm.fm_flags        = req_flags;
    fm.fm_extent_count = 0;                       /* масиву немає — тільки лічи */
    if (ioctl(fd, FS_IOC_FIEMAP, &fm) < 0)
        return -1;
    return (long long)fm.fm_mapped_extents;
}

int main(int argc, char **argv)
{
    unsigned req_flags = 0;
    int verbose = 0, count_only = 0, opt, bad = 0;

    while ((opt = getopt(argc, argv, "svc")) != -1) {
        switch (opt) {
        case 's': req_flags |= FIEMAP_FLAG_SYNC; break;
        case 'v': verbose = 1; break;
        case 'c': count_only = 1; break;
        default:  fprintf(stderr, "вжиток: %s [-s] [-v] [-c] файл...\n", argv[0]);
                  return 2;
        }
    }
    if (optind == argc) {
        fprintf(stderr, "вжиток: %s [-s] [-v] [-c] файл...\n", argv[0]);
        return 2;
    }

    for (int i = optind; i < argc; i++) {
        if (!count_only) {
            if (map_file(argv[i], req_flags, verbose) < 0)
                bad = 1;
            continue;
        }
        int fd = open(argv[i], O_RDONLY);
        if (fd < 0) { perror(argv[i]); bad = 1; continue; }
        long long n = count_extents(fd, req_flags);
        if (n < 0) { fprintf(stderr, "%s: FIEMAP: %s\n", argv[i], strerror(errno)); bad = 1; }
        else       { printf("%s: %lld екстентів\n", argv[i], n); }
        close(fd);
    }
    return bad ? 1 : 0;
}
