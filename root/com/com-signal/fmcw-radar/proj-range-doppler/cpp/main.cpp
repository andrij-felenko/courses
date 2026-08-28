#include <vector>
#include <complex>
#include <cmath>
#include <algorithm>
#include <span>
#include <numbers>

namespace radar {

using ComplexF = std::complex<float>;

struct Target {
    float range_m{0.0f};       // Відстань до цілі, м
    float velocity_ms{0.0f};   // Радіальна швидкість, м/с
    float power_db{0.0f};      // Потужність відбиття, дБ
    int range_bin{0};          // Індекс біна дальності
    int doppler_bin{0};        // Індекс біна швидкості
};

class FmcwProcessor {
public:
    FmcwProcessor(int n_samples, int n_chirps, float range_res, float vel_res)
        : n_samples_(n_samples), n_chirps_(n_chirps),
          range_res_(range_res), vel_res_(vel_res),
          win_fast_(generate_hanning(n_samples)),
          win_slow_(generate_hanning(n_chirps)),
          rd_map_power_(n_samples * n_chirps, 0.0f) {}

    // Обробка кадру: 2D-FFT та формування карти потужності
    void compute_range_doppler_map(std::span<ComplexF> cube) {
        std::vector<ComplexF> row_buf(n_samples_);
        std::vector<ComplexF> col_buf(n_chirps_);

        // 1. Range-FFT вздовж швидкого часу (рядки)
        for (int c = 0; c < n_chirps_; ++c) {
            for (int s = 0; s < n_samples_; ++s) {
                row_buf[s] = cube[c * n_samples_ + s] * win_fast_[s];
            }
            fft(row_buf);
            for (int s = 0; s < n_samples_; ++s) {
                cube[c * n_samples_ + s] = row_buf[s];
            }
        }

        // 2. Doppler-FFT вздовж повільного часу (стовпчики)
        for (int s = 0; s < n_samples_; ++s) {
            for (int c = 0; c < n_chirps_; ++c) {
                col_buf[c] = cube[c * n_samples_ + s] * win_slow_[c];
            }
            fft(col_buf);

            // 3. FFTShift і збереження квадрата амплітуди
            for (int c = 0; c < n_chirps_; ++c) {
                int shifted_c = (c + n_chirps_ / 2) % n_chirps_;
                rd_map_power_[s * n_chirps_ + shifted_c] = std::norm(col_buf[c]);
            }
        }
    }

    // 2D CA-CFAR виявлення цілей
    [[nodiscard]] std::vector<Target> detect_cfar(int guard_r, int guard_d,
                                                  int train_r, int train_d,
                                                  float p_fa) const {
        std::vector<Target> detected;
        const int n_train_cells = (2 * (train_r + guard_r) + 1) * (2 * (train_d + guard_d) + 1)
                                - (2 * guard_r + 1) * (2 * guard_d + 1);

        const float alpha = static_cast<float>(n_train_cells) *
                            (std::pow(p_fa, -1.0f / static_cast<float>(n_train_cells)) - 1.0f);

        const int r_start = train_r + guard_r;
        const int r_end = n_samples_ - (train_r + guard_r);
        const int d_start = train_d + guard_d;
        const int d_end = n_chirps_ - (train_d + guard_d);

        for (int r = r_start; r < r_end; ++r) {
            for (int d = d_start; d < d_end; ++d) {
                const float cut_val = rd_map_power_[r * n_chirps_ + d];

                float noise_sum = 0.0f;
                for (int dr = -(train_r + guard_r); dr <= (train_r + guard_r); ++dr) {
                    for (int dd = -(train_d + guard_d); dd <= (train_d + guard_d); ++dd) {
                        if (std::abs(dr) <= guard_r && std::abs(dd) <= guard_d) {
                            continue;
                        }
                        noise_sum += rd_map_power_[(r + dr) * n_chirps_ + (d + dd)];
                    }
                }

                const float noise_avg = noise_sum / static_cast<float>(n_train_cells);
                if (cut_val <= alpha * noise_avg) {
                    continue;
                }

                // Перевірка на локальний максимум
                bool is_peak = true;
                for (int dr = -guard_r; dr <= guard_r && is_peak; ++dr) {
                    for (int dd = -guard_d; dd <= guard_d; ++dd) {
                        if (dr == 0 && dd == 0) continue;
                        if (rd_map_power_[(r + dr) * n_chirps_ + (d + dd)] >= cut_val) {
                            is_peak = false;
                            break;
                        }
                    }
                }

                if (is_peak) {
                    detected.push_back(Target{
                        .range_m = static_cast<float>(r) * range_res_,
                        .velocity_ms = static_cast<float>(d - n_chirps_ / 2) * vel_res_,
                        .power_db = 10.0f * std::log10(cut_val + 1e-12f),
                        .range_bin = r,
                        .doppler_bin = d
                    });
                }
            }
        }
        return detected;
    }

private:
    int n_samples_;
    int n_chirps_;
    float range_res_;
    float vel_res_;
    std::vector<float> win_fast_;
    std::vector<float> win_slow_;
    std::vector<float> rd_map_power_;

    static std::vector<float> generate_hanning(int n) {
        std::vector<float> w(n);
        for (int i = 0; i < n; ++i) {
            w[i] = 0.5f * (1.0f - std::cos(2.0f * std::numbers::pi_v<float> * static_cast<float>(i) / static_cast<float>(n - 1)));
        }
        return w;
    }

    static void fft(std::span<ComplexF> x) {
        const size_t n = x.size();
        size_t j = 0;
        for (size_t i = 0; i < n - 1; ++i) {
            if (i < j) std::swap(x[i], x[j]);
            size_t k = n >> 1;
            while (k <= j) {
                j -= k;
                k >>= 1;
            }
            j += k;
        }

        for (size_t len = 2; len <= n; len <<= 1) {
            const float angle = -2.0f * std::numbers::pi_v<float> / static_cast<float>(len);
            const ComplexF wlen(std::cos(angle), std::sin(angle));
            for (size_t i = 0; i < n; i += len) {
                ComplexF w(1.0f, 0.0f);
                for (size_t k = 0; k < len / 2; ++k) {
                    const ComplexF u = x[i + k];
                    const ComplexF v = x[i + k + len / 2] * w;
                    x[i + k] = u + v;
                    x[i + k + len / 2] = u - v;
                    w *= wlen;
                }
            }
        }
    }
};

} // namespace radar
