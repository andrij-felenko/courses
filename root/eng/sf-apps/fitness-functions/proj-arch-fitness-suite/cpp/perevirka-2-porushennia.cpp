// level: модуль → номер шару (більший = вищий). Ребро вгору — порушення.
std::vector<std::string> check_layers(
        const Graph& g, const std::unordered_map<std::string, int>& level) {
    auto lv = [&](const std::string& m) {
        auto it = level.find(m);
        return it == level.end() ? 0 : it->second;
    };
    std::vector<std::string> bad;
    for (const auto& [u, deps] : g)
        for (const std::string& v : deps)
            if (lv(u) < lv(v))                        // залежність веде ВГОРУ
                bad.push_back(u + "(р." + std::to_string(lv(u)) + ") → " +
                              v + "(р." + std::to_string(lv(v)) + "): ребро вгору");
    return bad;
}
