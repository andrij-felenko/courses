#include <cstdint>
#include <atomic>
#include <algorithm>

class ClockSlewer {
public:
    static constexpr int64_t kMaxSlewPpm = 500; // 500 PPM max speed

    void setTimeStepping(int64_t targetWallUs, int64_t currentUptimeUs) noexcept {
        int64_t newOffset = targetWallUs - currentUptimeUs;
        base_offset_us_.store(newOffset, std::memory_order_relaxed);
        error_remaining_us_.store(0, std::memory_order_relaxed);
        last_update_uptime_.store(currentUptimeUs, std::memory_order_release);
    }

    void adjustSlewing(int64_t errorUs) noexcept {
        error_remaining_us_.fetch_add(errorUs, std::memory_order_relaxed);
    }

    int64_t getWallTimeUs(int64_t currentUptimeUs) noexcept {
        int64_t lastUptime = last_update_uptime_.load(std::memory_order_relaxed);
        int64_t dt = currentUptimeUs - lastUptime;
        
        if (dt > 0) {
            int64_t error = error_remaining_us_.load(std::memory_order_relaxed);
            if (error != 0) {
                int64_t maxSlewDelta = (dt * kMaxSlewPpm) / 1000000LL;
                int64_t applySlew = 0;
                
                if (error > 0) {
                    applySlew = std::min(error, maxSlewDelta);
                } else {
                    applySlew = std::max(error, -maxSlewDelta);
                }
                
                base_offset_us_.fetch_add(applySlew, std::memory_order_relaxed);
                error_remaining_us_.fetch_sub(applySlew, std::memory_order_relaxed);
                last_update_uptime_.store(currentUptimeUs, std::memory_order_relaxed);
            }
        }
        
        return currentUptimeUs + base_offset_us_.load(std::memory_order_relaxed);
    }

private:
    std::atomic<int64_t> base_offset_us_{0};
    std::atomic<int64_t> error_remaining_us_{0};
    std::atomic<int64_t> last_update_uptime_{0};
};
