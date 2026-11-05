#include "I2cLevelShifter.hpp"
#include <iostream>

int main() {
    hardware::I2cLevelShifter shifter(0, 21, 22, hardware::BusSpeed::Standard);

    std::cout << "I2cLevelShifter ініціалізовано. Опитування 5V давача..." << std::endl;

    constexpr uint8_t kSensorAddress = 0x48;
    uint8_t sensor_data[2] = {0};

    hardware::I2cError err = shifter.readData(kSensorAddress, sensor_data, sizeof(sensor_data));
    
    if (err == hardware::I2cError::Success) {
        std::cout << "Успішно прочитано дані з 5V сенсора." << std::endl;
    } else {
        std::cerr << "Помилка комунікації з 5V сенсором! Спроба відновлення шини..." << std::endl;
        
        if (shifter.recoverBus() == hardware::I2cError::Success) {
            std::cout << "Шину успішно відновлено." << std::endl;
            shifter.setSpeed(hardware::BusSpeed::Fast);
        } else {
            std::cerr << "Критична помилка: не вдалося відновити шину I2C." << std::endl;
            return 1;
        }
    }

    return 0;
}
