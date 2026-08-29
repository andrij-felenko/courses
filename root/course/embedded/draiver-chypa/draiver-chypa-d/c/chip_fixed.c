#include "chip_fixed.h"

/* Скільки мікрометрів на секунду в квадраті в одному мікро-g:
 * 1 мкg = 9.80665e-6 м/с² = 9.80665 мкм/с². Тримаємо як ціле 980665/100000. */
#define UG_TO_UM_S2_NUM 980665LL
#define UG_TO_UM_S2_DEN 100000LL

int32_t chip_div_round(int64_t numerator, int64_t denominator)
{
    if (denominator == 0) {
        return 0;
    }
    int64_t half = denominator / 2;
    int64_t result = (numerator >= 0) ? (numerator + half) / denominator
                                      : (numerator - half) / denominator;
    return (int32_t)result;
}

int32_t chip_raw_to_mg(int16_t raw_code, chip_range_t range)
{
    /* raw · (мкg/LSB) дає мікрогравітації; 1000 мкg = 1 мг. */
    int64_t product = (int64_t)raw_code * (int64_t)chip_sensitivity_ug(range);
    return chip_div_round(product, 1000);
}

int32_t chip_raw_to_mm_s2(int16_t raw_code, chip_range_t range)
{
    /* raw · мкg/LSB → мкg; мкg · 9.80665 → мкм/с²; 1000 мкм/с² = 1 мм/с². */
    int64_t micro_g = (int64_t)raw_code * (int64_t)chip_sensitivity_ug(range);
    int64_t micro_m_s2_num = micro_g * UG_TO_UM_S2_NUM;
    return chip_div_round(micro_m_s2_num, UG_TO_UM_S2_DEN * 1000LL);
}

uint16_t chip_le16(const uint8_t *pair)
{
    return (uint16_t)((uint16_t)pair[0] | (uint16_t)((uint16_t)pair[1] << 8));
}

int16_t chip_sign_extend(uint16_t word, chip_resolution_t resolution)
{
    unsigned shift = (unsigned)resolution;      /* 0 або 4                    */
    unsigned bits = 16u - shift;                /* корисна розрядність слова  */

    uint32_t magnitude_mask = (uint32_t)((1uL << bits) - 1uL);
    uint32_t sign_bit = (uint32_t)(1uL << (bits - 1u));

    uint32_t value = ((uint32_t)word >> shift) & magnitude_mask;
    /* Класичний трюк переносного розширення знака: XOR зі знаковим бітом і
     * віднімання його ж перетворює беззнакове поле на від'ємне число. */
    return (int16_t)((int32_t)(value ^ sign_bit) - (int32_t)sign_bit);
}
