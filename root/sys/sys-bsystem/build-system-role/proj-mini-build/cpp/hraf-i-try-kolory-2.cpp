// Три кольори: 0 — не заходили, 1 — на стеку, 2 — закрита.
// Ребро у вершину кольору 1 веде назад у власну гілку — це і є цикл.
static void checkAcyclic(const std::vector<Node>& g) {
    std::vector<int> color(g.size(), 0), path;   // path — поточна гілка, для повідомлення
    struct Frame { int v; size_t i; };
    std::vector<Frame> st;
    for (int s = 0; s < (int)g.size(); ++s) {
        if (color[s]) continue;
        color[s] = 1; path.push_back(s); st.push_back({s, 0});
        while (!st.empty()) {
            int v = st.back().v;
            if (st.back().i < g[v].ins.size()) {
                int u = g[v].ins[st.back().i++];
                if (color[u] == 1) {                       // ← цикл
                    std::string msg;
                    auto it = std::find(path.begin(), path.end(), u);
                    for (; it != path.end(); ++it) msg += g[*it].rule.out + " → ";
                    throw std::runtime_error("цикл у правилах: " + msg + g[u].rule.out);
                }
                if (!color[u]) { color[u] = 1; path.push_back(u); st.push_back({u, 0}); }
            } else {
                color[v] = 2; path.pop_back(); st.pop_back();
            }
        }
    }
}
