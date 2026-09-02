#include "sticks.h"

// Заводське калібрування. На серійному пульті його читають із флеш-розділу
// після процедури обертання стіків; тут це константи — тема про інше.
static const axis_cfg_t s_cfg[HAL_ADC_AXES] = {
    {320, 2048, 3780, 25, 30, 64, false},   // крен
    {330, 2050, 3770, 25, 30, 64, false},   // тангаж
    {310, 2048, 3790,  0,  0, 96, true },   // газ: без мертвої зони й експоненти
    {325, 2045, 3775, 25, 20, 64, false},   // рискання
};

static int32_t s_filt[HAL_ADC_AXES] = {2048, 2050, 310, 2045};
static uint8_t s_bad[HAL_ADC_AXES];

// Обрив або коротке замикання давача Холла: жива вісь ніколи не впирається
// в самі краї шкали АЦП.
#define RAW_FLOOR   8
#define RAW_CEIL    4087
#define BAD_LIMIT   50

// Кубічна експонента цілими: out = x·(1−k) + k·x³, де x у діапазоні ±1024.
// Проміжок x²>>10 не перевищує 1024, тож 32 біти не переповнюються.
static int32_t apply_expo(int32_t x, uint8_t k_pct)
{
    if (k_pct == 0) {
        return x;
    }
    int32_t cube = (((x * x) >> 10) * x) >> 10;
    return (x * (int32_t)(100 - k_pct) + cube * (int32_t)k_pct) / 100;
}

uint16_t sticks_process(uint8_t ch, uint16_t raw)
{
    if (ch >= HAL_ADC_AXES) {
        return AXIS_CENTER;
    }
    const axis_cfg_t *c = &s_cfg[ch];

    if (raw <= RAW_FLOOR || raw >= RAW_CEIL) {
        if (s_bad[ch] < 255) {
            s_bad[ch]++;
        }
    } else if (s_bad[ch] > 0) {
        s_bad[ch]--;
    }

    // IIR першого порядку: свіжий відлік із вагою alpha/256.
    s_filt[ch] += ((int32_t)raw - s_filt[ch]) * (int32_t)c->alpha >> 8;

    int32_t val = s_filt[ch];
    if (val < (int32_t)c->min) {
        val = c->min;
    }
    if (val > (int32_t)c->max) {
        val = c->max;
    }

    if (c->unipolar) {
        int32_t span = (int32_t)c->max - (int32_t)c->min;
        return span > 0 ? (uint16_t)((val - c->min) * AXIS_MAX / span) : 0;
    }

    int32_t diff = val - (int32_t)c->center;
    if (diff > -(int32_t)c->deadband && diff < (int32_t)c->deadband) {
        return AXIS_CENTER;
    }
    // Зсуваємо на ширину мертвої зони, щоб на її краю не було стрибка каналу.
    diff += (diff > 0) ? -(int32_t)c->deadband : (int32_t)c->deadband;

    int32_t span = (diff > 0) ? (int32_t)c->max - (int32_t)c->center - (int32_t)c->deadband
                              : (int32_t)c->center - (int32_t)c->min - (int32_t)c->deadband;
    if (span <= 0) {
        return AXIS_CENTER;
    }

    int32_t norm = diff * AXIS_CENTER / span;
    if (norm > AXIS_CENTER) {
        norm = AXIS_CENTER;
    }
    if (norm < -AXIS_CENTER) {
        norm = -AXIS_CENTER;
    }

    int32_t out = AXIS_CENTER + apply_expo(norm, c->expo_pct);
    if (out < 0) {
        out = 0;
    }
    if (out > AXIS_MAX) {
        out = AXIS_MAX;
    }
    return (uint16_t)out;
}

uint8_t sticks_dead_axes(void)
{
    uint8_t mask = 0;
    for (uint8_t i = 0; i < HAL_ADC_AXES; i++) {
        if (s_bad[i] > BAD_LIMIT) {
            mask |= (uint8_t)(1u << i);
        }
    }
    return mask;
}

uint8_t sticks_safety_check(const uint16_t *scaled, uint16_t switches)
{
    uint8_t faults = 0;
    if (scaled[AXIS_THROTTLE] > (AXIS_MAX * 5) / 100) {   // газ відхилений понад 5%
        faults |= SAFETY_THROTTLE_UP;
    }
    if (switches & SW_ARM) {
        faults |= SAFETY_ARM_ON;
    }
    if (sticks_dead_axes()) {
        faults |= SAFETY_AXIS_DEAD;
    }
    return faults;
}

uint8_t sticks_aux_update(uint16_t switches)
{
    static uint8_t value = 128;
    static uint8_t divider;

    // Кнопки опитуються на 1 кГц, а підкручувати канал корисного навантаження
    // треба на 100 Гц — інакше палець не встигає зупинити його де треба.
    if (++divider >= 10) {
        divider = 0;
        if ((switches & SW_PAY_UP) && value < 255) {
            value++;
        }
        if ((switches & SW_PAY_DN) && value > 0) {
            value--;
        }
    }
    return value;
}
