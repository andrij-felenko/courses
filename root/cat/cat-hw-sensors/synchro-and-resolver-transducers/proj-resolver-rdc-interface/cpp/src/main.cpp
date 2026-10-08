#include "ad2s1210_driver.hpp"
#include <iostream>
#include <iomanip>
#include <unordered_map>

/**
 * @brief Симулятор апаратного середовища (SPI та GPIO) для перевірки роботи драйвера AD2S1210.
 */
class SimulatedSpiHardware : public resolver::ISpiDriver, public resolver::ISpiGpio {
public:
    SimulatedSpiHardware() {
        // Заповнення замовчальних значень регістрів AD2S1210
        registers_[0x84] = 0x20; // LOS threshold
        registers_[0x85] = 0x7F; // DOS Overrange
        registers_[0x86] = 0x28; // DOS Mismatch
        registers_[0x87] = 0x0A; // LOT High
        registers_[0x88] = 0x05; // LOT Low
        registers_[0x89] = 0x28; // Excitation Freq
        registers_[0x92] = 0xC0; // Control (16-bit)
        registers_[0xFF] = 0x00; // Fault (відсутність помилок)
    }

    // --- Реалізація ISpiGpio ---
    void write_pin(Pin pin, Level level) override {
        switch (pin) {
            case Pin::CS: cs_pin_ = level; break;
            case Pin::A0:
                a0_pin_ = level;
                update_current_mode();
                break;
            case Pin::A1:
                a1_pin_ = level;
                update_current_mode();
                break;
            case Pin::SAMPLE:
                if (sample_pin_ == Level::High && level == Level::Low) {
                    // Симуляція засувки при спадному фронті SAMPLE
                    latched_position_code_ = current_sim_position_code_;
                    latched_velocity_code_ = current_sim_velocity_code_;
                }
                sample_pin_ = level;
                break;
            case Pin::RESET:
                reset_pin_ = level;
                if (level == Level::Low) {
                    registers_[0xFF] = 0x00;
                }
                break;
        }
    }

    void delay_us(std::uint32_t /*microseconds*/) override {
        // У симуляції програмна затримка не потрібна
    }

    // --- Реалізація ISpiDriver ---
    bool transfer(std::span<const std::uint8_t> tx_buf, std::span<std::uint8_t> rx_buf) override {
        for (std::size_t i = 0; i < tx_buf.size() && i < rx_buf.size(); ++i) {
            std::uint8_t rx = 0;
            if (!transfer_byte(tx_buf[i], rx)) return false;
            rx_buf[i] = rx;
        }
        return true;
    }

    bool transfer_byte(std::uint8_t tx_byte, std::uint8_t& rx_byte) override {
        rx_byte = 0;
        if (cs_pin_ == Level::High) {
            return false;
        }

        if (current_mode_ == resolver::Mode::Configuration) {
            if (!write_address_latched_) {
                selected_reg_addr_ = tx_byte;
                write_address_latched_ = true;
            } else {
                registers_[selected_reg_addr_] = tx_byte;
                write_address_latched_ = false;
            }
            rx_byte = registers_[selected_reg_addr_];
        } else if (current_mode_ == resolver::Mode::Position) {
            if (byte_counter_ == 0) {
                rx_byte = static_cast<std::uint8_t>((latched_position_code_ >> 8) & 0xFF);
                byte_counter_ = 1;
            } else {
                rx_byte = static_cast<std::uint8_t>(latched_position_code_ & 0xFF);
                byte_counter_ = 0;
            }
        } else if (current_mode_ == resolver::Mode::Velocity) {
            if (byte_counter_ == 0) {
                rx_byte = static_cast<std::uint8_t>((latched_velocity_code_ >> 8) & 0xFF);
                byte_counter_ = 1;
            } else {
                rx_byte = static_cast<std::uint8_t>(latched_velocity_code_ & 0xFF);
                byte_counter_ = 0;
            }
        }

        return true;
    }

    // Допоміжні методи симуляції руху валу
    void simulate_step(double delta_angle_deg, double current_rpm) {
        simulated_deg_ += delta_angle_deg;
        while (simulated_deg_ >= 360.0) simulated_deg_ -= 360.0;
        while (simulated_deg_ < 0.0) simulated_deg_ += 360.0;

        current_sim_position_code_ = static_cast<std::uint16_t>((simulated_deg_ / 360.0) * 65536.0);

        double max_rpm = 7500.0;
        double norm_vel = current_rpm / max_rpm;
        current_sim_velocity_code_ = static_cast<std::int16_t>(norm_vel * 32767.0);
    }

    void inject_fault(std::uint8_t fault_mask) {
        registers_[0xFF] |= fault_mask;
    }

    void clear_faults() {
        registers_[0xFF] = 0x00;
    }

private:
    Level cs_pin_{Level::High};
    Level a0_pin_{Level::Low};
    Level a1_pin_{Level::Low};
    Level sample_pin_{Level::High};
    Level reset_pin_{Level::High};

    resolver::Mode current_mode_{resolver::Mode::Position};
    std::unordered_map<std::uint8_t, std::uint8_t> registers_{};

    bool write_address_latched_{false};
    std::uint8_t selected_reg_addr_{0};
    int byte_counter_{0};

    double simulated_deg_{0.0};
    std::uint16_t current_sim_position_code_{0};
    std::int16_t current_sim_velocity_code_{0};
    std::uint16_t latched_position_code_{0};
    std::int16_t latched_velocity_code_{0};

    void update_current_mode() {
        std::uint8_t mode_val = (a1_pin_ == Level::High ? 2 : 0) | (a0_pin_ == Level::High ? 1 : 0);
        current_mode_ = static_cast<resolver::Mode>(mode_val);
        byte_counter_ = 0;
        write_address_latched_ = false;
    }
};

int main() {
    std::cout << "=== Драйвер AD2S1210 Перетворювача Резольвер-Цифра (C++) ===" << std::endl;

    SimulatedSpiHardware hardware;
    resolver::Ad2s1210Driver driver(hardware, hardware);

    resolver::Config config{};
    config.resolution = resolver::Resolution::Res16Bit;
    config.excitation_freq_hz = 10000; // 10 кГц
    config.clk_in_hz = 8192000;        // 8.192 МГц
    config.hysteresis_enable = true;

    std::cout << "\n[1] Ініціалізація драйвера та налаштування AD2S1210..." << std::endl;
    if (!driver.init(config)) {
        std::cerr << "Помилка: не вдалося ініціалізувати AD2S1210!" << std::endl;
        return 1;
    }
    std::cout << "Успішно ініціалізовано. Роздільна здатність: 16 біт, Частота збудження: 10 кГц." << std::endl;

    std::cout << "\n[2] Запуск вимірювального циклу руху валу резольвера:" << std::endl;
    std::cout << std::setw(6) << "Крок"
              << std::setw(14) << "Кут (град)"
              << std::setw(14) << "Кут (рад)"
              << std::setw(14) << "Швидкість(RPM)"
              << std::setw(14) << "Швидкість(рад/с)"
              << std::setw(12) << "Статус" << std::endl;
    std::cout << std::string(74, '-') << std::endl;

    double target_rpm = 1500.0; // Симуляція вращення валу з 1500 RPM
    double deg_per_step = (target_rpm * 360.0 / 60.0) * 0.005; // Крок за 5 мс

    for (int step = 1; step <= 8; ++step) {
        hardware.simulate_step(deg_per_step, target_rpm);

        auto data_opt = driver.read_resolver_data();
        if (data_opt.has_value()) {
            const auto& data = data_opt.value();
            std::cout << std::setw(6) << step
                      << std::fixed << std::setprecision(2)
                      << std::setw(14) << data.position_degrees
                      << std::setw(14) << data.position_radians
                      << std::setw(14) << data.velocity_rpm
                      << std::setw(14) << data.velocity_rad_per_sec
                      << std::setw(12) << (data.is_valid ? "OK" : "FAULT")
                      << std::endl;
        } else {
            std::cout << std::setw(6) << step << "  Помилка читання SPI" << std::endl;
        }
    }

    std::cout << "\n[3] Симуляція апаратного збою (LOS - Втрата сигналу резольвера):" << std::endl;
    hardware.inject_fault(0x04); // Біт 2 = LOS (Loss of Signal)

    auto fault_data_opt = driver.read_resolver_data();
    if (fault_data_opt.has_value()) {
        const auto& data = fault_data_opt.value();
        std::cout << "Результат вимірювання: data.is_valid = " << (data.is_valid ? "true" : "false") << std::endl;
        std::cout << "Деталізовані прапорці помилок Fault Register (0x" 
                  << std::hex << static_cast<int>(data.fault.raw_value) << std::dec << "):" << std::endl;
        std::cout << " - Втрата сигналу (LOS): " << (data.fault.loss_of_signal ? "ТАК" : "НІ") << std::endl;
        std::cout << " - Деградація сигналу (DOS): " << (data.fault.degradation_of_signal ? "ТАК" : "НІ") << std::endl;
        std::cout << " - Втрата стеження (LOT): " << (data.fault.loss_of_tracking ? "ТАК" : "НІ") << std::endl;
    }

    std::cout << "\n[4] Очищення апаратних помилок та скидання:" << std::endl;
    hardware.clear_faults();
    driver.reset_hardware();

    auto clean_data = driver.read_resolver_data();
    if (clean_data.has_value() && clean_data->is_valid) {
        std::cout << "Скидання пройшло успішно, пристрій повернувся в робочий стан." << std::endl;
    }

    std::cout << "\nДемонстрацію роботи C++ драйвера AD2S1210 завершено." << std::endl;
    return 0;
}
