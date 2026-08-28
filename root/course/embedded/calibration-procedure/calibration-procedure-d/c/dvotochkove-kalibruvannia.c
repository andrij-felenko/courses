typedef struct {
    float k;   // кодів на одиницю величини (нахил)
    float b;   // сирий код при нульовій величині (зсув)
} cal_t;

// крок калібрування: два усереднені сирі коди на двох еталонах
cal_t cal_two_point(int32_t raw_low,  float x_low,
                    int32_t raw_high, float x_high)
{
    cal_t c;
    c.k = (float)(raw_high - raw_low) / (x_high - x_low);
    c.b = raw_low - c.k * x_low;
    return c;
}

// рантайм: сирий код → фізична величина
float cal_apply(const cal_t *c, int32_t raw)
{
    return (raw - c->b) / c->k;
}
