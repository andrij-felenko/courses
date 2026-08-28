#include "Button.h"

Button btn(2);                 // сигнал KY-004 на D2; вікно 15 мс, довгий 800 мс — за замовчуванням
const uint8_t LED = 13;
bool ledOn = false;
long presses = 0;

void setup() {
  Serial.begin(9600);
  pinMode(LED, OUTPUT);
  btn.begin();                 // тут визначиться полярність — не тримай кнопку!
}

void loop() {
  btn.update();                // єдиний обов'язок: смикати часто й неблокуюче

  if (btn.pressed()) {         // мить натиску — рівно раз на тик
    ledOn = !ledOn;
    digitalWrite(LED, ledOn);
    presses++;
  }
  if (btn.longPress()) {       // тримали довше 800 мс
    ledOn = false;
    digitalWrite(LED, LOW);
    Serial.print("натисків: ");
    Serial.println(presses);
  }

  // ... тут може бути будь-що інше: loop не блокується кнопкою ...
}
