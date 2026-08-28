#include <iostream>
#include <cassert>
#include <array>
#include "sensor_driver.hpp"

class MockBus {
public:
    uint32_t current_time_us{0};
    std::array<uint8_t, 256> registers{};
    bool inject_bus_error{false};
    bool bus_recovered{false};

    [[nodiscard]] driver::Status read(uint8_t reg, std::span<uint8_t> rx) noexcept {
        if (inject_bus_error) return driver::Status::BusIo;
        for (size_t i = 0; i < rx.size(); ++i) {
            rx[i] = registers[static_cast<uint8_t>(reg + i)];
        }
        return driver::Status::Ok;
    }

    [[nodiscard]] driver::Status write(uint8_t reg, std::span<const uint8_t> tx) noexcept {
        if (inject_bus_error) return driver::Status::BusIo;
        for (size_t i = 0; i < tx.size(); ++i) {
            registers[static_cast<uint8_t>(reg + i)] = tx[i];
        }
        return driver::Status::Ok;
    }

    [[nodiscard]] uint32_t get_time_us() const noexcept {
        return current_time_us;
    }

    [[nodiscard]] driver::Status recover() noexcept {
        bus_recovered = true;
        inject_bus_error = false;
        return driver::Status::Ok;
    }
};

int main() {
    std::cout << "=== Запуск тестів драйвера сенсора на хості (C++) ===\n";

    MockBus mock;
    mock.registers[0xD0] = 0x58; // Expected Chip ID

    driver::SensorDevice<MockBus> sensor(mock);
    driver::Status st = sensor.init();
    assert(st == driver::Status::Ok);
    assert(sensor.state() == driver::State::Idle);
    std::cout << "[OK] Тест 1: Валідація Chip ID пройшла успішно\n";

    st = sensor.start_measurement();
    assert(st == driver::Status::Ok);
    assert(sensor.state() == driver::State::Converting);

    // Минуло лише 10 мс із 20 мс
    mock.current_time_us += 10000;
    auto res = sensor.poll();
    assert(!res.has_value());
    assert(res.error() == driver::Status::NotReady);
    std::cout << "[OK] Тест 2: Неблокуюче очікування (NotReady) працює коректно\n";

    // Минуло ще 15 мс (> 20 мс)
    mock.current_time_us += 15000;
    mock.registers[0xF7] = 0x66;
    mock.registers[0xF8] = 0x66;
    mock.registers[0xF9] = 0xBE;
    mock.registers[0xFA] = 0xE4;
    mock.registers[0xFB] = 0x42;
    mock.registers[0xFC] = 0x7E;

    res = sensor.poll();
    assert(res.has_value());
    assert(sensor.state() == driver::State::DataReady);
    std::cout << "[OK] Тест 3: Дані прочитано. T = " 
              << res->temperature_mdeg_c / 1000 << "." << res->temperature_mdeg_c % 1000 
              << " °C, P = " << res->pressure_pa << " Па\n";

    // Ін'єкція помилки CRC
    sensor.start_measurement();
    mock.current_time_us += 25000;
    mock.registers[0xF9] ^= 0xFF; // Псування контрольного байта

    res = sensor.poll();
    assert(!res.has_value());
    assert(res.error() == driver::Status::CrcMismatch);
    assert(sensor.state() == driver::State::Error);
    std::cout << "[OK] Тест 4: Спотворення даних успішно перехоплено перевіркою CRC-8\n";

    // Тест відновлення шини
    sensor.reset_fsm();
    mock.inject_bus_error = true;
    st = sensor.start_measurement();
    assert(st == driver::Status::BusIo);
    st = sensor.recover_bus();
    assert(st == driver::Status::Ok);
    assert(mock.bus_recovered);
    std::cout << "[OK] Тест 5: Автоматичне відновлення шини виконано успішно\n";

    std::cout << "=== Усі тести завершено успішно! ===\n";
    return 0;
}
