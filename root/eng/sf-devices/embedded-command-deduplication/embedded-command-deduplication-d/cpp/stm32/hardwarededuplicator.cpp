#include <cstdint>
#include <cstddef>
#include <array>
#include <algorithm>
#include <atomic>

template <std::size_t RingCapacity = 64, std::size_t HashTableSize = 128, std::size_t MaxProbes = 8>
class HardwareDeduplicator {
    static_assert((RingCapacity & (RingCapacity - 1)) == 0, "Ring capacity must be a power of two");
    static_assert((HashTableSize & (HashTableSize - 1)) == 0, "Hash table size must be a power of two");

public:
    enum class State : uint8_t {
        Free = 0,
        InProgress,
        Committed,
        Aborted
    };

    struct alignas(32) Descriptor {
        uint32_t tx_id{0};
        uint32_t timestamp_cycles{0};
        uint16_t sender_id{0};
        State state{State::Free};
        uint8_t response_len{0};
        std::array<uint8_t, 16> response{};
        uint8_t padding[4]{};
    };

    HardwareDeduplicator() noexcept {
        hash_table_.fill(kInvalidSlot);
    }

    State CheckAndClaim(uint32_t tx_id, uint16_t sender_id, uint16_t& out_slot) noexcept {
        const uint16_t start_bucket = static_cast<uint16_t>(tx_id & kHashMask);

        for (std::size_t probe = 0; probe < MaxProbes; ++probe) {
            const uint16_t bucket = static_cast<uint16_t>((start_bucket + probe) & kHashMask);
            const uint16_t slot = hash_table_[bucket];

            if (slot == kInvalidSlot) {
                break;
            }

            const auto& desc = ring_[slot];
            if (desc.tx_id == tx_id && desc.sender_id == sender_id && desc.state != State::Free) {
                out_slot = slot;
                return desc.state;
            }
        }

        const uint32_t current_head = head_index_.fetch_add(1, std::memory_order_relaxed);
        const uint16_t new_slot = static_cast<uint16_t>(current_head & kRingMask);
        auto& target = ring_[new_slot];

        if (target.state != State::Free) {
            const uint16_t old_bucket = static_cast<uint16_t>(target.tx_id & kHashMask);
            for (std::size_t probe = 0; probe < MaxProbes; ++probe) {
                const uint16_t b = static_cast<uint16_t>((old_bucket + probe) & kHashMask);
                if (hash_table_[b] == new_slot) {
                    hash_table_[b] = kInvalidSlot;
                    break;
                }
            }
        }

        target.tx_id = tx_id;
        target.sender_id = sender_id;
        target.timestamp_cycles = *reinterpret_cast<volatile uint32_t*>(0xE0001004UL);
        target.response_len = 0;
        target.state = State::InProgress;

        for (std::size_t probe = 0; probe < MaxProbes; ++probe) {
            const uint16_t b = static_cast<uint16_t>((start_bucket + probe) & kHashMask);
            if (hash_table_[b] == kInvalidSlot) {
                hash_table_[b] = new_slot;
                break;
            }
        }

        std::atomic_thread_fence(std::memory_order_release);
        out_slot = new_slot;
        return State::Free;
    }

    void CommitResult(uint16_t slot, const uint8_t* payload, uint8_t len) noexcept {
        if (slot >= RingCapacity) return;

        auto& desc = ring_[slot];
        desc.response_len = std::min(len, static_cast<uint8_t>(desc.response.size()));
        std::copy_n(payload, desc.response_len, desc.response.begin());

        std::atomic_thread_fence(std::memory_order_release);
        desc.state = State::Committed;
    }

private:
    static constexpr uint16_t kInvalidSlot = 0xFFFFU;
    static constexpr std::size_t kHashMask = HashTableSize - 1;
    static constexpr std::size_t kRingMask = RingCapacity - 1;

    alignas(32) std::array<Descriptor, RingCapacity> ring_{};
    std::array<uint16_t, HashTableSize> hash_table_{};
    std::atomic<uint32_t> head_index_{0};
};
