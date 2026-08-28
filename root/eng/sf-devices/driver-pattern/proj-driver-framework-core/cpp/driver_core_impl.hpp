/* ============================================================================
 * ФАЙЛ: driver_core_impl.hpp - C++20 Реалізація статичного драйвера
 * ============================================================================ */
#ifndef DRIVER_CORE_IMPL_HPP
#define DRIVER_CORE_IMPL_HPP

#include "driver_core.hpp"

namespace embed::driver {

template <HardwareBusRegister THardware, size_t QueueCapacity = 8>
class StaticI2cDriver {
    static_assert((QueueCapacity & (QueueCapacity - 1)) == 0, "Capacity must be power of 2");
public:
    explicit StaticI2cDriver(THardware& hw) noexcept : hw_(hw), state_(Status::Uninitialized) {}

    [[nodiscard]] Status init() noexcept {
        hw_.generate_stop();
        state_.store(Status::Ok, std::memory_order_release);
        return Status::Ok;
    }

    [[nodiscard]] Status submit(Transaction trans) noexcept {
        if (state_.load(std::memory_order_relaxed) == Status::Uninitialized) {
            return Status::Uninitialized;
        }

        const size_t head = queue_head_.load(std::memory_order_relaxed);
        const size_t next_head = (head + 1) & (QueueCapacity - 1);
        if (next_head == queue_tail_.load(std::memory_order_acquire)) {
            return Status::Overflow;
        }

        queue_[head] = trans;
        queue_head_.store(next_head, std::memory_order_release);

        // Якщо шина вільна — запускаємо виконання
        try_start_next();
        return Status::Ok;
    }

    void poll_isr() noexcept {
        if (!active_transaction_.has_value()) return;

        if (hw_.is_nack()) {
            stats_.nack_errors++;
            hw_.generate_stop();
            active_transaction_.reset();
            try_start_next();
            return;
        }

        auto& trans = *active_transaction_;
        if (trans.op_type == OpType::Write) {
            if (hw_.is_tx_empty()) {
                if (tx_offset_ < trans.tx_data.size()) {
                    hw_.write_data(trans.tx_data[tx_offset_++]);
                } else {
                    hw_.generate_stop();
                    stats_.successful_transfers++;
                    active_transaction_.reset();
                    try_start_next();
                }
            }
        } else if (trans.op_type == OpType::Read) {
            if (hw_.is_rx_ready()) {
                if (rx_offset_ < trans.rx_data.size()) {
                    trans.rx_data[rx_offset_++] = hw_.read_data();
                }
                if (rx_offset_ >= trans.rx_data.size()) {
                    hw_.generate_stop();
                    stats_.successful_transfers++;
                    active_transaction_.reset();
                    try_start_next();
                }
            }
        }
    }

    [[nodiscard]] DriverStats stats() const noexcept { return stats_; }

private:
    void try_start_next() noexcept {
        if (active_transaction_.has_value()) return;

        const size_t tail = queue_tail_.load(std::memory_order_relaxed);
        if (tail == queue_head_.load(std::memory_order_acquire)) {
            return; // Черга порожня
        }

        active_transaction_ = queue_[tail];
        queue_tail_.store((tail + 1) & (QueueCapacity - 1), std::memory_order_release);

        tx_offset_ = 0;
        rx_offset_ = 0;
        stats_.total_transfers++;

        hw_.generate_start();
        hw_.write_data(static_cast<uint8_t>(active_transaction_->dev_addr << 1));
    }

    THardware& hw_;
    std::atomic<Status> state_;
    std::array<Transaction, QueueCapacity> queue_{};
    std::atomic<size_t> queue_head_{0};
    std::atomic<size_t> queue_tail_{0};
    std::optional<Transaction> active_transaction_{std::nullopt};
    size_t tx_offset_{0};
    size_t rx_offset_{0};
    DriverStats stats_{};
};

} // namespace embed::driver

#endif /* DRIVER_CORE_IMPL_HPP */
