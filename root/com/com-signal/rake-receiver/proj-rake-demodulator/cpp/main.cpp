#include <iostream>
#include <vector>
#include <complex>
#include <random>
#include <numeric>
#include <iomanip>

class RakeReceiver {
public:
    using Complex = std::complex<double>;

    struct Finger {
        int delay_chips;
        Complex channel_h;
        Complex finger_output{0.0, 0.0};
    };

    explicit RakeReceiver(std::vector<double> pn_sequence)
        : pn_seq_(std::move(pn_sequence)) {}

    void set_fingers(std::vector<Finger> fingers) {
        fingers_ = std::move(fingers);
    }

    Complex process(const std::vector<Complex>& rx_signal) {
        Complex total_sum{0.0, 0.0};

        for (auto& finger : fingers_) {
            Complex corr{0.0, 0.0};
            const int tau = finger.delay_chips;

            for (size_t i = 0; i < pn_seq_.size(); ++i) {
                if (i + tau < rx_signal.size()) {
                    corr += rx_signal[i + tau] * pn_seq_[i];
                }
            }
            corr /= static_cast<double>(pn_seq_.size());

            // MRC weighting: w_k = conj(h_k)
            const Complex weight = std::conj(finger.channel_h);
            finger.finger_output = corr * weight;

            total_sum += finger.finger_output;
        }

        return total_sum;
    }

    const std::vector<Finger>& fingers() const { return fingers_; }

private:
    std::vector<double> pn_seq_;
    std::vector<Finger> fingers_;
};

int main() {
    // 31-чипова PN послідовність
    const std::vector<double> pn_seq = {
        1, 1, 1, 1, -1, 1, -1, 1, 1, -1, -1, 1, 1, 1, -1, 1,
        -1, -1, -1, 1, -1, 1, -1, -1, 1, -1, -1, -1, -1, 1, -1
    };

    const size_t total_samples = pn_seq.size() + 16;
    using Complex = std::complex<double>;

    // Параметри багатопроменевого каналу
    struct Path { int delay; double amp; double phase; };
    const std::vector<Path> paths = {
        {0, 0.85, 0.2},
        {4, 0.55, 1.1},
        {9, 0.35, 2.3}
    };

    const double tx_bit = 1.0;
    std::vector<Complex> rx_signal(total_samples, Complex{0.0, 0.0});

    // Формування каналу
    for (const auto& path : paths) {
        Complex h_k = std::polar(path.amp, path.phase);
        for (size_t i = 0; i < pn_seq.size(); ++i) {
            rx_signal[i + path.delay] += tx_bit * pn_seq[i] * h_k;
        }
    }

    // AWGN шум
    std::mt19937 rng(42);
    std::normal_distribution<double> noise_dist(0.0, 0.15);
    for (auto& sample : rx_signal) {
        sample += Complex{noise_dist(rng), noise_dist(rng)};
    }

    // Налаштування RAKE приймача
    RakeReceiver rake(pn_seq);
    std::vector<RakeReceiver::Finger> fingers;
    for (const auto& path : paths) {
        fingers.push_back({path.delay, std::polar(path.amp, path.phase)});
    }
    rake.set_fingers(fingers);

    // Виконання прийому
    Complex total_mrc = rake.process(rx_signal);

    std::cout << std::fixed << std::setprecision(3);
    std::cout << "=== Демодулювання пальців RAKE (C++) ===\n";
    for (size_t i = 0; i < rake.fingers().size(); ++i) {
        const auto& f = rake.fingers()[i];
        std::cout << "Палець " << i << " (τ=" << f.delay_chips
                  << "): вихід = " << f.finger_output
                  << " (абс = " << std::abs(f.finger_output) << ")\n";
    }

    std::cout << "-----------------------------------------\n";
    std::cout << "Сумарний MRC сигнал: " << total_mrc << "\n";
    std::cout << "Детектований біт: " << (total_mrc.real() > 0 ? 1 : -1)
              << " (оригінал: " << static_cast<int>(tx_bit) << ")\n";

    return 0;
}
