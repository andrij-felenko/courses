#include <cstdint>
#include <atomic>

struct PpsEvent {
    uint64_t pps_uptime_us;
    bool valid;
};

class PpsSyncHandler {
public:
    // Викликається з апаратного ISR за зростаючим фронтом PPS
    void handlePpsInterruptFromIsr(uint64_t capturedUptimeUs) noexcept {
        captured_pps_uptime_.store(capturedUptimeUs, std::memory_order_release);
        pps_flag_.store(true, std::memory_order_release);
    }

    // Викликається фоновою задачею після розбору NMEA пакета
    bool processGnssMessage(uint64_t nmeaUtcSeconds, int64_t& calculatedOffsetOut) noexcept {
        if (!pps_flag_.load(std::memory_order_acquire)) {
            return false; // Імпульсу PPS ще не було
        }

        uint64_t ppsUptime = captured_pps_uptime_.load(std::memory_order_acquire);
        pps_flag_.store(false, std::memory_order_release);

        uint64_t targetWallUs = nmeaUtcSeconds * 1000000ULL;
        calculatedOffsetOut = static_cast<int64_t>(targetWallUs) - static_cast<int64_t>(ppsUptime);
        return true;
    }

private:
    std::atomic<uint64_t> captured_pps_uptime_{0};
    std::atomic<bool> pps_flag_{false};
};
