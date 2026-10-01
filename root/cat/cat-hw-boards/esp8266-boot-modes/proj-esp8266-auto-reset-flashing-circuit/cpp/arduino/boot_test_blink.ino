// Перевірка автономного старту ESP8266 (SPI Flash Boot Mode)
// Вивід логів на швидкості 74880 baud відповідає системному кварцу 26 МГц ROM-бутлоадера

#include <Arduino.h>

// Для більшості плат ESP8266 (NodeMCU, ESP-12E/F) вбудований світлодіод підключено до GPIO2 (інверсний рівень)
static const uint8_t LED_PIN = 2;
static uint32_t s_blink_counter = 0;

void setup() {
    // Налаштовуємо UART на 74880 baud для читання первинного логу ROM-завантажувача
    Serial.begin(74880);
    delay(100);

    Serial.println();
    Serial.println(F("========================================="));
    Serial.println(F("[BOOT VERIFY] Тест автономного старту ESP8266"));
    Serial.println(F("[BOOT VERIFY] Перевірка режиму SPI Flash Boot"));
    Serial.println(F("========================================="));

    // Виводимо системну інформацію про причину скидання чипа
    Serial.print(F("Причина останнього скидання (Reset Reason): "));
    Serial.println(ESP.getResetReason());

    Serial.print(F("Частота процесора: "));
    Serial.print(ESP.getCpuFreqMHz());
    Serial.println(F(" МГц"));

    Serial.print(F("Обсяг Flash-пам'яті: "));
    Serial.print(ESP.getFlashChipRealSize() / (1024 * 1024));
    Serial.println(F(" МБ"));

    // Налаштовуємо вивід GPIO2 для світлодіода
    pinMode(LED_PIN, OUTPUT);
    digitalWrite(LED_PIN, HIGH); // Вимкнено (інверсна логіка)

    Serial.println(F("[BOOT VERIFY] Успішно! ROM-бутлоадер запустив прошивку з Flash."));
    Serial.println(F("[BOOT VERIFY] Початок миготіння світлодіодом..."));
}

void loop() {
    s_blink_counter++;

    // Увімкнути світлодіод (LOW)
    digitalWrite(LED_PIN, LOW);
    Serial.print(F("[BLINK] Цикл #"));
    Serial.print(s_blink_counter);
    Serial.println(F(" -> Світлодіод УВІМКНЕНО"));
    delay(500);

    // Вимкнути світлодіод (HIGH)
    digitalWrite(LED_PIN, HIGH);
    Serial.print(F("[BLINK] Цикл #"));
    Serial.print(s_blink_counter);
    Serial.println(F(" -> Світлодіод ВИМКНЕНО"));
    delay(500);
}
