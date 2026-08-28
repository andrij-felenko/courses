static long long count_extents(int fd, unsigned req_flags)
{
    fiemap fm{};
    fm.fm_start        = 0;
    fm.fm_length       = FIEMAP_MAX_OFFSET;
    fm.fm_flags        = req_flags;
    fm.fm_extent_count = 0;                       // масиву немає — тільки лічи
    if (::ioctl(fd, FS_IOC_FIEMAP, &fm) < 0)
        return -1;
    return static_cast<long long>(fm.fm_mapped_extents);
}

int main(int argc, char **argv)
{
    unsigned req_flags = 0;
    bool verbose = false, count_only = false;
    int opt = 0, bad = 0;

    while ((opt = ::getopt(argc, argv, "svc")) != -1) {
        switch (opt) {
        case 's': req_flags |= FIEMAP_FLAG_SYNC; break;
        case 'v': verbose = true; break;
        case 'c': count_only = true; break;
        default:
            std::cerr << "вжиток: " << argv[0] << " [-s] [-v] [-c] файл...\n";
            return 2;
        }
    }
    if (optind == argc) {
        std::cerr << "вжиток: " << argv[0] << " [-s] [-v] [-c] файл...\n";
        return 2;
    }

    for (int i = optind; i < argc; i++) {
        if (!count_only) {
            if (map_file(argv[i], req_flags, verbose) < 0)
                bad = 1;
            continue;
        }
        UniqueFd fd{::open(argv[i], O_RDONLY)};
        if (!fd.valid()) { std::perror(argv[i]); bad = 1; continue; }
        long long n = count_extents(fd.get(), req_flags);
        if (n < 0) {
            std::cerr << argv[i] << ": FIEMAP: " << std::strerror(errno) << "\n";
            bad = 1;
        } else {
            std::cout << argv[i] << ": " << n << " екстентів\n";
        }
    }
    return bad ? 1 : 0;
}
