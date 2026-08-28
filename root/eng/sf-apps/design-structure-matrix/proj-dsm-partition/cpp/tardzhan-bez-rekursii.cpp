struct Frame { int v; int e; };                   // вершина і номер наступної дуги

// Компоненти нумеруються в порядку виходу, а він УЖЕ топологічний:
// якщо компонента A потребує компоненти B, то comp[B] < comp[A].
static int tarjan(const Csr& g, std::vector<int>& comp) {
    const int n = g.n;
    std::vector<int> idx(n, -1), low(n, 0);
    std::vector<char> onstk(n, 0);
    std::vector<int> cand;                        // стек кандидатів
    std::vector<Frame> call;                      // стек кадрів замість рекурсії
    comp.assign(n, -1);
    int timer = 0, ncomp = 0;

    for (int root = 0; root < n; ++root) {
        if (idx[root] != -1) continue;            // кілька незв'язаних частин — звідси
        idx[root] = low[root] = timer++;
        cand.push_back(root);
        onstk[root] = 1;
        call.push_back({root, g.head[root]});

        while (!call.empty()) {
            const int v = call.back().v;
            const int e = call.back().e;
            if (e < g.head[v + 1]) {
                call.back().e = e + 1;            // зсунути ДО можливого push_back:
                const int w = g.to[e];            // після нього посилання на кадр мертве
                if (idx[w] == -1) {
                    idx[w] = low[w] = timer++;
                    cand.push_back(w);
                    onstk[w] = 1;
                    call.push_back({w, g.head[w]});
                } else if (onstk[w]) {
                    low[v] = std::min(low[v], idx[w]);
                }
                continue;
            }
            if (low[v] == idx[v]) {               // v — корінь компоненти
                for (;;) {
                    const int w = cand.back();
                    cand.pop_back();
                    onstk[w] = 0;
                    comp[w] = ncomp;
                    if (w == v) break;
                }
                ++ncomp;
            }
            call.pop_back();
            if (!call.empty()) {                  // повернення в батька
                const int p = call.back().v;
                low[p] = std::min(low[p], low[v]);
            }
        }
    }
    return ncomp;
}
