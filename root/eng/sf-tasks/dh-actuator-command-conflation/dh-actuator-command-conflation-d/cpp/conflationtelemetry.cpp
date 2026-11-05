#include <cstdint>
#include <atomic>
#include <algorithm>

class ConflationTelemetry {
public:
    struct Snapshot {
        uint32_t total_incoming{0};
        uint32_t suppressed_dedup{0};
        uint32_t suppressed_conflated{0};
        uint32_t suppressed_out_of_order{0};
        uint32_t dispatched_count{0};
        uint32_t max_latency_ms{0};
        float suppression_rate{0.0f};
    };

    void record_incoming() noexcept {
        total_incoming_.fetch_add(1, std::memory_order_relaxed);
    }

    void record_dedup() noexcept {
        suppressed_dedup_.fetch_add(1, std::memory_order_relaxed);
    }

    void record_conflated() noexcept {
        suppressed_conflated_.fetch_add(1, std::memory_order_relaxed);
    }

    void record_out_of_order() noexcept {
        suppressed_out_of_order_.fetch_add(1, std::memory_order_relaxed);
    }

    void record_dispatch(uint32_t latency_ms) noexcept {
        dispatched_count_.fetch_add(1, std::memory_order_relaxed);
        
        uint32_t current_max = max_latency_ms_.load(std::memory_order_relaxed);
        while (latency_ms > current_max && 
               !max_latency_ms_.compare_exchange_weak(current_max, latency_ms, std::memory_order_relaxed)) {
            // Атомарне оновлення максимальної затримки
        }
    }

    [[nodiscard]] Snapshot get_snapshot_and_reset() noexcept {
        Snapshot snap;
        snap.total_incoming = total_incoming_.exchange(0, std::memory_order_relaxed);
        snap.suppressed_dedup = suppressed_dedup_.exchange(0, std::memory_order_relaxed);
        snap.suppressed_conflated = suppressed_conflated_.exchange(0, std::memory_order_relaxed);
        snap.suppressed_out_of_order = suppressed_out_of_order_.exchange(0, std::memory_order_relaxed);
        snap.dispatched_count = dispatched_count_.exchange(0, std::memory_order_relaxed);
        snap.max_latency_ms = max_latency_ms_.exchange(0, std::memory_order_relaxed);

        uint32_t total_suppressed = snap.suppressed_dedup + snap.suppressed_conflated + snap.suppressed_out_of_order;
        if (snap.total_incoming > 0) {
            snap.suppression_rate = static_cast<float>(total_suppressed) / static_cast<float>(snap.total_incoming);
        }

        return snap;
    }

private:
    std::atomic<uint32_t> total_incoming_{0};
    std::atomic<uint32_t> suppressed_dedup_{0};
    std::atomic<uint32_t> suppressed_conflated_{0};
    std::atomic<uint32_t> suppressed_out_of_order_{0};
    std::atomic<uint32_t> dispatched_count_{0};
    std::atomic<uint32_t> max_latency_ms_{0};
};
