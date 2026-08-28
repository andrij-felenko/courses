// atmega-fan-pwm.ino — 25-кГц ШІМ через Timer1 (Fast PWM, TOP=ICR1) на пін 9
// Пін 9 = OC1A на ATmega328 (Uno/Nano). Пін 10 (OC1B) можна вести паралельно.
#include <Arduino.h>

const uint16_t PWM_TOP = 639;    // 16 МГц / 25 кГц − 1 → період рівно 25 кГц

void fanPwmBegin() {
  pinMode(9, OUTPUT);
  // Fast PWM, TOP=ICR1 (режим 14): WGM13:12:11:10 = 1110
  // Не-інверсний вихід на OC1A: COM1A1=1
  TCCR1A = _BV(COM1A1) | _BV(WGM11);
  TCCR1B = _BV(WGM13)  | _BV(WGM12) | _BV(CS10);   // CS10 → prescaler = 1
  ICR1  = PWM_TOP;                                  // задає частоту (верх лічильника)
  OCR1A = 0;                                        // старт: вентилятор стоїть
}

void fanSetSpeed(uint8_t percent) {                 // 0…100 %
  if (percent > 100) percent = 100;
  OCR1A = (uint32_t)percent * PWM_TOP / 100;        // заповнення = частка від періоду
}

void setup() { fanPwmBegin(); fanSetSpeed(60); }
void loop()  {}
