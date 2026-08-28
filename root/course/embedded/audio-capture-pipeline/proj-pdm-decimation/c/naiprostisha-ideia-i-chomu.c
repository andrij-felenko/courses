// Наївний boxcar-дециматор: середнє кожних D бітів → один відлік.
// Повертає, скільки відліків PCM поклав у out.
static int pdm_decimate_boxcar(const uint8_t *pdm, int nbytes,
                               int D, int16_t *out) {
    int8_t bits[8];
    int acc = 0;       // сума біполярних бітів у поточному вікні
    int cnt = 0;       // скільки бітів уже назбирали (0..D)
    int nout = 0;

    for (int i = 0; i < nbytes; i++) {
        pdm_unpack_byte(pdm[i], bits);
        for (int k = 0; k < 8; k++) {
            acc += bits[k];        // додали ще один біт
            if (++cnt == D) {      // назбирали повне вікно з D бітів
                // acc у діапазоні [−D, +D]; масштабуємо у int16
                out[nout++] = (int16_t)(acc * (32767 / D));
                acc = 0;           // почали нове вікно з нуля
                cnt = 0;
            }
        }
    }
    return nout;
}
