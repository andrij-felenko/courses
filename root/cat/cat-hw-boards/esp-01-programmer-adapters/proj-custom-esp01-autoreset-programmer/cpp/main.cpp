#include "esp01_tester.hpp"

// Екземпляр тестера для модуля ESP-01
// На модулі ESP-01 синій світлодіод підключено до GPIO2 (Active-Low)
static Esp01Tester g_tester(2, true);

void setup() {
    // Ініціалізація об'єктів тестування та вивід системної інформації при 115200 baud
    g_tester.begin(115200);
}

void loop() {
    // Головний цикл оновлення індикації та відправки статусу UART
    g_tester.update();
}
