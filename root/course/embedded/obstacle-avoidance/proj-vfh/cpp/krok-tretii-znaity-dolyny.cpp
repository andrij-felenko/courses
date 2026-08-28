// Бінаризація гістограми з гістерезисом на двох порогах.
// occ[] тримається МІЖ тактами (static або поле стану) — у цьому й суть.
void binarize_hysteresis(const float hist[N_SECTORS], uint8_t occ[N_SECTORS])
{
    for (int k = 0; k < N_SECTORS; k++) {
        if      (hist[k] > THR_HIGH) occ[k] = 1;   // впевнено зайнято
        else if (hist[k] < THR_LOW)  occ[k] = 0;   // впевнено вільно
        // між порогами — НЕ чіпаємо occ[k]: лишається минулий стан
    }
}
