// повний крок ПІ-регулятора з антивіндапом (викликати рівно раз на dt)
typedef struct {
    float Kp, Ki;          // коефіцієнти (з lambda-налаштування чи ЗН)
    float integ;           // накопичувач інтеграла (стан)
    float out_min, out_max;// межі виконавчого органу (насичення)
    float i_min, i_max;    // межі самого інтеграла (антивіндап-затиск)
} PI_t;

float pi_step(PI_t *c, float setpoint, float measured, float dt) {
    float e = setpoint - measured;            // помилка
    c->integ += e * dt;                       // накопичуємо площу помилки
    // антивіндап: не даємо інтегралу роздуватися понад межі
    if (c->integ > c->i_max) c->integ = c->i_max;
    if (c->integ < c->i_min) c->integ = c->i_min;
    float u = c->Kp * e + c->Ki * c->integ;   // ПІ-закон
    // насичення виходу під реальний виконавчий орган
    if (u > c->out_max) u = c->out_max;
    if (u < c->out_min) u = c->out_min;
    return u;
}
