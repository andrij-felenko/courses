#include "RVDTDecoder.hpp"
#include <iostream>
#include <iomanip>

/**
 * @brief Симуляція апаратного шинного адаптера SPI для підключення RDC-конвертера
 */
class SimulatedRvdSpiBus : public hw_controls::IRVdtSpiBus {
public:
    void set_cs(bool active) override {
        cs_active_ = active;
    }

    void set_sample(bool active) override {
        sample_active_ = active;
    }

    void set_mode_lines(bool a0, bool a1) override {
        a0_ = a0;
        a1_ = a1;
    }

    uint8_t transfer_byte(uint8_t tx_byte) override {
        (void)tx_byte;
        // Симуляція прийому нормальних даних позиції (наприклад код 32768 — нульове положення вала)
        if (!a0_ && !a1_) {
            byte_counter_++;
            return (byte_counter_ % 2 == 1) ? 0x80 : 0x00; // 0x8000 = 32768
        }
        
        // Симуляція читання регістра помилок (0x00 — відсутність аварій)
        return 0x00;
    }

    void delay_us(uint32_t microseconds) override {
        (void)microseconds;
    }

private:
    bool cs_active_{true};
    bool sample_active_{true};
    bool a0_{false};
    bool a1_{false};
    uint32_t byte_counter_{0};
};

int main() {
    std::cout << "=== Драйвер декодера RVDT (C++) ===\n\n";

    SimulatedRvdSpiBus spi_bus;

    hw_controls::RVDTConfig config{};
    config.resolution = hw_controls::Resolution::Bits16;
    config.excitation_freq = hw_controls::ExcitationFreq::Freq10kHz;
    config.full_scale_angle_deg = 60.0f; // Діапазон ±60°
    config.ratiometric_gain = 1.0f;

    hw_controls::RVDTDecoder decoder(spi_bus, config);

    if (!decoder.init()) {
        std::cout << "[ПОМИЛКА] Не вдалося ініціалізувати RDC-конвертер!\n";
        return 1;
    }
    std::cout << "[OK] RDC-конвертер успішно ініціалізовано.\n\n";

    // Симуляція основного циклу вимірювання
    for (int step = 1; step <= 3; ++step) {
        auto result = decoder.read_position();
        if (result && result->valid) {
            std::cout << "[Крок " << step << "] Отримано вимірювання RVDT:\n";
            std::cout << "  Сирий код: " << result->raw_code << "\n";
            std::cout << "  Кут (градуси): " << std::fixed << std::setprecision(3) << result->angle_deg << " deg\n";
            std::cout << "  Кут (радіани): " << std::setprecision(4) << result->angle_rad << " rad\n";
            std::cout << "  Статус: НОРМА\n\n";
        } else {
            std::cout << "[Крок " << step << "] Аварія тракту RVDT!\n";
            auto faults = decoder.read_faults();
            if (faults.loss_of_signal) {
                std::cout << "  - Виявлено розрив лінії збудження (LOS)\n";
            }
            if (faults.loss_of_tracking) {
                std::cout << "  - Втрата відстеження кута (LOT)\n";
            }
            decoder.reset_fault_latch();
        }
    }

    return 0;
}
