#include <Arduino.h>

// Для вимірювання VCC через ESP.getVcc() необхідно додати макрос:
ADC_MODE(ADC_VCC);

void setupPowerManagement() {
    Serial.begin(115200);
    
    uint16_t vcc_mv = ESP.getVcc();
    Serial.printf("Напруга шини VCC: %u мВ\n", vcc_mv);
    
    if (vcc_mv < 2900) {
        Serial.println("КРИТИЧНЕ ПОПЕРЕДЖЕННЯ: Виявлено падіння живлення! Перевірте LDO та ємності.");
    }
}

void goToSleep(uint32_t seconds) {
    Serial.printf("Засинаємо на %u секунд...\n", seconds);
    // Для автоматичного пробудження GPIO16 має бути з'єднаний з RST
    ESP.deepSleep(seconds * 1000000ULL, WAKE_RF_DEFAULT);
}
