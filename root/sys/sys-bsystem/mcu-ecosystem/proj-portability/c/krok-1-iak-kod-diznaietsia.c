// Діагностика: яка платформа йде у збірку?
#if defined(ARDUINO_ARCH_ESP32)
  #pragma message("Target: ESP32 (Arduino core)")
#elif defined(__AVR__)
  #pragma message("Target: AVR (bare-metal or Arduino AVR)")
#elif defined(ARDUINO_ARCH_STM32)
  #pragma message("Target: STM32 (Arduino_STM32 core)")
#elif defined(ESP_PLATFORM)
  #pragma message("Target: ESP32 (ESP-IDF)")
#else
  #error "Непідтримувана платформа — додайте гілку HAL для цього чипа!"
#endif
