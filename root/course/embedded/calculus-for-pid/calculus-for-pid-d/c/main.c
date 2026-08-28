#include <math.h>

/* Налаштування регулятора (стандартна форма через Kp, Ti, Td) */
typedef struct {
    float Kp, Ti, Td;      /* підсилення й часи інтегрування/диференціювання */
    float tau_f;           /* стала часу фільтра похідної, с (≈ Td/N) */
    float u_min, u_max;    /* межі виконавчого органу */
    float Tt;              /* стала часу трекінгу (анти-windup) */
} pid_cfg_t;

/* Стан регулятора — живе між викликами */
typedef struct {
    float integral;        /* накопичена дія I */
    float meas_prev;       /* попередній вимір (для похідної по виміру) */
    float d_filt;          /* фільтроване значення похідної */
    int   first;           /* прапорець першого виклику */
} pid_state_t;

static float clampf(float x, float lo, float hi) {
    return x < lo ? lo : (x > hi ? hi : x);
}

/* Один крок PID. Викликати періодично; dt — фактичний час від минулого виклику. */
float pid_step(const pid_cfg_t *c, pid_state_t *s,
               float setpoint, float measured, float dt)
{
    float e = setpoint - measured;                 /* поточна похибка */

    /* --- D: похідна ПО ВИМІРУ (немає дериватив-стрибка на зміні уставки) --- */
    float d_raw;
    if (s->first) { d_raw = 0.0f; s->first = 0; }  /* на першому кроці нахилу ще нема */
    else          d_raw = -(measured - s->meas_prev) / dt;   /* мінус: ріст виміру = спад похибки */
    s->meas_prev = measured;

    /* фільтр похідної (низькочастотний 1-го порядку): гасить підсилений шум */
    float alpha = dt / (c->tau_f + dt);
    s->d_filt += alpha * (d_raw - s->d_filt);

    /* --- зібрати три складові (Ki = Kp/Ti, Kd = Kp·Td) --- */
    float P = c->Kp * e;
    float I = (c->Ti > 0.0f) ? (c->Kp / c->Ti) * s->integral : 0.0f;
    float D = c->Kp * c->Td * s->d_filt;

    float u_unsat = P + I + D;                      /* до обмеження */
    float u_sat   = clampf(u_unsat, c->u_min, c->u_max);

    /* --- I з інтегруванням + зворотний перерахунок (back-calculation) --- */
    /* трекінг зливає з інтеграла рівно той надлишок, що орган не зміг видати */
    if (c->Ti > 0.0f) {
        float track = (c->Tt > 0.0f) ? (u_sat - u_unsat) / c->Tt : 0.0f;
        s->integral += (e + track) * dt;
    }

    return u_sat;                                   /* у привід — обмежене значення */
}
