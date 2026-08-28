/**
 * @file main_test.cpp
 * @brief Повний виконуваний тестовий набір для перевірки Transaction Layer.
 */

#include "CppAdapters.hpp"
#include "CppImuDriver.hpp"
#include <iostream>
#include <cassert>
#include <cmath>

int main() {
    using namespace embedded::bus;
    using namespace embedded::sensor;

    std::cout << "[TEST] 1. Ініціалізація віртуальної шини Mock Adapter..." << std::endl;
    MockBusAdapter mock_bus;

    // Встановлюємо очікуваний Chip ID в регістрі 0x00
    mock_bus.set_reg(ImuDriver<MockBusAdapter>::REG_CHIP_ID, 0x24);

    ImuDriver<MockBusAdapter> imu(mock_bus);

    auto init_res = imu.init();
    assert(init_res.has_value() && "Ініціалізація IMU має пройти успішно");
    std::cout << "  -> IMU успішно ініціалізовано. Chip ID підтверджено." << std::endl;
    std::cout << "  -> Регістр PWR_CTRL: 0x" << std::hex << (int)mock_bus.get_reg(0x7D) << std::dec << std::endl;
    assert(mock_bus.get_reg(0x7D) == 0x0E);

    std::cout << "[TEST] 2. Емуляція відліків сенсора (1g по осі Z, 0 по осях X та Y)..." << std::endl;
    // 1g = ~8192 LSB при шкалі ±4g (32768 / 4 = 8192)
    int16_t sim_az = 8192;
    mock_bus.set_reg(0x12, 0x00); // Accel X LSB
    mock_bus.set_reg(0x13, 0x00); // Accel X MSB
    mock_bus.set_reg(0x14, 0x00); // Accel Y LSB
    mock_bus.set_reg(0x15, 0x00); // Accel Y MSB
    mock_bus.set_reg(0x16, static_cast<uint8_t>(sim_az & 0xFF));        // Accel Z LSB
    mock_bus.set_reg(0x17, static_cast<uint8_t>((sim_az >> 8) & 0xFF)); // Accel Z MSB

    auto sample_res = imu.read_sample();
    assert(sample_res.has_value() && "Зчитування відліку має пройти успішно");

    const auto& sample = *sample_res;
    std::cout << "  -> Зчитане прискорення: X=" << sample.accel_mps2.x 
              << " Y=" << sample.accel_mps2.y 
              << " Z=" << sample.accel_mps2.z << " м/с²" << std::endl;

    assert(std::abs(sample.accel_mps2.z - 9.80665f) < 0.05f && "Прискорення Z має дорівнювати 1g (~9.81 м/с²)");

    std::cout << "[TEST] 3. Перевірка реакції на апаратну помилку шини (NACK Injection)..." << std::endl;
    mock_bus.set_inject_nack(true);
    auto failed_sample = imu.read_sample();
    assert(!failed_sample.has_value() && "Транзакція має завершитися помилкою при NACK");
    assert(failed_sample.error() == BusError::Nack);
    std::cout << "  -> Драйвер коректно повернув BusError::Nack без падіння системи." << std::endl;

    std::cout << "\n[SUCCESS] Усі модульні тести рівня транзакцій пройдено успішно!" << std::endl;
    return 0;
}
