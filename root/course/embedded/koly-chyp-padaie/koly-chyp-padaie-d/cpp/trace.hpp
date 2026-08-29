#pragma once

#include <cstdint>
#include <optional>
#include <string_view>

namespace trace {

// Обгортка, щоб число друкувалося як 0xXXXXXXXX без окремої функції-форматера.
struct Hex {
    std::uint32_t value;
};

// USART2 (PA2 — TX, PA3 — RX), 115200 8N1, суто опитуванням: друкувати
// доводиться з обробника збою, де переривання й DMA вже нічого не варті.
class Uart {
public:
    void init() noexcept;

    void write(std::string_view text) noexcept;
    void write(char symbol) noexcept;
    void write(Hex value) noexcept;

    template <typename... Parts>
    void print(Parts... parts) noexcept
    {
        (write(parts), ...);
    }

    template <typename... Parts>
    void line(Parts... parts) noexcept
    {
        print(parts..., std::string_view{"\r\n"});
    }

    // Неблокуюче читання: порожньо, якщо байта немає.
    [[nodiscard]] std::optional<char> read() noexcept;

    // Дочекатися, доки останній байт фізично вийде з зсувного регістра.
    void flush() noexcept;

private:
    void put(std::uint8_t byte) noexcept;
};

inline constinit Uart out{};

} // namespace trace
