#include <cstdint>
#include <cstddef>
#include <span>
#include <array>
#include <optional>
#include <algorithm>

template <size_t Order = 4, size_t Decimation = 32>
class PdmCicDecimator {
public:
    static constexpr size_t BitGrowth = 1 + Order * 5; // 21 біт для N=4, R=32

    constexpr PdmCicDecimator() = default;

    void reset() noexcept {
        m_integrators.fill(0);
        m_combs.fill(0);
        m_fir_history.fill(0);
        m_dec_counter = 0;
        m_fir_idx = 0;
        m_fir_phase = false;
        m_dc_x_prev = 0;
        m_dc_y_prev = 0;
    }

    // Обробка буфера слів PDM із записом PCM відліків у вихідний span
    size_t process(std::span<const uint32_t> pdm_in, std::span<int16_t> pcm_out) noexcept {
        size_t pcm_count = 0;

        for (uint32_t word : pdm_in) {
            for (int bit = 31; bit >= 0; --bit) {
                const int32_t bit_val = ((word >> bit) & 1U) ? 1 : -1;

                // 1. Каскади інтеграторів (тактування 3.072 МГц)
                m_integrators[0] += bit_val;
                for (size_t i = 1; i < Order; ++i) {
                    m_integrators[i] += m_integrators[i - 1];
                }

                // 2. Децимація R = 32
                if (++m_dec_counter >= Decimation) {
                    m_dec_counter = 0;

                    int32_t stage_input = m_integrators[Order - 1];

                    // 3. Каскади гребінок на частоті 96 кГц (M = 1)
                    for (size_t i = 0; i < Order; ++i) {
                        const int32_t diff = stage_input - m_combs[i];
                        m_combs[i] = stage_input;
                        stage_input = diff;
                    }

                    // Масштабування виходу CIC (2^20 gain -> зсув на 5 біт для 16-біт PCM)
                    const int32_t cic_scaled = stage_input >> 5;

                    // 4. Half-Band фільтр та DC-блокер -> 48 кГц
                    if (auto sample = process_post_filter(cic_scaled)) {
                        if (pcm_count < pcm_out.size()) {
                            pcm_out[pcm_count++] = *sample;
                        }
                    }
                }
            }
        }
        return pcm_count;
    }

private:
    static constexpr std::array<int16_t, 5> CoeffsQ15 = {
        -242, 832, -2480, 9984, 16384
    };

    std::optional<int16_t> process_post_filter(int32_t sample_in) noexcept {
        m_fir_history[m_fir_idx] = sample_in;
        m_fir_idx = (m_fir_idx + 1) & 15U;
        m_fir_phase = !m_fir_phase;

        // Децимація на 2: обчислюємо вихід лише через такт
        if (m_fir_phase) {
            return std::nullopt;
        }

        int64_t acc = 0;
        const size_t idx = m_fir_idx;

        acc += static_cast<int64_t>(m_fir_history[(idx + 0) & 15U] + m_fir_history[(idx + 14) & 15U]) * CoeffsQ15[0];
        acc += static_cast<int64_t>(m_fir_history[(idx + 2) & 15U] + m_fir_history[(idx + 12) & 15U]) * CoeffsQ15[1];
        acc += static_cast<int64_t>(m_fir_history[(idx + 4) & 15U] + m_fir_history[(idx + 10) & 15U]) * CoeffsQ15[2];
        acc += static_cast<int64_t>(m_fir_history[(idx + 6) & 15U] + m_fir_history[(idx + 8)  & 15U]) * CoeffsQ15[3];
        acc += static_cast<int64_t>(m_fir_history[(idx + 7) & 15U]) * CoeffsQ15[4] * 2;

        const int32_t fir_out = static_cast<int32_t>(acc >> 16);

        // DC-блокер: y[n] = x[n] - x[n-1] + 0.995 * y[n-1]
        const int32_t dc_out = fir_out - m_dc_x_prev + static_cast<int32_t>((static_cast<int64_t>(m_dc_y_prev) * 32604) >> 15);
        m_dc_x_prev = fir_out;
        m_dc_y_prev = dc_out;

        return static_cast<int16_t>(std::clamp(dc_out, -32768, 32767));
    }

    std::array<int32_t, Order> m_integrators{};
    std::array<int32_t, Order> m_combs{};
    std::array<int32_t, 16> m_fir_history{};
    size_t m_dec_counter{0};
    size_t m_fir_idx{0};
    bool m_fir_phase{false};
    int32_t m_dc_x_prev{0};
    int32_t m_dc_y_prev{0};
};
