#include "Adxl345.hpp"
#include <iostream>
#include <iomanip>
#include <vector>
#include <deque>
#include <cmath>

// Модель апаратного шинного інтерфейсу I2C для симуляції роботи акселерометра ADXL345
class SimulatedI2cBus : public adxl345::IBus {
public:
    SimulatedI2cBus() {
        // Ініціалізація скинутих значень регістрів ADXL345
        registers_[adxl345::Register::DEVID] = adxl345::ADXL345_EXPECTED_DEVID;
        registers_[adxl345::Register::POWER_CTL] = 0x00;
        registers_[adxl345::Register::DATA_FORMAT] = 0x00;
        registers_[adxl345::Register::FIFO_CTL] = 0x00;
        registers_[adxl345::Register::FIFO_STATUS] = 0x00;
        registers_[adxl345::Register::INT_SOURCE] = 0x00;
    }

    bool writeRegister(uint8_t reg, uint8_t value) override {
        registers_[reg] = value;
        return true;
    }

    bool readRegister(uint8_t reg, uint8_t& value) override {
        if (reg == adxl345::Register::FIFO_STATUS) {
            // Динамічне повернення кількості накопичених кадрів у FIFO
            value = static_cast<uint8_t>(fifoQueue_.size() & 0x1F);
        } else if (reg == adxl345::Register::INT_SOURCE) {
            uint8_t intStatus = 0;
            uint8_t watermark = registers_[adxl345::Register::FIFO_CTL] & 0x1F;
            if (fifoQueue_.size() >= watermark && watermark > 0) {
                intStatus |= adxl345::IntBit::WATERMARK;
            }
            if (fifoQueue_.size() >= 32) {
                intStatus |= adxl345::IntBit::OVERRUN;
            }
            value = intStatus;
        } else {
            value = registers_[reg];
        }
        return true;
    }

    bool readBurst(uint8_t startReg, std::span<uint8_t> buffer) override {
        if (startReg == adxl345::Register::DATAX0) {
            // Читання з FIFO-буфера
            size_t sampleCount = buffer.size() / 6;
            for (size_t i = 0; i < sampleCount; ++i) {
                if (fifoQueue_.empty()) {
                    break;
                }
                auto rawFrame = fifoQueue_.front();
                fifoQueue_.pop_front();

                size_t offset = i * 6;
                buffer[offset + 0] = static_cast<uint8_t>(rawFrame[0] & 0xFF);
                buffer[offset + 1] = static_cast<uint8_t>((rawFrame[0] >> 8) & 0xFF);
                buffer[offset + 2] = static_cast<uint8_t>(rawFrame[1] & 0xFF);
                buffer[offset + 3] = static_cast<uint8_t>((rawFrame[1] >> 8) & 0xFF);
                buffer[offset + 4] = static_cast<uint8_t>(rawFrame[2] & 0xFF);
                buffer[offset + 5] = static_cast<uint8_t>((rawFrame[2] >> 8) & 0xFF);
            }
            return true;
        }
        return false;
    }

    // Метод симуляції надходження нових інерційних даних від сенсора
    void generateHardwareSample(int16_t rawX, int16_t rawY, int16_t rawZ) {
        if (fifoQueue_.size() < 32) {
            fifoQueue_.push_back({rawX, rawY, rawZ});
        }
    }

private:
    std::unordered_map<uint8_t, uint8_t> registers_;
    std::deque<std::array<int16_t, 3>> fifoQueue_;
};

int main() {
    std::cout << "--- Запуск C++ драйвера акселерометра ADXL345 ---\n";

    SimulatedI2cBus bus;
    adxl345::ADXL345 sensor(bus);

    // 1. Ініціалізація акселерометра (розмах ±2g, повна роздільна здатність)
    if (!sensor.init(adxl345::Range::Range_2G, true)) {
        std::cerr << "Помилка: не вдалося ініціалізувати ADXL345!\n";
        return 1;
    }
    std::cout << "ADXL345 успішно ініціалізовано.\n";

    // 2. Реєстрація зворотного виклику (callback) для події досягнення рівня Watermark у FIFO
    sensor.registerCallback(adxl345::Event::Watermark, [](adxl345::Event event, std::span<const adxl345::AccelData> samples) {
        (void)event;
        std::cout << "\n[ПОДІЯ: WATERMARK] Отримано пачку з " << samples.size() << " кадрів з FIFO-буфера:\n";
        for (size_t i = 0; i < samples.size(); ++i) {
            std::cout << "  Кадр [" << std::setw(2) << i + 1 << "] -> "
                      << "X: " << std::setw(7) << std::fixed << std::setprecision(4) << samples[i].x << " g | "
                      << "Y: " << std::setw(7) << std::fixed << std::setprecision(4) << samples[i].y << " g | "
                      << "Z: " << std::setw(7) << std::fixed << std::setprecision(4) << samples[i].z << " g\n";
        }
    });

    // 3. Реєстрація callback для обробки переповнення FIFO (Overrun)
    sensor.registerCallback(adxl345::Event::Overrun, [](adxl345::Event event, std::span<const adxl345::AccelData> samples) {
        (void)event;
        (void)samples;
        std::cout << "\n[ПОПЕРЕДЖЕННЯ: OVERRUN] Переповнення апаратного FIFO-буфера ADXL345!\n";
    });

    // 4. Конфігурація FIFO: Потоковий режим (Stream), поріг Watermark = 8 кадрів
    constexpr uint8_t WATERMARK_LEVEL = 8;
    if (!sensor.configureFifo(adxl345::FifoMode::Stream, WATERMARK_LEVEL)) {
        std::cerr << "Помилка налаштування FIFO буфера!\n";
        return 1;
    }
    std::cout << "Налаштовано Stream FIFO режим із рівнем Watermark = " << static_cast<int>(WATERMARK_LEVEL) << ".\n";

    // 5. Симуляція неблокуючого головного циклу обробки (Super-loop)
    std::cout << "Запуск суперциклу опитування сенсора...\n";
    float step = 0.0f;
    for (int cycle = 0; cycle < 25; ++cycle) {
        // Симуляція генерації 1 кадру прискорення кожні кілька ітерацій
        // Моделюємо дію сили тяжіння (~1g по осі Z) із гармонічною вібрацією по X та Y
        int16_t rawX = static_cast<int16_t>(std::sin(step) * 100.0f);
        int16_t rawY = static_cast<int16_t>(std::cos(step) * 100.0f);
        int16_t rawZ = static_cast<int16_t>(256.0f + std::sin(step * 2.0f) * 10.0f); // ~1.0g + шум
        step += 0.4f;

        bus.generateHardwareSample(rawX, rawY, rawZ);

        // Обробка переривань у неблокуючому стилі
        sensor.processInterrupts();
    }

    std::cout << "\nРоботу драйвера ADXL345 успішно завершено.\n";
    return 0;
}
