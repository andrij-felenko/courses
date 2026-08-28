#define DAC_BITS      16
#define DAC_MAX       ((1 << DAC_BITS) - 1)   /* 65535 для 16-біт ЦАП */
#define DAC_CENTER    (1 << (DAC_BITS - 1))   /* середина шкали */

/* Крутість: скільки кодів ЦАП на один ppb (Q16, з EEPROM).
 * Знак: якщо ріст коду ЦАП ПІДВИЩУЄ частоту, slope > 0. */
static int32_t g_codes_per_ppb_q16;

typedef enum { DAC_OK = 0, DAC_RAILED_LOW, DAC_RAILED_HIGH } dac_status_t;

/* Перетворити поправку Δf/f (Q16 ppb) у код ЦАП відносно центру шкали.
 * Компенсація ЗНАКУ: щоб ПОГАСИТИ дрейф +X ppb, треба зсунути частоту на −X,
 * тому беремо мінус поліному. Повертає статус railing. */
static dac_status_t dcxo_ppb_to_dac(int32_t dff_q16_ppb, uint16_t *out_code)
{
    /* потрібний зсув = −дрейф; код = центр + зсув·крутість */
    int64_t codes_q32 = -(int64_t)dff_q16_ppb * g_codes_per_ppb_q16; /* Q16·Q16 = Q32 */
    int32_t codes = (int32_t)(codes_q32 >> 32);                      /* Q32 → ціле число кодів */
    int32_t code = (int32_t)DAC_CENTER + codes;

    if (code < 0)         { *out_code = 0;        return DAC_RAILED_LOW;  }
    if (code > DAC_MAX)   { *out_code = DAC_MAX;  return DAC_RAILED_HIGH; }
    *out_code = (uint16_t)code;
    return DAC_OK;
}
