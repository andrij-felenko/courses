#pragma once

#include <cstddef>
#include <cstdint>
#include <functional>
#include <span>
#include <string_view>

// Формат кадру в лінії:
//
//   COBS( [seq:1] [payload:0..kMaxPayload] [CRC-16:2, старший байт перший] ) [0x00]
//
// Квитанція (ACK) — кадр із порожнім навантаженням: поле seq несе номер, який квитують.

namespace link {

inline constexpr std::size_t kMaxPayload = 64;
inline constexpr std::size_t kSeqSize    = 1;
inline constexpr std::size_t kCrcSize    = 2;
inline constexpr std::size_t kMaxFrame   = kSeqSize + kMaxPayload + kCrcSize;
inline constexpr std::size_t kMaxWire    = kMaxFrame + kMaxFrame / 254 + 2;
inline constexpr std::uint8_t kDelimiter = 0x00;

// Простір номерів 8-бітний, S = 256: для Selective Repeat треба S >= 2*W,
// а для індексації слотів через (seq % kWindow) — щоб S ділилося на W націло.
inline constexpr std::size_t kWindow = 8;

enum class Error : std::uint8_t {
    TooLong,        // навантаження більше за kMaxPayload
    NoSpace,        // не влізло у виданий буфер
    CobsCorrupted,  // структурно пошкоджене COBS-тіло
    CrcMismatch,    // остача CRC ненульова
    ShortFrame,     // кадр коротший за службовий мінімум
    Overflow,       // роздільник не прийшов, буфер прийому переповнено
    WindowFull,     // усі неквитовані слоти зайняті
    LinkDown        // вичерпано ліміт повторів
};

[[nodiscard]] constexpr std::string_view describe(Error e) noexcept {
    switch (e) {
        case Error::TooLong:       return "навантаження задовге";
        case Error::NoSpace:       return "малий буфер";
        case Error::CobsCorrupted: return "пошкоджений COBS";
        case Error::CrcMismatch:   return "не збіглася CRC";
        case Error::ShortFrame:    return "надто короткий кадр";
        case Error::Overflow:      return "переповнення прийому";
        case Error::WindowFull:    return "вікно заповнене";
        case Error::LinkDown:      return "лінія розірвана";
    }
    return "невідомо";
}

using Bytes = std::span<const std::uint8_t>;

// Куди віддавати готові байти: UART, RS-485, радіомодуль — або імітатор каналу.
// Замикання тут захоплює один вказівник, тож у std::function лишається на місці.
using ByteSink = std::function<void(Bytes)>;

// Різниця номерів у кільцевому просторі 0..255.
[[nodiscard]] constexpr std::uint8_t seq_diff(std::uint8_t a, std::uint8_t b) noexcept {
    return static_cast<std::uint8_t>(a - b);
}

// Чи номер a попереду b (у межах півкола простору номерів).
[[nodiscard]] constexpr bool seq_after(std::uint8_t a, std::uint8_t b) noexcept {
    const std::uint8_t d = seq_diff(a, b);
    return d != 0 && d < 128;
}

}  // namespace link
