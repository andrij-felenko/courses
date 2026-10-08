#include "power_management.hpp"
#include <iostream>

PowerManager::PowerManager(LowPowerMode initial_mode)
    : low_power_mode_(initial_mode) {}

PowerManager::~PowerManager() {
    if (woken_up_) {
        restoreSystemClock();
    }
}

void PowerManager::configureWakeupSource(uint8_t gpio_pin) {
    wakeup_pin_ = gpio_pin;
    wakeup_configured_ = true;
    std::cout << "[PowerManager] EXTI лінію на pin " << static_cast<int>(gpio_pin)
              << " зареєстровано як джерело пробудження (Wake-up Source).\n";
}

void PowerManager::enterSleep() {
    if (!wakeup_configured_) {
        std::cout << "[PowerManager] ПОПЕРЕДЖЕННЯ: Джерело пробудження не skonфігуровано!\n";
    }

    std::cout << "[PowerManager] Переведення мікроконтролера у режим ";
    switch (low_power_mode_) {
    case LowPowerMode::Sleep:
        std::cout << "Sleep (Light Sleep)...\n";
        break;
    case LowPowerMode::DeepSleep:
        std::cout << "Deep Sleep (Stop Mode)...\n";
        break;
    case LowPowerMode::Standby:
        std::cout << "Standby Mode...\n";
        break;
    }

    // Симуляція апаратного переходу у режим сну (на реальному МК: __WFI() або HAL_PWR_EnterSTOPMode())
    std::cout << "[PowerManager] [CPU] Тактування зупинено. Процесор чекає на апаратне переривання EXTI...\n";

    woken_up_ = true;
    restoreSystemClock();
}

void PowerManager::restoreSystemClock() {
    // Відновлення системних генераторів (PLL/HSI) та тактування периферії після пробудження зі сну
    std::cout << "[PowerManager] [SYS] Відновлено системне тактування (PLL / High-Speed Clock) та периферію.\n";
}
