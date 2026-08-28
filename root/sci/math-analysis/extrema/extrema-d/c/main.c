/* Шукає заповнення ШІМ [0..100] з найменшою похибкою регулювання.
   cost(x) — задана функція похибки (вимірювана або модельна). */
typedef float (*cost_fn)(float duty);

float find_min_duty(cost_fn cost, float lo, float hi)
{
    const float h    = 0.5f;    /* крок для скінченної різниці */
    const float step = 1.0f;    /* крок проходу по діапазону   */
    float best_x = lo;
    float best_y = cost(lo);    /* кінець lo — теж кандидат на мінімум */

    for (float x = lo + step; x <= hi - step; x += step) {
        /* наближена похідна — центральна різниця */
        float slope = (cost(x + h) - cost(x - h)) / (2.0f * h);

        /* критична точка: похідна майже нуль і кривина «чаша» */
        if (slope > -1e-3f && slope < 1e-3f) {
            float y = cost(x);
            if (y < best_y) { best_y = y; best_x = x; }
        }
    }

    float y_hi = cost(hi);      /* другий кінець — теж кандидат  */
    if (y_hi < best_y) { best_y = y_hi; best_x = hi; }

    return best_x;              /* заповнення з найменшою похибкою */
}
