// Чи є напрямлений шлях src → … → dst.
bool reaches(const Graph& g, const std::string& src, const std::string& dst) {
    std::unordered_set<std::string> seen{src};
    std::vector<std::string> stack{src};
    while (!stack.empty()) {
        std::string u = stack.back();
        stack.pop_back();
        auto it = g.find(u);
        if (it == g.end()) continue;
        for (const std::string& v : it->second) {   // порядок обходу не важить
            if (v == dst) return true;
            if (seen.insert(v).second)               // вставили вперше → у стек
                stack.push_back(v);
        }
    }
    return false;
}

// rules: пари (X, Y) зі змістом «X не сміє досягати Y».
std::vector<std::string> check_forbidden(
        const Graph& g,
        const std::vector<std::pair<std::string, std::string>>& rules) {
    std::vector<std::string> bad;
    for (const auto& [x, y] : rules)
        if (reaches(g, x, y))
            bad.push_back(x + " ⇏ " + y + ": є шлях " + x + " → … → " + y);
    return bad;
}
