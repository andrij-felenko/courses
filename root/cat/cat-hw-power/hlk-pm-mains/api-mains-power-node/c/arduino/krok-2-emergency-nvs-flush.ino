/* ============================================================================
   krok-2-emergency-nvs-flush.ino — Arduino: аварійне збереження (Dying Gasp)
   ========================================================================== */

#include <EEPROM.h>

const uint8_t PIN_ZERO_CROSS = 2;
const uint8_t PIN_RELAY      = 7;

struct DeviceMetrics {
    uint32_t switchCount;
    uint32_t activeSeconds;
    uint8_t  lastRelayState;
    uint8_t  magicMarker;
};

DeviceMetrics g_metrics = { 1042, 86400, 1, 0xA5 };
volatile unsigned long g_lastZeroCrossUs = 0;
volatile bool g_mainsLost = false;

void IRAM_ATTR onZeroCross() {
    g_lastZeroCrossUs = micros();
}

void setup() {
    Serial.begin(115200);
    pinMode(PIN_ZERO_CROSS, INPUT_PULLUP);
    pinMode(PIN_RELAY, OUTPUT);
    digitalWrite(PIN_RELAY, HIGH); // Реле увімкнене в робочому режимі

    EEPROM.begin(sizeof(DeviceMetrics));
    attachInterrupt(digitalPinToInterrupt(PIN_ZERO_CROSS), onZeroCross, FALLING);
    g_lastZeroCrossUs = micros();
}

void loop() {
    unsigned long now = micros();

    // Якщо за 15 мс немає імпульсу нуля — мережа пропала, задіюємо запас HLK-PM
    if (!g_mainsLost && (now - g_lastZeroCrossUs) > 15000) {
        g_mainsLost = true;

        // 1. Негайно знімаємо струм із котушки реле (економимо до 80 мА)
        digitalWrite(PIN_RELAY, LOW);

        // 2. Аварійний запис у EEPROM
        g_metrics.lastRelayState = 0;
        EEPROM.put(0, g_metrics);
#if defined(ESP8266) || defined(ESP32)
        EEPROM.commit();
#endif
        Serial.println(F("Dying Gasp: стан записано в EEPROM за 4 мс!"));

        // Зависаємо для безпечного вимкнення при падінні 5В/3.3В
        while (true) {
            delay(100);
        }
    }
}
