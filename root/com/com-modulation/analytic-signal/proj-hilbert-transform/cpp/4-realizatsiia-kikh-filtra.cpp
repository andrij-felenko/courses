#include <iostream>
#include <vector>
#include <cmath>
#include <numbers>
#include <memory>
#include <iomanip>

class FirHilbertFilter {
public:
    struct QuadraturePair {
        double real_i; // Дійсна частина (In-phase, з узгодженою затримкою)
        double imag_q; // Уявна частина (Quadrature, з виходу Гільберта)

        [[nodiscard]] double envelope() const noexcept {
            return std::hypot(real_i, imag_q);
        }

        [[nodiscard]] double phase() const noexcept {
            return std::atan2(imag_q, real_i);
        }
    };

    explicit FirHilbertFilter(std::size_t num_taps) {
        if (num_taps % 2 == 0) ++num_taps; // Гарантуємо непарну довжину
        length_ = num_taps;
        delay_ = (num_taps - 1) / 2;
        delay_line_.assign(length_, 0.0);
        taps_.assign(length_, 0.0);

        // Обчислення коефіцієнтів з вікном Хеммінга
        const int half = static_cast<int>(delay_);
        for (int i = -half; i <= half; ++i) {
            const std::size_t idx = static_cast<std::size_t>(i + half);
            if (i % 2 != 0) {
                const double w = 0.54 + 0.46 * std::cos(std::numbers::pi * static_cast<double>(i) / static_cast<double>(half));
                taps_[idx] = (2.0 / (std::numbers::pi * static_cast<double>(i))) * w;
            } else {
                taps_[idx] = 0.0;
            }
        }
    }

    // Обробка одного відліку потоку в реальному часі
    QuadraturePair process(double sample_in) noexcept {
        delay_line_[head_] = sample_in;

        double q_acc = 0.0;
        std::size_t idx = head_;

        for (std::size_t k = 0; k < length_; ++k) {
            q_acc += taps_[k] * delay_line_[idx];
            if (idx == 0) {
                idx = length_ - 1;
            } else {
                --idx;
            }
        }

        const std::size_t delayed_idx = (head_ + length_ - delay_) % length_;
        const double i_val = delay_line_[delayed_idx];

        head_ = (head_ + 1) % length_;

        return QuadraturePair{.real_i = i_val, .imag_q = q_acc};
    }

    void reset() noexcept {
        std::fill(delay_line_.begin(), delay_line_.end(), 0.0);
        head_ = 0;
    }

private:
    std::vector<double> taps_;
    std::vector<double> delay_line_;
    std::size_t length_{31};
    std::size_t delay_{15};
    std::size_t head_{0};
};

int main() {
    FirHilbertFilter filter(31);

    std::cout << std::fixed << std::setprecision(4);
    std::cout << "Sample\tInput\t\tI (Delayed)\tQ (Hilbert)\tEnvelope\n";
    std::cout << "----------------------------------------------------------------\n";

    for (int n = 0; n < 40; ++n) {
        const double in = std::cos(2.0 * std::numbers::pi * 0.1 * static_cast<double>(n));
        const auto pair = filter.process(in);

        if (n >= 15) { // Пропускаємо початкове заповнення фільтра
            std::cout << n << "\t" 
                      << (in >= 0 ? " " : "") << in << "\t"
                      << (pair.real_i >= 0 ? " " : "") << pair.real_i << "\t"
                      << (pair.imag_q >= 0 ? " " : "") << pair.imag_q << "\t"
                      << pair.envelope() << "\n";
        }
    }

    return 0;
}
