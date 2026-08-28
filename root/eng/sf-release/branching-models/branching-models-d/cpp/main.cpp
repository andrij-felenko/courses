// ============================================================================
// Патч виправлення для ядра мережевого драйвера (C++20 версія)
// Демонструє використання RAII, std::span та std::expected для сучасного стовбура
// ============================================================================

#include <cstdint>
#include <cstddef>
#include <array>
#include <span>
#include <expected>
#include <system_error>
#include <unistd.h>

namespace hardware::telemetry {

constexpr size_t MaxPayloadSize = 512;
constexpr size_t RingCapacity   = 64;

enum class TelemetryError {
    InvalidArgument,
    MessageTooLarge,
    BufferFull,
    SystemError
};

struct [[nodiscard]] TelemetryFrame {
    uint32_t message_id{0};
    uint16_t payload_len{0};
    std::array<uint8_t, MaxPayloadSize> payload{};
};

// RAII обгортка системного дескриптора для унеможливлення витоків ресурсів
class UniqueFileDescriptor {
public:
    constexpr UniqueFileDescriptor() noexcept : fd_{-1} {}
    explicit UniqueFileDescriptor(int fd) noexcept : fd_{fd} {}

    ~UniqueFileDescriptor() noexcept {
        reset();
    }

    UniqueFileDescriptor(const UniqueFileDescriptor&) = delete;
    UniqueFileDescriptor& operator=(const UniqueFileDescriptor&) = delete;

    UniqueFileDescriptor(UniqueFileDescriptor&& other) noexcept : fd_{other.release()} {}
    UniqueFileDescriptor& operator=(UniqueFileDescriptor&& other) noexcept {
        if (this != &other) {
            reset(other.release());
        }
        return *this;
    }

    void reset(int new_fd = -1) noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
        }
        fd_ = new_fd;
    }

    [[nodiscard]] int release() noexcept {
        int old = fd_;
        fd_ = -1;
        return old;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool is_valid() const noexcept { return fd_ >= 0; }

private:
    int fd_{-1};
};

class TelemetryRingBuffer {
public:
    void reset() noexcept {
        notify_fd_.reset();
        head_ = 0;
        tail_ = 0;
        frames_.fill(TelemetryFrame{});
    }

    [[nodiscard]] auto push_frame(std::span<const uint8_t> raw_bytes) noexcept 
        -> std::expected<void, TelemetryError> 
    {
        // Сувора перевірка розміру вхідного буфера
        if (raw_bytes.size() > sizeof(TelemetryFrame)) {
            return std::unexpected(TelemetryError::MessageTooLarge);
        }

        const size_t next_head = (head_ + 1) % RingCapacity;
        if (next_head == tail_) {
            return std::unexpected(TelemetryError::BufferFull);
        }

        auto* dest = reinterpret_cast<uint8_t*>(&frames_[head_]);
        std::copy(raw_bytes.begin(), raw_bytes.end(), dest);
        head_ = next_head;

        return {};
    }

    void set_notifier(int fd) noexcept {
        notify_fd_.reset(fd);
    }

private:
    std::array<TelemetryFrame, RingCapacity> frames_{};
    size_t head_{0};
    size_t tail_{0};
    UniqueFileDescriptor notify_fd_;
};

} // namespace hardware::telemetry
