struct SubGraph {
    std::vector<int> nparents; // скільки батьків-кандидатів у кожного кандидата
    std::vector<int> kid_off;  // N + 1 зсувів у kids
    std::vector<int> kids;     // діти-кандидати всіх кандидатів підряд
};

static SubGraph build_sub(const Dag& g, const Candidates& c)
{
    const int N = static_cast<int>(c.id.size());
    SubGraph s;
    s.nparents.assign(N, 0);
    s.kid_off.assign(N + 1, 0);

    for (int i = 0; i < N; ++i) {
        const int v = c.id[i];
        for (int k = g.par_off[v]; k < g.par_off[v + 1]; ++k) {
            const int j = c.local[g.par[k]];
            if (j < 0) continue;    // ребро назовні — обрізане
            ++s.nparents[i];
            ++s.kid_off[j + 1];     // у батька j стало на одну дитину більше
        }
    }
    for (int j = 0; j < N; ++j)     // зсуви = часткові суми кількостей
        s.kid_off[j + 1] += s.kid_off[j];

    s.kids.assign(s.kid_off[N], 0);
    std::vector<int> cursor(s.kid_off.begin(), s.kid_off.end() - 1);
    for (int i = 0; i < N; ++i) {
        const int v = c.id[i];
        for (int k = g.par_off[v]; k < g.par_off[v + 1]; ++k) {
            const int j = c.local[g.par[k]];
            if (j >= 0) s.kids[cursor[j]++] = i;
        }
    }
    return s;
}
