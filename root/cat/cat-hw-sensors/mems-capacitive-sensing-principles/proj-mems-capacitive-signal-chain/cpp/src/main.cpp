#include "mems_capacitive_driver.hpp"
#include <cmath>
#include <iomanip>
#include <iostream>
#include <vector>

/**
 * @brief Симульований апаратний адаптер для демонстрації роботи MEMS-вимірювання.
 *
 * Симулює фізичний зсув MEMS-обкладок, наявність паразитичної ємності (baseline drift),
 * високочастотного носія та шумів АЦП.
 */
class SimulatedMemsHardwareAdapter : public mems::IMemsHardwareAdapter {
public:
    SimulatedMemsHardwareAdapter() = default;

    bool configure_excitation(uint32_t frequency_hz) override {
        excitation_freq_ = frequency_hz;
        excitation_enabled_ = true;
        sample_counter_ = 0;
        return true;
    }

    bool set_excitation_enabled(bool enable) override {
        excitation_enabled_ = enable;
        return true;
    }

    bool set_dac_offset_voltage(float volts) override {
        dac_offset_v_ = volts;
        return true;
    }

    float read_adc_voltage() override {
        if (!excitation_enabled_) {
            return 0.0f;
        }

        // Чергуємо фазу для кожної вибірки (імітація меандру збудження 0° / 180°)
        current_phase_ = (sample_counter_ % 2 == 0) ? mems::ExcitationPhase::Phase0
                                                    : mems::ExcitationPhase::Phase180;
        sample_counter_++;

        float phase_sign = (current_phase_ == mems::ExcitationPhase::Phase0) ? 1.0f : -1.0f;

        // Вплив корисного зсуву обкладок MEMS
        float useful_signal = physical_displacement_um_ * 0.15f; // 0.15 В / мкм

        // Постійна паразитична ємність та температурний дрейф
        float total_displacement_signal = useful_signal + parasitic_baseline_v_ - dac_offset_v_;

        // Модуляція високою частотою носія + легкий білий шум
        float simulated_noise = 0.005f * std::sin(static_cast<float>(sample_counter_) * 0.5f);
        float adc_voltage = total_displacement_signal * phase_sign + simulated_noise;

        return adc_voltage;
    }

    mems::ExcitationPhase current_excitation_phase() const override {
        return current_phase_;
    }

    // Симуляційні методи для виклику з тесту
    void set_physical_displacement(float um) {
        physical_displacement_um_ = um;
    }

    void set_parasitic_baseline(float volts) {
        parasitic_baseline_v_ = volts;
    }

private:
    uint32_t excitation_freq_{100000};
    bool excitation_enabled_{false};
    mems::ExcitationPhase current_phase_{mems::ExcitationPhase::Phase0};
    uint64_t sample_counter_{0};

    float dac_offset_v_{0.0f};
    float parasitic_baseline_v_{0.25f}; // Симульований початковий дрейф 0.25 В
    float physical_displacement_um_{0.0f};
};

int main() {
    std::cout << "=========================================================\n";
    std::cout << " MEMS Capacitive Sensing & Phase Demodulation Driver Demo\n";
    std::cout << "=========================================================\n\n";

    SimulatedMemsHardwareAdapter hw_adapter;

    // Налаштування параметрів вимірювального тракту
    mems::CapacitiveSensingConfig config;
    config.excitation_freq_hz = 100000;       // 100 кГц несуча
    config.calibration_samples = 128;          // 128 вибірок для нульового baseline
    config.lpf_alpha = 0.1f;                   // ФНЧ згладжування
    config.sensitivity_pf_per_volt = 2.0f;     // 2 pF / В
    config.scale_factor_um_per_pf = 1.5f;      // 1.5 мкм / pF

    mems::MemsCapacitiveDriver driver(hw_adapter, config);

    std::cout << "[1] Ініціалізація периферії мікроконтролера...\n";
    if (!driver.initialize()) {
        std::cerr << "Помилка: не вдалося ініціалізувати MEMS-драйвер!\n";
        return 1;
    }
    std::cout << "   Успішно ініціалізовано. Частота збудження: " << config.excitation_freq_hz << " Гц.\n\n";

    // Задаємо паразитичний зміщення ємності монтажу у стані спокою
    hw_adapter.set_parasitic_baseline(0.25f);
    hw_adapter.set_physical_displacement(0.0f); // MEMS у стані спокою

    std::cout << "[2] Автоматичне калібрування baseline (нівелювання паразитичної ємності)...\n";
    mems::CalibrationStatus cal_status = driver.calibrate_baseline();

    if (cal_status != mems::CalibrationStatus::Success) {
        std::cerr << "Помилка калібрування! Код статусу: "
                  << static_cast<int>(cal_status) << "\n";
        return 1;
    }

    std::cout << "   Калібрування завершено успішно!\n";
    std::cout << "   Визначений baseline offset: " << driver.get_baseline_offset_v() << " В\n\n";

    std::cout << "[3] Початок обробки потоку вимірювань (імітація мікромеханічного зсуву)...\n";
    std::cout << std::fixed << std::setprecision(4);
    std::cout << "-----------------------------------------------------------------------------------\n";
    std::cout << "Крок | Заданий зсув | ADC Raw (В) | Demod (В) | Filtered (В) | Delta C (pF) | Displacement (мкм)\n";
    std::cout << "-----------------------------------------------------------------------------------\n";

    // Сценарій тестування: механічний зсув MEMS-обкладок від 0 до 2 мкм і назад
    std::vector<float> displacement_steps = {0.0f, 0.5f, 1.0f, 1.5f, 2.0f, 1.5f, 0.8f, 0.0f};

    std::size_t step_index = 0;
    for (float target_disp : displacement_steps) {
        hw_adapter.set_physical_displacement(target_disp);

        // Пропускаємо кілька тактів для стабілізації ФНЧ
        for (int i = 0; i < 5; ++i) {
            driver.process_sample();
        }

        std::cout << std::setw(4) << ++step_index << " | "
                  << std::setw(12) << target_disp << " | "
                  << std::setw(11) << driver.get_last_raw_voltage() << " | "
                  << std::setw(9) << driver.get_last_demodulated_voltage() << " | "
                  << std::setw(12) << driver.get_last_filtered_voltage() << " | "
                  << std::setw(12) << driver.get_capacitance_delta_pf() << " | "
                  << std::setw(16) << driver.get_displacement_um() << "\n";
    }

    std::cout << "-----------------------------------------------------------------------------------\n";
    std::cout << "\nДемонстрацію успішно завершено.\n";

    return 0;
}
