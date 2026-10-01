#include <Arduino.h>

// Клас для опитування кнопок адаптера та керування індикацією
class ButtonTester {
public:
    ButtonTester(uint8_t flashPin, uint8_t ledPin, unsigned long debounceDelayMs = 50)
        : m_flashPin(flashPin),
          m_ledPin(ledPin),
          m_debounceDelayMs(debounceDelayMs),
          m_lastFlashState(HIGH),
          m_stableFlashState(HIGH),
          m_lastDebounceTime(0) {}

    // Ініціалізація апаратних виводів
    void begin() {
        // Налаштування кнопки Flash з внутрішньою підтяжкою до VCC
        pinMode(m_flashPin, INPUT_PULLUP);

        // Налаштування виводу індикатора (вбудований світлодіод ESP-01 на GPIO2, інверсна логіка)
        pinMode(m_ledPin, OUTPUT);
        digitalWrite(m_ledPin, HIGH); // Світлодіод вимкнено за замовчуванням (активний LOW)

        // Первинне зчитування стану
        m_stableFlashState = digitalRead(m_flashPin);
        m_lastFlashState = m_stableFlashState;

        Serial.println(F("[ButtonTester] Апаратні виводи GPIO0 (Flash) та GPIO2 (LED) успішно ініціалізовано."));
    }

    // Періодичне опитування стану з програмним придушенням дребезгу
    void update() {
        int reading = digitalRead(m_flashPin);
        unsigned long currentMillis = millis();

        // Якщо рівень змінився (включаючи дребезг), перезапускаємо таймер
        if (reading != m_lastFlashState) {
            m_lastDebounceTime = currentMillis;
            m_lastFlashState = reading;
        }

        // Перевіряємо, чи минув інтервал придушення дребезгу
        if ((currentMillis - m_lastDebounceTime) > m_debounceDelayMs) {
            // Якщо стан дійсно змінився порівняно зі стабільним
            if (reading != m_stableFlashState) {
                m_stableFlashState = reading;

                // Обробка зміни стану кнопки Flash (GPIO0)
                if (m_stableFlashState == LOW) {
                    // Кнопку натиснуто (замкнено на GND)
                    digitalWrite(m_ledPin, LOW); // Увімкнути світлодіод індикації
                    Serial.print(F("[ПОДІЯ] ["));
                    Serial.print(currentMillis);
                    Serial.println(F(" ms] Кнопка Flash (GPIO0) НАТИСНУТА (LOW). Світлодіод УВІМКНЕНО."));
                } else {
                    // Кнопку відпущено (підтягнуто до 3.3V)
                    digitalWrite(m_ledPin, HIGH); // Вимкнути світлодіод
                    Serial.print(F("[ПОДІЯ] ["));
                    Serial.print(currentMillis);
                    Serial.println(F(" ms] Кнопка Flash (GPIO0) ВІДПУЩЕНА (HIGH). Світлодіод ВИМКНЕНО."));
                }
            }
        }
    }

    // Отримання поточного стабільного стану кнопки Flash
    bool isFlashPressed() const {
        return (m_stableFlashState == LOW);
    }

private:
    uint8_t m_flashPin;
    uint8_t m_ledPin;
    unsigned long m_debounceDelayMs;
    int m_lastFlashState;
    int m_stableFlashState;
    unsigned long m_lastDebounceTime;
};

// Константи виводів модуля ESP-01
constexpr uint8_t FLASH_BUTTON_PIN = 0; // GPIO0 (кнопка Flash / завантаження)
constexpr uint8_t LED_INDICATOR_PIN = 2; // GPIO2 (синій індикаторний світлодіод ESP-01)
constexpr unsigned long SERIAL_BAUD_RATE = 115200; // Швидкість послідовного порту

// Глобальний екземпляр тестера
ButtonTester g_buttonTester(FLASH_BUTTON_PIN, LED_INDICATOR_PIN);

void setup() {
    // Ініціалізація послідовного порту UART
    Serial.begin(SERIAL_BAUD_RATE);
    delay(200); // Час на стабілізацію лінії UART після подачі живлення

    Serial.println();
    Serial.println(F("=================================================="));
    Serial.println(F("   Тестовий скетч діагностики адаптера ESP-01    "));
    Serial.println(F("=================================================="));

    // Друк інформації про причину останнього скидання ESP8266
    Serial.print(F("[СИСТЕМА] Причина скидання чипа: "));
    Serial.println(ESP.getResetReason());
    Serial.print(F("[СИСТЕМА] Частота ядра CPU: "));
    Serial.print(ESP.getCpuFreqMHz());
    Serial.println(F(" МГц"));
    Serial.print(F("[СИСТЕМА] Розмір Flash-пам'яті: "));
    Serial.print(ESP.getFlashChipSize() / 1024);
    Serial.println(F(" КБ"));

    // Ініціалізація об'єкта перевірки кнопок
    g_buttonTester.begin();
    Serial.println(F("[СИСТЕМА] Тестування запущено. Натисніть кнопку Flash або Reset на адаптері..."));
    Serial.println(F("--------------------------------------------------"));
}

void loop() {
    // Опитування стану кнопок адаптера у кожному циклі
    g_buttonTester.update();
}
