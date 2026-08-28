#include <iostream>
#include <memory>
#include <string_view>
#include <atomic>
#include <expected>
#include <chrono>

struct TariffContext {
    uint64_t device_id;
    double kilowatt_hours;
    uint32_t zone_code;
};

struct CalculationResult {
    double total_cost;
    std::string_view tariff_name;
};

// 1. Abstraction Interface (Шов абстракції)
class ITariffCalculator {
public:
    virtual ~ITariffCalculator() = default;
    [[nodiscard]] virtual std::expected<CalculationResult, std::string> 
    calculate(const TariffContext& ctx) const noexcept = 0;
};

// 2. Legacy Implementation (Старий монолітний розрахунок)
class LegacyTariffCalculator final : public ITariffCalculator {
public:
    std::expected<CalculationResult, std::string> calculate(const TariffContext& ctx) const noexcept override {
        if (ctx.kilowatt_hours < 0) {
            return std::unexpected("Invalid negative kWh in legacy calculator");
        }
        // Застарілий алгоритм із лінійним коефіцієнтом
        double cost = ctx.kilowatt_hours * 2.45;
        if (ctx.zone_code == 2) {
            cost *= 0.5; // Нічний тариф
        }
        return CalculationResult{.total_cost = cost, .tariff_name = "Legacy-Flat-v1"};
    }
};

// 3. New Implementation (Новий модуль з підтримкою динамічних сіток)
class DynamicGridTariffCalculator final : public ITariffCalculator {
public:
    std::expected<CalculationResult, std::string> calculate(const TariffContext& ctx) const noexcept override {
        if (ctx.kilowatt_hours < 0) {
            return std::unexpected("Invalid negative kWh in new calculator");
        }
        // Новий високопродуктивний алгоритм із градацією зон
        double base_rate = (ctx.zone_code == 2) ? 1.20 : 2.80;
        double cost = ctx.kilowatt_hours * base_rate;
        if (ctx.kilowatt_hours > 500.0) {
            cost += (ctx.kilowatt_hours - 500.0) * 0.40; // Прогресивна шкала
        }
        return CalculationResult{.total_cost = cost, .tariff_name = "DynamicGrid-v2"};
    }
};

// 4. Branch Router (Динамічний перемикач на основі Feature Flag)
class TariffServiceBoundary final {
private:
    std::unique_ptr<ITariffCalculator> legacy_calc_;
    std::unique_ptr<ITariffCalculator> new_calc_;
    std::atomic<bool> use_new_engine_{false};

public:
    TariffServiceBoundary(std::unique_ptr<ITariffCalculator> legacy,
                          std::unique_ptr<ITariffCalculator> next_gen)
        : legacy_calc_(std::move(legacy)), new_calc_(std::move(next_gen)) {}

    void set_use_new_engine(bool enable) noexcept {
        use_new_engine_.store(enable, std::memory_order_release);
    }

    [[nodiscard]] std::expected<CalculationResult, std::string> 
    process_billing(const TariffContext& ctx) const noexcept {
        if (use_new_engine_.load(std::memory_order_acquire)) {
            return new_calc_->calculate(ctx);
        }
        return legacy_calc_->calculate(ctx);
    }
};

int main() {
    auto boundary = std::make_unique<TariffServiceBoundary>(
        std::make_unique<LegacyTariffCalculator>(),
        std::make_unique<DynamicGridTariffCalculator>()
    );

    TariffContext sample_ctx{.device_id = 4091, .kilowatt_hours = 620.0, .zone_code = 1};

    // Обробка legacy-двигуном
    auto res1 = boundary->process_billing(sample_ctx);
    if (res1) {
        std::cout << "Legacy Cost: " << res1->total_cost << " (" << res1->tariff_name << ")\n";
    }

    // Динамічне канарейкове перемикання на новий двигун
    boundary->set_use_new_engine(true);

    auto res2 = boundary->process_billing(sample_ctx);
    if (res2) {
        std::cout << "New Engine Cost: " << res2->total_cost << " (" << res2->tariff_name << ")\n";
    }

    return 0;
}
