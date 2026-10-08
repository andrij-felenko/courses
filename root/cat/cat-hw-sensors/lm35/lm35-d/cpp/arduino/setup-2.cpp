#include <Arduino.h>

const int ADC_PIN = A0;
const float V_REF = 1.1; // Внутрішня опорна напруга 1.1 В
const float SENSITIVITY = 0.010; // 10 мВ/°C
const float EMA_ALPHA = 0.15; // Коефіцієнт згладжування

float filtered_temp = 0.0;
bool is_first_read = true;

void setup() {
  Serial.begin(9600);
#if defined(__AVR__)
  // Перемикання АЦП на внутрішнє джерело опорної напруги 1.1 В
  analogReference(INTERNAL);
#endif
}

void loop() {
  int raw_adc = analogRead(ADC_PIN);
  
  // Перетворення коду 10-бітного АЦП у напругу
  float voltage = ((float)raw_adc / 1023.0) * V_REF;
  float current_temp = voltage / SENSITIVITY;

  if (is_first_read) {
    filtered_temp = current_temp;
    is_first_read = false;
  } else {
    filtered_temp = (EMA_ALPHA * current_temp) + ((1.0 - EMA_ALPHA) * filtered_temp);
  }

  delay(100);
}
