static int make_file(const std::string &path) {
    int fd = open(path.c_str(), O_RDWR | O_CREAT, 0644);
    struct stat st{};
    fstat(fd, &st);
    if (static_cast<std::size_t>(st.st_size) < FSIZE) {
        std::vector<char> chunk(1 << 20, 0xA5);
        for (std::size_t off = 0; off < FSIZE; off += (1 << 20)) {
            write(fd, chunk.data(), chunk.size());
        }
    }
    fsync(fd);
    return fd;
}

static void chill(int fd) {
    fsync(fd);
    posix_fadvise(fd, 0, 0, POSIX_FADV_DONTNEED);
}

static void exp_file(int fd, const std::string &label, bool cold, int advice, bool randomly) {
    mark m;
    std::size_t n = FSIZE / PGSZ;
    if (cold) chill(fd);

    char *p = static_cast<char*>(mmap(nullptr, FSIZE, PROT_READ, MAP_PRIVATE, fd, 0));
    if (advice) madvise(p, FSIZE, advice);
    std::cout << "  " << std::left << std::setw(32) << label
              << " резидентних до обходу: " << resident(p, FSIZE) << " з " << n << "\n";

    if (randomly) {
        auto idx = permutation(n);
        mark_begin(m);
        touch_perm(p, idx);
        mark_end(m, "  обхід");
    } else {
        mark_begin(m);
        touch_seq(p, FSIZE, false);
        mark_end(m, "  обхід");
    }
    munmap(p, FSIZE);
}
