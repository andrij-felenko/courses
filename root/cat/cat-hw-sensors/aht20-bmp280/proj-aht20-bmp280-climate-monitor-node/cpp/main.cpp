#include <iostream>
#include <iomanip>
#include <chrono>
#include <thread>
#include <random>
#include <cstring>
#include "ClimateNode.hpp"

// Симулятор I2C шини для тестування кліматичного вузла без фізичного заліза
class MockI2CBus : public II2CBus {
public:
    MockI2CBus() : gen_(rd_()), noise_(-0.5f, 0.5f) {}

    bool writeRegisters(uint8_t dev_addr, uint8_t reg, const uint8_t* data, std::size_t len) override {
        if (dev_addr == BMP280_I2C_ADDR && reg == 0xF4 && len >= 1) {
            bmp280_ctrl_meas_ = data[0];
            return true;
        }
        return true;
    }

    bool readRegisters(uint8_t dev_addr, uint8_t reg, uint8_t* data, std::size_t len) override {
        if (dev_addr == BMP280_I2C_ADDR) {
            if (reg == 0xD0 && len == 1) {
                data[0] = 0x58; // BMP280 Chip ID
                return true;
            }
            if (reg == 0x88 && len == 24) {
                // Набір типових калібрувальних коефіцієнтів BMP280
                uint16_t calib[] = {
                    27504, 26435, -4000,
                    36477, -10685, 3024, 2855, 30, -11500, 9900, -2142, 4200
                };
                std::memcpy(data, calib, 24);
                return true;
            }
            if (reg == 0xF7 && len == 6) {
                // Генерація зашумлених показників для випробування фільтрації
                float sim_temp = 23.5f + noise_(gen_);
                float sim_press_hpa = 1013.25f + noise_(gen_);

                int32_t adc_T = static_cast<int32_t>((sim_temp + 10.0f) * 2000.0f);
                int32_t adc_P = static_cast<int32_t>((sim_press_hpa) * 400.0f);

                data[0] = (adc_P >> 12) & 0xFF;
                data[1] = (adc_P >> 4) & 0xFF;
                data[2] = (adc_P << 4) & 0xF0;
                data[3] = (adc_T >> 12) & 0xFF;
                data[4] = (adc_T >> 4) & 0xFF;
                data[5] = (adc_T << 4) & 0xF0;
                return true;
            }
        }
        return false;
    }

    bool writeBytes(uint8_t dev_addr, const uint8_t* data, std::size_t len) override {
        if (dev_addr == AHT20_I2C_ADDR) {
            if (len == 3 && data[0] == 0xAC) {
                aht20_triggered_ = true;
            }
            return true;
        }
        return false;
    }

    bool readBytes(uint8_t dev_addr, uint8_t* data, std::size_t len) override {
        if (dev_addr == AHT20_I2C_ADDR) {
            if (len == 1) {
                data[0] = 0x08; // Calibrated (bit 3 = 1), Not Busy (bit 7 = 0)
                return true;
            }
            if (len == 7) {
                data[0] = 0x08;

                float sim_temp = 23.2f + noise_(gen_);
                float sim_hum  = 48.5f + noise_(gen_);

                uint32_t raw_hum = static_cast<uint32_t>((sim_hum / 100.0f) * 1048576.0f);
                uint32_t raw_temp = static_cast<uint32_t>(((sim_temp + 50.0f) / 200.0f) * 1048576.0f);

                data[1] = (raw_hum >> 12) & 0xFF;
                data[2] = (raw_hum >> 4) & 0xFF;
                data[3] = ((raw_hum & 0x0F) << 4) | ((raw_temp >> 16) & 0x0F);
                data[4] = (raw_temp >> 8) & 0xFF;
                data[5] = raw_temp & 0xFF;
                data[6] = 0x00; // CRC
                return true;
            }
        }
        return false;
    }

private:
    std::random_device rd_;
    std::mt19937 gen_;
    std::uniform_real_distribution<float> noise_;
    uint8_t bmp280_ctrl_meas_{0};
    bool aht20_triggered_{false};
};

int main() {
    std::cout << "========================================================\n";
    std::cout << "  Кліматичний вузол AHT20 + BMP280 (Неблокуюче опитування)\n";
    std::cout << "========================================================\n\n";

    MockI2CBus i2c_bus;
    PollingConfig config;
    config.poll_interval_ms = 500; // Інтервал вимірювання 500 мс для демо
    config.aht20_delay_ms = 80;
    config.bmp280_delay_ms = 45;

    ClimateNode node(i2c_bus, config);

    if (!node.begin()) {
        std::cerr << "[ПОМИЛКА] Не вдалося ініціалізувати датчики AHT20 / BMP280!\n";
        return 1;
    }

    std::cout << "[ОК] Кліматичний вузол успішно проініціалізовано.\n";
    std::cout << "Запуск неблокуючого суперциклу виконання...\n\n";

    uint32_t simulated_time_ms = 0;
    uint32_t main_loop_ticks = 0;

    // Симуляція суперциклу виконання прошивки протягом 5 секунд
    while (simulated_time_ms <= 5000) {
        // Оновлюємо стан автомата опитування сенсорів
        node.update(simulated_time_ms);

        // Перевіряємо, чи зформовано новий телеметричний пакет
        if (node.hasNewPacket()) {
            auto packet_opt = node.getLatestPacket();
            if (packet_opt.has_value()) {
                const auto& packet = packet_opt.value();
                uint16_t calculated_crc = packet.calculateCRC();
                bool crc_ok = (calculated_crc == packet.checksum);

                std::cout << std::fixed << std::setprecision(2);
                std::cout << "[" << std::setw(5) << packet.timestamp_ms << " мс] Новий телеметричний пакет:\n";
                std::cout << "  ├── Температура : " << packet.temperature << " °C\n";
                std::cout << "  ├── Вологість    : " << packet.humidity << " %RH\n";
                std::cout << "  ├── Атм. тиск   : " << packet.pressure_hpa << " гПа\n";
                std::cout << "  ├── Прапорці    : 0x" << std::hex << static_cast<int>(packet.status_flags) << std::dec;
                std::cout << " (AHT20:" << ((packet.status_flags & 0x01) ? "OK" : "ERR");
                std::cout << ", BMP280:" << ((packet.status_flags & 0x02) ? "OK" : "ERR");
                std::cout << ", Filter:" << ((packet.status_flags & 0x04) ? "FULL" : "FILL") << ")\n";
                std::cout << "  └── CRC16-CCITT : 0x" << std::hex << packet.checksum << std::dec;
                std::cout << " (" << (crc_ok ? "ВАЛІДНА" : "ПОМИЛКА") << ")\n\n";
            }
        }

        main_loop_ticks++;
        simulated_time_ms += 10;
        std::this_thread::sleep_for(std::chrono::milliseconds(1));
    }

    std::cout << "========================================================\n";
    std::cout << "Виконання завершено успішно.\n";
    std::cout << "Всього ітерацій суперциклу: " << main_loop_ticks << " (головний цикл не блокувався).\n";

    return 0;
}
