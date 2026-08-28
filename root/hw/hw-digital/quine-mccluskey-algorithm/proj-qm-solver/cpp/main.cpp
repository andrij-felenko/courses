#include <iostream>
#include <vector>
#include <string>
#include <algorithm>
#include <cstdint>
#include <bit>

struct Term {
    uint32_t bits{0};  // Значення визначених бітів
    uint32_t mask{0};  // Маска прочерків '-' (1 де змінна випала)
    bool used{false};  // Чи склеївся терм у наступне покоління

    bool operator==(const Term& other) const noexcept {
        return bits == other.bits && mask == other.mask;
    }

    [[nodiscard]] bool covers(uint32_t minterm) const noexcept {
        return (minterm & ~mask) == (bits & ~mask);
    }

    [[nodiscard]] std::string to_string(int nvars) const {
        std::string s;
        s.reserve(nvars);
        for (int i = nvars - 1; i >= 0; --i) {
            if (mask & (1U << i)) {
                s.push_back('-');
            } else if (bits & (1U << i)) {
                s.push_back('1');
            } else {
                s.push_back('0');
            }
        }
        return s;
    }
};

class QuineMcCluskeySolver {
public:
    QuineMcCluskeySolver(int nvars, std::vector<uint32_t> minterms, std::vector<uint32_t> dontcares = {})
        : nvars_(nvars), minterms_(std::move(minterms)), dontcares_(std::move(dontcares)) {}

    [[nodiscard]] std::vector<Term> solve() {
        std::vector<Term> current;
        current.reserve(minterms_.size() + dontcares_.size());

        for (uint32_t m : minterms_) current.push_back(Term{.bits = m, .mask = 0, .used = false});
        for (uint32_t d : dontcares_) current.push_back(Term{.bits = d, .mask = 0, .used = false});

        std::vector<Term> prime_implicants;

        // Фаза 1: Каскадне склеювання поколінь
        while (!current.empty()) {
            std::vector<Term> next_generation;

            for (size_t i = 0; i < current.size(); ++i) {
                for (size_t j = i + 1; j < current.size(); ++j) {
                    if (current[i].mask != current[j].mask) continue;

                    uint32_t diff = (current[i].bits ^ current[j].bits) & ~current[i].mask;
                    if (diff != 0 && (diff & (diff - 1)) == 0) {
                        current[i].used = true;
                        current[j].used = true;

                        Term merged{
                            .bits = current[i].bits & ~diff,
                            .mask = current[i].mask | diff,
                            .used = false
                        };

                        if (std::find(next_generation.begin(), next_generation.end(), merged) == next_generation.end()) {
                            next_generation.push_back(merged);
                        }
                    }
                }
            }

            for (const auto& term : current) {
                if (!term.used) {
                    if (std::find(prime_implicants.begin(), prime_implicants.end(), term) == prime_implicants.end()) {
                        prime_implicants.push_back(term);
                    }
                }
            }

            current = std::move(next_generation);
        }

        // Фаза 2: Вибір покриття
        return select_minimal_cover(prime_implicants);
    }

private:
    int nvars_;
    std::vector<uint32_t> minterms_;
    std::vector<uint32_t> dontcares_;

    [[nodiscard]] std::vector<Term> select_minimal_cover(const std::vector<Term>& primes) const {
        if (primes.empty() || minterms_.empty()) return {};

        std::vector<std::vector<bool>> chart(primes.size(), std::vector<bool>(minterms_.size(), false));
        for (size_t p = 0; p < primes.size(); ++p) {
            for (size_t m = 0; m < minterms_.size(); ++m) {
                chart[p][m] = primes[p].covers(minterms_[m]);
            }
        }

        std::vector<bool> covered_minterms(minterms_.size(), false);
        std::vector<bool> chosen_primes(primes.size(), false);

        // 1. Пошук істотних простих імплікантів (EPI)
        for (size_t m = 0; m < minterms_.size(); ++m) {
            int count = 0;
            int last_p = -1;
            for (size_t p = 0; p < primes.size(); ++p) {
                if (chart[p][m]) {
                    count++;
                    last_p = static_cast<int>(p);
                }
            }
            if (count == 1 && last_p != -1 && !chosen_primes[last_p]) {
                chosen_primes[last_p] = true;
                for (size_t j = 0; j < minterms_.size(); ++j) {
                    if (chart[last_p][j]) covered_minterms[j] = true;
                }
            }
        }

        // 2. Жадібний вибір для залишку стовпців
        while (true) {
            if (std::all_of(covered_minterms.begin(), covered_minterms.end(), [](bool v) { return v; })) {
                break;
            }

            int best_p = -1;
            int max_new_cover = 0;

            for (size_t p = 0; p < primes.size(); ++p) {
                if (chosen_primes[p]) continue;
                int new_cover = 0;
                for (size_t m = 0; m < minterms_.size(); ++m) {
                    if (!covered_minterms[m] && chart[p][m]) {
                        new_cover++;
                    }
                }
                if (new_cover > max_new_cover) {
                    max_new_cover = new_cover;
                    best_p = static_cast<int>(p);
                }
            }

            if (best_p == -1 || max_new_cover == 0) break;

            chosen_primes[best_p] = true;
            for (size_t m = 0; m < minterms_.size(); ++m) {
                if (chart[best_p][m]) covered_minterms[m] = true;
            }
        }

        std::vector<Term> result;
        for (size_t p = 0; p < primes.size(); ++p) {
            if (chosen_primes[p]) result.push_back(primes[p]);
        }
        return result;
    }
};

int main() {
    // Приклад F(A,B,C,D) = Σ m(0, 1, 2, 5, 6, 7, 8, 9, 10, 14)
    QuineMcCluskeySolver solver(4, {0, 1, 2, 5, 6, 7, 8, 9, 10, 14});
    auto result = solver.solve();

    std::cout << "Minimal SOP terms:\n";
    for (size_t i = 0; i < result.size(); ++i) {
        if (i > 0) std::cout << " + ";
        std::cout << result[i].to_string(4);
    }
    std::cout << '\n';
    return 0;
}
