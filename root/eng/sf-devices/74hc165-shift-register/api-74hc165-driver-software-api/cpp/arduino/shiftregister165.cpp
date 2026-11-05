#include <Arduino.h>

// Клас драйвера 74HC165
class ShiftRegister165 {
private:
    uint8_t pin_sh_ld;
    uint8_t pin_clk;
    uint8_t pin_data;

public:
    ShiftRegister165(uint8_t sh_ld, uint8_t clk, uint8_t data) 
        : pin_sh_ld(sh_ld), pin_clk(clk), pin_data(data) {}

    void init() const {
        pinMode(pin_sh_ld, OUTPUT);
        pinMode(pin_clk, OUTPUT);
        pinMode(pin_data, INPUT);

        digitalWrite(pin_sh_ld, HIGH);
        digitalWrite(pin_clk, LOW);
    }

    uint8_t read() const {
        uint8_t incoming_data = 0;

        // Вимикаємо переривання для гарантії таймінгів
        noInterrupts();

        // Імпульс захоплення даних
        digitalWrite(pin_sh_ld, LOW);
        delayMicroseconds(1); // Гарантована затримка для старих чипів
        digitalWrite(pin_sh_ld, HIGH);

        // Зчитування даних
        for (int i = 7; i >= 0; i--) {
            // Зчитуємо біт
            if (digitalRead(pin_data) == HIGH) {
                incoming_data |= (1 << i);
            }

            // Тактовий імпульс
            digitalWrite(pin_clk, HIGH);
            delayMicroseconds(1);
            digitalWrite(pin_clk, LOW);
        }

        // Вмикаємо переривання
        interrupts();

        return incoming_data;
    }
};
