struct Node {
    Rule rule;
    std::vector<int> ins;    // входи, які теж хтось будує
    std::vector<int> outs;   // хто чекає на цю вершину
    int pending = 0;         // скільки входів іще не готові
};

static std::vector<Node> buildGraph(std::vector<Rule> rules) {
    std::vector<Node> g(rules.size());
    std::unordered_map<std::string, int> byOut;
    for (size_t i = 0; i < rules.size(); ++i) {
        if (!byOut.emplace(rules[i].out, (int)i).second)
            throw std::runtime_error("два правила на один вихід: " + rules[i].out);
        g[i].rule = std::move(rules[i]);
    }
    for (int v = 0; v < (int)g.size(); ++v)
        for (const auto& in : g[v].rule.ins) {
            auto it = byOut.find(in);
            if (it == byOut.end()) {                 // лист: файл просто мусить існувати
                if (!fs::exists(in))
                    throw std::runtime_error("нема ні файлу, ні правила: " + in);
                continue;
            }
            g[v].ins.push_back(it->second);
            g[it->second].outs.push_back(v);
            ++g[v].pending;
        }
    return g;
}
