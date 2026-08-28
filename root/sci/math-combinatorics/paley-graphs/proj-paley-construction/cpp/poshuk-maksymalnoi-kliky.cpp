#include <vector>
#include <cstdint>
#include <algorithm>
#include <bit>

class PaleyCliqueSolver {
public:
    static uint32_t find_maximum_clique(const PaleyGraph &g) {
        uint32_t words = g.words_per_row();
        std::vector<uint64_t> R(words, 0);
        std::vector<uint64_t> P(words, ~0ULL);
        std::vector<uint64_t> X(words, 0);

        if (uint32_t rem = g.order() % 64; rem != 0) {
            P.back() = (1ULL << rem) - 1;
        }

        uint32_t max_clique = 0;
        solve(g, R, P, X, max_clique);
        return max_clique;
    }

private:
    static void solve(const PaleyGraph &g,
                      std::vector<uint64_t> &R,
                      std::vector<uint64_t> &P,
                      std::vector<uint64_t> &X,
                      uint32_t &max_clique) {
        bool p_empty = std::all_of(P.begin(), P.end(), [](uint64_t v) { return v == 0; });
        bool x_empty = std::all_of(X.begin(), X.end(), [](uint64_t v) { return v == 0; });

        if (p_empty && x_empty) {
            uint32_t cur_size = 0;
            for (uint64_t word : R) cur_size += static_cast<uint32_t>(std::popcount(word));
            max_clique = std::max(max_clique, cur_size);
            return;
        }

        if (p_empty) return;

        // Пошук півота у P | X
        uint32_t words = g.words_per_row();
        uint32_t pivot = 0;
        for (uint32_t w = 0; w < words; ++w) {
            if (uint64_t union_px = P[w] | X[w]; union_px != 0) {
                pivot = w * 64 + static_cast<uint32_t>(std::countr_zero(union_px));
                break;
            }
        }

        auto pivot_adj = g.row_bitset(pivot);
        std::vector<uint64_t> candidates(words);
        for (uint32_t w = 0; w < words; ++w) {
            candidates[w] = P[w] & ~pivot_adj[w];
        }

        for (uint32_t w = 0; w < words; ++w) {
            while (candidates[w] != 0) {
                uint32_t bit = static_cast<uint32_t>(std::countr_zero(candidates[w]));
                uint32_t v = w * 64 + bit;
                candidates[w] &= ~(1ULL << bit);

                auto v_adj = g.row_bitset(v);
                std::vector<uint64_t> R_next = R;
                std::vector<uint64_t> P_next(words);
                std::vector<uint64_t> X_next(words);

                for (uint32_t k = 0; k < words; ++k) {
                    P_next[k] = P[k] & v_adj[k];
                    X_next[k] = X[k] & v_adj[k];
                }
                R_next[v / 64] |= (1ULL << (v % 64));

                solve(g, R_next, P_next, X_next, max_clique);

                P[v / 64] &= ~(1ULL << (v % 64));
                X[v / 64] |= (1ULL << (v % 64));
            }
        }
    }
};
