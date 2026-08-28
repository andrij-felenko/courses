#include <cstdint>
#include <cstddef>
#include <array>
#include <span>
#include <functional>

struct DmaStreamRegisters {
    volatile uint32_t CR;
    volatile uint32_t NDTR;
    volatile uint32_t PAR;
    volatile uint32_t M0AR;
    volatile uint32_t FCR;
};

template <size_t TotalSize>
class CircularDmaReceiver {
    static_assert(TotalSize % 64 == 0, "Buffer size must be a multiple of 64 for cache alignment");
    static constexpr size_t HalfSize = TotalSize / 2;

    inline static constexpr uint32_t CR_EN   = (1u << 0);
    inline static constexpr uint32_t CR_HTIE = (1u << 3);
    inline static constexpr uint32_t CR_TCIE = (1u << 4);
    inline static constexpr uint32_t CR_CIRC = (1u << 8);
    inline static constexpr uint32_t CR_MINC = (1u << 10);

public:
    using Callback = std::function<void(std::span<const uint8_t>)>;

private:
    alignas(32) std::array<uint8_t, TotalSize> buffer_{};
    DmaStreamRegisters* dma_hw_{nullptr};
    Callback on_data_ready_{};

public:
    CircularDmaReceiver() noexcept = default;

    void init(DmaStreamRegisters* dma_hw, volatile uint32_t* periph_reg, Callback cb) noexcept {
        dma_hw_ = dma_hw;
        on_data_ready_ = std::move(cb);

        if (!dma_hw_) return;

        dma_hw_->CR &= ~CR_EN;
        while (dma_hw_->CR & CR_EN) {}

        dma_hw_->PAR = reinterpret_cast<uint32_t>(periph_reg);
        dma_hw_->M0AR = reinterpret_cast<uint32_t>(buffer_.data());
        dma_hw_->NDTR = TotalSize;

        dma_hw_->CR = CR_MINC | CR_CIRC | CR_TCIE | CR_HTIE;
        dma_hw_->CR |= CR_EN;
    }

    void handle_irq(uint32_t isr_flags, volatile uint32_t* ifcr) noexcept {
        constexpr uint32_t FLAG_HT = (1u << 4);
        constexpr uint32_t FLAG_TC = (1u << 5);

        if (isr_flags & FLAG_HT) {
            *ifcr = FLAG_HT;
            if (on_data_ready_) {
                on_data_ready_(std::span<const uint8_t>(buffer_.data(), HalfSize));
            }
        }

        if (isr_flags & FLAG_TC) {
            *ifcr = FLAG_TC;
            if (on_data_ready_) {
                on_data_ready_(std::span<const uint8_t>(buffer_.data() + HalfSize, HalfSize));
            }
        }
    }
};
