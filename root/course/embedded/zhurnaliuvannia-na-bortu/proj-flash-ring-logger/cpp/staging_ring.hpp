// Проміжна черга в RAM для записів із обробників переривань.
//
// Писати у SPI Flash із переривання не можна: Page Program триває 0.7–3.0 мс,
// а обробник мусить укластися в одиниці мікросекунд. Тому ISR кладе сюди рівно
// 12 байтів і виходить, а фонова задача з найнижчим пріоритетом переносить їх
// у Flash.
//
// Черга розрахована на ОДНОГО виробника й ОДНОГО споживача. Якщо джерел
// переривань кілька, вони мусять іти через одне переривання найвищого
// пріоритету: два ISR, що одночасно рухають head, зіпсують чергу.

#pragma once

#include <array>
#include <atomic>
#include <cstddef>
#include <cstdint>
#include <optional>

#include "record_codec.hpp"
#include "ring_logger.hpp"

namespace fl {

inline constexpr std::size_t kStageCapacity = 32;

// Рівно 12 байтів: 1 + 1 + 2 + 4 + 4. Довшого навантаження в перериванні
// не буває — туди їде код події й одне число.
struct StagedRecord {
    Level         level{Level::Trace};
    std::uint8_t  moduleId{0};
    std::uint16_t arg{0};
    std::uint32_t timestampMs{0};
    std::uint32_t tokenId{0};
};
static_assert(sizeof(StagedRecord) == 12, "кадр черги мусить лишатися 12-байтним");

template <std::size_t Capacity>
class StagingRing {
    static_assert(Capacity >= 2 && (Capacity & (Capacity - 1)) == 0,
                  "ємність мусить бути степенем двійки: індекс береться маскою");

public:
    // Викликається з переривання.
    bool push(const StagedRecord& record) noexcept
    {
        const std::uint32_t head = head_.load(std::memory_order_relaxed);
        const std::uint32_t tail = tail_.load(std::memory_order_acquire);

        // Різниця беззнакова, тож переповнення лічильників рахунку не ламає.
        if (head - tail >= Capacity) {
            dropped_.fetch_add(1, std::memory_order_relaxed);
            return false;
        }

        slots_[head & (Capacity - 1)] = record;
        // release: слот заповнено ДО того, як задача побачить новий head.
        head_.store(head + 1, std::memory_order_release);
        return true;
    }

    // Викликається з фонової задачі.
    std::optional<StagedRecord> pop() noexcept
    {
        const std::uint32_t tail = tail_.load(std::memory_order_relaxed);
        const std::uint32_t head = head_.load(std::memory_order_acquire);
        if (head == tail) {
            return std::nullopt;
        }

        const StagedRecord record = slots_[tail & (Capacity - 1)];
        tail_.store(tail + 1, std::memory_order_release);
        return record;
    }

    [[nodiscard]] std::uint32_t takeDropped() noexcept
    {
        return dropped_.exchange(0, std::memory_order_relaxed);
    }

private:
    std::array<StagedRecord, Capacity> slots_{};
    std::atomic<std::uint32_t> head_{0};
    std::atomic<std::uint32_t> tail_{0};
    std::atomic<std::uint32_t> dropped_{0};
};

// Переносить усе накопичене у Flash. Якщо кадри губилися — додає окремий
// запис Warn із їх кількістю: мовчазна діра в журналі гірша за визнану втрату.
template <std::size_t Capacity>
std::size_t drain(StagingRing<Capacity>& ring, RingLogger& logger)
{
    std::size_t written = 0;
    std::uint32_t lastTimestamp = logger.lastTimestampMs();

    while (const std::optional<StagedRecord> record = ring.pop()) {
        lastTimestamp = record->timestampMs;

        std::array<std::byte, 2> payload{};
        putU16(payload, record->arg);

        if (!logger.append(record->level, record->moduleId, record->timestampMs, record->tokenId,
                           payload)) {
            // Кристал не бере запис. Далі черпати немає сенсу — решта кадрів
            // лишається в черзі до наступного заходу, а не гине по одному.
            break;
        }
        ++written;
    }

    if (const std::uint32_t dropped = ring.takeDropped(); dropped > 0) {
        std::array<std::byte, 4> payload{};
        putU32(payload, dropped);
        static_cast<void>(logger.append(Level::Warn, kLoggerModule, lastTimestamp, kTokenIsrDrops,
                                        payload));
    }

    return written;
}

}  // namespace fl
