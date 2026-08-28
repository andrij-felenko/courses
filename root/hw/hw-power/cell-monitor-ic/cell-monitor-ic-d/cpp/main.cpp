// хост прочитав напруги всіх комірок стосу з монітора;
// вмикаємо баланс-ключ на кожній, що втекла вперед від найнижчої
#define N_CELLS        12u
#define BAL_THRESH_MV  15u      // поріг розбалансу, мВ

// повертає маску: біт i == 1 → зливати комірку i
uint16_t balance_decide(const uint16_t v_mV[N_CELLS]) {
    uint16_t v_min = v_mV[0];
    for (uint8_t i = 1; i < N_CELLS; i++)      // знайти найнижчу комірку
        if (v_mV[i] < v_min) v_min = v_mV[i];

    uint16_t mask = 0;
    for (uint8_t i = 0; i < N_CELLS; i++)
        if (v_mV[i] - v_min > BAL_THRESH_MV)    // втекла більш ніж на поріг
            mask |= (uint16_t)(1u << i);

    return mask;                                // цю маску хост запише в чип
}
