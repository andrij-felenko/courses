// Приклад неблокуючого виконання в середовищі Arduino Core for ESP8266
#include <ESP8266WiFi.h>

void processHeavyDataAsync(uint32_t totalIterations) {
    static uint32_t currentStep = 0;
    
    // Обробка даних порціями (chunking) для збереження кванту часу Wi-Fi стека
    while (currentStep < totalIterations) {
        // Виконання однієї порції обчислень
        doComputationStep(currentStep++);
        
        // Кожні 100 ітерацій повертаємо керування фоновим задачам та скидаємо WDT
        if (currentStep % 100 == 0) {
            yield(); // Передача кванту часу системному циклу Non-OS SDK
            return;  // Повернення керування для наступного виклику у loop()
        }
    }
}
