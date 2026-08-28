// C++ implementation: RAII, std::vector, std::complex, modern idioms
#include <iostream>
#include <vector>
#include <complex>
#include <cmath>
#include <numbers>
#include <numeric>

class IQModem {
public:
    IQModem(std::size_t samples, double fs, double fc)
        : fs_(fs), fc_(fc),
          baseband_(samples), passband_(samples), recovered_(samples) {}

    void set_baseband(const std::vector<std::complex<double>>& input) {
        baseband_ = input;
    }

    void modulate() {
        const double dt = 1.0 / fs_;
        for (std::size_t n = 0; n < baseband_.size(); ++n) {
            const double t = n * dt;
            const double phase = 2.0 * std::numbers::pi * fc_ * t;
            // s(t) = Re{ s_l(t) * e^(j w_c t) } = I(t)*cos(w_c t) - Q(t)*sin(w_c t)
            const std::complex<double> carrier{std::cos(phase), std::sin(phase)};
            passband_[n] = (baseband_[n] * carrier).real();
        }
    }

    void demodulate(std::size_t filter_len) {
        const std::size_t N = passband_.size();
        const double dt = 1.0 / fs_;
        std::vector<std::complex<double>> raw(N);

        for (std::size_t n = 0; n < N; ++n) {
            const double t = n * dt;
            const double phase = 2.0 * std::numbers::pi * fc_ * t;
            const std::complex<double> lo{2.0 * std::cos(phase), -2.0 * std::sin(phase)};
            raw[n] = passband_[n] * lo;
        }

        // Застосування ФНЧ (КІХ-фільтр ковзного середнього)
        const int half_w = static_cast<int>(filter_len / 2);
        for (std::size_t n = 0; n < N; ++n) {
            std::complex<double> sum{0.0, 0.0};
            int count = 0;
            for (int k = -half_w; k <= half_w; ++k) {
                const int idx = static_cast<int>(n) + k;
                if (idx >= 0 && idx < static_cast<int>(N)) {
                    sum += raw[idx];
                    ++count;
                }
            }
            recovered_[n] = sum / static_cast<double>(count);
        }
    }

    const std::vector<double>& get_passband() const { return passband_; }
    const std::vector<std::complex<double>>& get_recovered() const { return recovered_; }

private:
    double fs_;
    double fc_;
    std::vector<std::complex<double>> baseband_;
    std::vector<double> passband_;
    std::vector<std::complex<double>> recovered_;
};

int main() {
    constexpr std::size_t N = 1000;
    constexpr double fs = 10000.0;
    constexpr double fc = 2000.0;

    IQModem modem(N, fs, fc);
    std::vector<std::complex<double>> input_signal(N);

    for (std::size_t n = 0; n < N; ++n) {
        const double t = n / fs;
        const double i_val = std::cos(2.0 * std::numbers::pi * 100.0 * t);
        const double q_val = std::sin(2.0 * std::numbers::pi * 50.0 * t);
        input_signal[n] = {i_val, q_val};
    }

    modem.set_baseband(input_signal);
    modem.modulate();
    modem.demodulate(41);

    const auto& rec = modem.get_recovered();
    std::cout << "Зразок [500]: Orig=" << input_signal[500] 
              << " -> Rec=" << rec[500] << '\n';

    return 0;
}
