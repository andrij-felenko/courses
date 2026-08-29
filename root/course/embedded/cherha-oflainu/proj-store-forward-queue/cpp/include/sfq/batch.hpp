// batch.hpp — пачка кадрів на одну радіопередачу.
//
// Обмежена і числом кадрів, і байтами: канал усе одно має свій MTU, і
// слати більше немає сенсу. Пам'ять — усередині об'єкта; навантаження
// кадрів дивляться у власну арену пачки, тому копіювати її не можна:
// spans пережили б своє сховище.
#pragma once

#include <algorithm>
#include <array>
#include <cstddef>
#include <cstdint>
#include <span>

#include "sfq/frame.hpp"

namespace sfq {

class DrainBatch {
public:
    static constexpr std::size_t kMaxRecords = 8;
    static constexpr std::size_t kArenaBytes = 1024;

    struct Item {
        std::uint32_t seq{};
        std::uint64_t timestamp_ms{};
        RecordType type{};
        Priority priority{};
        std::span<const std::byte> payload{};
    };

    DrainBatch() = default;
    DrainBatch(const DrainBatch&) = delete;
    DrainBatch& operator=(const DrainBatch&) = delete;

    void clear() noexcept
    {
        count_ = 0;
        used_ = 0;
    }

    // false — пачка добита: або кадрів уже вісім, або арена не вміщує.
    [[nodiscard]] bool try_append(const FrameHeader& hdr, std::span<const std::byte> payload) noexcept
    {
        if (count_ == kMaxRecords || used_ + payload.size() > kArenaBytes) {
            return false;
        }

        const auto slot = std::span{arena_}.subspan(used_, payload.size());
        std::ranges::copy(payload, slot.begin());
        used_ += payload.size();

        items_[count_++] = Item{
            .seq = hdr.seq,
            .timestamp_ms = hdr.timestamp_ms,
            .type = hdr.type,
            .priority = hdr.priority,
            .payload = slot,
        };
        return true;
    }

    [[nodiscard]] std::span<const Item> items() const noexcept
    {
        return std::span{items_.data(), count_};
    }
    [[nodiscard]] bool empty() const noexcept { return count_ == 0; }
    [[nodiscard]] std::size_t size() const noexcept { return count_; }
    [[nodiscard]] std::size_t bytes() const noexcept { return used_; }

    [[nodiscard]] std::uint32_t first_seq() const noexcept
    {
        return count_ == 0 ? 0 : items_[0].seq;
    }
    [[nodiscard]] std::uint32_t last_seq() const noexcept
    {
        return count_ == 0 ? 0 : items_[count_ - 1].seq;
    }

private:
    std::array<Item, kMaxRecords> items_{};
    std::array<std::byte, kArenaBytes> arena_{};
    std::size_t count_{};
    std::size_t used_{};
};

}  // namespace sfq
