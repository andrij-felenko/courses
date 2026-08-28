#include <iostream>
#include <cassert>

int main() {
    std::cout << "[C++20 Mock Test] Початок тестування концептуального драйвера BME280...\n";

    using MockBus = hal::mock::MockI2cBus<256>;
    MockBus mock_bus{sensors::Bme280<MockBus>::DefaultAddress};

    /* Налаштування регістрів емулятора */
    mock_bus.set_reg(sensors::Bme280<MockBus>::ChipIdRegister, sensors::Bme280<MockBus>::ExpectedChipId);
    mock_bus.set_reg(sensors::Bme280<MockBus>::CalibRegister + 0, 0x70);
    mock_bus.set_reg(sensors::Bme280<MockBus>::CalibRegister + 1, 0x6B);
    mock_bus.set_reg(sensors::Bme280<MockBus>::CalibRegister + 2, 0x43);
    mock_bus.set_reg(sensors::Bme280<MockBus>::CalibRegister + 3, 0x67);
    mock_bus.set_reg(sensors::Bme280<MockBus>::CalibRegister + 4, 0x18);
    mock_bus.set_reg(sensors::Bme280<MockBus>::CalibRegister + 5, 0xFC);

    mock_bus.set_reg(sensors::Bme280<MockBus>::TempMsbReg + 0, 0x7E);
    mock_bus.set_reg(sensors::Bme280<MockBus>::TempMsbReg + 1, 0xEC);
    mock_bus.set_reg(sensors::Bme280<MockBus>::TempMsbReg + 2, 0x00);

    /* Створення екземпляра шаблонного драйвера */
    sensors::Bme280<MockBus> sensor{mock_bus};

    auto status = sensor.init();
    assert(hal::is_ok(status));
    std::cout << " -> C++20 сенсор успішно ініціалізовано.\n";

    auto [read_status, temp] = sensor.read_temperature_c_x100();
    assert(hal::is_ok(read_status));
    std::cout << " -> Зчитана температура: " << (temp / 100) << "." << (temp % 100) << " °C\n";
    assert(temp >= 2400 && temp <= 2600);

    mock_bus.set_force_nack(true);
    auto [err_status, _] = sensor.read_temperature_c_x100();
    assert(err_status == hal::Status::Nack);
    std::cout << " -> Перевірка відмови зв'язку NACK успішна.\n";

    std::cout << "[C++20 Mock Test] Усі концептуальні перевірки пройдено!\n";
    return 0;
}
