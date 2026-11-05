#include <cstdint>
#include <cstddef>
#include <array>

template <size_t Capacity>
class RingBuffer {
    static_assert((Capacity & (Capacity - 1)) == 0, "Capacity must be a power of two");
public:
    RingBuffer() : head_(0), tail_(0) {}

    bool PushFromIsr(uint8_t byte) {
        size_t next_head = (head_ + 1) & mask_;
        if (next_head != tail_) {
            buffer_[head_] = byte;
            head_ = next_head;
            return true;
        }
        return false;
    }

    bool Pop(uint8_t &byte) {
        if (head_ == tail_) {
            return false;
        }
        byte = buffer_[tail_];
        tail_ = (tail_ + 1) & mask_;
        return true;
    }

private:
    std::array<uint8_t, Capacity> buffer_;
    static constexpr size_t mask_ = Capacity - 1;
    volatile size_t head_;
    volatile size_t tail_;
};

class UartPipeline {
public:
    enum class State { Sof, Len, Data, Crc };

    UartPipeline() : state_(State::Sof), len_(0), index_(0), crc_(0), frames_received_(0), overruns_(0) {}

    void IsrPush(uint8_t byte) {
        if (!ring_.PushFromIsr(byte)) {
            overruns_++;
        }
    }

    void Process() {
        uint8_t byte;
        while (ring_.Pop(byte)) {
            ParseByte(byte);
        }
    }

    uint32_t GetFramesReceived() const { return frames_received_; }
    uint32_t GetOverruns() const { return overruns_; }

private:
    void ParseByte(uint8_t byte) {
        switch (state_) {
            case State::Sof:
                if (byte == 0xAA) {
                    state_ = State::Len;
                    crc_ = byte;
                }
                break;
            case State::Len:
                if (byte > 0 && byte <= payload_.size()) {
                    len_ = byte;
                    index_ = 0;
                    crc_ ^= byte;
                    state_ = State::Data;
                } else {
                    state_ = State::Sof;
                }
                break;
            case State::Data:
                payload_[index_++] = byte;
                crc_ ^= byte;
                if (index_ >= len_) {
                    state_ = State::Crc;
                }
                break;
            case State::Crc:
                if (byte == crc_) {
                    frames_received_++;
                }
                state_ = State::Sof;
                break;
        }
    }

    RingBuffer<256> ring_;
    State state_;
    uint8_t len_;
    uint8_t index_;
    std::array<uint8_t, 64> payload_;
    uint8_t crc_;
    uint32_t frames_received_;
    uint32_t overruns_;
};
