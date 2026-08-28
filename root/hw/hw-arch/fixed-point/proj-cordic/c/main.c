// theta у Q-форматі, |theta| ≤ ~99°;  повертає sin/cos через вказівники
void cordic_sincos(int32_t theta, int32_t *sin_out, int32_t *cos_out) {
    int32_t x = ONE_OVER_K;              // = 1/K у Q-форматі (гасить посилення наперед)
    int32_t y = 0;
    int32_t z = theta;                   // лишок кута, женемо до нуля
    for (int i = 0; i < N; i++) {
        int32_t x_new, y_new;
        if (z >= 0) {                    // знак z = напрям повороту
            x_new = x - (y >> i);        // псевдо-обертання вперед
            y_new = y + (x >> i);        //   (зсуви замість множень!)
            z     = z - ATAN[i];         // списали kᵢ з лишку
        } else {
            x_new = x + (y >> i);        // псевдо-обертання назад
            y_new = y - (x >> i);
            z     = z + ATAN[i];
        }
        x = x_new;                       // ОНОВЛЮВАТИ РАЗОМ: y залежить від старого x
        y = y_new;
    }
    *sin_out = y;                        // y ≈ sin theta
    *cos_out = x;                        // x ≈ cos theta
}
