#include <array>
#include <atomic>
#include <chrono>
#include <span>
#include <optional>
#include <cstring>

template <typename T, size_t OutputDim>
struct PredictionFrame {
    std::array<T, OutputDim> values{};
    std::chrono::microseconds timestamp{0};
    uint32_t frameId{0};
};

template <typename T, size_t OutputDim>
class LockFreeTripleBuffer {
public:
    using FrameType = PredictionFrame<T, OutputDim>;

    LockFreeTripleBuffer() noexcept 
        : cleanIdx_{0}, writeIdx_{1}, readIdx_{2} {
        buffers_.fill(FrameType{});
    }

    /* Викликається фоновим потоком ML */
    void write(const FrameType& data) noexcept {
        buffers_[writeIdx_] = data;
        // Публікуємо свіжий буфер із релізом пам'яті
        uint_fast8_t oldClean = cleanIdx_.exchange(writeIdx_, std::memory_order_release);
        writeIdx_ = static_cast<uint8_t>(oldClean);
    }

    /* Викликається високочастотним контуром керування (Wait-Free) */
    [[nodiscard]] std::pair<FrameType, bool> read() noexcept {
        uint_fast8_t currentClean = cleanIdx_.load(std::memory_order_acquire);
        bool isFresh = false;

        if (currentClean != readIdx_) {
            uint_fast8_t oldClean = cleanIdx_.exchange(readIdx_, std::memory_order_acq_rel);
            readIdx_ = static_cast<uint8_t>(oldClean);
            isFresh = true;
        }

        return { buffers_[readIdx_], isFresh };
    }

private:
    alignas(64) std::array<FrameType, 3> buffers_;
    alignas(64) std::atomic<uint_fast8_t> cleanIdx_;
    uint8_t writeIdx_;
    uint8_t readIdx_;
};
