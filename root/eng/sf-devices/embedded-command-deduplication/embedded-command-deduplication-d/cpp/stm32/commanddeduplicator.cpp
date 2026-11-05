#include <cstdint>
#include <cstddef>
#include <array>
#include <algorithm>

template <std::size_t CacheSize = 64, std::size_t HashTableSize = 127, std::size_t MaxProbes = 8>
class CommandDeduplicator {
public:
    enum class TxState : uint8_t {
        Empty = 0,
        Processing,
        Completed,
        Failed
    };

    struct TxDescriptor {
        uint32_t tx_id{0};
        uint16_t sender_id{0};
        TxState state{TxState::Empty};
        uint32_t timestamp_ms{0};
        std::array<uint8_t, 16> response{};
        uint8_t response_len{0};
    };

    CommandDeduplicator() {
        hash_table_.fill(kInvalidSlot);
    }

    /* Метод перевірки та резервування транзакції без виклику heap */
    TxState CheckAndInsert(uint32_t tx_id, uint16_t sender_id, uint32_t current_time_ms, uint16_t& out_slot) {
        const uint16_t start_bucket = Hash(tx_id);

        /* 1. Пошук у хеш-таблиці з відкритою адресацією */
        for (std::size_t probe = 0; probe < MaxProbes; ++probe) {
            const uint16_t bucket = (start_bucket + probe) % HashTableSize;
            const uint16_t slot = hash_table_[bucket];

            if (slot == kInvalidSlot) {
                break;
            }

            const auto& desc = ring_buffer_[slot];
            if (desc.tx_id == tx_id && desc.sender_id == sender_id && desc.state != TxState::Empty) {
                out_slot = slot;
                return desc.state;
            }
        }

        /* 2. Витіснення найстарішого елемента FIFO */
        const uint16_t new_slot = head_idx_;
        auto& new_desc = ring_buffer_[new_slot];

        if (new_desc.state != TxState::Empty) {
            const uint16_t old_bucket = Hash(new_desc.tx_id);
            for (std::size_t probe = 0; probe < MaxProbes; ++probe) {
                const uint16_t b = (old_bucket + probe) % HashTableSize;
                if (hash_table_[b] == new_slot) {
                    hash_table_[b] = kInvalidSlot;
                    break;
                }
            }
        }

        /* Запис нового елемента */
        new_desc.tx_id = tx_id;
        new_desc.sender_id = sender_id;
        new_desc.state = TxState::Processing;
        new_desc.timestamp_ms = current_time_ms;
        new_desc.response_len = 0;

        for (std::size_t probe = 0; probe < MaxProbes; ++probe) {
            const uint16_t bucket = (start_bucket + probe) % HashTableSize;
            if (hash_table_[bucket] == kInvalidSlot) {
                hash_table_[bucket] = new_slot;
                break;
            }
        }

        head_idx_ = (head_idx_ + 1) % CacheSize;
        out_slot = new_slot;
        return TxState::Empty;
    }

    void CommitResponse(uint16_t slot, const uint8_t* resp_data, uint8_t resp_len) {
        if (slot >= CacheSize) return;

        auto& desc = ring_buffer_[slot];
        desc.response_len = std::min(resp_len, static_cast<uint8_t>(desc.response.size()));
        std::copy_n(resp_data, desc.response_len, desc.response.begin());
        desc.state = TxState::Completed;
    }

    const TxDescriptor& GetDescriptor(uint16_t slot) const {
        return ring_buffer_[slot];
    }

private:
    static constexpr uint16_t kInvalidSlot = 0xFFFFU;

    static constexpr uint16_t Hash(uint32_t tx_id) {
        return static_cast<uint16_t>(tx_id % HashTableSize);
    }

    std::array<TxDescriptor, CacheSize> ring_buffer_{};
    std::array<uint16_t, HashTableSize> hash_table_{};
    uint16_t head_idx_{0};
};
