#include <iostream>
#include <iomanip>
#include <cstdlib>
#include "HallSensorChopper.h"

// Функція для симуляції апаратного перемикання ключів давача Холла
void setHardwarePhase(int phase) {
    // В реальності тут буде запис у регістри мікроконтролера або керування GPIO
    // для перемикання напрямку струму через давач (чоппінг).
}

// Функція для симуляції зчитування АЦП
// Додаємо постійне зміщення (offset) та випадковий шум
float readAdc(int phase, float trueMagneticField, float offsetVoltage) {
    // Імітуємо випадковий шум (від -0.05 до 0.05)
    float noise = ((std::rand() % 100) / 100.0f - 0.5f) * 0.1f; 
    
    if (phase == 0) {
        return trueMagneticField + offsetVoltage + noise;
    } else {
        return -trueMagneticField + offsetVoltage + noise;
    }
}

int main() {
    // Ініціалізуємо давач з вікном фільтрації з 4 вимірювань
    HallSensorChopper sensor(4);
    
    // Параметри середовища для симуляції
    const float trueMagneticField = 2.5f; // Справжнє магнітне поле (корисний сигнал)
    const float offsetVoltage = 1.2f;     // Напруга зміщення (паразитний сигнал)
    
    std::cout << std::fixed << std::setprecision(3);
    std::cout << "Starting ADC polling loop...\n";
    std::cout << "True magnetic field: " << trueMagneticField 
              << ", Offset voltage: " << offsetVoltage << "\n\n";
              
    // Головний цикл (імітація регулярного опитування протягом 10 циклів вимірювання)
    // 20 ітерацій АЦП = 10 повних циклів чоппінгу
    for (int i = 0; i < 20; ++i) {
        // 1. Отримуємо поточну фазу, щоб налаштувати апаратні ключі
        int phase = sensor.getPhase();
        setHardwarePhase(phase);
        
        // 2. Зчитуємо сире значення з АЦП
        float rawAdc = readAdc(phase, trueMagneticField, offsetVoltage);
        
        // 3. Передаємо сире значення в тракт обробки (може викликатися в ISR)
        sensor.processAdcSample(rawAdc);
        
        // Виводимо результати після кожного повного циклу (після фази 1)
        if (phase == 1) {
            std::cout << "Chopper Cycle " << (i / 2) + 1 
                      << ": Compensated field = " << sensor.getCompensatedValue() << "\n";
        }
    }
    
    return 0;
}
