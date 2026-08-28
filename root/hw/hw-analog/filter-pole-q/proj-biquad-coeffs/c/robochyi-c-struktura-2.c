// Розрахувати коефіцієнти ФНЧ-біквада для пари полюсів (f0, Q) при частоті fs.
// Білінійне перетворення з передкомпенсацією частоти вшите в sin/cos(ω₀).
// f0, fs — у герцах; Q — добротність пари полюсів. Стан НЕ чіпаємо.
static void biquad_lowpass(biquad *bq, float f0, float Q, float fs)
{
    float w0 = 2.0f * (float)M_PI * f0 / fs;   // цифрова кутова частота
    float cw = cosf(w0);
    float sw = sinf(w0);
    float alpha = sw / (2.0f * Q);             // уся добротність — тут

    float b0 = (1.0f - cw) * 0.5f;
    float b1 =  1.0f - cw;
    float b2 = (1.0f - cw) * 0.5f;
    float a0 =  1.0f + alpha;
    float a1 = -2.0f * cw;
    float a2 =  1.0f - alpha;

    // нормуємо на a0 — щоб у різницевому рівнянні не лишилося ділення
    float inv_a0 = 1.0f / a0;
    bq->b0 = b0 * inv_a0;
    bq->b1 = b1 * inv_a0;
    bq->b2 = b2 * inv_a0;
    bq->a1 = a1 * inv_a0;
    bq->a2 = a2 * inv_a0;
}

// Обнулити пам'ять ланки (перед першим запуском або після паузи в потоці).
static void biquad_reset(biquad *bq)
{
    bq->x1 = bq->x2 = bq->y1 = bq->y2 = 0.0f;
}
