// Позначити все, що досяжне з roots (разом із самими roots).
static void mark_reachable(const Dag& g, const std::vector<int>& roots,
                           std::vector<char>& mark)
{
    std::vector<int> stack;
    for (int r : roots)
        if (!mark[r]) { mark[r] = 1; stack.push_back(r); }

    while (!stack.empty()) {
        const int v = stack.back();
        stack.pop_back();
        for (int k = g.par_off[v]; k < g.par_off[v + 1]; ++k) {
            const int p = g.par[k];
            if (!mark[p]) { mark[p] = 1; stack.push_back(p); }
        }
    }
}

struct Candidates {
    std::vector<int> id;    // локальний номер 0..N-1 → номер у повному графі
    std::vector<int> local; // номер у повному графі → локальний номер або −1
};

static Candidates collect(const Dag& g, int bad, const std::vector<int>& good)
{
    std::vector<char> checked(g.n, 0);
    mark_reachable(g, good, checked);   // усе, що вже накрите добрими

    Candidates c;
    c.local.assign(g.n, -1);
    if (checked[bad])
        return c;                       // поганий в історії доброго — вхід суперечливий

    std::vector<int> stack;
    c.local[bad] = 0;
    c.id.push_back(bad);
    stack.push_back(bad);

    while (!stack.empty()) {
        const int v = stack.back();
        stack.pop_back();
        for (int k = g.par_off[v]; k < g.par_off[v + 1]; ++k) {
            const int p = g.par[k];
            if (checked[p] || c.local[p] >= 0)
                continue;               // за межі множини не виходимо
            c.local[p] = static_cast<int>(c.id.size());
            c.id.push_back(p);
            stack.push_back(p);
        }
    }
    return c;
}
