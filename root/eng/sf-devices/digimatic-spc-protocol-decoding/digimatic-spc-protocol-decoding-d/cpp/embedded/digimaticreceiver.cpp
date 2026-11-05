#include <cstdint>
#include <cstddef>
#include <array>
#include <atomic>

template <size_t Capacity = 32>
class DigimaticReceiver {
    static_assert((Capacity & (Capacity - 1)) == 0, "Capacity must be a power of two");

public:
    struct Measurement {
        int32_t value_um{0};      // Відстань у мікрометрах (1 мкм = 10⁻⁶ м)
        bool is_inch{false};       // Одиниці вимірювання
        bool is_negative{false};   // Знак результату
        bool valid{false};         // Валідність пакета
    };

    DigimaticReceiver() : head_(0), tail_(0), bit_counter_(0), accumulator_(0) {}

    // Обробник спаду тактової лінії CLK (викликається з апаратного переривання)
    void onClockFallingEdge(bool data_level) noexcept {
        if (bit_counter_ < 52) {
            if (data_level) {
                accumulator_ |= (uint64_t{1} << bit_counter_);
            }
            bit_counter_++;

            if (bit_counter_ == 52) {
                size_t current_head = head_.load(std::memory_order_relaxed);
                size_t next_head = (current_head + 1) & (Capacity - 1);

                if (next_head != tail_.load(std::memory_order_acquire)) {
                    buffer_[current_head] = accumulator_;
                    head_.store(next_head, std::memory_order_release);
                }
                bit_counter_ = 0;
                accumulator_ = 0;
            }
        }
    }

    // Зчитування та декодування чергового вимірювання
    bool read(Measurement &out) noexcept {
        size_t current_tail = tail_.load(std::memory_order_relaxed);
        if (current_tail == head_.load(std::memory_order_acquire)) {
            return false; // Буфер порожній
        }

        uint64_t raw = buffer_[current_tail];
        tail_.store((current_tail + 1) & (Capacity - 1), std::memory_order_release);

        return decodeFrame(raw, out);
    }

private:
    std::array<uint64_t, Capacity> buffer_{};
    std::atomic<size_t> head_{0};
    std::atomic<size_t> tail_{0};
    uint8_t bit_counter_{0};
    uint64_t accumulator_{0};

    static bool decodeFrame(uint64_t raw, Measurement &out) noexcept {
        constexpr std::array<int32_t, 6> PowersOfTen{1, 10, 100, 1000, 10000, 100000};
        std::array<uint8_t, 13> d{};

        for (size_t i = 0; i < 13; ++i) {
            d[i] = static_cast<uint8_t>((raw >> (i * 4)) & 0x0F);
        }

        // Перевірка преамбули
        if (d[0] != 0x0F || d[1] != 0x0F || d[2] != 0x0F || d[3] != 0x0F) {
            out.valid = false;
            return false;
        }

        // Валідація BCD
        for (size_t i = 5; i <= 10; ++i) {
            if (d[i] > 9) {
                out.valid = false;
                return false;
            }
        }

        int32_t raw_val = d[5] + d[6]*10 + d[7]*100 + d[8]*1000 + d[9]*10000 + d[10]*100000;
        uint8_t exp = d[11] > 5 ? 5 : d[11];
        int32_t val_um = (raw_val * 1000) / PowersOfTen[exp];

        out.is_negative = (d[4] & 0x08) != 0;
        out.value_um = out.is_negative ? -val_um : val_um;
        out.is_inch = (d[12] & 0x01) != 0;
        out.valid = true;
        return true;
    }
};
