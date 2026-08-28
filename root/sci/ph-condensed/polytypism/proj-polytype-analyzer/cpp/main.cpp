#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <complex>
#include <cmath>
#include <iomanip>
#include <numbers>
#include <stdexcept>
#include <span >

class PolytypeSimulator20 {
public:
    explicit PolytypeSimulator20(int n1, int n2, std::string_view name = "Custom")
        : name_{name}, zhdanov_{n1, n2} {
        if (n1 < 0 || n2 < 0) {
            throw std::invalid_argument("Індекси Жданова не можуть бути від'ємними.");
        }
        expandSequence(n1, n2);
        computeJagodzinski();
    }

    [[nodiscard]] std::string_view getName() const noexcept { return name_; }
    [[nodiscard]] std::string_view getSequence() const noexcept { return sequence_; }
    [[nodiscard]] std::string_view getJagodzinski() const noexcept { return jagodzinski_; }
    [[nodiscard]] double getHexagonality() const noexcept { return hexagonality_; }
    [[nodiscard]] std::size_t getPeriod() const noexcept { return period_; }
    [[nodiscard]] std::pair<int, int> getZhdanov() const noexcept { return zhdanov_; }

    [[nodiscard]] double computeIntensity10L(double l_val) const noexcept {
        std::complex<double> s_sum{0.0, 0.0};
        const double pi = std::numbers::pi;
        
        for (std::size_t j = 0; j < period_; ++j) {
            double xj = 0.0;
            if (sequence_[j] == 'B') {
                xj = 2.0 / 3.0;
            } else if (sequence_[j] == 'C') {
                xj = 1.0 / 3.0;
            }

            double phase = 2.0 * pi * (xj + l_val * (static_cast<double>(j) / period_));
            s_sum += std::polar(1.0, phase);
        }
        return std::norm(s_sum);
    }

private:
    std::string name_;
    std::pair<int, int> zhdanov_;
    std::string sequence_;
    std::string jagodzinski_;
    std::size_t period_{0};
    double hexagonality_{0.0};

    void expandSequence(int n1, int n2) {
        if (n1 == 0 && n2 == 0) {
            sequence_ = "A";
            period_ = 1;
            return;
        }

        int curr = 0;
        sequence_.reserve(n1 + n2 + 1);
        sequence_ += 'A';

        for (int i = 0; i < n1; ++i) {
            curr = (curr + 1) % 3;
            sequence_ += (curr == 0 ? 'A' : (curr == 1 ? 'B' : 'C'));
        }
        for (int i = 0; i < n2; ++i) {
            curr = (curr + 2) % 3;
            sequence_ += (curr == 0 ? 'A' : (curr == 1 ? 'B' : 'C'));
        }
        period_ = sequence_.length() - 1;
        sequence_.pop_back();
    }

    void computeJagodzinski() {
        std::size_t h_count = 0;
        jagodzinski_.reserve(period_);

        for (std::size_t i = 0; i < period_; ++i) {
            char prev = sequence_[(i + period_ - 1) % period_];
            char next = sequence_[(i + 1) % period_];
            if (prev == next) {
                jagodzinski_ += 'h';
                h_count++;
            } else {
                jagodzinski_ += 'k';
            }
        }
        hexagonality_ = (static_cast<double>(h_count) / period_) * 100.0;
    }
};

int main() {
    try {
        const std::vector<PolytypeSimulator20> polytypes{
            PolytypeSimulator20{3, 0, "3C-SiC"},
            PolytypeSimulator20{2, 2, "4H-SiC"},
            PolytypeSimulator20{3, 3, "6H-SiC"},
            PolytypeSimulator20{3, 2, "15R-SiC"}
        };

        std::cout << std::fixed << std::setprecision(2);
        std::cout << std::left << std::setw(10) << "Політип" << " | "
                  << std::setw(8) << "Період N" << " | "
                  << std::setw(12) << "Шари" << " | "
                  << std::setw(16) << "Ягодзінський" << " | "
                  << std::setw(10) << "α_h (%)" << "\n";
        std::cout << std::string(68, '-') << "\n";

        for (const auto& sim : polytypes) {
            std::cout << std::setw(10) << sim.getName() << " | "
                      << std::setw(8) << sim.getPeriod() << " | "
                      << std::setw(12) << sim.getSequence() << " | "
                      << std::setw(16) << sim.getJagodzinski() << " | "
                      << std::setw(10) << sim.getHexagonality() << "%\n";
        }

        std::cout << "\nДифракційний профіль 4H-SiC (10L стержень):\n";
        const auto& sim4h = polytypes[1];
        for (double l = 0.0; l <= 2.0 + 1e-9; l += 0.25) {
            std::cout << "L = " << std::setw(4) << l 
                      << " | I(10L) = " << std::setw(6) << sim4h.computeIntensity10L(l) << "\n";
        }
    } catch (const std::exception& ex) {
        std::cerr << "Помилка симуляції: " << ex.what() << "\n";
        return 1;
    }

    return 0;
}
