#include <cstdint>
#include <chrono>
#include <mutex>
#include <expected>
#include <thread>
#include <stdexcept>

class SnowflakeGenerator {
public:
    enum class Error {
        InvalidWorkerOrDatacenter,
        ClockRegressionExceeded
    };

    static constexpr uint64_t Epoch = 1288834974657ULL;
    static constexpr uint32_t WorkerBits = 5;
    static constexpr uint32_t DatacenterBits = 5;
    static constexpr uint32_t SequenceBits = 12;

    static constexpr uint64_t MaxWorkerId = (1ULL << WorkerBits) - 1;
    static constexpr uint64_t MaxDatacenterId = (1ULL << DatacenterBits) - 1;
    static constexpr uint64_t SequenceMask = (1ULL << SequenceBits) - 1;

    static constexpr uint32_t WorkerShift = SequenceBits;
    static constexpr uint32_t DatacenterShift = SequenceBits + WorkerBits;
    static constexpr uint32_t TimestampShift = SequenceBits + WorkerBits + DatacenterBits;

    SnowflakeGenerator(uint64_t worker_id, uint64_t datacenter_id)
        : worker_id_(worker_id), datacenter_id_(datacenter_id) {
        if (worker_id > MaxWorkerId || datacenter_id > MaxDatacenterId) {
            throw std::invalid_argument("Worker ID or Datacenter ID out of bounds");
        }
    }

    std::expected<uint64_t, Error> NextId() {
        std::lock_guard<std::mutex> lock(mutex_);
        auto ts = CurrentTimeMillis();

        if (ts < last_timestamp_) {
            const auto drift = last_timestamp_ - ts;
            if (drift < 5) {
                ts = WaitNextMillis(last_timestamp_);
            } else {
                return std::unexpected(Error::ClockRegressionExceeded);
            }
        }

        if (ts == last_timestamp_) {
            sequence_ = (sequence_ + 1) & SequenceMask;
            if (sequence_ == 0) {
                ts = WaitNextMillis(last_timestamp_);
            }
        } else {
            sequence_ = 0;
        }

        last_timestamp_ = ts;

        const uint64_t id = ((ts - Epoch) << TimestampShift)
                          | (datacenter_id_ << DatacenterShift)
                          | (worker_id_ << WorkerShift)
                          | sequence_;

        return id;
    }

private:
    static uint64_t CurrentTimeMillis() noexcept {
        using namespace std::chrono;
        return duration_cast<milliseconds>(
            system_clock::now().time_since_epoch()
        ).count();
    }

    static uint64_t WaitNextMillis(uint64_t last_ts) noexcept {
        auto ts = CurrentTimeMillis();
        while (ts <= last_ts) {
            std::this_thread::yield();
            ts = CurrentTimeMillis();
        }
        return ts;
    }

    const uint64_t worker_id_;
    const uint64_t datacenter_id_;
    uint64_t sequence_{0};
    uint64_t last_timestamp_{0};
    std::mutex mutex_;
};
