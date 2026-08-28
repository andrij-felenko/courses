/**
 * @file main.cpp
 * @brief Тестова верифікація C++20 драйвера BMP280 з використанням концептів та одиниць SI.
 */

#include <iostream>
#include <vector>
#include <array>
#include <cstring>
#include <cassert>
#include "Bmp280Driver.hpp"

using namespace sf::devices;
using namespace sf::devices::units::literals;

/**
 * @brief Емулятор апаратної шини, що задовольняє концепт BusDevice.
 */
class MockBusHardware {
public:
    DriverError read(uint8_t devAddr, uint8_t reg, std::span<uint8_t> rx) noexcept {
        (void)devAddr;
        if (isLocked_) return DriverError::BusTimeout;

        if (reg == 0xD0 && rx.size() == 1) {
            rx[0] = 0x58; // BMP280 Chip ID
            return DriverError::None;
        }

        if (reg == 0x88 && rx.size() <= calibRom_.size()) {
            std::memcpy(rx.data(), calibRom_.data(), rx.size());
            return DriverError::None;
        }

        if (reg == 0xF7 && rx.size() <= sampleRegs_.size()) {
            std::memcpy(rx.data(), sampleRegs_.data(), rx.size());
            return DriverError::None;
        }

        return DriverError::None;
    }

    DriverError write(uint8_t devAddr, uint8_t reg, std::span<const uint8_t> tx) noexcept {
        (void)devAddr;
        (void)reg;
        (void)tx;
        if (isLocked_) return DriverError::BusTimeout;
        return DriverError::None;
    }

    DriverError readDmaAsync(uint8_t devAddr, uint8_t reg, std::span<uint8_t> rx) noexcept {
        (void)devAddr;
        if (isLocked_) return DriverError::BusTimeout;
        if (reg == 0xF7 && rx.size() <= sampleRegs_.size()) {
            std::memcpy(rx.data(), sampleRegs_.data(), rx.size());
            return DriverError::None;
        }
        return DriverError::BusNack;
    }

    void resetBus() noexcept {
        isLocked_ = false;
        recoveryCycles_ += 9;
    }

    void delayMs(uint32_t ms) noexcept {
        (void)ms;
    }

    void setLock(bool lock) noexcept { isLocked_ = lock; }

    MockBusHardware() {
        // Заповнення калібрувальної NVM таблиці
        calibRom_ = {
            0x70, 0x6B, 0xE8, 0xFB, 0x18, 0xFC,
            0x7D, 0x8E, 0x43, 0xD6, 0xD0, 0x0B,
            0x27, 0x0B, 0x8C, 0x00, 0xF9, 0xFF,
            0x8C, 0x3C, 0xF8, 0xC6, 0x70, 0x17
        };

        // Заповнення тестового вектора: ADC_P = 415148, ADC_T = 519888
        sampleRegs_ = {
            0x65, 0x5A, 0xC0, // PRESS_MSB, LSB, XLSB
            0x7E, 0xEC, 0x00  // TEMP_MSB, LSB, XLSB
        };
    }

private:
    std::array<uint8_t, 24> calibRom_{};
    std::array<uint8_t, 6>  sampleRegs_{};
    bool isLocked_{false};
    uint32_t recoveryCycles_{0};
};

static_assert(BusDevice<MockBusHardware>, "MockBusHardware must satisfy BusDevice concept");

int main() {
    std::cout << "[TEST C++20] Запуск верифікації Bmp280Driver...\n";

    MockBusHardware bus;
    Bmp280Driver<MockBusHardware> driver(bus);

    // 1. Тест ініціалізації
    auto err = driver.initialize();
    assert(err == DriverError::None);
    std::cout << "  [OK] Драйвер успішно ініціалізований через C++20 концепт BusDevice\n";

    // 2. Тест конфігурації
    err = driver.configure(OverSampling::X2, OverSampling::X16, SensorMode::Normal, IirFilter::X16);
    assert(err == DriverError::None);
    std::cout << "  [OK] Типобезпечна конфігурація записана\n";

    // 3. Тест синхронного вимірювання
    auto optSample = driver.readSynchronous();
    assert(optSample.has_value());
    assert(optSample->isValid);

    std::cout << "  [OK] Отримано вибірку SI:\n";
    std::cout << "       Температура: " << optSample->temperature.value() << " °C ("
              << optSample->temperature.kelvin() << " K)\n";
    std::cout << "       Тиск: " << optSample->pressure.value() << " Па ("
              << optSample->pressure.hectopascals() << " гПа / "
              << optSample->pressure.millibars() << " мбар)\n";

    // Порівняння з користувацькими літералами
    assert(optSample->pressure.hectopascals() > 1000.0f);
    assert(optSample->pressure < 110000.0_Pa);

    // 4. Тест асинхронного DMA
    err = driver.startDmaRead();
    assert(err == DriverError::None);
    driver.onDmaComplete();

    auto last = driver.lastSample();
    assert(last.has_value());
    assert(last->isValid);
    std::cout << "  [OK] Асинхронний DMA трансфер та callback перевірено\n";

    // 5. Тест шинного збою та відновлення
    bus.setLock(true);
    auto failedSample = driver.readSynchronous();
    assert(!failedSample.has_value());
    assert(driver.errorCount() > 0);

    err = driver.recover();
    assert(err == DriverError::None);
    std::cout << "  [OK] Автоматичне відновлення шини (9 SCL тактів) виконано успішно\n";

    std::cout << "[SUCCESS] Усі тести C++20 драйвера пройдено бездоганно!\n";
    return 0;
}
