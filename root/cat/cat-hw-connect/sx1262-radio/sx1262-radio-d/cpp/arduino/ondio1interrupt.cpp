#include <Arduino.h>
#include <SPI.h>

const int PIN_CS   = 5;
const int PIN_BUSY = 26;
const int PIN_DIO1 = 25;

volatile bool dio1_triggered = false;

void IRAM_ATTR onDio1Interrupt() {
    dio1_triggered = true;
}

void sx1262_wait_busy() {
    while (digitalRead(PIN_BUSY) == HIGH) {
        delayMicroseconds(5);
    }
}

void sx1262_write_command(uint8_t opcode, const uint8_t* params, size_t length) {
    sx1262_wait_busy();

    digitalWrite(PIN_CS, LOW);
    SPI.transfer(opcode);
    for (size_t i = 0; i < length; i++) {
        SPI.transfer(params[i]);
    }
    digitalWrite(PIN_CS, HIGH);

    sx1262_wait_busy();
}

void setup() {
    Serial.begin(115200);
    pinMode(PIN_CS, OUTPUT);
    pinMode(PIN_BUSY, INPUT);
    pinMode(PIN_DIO1, INPUT);

    digitalWrite(PIN_CS, HIGH);
    SPI.begin();

    attachInterrupt(digitalPinToInterrupt(PIN_DIO1), onDio1Interrupt, RISING);
}

void loop() {
    if (dio1_triggered) {
        dio1_triggered = false;
        Serial.println(F("Переривання від SX1262 успішно перехоплено"));
        
        // Очищення статусу переривань у чипі (ClearIrqStatus, Opcode 0x02)
        uint8_t clear_mask[2] = {0x07, 0xFF};
        sx1262_write_command(0x02, clear_mask, 2);
    }
}
