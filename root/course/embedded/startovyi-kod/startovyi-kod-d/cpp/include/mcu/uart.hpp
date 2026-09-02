#pragma once

#include <cstdint>
#include <string_view>

namespace mcu {

/* Мінімальний передавач USART1 (вивід PA9, 8 біт, без парності, 1 стоп).
   Конструктор чіпає залізо — саме тому глобальний об'єкт цього класу
   залежить від того, чи вже налаштоване тактування. */
class uart {
public:
    explicit uart(std::uint32_t baud_rate) noexcept;

    void write(std::string_view text) const noexcept;

    [[nodiscard]] std::uint32_t baud_rate() const noexcept { return baud_; }

private:
    void put(char symbol) const noexcept;

    std::uint32_t baud_;
};

/* Глобальний об'єкт: його конструктор відпрацює під час обходу
   .init_array, ДО main() — і в порядку, якого стандарт не визначає. */
extern uart g_console_uart;

/* Те саме, але без фіаско порядку ініціалізації: локальний static
   конструюється в мить першого виклику функції. */
[[nodiscard]] uart& console() noexcept;

} // namespace mcu
