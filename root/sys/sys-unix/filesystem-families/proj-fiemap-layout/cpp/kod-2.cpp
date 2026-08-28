class UniqueFd {
    int fd_{-1};
public:
    explicit UniqueFd(int fd = -1) : fd_(fd) {}
    ~UniqueFd() { if (fd_ >= 0) ::close(fd_); }
    UniqueFd(const UniqueFd &) = delete;
    UniqueFd &operator=(const UniqueFd &) = delete;
    UniqueFd(UniqueFd &&o) noexcept : fd_(o.fd_) { o.fd_ = -1; }
    UniqueFd &operator=(UniqueFd &&o) noexcept {
        if (this != &o) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = o.fd_; o.fd_ = -1;
        }
        return *this;
    }
    [[nodiscard]] int get() const { return fd_; }
    [[nodiscard]] bool valid() const { return fd_ >= 0; }
};

static int map_file(const char *path, unsigned req_flags, bool verbose)
{
    UniqueFd fd{::open(path, O_RDONLY)};
    if (!fd.valid()) { std::perror(path); return -1; }

    struct stat st;
    if (::fstat(fd.get(), &st) < 0) { std::perror("fstat"); return -1; }

    size_t buf_size = sizeof(fiemap) + SLOTS * sizeof(fiemap_extent);
    std::vector<uint8_t> buffer(buf_size, 0);
    auto *fm = reinterpret_cast<fiemap*>(buffer.data());

    Walk w;
    uint64_t want = 0, idx = 0;
    bool last = false;
    int rc = 0;

    if (verbose)
        std::cout << "       №     зсув у файлі      довжина    зсув на носії  прапорці\n";

    while (!last) {
        std::memset(buffer.data(), 0, buf_size);
        fm->fm_start        = want;
        fm->fm_length       = FIEMAP_MAX_OFFSET - want;
        fm->fm_flags        = want ? (req_flags & ~FIEMAP_FLAG_SYNC) : req_flags;
        fm->fm_extent_count = SLOTS;

        if (::ioctl(fd.get(), FS_IOC_FIEMAP, fm) < 0) {
            if (errno == EBADR)
                std::cerr << path << ": ФС не розуміє прапорці 0x" << std::hex << fm->fm_flags << std::dec << "\n";
            else if (errno == EOPNOTSUPP)
                std::cerr << path << ": ця файлова система не віддає карту\n";
            else
                std::cerr << path << ": FIEMAP: " << std::strerror(errno) << "\n";
            rc = -1;
            break;
        }
        if (fm->fm_mapped_extents == 0)
            break;                                // даних далі немає

        for (unsigned i = 0; i < fm->fm_mapped_extents; i++) {
            const auto &e = fm->fm_extents[i];
            w.take(e, verbose, ++idx);
            if (e.fe_flags & FIEMAP_EXTENT_LAST)
                last = true;
        }

        if (w.seen_end <= want)                   // карта не рухається
            break;
        want = w.seen_end;
    }

    if (rc == 0 && w.seen_end < static_cast<uint64_t>(st.st_size)) {
        w.holes++;                                // хвостова діра
        w.hole_bytes += static_cast<uint64_t>(st.st_size) - w.seen_end;
    }

    if (rc == 0) {
        std::cout << path << "\n";
        printf("  розмір               %" PRIu64 " Б\n", static_cast<uint64_t>(st.st_size));
        printf("  віддано блоків       %" PRIu64 " Б\n", static_cast<uint64_t>(st.st_blocks) * 512);
        printf("  екстентів            %" PRIu64 "\n", w.n);
        if (w.n) {
            printf("  відображено          %" PRIu64 " Б\n", w.mapped);
            printf("  середня довжина      %.0f Б\n", static_cast<double>(w.mapped) / static_cast<double>(w.n));
            printf("  найдовший            %" PRIu64 " Б\n", w.longest);
        }
        if (w.pairs)
            printf("  частка суцільності   %.3f (%" PRIu64 " з %" PRIu64
                   " сусідніх пар упритул)\n",
                   static_cast<double>(w.glued) / static_cast<double>(w.pairs), w.glued, w.pairs);
        if (w.holes)     printf("  дірок                %" PRIu64 " на %" PRIu64 " Б\n",
                                w.holes, w.hole_bytes);
        if (w.unwritten) printf("  недоторканих         %" PRIu64 " Б (unwritten)\n", w.unwritten);
        if (w.delalloc)  printf("  ще не розподілено    %" PRIu64 " Б (delalloc)\n", w.delalloc);
        if (w.shared)    printf("  спільних із кимось   %" PRIu64 " Б (shared)\n", w.shared);
        if (w.encoded)   printf("  закодованих          %" PRIu64 " Б (encoded)\n", w.encoded);
    }

    return rc;
}
