// Диспетчер шин: ідіоматичний типізований C++20 із RAII та span
#include <cstdint>
#include <cstddef>
#include <span>
#include <array>
#include <functional>
#include <optional>

enum class BusType : uint8_t {
    I2C,
    SPI
};

enum class BusDirection : uint8_t {
    Write,
    Read,
    WriteThenRead
};

struct BusTransaction {
    BusType                          type;
    uint8_t                          device_id; // I2C 7-bit адреса або пін CS
    uint8_t                          register_address;
    std::span<const uint8_t>         tx_buffer{};
    std::span<uint8_t>               rx_buffer{};
    std::function<void(bool)>        completion_callback{};
};

template <size_t QueueCapacity = 16>
class AsyncBusDispatcher {
public:
    AsyncBusDispatcher() = default;

    [[nodiscard]] bool submit(BusTransaction transaction) noexcept {
        const size_t next_head = (head_ + 1) % QueueCapacity;
        if (next_head == tail_) {
            return false; // Черга переповнена
        }
        queue_[head_] = std::move(transaction);
        head_ = next_head;

        if (!is_busy_) {
            process_next();
        }
        return true;
    }

    void on_transfer_complete_isr(bool success) noexcept {
        if (head_ != tail_) {
            auto& current = queue_[tail_];
            if (current.completion_callback) {
                current.completion_callback(success);
            }
            tail_ = (tail_ + 1) % QueueCapacity;
        }
        process_next();
    }

private:
    void process_next() noexcept {
        if (head_ == tail_) {
            is_busy_ = false;
            return;
        }
        is_busy_ = true;
        const auto& current = queue_[tail_];

        switch (current.type) {
        case BusType::I2C:
            // Запуск I2C DMA обміну з передачею current.rx_buffer.data()
            break;
        case BusType::SPI:
            // Затискання CS (current.device_id) та запуск повнодуплексного SPI DMA
            break;
        }
    }

    std::array<BusTransaction, QueueCapacity> queue_{};
    volatile size_t head_{0};
    volatile size_t tail_{0};
    volatile bool   is_busy_{false};
};
