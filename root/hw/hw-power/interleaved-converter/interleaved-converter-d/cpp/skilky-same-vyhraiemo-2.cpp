// Балансування: тягнемо кожну фазу до середнього струму по всіх фазах.
void balance_phases(int16_t i_phase[N_PHASES], uint16_t duty[N_PHASES]) {
    int32_t sum = 0;
    for (uint8_t k = 0; k < N_PHASES; k++) sum += i_phase[k];
    int16_t i_avg = (int16_t)(sum / N_PHASES);   // цільовий струм на фазу

    for (uint8_t k = 0; k < N_PHASES; k++) {
        int16_t err = i_phase[k] - i_avg;         // ця фаза тягне більше/менше?
        // тягне більше середнього → трохи прикрити її заповнення, і навпаки
        duty[k] -= (err >> 4);                     // м'який коефіцієнт (÷16)
    }
}
