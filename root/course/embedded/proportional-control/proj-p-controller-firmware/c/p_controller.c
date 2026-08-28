// p_controller.c
#include "p_controller.h"

// один такт пропорційного регулятора; повертає ГОТОВИЙ до подачі вплив
float p_step(p_ctrl_t *c, float setpoint, float measure)
{
    // 1. пропорційна дія із зважуванням завдання (beta):
    //    beta = 1 -> Kp*(r - y) ; beta = 0 -> -Kp*y ; проміжне — суміш
    float p_term = c->kp * (c->beta * setpoint - measure);

    // 2. додаємо відому наперед поправку (живлення наперед / зсув)
    float u = p_term + c->u_bias;

    c->last_u = u;                       // сирий вихід — для діагностики

    // 3. обмеження під РЕАЛЬНІ межі виконавчого органу
    c->saturated = false;
    if (u > c->u_max) { u = c->u_max; c->saturated = true; }
    if (u < c->u_min) { u = c->u_min; c->saturated = true; }

    return u;                            // тільки тепер віддавати на драйвер
}
