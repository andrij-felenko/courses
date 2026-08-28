#include <cstdint>
#include <array>
#include <optional>

namespace mavlink_sec {

struct StreamKey {
    uint8_t sysid{0};
    uint8_t compid{0};
    uint8_t link_id{0};

    constexpr bool operator==(const StreamKey&) const noexcept = default;
};

struct StreamEntry {
    StreamKey key{};
    bool      active{false};
    uint64_t  last_timestamp{0};
};

class StreamTable {
public:
    static constexpr size_t kMaxStreams = 16;

    StreamEntry* getOrCreate(const StreamKey& key) noexcept {
        for (auto& entry : entries_) {
            if (entry.active && entry.key == key) {
                return &entry;
            }
        }
        for (auto& entry : entries_) {
            if (!entry.active) {
                entry.key = key;
                entry.active = true;
                entry.last_timestamp = 0;
                return &entry;
            }
        }
        return nullptr;
    }

    void reset() noexcept {
        entries_.fill(StreamEntry{});
    }

private:
    std::array<StreamEntry, kMaxStreams> entries_{};
};

} // namespace mavlink_sec
