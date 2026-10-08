#include <iostream>
#include <iomanip>
#include <cmath>
#include "adc_config.hpp"
#include "lm35_filter.hpp"

// Симуляція апаратного аналогового середовища та АЦП мікроконтролера
namespace MockHardware {
    static float g_simulated_real_temp_c = 24.5f; // Фактична температура довкілля у °C
    static uint32_t g_sample_counter = 0;

    // Зворотний виклик аналого-цифрового перетворення для входу АЦП
    uint16_t readAdcPin(uint8_t pin) {
        (void)pin;
        ++g_sample_counter;

        // Симуляція високочастотного шуму на аналоговій лінії та випадкових наводок
        float noise = std::sin(g_sample_counter * 0.8f) * 0.7f;
        if (g_sample_counter % 6 == 0) {
            noise += 1.5f; // Поодинокий імпульсний завадовий сплеск
        }

        float current_temp = g_simulated_real_temp_c + noise;

        // Перетворення температури у напругу (LM35DZ: 10 мВ / °C = 0.010 В / °C)
        float voltage_v = current_temp * LM35Filter::LM35_SENSITIVITY_V_PER_C;

        // Налаштування АЦП: опорна напруга 1,1 В, 10-бітний АЦП (1024 рівні)
        constexpr float ref_v = 1.1f;
        constexpr uint32_t max_adc = 1023;

        if (voltage_v < 0.0f) voltage_v = 0.0f;
        if (voltage_v > ref_v) voltage_v = ref_v;

        return static_cast<uint16_t>((voltage_v / ref_v) * max_adc + 0.5f);
    }
}

int main() {
    std::cout << "====================================================================\n";
    std::cout << " Моніторинг довкілля: Аналоговий давач температури LM35DZ (C++)\n";
    std::cout << "====================================================================\n\n";

    // 1. Конфігурація АЦП мікроконтролера: вибір внутрішньої опорної напруги 1,1 В
    AdcConfig adc_config;
    adc_config.reference = AdcReference::Internal1V1;
    adc_config.ref_voltage_v = 1.1f;
    adc_config.resolution = AdcResolution::Bits10; // 10-бітний АЦП (0..1023)
    adc_config.analog_pin = 0;                     // Канал АЦП0

    // 2. Параметри калібрування аналогового тракту
    CalibrationParams cal_params;
    cal_params.offset_celsius = -0.2f; // Адитивний зсув (°C)
    cal_params.scale_factor = 1.005f;  // Множник масштабу

    std::cout << "[ІНІЦІАЛІЗАЦІЯ] Параметри АЦП:\n";
    std::cout << "  - Джерело опорної напруги: Внутрішнє 1,1 В (замість VCC)\n";
    std::cout << "  - Роздільна здатність АЦП: " << static_cast<int>(adc_config.resolution) << " біт (0.." << adc_config.maxAdcValue() << ")\n";
    std::cout << "  - Динамічний діапазон вимірювання: від 0 °C до +110 °C\n";
    std::cout << "  - Калібрування: offset = " << cal_params.offset_celsius << " °C, scale = " << cal_params.scale_factor << "\n\n";

    // 3. Створення драйвера LM35Filter із розміром вікна цифрового усереднення 8 відліків
    constexpr size_t WINDOW_SIZE = 8;
    LM35Filter filter(adc_config, cal_params, MockHardware::readAdcPin, WINDOW_SIZE);

    if (!filter.init()) {
        std::cerr << "[ПОМИЛКА] Не вдалося ініціалізувати драйвер LM35!\n";
        return 1;
    }

    std::cout << "[ІНІЦІАЛІЗАЦІЯ] Буфер усереднення заповнено " << WINDOW_SIZE << " первинними відліками.\n\n";

    std::cout << "--------------------------------------------------------------------\n";
    std::cout << " Крок | Сирий АЦП | Фільтр АЦП | Напруга мВ | Температура °C\n";
    std::cout << "--------------------------------------------------------------------\n";

    // 4. Цикл моніторингу температури та придушення високочастотних завад
    for (int step = 1; step <= 15; ++step) {
        // Симуляція зміни температури довкілля на 9 кроці
        if (step == 9) {
            MockHardware::g_simulated_real_temp_c = 28.3f;
            std::cout << ">>> [ПОДІЯ] Температура довкілля зросла до 28.3 °C <<<\n";
        }

        uint16_t raw_adc = filter.sample();
        float filtered_adc = filter.getFilteredRaw();
        float voltage_mv = filter.rawToMillivolts(raw_adc);
        float temp_c = filter.getTemperatureCelsius();

        std::cout << std::setw(5) << step << " | "
                  << std::setw(9) << raw_adc << " | "
                  << std::setw(10) << std::fixed << std::setprecision(1) << filtered_adc << " | "
                  << std::setw(10) << std::fixed << std::setprecision(1) << voltage_mv << " | "
                  << std::setw(14) << std::fixed << std::setprecision(2) << temp_c << "\n";
    }

    std::cout << "--------------------------------------------------------------------\n\n";
    std::cout << "[УСПІХ] Моніторинг завершено. Цифровий фільтр придушив шуми аналогового тракту.\n";

    return 0;
}
