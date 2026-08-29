#include "pipeline.h"

#include <stddef.h>

/* ---- Дрібні цілочисельні помічники ------------------------------------ */

static int32_t clamp_i32(int32_t v, int32_t lo, int32_t hi)
{
    if (v < lo) return lo;
    if (v > hi) return hi;
    return v;
}

/* Множення на коефіцієнт Q8.8 з поверненням у Q0.
   Зсув вправо для від'ємних чисел на GCC і Clang арифметичний, тобто
   округлює вниз: результат занижений щонайбільше на одну одиницю виходу.
   Це прийнятно, і саме тому тут зсув, а не ділення: ділення на M0+ —
   бібліотечна підпрограма на кілька десятків тактів. */
static int32_t mul_q8(int32_t coeff_q8, int32_t x)
{
    return (coeff_q8 * x) >> 8;
}

/* ---- Фільтр ------------------------------------------------------------ */

bool ema_init(ema_filter_t *f, uint8_t shift_k)
{
    if (f == NULL || shift_k < 1U || shift_k > 12U) {
        return false;
    }
    f->value = 0;
    f->shift_k = shift_k;
    f->primed = false;
    return true;
}

int32_t ema_update(ema_filter_t *f, int32_t sample)
{
    /* Перший відлік беремо як є. Інакше фільтр стартував би з нуля і повз
       до робочої точки кілька сотень періодів, а ПІД усе це вважав би
       справжньою помилкою і гнав би нагрівач на повну. */
    if (!f->primed) {
        f->value = sample;
        f->primed = true;
        return f->value;
    }
    f->value += (sample - f->value) >> f->shift_k;
    return f->value;
}

/* ---- Регулятор --------------------------------------------------------- */

bool pid_init(pid_t *p, const pid_cfg_t *cfg)
{
    if (p == NULL || cfg == NULL) {
        return false;
    }
    /* Коефіцієнти мусять лишатися в межах Q8.8, інакше добуток
       kp * error виходить за int32 і регулятор стрибне у від'ємні значення. */
    if (cfg->kp_q8 < 0 || cfg->kp_q8 > Q8_LIMIT ||
        cfg->ki_q8 < 0 || cfg->ki_q8 > Q8_LIMIT ||
        cfg->kd_q8 < 0 || cfg->kd_q8 > Q8_LIMIT) {
        return false;
    }
    if (cfg->out_min >= cfg->out_max || cfg->out_max > PWM_MAX_DUTY) {
        return false;
    }

    p->cfg = *cfg;

    /* Anti-Windup: замість того щоб щоразу відкручувати накопичувач назад із
       уже обчисленої складової, рахуємо межу самої суми один раз тут.
       Сума не має права зрости більше, ніж треба, щоб інтегральна складова
       сама покрила всю вихідну шкалу: integral_limit = out_max * 256 / ki.
       Заразом це і є захист від переповнення: добуток ki * integral за
       побудовою не перевищує out_max * 256, тобто 16.7 млн для 16-бітного ШІМ.
       64-бітна арифметика тут дозволена — це налаштування, не гарячий цикл. */
    if (cfg->ki_q8 > 0) {
        int64_t limit = ((int64_t)cfg->out_max * Q8_ONE) / cfg->ki_q8;
        if (limit > INT32_MAX) {
            limit = INT32_MAX;
        }
        p->integral_limit = (int32_t)limit;
    } else {
        p->integral_limit = 0; /* без інтегральної складової сума не потрібна */
    }

    pid_reset(p);
    return true;
}

void pid_reset(pid_t *p)
{
    p->integral = 0;
    p->prev_error = 0;
    p->have_prev = false;
}

int32_t pid_update(pid_t *p, int32_t setpoint, int32_t measured)
{
    const int32_t error = setpoint - measured;

    const int32_t p_term = mul_q8(p->cfg.kp_q8, error);

    /* Накопичувач обмежуємо ДО множення, а не після. Так він фізично не
       може дорости до переповнення int32 — а саме це, а не завелика
       інтегральна складова, є справжньою пасткою: переповнення міняє знак
       і вимикає нагрівач замість того, щоб гнати його на максимум. */
    int32_t acc = p->integral + error;
    acc = clamp_i32(acc, -p->integral_limit, p->integral_limit);
    p->integral = acc;
    const int32_t i_term = mul_q8(p->cfg.ki_q8, acc);

    /* На першому кроці попередньої помилки ще немає: якщо взяти нуль,
       диференційна складова дасть удар на всю шкалу з нічого. */
    int32_t d_term = 0;
    if (p->have_prev) {
        d_term = mul_q8(p->cfg.kd_q8, error - p->prev_error);
    }
    p->prev_error = error;
    p->have_prev = true;

    return clamp_i32(p_term + i_term + d_term, p->cfg.out_min, p->cfg.out_max);
}

/* ---- Конвеєр ----------------------------------------------------------- */

int32_t adc_code_to_mv(uint16_t raw_adc)
{
    uint32_t code = raw_adc;
    if (code > (uint32_t)ADC_MAX_CODE) {
        code = (uint32_t)ADC_MAX_CODE;
    }
    /* Чисельник максимум 4095 * 3300 = 13 513 500 — вміщується в 32 біти,
       тож проміжного приведення до 64 біт не треба. */
    return (int32_t)((code * (uint32_t)ADC_VREF_MV) / (uint32_t)ADC_MAX_CODE);
}

bool pipeline_init(pipeline_t *pl, uint8_t shift_k, const pid_cfg_t *cfg)
{
    if (pl == NULL) {
        return false;
    }
    if (!ema_init(&pl->filter, shift_k)) {
        return false;
    }
    if (!pid_init(&pl->pid, cfg)) {
        return false;
    }
    pl->last_mv = 0;
    pl->last_duty = 0;
    return true;
}

uint16_t pipeline_step(pipeline_t *pl, uint16_t raw_adc, uint16_t target_mv)
{
    /* 1. Код АЦП у мілівольти. */
    const int32_t mv_raw = adc_code_to_mv(raw_adc);

    /* 2. Згладжування: без нього диференційна складова підсилювала б
          тремтіння молодших розрядів АЦП. */
    const int32_t mv_filtered = ema_update(&pl->filter, mv_raw);
    pl->last_mv = mv_filtered;

    /* 3. Керуючий сигнал. */
    const int32_t control = pid_update(&pl->pid, (int32_t)target_mv, mv_filtered);

    /* 4. Регістр порівняння таймера. Межі регулятора вже лежать у діапазоні
          ШІМ, але обрізаємо ще раз: у регістр іде значення, а не сподівання. */
    pl->last_duty = (uint16_t)clamp_i32(control, 0, PWM_MAX_DUTY);
    return pl->last_duty;
}
