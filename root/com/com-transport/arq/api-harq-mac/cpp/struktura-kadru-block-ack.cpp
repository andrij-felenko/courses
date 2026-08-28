#include <cstdint>
#include <bitset>

struct Ieee80211BlockAckFrame {
    uint16_t ba_control = 0;
    uint16_t starting_seq_ctrl = 0;
    uint64_t ba_bitmap = 0;

    [[nodiscard]] uint16_t starting_sequence_number() const noexcept {
        return (starting_seq_ctrl >> 4) & 0x0FFF;
    }

    [[nodiscard]] bool is_mpdu_acked(uint16_t seq_num) const noexcept {
        uint16_t ssn = starting_sequence_number();
        uint16_t diff = (seq_num - ssn) & 0x0FFF;
        if (diff < 64) {
            return (ba_bitmap & (1ULL << diff)) != 0;
        }
        return false;
    }
};
