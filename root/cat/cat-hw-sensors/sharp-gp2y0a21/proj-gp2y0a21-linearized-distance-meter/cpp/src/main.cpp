#include "adc_interface.hpp"
#include "gp2y0a21.hpp"
#include <iostream>
#include <vector>
#include <iomanip>

/**
 * @brief Клас-імітатор АЦП для демонстрування роботи C++ драйвера SharpGP2Y0A21.
 * Згенерована послідовність містить нормальні значення, імпульсний шум та межові значення.
 */
class SimulatedAdcChannel : public IAdcChannel {
public:
    explicit SimulatedAdcChannel(std::vector<uint16_t> samples)
        : samples_(std::move(samples)), index_(0) {}

    uint16_t readRaw() override {
        if (samples_.empty()) {
            return 0;
        }
        uint16_t value = samples_[index_ % samples_.size()];
        index_++;
        return value;
    }

private:
    std::vector<uint16_t> samples_;
    std::size_t index_;
};

int main() {
    std::cout << "=== Драйвер ІЧ-далекоміра Sharp GP2Y0A21YK0F ===" << std::endl;

    // Послідовність вибірок АЦП:
    // 1. Початковий замір на ~20 см (ADC ~305) з імпульсним шумом (1023)
    // 2. Переміщення об'єкта на ~40 см (ADC ~165)
    // 3. Занадто близько (<10 см, ADC ~680)
    // 4. Занадто далеко (>80 см, ADC ~50)
    std::vector<uint16_t> adcSequence = {
        // Серія 1: ~20 см із поодинокою імпульсною завадою (1023)
        305, 310, 1023, 300, 308,

        // Серія 2: ~40 см
        165, 168, 162, 166, 164,

        // Серія 3: Об'єкт занадто близько (<10 см)
        650, 680, 700, 660, 690,

        // Серія 4: Об'єкт занадто далеко (>80 см)
        50, 45, 52, 48, 51
    };

    SimulatedAdcChannel adcHardware(adcSequence);
    SharpGP2Y0A21 sensor(adcHardware);

    std::cout << "\n--- Етап 1: Перевірка накопичення вибірок у буфері ---" << std::endl;
    for (int i = 1; i <= 4; ++i) {
        sensor.sample();
        MeasurementResult result = sensor.getDistance();
        std::cout << "Вибірка #" << i << " | Статус: ";
        if (result.status == DistanceStatus::InsufficientSamples) {
            std::cout << "InsufficientSamples (Буфер не заповнений)" << std::endl;
        }
    }

    std::cout << "\n--- Етап 2: Зчитування відстаней з придушенням завад та валідацією ---" << std::endl;
    for (std::size_t step = 0; step < 16; ++step) {
        sensor.sample();
        MeasurementResult result = sensor.getDistance();
        uint16_t medianValue = 0;
        sensor.getMedianAdc(medianValue);

        std::cout << "Крок #" << std::setw(2) << (step + 1)
                  << " | Медіана АЦП: " << std::setw(4) << medianValue
                  << " | Відстань: " << std::setw(6) << std::fixed << std::setprecision(2) << result.distanceCm << " см"
                  << " | Статус: ";

        switch (result.status) {
            case DistanceStatus::OK:
                std::cout << "OK";
                break;
            case DistanceStatus::OutOfBoundsTooClose:
                std::cout << "OutOfBoundsTooClose (<10 см)";
                break;
            case DistanceStatus::OutOfBoundsTooFar:
                std::cout << "OutOfBoundsTooFar (>80 см)";
                break;
            case DistanceStatus::InsufficientSamples:
                std::cout << "InsufficientSamples";
                break;
        }
        std::cout << std::endl;
    }

    return 0;
}
