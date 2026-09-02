#include "rawframe.h"

uint16_t rf_u16_lsb_first(const uint8_t *p) {
    /* Компілятор із -O2 бачить цей патерн і кладе LDRH (або LDRB+LDRB
       на ядрі без непарного доступу) — жодних накладних витрат. */
    return (uint16_t)((uint16_t)p[0] | ((uint16_t)p[1] << 8));
}

uint16_t rf_u16_msb_first(const uint8_t *p) {
    /* Той самий патерн, який GCC згортає в LDRH + REV16. */
    return (uint16_t)(((uint16_t)p[0] << 8) | (uint16_t)p[1]);
}

uint32_t rf_u20_msb_first(const uint8_t *p) {
    const uint32_t w = ((uint32_t)p[0] << 16) | ((uint32_t)p[1] << 8) | (uint32_t)p[2];
    /* Молодші чотири розряди третього байта — службові, значущих 20. */
    return w >> 4;
}

int16_t rf_sign_extend_shift(uint16_t v, unsigned bits) {
    if (bits == 0u || bits > 16u) {
        return 0; /* безглузда ширина поля */
    }
    {
        const unsigned s = 16u - bits;
        /* Зсуваємо поле вліво беззнаково (щоб не переповнити знаковий тип),
           а вже арифметичний зсув праворуч розмножує знаковий біт.
           Перетворення uint16→int16 понад 32767 до C23 реалізаційно
           визначене; на всіх embedded-ABI це доповняльний код. */
        const int16_t up = (int16_t)(uint16_t)(v << s);
        return (int16_t)(up >> s);
    }
}

int16_t rf_sign_extend_mask(uint16_t v, unsigned bits) {
    if (bits == 0u || bits > 16u) {
        return 0;
    }
    if (bits == 16u) {
        return (int16_t)v;
    }
    {
        /* Повністю переносний варіант: усе рахується беззнаково. */
        const uint16_t mask = (uint16_t)(0xFFFFu << bits); /* 0xF000 для 12 бітів */
        const uint16_t sign = (uint16_t)(1u << (bits - 1u)); /* 0x0800 для 12 бітів */
        uint16_t field = (uint16_t)(v & (uint16_t)~mask);
        if ((field & sign) != 0u) {
            field |= mask;
        }
        return (int16_t)field;
    }
}

int16_t rf_sign_extend_hw12(uint16_t v) {
#if defined(__ARM_ARCH) && (__ARM_ARCH >= 7)
    /* SBFX Rd, Rn, #lsb, #width — витяг бітового поля зі знаковим
       розширенням за один такт. Ширина мусить бути безпосереднім
       операндом, тому функція фіксована на 12 бітах. */
    int32_t r;
    __asm__("sbfx %0, %1, #0, #12" : "=r"(r) : "r"((uint32_t)v));
    return (int16_t)r;
#else
    return rf_sign_extend_mask(v, 12u);
#endif
}

void rf_parse_left_aligned(const uint8_t buf[6], unsigned bits, int16_t out[3]) {
    /* Значущі розряди стоять у старших бітах слова, молодші зайняті нулями
       або прапорцями готовності. Знак уже на своєму місці — лишається
       поділити на 2^(16-bits) арифметичним зсувом. */
    const unsigned shift = (bits >= 16u) ? 0u : (16u - bits);
    unsigned i;
    for (i = 0u; i < 3u; ++i) {
        const int16_t word = (int16_t)rf_u16_lsb_first(&buf[2u * i]);
        out[i] = (int16_t)(word >> shift);
    }
}

void rf_parse_right_aligned(const uint8_t buf[6], unsigned bits, int16_t out[3]) {
    /* Значущі розряди в молодших бітах, старші нульові — без розширення
       від'ємне число прочиталось би як велике додатне. */
    unsigned i;
    for (i = 0u; i < 3u; ++i) {
        out[i] = rf_sign_extend_mask(rf_u16_lsb_first(&buf[2u * i]), bits);
    }
}

void rf_parse_be16(const uint8_t buf[6], int16_t out[3]) {
    unsigned i;
    for (i = 0u; i < 3u; ++i) {
        out[i] = (int16_t)rf_u16_msb_first(&buf[2u * i]);
    }
}
