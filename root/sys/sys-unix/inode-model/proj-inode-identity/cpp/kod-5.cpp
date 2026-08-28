// У C++ вивід форматують через std::cout та std::string, а пам'ять контейнерів звільняється автоматично:
std::string human(uintmax_t bytes)
{
    static const char *unit[] = { "Б", "КіБ", "МіБ", "ГіБ", "ТіБ", "ПіБ" };
    double v = static_cast<double>(bytes);
    size_t u = 0;
    while (v >= 1024.0 && u + 1 < sizeof(unit) / sizeof(*unit)) { v /= 1024.0; u++; }
    char buf[64];
    if (u == 0) std::snprintf(buf, sizeof(buf), "%ju Б", bytes);
    else        std::snprintf(buf, sizeof(buf), "%.1f %s", v, unit[u]);
    return buf;
}

void report(const context& c)
{
    size_t ng = 0;
    for (const auto& [key, info] : c.seen)
        if (info.seen > 1) ng++;

    std::cout << "\n──── підсумок ────\n";
    std::cout << "каталогів               : " << c.dirs << "\n";
    std::cout << "звичайних файлів        : " << c.files << "\n";
    std::cout << "символьних посилань     : " << c.symlinks << "\n";
    std::cout << "інших об'єктів          : " << c.others << "\n";
    std::cout << "реальний обсяг          : " << human(c.real_bytes) << "   (Σ st_blocks·512, кожен inode раз)\n";
    std::cout << "номінальний обсяг       : " << human(c.apparent_bytes) << "   (Σ st_size)\n";
    std::cout << "подвійного обліку уникнуто: " << human(c.shared_bytes) << " у " << ng << " групах посилань\n";
    if (c.crossings) std::cout << "меж монтування пропущено: " << c.crossings << "\n";
    if (c.vanished)  std::cout << "зникло під час обходу   : " << c.vanished << "\n";
    if (c.errors)    std::cout << "!! помилок              : " << c.errors << " — підсумок НЕПОВНИЙ\n";
}

int main(int argc, char **argv)
{
    context c;
    int argi = 1;
    if (argi < argc && std::string_view(argv[argi]) == "-x") { c.one_fs = true; argi++; }
    if (argi >= argc) {
        std::cerr << "вжиток: inodesum [-x] шлях...\n";
        return 2;
    }

    std::string path;
    for (; argi < argc; argi++) {
        path = argv[argi];

        struct stat st{};
        if (fstatat_retry(AT_FDCWD, path.c_str(), &st, AT_SYMLINK_NOFOLLOW) != 0) {
            warn_at(c, path, "fstatat");
            continue;
        }
        c.root_dev = st.st_dev;
        account(c, st, path);

        if (S_ISDIR(st.st_mode)) {
            int fd = openat_retry(AT_FDCWD, path.c_str(), O_RDONLY | O_DIRECTORY | O_CLOEXEC);
            if (fd < 0) { warn_at(c, path, "openat"); continue; }
            walk(fd, path, c);
        }
    }

    report(c);
    return c.errors > 0 ? 1 : 0;
}
