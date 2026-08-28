#include <iostream>
#include <vector>
#include <complex>
#include <cmath>
#include <numbers>
#include <span>
#include <memory>
#include <iomanip>
#include <algorithm>

namespace sar {

using Complex = std::complex<float>;
constexpr float C_LIGHT = 299792458.0f;

struct RadarConfig {
    float carrier_freq_hz{9.6e9f};      // X-діапазон: 9.6 ГГц (λ ≈ 0.0312 м)
    float range_bandwidth_hz{100.0e6f};  // Смуга ЛЧМ: 100 МГц (δ_r = 1.5 м)
    float pulse_duration_s{10.0e-6f};    // Тривалість імпульсу: 10 мкс
    float sampling_rate_hz{120.0e6f};   // Частота дискретизації АЦП: 120 МГц
    float platform_velocity_ms{150.0f};  // Швидкість літака: 150 м/с
    float prf_hz{500.0f};                // Частота повторення імпульсів: 500 Гц
    float target_range_m{3000.0f};       // Початкова дальність до цілі R₀: 3 км
    float antenna_length_m{1.5f};        // Фізична довжина антени: 1.5 м (δ_az = 0.75 м)
    size_t num_range_bins{256};          // Кількість відліків за дальністю
    size_t num_azimuth_pulses{256};      // Кількість азимутальних зондувань
};

// 1D Швидке перетворення Фур'є (Cooley-Tukey Radix-2)
void fft1d(std::span<Complex> data, bool inverse = false) {
    const size_t n = data.size();
    if (n <= 1) return;

    for (size_t i = 1, j = 0; i < n; ++i) {
        size_t bit = n >> 1;
        for (; j & bit; bit >>= 1) {
            j ^= bit;
        }
        j ^= bit;
        if (i < j) std::swap(data[i], data[j]);
    }

    for (size_t len = 2; len <= n; len <<= 1) {
        float angle = 2.0f * std::numbers::pi_v<float> / static_cast<float>(len);
        if (inverse) angle = -angle;
        Complex wlen(std::cos(angle), std::sin(angle));

        for (size_t i = 0; i < n; i += len) {
            Complex w(1.0f, 0.0f);
            for (size_t j = 0; j < len / 2; ++j) {
                Complex u = data[i + j];
                Complex v = data[i + j + len / 2] * w;
                data[i + j] = u + v;
                data[i + j + len / 2] = u - v;
                w *= wlen;
            }
        }
    }

    if (inverse) {
        const float scale = 1.0f / static_cast<float>(n);
        for (auto& val : data) val *= scale;
    }
}

class RangeDopplerProcessor {
public:
    explicit RangeDopplerProcessor(RadarConfig cfg)
        : cfg_(cfg),
          wavelength_(C_LIGHT / cfg.carrier_freq_hz),
          chirp_rate_(cfg.range_bandwidth_hz / cfg.pulse_duration_s),
          raw_data_(cfg.num_azimuth_pulses * cfg.num_range_bins, Complex{0.0f, 0.0f}),
          focused_image_(cfg.num_azimuth_pulses * cfg.num_range_bins, Complex{0.0f, 0.0f}) {}

    // Генерація синтетичного радарного відгуку від точкової цілі
    void simulate_point_target(float target_azimuth_time_s = 0.0f) {
        const float dt = 1.0f / cfg_.sampling_rate_hz;
        const float d_eta = 1.0f / cfg_.prf_hz;
        const float r0 = cfg_.target_range_m;

        for (size_t az = 0; az < cfg_.num_azimuth_pulses; ++az) {
            float eta = (static_cast<float>(az) - static_cast<float>(cfg_.num_azimuth_pulses) / 2.0f) * d_eta;
            float r_eta = std::sqrt(r0 * r0 + (cfg_.platform_velocity_ms * (eta - target_azimuth_time_s)) *
                                               (cfg_.platform_velocity_ms * (eta - target_azimuth_time_s)));
            float tau_0 = 2.0f * r_eta / C_LIGHT;

            for (size_t rg = 0; rg < cfg_.num_range_bins; ++rg) {
                float tau = (static_cast<float>(rg) - static_cast<float>(cfg_.num_range_bins) / 2.0f) * dt + 2.0f * r0 / C_LIGHT;
                float t_diff = tau - tau_0;

                if (std::abs(t_diff) <= cfg_.pulse_duration_s / 2.0f) {
                    float phase = -2.0f * std::numbers::pi_v<float> * cfg_.carrier_freq_hz * tau_0 +
                                  std::numbers::pi_v<float> * chirp_rate_ * t_diff * t_diff;
                    raw_data_[az * cfg_.num_range_bins + rg] = Complex(std::cos(phase), std::sin(phase));
                }
            }
        }
    }

    // Повний цикл 2D-фокусування
    void process() {
        focused_image_ = raw_data_;

        // 1. Стиснення за дальністю (Range Compression)
        range_compression();

        // 2. Азимутальне БПФ у простір Range-Doppler
        azimuth_fft(false);

        // 3. Корекція міграції дальності (RCMC)
        range_cell_migration_correction();

        // 4. Азимутальне узгоджене стиснення та IFFT
        azimuth_compression();
    }

    [[nodiscard]] const std::vector<Complex>& get_image() const noexcept {
        return focused_image_;
    }

    void print_peak_metrics() const {
        size_t max_az = 0, max_rg = 0;
        float max_mag = 0.0f;

        for (size_t az = 0; az < cfg_.num_azimuth_pulses; ++az) {
            for (size_t rg = 0; rg < cfg_.num_range_bins; ++rg) {
                float mag = std::abs(focused_image_[az * cfg_.num_range_bins + rg]);
                if (mag > max_mag) {
                    max_mag = mag;
                    max_az = az;
                    max_rg = rg;
                }
            }
        }

        std::cout << "[SAR-RDA] Пік фокусування точкової цілі:\n"
                  << "  Азимутальний індекс : " << max_az << " / " << cfg_.num_azimuth_pulses << "\n"
                  << "  Індекс дальності    : " << max_rg << " / " << cfg_.num_range_bins << "\n"
                  << "  Амплітуда піка      : " << std::fixed << std::setprecision(2) << max_mag << "\n"
                  << "  Теоретична розд. rg : " << (C_LIGHT / (2.0f * cfg_.range_bandwidth_hz)) << " м\n"
                  << "  Теоретична розд. az : " << (cfg_.antenna_length_m / 2.0f) << " м\n";
    }

private:
    void range_compression() {
        const size_t n_rg = cfg_.num_range_bins;
        const float df = cfg_.sampling_rate_hz / static_cast<float>(n_rg);

        std::vector<Complex> matched_filter(n_rg);
        for (size_t i = 0; i < n_rg; ++i) {
            float f = (static_cast<float>(i) - static_cast<float>(n_rg) / 2.0f) * df;
            if (std::abs(f) <= cfg_.range_bandwidth_hz / 2.0f) {
                float phase = std::numbers::pi_v<float> * f * f / chirp_rate_;
                matched_filter[i] = Complex(std::cos(phase), std::sin(phase));
            }
        }

        std::vector<Complex> row(n_rg);
        for (size_t az = 0; az < cfg_.num_azimuth_pulses; ++az) {
            for (size_t rg = 0; rg < n_rg; ++rg) {
                row[rg] = focused_image_[az * n_rg + rg];
            }
            fft1d(row, false);
            for (size_t rg = 0; rg < n_rg; ++rg) {
                row[rg] *= matched_filter[rg];
            }
            fft1d(row, true);
            for (size_t rg = 0; rg < n_rg; ++rg) {
                focused_image_[az * n_rg + rg] = row[rg];
            }
        }
    }

    void azimuth_fft(bool inverse) {
        const size_t n_az = cfg_.num_azimuth_pulses;
        const size_t n_rg = cfg_.num_range_bins;
        std::vector<Complex> col(n_az);

        for (size_t rg = 0; rg < n_rg; ++rg) {
            for (size_t az = 0; az < n_az; ++az) {
                col[az] = focused_image_[az * n_rg + rg];
            }
            fft1d(col, inverse);
            for (size_t az = 0; az < n_az; ++az) {
                focused_image_[az * n_rg + rg] = col[az];
            }
        }
    }

    void range_cell_migration_correction() {
        const size_t n_az = cfg_.num_azimuth_pulses;
        const size_t n_rg = cfg_.num_range_bins;
        const float d_eta_f = cfg_.prf_hz / static_cast<float>(n_az);
        const float dr = C_LIGHT / (2.0f * cfg_.sampling_rate_hz);

        std::vector<Complex> corrected_row(n_rg);

        for (size_t az = 0; az < n_az; ++az) {
            float f_eta = (static_cast<float>(az) - static_cast<float>(n_az) / 2.0f) * d_eta_f;
            // Розрахунок зміщення траєкторії: ΔR(f_eta) = λ² · R₀ · f_eta² / (8 · v²)
            float delta_r = (wavelength_ * wavelength_ * cfg_.target_range_m * f_eta * f_eta) /
                            (8.0f * cfg_.platform_velocity_ms * cfg_.platform_velocity_ms);
            float bin_shift = delta_r / dr;

            for (size_t rg = 0; rg < n_rg; ++rg) {
                float src_idx = static_cast<float>(rg) + bin_shift;
                int idx0 = static_cast<int>(std::floor(src_idx));
                float frac = src_idx - static_cast<float>(idx0);

                if (idx0 >= 0 && idx0 + 1 < static_cast<int>(n_rg)) {
                    Complex val0 = focused_image_[az * n_rg + idx0];
                    Complex val1 = focused_image_[az * n_rg + idx0 + 1];
                    corrected_row[rg] = val0 * (1.0f - frac) + val1 * frac;
                } else {
                    corrected_row[rg] = Complex{0.0f, 0.0f};
                }
            }
            for (size_t rg = 0; rg < n_rg; ++rg) {
                focused_image_[az * n_rg + rg] = corrected_row[rg];
            }
        }
    }

    void azimuth_compression() {
        const size_t n_az = cfg_.num_azimuth_pulses;
        const size_t n_rg = cfg_.num_range_bins;
        const float d_eta_f = cfg_.prf_hz / static_cast<float>(n_az);

        for (size_t az = 0; az < n_az; ++az) {
            float f_eta = (static_cast<float>(az) - static_cast<float>(n_az) / 2.0f) * d_eta_f;
            float val = (wavelength_ * f_eta) / (2.0f * cfg_.platform_velocity_ms);
            val = std::clamp(val, -0.999f, 0.999f);

            // Азимутальний фазовий узгоджений множник
            float phase = (4.0f * std::numbers::pi_v<float> * cfg_.target_range_m / wavelength_) *
                          std::sqrt(1.0f - val * val);
            Complex az_ref(std::cos(phase), std::sin(phase));

            for (size_t rg = 0; rg < n_rg; ++rg) {
                focused_image_[az * n_rg + rg] *= az_ref;
            }
        }

        // Обернене азимутальне БПФ
        azimuth_fft(true);
    }

    RadarConfig cfg_;
    float wavelength_;
    float chirp_rate_;
    std::vector<Complex> raw_data_;
    std::vector<Complex> focused_image_;
};

} // namespace sar

int main() {
    sar::RadarConfig cfg;
    sar::RangeDopplerProcessor proc(cfg);

    std::cout << "1. Синтез відгуку точкової цілі на дальності R₀ = 3000 м...\n";
    proc.simulate_point_target(0.0f);

    std::cout << "2. Виконання 2D-фокусування Range-Doppler (RDA)...\n";
    proc.process();

    proc.print_peak_metrics();
    return 0;
}
