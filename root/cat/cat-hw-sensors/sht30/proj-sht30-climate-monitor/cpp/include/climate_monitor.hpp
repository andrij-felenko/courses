#pragma once

#include "sht30.hpp"
#include <chrono>

namespace sensors {

/**
 * @brief Результати поточного стану мікроклімату та діагностики давача.
 */
struct ClimateStatus {
    float temperature_c{0.0f};     ///< Температура повітря (°C)
    float humidity_percent{0.0f};  ///< Відносна вологість (%)
    float dew_point_c{0.0f};       ///< Обчислена точка роси (°C)
    bool condensation_risk{false}; ///< Виявлено високий ризик конденсату
    bool crc_ok{false};            ///< Цілісність зчитаних даних підтверджено
};

/**
 * @brief Модуль аналізу мікроклімату, обчислення точки роси та обслуговування SHT30.
 */
class ClimateMonitor {
public:
    explicit ClimateMonitor(SHT30& sensor, float condensation_threshold_rh = 85.0f);

    /**
     * @brief Зчитує дані із SHT30, валідує CRC-8 та розраховує похідні параметри.
     */
    ClimateStatus update();

    /**
     * @brief Обчислює точку роси за наближеною формулою Магнуса-Тетенса.
     * @param temp_c Температура повітря (°C)
     * @param rh_percent Відносна вологість (%)
     * @return Точка роси (°C)
     */
    static float calculate_dew_point(float temp_c, float rh_percent) noexcept;

    /**
     * @brief Процедура висушування чутливого елемента внутрішнім нагрівачем SHT30.
     * @param duration Тривалість роботи нагрівача
     */
    bool perform_decondensation_cycle(std::chrono::milliseconds duration = std::chrono::milliseconds(1500));

    /**
     * @brief Переведення давача у режим сну.
     */
    bool enter_sleep_mode();

private:
    SHT30& sensor_;
    float condensation_threshold_rh_;
};

} // namespace sensors
