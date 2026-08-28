struct Cond {
    int count = 0;
    std::vector<std::vector<int>> members;        // блок → елементи, за зростанням id
    std::vector<std::pair<int, int>> edge;        // (блок-споживач, блок-постачальник)
};

static Cond condense(const Csr& g, const std::vector<int>& comp, int ncomp) {
    Cond c;
    c.count = ncomp;
    c.members.assign(ncomp, {});
    for (int v = 0; v < g.n; ++v) c.members[comp[v]].push_back(v);
    for (int v = 0; v < g.n; ++v)
        for (int e = g.head[v]; e < g.head[v + 1]; ++e)
            if (comp[v] != comp[g.to[e]]) c.edge.emplace_back(comp[v], comp[g.to[e]]);
    std::sort(c.edge.begin(), c.edge.end());
    c.edge.erase(std::unique(c.edge.begin(), c.edge.end()), c.edge.end());
    return c;
}

// Порядок блоків: кожен після всіх, кого потребує. Серед незалежних блоків
// беремо той, чий перший елемент менший за абеткою, — і вивід стає не лише
// відтворюваним, а СТІЙКИМ: поява нового модуля не перетасовує решту.
static std::vector<int> canonical_order(const Cond& c) {
    std::vector<int> pending(c.count, 0);
    std::vector<std::vector<int>> users(c.count);
    for (const auto& e : c.edge) { ++pending[e.first]; users[e.second].push_back(e.first); }

    auto worse = [&](int x, int y) { return c.members[x][0] > c.members[y][0]; };
    std::priority_queue<int, std::vector<int>, decltype(worse)> ready(worse);
    for (int b = 0; b < c.count; ++b) if (pending[b] == 0) ready.push(b);

    std::vector<int> order;
    order.reserve(c.count);
    while (!ready.empty()) {
        const int b = ready.top();
        ready.pop();
        order.push_back(b);
        for (const int u : users[b]) if (--pending[u] == 0) ready.push(u);
    }
    return order;                                 // коротший за count — лише при помилці
}
