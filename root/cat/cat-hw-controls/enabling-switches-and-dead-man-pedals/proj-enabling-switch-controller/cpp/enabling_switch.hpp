#ifndef ENABLING_SWITCH_HPP
#define ENABLING_SWITCH_HPP

#include <cstdint>

// Базові дискретні стани кінцевого автомата трипозиційного органу дозволу
enum class EnablingState : uint8_t {
    Released, // Важіль відпущено (стан 1: OFF)
    Enabled,  // Робочий проміжний стан (стан 2: ON)
    Panic,    // Судомне продавлювання до упору (стан 3: OFF)
    Fault     // Апаратна несправність або часова неузгодженість ліній
};

// Перелічення подій vigilance control (контролю пильності)
enum class VigilanceStatus : uint8_t {
    Normal,   // Робота в нормі
    Warning,  // Попередження про наближення ліміту часу утримання
    Expired   // Час вичерпано, потрібне перевідпускання кнопки
};

// Конфігураційні часові параметри драйвера (у мілісекундах)
struct DriverConfig {
    uint32_t debounce_ms{20};        // Час цифрового дебаунсу контактів (t_debounce)
    uint32_t discrepancy_ms{50};     // Допустиме вікно розсинхронізму каналів (t_discrepancy)
    uint32_t hold_max_ms{15000};     // Максимальний час безперервного утримання (t_hold)
    uint32_t warn_ms{2000};          // Тривалість попереджувального сигналу (t_warn)
    uint32_t react_ms{1000};         // Час для реакції оператора після попередження (t_react)
};

// Клас для зчитування, фільтрації брязкоту та контролю неузгодженості двох фізичних каналів
class ChannelReader {
public:
    ChannelReader() = default;

    // Оновлення стану каналів із передачею поточних фізичних рівнів і часової мітки
    void update(bool raw_ch_a, bool raw_ch_b, uint32_t current_time_ms, const DriverConfig& config);

    // Отримання відфільтрованого стану контактів
    bool get_filtered_a() const { return filtered_ch_a_; }
    bool get_filtered_b() const { return filtered_ch_b_; }

    // Перевірка наявності апаратної помилки розсинхронізації ліній
    bool has_discrepancy_fault() const { return discrepancy_fault_; }

    // Скидання прапорця помилки розсинхронізації після усунення несправності
    void clear_fault() { discrepancy_fault_ = false; }

private:
    bool raw_ch_a_{false};
    bool raw_ch_b_{false};
    bool filtered_ch_a_{false};
    bool filtered_ch_b_{false};

    uint32_t last_change_a_ms_{0};
    uint32_t last_change_b_ms_{0};
    uint32_t discrepancy_start_ms_{0};

    bool discrepancy_active_{false};
    bool discrepancy_fault_{false};
};

// Клас керування таймерами контролю пильності (vigilance control)
class VigilanceTimer {
public:
    VigilanceTimer() = default;

    // Оновлення таймера у робочому стані Enabled
    void update(bool is_enabled, uint32_t current_time_ms, const DriverConfig& config);

    // Отримання поточного статусу контролю пильності
    VigilanceStatus get_status() const { return status_; }

    // Скидання таймера при відпусканні важеля
    void reset();

private:
    VigilanceStatus status_{VigilanceStatus::Normal};
    uint32_t enabled_start_ms_{0};
    bool timer_active_{false};
};

// Головний клас-контролер скінченного автомата трипозиційного органу дозволу
class EnablingSwitchController {
public:
    explicit EnablingSwitchController(const DriverConfig& config = DriverConfig());

    // Головний метод циклічного оновлення стану драйвера
    void update(bool raw_pin_a, bool raw_pin_b, uint32_t current_time_ms);

    // Перевірка дозволу на рух виконавчих механізмів
    bool is_enabled() const { return current_state_ == EnablingState::Enabled && vigilance_status_ == VigilanceStatus::Normal; }

    // Отримання поточного дискретного стану кінцевого автомата
    EnablingState get_state() const { return current_state_; }

    // Отримання статусу таймера пильності
    VigilanceStatus get_vigilance_status() const { return vigilance_status_; }

    // Отримання конфігураційних параметрів
    const DriverConfig& get_config() const { return config_; }

private:
    DriverConfig config_;
    ChannelReader channel_reader_;
    VigilanceTimer vigilance_timer_;

    EnablingState current_state_{EnablingState::Released};
    VigilanceStatus vigilance_status_{VigilanceStatus::Normal};

    bool require_full_release_{false}; // Прапорець вимоги перевідпускання після Panic/Fault
};

#endif // ENABLING_SWITCH_HPP
