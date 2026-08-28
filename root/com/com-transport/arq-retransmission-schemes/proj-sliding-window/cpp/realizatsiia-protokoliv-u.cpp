#include <iostream>
#include <vector>
#include <array>
#include <optional>
#include <cstdint>
#include <cstring>
#include <memory>
#include <algorithm>

namespace arq {

constexpr size_t MAX_PAYLOAD   = 64;
constexpr uint8_t SEQ_SPACE    = 8;  // M = 8
constexpr uint8_t WIN_SIZE_SR  = 4;  // W <= M / 2
constexpr int     RTO_TICKS    = 5;

enum class FrameType : uint8_t {
    Data = 1,
    Ack  = 2,
    Nack = 3
};

struct Frame {
    FrameType type{FrameType::Data};
    uint8_t   seq{0};
    uint8_t   ack{0};
    uint8_t   len{0};
    std::array<uint8_t, MAX_PAYLOAD> payload{};
    uint16_t  crc{0};

    [[nodiscard]] uint16_t compute_crc() const noexcept {
        uint16_t res = 0xFFFF;
        const auto* raw = reinterpret_cast<const uint8_t*>(this);
        const size_t sz = sizeof(Frame) - sizeof(uint16_t);
        for (size_t i = 0; i < sz; ++i) {
            res ^= static_cast<uint16_t>(raw[i]) << 8;
            for (int b = 0; b < 8; ++b) {
                if (res & 0x8000) res = (res << 1) ^ 0x1021;
                else res <<= 1;
            }
        }
        return res;
    }

    [[nodiscard]] bool is_valid() const noexcept {
        return compute_crc() == crc;
    }
};

[[nodiscard]] inline bool in_window(uint8_t seq, uint8_t base, uint8_t win) noexcept {
    const uint8_t dist = (seq - base + SEQ_SPACE) % SEQ_SPACE;
    return dist < win;
}

// ── Передавач Selective Repeat (окремий таймер на кожен кадр) ──
class SelectiveRepeatSender {
public:
    struct Slot {
        Frame frame;
        bool  acked{false};
        int   timer{0};
        bool  active{false};
    };

    SelectiveRepeatSender() = default;

    std::optional<Frame> send(const std::vector<uint8_t>& data) {
        if (!in_window(next_seq_, send_base_, WIN_SIZE_SR)) {
            return std::nullopt; // Вікно переповнено
        }

        Slot& slot = slots_[next_seq_];
        slot.frame.type = FrameType::Data;
        slot.frame.seq = next_seq_;
        slot.frame.ack = 0;
        slot.frame.len = static_cast<uint8_t>(std::min(data.size(), MAX_PAYLOAD));
        std::copy_n(data.begin(), slot.frame.len, slot.frame.payload.begin());
        slot.frame.crc = slot.frame.compute_crc();

        slot.acked = false;
        slot.timer = RTO_TICKS;
        slot.active = true;

        Frame out = slot.frame;
        next_seq_ = (next_seq_ + 1) % SEQ_SPACE;
        return out;
    }

    void on_ack(const Frame& ack) {
        if (!ack.is_valid() || ack.type != FrameType::Ack) return;

        const uint8_t acked_seq = ack.ack;
        if (in_window(acked_seq, send_base_, WIN_SIZE_SR)) {
            slots_[acked_seq].acked = true;
            slots_[acked_seq].active = false;

            // Зсув вікна передавача вправо, якщо підтверджено базовий слот
            while (slots_[send_base_].acked && send_base_ != next_seq_) {
                slots_[send_base_].acked = false;
                send_base_ = (send_base_ + 1) % SEQ_SPACE;
            }
        }
    }

    std::vector<Frame> tick() {
        std::vector<Frame> retransmissions;
        for (uint8_t i = 0; i < SEQ_SPACE; ++i) {
            if (slots_[i].active && !slots_[i].acked) {
                if (--slots_[i].timer <= 0) {
                    // Таймаут ЛИШЕ для цього конкретного кадру
                    slots_[i].timer = RTO_TICKS;
                    retransmissions.push_back(slots_[i].frame);
                }
            }
        }
        return retransmissions;
    }

    [[nodiscard]] uint8_t base() const noexcept { return send_base_; }

private:
    uint8_t send_base_{0};
    uint8_t next_seq_{0};
    std::array<Slot, SEQ_SPACE> slots_{};
};

// ── Приймач Selective Repeat (буфер out-of-order пакетів) ──
class SelectiveRepeatReceiver {
public:
    struct Slot {
        Frame frame;
        bool  received{false};
    };

    SelectiveRepeatReceiver() = default;

    std::optional<Frame> on_frame(const Frame& in, std::vector<std::vector<uint8_t>>& delivered) {
        if (!in.is_valid() || in.type != FrameType::Data) return std::nullopt;

        const uint8_t seq = in.seq;
        Frame ack;
        ack.type = FrameType::Ack;
        ack.seq = 0;
        ack.ack = seq; // Індивідуальне підтвердження саме цього кадру
        ack.len = 0;
        ack.crc = ack.compute_crc();

        if (in_window(seq, rcv_base_, WIN_SIZE_SR)) {
            slots_[seq].frame = in;
            slots_[seq].received = true;

            // Перевіряємо, чи можна видати накопичені кадри застосунку
            while (slots_[rcv_base_].received) {
                const auto& f = slots_[rcv_base_].frame;
                std::vector<uint8_t> payload(f.payload.begin(), f.payload.begin() + f.len);
                delivered.push_back(std::move(payload));

                slots_[rcv_base_].received = false;
                rcv_base_ = (rcv_base_ + 1) % SEQ_SPACE; // Зсув вікна прийому
            }
        }
        return ack;
    }

    [[nodiscard]] uint8_t base() const noexcept { return rcv_base_; }

private:
    uint8_t rcv_base_{0};
    std::array<Slot, SEQ_SPACE> slots_{};
};

} // namespace arq
