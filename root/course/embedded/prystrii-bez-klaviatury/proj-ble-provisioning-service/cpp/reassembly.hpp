#pragma once

#include <cstdint>
#include <expected>
#include <span>
#include <vector>

/*
 * Збирання довгих записів ATT.
 *
 * Базовий MTU — 23 байти, з них 3 зʼїдає заголовок (Opcode + Attribute Handle),
 * тож на корисне навантаження лишається 20. Ключ X25519 — уже 32 байти, пакет
 * конфігурації — 80–120. Два виходи, і потрібні обидва: узгодити більший MTU,
 * а коли клієнт цього не вміє — зібрати значення з Prepare Write Request.
 */
namespace prov {

inline constexpr std::uint16_t AttMtuDefault = 23;
inline constexpr std::uint16_t AttMtuMax = 256;
inline constexpr std::uint16_t AttHeaderSize = 3;
inline constexpr std::size_t AttReassemblyCapacity = 256;

// Коди помилок ATT (Bluetooth Core, Vol 3, Part F, 3.4.1.1).
enum class AttError : std::uint8_t {
    InvalidOffset = 0x07,
    PrepareQueueFull = 0x09,
    InvalidAttributeLength = 0x0D,
    Unlikely = 0x0E
};

// Відповідь на ATT_EXCHANGE_MTU_REQ: беремо менше з двох стель.
[[nodiscard]] std::uint16_t negotiate_mtu(std::uint16_t client_mtu) noexcept;

[[nodiscard]] constexpr std::uint16_t mtu_payload(std::uint16_t mtu) noexcept
{
    return static_cast<std::uint16_t>(mtu - AttHeaderSize);
}

class AttReassembler {
public:
    struct Assembled {
        std::uint16_t char_uuid{0};
        std::span<const std::uint8_t> value{};
    };

    // Черговий Prepare Write Request.
    std::expected<void, AttError> prepare(std::uint16_t char_uuid,
                                          std::uint16_t offset,
                                          std::span<const std::uint8_t> value);

    // Execute Write Request. commit == false — клієнт скасував чергу.
    std::expected<Assembled, AttError> execute(bool commit);

    void cancel() noexcept;

private:
    std::vector<std::uint8_t> buffer_;
    std::uint16_t char_uuid_{0};
    bool active_{false};
};

}  // namespace prov
