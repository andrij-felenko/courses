// Пастка вкладеності в живому драйвері: низькорівнева функція вмикає
// переривання безумовно й тим самим знімає захист із зовнішньої секції.
#include <cstddef>
#include <cstdint>
#include <span>

#include "demo/demos.hpp"
#include "mcu/cpu.hpp"

namespace {

struct UsartRegs {
    volatile std::uint32_t sr;  // 0x00 — стан
    volatile std::uint32_t dr;  // 0x04 — дані
    volatile std::uint32_t brr; // 0x08 — дільник швидкості
    volatile std::uint32_t cr1; // 0x0C — керування
};

// STM32F4: USART1 за адресою 0x40011000.
UsartRegs* const usart1 = reinterpret_cast<UsartRegs*>(0x40011000UL);
constexpr std::uint32_t kSrTxe = 1U << 7;
constexpr std::byte kPacketHeader{0xA5};

// CRC-8, поліном 0x07.
std::byte packet_crc8(std::span<const std::byte> payload) noexcept
{
    std::uint8_t crc = 0xFF;

    for (const std::byte value : payload) {
        crc ^= std::to_integer<std::uint8_t>(value);
        for (int bit = 0; bit < 8; ++bit) {
            crc = ((crc & 0x80U) != 0U) ? static_cast<std::uint8_t>((crc << 1) ^ 0x07U)
                                        : static_cast<std::uint8_t>(crc << 1);
        }
    }
    return std::byte{crc};
}

// Низький рівень драйвера: власна критична секція навколо регістра даних.
void uart_send_byte(std::byte value) noexcept
{
    mcu::cpu::disable_irq();

    // Друга вада на додачу до головної: очікування апаратури всередині
    // вимкнених переривань — на 115200 це до 87 мкс на кожен байт.
    while ((usart1->sr & kSrTxe) == 0U) {
    }
    usart1->dr = std::to_integer<std::uint32_t>(value);

    mcu::cpu::enable_irq(); // ПОМИЛКА: знімає й чужий захист
}

} // namespace

namespace demo {

bool telemetry_send_packet(std::span<const std::byte> payload) noexcept
{
    if (payload.empty() || payload.size() > 255U) {
        return false;
    }

    mcu::cpu::disable_irq(); // зовнішня секція: пакет має піти неподільно

    const std::byte crc = packet_crc8(payload);
    uart_send_byte(kPacketHeader); // і саме тут захист зникає

    // Далі переривання УВІМКНЕНІ. ISR вклинюється між байтами й пише в той
    // самий dr — приймач дістає перемішаний кадр.
    for (const std::byte value : payload) {
        uart_send_byte(value);
    }
    uart_send_byte(crc);

    mcu::cpu::enable_irq();
    return true;
}

} // namespace demo
