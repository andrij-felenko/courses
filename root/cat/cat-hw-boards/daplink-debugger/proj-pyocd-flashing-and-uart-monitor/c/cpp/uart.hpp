#pragma once

#include <cstdint>
#include <cstddef>
#include <string_view>
#include <span>

namespace mcu {

// Клас Uart реалізує інкапсуляцію апаратного модуля UART мікроконтролера ARM Cortex-M
class Uart {
public:
    enum class BaudRate : uint32_t {
        Baud9600   = 9600,
        Baud19200  = 19200,
        Baud57600  = 57600,
        Baud115200 = 115200
    };

    explicit Uart(BaudRate baud_rate = BaudRate::Baud115200) noexcept;
    ~Uart() = default;

    // Контроль єдиного володіння апаратним ресурсом
    Uart(const Uart&) = delete;
    Uart& operator=(const Uart&) = delete;

    Uart(Uart&& other) noexcept;
    Uart& operator=(Uart&& other) noexcept;

    // Ініціалізація апаратних регістрів мікроконтролера
    void init();

    // Відправка одного символу
    void send_char(char c) const;

    // Відправка рядка через безпечний тип std::string_view
    void send_string(std::string_view str) const;

    // Відправка послідовності байтів через std::span
    void send_bytes(std::span<const uint8_t> data) const;

    // Спроба зчитування отриманого символу без блокування
    [[nodiscard]] bool receive_char(char& out_c) const;

    // Статус ініціалізації модуля
    [[nodiscard]] bool is_initialized() const noexcept { return is_initialized_; }

private:
    BaudRate baud_rate_;
    bool is_initialized_{false};

    void configure_hardware() const;
};

} // namespace mcu
