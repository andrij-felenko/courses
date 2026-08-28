#include <iostream>
#include <vector>
#include <map>
#include <span>
#include <optional>
#include <expected>
#include <cstdint>
#include <chrono>
#include <cstring>
#include <algorithm>

namespace net {

inline constexpr size_t MaxIpPacketSize = 65535;
inline constexpr size_t MaxPayloadSize   = MaxIpPacketSize - 20;
inline constexpr auto ReassemblyTimeout = std::chrono::seconds(30);

enum class DefragError {
    PayloadTooLarge,
    UnalignedIntermediateFragment,
    ContradictoryTotalLength,
    AllocationFailed,
    CorruptedData
};

struct PacketKey {
    uint32_t src_ip{0};
    uint32_t dst_ip{0};
    uint16_t id{0};
    uint8_t  protocol{0};

    auto operator<=>(const PacketKey&) const = default;
};

class IpReassemblyEngine {
public:
    struct ReassemblyEntry {
        std::vector<uint8_t> buffer;
        std::map<uint16_t, uint16_t> intervals; /* start -> end */
        std::optional<uint16_t> expected_total_len;
        std::chrono::steady_clock::time_point created_at;

        explicit ReassemblyEntry(std::chrono::steady_clock::time_point now)
            : buffer(MaxPayloadSize, 0), created_at(now) {}
    };

    void cleanup_expired(std::chrono::steady_clock::time_point now = std::chrono::steady_clock::now()) {
        std::erase_if(queues_, [now](const auto& item) {
            return (now - item.second.created_at) > ReassemblyTimeout;
        });
    }

    std::expected<std::optional<std::vector<uint8_t>>, DefragError>
    process_fragment(const PacketKey& key,
                     uint16_t offset_8b,
                     bool more_fragments,
                     std::span<const uint8_t> payload,
                     std::chrono::steady_clock::time_point now = std::chrono::steady_clock::now()) {
        const uint32_t byte_offset = static_cast<uint32_t>(offset_8b) * 8;
        const uint32_t byte_end = byte_offset + static_cast<uint32_t>(payload.size());

        if (byte_end > MaxPayloadSize) {
            return std::unexpected(DefragError::PayloadTooLarge);
        }

        if (more_fragments && (payload.size() % 8 != 0)) {
            return std::unexpected(DefragError::UnalignedIntermediateFragment);
        }

        cleanup_expired(now);

        auto [it, inserted] = queues_.try_emplace(key, now);
        auto& entry = it->second;

        if (!more_fragments) {
            if (entry.expected_total_len && *entry.expected_total_len != static_cast<uint16_t>(byte_end)) {
                return std::unexpected(DefragError::ContradictoryTotalLength);
            }
            entry.expected_total_len = static_cast<uint16_t>(byte_end);
        }

        std::memcpy(entry.buffer.data() + byte_offset, payload.data(), payload.size());
        merge_interval(entry.intervals, static_cast<uint16_t>(byte_offset), static_cast<uint16_t>(byte_end));

        if (entry.expected_total_len.has_value()) {
            const uint16_t target_len = *entry.expected_total_len;
            if (!entry.intervals.empty()) {
                const auto& [first_start, first_end] = *entry.intervals.begin();
                if (first_start == 0 && first_end == target_len) {
                    std::vector<uint8_t> assembled(entry.buffer.begin(), entry.buffer.begin() + target_len);
                    queues_.erase(it);
                    return assembled;
                }
            }
        }

        return std::nullopt; /* Дейтаграма ще не повна, очікуємо решту фрагментів */
    }

private:
    static void merge_interval(std::map<uint16_t, uint16_t>& intervals, uint16_t start, uint16_t end) {
        auto it = intervals.upper_bound(start);
        if (it != intervals.begin()) {
            auto prev = std::prev(it);
            if (prev->second >= start) {
                start = prev->first;
                end = std::max(end, prev->second);
                it = intervals.erase(prev);
            }
        }
        while (it != intervals.end() && it->first <= end) {
            end = std::max(end, it->second);
            it = intervals.erase(it);
        }
        intervals[start] = end;
    }

    std::map<PacketKey, ReassemblyEntry> queues_;
};

} // namespace net
