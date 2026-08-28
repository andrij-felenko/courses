// szilard_sim.cpp - Об'єктно-орієнтована симуляція двигуна Сіларда на C++20
#include <iostream>
#include <cmath>
#include <random>
#include <numbers>
#include <iomanip>
#include <expected>
#include <string_view>

namespace thermo {

constexpr double kBoltzmann = 1.380649e-23;       // Дж/К
constexpr double kElemCharge = 1.602176634e-19;   // Кл
constexpr double kLn2 = std::numbers::ln2;

enum class Position : uint8_t { Left = 0, Right = 1 };

struct CycleResult {
    double work_extracted_J;
    double heat_absorbed_J;
    double heat_erased_J;
    double entropy_net_JK;
};

class SzilardEngine {
public:
    explicit SzilardEngine(double temperature = 300.0)
        : temp_(temperature), rng_(std::random_device{}()), dist_(0, 1) {}

    // Виконання одного термодинамічного циклу
    [[nodiscard]] CycleResult step() {
        // 1. Вставляння перегородки та вимірювання
        const Position pos = (dist_(rng_) == 0) ? Position::Left : Position::Right;
        const uint8_t memory_bit = static_cast<uint8_t>(pos);

        // 2. Ізотермічне розширення (вилучення роботи)
        const double work = kBoltzmann * temp_ * kLn2;
        const double q_in = work;

        // 3. Стирання біта пам'яті (Ландауер)
        const double q_erasure = kBoltzmann * temp_ * kLn2;
        const double ds_bath = - q_in / temp_;
        const double ds_erasure = q_erasure / temp_;

        (void)memory_bit;

        return CycleResult{
            .work_extracted_J = work,
            .heat_absorbed_J = q_in,
            .heat_erased_J = q_erasure,
            .entropy_net_JK = ds_bath + ds_erasure
        };
    }

    [[nodiscard]] double temperature() const noexcept { return temp_; }

private:
    double temp_;
    std::mt19937 rng_;
    std::uniform_int_distribution<int> dist_;
};

} // namespace thermo

int main() {
    constexpr std::size_t kCycles = 100'000;
    thermo::SzilardEngine engine(300.0);

    double total_work = 0.0;
    double total_erasure = 0.0;
    double total_ds = 0.0;

    for (std::size_t i = 0; i < kCycles; ++i) {
        auto res = engine.step();
        total_work += res.work_extracted_J;
        total_erasure += res.heat_erased_J;
        total_ds += res.entropy_net_JK;
    }

    const double avg_work_meV = (total_work / kCycles) / thermo::kElemCharge * 1000.0;
    const double avg_erasure_meV = (total_erasure / kCycles) / thermo::kElemCharge * 1000.0;
    const double avg_ds = total_ds / kCycles;

    std::cout << std::fixed << std::setprecision(4);
    std::cout << "=== Симуляція двигуна Сіларда (C++20) [" << kCycles << " циклів] ===\n";
    std::cout << "Середня вилучена робота за цикл : " << avg_work_meV << " meV\n";
    std::cout << "Середнє тепло стирання Ландауера: " << avg_erasure_meV << " meV\n";
    std::cout << "Сумарна зміна ентропії за цикл   : " << std::scientific << avg_ds << " Дж/К\n";

    return 0;
}
