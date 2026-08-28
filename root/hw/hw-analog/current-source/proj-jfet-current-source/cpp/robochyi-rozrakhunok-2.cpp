/*
 * Струм self-bias-джерела при заданому резисторі витоку.
 * Простою ітерацією петлі U_GS = −I·R_S → I(U_GS) за квадратичним законом.
 * Петля стискальна, тож збігається за кілька кроків.
 */
float biasCurrent(const Jfet &q, float rs)
{
    if (rs <= 0.0f) return q.idss;         // закорочений затвор

    float i = q.idss;                      // старт зверху, з I_DSS
    for (int n = 0; n < 40; n++) {
        float ugs = -i * rs;               // напруга, яку дає резистор
        if (ugs <= q.vp) ugs = q.vp;       // глибше відсічки не буває
        float t = 1.0f - ugs / q.vp;       // = (1 − U_GS/U_P)
        i = q.idss * t * t;                // струм за квадратичним законом
    }
    return i;
}
