#include <Wire.h>

static const uint8_t PCF_ADDR = 0x20;   // A0..A2 = 0
static const uint8_t INT_PIN  = 4;      // вивід INT чипа → GPIO4 ESP32

// Тіньова копія порту: біти входів (P4) тримаємо в 1, решта — стани виходів.
// 0 у біті виходу = світлодіод горить (активний низький рівень).
static uint8_t shadow = 0xFF;           // старт: усе вимкнено, входи відпущені

static bool pcf_write(uint8_t value) {
    Wire.beginTransmission(PCF_ADDR);
    Wire.write(value);                  // один байт — нові стани всіх 8 ніжок
    return Wire.endTransmission() == 0; // 0 = чип відповів ACK; інакше NACK
}

static bool pcf_read(uint8_t *out) {
    if (Wire.requestFrom(PCF_ADDR, (uint8_t)1) != 1) return false;
    *out = Wire.read();                 // знімок усіх 8 ніжок «як є»
    return true;
}

static inline bool button_pressed(uint8_t port) {
    return (port & (1 << 4)) == 0;      // кнопка на землю → натиснута = 0
}

void setup() {
    Wire.begin();                       // SDA/SCL за замовчуванням платформи
    pinMode(INT_PIN, INPUT_PULLUP);     // INT відкритий стік → підтяжка вгору

    shadow &= ~(1 << 0);                // P0 = 0 → перший світлодіод горить
    shadow |=  (1 << 4);                // P4 = 1 → дозволяємо читати кнопку
    pcf_write(shadow);                  // одна транзакція ≈ 180 мкс на 100 кГц
}

void loop() {
    // INT в open-drain просідає в 0, коли на вході щось змінилося.
    if (digitalRead(INT_PIN) == LOW) {
        uint8_t port;
        if (pcf_read(&port)) {          // саме читання знімає сигнал INT чипа
            if (button_pressed(port))
                shadow ^= (1 << 1);     // натиск → перемкнути другий світлодіод
            pcf_write(shadow);
        }
    }
}
