/* Опис усієї розімкненої петлі — усе, що аналізатор має знати про контур */
typedef struct {
    double wp_plant;   /* полюс об'єкта (механіка), рад/с */
    double wp_sensor;  /* полюс давача-фільтра, рад/с    */
    double Kp, Ki, Kd; /* коефіцієнти ПІД                */
    double wd;         /* полюс фільтра похідної, рад/с  */
    double Ts;         /* крок дискретизації, с          */
    double dc_gain;    /* сумарний сталий коеф. тракту (об'єкт·давач·актуатор) */
} loop_t;

/* Комплексне підсилення розімкненої петлі на частоті w (рад/с) */
static cplx loop_L(const loop_t *L, double w) {
    /* цифровий мертвий час: пів-такт фіксатора + такт на обчислення ≈ 1.5·Ts */
    double tau = 1.5 * L->Ts;

    cplx out = c_make(L->dc_gain, 0.0);        /* сталий коефіцієнт тракту */
    out = c_mul(out, link_pole(w, L->wp_plant));
    out = c_mul(out, link_pole(w, L->wp_sensor));
    out = c_mul(out, link_pid(w, L->Kp, L->Ki, L->Kd, L->wd));
    out = c_mul(out, link_delay(w, tau));
    return out;
}
