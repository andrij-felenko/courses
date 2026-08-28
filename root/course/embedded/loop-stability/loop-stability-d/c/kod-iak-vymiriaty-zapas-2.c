typedef struct {
    double Kp, Ki, Kd, tau_d;   // регулятор
    double tau_p1, tau_p2;      // два полюси об'єкта
    double tau_sensor;          // полюс давача
    double Ts;                  // період дискретизації (1/fs)
    double t_compute;           // затримка обчислень (частка Ts або цілий Ts)
} loop_t;

static double complex L_of_w(const loop_t *m, double w) {
    double complex L = pid(w, m->Kp, m->Ki, m->Kd, m->tau_d);
    L *= pole(w, m->tau_p1);
    L *= pole(w, m->tau_p2);
    L *= pole(w, m->tau_sensor);
    // ефективна затримка дискретного контуру: пів-такту утримки + обчислення
    double dt_eff = 0.5 * m->Ts + m->t_compute;
    L *= dead_time(w, dt_eff);
    return L;
}
