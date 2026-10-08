#ifndef RTD_MATH_HPP
#define RTD_MATH_HPP

#include <cstdint>
#include <cmath>
#include "max31865_sensor.hpp"

/**
 * @brief Математичний клас RtdMath для перетворення коду АЦП у опір та температуру.
 * Використовує рівняння Каллендара — Ван Дюзена з компенсацією нелінійності платини.
 */
class RtdMath {
public:
    // Константи платини IEC 60751 (DIN EN 60751)
    static constexpr float ALPHA_A = 3.9083e-3f;  // Коефіцієнт A (°C^-1)
    static constexpr float ALPHA_B = -5.775e-7f;  // Коефіцієнт B (°C^-2)
    static constexpr float ALPHA_C = -4.183e-12f; // Коефіцієнт C (°C^-4 для t < 0 °C)

    /**
     * @brief Перетворення 15-бітного сухого коду АЦП у співвідносний опір терморезистора RTD.
     * @param adc_code 15-бітне значення АЦП (0..32767)
     * @param r_ref_ohm Точний опір опорного резистора Rref (наприклад, 400.0 або 4000.0 Ом)
     * @return Обчислений опір датчика в Омах
     */
    static float adcToResistance(uint16_t adc_code, float r_ref_ohm) noexcept {
        return (static_cast<float>(adc_code) * r_ref_ohm) / 32768.0f;
    }

    /**
     * @brief Обчислення точної температури за виміряним опором RTD.
     * Застосовує розв'язок квадратного рівняння для t >= 0 °C та ітераційний метод Ньютона-Рафсона для t < 0 °C.
     * @param r_ohm Виміряний опір термодатчика
     * @param r_0_ohm Номінальний опір датчика при 0 °C (100 Ом для PT100, 1000 Ом для PT1000)
     * @return Обчислена температура в °C
     */
    static float resistanceToTemperature(float r_ohm, float r_0_ohm) noexcept {
        if (r_ohm <= 0.0f || r_0_ohm <= 0.0f) {
            return -273.15f; // Абсолютний нуль або некоректні дані
        }

        const float z = 1.0f - (r_ohm / r_0_ohm);
        const float discriminant = (ALPHA_A * ALPHA_A) - (4.0f * ALPHA_B * z);

        if (discriminant < 0.0f) {
            return -273.15f;
        }

        // Початкове наближення за квадратним рівнянням Каллендара — Ван Дюзена
        float temp = (-ALPHA_A + std::sqrt(discriminant)) / (2.0f * ALPHA_B);

        // Якщо температура додатна або дорівнює нулю, квадратний розв'язок точний
        if (temp >= 0.0f) {
            return temp;
        }

        // Для від'ємних температур (t < 0 °C) уточнюємо значення за поліномом 4-го ступеня методом Ньютона-Рафсона
        for (int i = 0; i < 4; ++i) {
            const float t2 = temp * temp;
            const float t3 = t2 * temp;
            const float t4 = t3 * temp;

            // f(t) = R_0 * (1 + A*t + B*t^2 + C*(t - 100)*t^3) - R
            const float f_val = r_0_ohm * (1.0f + ALPHA_A * temp + ALPHA_B * t2 + ALPHA_C * (temp - 100.0f) * t3) - r_ohm;
            // f'(t) = R_0 * (A + 2*B*t + 4*C*t^3 - 300*C*t^2)
            const float f_prime = r_0_ohm * (ALPHA_A + 2.0f * ALPHA_B * temp + 4.0f * ALPHA_C * t3 - 300.0f * ALPHA_C * t2);

            if (std::abs(f_prime) < 1e-9f) {
                break;
            }

            temp = temp - (f_val / f_prime);
        }

        return temp;
    }

    /**
     * @brief Сформувати структуровану телеметрію на основі сирого коду АЦП.
     */
    static RtdTelemetry convertAdcToTelemetry(uint16_t adc_code,
                                              const RtdConfig& config,
                                              FaultFlags fault_flags,
                                              uint32_t timestamp_ms) noexcept {
        RtdTelemetry telemetry{};
        telemetry.raw_adc = adc_code;
        telemetry.fault = fault_flags;
        telemetry.timestamp_ms = timestamp_ms;
        telemetry.resistance_ohm = adcToResistance(adc_code, config.r_ref_ohm);
        telemetry.temperature_c = resistanceToTemperature(telemetry.resistance_ohm, config.r_0_ohm);

        // Дані вважаються валідними, якщо відсутні апаратні помилки та температура в допустимих межах
        telemetry.is_valid = !fault_flags.anyFault() &&
                             (telemetry.temperature_c >= config.lower_temp_limit) &&
                             (telemetry.temperature_c <= config.upper_temp_limit);

        return telemetry;
    }
};

#endif // RTD_MATH_HPP
