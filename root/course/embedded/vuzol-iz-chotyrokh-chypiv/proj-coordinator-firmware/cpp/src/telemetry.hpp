#pragma once

// Телеметричний запис, його прапорці, CRC-16 і черга подій.

#include <array>
#include <bit>
#include <cstddef>
#include <cstdint>
#include <optional>
#include <span>
#include <type_traits>

#include "mcu.hpp"

namespace node {

inline constexpr std::size_t kRecordSize      = 24;
inline constexpr std::size_t kFlashPageSize   = 256;
inline constexpr std::size_t kFlashSectorSize = 4096;
inline constexpr std::uint32_t kFlashTotalSize = 0x100'0000u;   // 16 МБ
inline constexpr std::uint32_t kSectorCount   = kFlashTotalSize / kFlashSectorSize;
inline constexpr std::size_t kRecordsPerPage  = 10;   // 240 з 256 байтів
inline constexpr std::uint32_t kMasterWindowMs = 60'000u;

// ── Прапорці стану ───────────────────────────────────────────────────────
enum class Status : std::uint16_t {
    None         = 0x0000,
    SensorBmeOk  = 0x0001,   // вимірювання BME280 валідні
    RtcSyncOk    = 0x0002,   // час від DS3231, генератор не зривався
    FlashLogOk   = 0x0004,   // остання сторінка лягла у Flash без помилки
    Rs485Active  = 0x0008,   // ведучий опитував вузол нещодавно
};

constexpr Status operator|(Status a, Status b) noexcept {
    return static_cast<Status>(static_cast<std::uint16_t>(a) | static_cast<std::uint16_t>(b));
}
constexpr Status& operator|=(Status& a, Status b) noexcept { a = a | b; return a; }
constexpr bool has(Status set, Status flag) noexcept {
    return (static_cast<std::uint16_t>(set) & static_cast<std::uint16_t>(flag)) != 0u;
}

// ── Запис ────────────────────────────────────────────────────────────────
struct [[gnu::packed]] Record {
    std::uint32_t timestamp{};     // Unix-час від DS3231
    std::int32_t  temperature{};   // °C × 100
    std::uint32_t pressure{};      // Па × 100
    std::uint32_t humidity{};      // %RH × 1024
    std::uint16_t sequenceId{};    // порядковий номер зрізу
    Status        status{Status::None};
    std::uint16_t crc{};           // CRC-16 по перших 22 байтах
};

static_assert(sizeof(Record) == kRecordSize, "запис мусить бути рівно 24 байти");
static_assert(std::is_trivially_copyable_v<Record>);
static_assert(kRecordsPerPage * kRecordSize <= kFlashPageSize);

using RecordBytes = std::array<std::byte, kRecordSize>;

// ── CRC-16, поліном Modbus ───────────────────────────────────────────────
[[nodiscard]] constexpr std::uint16_t crc16(std::span<const std::byte> data) noexcept {
    std::uint16_t crc = 0xFFFFu;

    for (std::byte b : data) {
        crc ^= static_cast<std::uint16_t>(b);
        for (int i = 0; i < 8; ++i) {
            crc = (crc & 1u) ? static_cast<std::uint16_t>((crc >> 1) ^ 0xA001u)
                             : static_cast<std::uint16_t>(crc >> 1);
        }
    }
    return crc;
}

// bit_cast замість memcpy і reinterpret_cast: розкладка перевіряється
// компілятором, а не коментарем поруч.
[[nodiscard]] inline RecordBytes toBytes(const Record& rec) noexcept {
    return std::bit_cast<RecordBytes>(rec);
}

[[nodiscard]] inline Record fromBytes(const RecordBytes& raw) noexcept {
    return std::bit_cast<Record>(raw);
}

[[nodiscard]] inline std::uint16_t computeCrc(const Record& rec) noexcept {
    const RecordBytes raw = toBytes(rec);
    return crc16(std::span<const std::byte>{raw}.first(kRecordSize - sizeof(std::uint16_t)));
}

[[nodiscard]] inline bool valid(const Record& rec) noexcept {
    return computeCrc(rec) == rec.crc;
}

[[nodiscard]] inline bool erased(std::span<const std::byte> slot) noexcept {
    for (std::byte b : slot) {
        if (b != std::byte{0xFF}) return false;
    }
    return true;
}

// ── Події ────────────────────────────────────────────────────────────────
enum class Event : std::uint8_t {
    RtcTick,      // спадний фронт 1 Гц з DS3231
    Rs485Frame,   // USART зафіксував паузу t3.5 — кадр цілий
    Rs485Sent,    // відповідь дійшла до останнього стоп-біта
    FlashIdle,    // Flash звільнилася після стирання чи запису
};

// Кільце фіксованого розміру: пишуть переривання, читає головний цикл.
template <std::size_t N>
class EventQueue {
    static_assert((N & (N - 1)) == 0, "розмір черги — степінь двійки");

public:
    void push(Event ev) noexcept {
        const mcu::ScopedIrqLock lock;

        const std::size_t next = (head_ + 1) & (N - 1);
        if (next == tail_) {
            // Головний цикл десь застряг: подію втрачаємо свідомо й рахуємо.
            // Довше двох секунд цього однаково не буде — є сторожовий таймер.
            ++lost_;
            return;
        }
        slots_[head_] = ev;
        head_ = next;
    }

    [[nodiscard]] std::optional<Event> pop() noexcept {
        const mcu::ScopedIrqLock lock;

        if (tail_ == head_) return std::nullopt;

        const Event ev = slots_[tail_];
        tail_ = (tail_ + 1) & (N - 1);
        return ev;
    }

    [[nodiscard]] bool empty() const noexcept { return head_ == tail_; }
    [[nodiscard]] std::uint32_t lost() const noexcept { return lost_; }

private:
    std::array<Event, N> slots_{};
    volatile std::size_t head_{0};
    volatile std::size_t tail_{0};
    std::uint32_t lost_{0};
};

}  // namespace node
