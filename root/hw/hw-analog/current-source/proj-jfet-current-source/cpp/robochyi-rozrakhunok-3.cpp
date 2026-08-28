float biasCurrent(const Jfet &q, float rs)
{
    if (rs <= 0.0f) return q.idss;

    float i = q.idss * 0.5f;               // старт із середини діапазону
    for (int n = 0; n < 60; n++) {
        float ugs = -i * rs;
        if (ugs <= q.vp) ugs = q.vp;
        float t = 1.0f - ugs / q.vp;
        float iNew = q.idss * t * t;
        i = 0.5f * (i + iNew);             // демпфування — гасить гойдання
    }
    return i;
}
