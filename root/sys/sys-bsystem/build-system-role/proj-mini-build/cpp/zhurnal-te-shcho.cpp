struct Stamp { uint64_t key = 0, art = 0; };   // ключ задачі й геш артефакту

static std::unordered_map<std::string, Stamp> loadLog(const fs::path& p) {
    std::unordered_map<std::string, Stamp> log;
    std::ifstream f(p);
    std::string line;
    while (std::getline(f, line)) {
        std::istringstream is(line);
        Stamp s; std::string out;
        if (!(is >> std::hex >> s.key >> s.art)) continue;   // зіпсований рядок — пропустити
        is >> std::ws;
        if (std::getline(is, out) && !out.empty()) log[out] = s;
    }
    return log;
}

static void saveLog(const fs::path& p, const std::unordered_map<std::string, Stamp>& log) {
    std::ofstream f(p, std::ios::trunc);
    for (const auto& [out, s] : log) f << std::hex << s.key << ' ' << s.art << ' ' << out << '\n';
}
