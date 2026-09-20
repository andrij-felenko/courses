#include "Drv8833.hpp"
#include <iostream>

int main() {
    std::cout << "--- Запуск модуля керування моторами DRV8833 ---\n";

    Drv8833Config config;
    config.ain1_pin = 5;
    config.ain2_pin = 6;
    config.bin1_pin = 9;
    config.bin2_pin = 10;
    config.nsleep_pin = 4;
    config.nfault_pin = 2;
    config.timeout_ms = 2000;

    Drv8833 driver(config);
    driver.begin();

    std::cout << "[INFO] Драйвер ініціалізовано. Стан nSLEEP: "
              << (driver.isEnabled() ? "АКТИВНИЙ" : "СНУ") << "\n";

    std::cout << "\n[ТЕСТ 1] Запуск моторів: Мотор A = 80% (204 ШІМ), Мотор B = 50% (128 ШІМ)\n";
    driver.setMotor(MotorChannel::ChannelA, MotorMode::Forward, 204);
    driver.setMotor(MotorChannel::ChannelB, MotorMode::Forward, 128);

    uint32_t mockTimeMs = 100;
    driver.update(mockTimeMs);

    std::cout << "\n[ТЕСТ 2] Реверс: Мотор A = -255 (макс. назад), Мотор B = -100\n";
    driver.setSpeed(MotorChannel::ChannelA, -255);
    driver.setSpeed(MotorChannel::ChannelB, -100);

    mockTimeMs += 500;
    driver.update(mockTimeMs);

    std::cout << "\n[ТЕСТ 3] Активне гальмування мотора A та вільний хід мотора B\n";
    driver.stopMotor(MotorChannel::ChannelA, true);
    driver.stopMotor(MotorChannel::ChannelB, false);

    mockTimeMs += 200;
    driver.update(mockTimeMs);

    std::cout << "\n[ТЕСТ 4] Симуляція втрати зв'язку та спрацьовування таймауту ("
              << config.timeout_ms << " мс)...\n";
    driver.setSpeed(MotorChannel::ChannelA, 150);
    driver.setSpeed(MotorChannel::ChannelB, 150);

    mockTimeMs += 2500;
    driver.update(mockTimeMs);

    std::cout << "\n[ТЕСТ 5] Зупинка всіх моторів та переведення драйвера у режим сну (nSLEEP = LOW)\n";
    driver.stopAll(true);
    driver.disable();

    std::cout << "[INFO] Завершення роботи. Стан nSLEEP: "
              << (driver.isEnabled() ? "АКТИВНИЙ" : "СНУ") << "\n";

    return 0;
}
