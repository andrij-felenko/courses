// Формат самодостатнього кадру черги офлайну у NOR Flash.
//
//   зсув   розмір  поле
//   0      2       magic 0xAA55
//   2      4       seq          — монотонний лічильник кадрів
//   6      8       ts_ms        — Unix Epoch у мілісекундах
//   14     2       len          — довжина корисного навантаження
//   16     1       kind         — клас даних
//   17     len     payload
//   17+len 4       crc32        — IEEE 802.3 по байтах [0, 17+len)
//
// На носії живе байтовий формат, а не образ структури: жодного
// reinterpret_cast на буфер читання. Явна серіалізація знімає одразу
// вирівнювання (seq стоїть на непарному зсуві), порядок байтів і
// залежність від того, як компілятор вирішив ущільнити поля.
#pragma once

#include <cstddef>
#include <cstdint>
#include <expected>
#include <span>
#include <string_view>

namespace sf {

inline constexpr std::uint16_t kMagic = 0xAA55;

inline constexpr std::size_t kHeaderSize = 17;
inline constexpr std::size_t kCrcSize    = 4;
inline constexpr std::size_t kMaxPayload = 512;
inline constexpr std::size_t kMaxFrame   = kHeaderSize + kMaxPayload + kCrcSize;

// Класи даних із політики витіснення. Сканер їх не тлумачить — вони
// потрібні диспетчеру черги, коли сховище переповнене.
enum class Kind : std::uint8_t {
    Event  = 0, // Клас 0 — аварії, ніколи не витісняються
    Status = 1, // Клас 1 — періодичний агрегований статус
    Raw    = 2  // Клас 2 — високочастотний сирий потік
};

enum class FrameError {
    Erased,    // 0xFF 0xFF — далі в секторі порожньо
    BadMagic,  // байти є, але це не початок кадру
    BadLength, // len за межами дозволеного
    Truncated, // кадр не вміщується в те, що лишилось у секторі
    BadCrc     // запис обірвано знеструмленням або биті комірки
};

[[nodiscard]] std::string_view describe(FrameError error) noexcept;

struct Header {
    std::uint32_t seq{};
    std::uint64_t ts_ms{};
    std::uint16_t len{};
    Kind          kind{Kind::Raw};
};

struct Frame {
    Header                     header;
    std::span<const std::byte> payload;
    std::size_t                total{}; // повний розмір кадру на носії
};

[[nodiscard]] constexpr std::size_t frame_size(std::uint16_t payload_len) noexcept
{
    return kHeaderSize + payload_len + kCrcSize;
}

// Порівняння номерів із урахуванням переповнення лічильника: після
// 0xFFFFFFFF іде 1, і різниця, взята зі знаком, це переживає.
[[nodiscard]] constexpr bool seq_after(std::uint32_t a, std::uint32_t b) noexcept
{
    return static_cast<std::int32_t>(a - b) > 0;
}

[[nodiscard]] std::uint32_t crc32(std::span<const std::byte> data) noexcept;

// Складає кадр у dst і повертає його розмір.
[[nodiscard]] std::expected<std::size_t, FrameError>
encode(std::span<std::byte> dst, const Header& header,
       std::span<const std::byte> payload) noexcept;

// Розбирає кадр із початку raw. payload у результаті — зріз того самого
// буфера, копії немає; він живий, доки живий буфер читання.
[[nodiscard]] std::expected<Frame, FrameError>
parse(std::span<const std::byte> raw) noexcept;

} // namespace sf
