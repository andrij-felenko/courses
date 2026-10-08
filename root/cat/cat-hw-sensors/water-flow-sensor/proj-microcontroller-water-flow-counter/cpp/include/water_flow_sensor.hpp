#ifndef WATER_FLOW_SENSOR_HPP
#define WATER_FLOW_SENSOR_HPP

#include <cstdint>
#include <atomic>

#ifndef IRAM_ATTR
#define IRAM_ATTR
#endif

// Структура метрик вимірювання витрати рідини
struct FlowMetrics {
    float flow_rate_lpm{0.0f};    // Миттєва витрата води, літри за хвилину (л/хв)
    double total_liters{0.0};     // Накопичений сумарний об'єм води, літри
    uint32_t total_pulses{0};     // Загальна кількість зареєстрованих імпульсів
};

// Стан живлення сенсорного вузла для налаштування режимів роботи
enum class PowerState {
    Normal,      // Стандартний повнофункціональний режим
    LowPower,    // Енергозбереження: знижена частота відправки телеметрії
    Critical     // Критичний рівень живлення
};

class WaterFlowSensor {
public:
    // K-factor за замовчуванням: ~7.5 Гц на 1 л/хв для турбінного давача G1/2" YF-S201
    explicit WaterFlowSensor(uint8_t gpio_pin, float k_factor = 7.5f);

    // Ініціалізація давача та скидання лічильників
    void begin();

    // Неблокуюче оновлення обчислень витрати води в головному циклі
    void update(uint32_t current_time_ms);

    // Статичний обробник апаратного переривання від давача Холла (ISR)
    static void IRAM_ATTR handle_interrupt();

    // Отримання поточних метрик вимірювання
    FlowMetrics get_metrics() const;

    // Встановлення нового калібрувального коефіцієнта (K-factor)
    void set_k_factor(float k_factor);

    // Скидання накопиченого об'єму води
    void reset_total_volume();

    // Отримання вказівника на екземпляр класу для ISR
    static WaterFlowSensor* get_instance() { return instance_; }

private:
    uint8_t pin_;
    float k_factor_;

    // Атомарний лічильник імпульсів для безпечного обміну даними між ISR та основним потоком
    static std::atomic<uint32_t> pulse_count_;
    static WaterFlowSensor* instance_;

    uint32_t last_update_ms_{0};

    float current_flow_rate_{0.0f};
    double total_volume_liters_{0.0};
    uint32_t total_pulse_accumulator_{0};
};

#endif // WATER_FLOW_SENSOR_HPP
