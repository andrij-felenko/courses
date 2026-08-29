#pragma once

// Двійковий кадр телеметрії: 24 байти, big-endian, CRC-16/CCITT у хвості.
// Тут же живуть типи, що подорожують конвеєром: сирий пакет і нормалізована подія.

#include <chrono>
#include <cstdint>
#include <span>
#include <string>
#include <vector>

namespace ingest {

inline constexpr std::size_t kFrameSize = 24;
inline constexpr std::uint16_t kMagic = 0xAA55;
inline constexpr std::uint8_t kVersion = 1;

using Clock = std::chrono::system_clock;
using SteadyClock = std::chrono::steady_clock;

// Сирий пакет: байти з сокета плюс мітка часу прийому.
// Вектор усередині — саме тому пакет ходить конвеєром переміщенням, а не копією.
struct RawPacket {
    std::vector<std::uint8_t> data;
    Clock::time_point recv_wall{};      // t_recv за настінним годинником
    SteadyClock::time_point recv_mono{}; // монотонна мітка — нею міряємо затримку
    std::uint32_t peer_id{0};
};

// Розібраний кадр — числа вже у фізичних одиницях, але час ще не вирівняний.
struct TelemetryFrame {
    std::uint32_t device_id{0};
    std::uint32_t uptime_ms{0};
    double temperature_c{0.0};
    double humidity_pct{0.0};
    double battery_v{0.0};
    std::uint16_t seq{0};
    std::uint16_t status{0};
};

// Те, що піде у сховище пакетним записом.
struct NormalizedEvent {
    std::string device_id;
    Clock::time_point event_time{};          // t_event = t_recv - lag
    std::chrono::milliseconds lag{0};
    double temperature_c{0.0};
    double humidity_pct{0.0};
    double battery_v{0.0};
    std::uint16_t seq{0};
};

enum class FrameError {
    none = 0,
    bad_size,       // датаграма не завдовжки з кадр
    bad_magic,      // втрачена межа кадру
    bad_version,    // прошивка новіша за парсер
    crc_mismatch,   // кадр побився в дорозі
};

// Кількість значень enum — під масив лічильників у метриках.
inline constexpr std::size_t kFrameErrorCount = 5;

const char* to_string(FrameError error) noexcept;

// Результат розбору без винятків: на гарячому шляху битий кадр — норма, а не аварія.
struct DecodeResult {
    FrameError error{FrameError::none};
    TelemetryFrame frame{};

    explicit operator bool() const noexcept { return error == FrameError::none; }
};

std::uint16_t crc16_ccitt(std::span<const std::uint8_t> bytes) noexcept;

DecodeResult decode_frame(std::span<const std::uint8_t> bytes) noexcept;

// Фізичні межі давачів: усе поза ними — не дані, а несправність.
bool in_physical_range(const TelemetryFrame& frame) noexcept;

std::string format_device_id(std::uint32_t raw_id);

// Складання кадру потрібне генератору навантаження — і воно ж документує розкладку.
std::vector<std::uint8_t> encode_frame(std::uint32_t device_id, std::uint32_t uptime_ms,
                                       std::int16_t raw_temp, std::uint16_t raw_humidity,
                                       std::uint16_t raw_battery, std::uint16_t seq,
                                       std::uint16_t status);

}  // namespace ingest
