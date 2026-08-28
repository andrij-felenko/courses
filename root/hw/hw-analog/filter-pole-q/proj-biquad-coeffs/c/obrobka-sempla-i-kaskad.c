// Прогнати один семпл крізь ланку (Direct Form I). Повертає вихід y[n].
static float biquad_process(biquad *bq, float x)
{
    float y = bq->b0 * x
            + bq->b1 * bq->x1 + bq->b2 * bq->x2
            - bq->a1 * bq->y1 - bq->a2 * bq->y2;

    bq->x2 = bq->x1;   bq->x1 = x;     // зсув минулих входів
    bq->y2 = bq->y1;   bq->y1 = y;     // зсув минулих виходів
    return y;
}
