#include <array>
#include <concepts>
#include <cstdint>
#include <span>

template <std::size_t ChannelsCount, std::size_t MedianWindow = 3>
class SynchronizedAdcSampler {
    static_assert(MedianWindow == 3, "Дана реалізація оптимізована під 3-точкове вікно медіани");

public:
    static constexpr std::uint32_t AlphaFpShift = 8;
    static constexpr std::uint32_t AlphaFp = 38; // alpha = 38 / 256 ≈ 0.15

    struct alignas(4) DmaRawBuffer {
        std::array<std::uint16_t, ChannelsCount> data{};
    };

    SynchronizedAdcSampler() noexcept {
        reset();
    }

    void reset() noexcept {
        raw_dma_buffer_.data.fill(0);
        filtered_values_.fill(0);
        for (auto& filter : channel_filters_) {
            filter.history.fill(0);
            filter.history_idx = 0;
            filter.ema_accumulator = 0;
            filter.initialized = false;
        }
    }

    // Доступ до сирого буфера для прив'язки дескриптора DMA
    [[nodiscard]] std::uint16_t* raw_buffer_ptr() noexcept {
        return raw_dma_buffer_.data.data();
    }

    [[nodiscard]] constexpr std::size_t raw_buffer_size() const noexcept {
        return ChannelsCount;
    }

    // Обробка пакету вибірок після завершення транзакції DMA
    void process_samples() noexcept {
        for (std::size_t ch = 0; ch < ChannelsCount; ++ch) {
            const std::uint16_t raw_sample = raw_dma_buffer_.data[ch];
            auto& f = channel_filters_[ch];

            f.history[f.history_idx] = raw_sample;
            f.history_idx = (f.history_idx + 1) % MedianWindow;

            // Каскад 1: Швидкий 3-точковий медіанний фільтр
            const std::uint16_t median_val = compute_median3(f.history[0], f.history[1], f.history[2]);

            // Каскад 2: IIR згладжування з цілочисельною математикою
            if (!f.initialized) {
                f.ema_accumulator = static_cast<std::uint32_t>(median_val) << AlphaFpShift;
                f.initialized = true;
            } else {
                const auto current_val_fp = static_cast<std::int32_t>(median_val) << AlphaFpShift;
                const auto diff = current_val_fp - static_cast<std::int32_t>(f.ema_accumulator);
                f.ema_accumulator += static_cast<std::uint32_t>((diff * static_cast<std::int32_t>(AlphaFp)) >> AlphaFpShift);
            }

            filtered_values_[ch] = static_cast<std::uint16_t>(f.ema_accumulator >> AlphaFpShift);
        }
    }

    [[nodiscard]] std::uint16_t get_channel_value(std::size_t channel) const noexcept {
        if (channel < ChannelsCount) {
            return filtered_values_[channel];
        }
        return 0;
    }

    [[nodiscard]] std::span<const std::uint16_t, ChannelsCount> get_all_channels() const noexcept {
        return std::span<const std::uint16_t, ChannelsCount>(filtered_values_);
    }

private:
    struct FilterState {
        std::array<std::uint16_t, MedianWindow> history{};
        std::size_t history_idx{0};
        std::uint32_t ema_accumulator{0};
        bool initialized{false};
    };

    static constexpr std::uint16_t compute_median3(std::uint16_t a, std::uint16_t b, std::uint16_t c) noexcept {
        if (a > b) {
            if (b > c) return b;
            if (a > c) return c;
            return a;
        } else {
            if (a > c) return a;
            if (b > c) return c;
            return b;
        }
    }

    DmaRawBuffer raw_dma_buffer_{};
    std::array<FilterState, ChannelsCount> channel_filters_{};
    std::array<std::uint16_t, ChannelsCount> filtered_values_{};
};
