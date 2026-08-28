#include <stdint.h>

// bias — оцінка постійного зсуву у форматі 16.16 (Q16):
//   ціле значення bias, поділене на 65536, дає рівень у одиницях відліку.
static int32_t bias = 0;

void dc_block(int16_t *samples, int n) {
    for (int i = 0; i < n; i++) {
        int32_t x = (int32_t)samples[i] << 16;   // відлік → Q16 (кома зсунута на 16)
        bias += (x - bias) >> 10;                 // крок текучого інтегратора, α = 1/1024
        int32_t y = x - bias;                     // вхід мінус НЧ-копія = ФВЧ
        samples[i] = (int16_t)(y >> 16);          // Q16 → int16 (арифметичний зсув!)
    }
}
