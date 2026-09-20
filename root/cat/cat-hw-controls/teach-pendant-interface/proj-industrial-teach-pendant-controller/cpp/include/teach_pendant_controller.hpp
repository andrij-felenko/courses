#ifndef TEACH_PENDANT_CONTROLLER_HPP
#define TEACH_PENDANT_CONTROLLER_HPP

#include <cstdint>
#include <cstddef>
#include <functional>
#include <array>

// Перелічення станів трипозиційної кнопки дозволу (Enabling Switch)
enum class EnablingState : uint8_t {
    Released = 0, // Стан 1: Вільний (Off) - розімкнено
    Enabled  = 1, // Стан 2: Робоче натискання (Enable) - замкнено
    Panic    = 2  // Стан 3: Повне панічне стискання (Panic Stop) - розімкнено
};

// Перелічення станів кнопкової аварійної зупинки (E-Stop)
enum class EmergencyState : uint8_t {
    Normal    = 0, // Аварійна кнопка не натиснута
    Triggered = 1  // Аварійна кнопка натиснута (E-Stop active)
};

// Структура поточного стану пульта налагодження
struct PendantState {
    EnablingState enabling_switch{EnablingState::Released};
    EmergencyState estop_button{EmergencyState::Normal};
    std::array<int16_t, 6> joystick_axes{0, 0, 0, 0, 0, 0}; // 6-осьовий джойстик X, Y, Z, Rx, Ry, Rz (-1000..1000)
    uint16_t button_mask{0};                                // Битова маска допоміжних кнопок
    uint32_t timestamp_ms{0};                               // Часова позначка вимірювання
};

// Структура кадру мережевого пакета з CRC16
#pragma pack(push, 1)
struct PendantPacket {
    uint8_t header{0xAA};
    uint8_t enabling_status;
    uint8_t estop_status;
    uint16_t button_mask;
    int16_t axes[6];
    uint32_t timestamp_ms;
    uint16_t crc16;
};
#pragma pack(pop)

// Клас керування пультом налагодження промислового робота
class TeachPendantController {
public:
    using StateCallback = std::function<void(const PendantState&)>;
    using EmergencyCallback = std::function<void(EmergencyState)>;

    TeachPendantController();

    // Налаштування функцій зворотного виклику для подій
    void set_state_callback(StateCallback callback);
    void set_emergency_callback(EmergencyCallback callback);

    // Оновлення апаратного вводу та запуск автомата станів
    void update(uint32_t current_time_ms, 
                 uint8_t raw_enabling_pin1, 
                 uint8_t raw_enabling_pin2,
                 uint8_t raw_estop_pin,
                 const std::array<int16_t, 6>& raw_axes,
                 uint16_t raw_buttons);

    // Отримання поточного стану
    [[nodiscard]] const PendantState& get_current_state() const noexcept;

    // Формування кадру телеметрії із розрахунком CRC16
    [[nodiscard]] PendantPacket build_packet() const noexcept;

    // Статична функція обчислення CRC16-CCITT (Poly: 0x1021)
    [[nodiscard]] static uint16_t calculate_crc16(const uint8_t* data, size_t length) noexcept;

private:
    PendantState current_state_{};
    StateCallback state_callback_{nullptr};
    EmergencyCallback emergency_callback_{nullptr};

    // Параметри фільтрації брязкоту контактів
    uint32_t last_debounce_time_ms_{0};
    static constexpr uint32_t DEBOUNCE_DELAY_MS = 10;

    // Обробка автомата станів кнопки дозволу
    EnablingState evaluate_enabling_switch(uint8_t pin1, uint8_t pin2) noexcept;
};

#endif // TEACH_PENDANT_CONTROLLER_HPP
