// Керування мотор-редуктором 6 В через H-міст із неблокуючим плавним пуском
#include <Arduino.h>

const uint8_t PIN_IN1 = 8;    // Напрямок: пін 1
const uint8_t PIN_IN2 = 7;    // Напрямок: пін 2
const uint8_t PIN_PWM = 9;    // ШІМ-керування швидкістю (Timer1, 8-бітний режим)

enum MotorMode {
    MODE_STOP,      // Вільний вибіг (Hi-Z)
    MODE_FORWARD,   // Рух уперед
    MODE_REVERSE,   // Реверс
    MODE_BRAKE      // Активне електродинамічне гальмування
};

int16_t current_duty = 0;       // Поточна шпаруватість (0..255)
int16_t target_duty = 0;        // Задана шпаруватість (0..255)
MotorMode current_mode = MODE_STOP;

uint32_t last_ramp_tick = 0;
const uint16_t RAMP_STEP_MS = 5; // Крок наростання кожні 5 мс (розгін за 255 мс)

void motor_set_mode(MotorMode mode) {
    current_mode = mode;
    switch (mode) {
        case MODE_FORWARD:
            digitalWrite(PIN_IN1, HIGH);
            digitalWrite(PIN_IN2, LOW);
            break;
        case MODE_REVERSE:
            digitalWrite(PIN_IN1, LOW);
            digitalWrite(PIN_IN2, HIGH);
            break;
        case MODE_BRAKE:
            // Одночасне замикання нижніх ключів для гасіння проти-ЕРС
            digitalWrite(PIN_IN1, HIGH);
            digitalWrite(PIN_IN2, HIGH);
            target_duty = 255;
            current_duty = 255;
            analogWrite(PIN_PWM, 255);
            return;
        case MODE_STOP:
        default:
            digitalWrite(PIN_IN1, LOW);
            digitalWrite(PIN_IN2, LOW);
            target_duty = 0;
            current_duty = 0;
            analogWrite(PIN_PWM, 0);
            return;
    }
}

void motor_process_soft_start() {
    uint32_t now = millis();
    if (now - last_ramp_tick >= RAMP_STEP_MS) {
        last_ramp_tick = now;

        if (current_duty < target_duty) {
            current_duty += 5; // Плавне наростання шпаруватості
            if (current_duty > target_duty) {
                current_duty = target_duty;
            }
            analogWrite(PIN_PWM, current_duty);
        } else if (current_duty > target_duty) {
            current_duty -= 10; // Контрольоване скидання шпаруватості
            if (current_duty < target_duty) {
                current_duty = target_duty;
            }
            analogWrite(PIN_PWM, current_duty);
        }
    }
}

void setup() {
    pinMode(PIN_IN1, OUTPUT);
    pinMode(PIN_IN2, OUTPUT);
    pinMode(PIN_PWM, OUTPUT);

    motor_set_mode(MODE_STOP);

    // Завдання руху вперед із цільовою шпаруватістю 80% (204 / 255)
    motor_set_mode(MODE_FORWARD);
    target_duty = 204;
}

void loop() {
    // Неблокуюче оновлення генератора розгону в кожному проході циклу
    motor_process_soft_start();
}
