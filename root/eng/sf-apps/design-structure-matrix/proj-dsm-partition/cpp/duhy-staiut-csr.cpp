struct Csr {
    int n = 0;
    std::vector<int> head, to;                    // head має n + 1 елемент
};

static Csr build_csr(int n, const std::vector<std::pair<int, int>>& edge) {
    Csr g;
    g.n = n;
    g.head.assign(n + 1, 0);
    for (const auto& e : edge) ++g.head[e.first + 1];
    for (int i = 0; i < n; ++i) g.head[i + 1] += g.head[i];
    g.to.resize(edge.size());
    std::vector<int> put = g.head;                // куди класти наступного сусіда
    for (const auto& e : edge) g.to[put[e.first]++] = e.second;
    return g;
}
