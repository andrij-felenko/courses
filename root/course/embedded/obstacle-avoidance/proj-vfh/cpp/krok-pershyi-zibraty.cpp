// Побудова полярної гістограми щільності перешкод.
// rays[]  — кільце дальностей від давача (N_SECTORS променів)
// hist[]  — вихід: щільність перешкод по секторах
void build_histogram(const Ray rays[N_SECTORS], float hist[N_SECTORS])
{
    // Сталі спадання: на D_MAX внесок = 0, тобто a = b·D_MAX.
    // Візьмемо b = 1, тоді a = D_MAX; на D_MIN внесок максимальний.
    const float b = 1.0f;
    const float a = b * D_MAX;

    for (int i = 0; i < N_SECTORS; i++)
        hist[i] = 0.0f;                     // чистимо

    for (int i = 0; i < N_SECTORS; i++) {
        float d = rays[i].d;

        // Мертва зона й «немає відбитку» — промінь не голосує зовсім.
        if (d < D_MIN || d > D_MAX) continue;

        float c = rays[i].conf;
        float m = c * c * (a - b * d);      // вага перешкоди: conf² · (a − b·d)
        if (m < 0.0f) m = 0.0f;             // страховка від від'ємного біля D_MAX

        hist[i] += m;                       // промінь i припадає на сектор i
    }
}
