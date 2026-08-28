struct Choice {
    int commit = -1; // що перевіряти наступним (номер у повному графі)
    int total  = 0;  // N — скільки кандидатів лишилося
    int score  = 0;  // скільки з них гарантовано відпаде після відповіді
};

// skipped — прапорці завдовжки g.n у нумерації повного графа.
Choice next_to_test(const Dag& g, int bad, const std::vector<int>& good,
                    const std::vector<char>& skipped)
{
    const Candidates c = collect(g, bad, good);
    const SubGraph   s = build_sub(g, c);
    const int        N = static_cast<int>(c.id.size());

    Choice out;
    out.total = N;
    if (N <= 1) {                   // кандидат один — він і є перший поганий,
        if (N == 1) out.commit = c.id[0];   // перевіряти вже нічого
        return out;
    }

    std::vector<int> a(N, 0), stamp(N, -1);
    std::vector<int> pending = s.nparents;
    std::vector<int> stack, order;
    order.reserve(N);
    for (int i = 0; i < N; ++i)
        if (pending[i] == 0) order.push_back(i);

    for (std::size_t h = 0; h < order.size(); ++h) {
        const int i = order[h];
        const int v = c.id[i];

        int np = 0, only_parent = -1;
        for (int k = g.par_off[v]; k < g.par_off[v + 1]; ++k) {
            const int j = c.local[g.par[k]];
            if (j >= 0) { ++np; only_parent = j; }
        }

        if (np == 0)                        // дно множини
            a[i] = 1;
        else if (np == 1)                   // ланцюжок — задарма
            a[i] = a[only_parent] + 1;
        else                                // злиття — тільки повним обходом
            a[i] = count_reachable(g, c, i, stamp, stack);

        if (!skipped[v]) {                  // те, чого не повернемо, не оцінюємо
            const int score = std::min(a[i], N - a[i]);
            if (score > out.score) { out.score = score; out.commit = v; }
            if (std::abs(2 * a[i] - N) <= 1)
                return out;                 // бал уже максимальний, ⌊N/2⌋
        }

        for (int k = s.kid_off[i]; k < s.kid_off[i + 1]; ++k)
            if (--pending[s.kids[k]] == 0)
                order.push_back(s.kids[k]);
    }
    return out;                             // commit < 0 ⟺ усе пропущене
}
