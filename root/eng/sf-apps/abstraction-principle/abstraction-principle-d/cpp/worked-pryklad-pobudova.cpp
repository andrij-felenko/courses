#include <cstdint>
#include <cstddef>
#include <span>
#include <array>
#include <concepts>
#include <cstring>

// ── 1. Семантичний контракт через концепт (Compile-time абстракція) ───

template <typename T>
concept TelemetrySink = requires(T& sink, std::span<const uint8_t> data) {
    { sink.write_bytes(data) } -> std::same_as<bool>;
};

// ── 2. Бізнес-логіка: параметризована через концепт без vtable ───────

struct NavData {
    int32_t lat_deg_e7;
    int32_t lon_deg_e7;
    int32_t alt_mm;
    uint32_t timestamp_ms;
};

template <TelemetrySink Sink>
class NavTelemetryBroadcaster {
public:
    explicit NavTelemetryBroadcaster(Sink& sink) : sink_(sink) {}

    bool send_nav_packet(const NavData& nav) {
        std::array<uint8_t, 3 + sizeof(NavData) + 1> packet{};
        packet[0] = 0xAA; // Преамбула
        packet[1] = 0x55;
        packet[2] = static_cast<uint8_t>(sizeof(NavData));

        std::memcpy(&packet[3], &nav, sizeof(NavData));

        uint8_t crc = 0;
        for (size_t i = 0; i < packet.size() - 1; ++i) {
            crc ^= packet[i];
        }
        packet.back() = crc;

        // Виклик методу абстракції згортається компілятором у прямий машинний код
        return sink_.write_bytes(packet);
    }

private:
    Sink& sink_;
};

// ── 3. Конкретні реалізації під капотом ────────────────────────────────

// Реалізація 1: Кільцевий буфер пам'яті
template <size_t Capacity = 512>
class BlackboxSink {
public:
    bool write_bytes(std::span<const uint8_t> data) {
        if (count_ + data.size() > Capacity) {
            return false; // Інваріант ємності
        }
        for (uint8_t b : data) {
            storage_[head_] = b;
            head_ = (head_ + 1) % Capacity;
        }
        count_ += data.size();
        return true;
    }

    [[nodiscard]] size_t bytes_written() const noexcept { return count_; }

private:
    std::array<uint8_t, Capacity> storage_{};
    size_t head_{0};
    size_t count_{0};
};

// Реалізація 2: Апаратний UART
class UartSink {
public:
    UartSink(volatile uint32_t* dr, volatile uint32_t* sr)
        : uart_dr_(dr), uart_sr_(sr) {}

    bool write_bytes(std::span<const uint8_t> data) {
        for (uint8_t b : data) {
            while (!(*uart_sr_ & 0x80)) {
                // Очікування прапорця готовності TXE
            }
            *uart_dr_ = b;
        }
        return true;
    }

private:
    volatile uint32_t* uart_dr_;
    volatile uint32_t* uart_sr_;
};
