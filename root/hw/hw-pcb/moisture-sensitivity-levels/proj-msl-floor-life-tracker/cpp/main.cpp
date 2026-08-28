#include <iostream>
#include <string>
#include <string_view>
#include <chrono>
#include <array>
#include <vector>
#include <optional>
#include <expected>
#include <cmath>
#include <format>

namespace tracker {

using namespace std::chrono_literals;

enum class MslLevel : uint8_t {
    Msl1 = 0, Msl2, Msl2a, Msl3, Msl4, Msl5, Msl5a, Msl6
};

enum class State : uint8_t {
    SealedInMbb,
    ExposedOnLine,
    PausedDry10Rh,
    Recovering5Rh,
    ExpiredNeedsBake,
    BakingInOven,
    ConsumedInReflow
};

enum class PkgThickness : uint8_t {
    Le1_4mm = 0,
    Le2_0mm,
    Le4_5mm
};

struct MslTraits {
    MslLevel level;
    std::string_view label;
    std::chrono::hours nominal_floor_life;
    std::chrono::hours max_short_exposure;
};

constexpr std::array<MslTraits, 8> MslTable = {{
    { MslLevel::Msl1,  "MSL 1",  std::chrono::hours::max(), std::chrono::hours::max() },
    { MslLevel::Msl2,  "MSL 2",  8760h,                     12h },
    { MslLevel::Msl2a, "MSL 2a", 672h,                      12h },
    { MslLevel::Msl3,  "MSL 3",  168h,                      12h },
    { MslLevel::Msl4,  "MSL 4",  72h,                       8h  },
    { MslLevel::Msl5,  "MSL 5",  48h,                       8h  },
    { MslLevel::Msl5a, "MSL 5a", 24h,                       8h  },
    { MslLevel::Msl6,  "MSL 6",  6h,                        0h  }
}};

constexpr std::array<std::array<std::chrono::hours, 3>, 8> BakeTable125C = {{
    { 0h,  0h,  0h  },
    { 5h,  7h,  9h  },
    { 7h,  8h,  10h },
    { 9h,  18h, 48h },
    { 11h, 21h, 48h },
    { 15h, 24h, 48h },
    { 20h, 28h, 48h },
    { 24h, 32h, 48h }
}};

[[nodiscard]] double calculate_derating(double temp_c, double rh_percent) noexcept {
    const auto p_sat = [](double t) {
        return 0.61078 * std::exp((17.27 * t) / (t + 237.3));
    };
    const double p_actual = (rh_percent / 100.0) * p_sat(temp_c);
    const double p_nominal = 0.60 * p_sat(30.0);
    return std::max(0.1, p_actual / p_nominal);
}

class ComponentReel {
public:
    ComponentReel(std::string part_number, std::string lot_id,
                  MslLevel msl, PkgThickness thickness)
        : part_number_(std::move(part_number)),
          lot_id_(std::move(lot_id)),
          msl_(msl),
          thickness_(thickness),
          state_(State::SealedInMbb),
          floor_life_remaining_(MslTable[static_cast<size_t>(msl)].nominal_floor_life) {}

    [[nodiscard]] std::expected<void, std::string_view> unpack(bool hic_10_percent_blue) noexcept {
        if (state_ != State::SealedInMbb) {
            return std::unexpected("Котушка вже була відкрита раніше.");
        }
        if (!hic_10_percent_blue) {
            state_ = State::ExpiredNeedsBake;
            floor_life_remaining_ = 0h;
            return std::unexpected("HIC індикатор сигналізує про зволоження! Потрібен Bake.");
        }
        state_ = State::ExposedOnLine;
        current_session_exposure_ = 0h;
        return {};
    }

    [[nodiscard]] std::expected<void, std::string_view> store_in_dry_cabinet(double cabinet_rh) noexcept {
        if (state_ != State::ExposedOnLine) {
            return std::unexpected("У суху шафу можна помістити лише відкриту котушку.");
        }
        if (cabinet_rh <= 5.0) {
            state_ = State::Recovering5Rh;
            recovery_credit_ = 0h;
        } else if (cabinet_rh <= 10.0) {
            state_ = State::PausedDry10Rh;
        } else {
            return std::unexpected("Вологість шафи перевищує ліміт 10% RH.");
        }
        return {};
    }

    [[nodiscard]] std::expected<void, std::string_view> start_baking(double temp_c) noexcept {
        if (state_ != State::ExpiredNeedsBake && state_ != State::ExposedOnLine) {
            return std::unexpected("Сушіння не дозволено в поточному стані.");
        }
        if (std::abs(temp_c - 125.0) < 5.0) {
            const auto needed = BakeTable125C[static_cast<size_t>(msl_)][static_cast<size_t>(thickness_)];
            if (cumulative_bake_125c_ + needed > 96h) {
                return std::unexpected("Критично: перевищення сумарного ліміту 96 год при 125 °C!");
            }
            current_bake_remaining_ = needed;
        } else if (std::abs(temp_c - 40.0) < 5.0) {
            const auto needed = BakeTable125C[static_cast<size_t>(msl_)][static_cast<size_t>(thickness_)] * 18;
            current_bake_remaining_ = needed;
        } else {
            return std::unexpected("Непідтримуваний температурний режим печі.");
        }
        state_ = State::BakingInOven;
        return {};
    }

    void tick(std::chrono::hours dt, double ambient_t, double ambient_rh) noexcept {
        switch (state_) {
            case State::ExposedOnLine: {
                const double derating = calculate_derating(ambient_t, ambient_rh);
                const auto effective_spent = std::chrono::hours(static_cast<int64_t>(std::ceil(dt.count() * derating)));
                current_session_exposure_ += dt;
                if (effective_spent >= floor_life_remaining_) {
                    floor_life_remaining_ = 0h;
                    state_ = State::ExpiredNeedsBake;
                } else {
                    floor_life_remaining_ -= effective_spent;
                }
                break;
            }
            case State::Recovering5Rh: {
                recovery_credit_ += dt;
                const auto max_short = MslTable[static_cast<size_t>(msl_)].max_short_exposure;
                const auto needed = current_session_exposure_ * 5;
                if (current_session_exposure_ <= max_short && recovery_credit_ >= needed) {
                    floor_life_remaining_ = MslTable[static_cast<size_t>(msl_)].nominal_floor_life;
                    current_session_exposure_ = 0h;
                    recovery_credit_ = 0h;
                }
                break;
            }
            case State::BakingInOven: {
                cumulative_bake_125c_ += dt;
                if (dt >= current_bake_remaining_) {
                    current_bake_remaining_ = 0h;
                    floor_life_remaining_ = MslTable[static_cast<size_t>(msl_)].nominal_floor_life;
                    current_session_exposure_ = 0h;
                    state_ = State::PausedDry10Rh;
                } else {
                    current_bake_remaining_ -= dt;
                }
                break;
            }
            default:
                break;
        }
    }

    void print_status() const {
        std::cout << std::format("Деталь: {:<16} Лот: {:<12} MSL: {:<6} Залишок Life: {:>5}h\n",
                                 part_number_, lot_id_,
                                 MslTable[static_cast<size_t>(msl_)].label,
                                 floor_life_remaining_.count());
    }

private:
    std::string part_number_;
    std::string lot_id_;
    MslLevel msl_;
    PkgThickness thickness_;
    State state_;
    
    std::chrono::hours floor_life_remaining_{0h};
    std::chrono::hours current_session_exposure_{0h};
    std::chrono::hours recovery_credit_{0h};
    std::chrono::hours cumulative_bake_125c_{0h};
    std::chrono::hours current_bake_remaining_{0h};
};

} // namespace tracker

int main() {
    using namespace std::chrono_literals;
    std::cout << "=== ДЕМОНСТРАЦІЯ РОБОТИ MSL FLOOR LIFE TRACKER (C++20) ===\n\n";
    tracker::ComponentReel reel("STM32H743IIT6", "LOT-2026-A89",
                                tracker::MslLevel::Msl3,
                                tracker::PkgThickness::Le1_4mm);
    auto unpack_res = reel.unpack(true);
    if (!unpack_res) {
        std::cerr << "Помилка розпакування: " << unpack_res.error() << '\n';
        return 1;
    }
    reel.print_status();
    
    std::cout << "\n>>> 8 годин роботи в цеху при 30 °C / 75% RH...\n";
    for (int i = 0; i < 8; ++i) {
        reel.tick(1h, 30.0, 75.0);
    }
    reel.print_status();
    
    std::cout << "\n>>> Переміщення в суху шафу RH < 5% на відновлення...\n";
    auto store_res = reel.store_in_dry_cabinet(3.0);
    if (!store_res) {
        std::cerr << "Помилка сховища: " << store_res.error() << '\n';
        return 1;
    }
    for (int i = 0; i < 40; ++i) {
        reel.tick(1h, 22.0, 3.0);
    }
    reel.print_status();
    return 0;
}
