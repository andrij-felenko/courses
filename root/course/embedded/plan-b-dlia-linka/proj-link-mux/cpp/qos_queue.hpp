#pragma once

#include <algorithm>
#include <array>
#include <cstddef>
#include <cstdint>
#include <span>

namespace linkmux {

inline constexpr std::size_t kMaxPayload = 256;

enum class Priority : std::uint8_t {
    Critical  = 0,   // ручне пілотування, DISARM, RTL — не скидаємо ніколи
    Telemetry = 1,   // кути, координати, напруга — цінний лише найсвіжіший
    Video     = 2    // стиснений кадр — перше, чим жертвуємо
};

inline constexpr std::array<Priority, 3> kPriorityOrder{
    Priority::Critical, Priority::Telemetry, Priority::Video};

// Кадр цілком статичний: масив на місці, жодного вузла в купі.
struct Frame {
    std::uint16_t seq{0};
    std::uint16_t len{0};
    std::uint32_t stampMs{0};
    std::uint8_t  bearer{0};
    std::int16_t  rssiDbm{0};
    std::int8_t   snrDb{0};
    Priority      prio{Priority::Telemetry};
    std::array<std::uint8_t, kMaxPayload> payload{};

    [[nodiscard]] std::span<const std::uint8_t> bytes() const noexcept {
        return std::span<const std::uint8_t>(payload.data(), len);
    }

    static Frame make(Priority prio, std::span<const std::uint8_t> data,
                      std::uint16_t seq, std::uint32_t stampMs) noexcept;
};

enum class OverflowPolicy : std::uint8_t {
    Reject,      // критичне: повна черга — це помилка, а не тиша
    DropOldest,  // телеметрія: свіжі координати важать більше за старі
    DropNewest   // відео: смуги немає — новий кадр просто не беремо
};

// Смуга однієї важливості. Живе цілком у контексті задачі арбітра (кладе
// застосунок, забирає той самий цикл), тому атомарних лічильників тут немає.
template <std::size_t Capacity>
class FrameLane {
    static_assert(Capacity >= 2 && (Capacity & (Capacity - 1)) == 0,
                  "місткість мусить бути степенем двійки");

public:
    explicit FrameLane(OverflowPolicy policy) noexcept : policy_(policy) {}

    bool push(const Frame& frame) noexcept {
        if (size() >= Capacity) {
            switch (policy_) {
            case OverflowPolicy::Reject:
                return false;
            case OverflowPolicy::DropNewest:
                ++dropped_;
                return false;
            case OverflowPolicy::DropOldest:
                ++tail_;             // найстаріші координати вже нікому не треба
                ++dropped_;
                break;
            }
        }
        slots_[head_ & kMask] = frame;
        ++head_;
        peak_ = std::max(peak_, size());
        return true;
    }

    [[nodiscard]] const Frame* front() const noexcept {
        return empty() ? nullptr : &slots_[tail_ & kMask];
    }
    void popFront() noexcept {
        if (!empty()) { ++tail_; }
    }
    void flush() noexcept {
        dropped_ += static_cast<std::uint32_t>(size());
        tail_ = head_;
    }

    [[nodiscard]] std::size_t size() const noexcept { return head_ - tail_; }
    [[nodiscard]] bool empty() const noexcept { return head_ == tail_; }
    [[nodiscard]] std::uint32_t dropped() const noexcept { return dropped_; }
    [[nodiscard]] std::size_t peak() const noexcept { return peak_; }

private:
    static constexpr std::size_t kMask = Capacity - 1;

    std::array<Frame, Capacity> slots_{};
    std::size_t    head_{0};
    std::size_t    tail_{0};
    std::size_t    peak_{0};
    std::uint32_t  dropped_{0};
    OverflowPolicy policy_;
};

// Три ізольовані смуги: місткість і політика переповнення в кожної свої.
class TxQueues {
public:
    TxQueues() noexcept = default;

    bool push(Priority prio, const Frame& frame) noexcept;
    [[nodiscard]] const Frame* front(Priority prio) const noexcept;
    void popFront(Priority prio) noexcept;
    void flush(Priority prio) noexcept;
    [[nodiscard]] std::size_t size(Priority prio) const noexcept;
    [[nodiscard]] std::uint32_t dropped(Priority prio) const noexcept;

private:
    FrameLane<16> critical_{OverflowPolicy::Reject};
    FrameLane<8>  telemetry_{OverflowPolicy::DropOldest};
    FrameLane<4>  video_{OverflowPolicy::DropNewest};
};

}  // namespace linkmux
