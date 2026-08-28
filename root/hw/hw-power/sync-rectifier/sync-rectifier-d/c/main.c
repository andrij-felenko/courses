// Прошивка живиться сама й телеметрує ККД своїх шин.
// Той самий розрахунок, що вирішує, який нижній елемент ставити.
float Vf       = 0.40f;   // падіння Шотткі, В
float Rds      = 0.005f;  // Rds(on) нижнього MOSFET, Ом
float I        = 10.0f;   // струм навантаження, А
float oneMinusD = 0.9f;   // частка циклу на нижньому елементі (D = Vout/Vin = 0.1)
float Pout     = 1.2f * I; // корисна потужність = 12 Вт

float P_diode = Vf * I * oneMinusD;          // 0.40 * 10 * 0.9 = 3.6 Вт
float P_mos   = I * I * Rds * oneMinusD;      // 100 * 0.005 * 0.9 = 0.45 Вт

float eff_async = Pout / (Pout + P_diode);    // 12 / 15.6  ≈ 0.77
float eff_sync  = Pout / (Pout + P_mos);      // 12 / 12.45 ≈ 0.96
