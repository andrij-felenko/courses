constexpr size_t SLOTS = 4;
static std::array<int, SLOTS> slot = {-1, -1, -1, -1};

static void ok(long v) { send_line(std::format("OK {}", v)); }
static void err() { send_line(std::format("ERR {}", errno)); }
static int sl(long i) { return (i >= 0 && static_cast<size_t>(i) < SLOTS) ? slot[i] : -1; }

static int mode_flags(std::string_view m) {
    if (m == "r")  return O_RDONLY;
    if (m == "rw") return O_RDWR   | O_CREAT;
    if (m == "w")  return O_WRONLY | O_CREAT | O_TRUNC;
    if (m == "wx") return O_WRONLY | O_CREAT | O_EXCL;
    return -1;
}

static long count_prefix(const fs::path& dir, std::string_view prefix) {
    long k = 0;
    std::error_code ec;
    for (const auto& entry : fs::directory_iterator(dir, ec)) {
        if (entry.path().filename().string().starts_with(prefix))
            k++;
    }
    return ec ? -1 : k;
}

static void race(std::string_view prefix, int rounds, std::string& bits) {
    bits.clear();
    for (int i = 0; i < rounds; ++i) {
        auto name = at(std::format("{}-{}", prefix, i));
        int fd = ::open(name.c_str(), O_WRONLY | O_CREAT | O_EXCL, 0644);
        if (fd >= 0) { bits.push_back('1'); ::close(fd); }
        else { bits.push_back('0'); }
    }
}

static void serve() {
    std::string cmd;
    slot.fill(-1);

    while (recv_line(cmd) == 0) {
        long i = 0, n = 0, off = 0;
        char a_buf[64] = {}, b_buf[512] = {};

        if (::sscanf(cmd.c_str(), "OPEN %ld %63s %511s", &i, a_buf, b_buf) == 3 && i >= 0 && static_cast<size_t>(i) < SLOTS) {
            int fl = mode_flags(a_buf);
            slot[i] = (fl < 0) ? -1 : ::open(at(b_buf).c_str(), fl, 0644);
            if (slot[i] < 0) err(); else ok(0);
        }
        else if (::sscanf(cmd.c_str(), "WRITE %ld %ld", &i, &n) == 2) {
            std::vector<char> buf(static_cast<size_t>(n), 'x');
            ssize_t w = ::write(sl(i), buf.data(), buf.size());
            if (w != static_cast<ssize_t>(n)) err(); else ok(n);
        }
        else if (::sscanf(cmd.c_str(), "FSYNC %ld", &i) == 1) {
            if (::fsync(sl(i)) < 0) err(); else ok(0);
        }
        else if (::sscanf(cmd.c_str(), "PREAD %ld %ld %ld", &i, &off, &n) == 3) {
            std::vector<char> buf(4096);
            if (n > static_cast<long>(buf.size())) n = static_cast<long>(buf.size());
            ssize_t r = ::pread(sl(i), buf.data(), static_cast<size_t>(n), static_cast<off_t>(off));
            if (r < 0) err(); else ok(r);
        }
        else if (::sscanf(cmd.c_str(), "CLOSE %ld", &i) == 1) {
            int rc = ::close(sl(i));
            if (i >= 0 && static_cast<size_t>(i) < SLOTS) slot[i] = -1;
            if (rc < 0) err(); else ok(0);
        }
        else if (::sscanf(cmd.c_str(), "FLOCK %ld", &i) == 1) {
            if (::flock(sl(i), LOCK_EX | LOCK_NB) < 0) err(); else ok(0);
        }
        else if (::sscanf(cmd.c_str(), "FCNTL %ld", &i) == 1) {
            struct flock fl{};
            fl.l_type = F_WRLCK;
            fl.l_whence = SEEK_SET;
            if (::fcntl(sl(i), F_SETLK, &fl) < 0) err(); else ok(0);
        }
        else if (::sscanf(cmd.c_str(), "UNLINK %511s", b_buf) == 1) {
            std::error_code ec;
            fs::remove(at(b_buf), ec);
            if (ec) err(); else ok(0);
        }
        else if (::sscanf(cmd.c_str(), "COUNT %511s", b_buf) == 1) {
            ok(count_prefix(share_dir, b_buf));
        }
        else if (::sscanf(cmd.c_str(), "RACE %511s %ld", b_buf, &n) == 2) {
            std::string bits;
            race(b_buf, static_cast<int>(n), bits);
            send_line(bits);
        }
        else if (cmd == "BYE") return;
        else send_line("ERR 22");
    }
}
