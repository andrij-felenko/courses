#include "filters.h"

#include "afe_model.h" /* AFE_STEP_HZ для коефіцієнта проріджування */

int32_t div_round(int64_t numerator, int64_t denominator)
{
    if (denominator == 0) {
        return 0;
    }
    int64_t half = denominator / 2;
    int64_t result = (numerator >= 0) == (denominator > 0)
                   ? (numerator + half) / denominator
                   : (numerator - half) / denominator;
    return (int32_t)result;
}

void ma_init(ma_t *f)
{
    f->sum = 0;
    f->index = 0;
    f->count = 0;
    for (uint8_t i = 0; i < MA_WINDOW; ++i) {
        f->buffer[i] = 0;
    }
}

int32_t ma_update(ma_t *f, int32_t x)
{
    /* Кільцевий буфер: віднімаємо найстаріший відлік і додаємо новий, тож
       вартість кроку не залежить від довжини вікна. */
    f->sum -= f->buffer[f->index];
    f->buffer[f->index] = x;
    f->sum += x;
    f->index = (uint8_t)((f->index + 1) % MA_WINDOW);

    if (f->count < MA_WINDOW) {
        f->count++;
    }
    return div_round(f->sum, f->count);
}

bool ma_ready(const ma_t *f)
{
    return f->count >= MA_WINDOW;
}

bool ema_init(ema_t *f, uint8_t shift_k)
{
    if (shift_k == 0 || shift_k > 15) {
        return false;
    }
    f->accumulator = 0;
    f->shift_k = shift_k;
    f->initialized = false;
    return true;
}

int32_t ema_update(ema_t *f, int32_t x)
{
    if (!f->initialized) {
        /* Перший відлік заряджає накопичувач одразу: інакше фільтр повзтиме
           до робочої точки з нуля цілу секунду, а вимірювання вже йде. */
        f->accumulator = x << f->shift_k;
        f->initialized = true;
        return x;
    }

    f->accumulator += x - (f->accumulator >> f->shift_k);
    return f->accumulator >> f->shift_k;
}

void dec_init(dec_t *d)
{
    d->sum = 0;
    d->count = 0;
}

bool dec_push(dec_t *d, int32_t x, int32_t *out)
{
    d->sum += x;
    d->count++;

    if (d->count < DECIMATION_FACTOR) {
        return false;
    }

    /* Середнє пачки у форматі Q4: усереднення ста відліків дає приблизно
       3.3 додаткових розряди, і віддавати їх назад округленням до цілого
       коду означало б викинути весь виграш передискретизації. */
    *out = div_round((int64_t)d->sum * DECIMATION_Q, DECIMATION_FACTOR);
    d->sum = 0;
    d->count = 0;
    return true;
}
