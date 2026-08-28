#include <iostream>
#include <vector>
#include <cmath>
#include <random>
#include <memory>
#include <numeric>
#include <iomanip>
#include <stdexcept>
#include <span>

// Клас представлення булевої функції та її таблиці істинності
class TruthTable {
private:
    size_t num_vars_;
    std::vector<uint8_t> bits_;

public:
    explicit TruthTable(size_t num_vars) 
        : num_vars_(num_vars), bits_(1ULL << num_vars, 0) {}

    [[nodiscard]] size_t num_vars() const noexcept { return num_vars_; }
    [[nodiscard]] size_t size() const noexcept { return bits_.size(); }

    uint8_t operator[](size_t idx) const { return bits_.at(idx); }
    uint8_t& operator[](size_t idx) { return bits_.at(idx); }

    [[nodiscard]] std::span<const uint8_t> bits() const noexcept {
        return std::span<const uint8_t>(bits_.data(), bits_.size());
    }

    // Заповнення справді випадковою функцією R
    void generate_random(std::mt19937& rng) {
        std::uniform_int_distribution<int> dist(0, 1);
        for (auto& bit : bits_) {
            bit = static_cast<uint8_t>(dist(rng));
        }
    }

    // Заповнення псевдовипадковою функцією f_s з коротким зерном
    void generate_pseudorandom(uint32_t seed) {
        uint32_t state = seed;
        for (size_t i = 0; i < bits_.size(); ++i) {
            state = state * 1664525U + 1013904223U;
            uint8_t bit = static_cast<uint8_t>(((state ^ (i * 0x9e3779b9U)) >> 16) & 1);
            bits_[i] = bit;
        }
    }
};

// Клас аналізатора натуральних властивостей
class NaturalAnalyzer {
public:
    // Обчислення спектру Уолша-Адамара за час O(N * 2^n)
    [[nodiscard]] static int calculate_walsh_max(const TruthTable& tt) {
        const size_t n = tt.size();
        int max_walsh = 0;

        for (size_t w = 0; w < n; ++w) {
            int sum = 0;
            for (size_t x = 0; x < n; ++x) {
                size_t dot_product = std::popcount(w & x) & 1;
                int f_val = tt[x] ? -1 : 1;
                int walsh_val = dot_product ? -1 : 1;
                sum += f_val * walsh_val;
            }
            max_walsh = std::max(max_walsh, std::abs(sum));
        }
        return max_walsh;
    }

    // Натуральний розрізнювач D(f)
    [[nodiscard]] static bool is_natural_property(const TruthTable& tt) {
        int max_w = calculate_walsh_max(tt);
        double threshold = std::sqrt(static_cast<double>(tt.size())) * 2.2;
        return static_cast<double>(max_w) <= threshold;
    }
};

int main() {
    constexpr size_t N_VARS = 4;
    constexpr int NUM_TRIALS = 1000;

    std::cout << "=== Симулятор криптографічного розрізнювача Разборова-Рудіча (C++) ===\n";
    std::cout << "Кількість змінних n = " << N_VARS << ", Таблиця N = " << (1ULL << N_VARS) << " біт\n\n";

    std::random_device rd;
    std::mt19937 rng(rd());

    TruthTable tt(N_VARS);

    int random_accepted = 0;
    int prf_accepted = 0;

    // 1. Тест випадкового джерела R
    for (int i = 0; i < NUM_TRIALS; ++i) {
        tt.generate_random(rng);
        if (NaturalAnalyzer::is_natural_property(tt)) {
            random_accepted++;
        }
    }

    // 2. Тест псевдовипадкового джерела f_s
    for (int i = 0; i < NUM_TRIALS; ++i) {
        tt.generate_pseudorandom(static_cast<uint32_t>(i + 42));
        if (NaturalAnalyzer::is_natural_property(tt)) {
            prf_accepted++;
        }
    }

    double prob_random = static_cast<double>(random_accepted) / NUM_TRIALS;
    double prob_prf = static_cast<double>(prf_accepted) / NUM_TRIALS;
    double advantage = std::abs(prob_random - prob_prf);

    std::cout << std::fixed << std::setprecision(4);
    std::cout << "Pr[ D(R) = 1 ]  (Справді випадкові R)  = " << prob_random << " (Великість)\n";
    std::cout << "Pr[ D(f_G) = 1 ] (Псевдовипадкові f_G)  = " << prob_prf << " (Корисність)\n";
    std::cout << "Статистична перевага Advantage        = " << advantage << "\n\n";

    if (advantage > 0.1) {
        std::cout << "ВИСНОВОК: Розрізнювач зламав псевдовипадковий генератор!\n";
        std::cout << "Це ілюструє бар'єр Разборова-Рудіча: натуральне доведення знищує криптографію.\n";
    }

    return 0;
}
