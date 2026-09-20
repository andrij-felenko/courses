#include "estop_driver.h"
#include <iostream>

int main() {
    std::cout << "=== Промисловий моніторинг контуру E-Stop (C++) ===" << std::endl;

    EStopConfig config;
    config.debounce_ms = 10;
    config.max_discrepancy_ms = 100;

    EStopDriver driver(config);
    uint32_t time_ms = 0;

    // Сценарій 1: Нормальна робота (обидва NC-контакти замкнені = true)
    std::cout << "\n[Крок 1] Початок моніторингу у нормальному стані..." << std::endl;
    driver.update(true, true, time_ms);
    std::cout << "Поточний стан: " << (driver.isTripped() ? "Аварія" : "Норма") << std::endl;

    // Сценарій 2: Натискання кнопки E-Stop (обидва канали одночасно розмикаються = false)
    std::cout << "\n[Крок 2] Натискання кнопки аварійної зупинки..." << std::endl;
    time_ms += 50;
    // Опитування під час дебаунсу та фіксація
    driver.update(false, false, time_ms);
    time_ms += 15;
    driver.update(false, false, time_ms);

    std::cout << "Поточний стан: " << (driver.isTripped() ? "Аварія" : "Норма") << std::endl;

    // Сценарій 3: Спроба скидання, коли кнопка ще натиснута
    std::cout << "\n[Крок 3] Спроба скидання тривоги до повернення грибка..." << std::endl;
    driver.reset(time_ms);

    // Сценарій 4: Повернення грибка та успішний скид
    std::cout << "\n[Крок 4] Повернення грибка кнопкою у вихідне положення..." << std::endl;
    time_ms += 50;
    driver.update(true, true, time_ms);
    time_ms += 15;
    driver.update(true, true, time_ms);

    driver.reset(time_ms);
    std::cout << "Підсумковий стан: " << (driver.isTripped() ? "Аварія" : "Норма") << std::endl;

    // Сценарій 5: Симуляція апаратного пошкодження лінії (неодночасне розмикання понад 100 мс)
    std::cout << "\n[Крок 5] Симуляція обриву лише Каналу 1 (розсинхронізація)..." << std::endl;
    time_ms += 100;
    driver.update(false, true, time_ms); // Канал 1 розімкнено, Канал 2 замкнено
    time_ms += 15;
    driver.update(false, true, time_ms); // Таймер розсинхронізації запущено

    time_ms += 150; // Перевищення max_discrepancy_ms (100 мс)
    driver.update(false, true, time_ms);

    std::cout << "Стан після розсинхронізації: " << (driver.getState() == EStopState::DiscrepancyError ? "Помилка лінії (Discrepancy Error)" : "Інший") << std::endl;

    return 0;
}
