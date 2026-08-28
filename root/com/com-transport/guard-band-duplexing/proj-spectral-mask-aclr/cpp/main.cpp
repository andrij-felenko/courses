#include <iostream>
#include <vector>
#include <complex>
#include <cmath>
#include <span>
#include <numbers>
#include <algorithm>
#include <iomanip>

namespace dsp {

using Complex = std::complex<double>;

/* Ітеративне БПФ Cooley-Tukey (Radix-2) над даними у векторі */
void fft_radix2(std::span<Complex> data) {
    const size_t n = data.size();
    size_t j = 0;
    for (size_t i = 0; i < n - 1; ++i) {
        if (i < j) {
            std::swap(data[i], data[j]);
        }
        size_t k = n >> 1;
        while (k <= j) {
            j -= k;
            k >>= 1;
        }
        j += k;
    }

    for (size_t len = 2; len <= n; len <<= 1) {
        const double ang = -2.0 * std::numbers::pi / static_cast<double>(len);
        const Complex wlen(std::cos(ang), std::sin(ang));
        for (size_t i = 0; i < n; i += len) {
            Complex w(1.0, 0.0);
            for (size_t k = 0; k < len / 2; ++k) {
                const Complex u = data[i + k];
                const Complex v = data[i + k + len / 2] * w;
                data[i + k] = u + v;
                data[i + k + len / 2] = u - v;
                w *= wlen;
            }
        }
    }
}

/* Оцінка PSD за методом Велча з вікном Ханна та 50% перекриттям */
std::vector<double> estimate_psd_welch(std::span<const Complex> signal, size_t fft_size) {
    std::vector<double> psd(fft_size, 0.0);
    std::vector<double> window(fft_size);
    double win_energy = 0.0;

    for (size_t i = 0; i < fft_size; ++i) {
        window[i] = 0.5 * (1.0 - std::cos(2.0 * std::numbers::pi * static_cast<double>(i) / (fft_size - 1)));
        win_energy += window[i] * window[i];
    }

    const size_t hop = fft_size / 2;
    size_t frames_count = 0;
    std::vector<Complex> frame(fft_size);

    for (size_t offset = 0; offset + fft_size <= signal.size(); offset += hop) {
        for (size_t i = 0; i < fft_size; ++i) {
            frame[i] = signal[offset + i] * window[i];
        }

        fft_radix2(frame);

        for (size_t i = 0; i < fft_size; ++i) {
            const size_t shifted_idx = (i + fft_size / 2) % fft_size;
            psd[shifted_idx] += std::norm(frame[i]);
        }
        frames_count++;
    }

    if (frames_count > 0) {
        const double norm = 1.0 / (frames_count * win_energy);
        for (auto& val : psd) {
            val *= norm;
        }
    }

    return psd;
}

/* Обчислення сумарної потужності у заданому частотному інтервалі */
double integrate_band_power(std::span<const double> psd, double sample_rate,
                            double start_freq, double end_freq) {
    const size_t fft_size = psd.size();
    const double df = sample_rate / static_cast<double>(fft_size);
    const double half_fs = sample_rate / 2.0;
    double power = 0.0;

    for (size_t k = 0; k < fft_size; ++k) {
        const double freq = -half_fs + static_cast<double>(k) * df;
        if (freq >= start_freq && freq <= end_freq) {
            power += psd[k];
        }
    }
    return power;
}

struct AclrResult {
    double carrier_power;
    double lower_aclr_db;
    double upper_aclr_db;
    bool meets_standard;
};

/* Розрахунок метрик ACLR */
AclrResult evaluate_aclr(std::span<const double> psd, double sample_rate,
                         double channel_bw, double channel_spacing,
                         double threshold_db = 45.0) {
    const double p_carrier = integrate_band_power(psd, sample_rate, -channel_bw / 2.0, channel_bw / 2.0);
    const double p_lower = integrate_band_power(psd, sample_rate,
                                                -channel_spacing - channel_bw / 2.0,
                                                -channel_spacing + channel_bw / 2.0);
    const double p_upper = integrate_band_power(psd, sample_rate,
                                                channel_spacing - channel_bw / 2.0,
                                                channel_spacing + channel_bw / 2.0);

    const double aclr_low = 10.0 * std::log10(p_carrier / p_lower);
    const double aclr_high = 10.0 * std::log10(p_carrier / p_upper);

    return {
        .carrier_power = p_carrier,
        .lower_aclr_db = aclr_low,
        .upper_aclr_db = aclr_high,
        .meets_standard = (aclr_low >= threshold_db) && (aclr_high >= threshold_db)
    };
}

} // namespace dsp

int main() {
    constexpr double sample_rate = 61.44e6; /* 61.44 МГц */
    constexpr size_t fft_size = 2048;
    constexpr size_t num_samples = 32768;
    constexpr double channel_bw = 18.0e6;      /* 18 МГц корисна смуга */
    constexpr double channel_spacing = 20.0e6; /* 20 МГц крок каналів */

    std::vector<dsp::Complex> iq_signal(num_samples);

    /* Синтез сигналу з нелінійним спотворенням підсилювача потужності */
    for (size_t n = 0; n < num_samples; ++n) {
        const double t = static_cast<double>(n) / sample_rate;
        const double i_sig = std::cos(2.0 * std::numbers::pi * 2.0e6 * t) + 0.8 * std::cos(2.0 * std::numbers::pi * 6.0e6 * t);
        const double q_sig = std::sin(2.0 * std::numbers::pi * 2.0e6 * t) + 0.8 * std::sin(2.0 * std::numbers::pi * 6.0e6 * t);

        const double env_sq = i_sig * i_sig + q_sig * q_sig;
        const double compression = 1.0 - 0.04 * env_sq;

        iq_signal[n] = dsp::Complex(i_sig * compression, q_sig * compression);
    }

    const auto psd = dsp::estimate_psd_welch(iq_signal, fft_size);
    const auto result = dsp::evaluate_aclr(psd, sample_rate, channel_bw, channel_spacing);

    std::cout << std::fixed << std::setprecision(2);
    std::cout << "=== РЕЗУЛЬТАТИ СПЕКТРАЛЬНОГО АНАЛІЗУ (C++) ===\n";
    std::cout << "Потужність корисного каналу: " << std::scientific << result.carrier_power << " Вт\n" << std::fixed;
    std::cout << "Нижній ACLR (-20 МГц): " << result.lower_aclr_db << " дБ\n";
    std::cout << "Верхній ACLR (+20 МГц): " << result.upper_aclr_db << " дБ\n";
    std::cout << "Норматив 3GPP (>= 45.0 дБ): " << (result.meets_standard ? "ПРОЙДЕНО" : "НЕ ПРОЙДЕНО") << "\n";

    return result.meets_standard ? 0 : 1;
}
