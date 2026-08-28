// Розрахунок дільника UART мовою C++ (виконується під час збирання)
#include <cstdint>

struct UartBaudDiv {
    uint16_t mantissa;
    uint8_t  fraction;

    [[nodiscard]] constexpr uint16_t to_brr() const noexcept {
        return static_cast<uint16_t>((mantissa << 4) | (fraction & 0x0F));
    }
};

consteval UartBaudDiv calculate_baud_cpp(uint32_t f_pclk, uint32_t baud) {
    if (baud == 0 || f_pclk < baud) {
        // Зупиняє компіляцію, якщо параметри некоректні
        throw "Некоректний бітрейт для поточної тактової частоти!";
    }
    uint32_t div = (25 * f_pclk) / (4 * baud);
    uint32_t mantissa = div / 100;
    uint32_t fraction = (((div - (mantissa * 100)) * 16) + 50) / 100;
    return { static_cast<uint16_t>(mantissa), static_cast<uint8_t>(fraction) };
}

// Значення обчислюється один раз під час трансляції
constexpr auto BRR_VALUE = calculate_baud_cpp(84000000UL, 115200UL).to_brr();
