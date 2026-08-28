// ─────────── ЧАСТИНА 1: машинка ───────────
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <optional>
#include <unordered_map>
#include <unordered_set>
#include <vector>

enum class Op { And, Or, Xor };

class Bdd {
public:
    static constexpr int Zero = 0;
    static constexpr int One = 1;

    explicit Bdd(int nvars) : nvars_(nvars), nodes_(2) {}   // 0 і 1 — термінали

    // Єдине місце, де народжується вузол. Обидва правила зведення — тут.
    int mk(int var, int lo, int hi) {
        if (lo == hi) return lo;                       // усунення: змінна ні на що не впливає
        const Node node{var, lo, hi};
        if (const auto it = unique_.find(node); it != unique_.end())
            return it->second;                         // злиття: такий вузол уже є
        const int u = static_cast<int>(nodes_.size());
        nodes_.push_back(node);
        unique_.emplace(node, u);
        return u;
    }

    int variable(int i) { return mk(i, Zero, One); }

    // Розкладання Шеннона, застосоване до пари функцій.
    int apply(Op op, int f, int g) {
        ++calls_;
        if (const int t = terminal(op, f, g); t >= 0) return t;
        if (f > g) std::swap(f, g);                    // усі три операції комутативні
        const CacheKey key{op, f, g};
        if (const auto it = cache_.find(key); it != cache_.end()) { ++hits_; return it->second; }
        const int var = std::min(top(f), top(g));      // верхня зі змінних, що зустрілися
        const auto [f0, f1] = cofactors(f, var);
        const auto [g0, g1] = cofactors(g, var);
        const int r = mk(var, apply(op, f0, g0), apply(op, f1, g1));
        cache_.emplace(key, r);
        return r;
    }

    std::size_t size(int u) const {
        std::unordered_set<int> seen;
        std::vector<int> stack{u};
        while (!stack.empty()) {
            const int x = stack.back();
            stack.pop_back();
            if (x < 2 || !seen.insert(x).second) continue;
            stack.push_back(nodes_[x].lo);
            stack.push_back(nodes_[x].hi);
        }
        return seen.size();
    }

    // Скільки з 2^nvars наборів дають 1. double — бо 2^n переростає будь-яке ціле.
    double count(int u) const {
        std::unordered_map<int, double> memo;
        return std::ldexp(countRec(u, memo), top(u));  // рівні НАД коренем теж пропущені
    }

    // Набір, на якому f = 1. У зведеній діаграмі кожен вузол, крім 0, здійсненний,
    // тому спуск ніколи не заходить у глухий кут — жодного вороття.
    std::optional<std::vector<int>> witness(int u) const {
        if (u == Zero) return std::nullopt;
        std::vector<int> env(nvars_, 0);               // пропущені змінні байдужі — хай 0
        while (u != One) {
            const Node& nd = nodes_[u];
            const bool takeHigh = (nd.lo == Zero);
            env[nd.var] = takeHigh ? 1 : 0;
            u = takeHigh ? nd.hi : nd.lo;
        }
        return env;
    }

    long long calls() const { return calls_; }
    long long hits() const { return hits_; }
    std::size_t tableSize() const { return nodes_.size() - 2; }

private:
    struct Node {
        int var, lo, hi;
        bool operator==(const Node& o) const noexcept {
            return var == o.var && lo == o.lo && hi == o.hi;
        }
    };
    struct CacheKey {
        Op op; int f, g;
        bool operator==(const CacheKey& o) const noexcept {
            return op == o.op && f == o.f && g == o.g;
        }
    };
    struct Hash {
        std::size_t operator()(const Node& k) const noexcept { return mix(k.var, k.lo, k.hi); }
        std::size_t operator()(const CacheKey& k) const noexcept {
            return mix(static_cast<int>(k.op), k.f, k.g);
        }
        static std::size_t mix(int a, int b, int c) noexcept {
            std::uint64_t h = static_cast<std::uint32_t>(a);
            h = h * 0x9E3779B97F4A7C15ull + static_cast<std::uint32_t>(b);
            h = (h ^ (h >> 29)) * 0xBF58476D1CE4E5B9ull + static_cast<std::uint32_t>(c);
            return static_cast<std::size_t>(h ^ (h >> 32));
        }
    };

    // Термінал не має змінної: віддаємо «рівень нижче всіх» — так min() працює сам собою.
    int top(int u) const { return u < 2 ? nvars_ : nodes_[u].var; }

    std::pair<int, int> cofactors(int u, int var) const {
        if (top(u) != var) return {u, u};               // змінної немає — обидві половини ті самі
        return {nodes_[u].lo, nodes_[u].hi};
    }

    static int terminal(Op op, int f, int g) {
        switch (op) {
        case Op::And:
            if (f == Zero || g == Zero) return Zero;
            if (f == One) return g;
            if (g == One) return f;
            if (f == g) return f;
            break;
        case Op::Or:
            if (f == One || g == One) return One;
            if (f == Zero) return g;
            if (g == Zero) return f;
            if (f == g) return f;
            break;
        case Op::Xor:
            if (f == Zero) return g;
            if (g == Zero) return f;
            if (f == g) return Zero;
            break;
        }
        return -1;
    }

    double countRec(int u, std::unordered_map<int, double>& memo) const {
        if (u < 2) return static_cast<double>(u);       // 0 → жодного набору, 1 → один
        if (const auto it = memo.find(u); it != memo.end()) return it->second;
        const Node& nd = nodes_[u];
        const double r = std::ldexp(countRec(nd.lo, memo), top(nd.lo) - nd.var - 1)
                       + std::ldexp(countRec(nd.hi, memo), top(nd.hi) - nd.var - 1);
        memo.emplace(u, r);
        return r;
    }

    int nvars_;
    std::vector<Node> nodes_;
    std::unordered_map<Node, int, Hash> unique_;        // вузол → його єдиний номер
    std::unordered_map<CacheKey, int, Hash> cache_;     // (операція, f, g) → готова відповідь
    long long calls_ = 0, hits_ = 0;
};

// ─────────── ЧАСТИНА 2: два суматори й дослід ───────────
struct Carry { int ripple, lookahead; };

// Змінні: a0 b0 a1 b1 ... a(n-1) b(n-1) cin
static Carry buildAdder(Bdd& b, int n, bool dropCinTerm = false) {
    std::vector<int> A(n), B(n);
    for (int i = 0; i < n; ++i) {
        A[i] = b.variable(2 * i);
        B[i] = b.variable(2 * i + 1);
    }
    const int cin = b.variable(2 * n);

    int c = cin;                                        // ланцюжок: c = G_i + P_i·c
    for (int i = 0; i < n; ++i) {
        const int g = b.apply(Op::And, A[i], B[i]);
        const int p = b.apply(Op::Or, A[i], B[i]);
        c = b.apply(Op::Or, g, b.apply(Op::And, p, c));
    }
    const int ripple = c;

    std::vector<int> G(n), P(n);                        // прискорений: усі переноси наперед
    for (int i = 0; i < n; ++i) {
        G[i] = b.apply(Op::And, A[i], B[i]);
        P[i] = b.apply(Op::Xor, A[i], B[i]);
    }
    int cla = Bdd::Zero;
    for (int i = 0; i < n; ++i) {
        int t = G[i];
        for (int j = i + 1; j < n; ++j) t = b.apply(Op::And, t, P[j]);
        cla = b.apply(Op::Or, cla, t);
    }
    if (!dropCinTerm) {                                 // доданок cin·P0···P(n-1)
        int t = cin;
        for (int j = 0; j < n; ++j) t = b.apply(Op::And, t, P[j]);
        cla = b.apply(Op::Or, cla, t);
    }
    return {ripple, cla};
}

// f = x0·y0 + x1·y1 + ... — щоб побачити ціну порядку змінних
static int buildPairs(Bdd& b, int n, bool interleaved) {
    int f = Bdd::Zero;
    for (int i = 0; i < n; ++i) {
        const int x = b.variable(interleaved ? 2 * i : i);
        const int y = b.variable(interleaved ? 2 * i + 1 : n + i);
        f = b.apply(Op::Or, f, b.apply(Op::And, x, y));
    }
    return f;
}

int main() {
    std::printf("=== той самий перенос, зібраний двома різними схемами ===\n");
    std::printf("  n | вузлів | rc == cla | наборів Cout=1 | усього наборів\n");
    for (const int n : {4, 16, 32}) {
        Bdd b(2 * n + 1);
        const Carry c = buildAdder(b, n);
        std::printf(" %2d | %6zu | %9s | %14.0f | %.0f\n", n, b.size(c.ripple),
                    c.ripple == c.lookahead ? "ТАК" : "НІ", b.count(c.ripple),
                    std::ldexp(1.0, 2 * n + 1));
    }

    std::printf("\n=== а тепер у прискореному забули доданок cin·P0···P(n-1) ===\n");
    {
        const int n = 16;
        Bdd b(2 * n + 1);
        const Carry c = buildAdder(b, n, /*dropCinTerm=*/true);
        const int miter = b.apply(Op::Xor, c.ripple, c.lookahead);  // де схеми РІЗНЯТЬСЯ
        std::printf("  rc == cla: %s | вузлів у різниці: %zu | наборів-контрприкладів: %.0f з %.0f\n",
                    c.ripple == c.lookahead ? "ТАК" : "НІ", b.size(miter),
                    b.count(miter), std::ldexp(1.0, 2 * n + 1));
        const auto env = b.witness(miter);
        long long a = 0, bb = 0;
        for (int i = 0; i < n; ++i) {
            a |= static_cast<long long>((*env)[2 * i]) << i;
            bb |= static_cast<long long>((*env)[2 * i + 1]) << i;
        }
        const int cin = (*env)[2 * n];
        std::printf("  контрприклад: a=%lld, b=%lld, cin=%d\n", a, bb, cin);
        std::printf("  чесна арифметика: (a+b+cin) >> %d = %lld"
                    "   ← ланцюжок каже це, поламаний прискорений каже 0\n",
                    n, (a + bb + cin) >> n);
    }

    std::printf("\n=== ціна порядку змінних: f = x0·y0 + ... + x(n-1)·y(n-1) ===\n");
    std::printf("  n | чергуючи | групами | у скільки разів\n");
    for (int n = 2; n <= 12; ++n) {
        Bdd bi(2 * n), bg(2 * n);
        const std::size_t si = bi.size(buildPairs(bi, n, true));
        const std::size_t sg = bg.size(buildPairs(bg, n, false));
        std::printf(" %2d | %8zu | %7zu | %.0f×\n", n, si, sg, double(sg) / double(si));
    }

    std::printf("\n=== кеш ===\n");
    for (const int n : {8, 32}) {
        Bdd b(2 * n + 1);
        buildAdder(b, n);
        std::printf("  суматор n=%2d: викликів apply=%lld, влучань=%lld (%.0f%%),"
                    " вузлів у таблиці=%zu\n", n, b.calls(), b.hits(),
                    100.0 * double(b.hits()) / double(b.calls()), b.tableSize());
    }
    return 0;
}
