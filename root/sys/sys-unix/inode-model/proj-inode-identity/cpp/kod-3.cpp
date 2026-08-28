// У C++ структури описуються з ініціалізаторами за замовчуванням, а помилки — через std::system_category:
struct sparse_hit {
    std::string path;
    uintmax_t gap{0}, size{0}, real{0};
};

struct context {
    identity_table seen;
    bool one_fs{false};
    dev_t root_dev{0};

    uintmax_t dirs{0}, files{0}, symlinks{0}, others{0};
    uintmax_t real_bytes{0}, apparent_bytes{0}, shared_bytes{0};
    uintmax_t errors{0}, vanished{0}, crossings{0}, sparse_count{0};

    std::vector<sparse_hit> sparse;
};

void warn_at(context& c, const std::string& path, std::string_view what) {
    c.errors++;
    std::cerr << "inodesum: " << path << ": " << what << ": "
              << std::system_category().message(errno) << "\n";
}

void account(context& c, const struct stat& st, const std::string& path) {
    uintmax_t real = static_cast<uintmax_t>(st.st_blocks) * BLOCK_UNIT;
    uintmax_t size = static_cast<uintmax_t>(st.st_size);

    if (S_ISDIR(st.st_mode)) {
        c.dirs++;
        c.real_bytes += real;
        c.apparent_bytes += size;
        return;
    }

    if      (S_ISREG(st.st_mode)) c.files++;
    else if (S_ISLNK(st.st_mode)) c.symlinks++;
    else                          c.others++;

    if (st.st_nlink <= 1 || table_first_time(c.seen, st, path)) {
        c.real_bytes += real;
        c.apparent_bytes += size;
    } else {
        c.shared_bytes += real;
    }
}
