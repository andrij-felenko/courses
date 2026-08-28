struct Visibility {
    std::vector<Word> bits;                       // блок → маска блоків (себе включно)
    std::vector<long long> seen;                  // блок → скільки ЕЛЕМЕНТІВ бачить його член
    long long total = 0;
    double cost = 0.0;
};

static Visibility visibility(const Cond& c, const std::vector<int>& order, int n) {
    const int C = c.count;
    const size_t W = ((size_t)C + WBITS - 1) / WBITS;
    Visibility r;
    r.bits.assign((size_t)C * W, 0);
    r.seen.assign(C, 0);

    std::vector<std::vector<int>> deps(C);
    for (const auto& e : c.edge) deps[e.first].push_back(e.second);

    // Порядок такий, що блок іде ПІСЛЯ всіх, кого потребує, — отже, на момент
    // обробки всі доданки вже готові, і достатньо одного проходу.
    for (const int b : order) {
        Word* dst = &r.bits[(size_t)b * W];
        dst[b / WBITS] |= Word(1) << (b % WBITS);          // блок бачить сам себе
        for (const int d : deps[b]) {
            const Word* src = &r.bits[(size_t)d * W];
            for (size_t k = 0; k < W; ++k) dst[k] |= src[k];
        }
    }

    for (int b = 0; b < C; ++b) {                 // маска блоків → кількість елементів
        long long s = 0;
        const Word* src = &r.bits[(size_t)b * W];
        for (size_t k = 0; k < W; ++k) {
            Word w = src[k];
            while (w) {
                const int j = (int)k * WBITS + std::countr_zero(w);
                w &= w - 1;                       // погасити молодший установлений біт
                s += (long long)c.members[j].size();
            }
        }
        r.seen[b] = s;
        r.total += (long long)c.members[b].size() * s;
    }
    r.cost = (double)r.total / ((double)n * n);
    return r;
}
