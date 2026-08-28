// середній струм = (час_активний·I_активний + час_сну·I_сну) / період
const float period_s   = 60.0f;      // прокидання раз на хвилину
const float active_s    = 0.020f;     // 20 мс вимірювання
const float i_active_uA = 5000.0f;    // 5 мА у спалаху виміру
const float i_sleep_uA  = 3.0f;       // 3 мкА у сні

float duty      = active_s / period_s;                 // = 0.000333
float i_avg_uA  = duty * i_active_uA                    // активна частка
                + (1.0f - duty) * i_sleep_uA;           // + майже весь час сон
// i_avg = 0.000333·5000 + 0.999667·3 = 1.667 + 3.0 ≈ 4.67 мкА

float life_h    = 220000.0f / i_avg_uA;                 // 220 мА·год = 220000 мкА·год
float life_yr   = life_h / 24.0f / 365.0f;
// life = 220000 / 4.67 ≈ 47100 год ≈ 5.4 року
