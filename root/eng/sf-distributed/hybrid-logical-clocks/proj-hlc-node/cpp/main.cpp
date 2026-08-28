#include <iostream>
#include <chrono>
#include <mutex>
#include <cstdint>
#include <compare>
#include <expected>
#include <format>

enum class HlcError {
    ClockDriftExceeded,
    CounterOverflow
};

/* Незмінна структура мітки HLC із тристороннім порівнянням (C++20 spaceship operator) */
struct HlcTimestamp {
    uint64_t physical_ms{0};
    uint32_t logical{0};
    uint32_t node_id{0};

    auto operator<=>(const HlcTimestamp&) const = default;

    [[nodiscard]] uint64_t pack64() const noexcept {
        return ((physical_ms & 0x0000FFFFFFFFFFFFULL) << 16) | (logical & 0xFFFFULL);
    }

    static HlcTimestamp unpack64(uint64_t packed, uint32_t node_id = 0) noexcept {
        return HlcTimestamp{
            .physical_ms = (packed >> 16) & 0x0000FFFFFFFFFFFFULL,
            .logical = static_cast<uint32_t>(packed & 0xFFFFULL),
            .node_id = node_id
        };
    }
};

/* Потокобезпечний рушій годинника вузла */
class alignas(64) HybridLogicalClock {
public:
    explicit HybridLogicalClock(uint32_t node_id, std::chrono::milliseconds max_drift = std::chrono::milliseconds(500))
        : node_id_(node_id), max_drift_ms_(max_drift.count()), l_(get_system_time_ms()), c_(0) {}

    /* Генерація мітки для локальної події / відправки */
    [[nodiscard]] std::expected<HlcTimestamp, HlcError> now() noexcept {
        std::lock_guard<std::mutex> lock(mutex_);
        const uint64_t pt = get_system_time_ms();
        const uint64_t l_old = l_;

        if (pt > l_) {
            l_ = pt;
            c_ = 0;
        } else {
            l_ = l_old;
            if (c_ == UINT32_MAX) {
                return std::unexpected(HlcError::CounterOverflow);
            }
            ++c_;
        }

        return HlcTimestamp{
            .physical_ms = l_,
            .logical = c_,
            .node_id = node_id_
        };
    }

    /* Оновлення при отриманні повідомлення */
    [[nodiscard]] std::expected<HlcTimestamp, HlcError> update(const HlcTimestamp& remote_ts) noexcept {
        std::lock_guard<std::mutex> lock(mutex_);
        const uint64_t pt = get_system_time_ms();

        /* Перевірка максимального допустимого дрейфу */
        if (remote_ts.physical_ms > pt + max_drift_ms_) {
            return std::unexpected(HlcError::ClockDriftExceeded);
        }

        const uint64_t l_old = l_;
        uint64_t max_l = std::max({l_old, remote_ts.physical_ms, pt});

        if (max_l == l_old && max_l == remote_ts.physical_ms) {
            uint32_t max_c = std::max(c_, remote_ts.logical);
            if (max_c == UINT32_MAX) {
                return std::unexpected(HlcError::CounterOverflow);
            }
            c_ = max_c + 1;
        } else if (max_l == l_old) {
            if (c_ == UINT32_MAX) {
                return std::unexpected(HlcError::CounterOverflow);
            }
            ++c_;
        } else if (max_l == remote_ts.physical_ms) {
            if (remote_ts.logical == UINT32_MAX) {
                return std::unexpected(HlcError::CounterOverflow);
            }
            c_ = remote_ts.logical + 1;
        } else {
            c_ = 0;
        }

        l_ = max_l;

        return HlcTimestamp{
            .physical_ms = l_,
            .logical = c_,
            .node_id = node_id_
        };
    }

private:
    static uint64_t get_system_time_ms() noexcept {
        using namespace std::chrono;
        return duration_cast<milliseconds>(system_clock::now().time_since_epoch()).count();
    }

    const uint32_t node_id_;
    const uint64_t max_drift_ms_;
    uint64_t l_;
    uint32_t c_;
    mutable std::mutex mutex_;
};

int main() {
    HybridLogicalClock node_a(1);
    HybridLogicalClock node_b(2);

    auto send_result = node_a.now();
    if (!send_result) {
        std::cerr << "Failed to generate timestamp on Node A\n";
        return 1;
    }
    const HlcTimestamp ts_send = *send_result;
    std::cout << std::format("Node A [Send]: l={}, c={}, node={}\n",
                             ts_send.physical_ms, ts_send.logical, ts_send.node_id);

    auto recv_result = node_b.update(ts_send);
    if (!recv_result) {
        std::cerr << "Failed to update timestamp on Node B\n";
        return 1;
    }
    const HlcTimestamp ts_recv = *recv_result;
    std::cout << std::format("Node B [Recv]: l={}, c={}, node={}\n",
                             ts_recv.physical_ms, ts_recv.logical, ts_recv.node_id);

    const bool causal_order = (ts_send < ts_recv);
    std::cout << "Causality verified: " << (causal_order ? "YES" : "NO") << " (ts_send < ts_recv)\n";

    const uint64_t packed = ts_recv.pack64();
    std::cout << std::format("Packed 64-bit representation: 0x{:016X}\n", packed);

    return 0;
}
