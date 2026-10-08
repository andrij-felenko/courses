// Налаштування апаратного таймера STM32 (HardwareTimer) у C++ для усунення jitter
#include <Arduino.h>

// Приклад для STM32 HAL / Arduino STM32 Core з використанням апаратного таймера TIM2
TIM_TypeDef *Instance = TIM2;
HardwareTimer *MyTimer = new HardwareTimer(Instance);

void setupHardwareTimerPWM() {
    // Налаштування каналу 1 для генерації апаратного ШІМ на виводі PA0
    MyTimer->setPWM(1, PA0, 50, 7.5); // Частота 50 Гц, початковий duty cycle 7.5% (1.5 мс)
    
    // Встановлення точної ширини імпульсу 1500 мкс через регістр порівняння CCR без переривань
    MyTimer->setCaptureCompare(1, 1500, MICROSECOND_COMPARE_FORMAT);
    MyTimer->resume();
}
