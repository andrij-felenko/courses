#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <array>
#include <cmath>
#include <algorithm>
#include <numeric>
#include <expected>
#include <format>
#include <span>

namespace reflow {

enum class ProfileStage : uint8_t {
    Standby,
    Preheat,
    Soak,
    Reflow,
    Cooling,
    Finished,
    ErrorAbort
};

enum class SensorFault : uint8_t {
    None         = 0x00,
    OpenCircuit  = 0x01,
    OverVoltage  = 0x02,
    UnderVoltage = 0x04,
    CjcOutOfRange= 0x08
};

[[nodiscard]] constexpr std::string_view stage_name(ProfileStage st) noexcept {
    switch (st) {
        case ProfileStage::Standby:    return "STANDBY";
        case ProfileStage::Preheat:    return "PREHEAT";
        case ProfileStage::Soak:       return "SOAK";
        case ProfileStage::Reflow:     return "REFLOW";
        case ProfileStage::Cooling:    return "COOLING";
        case ProfileStage::Finished:   return "FINISHED";
        case ProfileStage::ErrorAbort: return "ERROR_ABORT";
    }
    return "UNKNOWN";
}

struct ProcessLimits {
    double liquidus_temp{217.0};
    double target_peak_temp{245.0};
    double min_peak_temp{238.0};
    double max_peak_temp{252.0};
    double target_tal_sec{65.0};
    double min_tal_sec{45.0};
    double max_tal_sec{90.0};
    double target_soak_sec{90.0};
    double min_soak_sec{60.0};
    double max_soak_sec{120.0};
    double max_preheat_ramp{3.0};
    double max_cooling_ramp{-4.0};
    double max_delta_t_reflow{8.0};
};

class ThermocoupleChannel {
public:
    explicit ThermocoupleChannel(std::string name) noexcept
        : name_{std::move(name)} 
    {
        history_.fill(25.0);
    }

    void update(double raw_temp, double dt, double current_time, double liquidus_temp) noexcept {
        if (!is_active_) return;

        // Перевірка на обрив термопари
        if (raw_temp > 400.0 || raw_temp < -20.0 || std::isnan(raw_temp)) {
            fault_ = SensorFault::OpenCircuit;
            is_active_ = false;
            return;
        }

        raw_temp_ = raw_temp;
        filtered_temp_ = ema_alpha_ * raw_temp + (1.0 - ema_alpha_) * filtered_temp_;
        
        const double oldest = history_[history_idx_];
        history_[history_idx_] = filtered_temp_;
        history_idx_ = (history_idx_ + 1) % history_.size();
        
        ramp_rate_ = (filtered_temp_ - oldest) / (history_.size() * dt);
        peak_temp_ = std::max(peak_temp_, filtered_temp_);

        if (filtered_temp_ >= liquidus_temp) {
            tal_seconds_ += dt;
            
            // Дифузійне зростання Cu6Sn5 за Арреніусом
            constexpr double R = 8.314462;
            constexpr double Q = 72500.0;
            constexpr double K0 = 1.2e-4;
            const double temp_k = filtered_temp_ + 273.15;
            const double k_rate = K0 * std::exp(-Q / (R * temp_k));
            imc_thickness_um_ += (k_rate * dt * 1e6) / (2.0 * std::max(imc_thickness_um_, 0.1));
        }
    }

    void start_soak(double time_sec) noexcept {
        soak_start_sec_ = time_sec;
    }

    void stop_soak(double time_sec) noexcept {
        soak_duration_sec_ = time_sec - soak_start_sec_;
    }

    [[nodiscard]] double calculate_pwi(const ProcessLimits& lim) noexcept {
        if (!is_active_) return 0.0;

        auto single_pwi = [](double val, double target, double low, double high) noexcept -> double {
            const double half = 0.5 * (high - low);
            return (half > 0.0001) ? (std::abs(val - target) / half * 100.0) : 0.0;
        };

        pwi_peak_ = single_pwi(peak_temp_, lim.target_peak_temp, lim.min_peak_temp, lim.max_peak_temp);
        pwi_tal_  = single_pwi(tal_seconds_, lim.target_tal_sec, lim.min_tal_sec, lim.max_tal_sec);
        pwi_soak_ = single_pwi(soak_duration_sec_, lim.target_soak_sec, lim.min_soak_sec, lim.max_soak_sec);

        return std::max({pwi_peak_, pwi_tal_, pwi_soak_});
    }

    [[nodiscard]] std::string_view name() const noexcept { return name_; }
    [[nodiscard]] double filtered_temperature() const noexcept { return filtered_temp_; }
    [[nodiscard]] double peak_temperature() const noexcept { return peak_temp_; }
    [[nodiscard]] double tal_duration() const noexcept { return tal_seconds_; }
    [[nodiscard]] double soak_duration() const noexcept { return soak_duration_sec_; }
    [[nodiscard]] double ramp_rate() const noexcept { return ramp_rate_; }
    [[nodiscard]] double imc_thickness() const noexcept { return imc_thickness_um_; }
    [[nodiscard]] bool is_active() const noexcept { return is_active_; }
    [[nodiscard]] SensorFault fault() const noexcept { return fault_; }

private:
    std::string name_;
    double raw_temp_{25.0};
    double filtered_temp_{25.0};
    double peak_temp_{25.0};
    double ramp_rate_{0.0};
    double tal_seconds_{0.0};
    double soak_start_sec_{0.0};
    double soak_duration_sec_{0.0};
    double imc_thickness_um_{0.5};
    double pwi_peak_{0.0};
    double pwi_tal_{0.0};
    double pwi_soak_{0.0};
    bool is_active_{true};
    SensorFault fault_{SensorFault::None};
    
    static constexpr double ema_alpha_{0.20};
    std::array<double, 5> history_{};
    size_t history_idx_{0};
};

class ReflowProfilerEngine {
public:
    explicit ReflowProfilerEngine(ProcessLimits limits = {}) noexcept
        : limits_{limits} {}

    void add_channel(std::string name) {
        channels_.emplace_back(std::move(name));
    }

    auto process_sample(std::span<const double> raw_values, double dt) noexcept 
        -> std::expected<ProfileStage, std::string_view> 
    {
        if (raw_values.size() != channels_.size()) {
            return std::unexpected{"Channel count mismatch"};
        }
        if (dt <= 0.0) {
            return std::unexpected{"dt must be positive non-zero"};
        }

        session_time_sec_ += dt;
        double min_t = 10000.0;
        double max_t = -1000.0;
        double sum_t = 0.0;
        size_t active_count = 0;

        for (size_t i = 0; i < channels_.size(); ++i) {
            channels_[i].update(raw_values[i], dt, session_time_sec_, limits_.liquidus_temp);
            if (channels_[i].is_active()) {
                const double t = channels_[i].filtered_temperature();
                min_t = std::min(min_t, t);
                max_t = std::max(max_t, t);
                sum_t += t;
                active_count++;
            }
        }

        if (active_count == 0) {
            stage_ = ProfileStage::ErrorAbort;
            return std::unexpected{"All channels disconnected or faulty"};
        }

        const double avg_t = sum_t / active_count;
        delta_t_current_ = max_t - min_t;

        if (avg_t >= limits_.liquidus_temp) {
            delta_t_max_reflow_ = std::max(delta_t_max_reflow_, delta_t_current_);
        }

        // Автомат стадій
        switch (stage_) {
            case ProfileStage::Standby:
                if (avg_t >= 35.0) {
                    stage_ = ProfileStage::Preheat;
                }
                break;
            case ProfileStage::Preheat:
                if (avg_t >= 150.0) {
                    stage_ = ProfileStage::Soak;
                    for (auto& ch : channels_) ch.start_soak(session_time_sec_);
                }
                break;
            case ProfileStage::Soak:
                if (avg_t >= 200.0) {
                    stage_ = ProfileStage::Reflow;
                    for (auto& ch : channels_) ch.stop_soak(session_time_sec_);
                }
                break;
            case ProfileStage::Reflow:
                if (avg_t < limits_.liquidus_temp && max_t > limits_.liquidus_temp) {
                    stage_ = ProfileStage::Cooling;
                }
                break;
            case ProfileStage::Cooling:
                if (max_t <= 45.0) {
                    stage_ = ProfileStage::Finished;
                }
                break;
            case ProfileStage::Finished:
            case ProfileStage::ErrorAbort:
                break;
        }

        // Розрахунок PWI
        overall_pwi_ = 0.0;
        for (auto& ch : channels_) {
            overall_pwi_ = std::max(overall_pwi_, ch.calculate_pwi(limits_));
        }

        return stage_;
    }

    void print_report() const {
        std::cout << "\n====================================================================\n";
        std::cout << "        ЗВІТ ВЕРИФІКАЦІЇ ТЕРМОПРОФІЛЮ ОПЛАВЛЕННЯ (C++20)            \n";
        std::cout << "====================================================================\n";
        std::cout << std::format("Загальний час сесії:      {:.1f} с\n", session_time_sec_);
        std::cout << std::format("Кількість каналів:        {}\n", channels_.size());
        std::cout << std::format("Максимальний Delta T:     {:.2f} °C (Ліміт: {:.1f} °C) -> {}\n",
                                  delta_t_max_reflow_, limits_.max_delta_t_reflow,
                                  (delta_t_max_reflow_ <= limits_.max_delta_t_reflow) ? "PASS" : "FAIL");
        std::cout << std::format("Підсумковий індекс PWI:   {:.1f}% -> {}\n",
                                  overall_pwi_,
                                  (overall_pwi_ < 50.0) ? "EXCELLENT (<50%)" :
                                  (overall_pwi_ < 100.0) ? "PASS (<100%)" : "REJECTED (>=100%)");
        std::cout << "--------------------------------------------------------------------\n";
        std::cout << std::format("{:<10} | {:<10} | {:<10} | {:<10} | {:<10}\n",
                                  "Канал", "T_peak", "TAL(с)", "Soak(с)", "IMC(мкм)");
        std::cout << "--------------------------------------------------------------------\n";
        for (const auto& ch : channels_) {
            if (ch.is_active()) {
                std::cout << std::format("{:<10} | {:>7.1f} °C | {:>7.1f} с | {:>7.1f} с | {:>7.2f} мкм\n",
                                          ch.name(), ch.peak_temperature(), ch.tal_duration(),
                                          ch.soak_duration(), ch.imc_thickness());
            } else {
                std::cout << std::format("{:<10} | FAULT / DISCONNECTED\n", ch.name());
            }
        }
        std::cout << "====================================================================\n\n";
    }

    [[nodiscard]] double overall_pwi() const noexcept { return overall_pwi_; }
    [[nodiscard]] ProfileStage stage() const noexcept { return stage_; }

private:
    ProcessLimits limits_;
    std::vector<ThermocoupleChannel> channels_;
    ProfileStage stage_{ProfileStage::Standby};
    double session_time_sec_{0.0};
    double delta_t_current_{0.0};
    double delta_t_max_reflow_{0.0};
    double overall_pwi_{0.0};
};

} // namespace reflow
