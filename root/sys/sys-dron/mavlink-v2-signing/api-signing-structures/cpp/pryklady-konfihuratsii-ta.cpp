#include <mavlink.h>
#include <array>
#include <span>
#include <chrono>
#include <cstdint>
#include <algorithm>

class MavlinkSigningContext {
public:
    using SecretKey = std::array<uint8_t, 32>;

    MavlinkSigningContext(uint8_t channel_idx, const SecretKey& key, uint8_t link_id)
        : channel_(channel_idx) {
        signing_ = {};
        streams_ = {};

        signing_.flags = MAVLINK_SIGNING_FLAG_SIGN_OUTGOING;
        signing_.link_id = link_id;
        signing_.timestamp = calculateCurrentMavlinkTimestamp();
        std::copy(key.begin(), key.end(), signing_.secret_key);
        signing_.streams = &streams_;
        signing_.accept_unsigned_callback = &MavlinkSigningContext::onFilterUnsigned;

        auto* status = mavlink_get_channel_status(channel_);
        status->signing = &signing_;
        status->signing_streams = &streams_;
    }

    void stepMonotonicTime() noexcept {
        const uint64_t now_ts = calculateCurrentMavlinkTimestamp();
        if (now_ts > signing_.timestamp) {
            signing_.timestamp = now_ts;
        } else {
            ++signing_.timestamp; // Гарантія суворої монотонності
        }
    }

    [[nodiscard]] uint8_t linkId() const noexcept { return signing_.link_id; }
    [[nodiscard]] uint64_t currentTimestamp() const noexcept { return signing_.timestamp; }

private:
    static bool onFilterUnsigned(const mavlink_status_t*, uint32_t msgid) noexcept {
        switch (msgid) {
            case MAVLINK_MSG_ID_HEARTBEAT:
            case MAVLINK_MSG_ID_ATTITUDE:
            case MAVLINK_MSG_ID_GLOBAL_POSITION_INT:
            case MAVLINK_MSG_ID_SYS_STATUS:
                return true;
            default:
                return false;
        }
    }

    static uint64_t calculateCurrentMavlinkTimestamp() noexcept {
        using namespace std::chrono;
        const auto now = system_clock::now();
        const auto us = duration_cast<microseconds>(now.time_since_epoch()).count();
        constexpr int64_t kMavlinkEpochUs = 1420070400000000LL; // 2015-01-01 GMT
        
        if (us <= kMavlinkEpochUs) {
            return 1ULL;
        }
        return static_cast<uint64_t>((us - kMavlinkEpochUs) / 10);
    }

    uint8_t channel_;
    mavlink_signing_t signing_{};
    mavlink_signing_streams_t streams_{};
};
