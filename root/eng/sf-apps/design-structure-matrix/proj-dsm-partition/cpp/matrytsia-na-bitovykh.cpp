struct Layout {
    std::vector<int> row;                         // номер рядка → елемент
    std::vector<int> at;                          // елемент → номер рядка
    std::vector<int> pos;                         // блок → його номер у порядку
};

static Layout lay_out(const Cond& c, const std::vector<int>& order, int n) {
    Layout L;
    L.row.reserve(n);
    for (const int b : order)
        for (const int v : c.members[b]) L.row.push_back(v);
    L.at.assign(n, 0);
    for (int k = 0; k < n; ++k) L.at[L.row[k]] = k;
    L.pos.assign(c.count, 0);
    for (int k = 0; k < (int)order.size(); ++k) L.pos[order[k]] = k;
    return L;
}

// Щільна бітова DSM у порядку друку. Пам'ять n²/8 байтів: 5 000 елементів —
// 3.1 МіБ, 50 000 — 312 МіБ, тож будуємо її лише коли справді показуємо.
static std::vector<Word> dense_dsm(const Csr& g, const Layout& L) {
    const int n = g.n;
    const size_t W = ((size_t)n + WBITS - 1) / WBITS;
    std::vector<Word> m((size_t)n * W, 0);
    for (int k = 0; k < n; ++k) {
        const int v = L.row[k];
        Word* dst = &m[(size_t)k * W];
        for (int e = g.head[v]; e < g.head[v + 1]; ++e) {
            const int j = L.at[g.to[e]];
            dst[j / WBITS] |= Word(1) << (j % WBITS);
        }
    }
    return m;
}

static void print_matrix(const Csr& g, const Input& in, const Cond& c,
                         const std::vector<int>& comp, const Layout& L, int limit) {
    const int n = g.n;
    if (n > limit) {
        std::printf("матриця не друкується: %d елементів (межа --limit %d)\n\n", n, limit);
        return;
    }
    const std::vector<Word> m = dense_dsm(g, L);
    const size_t W = ((size_t)n + WBITS - 1) / WBITS;

    int wide = 7;
    for (const std::string& s : in.name) wide = std::max(wide, (int)s.size());
    const int prefix = 3 + 2 + wide + 2 + 6;

    if (n >= 10) {                                // рядок десятків
        std::string h((size_t)prefix, ' ');
        for (int k = 1; k <= n; ++k) h.push_back(k < 10 ? ' ' : char('0' + k / 10 % 10));
        std::printf("%s\n", h.c_str());
    }
    std::string h((size_t)prefix, ' ');           // рядок одиниць
    for (int k = 1; k <= n; ++k) h.push_back(char('0' + k % 10));
    std::printf("%s\n", h.c_str());

    for (int k = 0; k < n; ++k) {
        const int v = L.row[k];
        std::string cells((size_t)n, '.');
        for (int j = 0; j < n; ++j)
            if ((m[(size_t)k * W + j / WBITS] >> (j % WBITS)) & 1) cells[j] = 'x';
        cells[k] = in.loop[v] ? '@' : '#';        // діагональ; '@' — петля сам-на-себе
        char blk[16];
        std::snprintf(blk, sizeof blk, "B%d%s", L.pos[comp[v]] + 1,
                      c.members[comp[v]].size() > 1 ? "*" : "");
        std::printf("%3d  %-*s  %-6s%s\n", k + 1, wide, in.name[v].c_str(), blk,
                    cells.c_str());
    }
    std::printf("\n");
}
