#include <iostream>
#include <cmath>
#include <array>
#include <span>
#include <expected>
#include <algorithm>
#include <numeric>
#include <string_view>

enum class DecisionStatus {
    Accepted,
    RejectOOD,
    RejectAmbiguous
};

struct SelectiveConfig {
    float temperature{1.0f};
    float energy_threshold{-5.0f};
    float entropy_threshold{0.40f};
};

struct SelectiveOutput {
    int predicted_class{-1};
    float confidence{0.0f};
    float free_energy{0.0f};
    float normalized_entropy{1.0f};
    DecisionStatus status{DecisionStatus::RejectOOD};
};

template <std::size_t MaxClasses = 16>
class SelectiveClassifierEngine {
public:
    static constexpr float kEpsilon = 1e-8f;

    explicit constexpr SelectiveClassifierEngine(SelectiveConfig cfg) noexcept 
        : cfg_(cfg) {}

    [[nodiscard]] std::expected<SelectiveOutput, std::string_view> evaluate(
        std::span<const float> logits
    ) const noexcept {
        if (logits.size() < 2 || logits.size() > MaxClasses) {
            return std::unexpected("Кількість класів має бути в межах [2, MaxClasses]");
        }
        if (cfg_.temperature <= kEpsilon) {
            return std::unexpected("Температура повинна бути строго додатною");
        }
        if (cfg_.entropy_threshold < 0.0f || cfg_.entropy_threshold > 1.0f) {
            return std::unexpected("Поріг ентропії має бути в діапазоні [0.0, 1.0]");
        }

        SelectiveOutput out{};
        const auto num_classes = logits.size();

        // 1. Пошук максимального логіта для чисельної стабільності
        const auto max_it = std::max_element(logits.begin(), logits.end());
        const float max_logit = *max_it;
        out.predicted_class = static_cast<int>(std::distance(logits.begin(), max_it));

        // 2. Обчислення зсунутих експонент
        std::array<float, MaxClasses> exp_scaled{};
        float sum_exp = 0.0f;
        const float inv_temp = 1.0f / cfg_.temperature;

        for (std::size_t i = 0; i < num_classes; ++i) {
            exp_scaled[i] = std::exp((logits[i] - max_logit) * inv_temp);
            sum_exp += exp_scaled[i];
        }

        if (sum_exp <= kEpsilon) {
            out.status = DecisionStatus::RejectOOD;
            return out;
        }

        // 3. Вільна енергія Гельмгольца
        out.free_energy = -max_logit - (cfg_.temperature * std::log(sum_exp));

        // Гейт 1: Фільтрація OOD-аномалій за вільною енергією
        if (out.free_energy > cfg_.energy_threshold) {
            out.status = DecisionStatus::RejectOOD;
            return out;
        }

        // 4. Розрахунок Softmax та ентропії Шеннона
        float entropy = 0.0f;
        const float inv_sum = 1.0f / sum_exp;

        for (std::size_t i = 0; i < num_classes; ++i) {
            const float p = exp_scaled[i] * inv_sum;
            if (p > kEpsilon) {
                entropy -= p * std::log(p);
            }
        }

        const float max_entropy = std::log(static_cast<float>(num_classes));
        out.normalized_entropy = (max_entropy > kEpsilon) ? (entropy / max_entropy) : 0.0f;
        out.confidence = exp_scaled[static_cast<std::size_t>(out.predicted_class)] * inv_sum;

        // Гейт 2: Фільтрація алеаторної неоднозначності за ентропією
        if (out.normalized_entropy > cfg_.entropy_threshold) {
            out.status = DecisionStatus::RejectAmbiguous;
            return out;
        }

        out.status = DecisionStatus::Accepted;
        return out;
    }

private:
    SelectiveConfig cfg_;
};

// ── Тестовий драйвер ──────────────────────────────────────────────────────
void run_cpp_test(
    std::string_view name,
    std::span<const float> logits,
    const SelectiveClassifierEngine<16>& engine,
    DecisionStatus expected
) {
    auto res = engine.evaluate(logits);
    if (!res) {
        std::cout << "[FAIL] " << name << " Помилка виконання: " << res.error() << "\n";
        return;
    }

    const bool passed = (res->status == expected);
    std::cout << "[" << (passed ? "PASS" : "FAIL") << "] Тест: " << name << "\n"
              << "  -> Статус: " << static_cast<int>(res->status)
              << " (очікувався: " << static_cast<int>(expected) << ")"
              << ", Клас: " << res->predicted_class
              << ", Впевненість: " << res->confidence
              << ", Енергія: " << res->free_energy
              << ", Ентропія: " << res->normalized_entropy << "\n";
}

int main() {
    SelectiveConfig cfg{
        .temperature = 1.0f,
        .energy_threshold = -5.0f,
        .entropy_threshold = 0.40f
    };
    SelectiveClassifierEngine<16> classifier(cfg);

    std::cout << "=== Запуск тестів вибіркового класифікатора (C++20) ===\n";

    // 1. In-Distribution
    constexpr std::array<float, 4> id_logits = { 8.5f, 1.2f, 0.4f, -0.8f };
    run_cpp_test("In-Distribution (чітке розпізнавання)", id_logits, classifier, DecisionStatus::Accepted);

    // 2. Алеаторний шум
    constexpr std::array<float, 4> noisy_logits = { 0.2f, 5.0f, 4.9f, 0.1f };
    run_cpp_test("Ambiguous Noise (висока ентропія на межі)", noisy_logits, classifier, DecisionStatus::RejectAmbiguous);

    // 3. OOD шум
    constexpr std::array<float, 4> ood_low_logits = { 0.1f, -0.2f, 0.05f, -0.1f };
    run_cpp_test("OOD Background Noise (висока вільна енергія)", ood_low_logits, classifier, DecisionStatus::RejectOOD);

    // 4. Слабкий OOD
    constexpr std::array<float, 4> ood_weak_logits = { 2.1f, -1.0f, -0.5f, -2.0f };
    run_cpp_test("OOD Weak Confidence", ood_weak_logits, classifier, DecisionStatus::RejectOOD);

    return 0;
}
