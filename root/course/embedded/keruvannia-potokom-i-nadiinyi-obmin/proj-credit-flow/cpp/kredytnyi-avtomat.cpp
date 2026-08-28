#include <array>
#include <span>
#include <optional>
#include <cstdint>
#include <algorithm>

enum class FrameType : uint8_t {
    Data = 0x01,
    CreditGrant = 0x02
};

struct PacketFrame {
    FrameType type{FrameType::Data};
    uint8_t seq_or_credit{0};
    uint8_t length{0};
    std::array<uint8_t, 64> payload{};
};

class CreditSender {
public:
    explicit constexpr CreditSender(int32_t initial_credits) noexcept
        : available_credits_{initial_credits} {}

    [[nodiscard]] bool can_send() const noexcept {
        return available_credits_ > 0;
    }

    [[nodiscard]] std::optional<PacketFrame> prepare_frame(std::span<const uint8_t> data) noexcept {
        if (available_credits_ <= 0 || data.size() > 64) {
            return std::nullopt;
        }

        PacketFrame frame;
        frame.type = FrameType::Data;
        frame.seq_or_credit = next_seq_++;
        frame.length = static_cast<uint8_t>(data.size());
        std::copy(data.begin(), data.end(), frame.payload.begin());

        --available_credits_;
        return frame;
    }

    void on_grant_received(uint8_t granted_credits) noexcept {
        available_credits_ += granted_credits;
    }

    [[nodiscard]] int32_t credits() const noexcept { return available_credits_; }

private:
    int32_t available_credits_{0};
    uint8_t next_seq_{0};
};

template <std::size_t MaxSlots = 4>
class CreditReceiver {
public:
    CreditReceiver() = default;

    [[nodiscard]] bool on_frame_received(const PacketFrame& frame) noexcept {
        if (frame.type != FrameType::Data) {
            return false;
        }
        if (occupied_slots_ >= MaxSlots) {
            return false; // Переповнення ліміту: помилка передавача
        }
        ++occupied_slots_;
        return true;
    }

    void release_slot() noexcept {
        if (occupied_slots_ > 0) {
            --occupied_slots_;
            ++pending_returns_;
        }
    }

    [[nodiscard]] std::optional<PacketFrame> make_grant_frame() noexcept {
        if (pending_returns_ == 0) {
            return std::nullopt;
        }

        PacketFrame frame;
        frame.type = FrameType::CreditGrant;
        frame.seq_or_credit = pending_returns_;
        frame.length = 0;

        pending_returns_ = 0;
        return frame;
    }

    [[nodiscard]] std::size_t occupied() const noexcept { return occupied_slots_; }

private:
    std::size_t occupied_slots_{0};
    uint8_t pending_returns_{0};
};
