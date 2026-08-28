#include <cstring>
#include <algorithm>

class PbcastReceiver {
public:
    explicit PbcastReceiver(uint64_t sender_id, uint64_t initial_seq = 0)
        : sender_id_(sender_id), low_watermark_(initial_seq), received_mask_(0) {
        slots_.resize(BufferCapacity);
    }

    bool insert_packet(uint64_t seq_num, std::span<const uint8_t> data) {
        if (data.size() > MaxPayloadSize) return false;
        if (seq_num <= low_watermark_) return false;

        const uint64_t offset = seq_num - low_watermark_ - 1;
        if (offset >= BufferCapacity) return false;

        const size_t slot_idx = seq_num % BufferCapacity;
        slots_[slot_idx].seq_num = seq_num;
        slots_[slot_idx].payload.assign(data.begin(), data.end());
        slots_[slot_idx].valid = true;

        if (offset < MaskBits) {
            received_mask_ |= (1ULL << offset);
        }

        /* Просування водяної лінії для безперервної послідовності */
        while (received_mask_ & 1ULL) {
            low_watermark_++;
            received_mask_ >>= 1;

            const uint64_t next_seq = low_watermark_ + MaskBits;
            const size_t next_idx = next_seq % BufferCapacity;
            if (slots_[next_idx].valid && slots_[next_idx].seq_num == next_seq) {
                received_mask_ |= (1ULL << (MaskBits - 1));
            }
        }

        return true;
    }

    [[nodiscard]] std::optional<std::span<const uint8_t>> get_packet(uint64_t seq_num) const {
        const size_t idx = seq_num % BufferCapacity;
        if (slots_[idx].valid && slots_[idx].seq_num == seq_num) {
            return std::span<const uint8_t>(slots_[idx].payload);
        }
        return std::nullopt;
    }

    [[nodiscard]] uint64_t low_watermark() const noexcept { return low_watermark_; }
    [[nodiscard]] uint64_t received_mask() const noexcept { return received_mask_; }

private:
    uint64_t sender_id_;
    uint64_t low_watermark_;
    uint64_t received_mask_;
    std::vector<PacketSlot> slots_;
};
