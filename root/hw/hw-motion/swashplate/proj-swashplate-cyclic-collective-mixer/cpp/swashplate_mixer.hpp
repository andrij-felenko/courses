#pragma once

#include <cstdint>
#include <array>

/**
 * @brief Тип геометрії автомата перекосу (розташування сервоприводів CCPM).
 */
enum class CcpmType {
    CCPM_120, /**< Три сервоприводи з кутовим інтервалом 120° (класична схема) */
    CCPM_140, /**< Схема 140° із симетричним відведенням бічних сервоприводів */
    CCPM_90   /**< Схема 90° із роздільними поздовжнім та поперечним сервоприводами */
};

/**
 * @brief Нормалізовані вхідні команди керування від пілота / автопілота [-1.0 ... +1.0].
 */
struct ControlInput {
    float collective;   /**< Спільний крок (вертикальна тяга) [-1.0 ... +1.0] */
    float cyclic_pitch; /**< Циклічний крок тангажу (ніс/хвіст) [-1.0 ... +1.0] */
    float cyclic_roll;  /**< Циклічний крок крену (ліворуч/праворуч) [-1.0 ... +1.0] */
};

/**
 * @brief Вихідні сигнали тривалості імпульсів ШІМ для трьох сервоприводів (мкс).
 */
struct ServoOutput {
    std::array<uint16_t, 3> pwm_us; /**< Тривалості імпульсів ШІМ [1000 ... 2000 мкс] */
};

/**
 * @brief Конфігураційні параметри геометрії автомата перекосу.
 */
struct SwashplateConfig {
    CcpmType type{CcpmType::CCPM_120}; /**< Геометрія CCPM */
    float arm_length_mm{20.0f};        /**< Довжина качалки сервопривода (мм) */
    float max_travel_mm{12.0f};        /**< Максимальний лінійний хід тяги (мм) */
    float ring_limit_norm{1.0f};       /**< Радіус кругового обмежувача (0.0 ... 1.0) */
};

/**
 * @brief Клас мікшера автомата перекосу з підтримкою CCPM та обмежувача ходу.
 */
class SwashplateMixer {
public:
    explicit SwashplateMixer(const SwashplateConfig& config) noexcept;

    /**
     * @brief Розрахунок вихідних сигналів ШІМ для сервоприводів за вхідними командами.
     * @param input Нормалізовані сигнали пілота (collective, pitch, roll).
     * @return Структура з тривалостями ШІМ у мікросекундах.
     */
    ServoOutput update(const ControlInput& input) noexcept;

    /**
     * @brief Застосування кругового обмежувача ходу тарілки (Swashplate Ring Limiter).
     * @param input Початкові вхідні сигнали.
     * @return Скориговані сигнали з обмеженим радіусом вектора циклічного кроку.
     */
    ControlInput applyRingLimiter(const ControlInput& input) const noexcept;

private:
    SwashplateConfig config_;

    /**
     * @brief Тригонометрична лінеаризація обертання качалки сервопривода.
     * @param linear_travel_mm Потрібне лінійне переміщення тяги (мм).
     * @return Кут повороту вала сервопривода в радіанах.
     */
    float linearizeServoArm(float linear_travel_mm) const noexcept;

    /**
     * @brief Перетворення кута повороту качалки в мікросекунди імпульсу ШІМ.
     * @param angle_rad Кут повороту вала сервопривода (рад).
     * @return Тривалість імпульсу в діапазоні 1000...2000 мкс (нейтраль 1500 мкс).
     */
    static uint16_t angleToPwmUs(float angle_rad) noexcept;
};
