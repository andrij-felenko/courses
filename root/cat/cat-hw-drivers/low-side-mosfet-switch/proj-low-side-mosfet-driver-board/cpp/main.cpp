#include "LowSideMosfet.hpp"
#include <iostream>
#include <thread>
#include <chrono>

int main() {
    std::cout << "=== Драйвер низькостороннього MOSFET-ключа (Low-Side Switch) ===" << std::endl;
    std::cout << "Демонстрація безпечного керування силовим навантаженням через ШІМ\n" << std::endl;

    // 1. Створення об'єкта драйвера
    LowSideMosfet mosfetDriver;

    // 2. Конфігурація апаратних параметрів
    MosfetConfig config;
    config.gpioPin = 15;               // Пин МК, підключений до затвора MOSFET через резистор
    config.pwmFrequencyHz = 2000;      // 2 кГц ШІМ для силового навантаження
    config.initialDutyCycle = 0.0f;    // Безпечний початковий стан (0% потужності)
    config.invertedLogic = false;      // Пряма логіка (HIGH = MOSFET відкритий)
    config.timerClockHz = 16000000;    // Тактова частота таймера МК (16 МГц)

    // 3. Безпечна ініціалізація
    if (!mosfetDriver.begin(config)) {
        std::cout << "Неможливо ініціалізувати драйвер MOSFET!" << std::endl;
        return 1;
    }

    std::cout << "\n--- 4. Увімкнення драйвера та встановлення базової потужності ---" << std::endl;
    mosfetDriver.enable();
    mosfetDriver.setDutyCycle(25.0f); // 25% потужності

    std::cout << "\n--- 5. Динамічне змінення частоти ШІМ ---" << std::endl;
    // Зміна частоти до 8 кГц (наприклад, для зменшення акустичного шуму обмоток мотора)
    mosfetDriver.setFrequency(8000);

    std::cout << "\n--- 6. Плавний пуск навантаження (Ramp Up 25% -> 80%) ---" << std::endl;
    // Плавне нарощування потужності від 25% до 80% за 300 мс з кроком 50 мс
    mosfetDriver.rampPower(80.0f, 300, 50);

    std::this_thread::sleep_for(std::chrono::milliseconds(200));

    std::cout << "\n--- 7. Плавне зниження потужності (Ramp Down 80% -> 10%) ---" << std::endl;
    mosfetDriver.rampPower(10.0f, 200, 40);

    std::cout << "\n--- 8. Перевірка спрацьовування аварійного вимкнення (Emergency Stop) ---" << std::endl;
    mosfetDriver.emergencyStop();

    std::cout << "\n--- 9. Спроба роботи після аварійного вимкнення та повторний запуск ---" << std::endl;
    std::cout << "Поточний стан увімкнення: " << (mosfetDriver.isEnabled() ? "УВІМКНЕНО" : "ВИМКНЕНО") << std::endl;
    
    // Відновлення роботи після зняття аварійного блокування
    mosfetDriver.enable();
    mosfetDriver.setDutyCycle(50.0f);

    std::cout << "\n--- 10. Завершення роботи програми (Деструктор автоматично вимкне ключ) ---" << std::endl;
    return 0;
}
