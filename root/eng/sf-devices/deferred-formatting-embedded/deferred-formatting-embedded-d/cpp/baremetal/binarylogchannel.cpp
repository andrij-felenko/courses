#include <cstdint>
#include <cstddef>
#include <array>
#include <atomic>

template <size_t BufferSize = 1024>
class BinaryLogChannel {
    static_assert((BufferSize & (BufferSize - 1)) == 0, "Розмір буфера має бути степенем двійки");

public:
    BinaryLogChannel() : head_(0), tail_(0), dropped_(0) {}

    template <typename... Args>
    bool log(uint16_t event_id, Args... args) {
        constexpr size_t payload_size = (sizeof(Args) + ... + 0);
        constexpr size_t total_size = sizeof(uint16_t) + sizeof(uint8_t) + payload_size;

        uint32_t current_head = head_.load(std::memory_order_relaxed);
        uint32_t current_tail = tail_.load(std::memory_order_acquire);

        if ((BufferSize - (current_head - current_tail)) < total_size) {
            dropped_.fetch_add(1, std::memory_order_relaxed);
            return false;
        }

        /* Фіксація зарезервованого місця */
        head_.store(current_head + total_size, std::memory_order_release);

        write_byte(current_head, static_cast<uint8_t>(event_id & 0xFF));
        write_byte(current_head + 1, static_cast<uint8_t>((event_id >> 8) & 0xFF));
        write_byte(current_head + 2, static_cast<uint8_t>(payload_size));

        size_t offset = 3;
        auto serialize = [this, current_head, &offset](const auto& value) {
            const auto* bytes = reinterpret_cast<const uint8_t*>(&value);
            for (size_t i = 0; i < sizeof(value); ++i) {
                this->write_byte(current_head + offset + i, bytes[i]);
            }
            offset += sizeof(value);
        };

        (serialize(args), ...);
        return true;
    }

private:
    void write_byte(size_t index, uint8_t value) {
        storage_[index & (BufferSize - 1)] = value;
    }

    alignas(4) std::array<uint8_t, BufferSize> storage_{};
    std::atomic<uint32_t> head_;
    std::atomic<uint32_t> tail_;
    std::atomic<uint32_t> dropped_;
};
