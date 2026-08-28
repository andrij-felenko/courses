#include <vector>
#include <utility>
#include <algorithm>

std::vector<int> de_bruijn_hierholzer(int k, int n) {
    std::size_t m = 1;                             // m = k^(n-1) — число вершин
    for (int i = 0; i < n - 1; ++i) m *= static_cast<std::size_t>(k);

    std::vector<int> nxt(m, 0);                    // наступний невитрачений символ вершини
    std::vector<std::pair<std::size_t, int>> stack{ {0, -1} };  // (вершина, ребро-вхід)
    std::vector<int> seq;

    while (!stack.empty()) {
        auto [v, sym] = stack.back();
        if (nxt[v] < k) {                          // є невитрачене ребро — глибше
            int c = nxt[v]++;
            stack.push_back({ (v * k + c) % m, c });
        } else {                                   // глухий кут — відступ із записом
            stack.pop_back();
            if (sym != -1) seq.push_back(sym);
        }
    }
    std::reverse(seq.begin(), seq.end());
    return seq;
}
