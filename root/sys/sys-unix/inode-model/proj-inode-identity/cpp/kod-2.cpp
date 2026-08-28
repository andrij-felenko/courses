// У C++ замість відкритої адресації та ручного виділення пам'яті використовують std::unordered_map:
struct dev_ino_pair {
    dev_t dev;
    ino_t ino;
    bool operator==(const dev_ino_pair& o) const noexcept {
        return dev == o.dev && ino == o.ino;
    }
};

struct dev_ino_hash {
    std::size_t operator()(const dev_ino_pair& p) const noexcept {
        auto mix = [](uint64_t h) {
            h ^= h >> 33;
            h *= UINT64_C(0xff51afd7ed558ccd);
            h ^= h >> 33;
            h *= UINT64_C(0xc4ceb9fe1a85ec53);
            h ^= h >> 33;
            return h;
        };
        return mix(static_cast<uint64_t>(p.ino) ^ mix(static_cast<uint64_t>(p.dev)));
    }
};

struct node_info {
    uintmax_t nlink{0};
    uintmax_t seen{0};
    uintmax_t size{0};
    uintmax_t real{0};
    std::string first_path;
};

using identity_table = std::unordered_map<dev_ino_pair, node_info, dev_ino_hash>;

bool table_first_time(identity_table& table, const struct stat& st, const std::string& path) {
    dev_ino_pair key{st.st_dev, st.st_ino};
    auto [it, inserted] = table.try_emplace(key, node_info{
        static_cast<uintmax_t>(st.st_nlink), 1,
        static_cast<uintmax_t>(st.st_size),
        static_cast<uintmax_t>(st.st_blocks) * BLOCK_UNIT,
        path
    });
    if (!inserted) {
        it->second.seen++;
        return false;
    }
    return true;
}
