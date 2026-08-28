#include <iostream>
#include <cstdint>
#include <shared_mutex>
#include <mutex>
#include <expected>
#include <string_view>

namespace mixed_fleet::consensus {

enum class FencingViolation {
    StaleEpochToken,
    IncompatibleMajorVersion
};

class EpochFencingCoordinator {
public:
    explicit EpochFencingCoordinator(uint64_t initial_epoch, uint32_t major_version) noexcept
        : current_epoch_(initial_epoch), active_major_(major_version) {}

    [[nodiscard]] std::expected<void, FencingViolation>
    verifyMutation(uint64_t request_token, uint32_t node_major) const noexcept {
        std::shared_lock lock(rw_mutex_);

        if (request_token < current_epoch_) {
            return std::unexpected(FencingViolation::StaleEpochToken);
        }

        if (node_major != active_major_) {
            return std::unexpected(FencingViolation::IncompatibleMajorVersion);
        }

        return {};
    }

    uint64_t incrementEpochOnHalt() noexcept {
        std::unique_lock lock(rw_mutex_);
        ++current_epoch_;
        return current_epoch_;
    }

    [[nodiscard]] uint64_t getActiveEpoch() const noexcept {
        std::shared_lock lock(rw_mutex_);
        return current_epoch_;
    }

private:
    mutable std::shared_mutex rw_mutex_;
    uint64_t current_epoch_{1};
    uint32_t active_major_{1};
};

} // namespace mixed_fleet::consensus
