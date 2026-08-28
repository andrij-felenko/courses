struct Hunt { uint64_t total, halted, undecided, best_ones, best_steps; };

Hunt hunt(uint32_t n, uint64_t cap) {
    uint32_t a_size = 4 * n + 4;              // дій на клітинку
    size_t cells = 2 * n;
    std::vector<uint32_t> table(cells, 0);
    table[0] = 7;                             // старт-нормалізація: A,0 = (1,R,B) = 7
    size_t free_cells = cells - 1;            // вільні клітинки — 1 … cells-1
    std::vector<uint32_t> idx(free_cells, 0); // мішано-основний лічильник
    Hunt r{0, 0, 0, 0, 0};
    for (;;) {
        for (size_t i = 0; i < free_cells; ++i) table[i + 1] = idx[i];
        ++r.total;
        Run run = simulate(table, n, cap);
        if (run.halted) {
            ++r.halted;
            if (run.ones  > r.best_ones)  r.best_ones  = run.ones;   // рекорд одиниць → Σ(n)
            if (run.steps > r.best_steps) r.best_steps = run.steps;  // рекорд кроків  → S(n)
        } else {
            ++r.undecided;                        // ще працює на стелі
        }
        // ++лічильник за основою a_size; переповнення → арену пройдено
        size_t k = 0;
        while (k < free_cells) { if (++idx[k] < a_size) break; idx[k] = 0; ++k; }
        if (k == free_cells) break;
    }
    return r;
}
