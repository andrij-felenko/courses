#include <math.h>

// паспорт/вимір обмотки та умови
const float R_OHM   = 0.030f;   // опір фази, Ом
const float MASS_KG = 0.040f;   // маса міді обмотки, кг
const float C_CU    = 385.0f;   // питома теплоємність міді, Дж/(кг·°C)
const float RTH     = 3.0f;     // тепловий опір у повітря БЕЗ обдуву, °C/Вт
const float T_AMB   = 25.0f;    // довкілля, °C
const float T_LIMIT = 155.0f;   // клас F, °C

// скільки секунд від ХОЛОДНОГО старту струм I тримається до межі класу
// (повертає -1, якщо усталена стеля нижча за межу — тоді пік безпечний назавжди)
float seconds_to_limit(float I)
{
    float P      = I * I * R_OHM;          // джоулева потужність, Вт
    float dT_inf = P * RTH;                // усталений перегрів, °C
    float dT_lim = T_LIMIT - T_AMB;        // дозволений перегрів, °C
    if (dT_inf <= dT_lim)
        return -1.0f;                      // стеля під класом — не згорить ніколи

    float C_th = MASS_KG * C_CU;           // теплоємність, Дж/°C  (= 15.4)
    float tau  = RTH * C_th;               // теплова стала часу, с (= 46.2)
    // t = -tau * ln(1 - dT_lim/dT_inf)
    return -tau * logf(1.0f - dT_lim / dT_inf);
}

// I_HOVER = 30 A -> стеля P·Rθ = 900*0.03*3 = 81 °C < 130 -> safe (-1)
// I_BURST = 80 A -> ≈ 11.8 c
