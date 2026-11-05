#include <cstdint>
#include <atomic>

enum class TimeSyncState {
    Unsynced,
    Synced,
    Slewing
};

class TimeModule {
public:
    static TimeModule& instance() {
        static TimeModule inst;
        return inst;
    }

    // Поточний монотонний uptime у мілісекундах
    uint64_t get_uptime_ms() const {
        return fetch_system_ticks_ms();
    }

    // Обчислення поточного UTC wall-clock часу
    uint64_t get_wall_clock_ms() const {
        return get_uptime_ms() + offset_ms_.load(std::memory_order_relaxed);
    }

    // Оновлення зсуву при отриманні точного часу від NTP/RTC
    void set_utc_time(uint64_t utc_ms) {
        uint64_t current_up = get_uptime_ms();
        int64_t new_offset = static_cast<int64_t>(utc_ms) - static_cast<int64_t>(current_up);
        
        offset_ms_.store(new_offset, std::memory_order_release);
        state_.store(TimeSyncState::Synced, std::memory_order_release);
    }

    TimeSyncState get_state() const {
        return state_.load(std::memory_order_acquire);
    }

private:
    TimeModule() : offset_ms_(0), state_(TimeSyncState::Unsynced) {}
    
    std::atomic<int64_t> offset_ms_;
    std::atomic<TimeSyncState> state_;

    uint64_t fetch_system_ticks_ms() const;
};
