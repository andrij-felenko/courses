/* Одиночний полюс на частоті wp (рад/с): інерція, до −90° фази */
static cplx link_pole(double w, double wp) {
    /* 1 / (1 + j·w/wp) */
    return c_div(c_make(1.0, 0.0), c_make(1.0, w / wp));
}

/* Чиста затримка tau (с): фаза −w·tau, модуль 1 */
static cplx link_delay(double w, double tau) {
    double a = -w * tau;
    return c_make(cos(a), sin(a));            /* e^(−j·w·tau) */
}

/* ПІД із фільтрованою похідною: Kp + Ki/(j·w) + Kd·j·w/(1 + j·w/wd) */
static cplx link_pid(double w, double Kp, double Ki, double Kd, double wd) {
    cplx P = c_make(Kp, 0.0);
    /* Ki/(j·w) = −j·Ki/w  (бо 1/j = −j) */
    cplx I = (w > 0.0) ? c_make(0.0, -Ki / w) : c_make(0.0, 0.0);
    /* Kd·j·w / (1 + j·w/wd) */
    cplx Dnum = c_make(0.0, Kd * w);
    cplx Dden = c_make(1.0, w / wd);
    cplx D = c_div(Dnum, Dden);
    return c_add(c_add(P, I), D);
}
