#include <cstdint>
#include <cstddef>
#include <array>
#include <span>
#include <algorithm>

namespace energy {

struct Metrics {
    float voltage_rms{0.0f};       // Напруга, В (RMS)
    float current_rms{0.0f};       // Струм, А (RMS)
    float active_power{0.0f};      // Активна потужність, Вт
    float apparent_power{0.0f};    // Повна потужність, ВА
    float power_factor{1.0f};      // Коефіцієнт потужності (0.00...1.00)
    uint64_t energy_micro_ws{0};   // Накопичена енергія у мікроджоулях (мкВт·с)
    double energy_kwh{0.0};        // Накопичена енергія, кВт·год
    uint32_t valid_frames{0};      // Лічильник успішних пакетів
    uint32_t checksum_errors{0};  // Лічильник помилок контрольної суми
};

class EnergyMeterHLW8032 {
public:
    static constexpr size_t kFrameLen = 24;
    static constexpr uint8_t kSync1 = 0x55;
    static constexpr uint8_t kSync2 = 0x5A;

    explicit constexpr EnergyMeterHLW8032(float k_voltage = 1.881f, float k_current = 1.000f) noexcept
        : k_voltage_{k_voltage > 0.0f ? k_voltage : 1.881f},
          k_current_{k_current > 0.0f ? k_current : 1.000f} {}

    // Обробка одного байта з UART
    void feed_byte(uint8_t byte) noexcept {
        switch (state_) {
        case State::WaitSync1:
            if (byte == kSync1) {
                buffer_[0] = byte;
                state_ = State::WaitSync2;
            }
            break;

        case State::WaitSync2:
            if (byte == kSync2) {
                buffer_[1] = byte;
                byte_idx_ = 2;
                state_ = State::CollectData;
            } else if (byte == kSync1) {
                buffer_[0] = byte;
            } else {
                state_ = State::WaitSync1;
            }
            break;

        case State::CollectData:
            buffer_[byte_idx_++] = byte;
            if (byte_idx_ >= kFrameLen) {
                process_frame();
                state_ = State::WaitSync1;
            }
            break;
        }
    }

    // Обробка масиву байтів із буфера DMA/FIFO
    void feed_buffer(std::span<const uint8_t> data) noexcept {
        for (uint8_t b : data) {
            feed_byte(b);
        }
    }

    [[nodiscard]] const Metrics& metrics() const noexcept { return metrics_; }

    void reset_energy() noexcept {
        metrics_.energy_micro_ws = 0;
        metrics_.energy_kwh = 0.0;
    }

    void set_calibration(float k_v, float k_i) noexcept {
        if (k_v > 0.0f) k_voltage_ = k_v;
        if (k_i > 0.0f) k_current_ = k_i;
    }

private:
    enum class State : uint8_t {
        WaitSync1,
        WaitSync2,
        CollectData
    };

    static constexpr uint32_t unpack_u24(const uint8_t* p) noexcept {
        return (static_cast<uint32_t>(p[0]) << 16) |
               (static_cast<uint32_t>(p[1]) << 8)  |
                static_cast<uint32_t>(p[2]);
    }

    void process_frame() noexcept {
        // Контрольна сума: сума байтів від 2 до 22
        uint8_t sum = 0;
        for (size_t i = 2; i <= 22; ++i) {
            sum += buffer_[i];
        }

        if (sum != buffer_[23]) {
            ++metrics_.checksum_errors;
            return;
        }

        ++metrics_.valid_frames;

        const uint32_t v_param = unpack_u24(&buffer_[2]);
        const uint32_t v_data  = unpack_u24(&buffer_[5]);
        const uint32_t i_param = unpack_u24(&buffer_[8]);
        const uint32_t i_data  = unpack_u24(&buffer_[11]);
        const uint32_t p_param = unpack_u24(&buffer_[14]);
        const uint32_t p_data  = unpack_u24(&buffer_[17]);

        if (v_data > 0) {
            metrics_.voltage_rms = (static_cast<float>(v_param) / static_cast<float>(v_data)) * k_voltage_;
        }

        if (i_data > 0) {
            const float raw_i = (static_cast<float>(i_param) / static_cast<float>(i_data)) * k_current_;
            metrics_.current_rms = (raw_i >= 0.015f) ? raw_i : 0.0f;
        } else {
            metrics_.current_rms = 0.0f;
        }

        if (p_data > 0 && metrics_.current_rms > 0.0f) {
            metrics_.active_power = (static_cast<float>(p_param) / static_cast<float>(p_data)) * k_voltage_ * k_current_;
        } else {
            metrics_.active_power = 0.0f;
        }

        metrics_.apparent_power = metrics_.voltage_rms * metrics_.current_rms;
        if (metrics_.apparent_power > 0.1f) {
            const float pf = metrics_.active_power / metrics_.apparent_power;
            metrics_.power_factor = std::clamp(pf, 0.0f, 1.0f);
        } else {
            metrics_.power_factor = 1.0f;
        }

        // 50 мс інтервал оновлення: 0.05 с * 1e6 = 50000 мкВт·с
        const auto delta_uWs = static_cast<uint64_t>(metrics_.active_power * 50000.0f);
        metrics_.energy_micro_ws += delta_uWs;
        metrics_.energy_kwh = static_cast<double>(metrics_.energy_micro_ws) / 3.6e12;
    }

    State state_{State::WaitSync1};
    std::array<uint8_t, kFrameLen> buffer_{};
    size_t byte_idx_{0};
    float k_voltage_{1.881f};
    float k_current_{1.000f};
    Metrics metrics_{};
};

} // namespace energy
