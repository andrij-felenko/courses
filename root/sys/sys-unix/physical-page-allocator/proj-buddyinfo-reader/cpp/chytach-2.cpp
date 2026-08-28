int main(int argc, char **argv)
{
    long pgsz = sysconf(_SC_PAGESIZE);
    unsigned long need = 0;
    std::string only;
    bool want_hidden = false;

    for (int i = 1; i < argc; i++) {
        std::string_view arg(argv[i]);
        if (arg == "--need" && i + 1 < argc)
            need = std::stoul(argv[++i]);
        else if (arg == "--zone" && i + 1 < argc)
            only = argv[++i];
        else if (arg == "--hidden")
            want_hidden = true;
        else { std::cerr << "не знаю опції " << arg << "\n"; return 2; }
    }

    std::string buf = slurp("/proc/buddyinfo");
    if (buf.empty()) { std::perror("buddyinfo"); return 1; }
    std::string zi = want_hidden ? slurp("/proc/zoneinfo") : "";

    std::vector<ZoneRow> rows;
    std::string_view sv(buf);
    while (!sv.empty()) {
        auto pos = sv.find('\n');
        std::string_view line = (pos == std::string_view::npos) ? sv : sv.substr(0, pos);
        sv = (pos == std::string_view::npos) ? std::string_view{} : sv.substr(pos + 1);

        ZoneRow r;
        if (parse_row(line, r)) {
            analyze(r);
            rows.push_back(std::move(r));
        }
    }
    if (rows.empty()) { std::cerr << "жодного рядка не розібрано\n"; return 1; }

    int wanted = -1;
    if (need) {
        wanted = 0;
        while (static_cast<unsigned long>(pgsz) << wanted < need && wanted < static_cast<int>(rows[0].nr_free.size()) - 1)
            wanted++;
    }

    std::string h1 = human(static_cast<unsigned long>(pgsz));
    std::string h2 = human(static_cast<unsigned long>(pgsz) << (rows[0].nr_free.size() - 1));
    std::cout << "кадр " << h1 << ", порядків " << rows[0].nr_free.size()
              << " → MAX_PAGE_ORDER = " << (rows[0].nr_free.size() - 1)
              << ", найбільший блок " << h2 << "\n\n";

    for (const auto &r : rows) {
        if (!only.empty() && only != r.name) continue;
        std::cout << "Node " << r.node << ", zone " << r.name
                  << "  вільно " << (r.free_pages * static_cast<double>(pgsz) / 1048576.0) << " МіБ";
        if (r.top >= 0) {
            std::cout << "   найбільший блок: порядок " << r.top << " = " << human(static_cast<unsigned long>(pgsz) << r.top) << "\n";
        } else {
            std::cout << "   вільних блоків немає зовсім\n";
        }

        if (want_hidden) {
            unsigned long hid = pcp_hidden(zi, r.node, r.name);
            std::cout << "    у запасах ядер, поза цим рядком: " << hid << " кадрів (" << human(hid * static_cast<unsigned long>(pgsz)) << ")\n";
        }

        if (need) {
            std::cout << "    під " << human(need) << " треба порядок " << wanted
                      << " → таких блоків ще дістану: " << (wanted < static_cast<int>(r.avail.size()) ? r.avail[wanted] : 0) << "\n";
            continue;
        }

        if (only.empty()) continue;
        std::cout << "    порядок     кадрів     у списку   ще дістану   розмір\n";
        for (std::size_t k = 0; k < r.nr_free.size(); k++) {
            std::cout << "    " << k << " " << (1UL << k) << " " << r.nr_free[k]
                      << " " << r.avail[k] << "   " << human(static_cast<unsigned long>(pgsz) << k) << "\n";
        }
        std::cout << "\n";
    }
    return 0;
}
