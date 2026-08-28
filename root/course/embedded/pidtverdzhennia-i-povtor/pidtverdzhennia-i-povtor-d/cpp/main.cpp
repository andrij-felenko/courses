#include <cstdint>
#include <cstddef>
#include <span>
#include <array>
#include <algorithm>
#include <functional>

namespace arq {

constexpr size_t MaxPayload   = 64;
constexpr uint8_t MaxRetries  = 5;
constexpr uint32_t MinRtoMs   = 20;
constexpr uint32_t MaxRtoMs   = 2000;
constexpr uint32_t InitialRto = 100;

enum class FrameType : uint8_t {
    Data = 0x01,
    Ack  = 0x02,
    Nack = 0x03
};

struct [[gnu::packed]] Frame {
    FrameType type{FrameType::Data};
    uint8_t   seq{0};
    uint8_t   len{0};
    std::array<uint8_t, MaxPayload> payload{};
    uint16_t  crc{0};

    [[nodiscard]] uint16_t calculateCrc() const noexcept {
        uint16_t val = 0xFFFF;
        const auto* ptr = reinterpret_cast<const uint8_t*>(this);
        const size_t headerLen = sizeof(Frame) - sizeof(crc);
        for (size_t i = 0; i < headerLen; ++i) {
            val ^= static_cast<uint16_t>(ptr[i]) << 8;
            for (uint8_t b = 0; b < 8; ++b) {
                if (val & 0x8000) val = (val << 1) ^ 0x1021;
                else              val = val << 1;
            }
        }
        return val;
    }

    [[nodiscard]] bool isCrcValid() const noexcept {
        return calculateCrc() == crc;
    }
};

enum class SenderState : uint8_t {
    Idle,
    WaitAck,
    Failed
};

class Sender {
public:
    using TxCallback = std::function<void(std::span<const uint8_t>)>;

    explicit Sender(TxCallback txCb) noexcept : transmitCb_{std::move(txCb)} {}

    bool send(std::span<const uint8_t> data, uint32_t nowMs) {
        if (state_ != SenderState::Idle || data.size() > MaxPayload) {
            return false;
        }

        pendingFrame_.type = FrameType::Data;
        pendingFrame_.seq  = nextSeq_;
        pendingFrame_.len  = static_cast<uint8_t>(data.size());
        std::copy(data.begin(), data.end(), pendingFrame_.payload.begin());
        pendingFrame_.crc  = pendingFrame_.calculateCrc();

        txTimestamp_       = nowMs;
        retries_           = 0;
        isRetransmission_  = false;
        state_             = SenderState::WaitAck;

        emitCurrentFrame();
        return true;
    }

    void poll(uint32_t nowMs) {
        if (state_ != SenderState::WaitAck) return;

        if (nowMs - txTimestamp_ >= rtoMs_) {
            if (retries_ < MaxRetries) {
                ++retries_;
                isRetransmission_ = true;
                rtoMs_ = std::min(rtoMs_ * 2, MaxRtoMs);
                txTimestamp_ = nowMs;
                emitCurrentFrame();
            } else {
                state_ = SenderState::Failed;
            }
        }
    }

    void onAckReceived(const Frame& ack, uint32_t nowMs) noexcept {
        if (state_ != SenderState::WaitAck || !ack.isCrcValid()) {
            return;
        }

        if (ack.type == FrameType::Ack && ack.seq == nextSeq_) {
            if (!isRetransmission_) {
                updateRto(nowMs - txTimestamp_);
            }
            nextSeq_ ^= 1;
            state_ = SenderState::Idle;
        }
    }

    [[nodiscard]] SenderState state() const noexcept { return state_; }
    void resetState() noexcept { state_ = SenderState::Idle; }

private:
    void updateRto(uint32_t sampleRttMs) noexcept {
        const auto err = static_cast<int32_t>(sampleRttMs) - static_cast<int32_t>(srttScaled_ >> 3);
        srttScaled_ += err;

        const auto absErr = std::abs(err);
        rttvarScaled_ += absErr - static_cast<int32_t>(rttvarScaled_ >> 2);

        const auto calculatedRto = (srttScaled_ >> 3) + rttvarScaled_;
        rtoMs_ = std::clamp(calculatedRto, MinRtoMs, MaxRtoMs);
    }

    void emitCurrentFrame() {
        if (transmitCb_) {
            const auto* rawPtr = reinterpret_cast<const uint8_t*>(&pendingFrame_);
            transmitCb_(std::span<const uint8_t>(rawPtr, sizeof(Frame)));
        }
    }

    TxCallback   transmitCb_;
    SenderState  state_{SenderState::Idle};
    uint8_t      nextSeq_{0};
    uint8_t      retries_{0};
    uint32_t     txTimestamp_{0};
    bool         isRetransmission_{false};
    Frame        pendingFrame_{};

    uint32_t     srttScaled_{InitialRto << 3};
    uint32_t     rttvarScaled_{(InitialRto / 2) << 2};
    uint32_t     rtoMs_{InitialRto};
};

class Receiver {
public:
    using TxCallback      = std::function<void(std::span<const uint8_t>)>;
    using DeliverCallback = std::function<void(std::span<const uint8_t>)>;

    Receiver(TxCallback txCb, DeliverCallback deliverCb) noexcept
        : transmitCb_{std::move(txCb)}, deliverCb_{std::move(deliverCb)} {}

    void onFrameReceived(const Frame& frame) {
        if (!frame.isCrcValid()) return;

        if (frame.type == FrameType::Data) {
            Frame ackReply{};
            ackReply.type = FrameType::Ack;
            ackReply.seq  = frame.seq;
            ackReply.len  = 0;
            ackReply.crc  = ackReply.calculateCrc();

            if (frame.seq == expectedSeq_) {
                if (deliverCb_) {
                    deliverCb_(std::span<const uint8_t>(frame.payload.data(), frame.len));
                }
                expectedSeq_ ^= 1;
            }

            if (transmitCb_) {
                const auto* rawPtr = reinterpret_cast<const uint8_t*>(&ackReply);
                transmitCb_(std::span<const uint8_t>(rawPtr, sizeof(Frame)));
            }
        }
    }

private:
    TxCallback      transmitCb_;
    DeliverCallback deliverCb_;
    uint8_t         expectedSeq_{0};
};

} // namespace arq
