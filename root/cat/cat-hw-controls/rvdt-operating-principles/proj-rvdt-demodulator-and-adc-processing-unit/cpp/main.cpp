#include "rvdt_decoder.hpp"
#include <iostream>
#include <iomanip>
#include <vector>
#include <cmath>
#include <cstdlib>

// Мок-реалізація апаратного інтерфейсу АЦП для тестування RVDTDecoder
class MockAdcHal : public controls::IAdcHal {
public:
    void setRotorAngle(float angle_deg) noexcept {
        target_angle_deg_ = angle_deg;
    }

    std::optional<controls::RVDTRawSample> readSample() override {
        if (simulate_fault_) {
            return std::nullopt;
        }

        // Симуляція кутової залежності напруг вторинних обмоток RVDT
        // S1 = V0 * (1 + k*theta), S2 = V0 * (1 - k*theta)
        const float v0 = 2.5f;
        const float k = 0.02f; // Чутливість
        const float noise = 0.01f * (std::rand() % 100 - 50) / 50.0f; // Завада +/- 1%

        controls::RVDTRawSample sample{};
        sample.s1_volts = std::clamp(v0 * (1.0f + k * target_angle_deg_) + noise, 0.1f, 4.9f);
        sample.s2_volts = std::clamp(v0 * (1.0f - k * target_angle_deg_) - noise, 0.1f, 4.9f);
        sample.v_ref_volts = 5.0f; // Стабільна опорна напруга 5В

        return sample;
    }

    void setFault(bool fault) noexcept {
        simulate_fault_ = fault;
    }

private:
    float target_angle_deg_{0.0f};
    bool simulate_fault_{false};
};

int main() {
    std::cout << "--- Симуляція апаратного декодера RVDT ---" << std::endl;

    MockAdcHal adc_hal;
    controls::RVDTConfig config{};
    config.sensitivity_deg_per_ratio = 25.0f; // 25 градусів на одиницю коефіцієнта
    config.iir_alpha = 0.2f;                    // Згладжування
    
    // Коефіцієнти кубічного полінома для корекції нелінійності
    config.poly_corr.c0 = 0.0f;
    config.poly_corr.c1 = 1.0f;
    config.poly_corr.c2 = 0.02f;
    config.poly_corr.c3 = 0.005f;

    controls::RVDTDecoder decoder(adc_hal, config);

    // Симуляція повороту ротора RVDT на кути від -30 до +30 градусів
    const std::vector<float> test_angles = {-30.0f, -15.0f, 0.0f, 12.5f, 25.0f};

    std::cout << std::fixed << std::setprecision(2);
    std::cout << "Заданий кут | Відношення | Відфільтрований кут | Стан" << std::endl;

    for (float angle : test_angles) {
        adc_hal.setRotorAngle(angle);

        // Пропускаємо кілька тактів для стабілізації ІІР-фільтра
        for (int i = 0; i < 5; ++i) {
            decoder.update();
        }

        auto res_opt = decoder.update();
        if (res_opt.has_value() && res_opt->is_valid) {
            std::cout << angle << " | " << res_opt->raw_ratio << " | " << res_opt->angle_degrees << " | Норма" << std::endl;
        } else {
            std::cout << angle << " | Помилка!" << std::endl;
        }
    }

    // Демонстрація виявлення аварійного стану (обрив лінії АЦП)
    std::cout << "\nТест аварійного стану (обрив лінії кабелю):" << std::endl;
    adc_hal.setFault(true);
    auto fault_res = decoder.update();
    if (!fault_res.has_value()) {
        std::cout << "Успішно виявлено помилку зчитування АЦП (збій HAL)!" << std::endl;
    }

    return 0;
}
