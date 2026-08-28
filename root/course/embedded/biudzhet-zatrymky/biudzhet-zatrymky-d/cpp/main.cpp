#include <iostream>
#include <string_view>
#include <array>
#include <span>
#include <chrono>
#include <numeric>
#include <iomanip>

namespace latency {

using namespace std::chrono_literals;
using FloatDurationMs = std::chrono::duration<float, std::milli>;

enum class StageType {
    Deterministic,
    Quantization,
    Stochastic
};

struct Stage {
    std::string_view name;
    StageType type{StageType::Deterministic};
    FloatDurationMs min{0.0f};
    FloatDurationMs typ{0.0f};
    FloatDurationMs max{0.0f};
};

struct BudgetSummary {
    FloatDurationMs min{0.0f};
    FloatDurationMs typ{0.0f};
    FloatDurationMs max{0.0f};
    FloatDurationMs jitter{0.0f};
};

template <std::size_t MaxStages = 16>
class Pipeline {
public:
    constexpr bool add_stage(std::string_view name, StageType type,
                             FloatDurationMs min, FloatDurationMs typ, FloatDurationMs max) noexcept {
        if (size_ >= MaxStages) return false;
        stages_[size_++] = Stage{name, type, min, typ, max};
        return true;
    }

    [[nodiscard]] constexpr BudgetSummary calculate() const noexcept {
        BudgetSummary summary{};
        for (std::size_t i = 0; i < size_; ++i) {
            summary.min += stages_[i].min;
            summary.typ += stages_[i].typ;
            summary.max += stages_[i].max;
        }
        summary.jitter = summary.max - summary.min;
        return summary;
    }

    [[nodiscard]] constexpr std::span<const Stage> stages() const noexcept {
        return std::span<const Stage>(stages_.data(), size_);
    }

    void print_report(std::string_view title) const {
        const auto b = calculate();
        std::cout << "====================================================\n";
        std::cout << " БЮДЖЕТ ЗАРИМКИ: " << title << "\n";
        std::cout << "----------------------------------------------------\n";
        std::cout << std::left << std::setw(24) << "Ланка тракту" << " | "
                  << std::setw(8) << "Min(мс)" << " | "
                  << std::setw(8) << "Typ(мс)" << " | "
                  << std::setw(8) << "Max(мс)" << "\n";
        std::cout << "----------------------------------------------------\n";

        for (const auto& stage : stages()) {
            std::cout << std::left << std::setw(24) << stage.name << " | "
                      << std::fixed << std::setprecision(2)
                      << std::setw(8) << stage.min.count() << " | "
                      << std::setw(8) << stage.typ.count() << " | "
                      << std::setw(8) << stage.max.count() << "\n";
        }
        std::cout << "----------------------------------------------------\n";
        std::cout << std::left << std::setw(24) << "РАЗОМ:" << " | "
                  << std::setw(8) << b.min.count() << " | "
                  << std::setw(8) << b.typ.count() << " | "
                  << std::setw(8) << b.max.count() << "\n";
        std::cout << " ДЖИТЕР ТРАКТУ:          | " << b.jitter.count() << " мс\n";
        std::cout << "====================================================\n\n";
    }

private:
    std::array<Stage, MaxStages> stages_{};
    std::size_t size_{0};
};

} // namespace latency
