#include <Arduino.h>
#include <math.h>

const float V_IN = 5.0;         // Напруга живлення дільника, В
const float R_LOAD = 10000.0;   // Опір навантажувального резистора RL, Ом
const float PARAM_M = -0.77;    // Кутовий коефіцієнт m у log-log координатах
const float PARAM_B = 1.33;     // Коефіцієнт зсуву b у log-log координатах

// Обчислення опору сенсора Rs за виміряною напругою Vout
float calculateRs(float vOut) {
  if (vOut <= 0.0 || vOut >= V_IN) return -1.0;
  return R_LOAD * (V_IN - vOut) / vOut;
}

// Розрахунок концентрації чадного газу у ppm
float calculatePpm(float rs, float r0) {
  if (rs <= 0.0 || r0 <= 0.0) return 0.0;
  float ratio = rs / r0;
  float logPpm = (log10(ratio) - PARAM_B) / PARAM_M;
  return pow(10.0, logPpm);
}
