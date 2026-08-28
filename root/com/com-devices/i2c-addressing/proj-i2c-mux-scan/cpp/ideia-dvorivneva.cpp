#include <Wire.h>

#define MUX_ADDR 0x70          // власна 7-бітна адреса мультиплексора

// Увімкнути рівно одну гілку (0…7), решту вимкнути.
void mux_select(uint8_t channel) {
  if (channel > 7) return;
  Wire.beginTransmission(MUX_ADDR);
  Wire.write(1 << channel);    // один біт = одна гілка
  Wire.endTransmission();
}

void read_sensor_on(uint8_t channel) {
  mux_select(channel);         // крок 1: вибрати гілку
  // крок 2: далі — звичайна робота з давачем 0x68 на ЦІЙ гілці
  Wire.beginTransmission(0x68);
  Wire.write(0x3B);            // напр., адреса регістра даних
  Wire.endTransmission(false); // повторний старт без відпускання шини
  Wire.requestFrom(0x68, 6);   // забрати 6 байт
  // ... читання Wire.read() ...
}
