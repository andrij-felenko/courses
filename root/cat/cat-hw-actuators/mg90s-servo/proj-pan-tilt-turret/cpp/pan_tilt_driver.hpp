#pragma once

#include <cstdint>
#include <algorithm>
#include <cmath>

namespace actuators {

/**
 * @brief Ідентифікатор осі двоосьової платформи
 */
enum class AxisId : uint8_t {
    PAN = 0,   ///< Горизонтальна вісь панорамування (азимут)
    TILT = 1   ///< Вертикальна вісь нахилу (елевація)
};

/**
 * @brief Поточний напрямок руху важеля сервопривода
 */
enum class Direction : int8_t {
    NEGATIVE = -1, ///< Рух у бік зменшення кута
    STOPPED  = 0,  ///< Привід нерухомий
    POSITIVE = 1   ///< Рух у бік збільшення кута
};

/**
 * @brief Функціональний тип зворотного виклику для генерації апаратного ШІМ-імпульсу
 * @param pin Номер GPIO-виводу мікроконтролера
 * @param pulse_us Тривалість активного імпульсу високого рівня у мікросекундах
 */
using PwmWriteCallback = void (*)(uint8_t pin, uint32_t pulse_us);

/**
 * @brief Конфігураційні параметри окремого сервопривода MG90S
 */
struct ServoConfig {
    uint8_t pin{0};                        ///< Апаратний вивід GPIO
    uint32_t min_pulse_us{500};            ///< Мінімальна тривалість імпульсу (0°), зазвичай 500 мкс
    uint32_t max_pulse_us{2400};           ///< Максимальна тривалість імпульсу (180°), зазвичай 2400 мкс
    float min_angle_deg{10.0f};            ///< Програмний кінцевик (soft-limit) знизу для захисту від удару об упор
    float max_angle_deg{170.0f};           ///< Програмний кінцевик (soft-limit) згори
    float backlash_deg{1.8f};              ///< Кутовий люфт металевого редуктора для компенсації при реверсі (1.0–2.5°)
    float default_speed_deg_s{60.0f};      ///< Базова кутова швидкість переміщення (град/с)
};

/**
 * @brief Динамічний стан осі сервопривода у часі
 */
struct AxisState {
    float current_angle_deg{90.0f};        ///< Фактичний поточний кут платформи
    float start_angle_deg{90.0f};          ///< Початковий кут сегмента траєкторії
    float target_angle_deg{90.0f};         ///< Цільовий кут переміщення
    uint64_t start_time_us{0};             ///< Часова мітка початку руху (мікросекунди)
    uint64_t duration_us{0};               ///< Розрахункова тривалість руху (мікросекунди)
    Direction last_direction{Direction::STOPPED}; ///< Останній активний напрямок для вибірки люфту
    bool in_motion{false};                 ///< Прапорець активного руху
    uint32_t last_pulse_us{1450};          ///< Останній згенерований імпульс ШІМ
};

/**
 * @brief Неблокуючий об'єктно-орієнтований драйвер двоосьової Pan-Tilt платформи на базі MG90S
 */
class PanTiltDriver {
public:
    /**
     * @brief Конструктор драйвера
     * @param pan_cfg Налаштування осі панорамування
     * @param tilt_cfg Налаштування осі нахилу
     * @param pwm_cb Вказівник на функцію апаратного виводу ШІМ
     */
    PanTiltDriver(const ServoConfig& pan_cfg, const ServoConfig& tilt_cfg, PwmWriteCallback pwm_cb);

    /**
     * @brief Ініціалізація вихідних позицій обох сервоприводів у нейтраль (90°)
     * @param current_time_us Поточний системний час у мікросекундах
     */
    void init(uint64_t current_time_us);

    /**
     * @brief Задання нової цільової позиції для окремої осі
     * @param axis Ідентифікатор осі (PAN або TILT)
     * @param target_deg Цільовий кут у градусах
     * @param speed_deg_s Швидкість руху (0 — використання швидкості за замовчуванням)
     * @param current_time_us Поточний системний час у мікросекундах
     * @return true, якщо координата пройшла валідацію soft-limits і прийнята
     */
    bool setTarget(AxisId axis, float target_deg, float speed_deg_s, uint64_t current_time_us);

    /**
     * @brief Синхронне задання цільових координат для обох осей
     * @param pan_deg Цільовий кут панорамування
     * @param tilt_deg Цільовий кут нахилу
     * @param speed_deg_s Швидкість руху
     * @param current_time_us Поточний системний час у мікросекундах
     * @return true, якщо обидва кути валідні
     */
    bool setTargetPanTilt(float pan_deg, float tilt_deg, float speed_deg_s, uint64_t current_time_us);

    /**
     * @brief Неблокуюче оновлення кінематики (викликається в кожній ітерації loop())
     * @param current_time_us Поточний системний час у мікросекундах
     */
    void update(uint64_t current_time_us);

    /**
     * @brief Перевірка активності руху конкретної осі
     */
    [[nodiscard]] bool isMoving(AxisId axis) const;

    /**
     * @brief Перевірка активності руху будь-якої з осей платформи
     */
    [[nodiscard]] bool isMoving() const;

    /**
     * @brief Отримання поточного розрахованого кута осі
     */
    [[nodiscard]] float getCurrentAngle(AxisId axis) const;

    /**
     * @brief Отримання останньої тривалості ШІМ-імпульсу осі (мкс)
     */
    [[nodiscard]] uint32_t getCurrentPulseUs(AxisId axis) const;

    /**
     * @brief Аварійна миттєва зупинка руху обох осей у поточній точці
     */
    void emergencyStop();

private:
    /**
     * @brief Плавна S-крива інтерполяції (квінтичний поліном Перліна з нульовим ривком jerk)
     * @param t Нормалізований прогрес часу [0.0 ... 1.0]
     * @return Коефіцієнт позиції [0.0 ... 1.0]
     */
    [[nodiscard]] static float smootherstep(float t);

    /**
     * @brief Перерахунок геометричного кута вала у тривалість активного імпульсу ШІМ
     */
    [[nodiscard]] uint32_t angleToPulseUs(const ServoConfig& cfg, float angle_deg) const;

    /**
     * @brief Розрахунок та застосування компенсації мертвого ходу (люфту шестерень)
     */
    [[nodiscard]] float applyBacklashCompensation(AxisState& state, const ServoConfig& cfg, float raw_angle) const;

    /**
     * @brief Оновлення стану окремої осі
     */
    void updateAxis(AxisId axis, uint64_t current_time_us);

    ServoConfig configs_[2];      ///< Масив конфігурацій [0]=PAN, [1]=TILT
    AxisState states_[2];        ///< Масив станів [0]=PAN, [1]=TILT
    PwmWriteCallback pwm_cb_{nullptr}; ///< Колбек генерації апаратного ШІМ
};

} // namespace actuators
