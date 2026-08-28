#include <cstdint>
#include <shared_mutex>
#include <mutex>
#include <optional>

enum class StorageTier : uint8_t { Hot, Warm, Cold };
enum class ChunkState : uint8_t { Online, Migrating };

class ChunkDescriptor {
public:
    ChunkDescriptor(uint64_t id, uint32_t crc)
        : id_(id), checksum_(crc), tier_(StorageTier::Hot), state_(ChunkState::Online) {}

    bool commit_migration(StorageTier new_tier, uint32_t verified_crc) {
        std::unique_lock lock(rw_mutex_);
        if (state_ != ChunkState::Migrating || checksum_ != verified_crc) {
            state_ = ChunkState::Online; // Відкат при збої
            return false;
        }
        tier_ = new_tier;
        state_ = ChunkState::Online;
        return true;
    }

    StorageTier get_tier() const {
        std::shared_lock lock(rw_mutex_);
        return tier_;
    }

private:
    const uint64_t id_;
    const uint32_t checksum_;
    StorageTier tier_;
    ChunkState state_;
    mutable std::shared_mutex rw_mutex_;
};
