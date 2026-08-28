#include <iostream>
#include <vector>
#include <cmath>
#include <complex>
#include <cstdint>
#include <numeric>

class V21Modem {
public:
    enum class Mode {
        Originate, // TX: 980/1180 Hz, RX: 1650/1850 Hz
        Answer     // TX: 1650/1850 Hz, RX: 980/1180 Hz
    };

    static constexpr double SampleRate = 8000.0;
    static constexpr double BaudRate = 300.0;
    static constexpr std::size_t SamplesPerBit = static_cast<std::size_t>(SampleRate / BaudRate);

    explicit V21Modem(Mode mode) : mode_(mode), phase_acc_(0.0) {
        if (mode_ == Mode::Originate) {
            tx_mark_ = 980.0;  tx_space_ = 1180.0;
            rx_mark_ = 1650.0; rx_space_ = 1850.0;
        } else {
            tx_mark_ = 1650.0; tx_space_ = 1850.0;
            rx_mark_ = 980.0;  rx_space_ = 1180.0;
        }
    }

    // Модуляція послідовності бітів у потік PCM-відліків
    [[nodiscard]] std::vector<float> modulate(const std::vector<uint8_t>& bits) {
        std::vector<float> pcm;
        pcm.reserve(bits.size() * SamplesPerBit);

        for (uint8_t bit : bits) {
            double freq = (bit != 0) ? tx_mark_ : tx_space_;
            double phase_inc = 2.0 * M_PI * freq / SampleRate;

            for (std::size_t i = 0; i < SamplesPerBit; ++i) {
                pcm.push_back(static_cast<float>(std::sin(phase_acc_)));
                phase_acc_ += phase_inc;
                if (phase_acc_ >= 2.0 * M_PI) {
                    phase_acc_ -= 2.0 * M_PI;
                }
            }
        }
        return pcm;
    }

    // Квадратурна демодуляція блоку PCM-відліків у біти
    [[nodiscard]] std::vector<uint8_t> demodulate(const std::vector<float>& pcm) const {
        std::size_t num_bits = pcm.size() / SamplesPerBit;
        std::vector<uint8_t> rx_bits;
        rx_bits.reserve(num_bits);

        double omega_mark = 2.0 * M_PI * rx_mark_ / SampleRate;
        double omega_space = 2.0 * M_PI * rx_space_ / SampleRate;

        for (std::size_t b = 0; b < num_bits; ++b) {
            std::complex<double> corr_mark{0.0, 0.0};
            std::complex<double> corr_space{0.0, 0.0};

            std::size_t offset = b * SamplesPerBit;
            for (std::size_t n = 0; n < SamplesPerBit; ++n) {
                double sample = pcm[offset + n];
                corr_mark += sample * std::polar(1.0, omega_mark * n);
                corr_space += sample * std::polar(1.0, omega_space * n);
            }

            rx_bits.push_back((std::norm(corr_mark) > std::norm(corr_space)) ? 1 : 0);
        }
        return rx_bits;
    }

private:
    Mode mode_;
    double phase_acc_;
    double tx_mark_, tx_space_;
    double rx_mark_, rx_space_;
};

int main() {
    V21Modem modem_tx(V21Modem::Mode::Originate);
    V21Modem modem_rx(V21Modem::Mode::Answer);

    const std::vector<uint8_t> tx_bits = {1, 0, 1, 1, 0, 0, 1, 0, 1, 1};

    std::cout << "=== V.21 FSK Modem Simulation (C++17) ===\n";
    std::cout << "Генерація модуляції FSK для " << tx_bits.size() << " бітів...\n";

    // 1. Модуляція
    auto pcm_signal = modem_tx.modulate(tx_bits);
    std::cout << "Згенеровано " << pcm_signal.size() << " відліків PCM.\n";

    // 2. Демодуляція
    auto rx_bits = modem_rx.demodulate(pcm_signal);

    // 3. Перевірка
    std::size_t errors = 0;
    for (std::size_t i = 0; i < tx_bits.size(); ++i) {
        bool match = (tx_bits[i] == rx_bits[i]);
        if (!match) ++errors;
        std::cout << "Біт " << i << ": TX=" << static_cast<int>(tx_bits[i])
                  << " -> RX=" << static_cast<int>(rx_bits[i])
                  << " [" << (match ? "OK" : "ERR") << "]\n";
    }

    std::cout << "Результат: " << (tx_bits.size() - errors) << "/" << tx_bits.size()
              << " бітів прийнято безпомилково.\n";

    return 0;
}
