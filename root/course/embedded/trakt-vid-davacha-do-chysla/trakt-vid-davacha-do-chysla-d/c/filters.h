#ifndef FILTERS_H
#define FILTERS_H

/*
 * Цифрова частина тракту (розділ 5) — цілочисельна від початку до кінця:
 * на Cortex-M0 і AVR апаратної плаваючої коми немає, а рахувати це доводиться
 * у переривання АЦП.
 */

#include <stdbool.h>
#include <stdint.h>

#include "afe_model.h" /* AFE_STEP_HZ — вхідна частота потоку відліків */

/* Вихідна частота потоку відліків після проріджування. */
#define CHAIN_RATE_HZ 1000
#define MAINS_HZ      50

/* Вікно рухомого середнього рівно на один період мережі: нуль АЧХ сідає точно
   на 50 Гц і на всі його гармоніки (розділ 5). */
#define MA_WINDOW (CHAIN_RATE_HZ / MAINS_HZ)

typedef struct {
    int32_t buffer[MA_WINDOW];
    int32_t sum;
    uint8_t index;
    uint8_t count;
} ma_t;

void    ma_init(ma_t *f);
int32_t ma_update(ma_t *f, int32_t x);
/* Поки вікно не заповнилось, на виході середнє неповного вікна — заваду 50 Гц
   воно ще не вирізає, і калібруватися по ньому не можна. */
bool    ma_ready(const ma_t *f);

/* Експоненційне згладжування y[n] = y[n-1] + (x[n] - y[n-1]) >> K.
   Накопичувач тримається у форматі Q(K), інакше молодші розряди губляться
   на кожному кроці й фільтр «застрягає» на цілому числі. */
typedef struct {
    int32_t accumulator;
    uint8_t shift_k;
    bool    initialized;
} ema_t;

/* shift_k від 1 до 15: нуль вимкнув би фільтр, більше — переповнення накопичувача. */
bool    ema_init(ema_t *f, uint8_t shift_k);
int32_t ema_update(ema_t *f, int32_t x);

/* Проріджувач «накопичити й скинути»: складає DECIMATION_FACTOR відліків
   зі 100 кГц і віддає один на 1 кГц. Це і є передискретизація з розділу 3.
   Результат віддається у форматі Q4 (1/16 кванта), щоб виграні усередненням
   розряди не пропали при поверненні до цілих кодів. */
#define DECIMATION_FACTOR (AFE_STEP_HZ / CHAIN_RATE_HZ)
#define DECIMATION_Q      16

typedef struct {
    int32_t sum;
    uint16_t count;
} dec_t;

void dec_init(dec_t *d);
/* Повертає true й кладе відлік у *out, коли пачка з DECIMATION_FACTOR зібрана. */
bool dec_push(dec_t *d, int32_t x, int32_t *out);

/* Ділення з округленням до найближчого — цілочисельне ділення в C відкидає
   дробову частину в бік нуля й дає систематичний зсув на пів кванта. */
int32_t div_round(int64_t numerator, int64_t denominator);

#endif /* FILTERS_H */
