// РАЗОВО на комп'ютері: надрукувати рядки таблиці для вставки у скетч.
// Термістор УНИЗУ; крок 5 °C від −10 до +45.
#include <stdio.h>
#include <math.h>
int main() {
  const double R_FIXED = 10000, R25 = 10000, BETA = 3950, T25 = 298.15;
  const double ADC_MAX = 1023;
  for (int tC = -10; tC <= 45; tC += 5) {
    double T   = tC + 273.15;
    // T → опір термістора (обернена B-формула)
    double R   = R25 * exp(BETA * (1.0/T - 1.0/T25));
    // опір → відлік (термістор унизу): ratio = R/(R+R_fixed)
    double adc = ADC_MAX * (R / (R + R_FIXED));
    printf("  {%4d, %3d},\n", (int)(adc + 0.5), tC * 10);  // t×10 → десяті
  }
  return 0;
}
