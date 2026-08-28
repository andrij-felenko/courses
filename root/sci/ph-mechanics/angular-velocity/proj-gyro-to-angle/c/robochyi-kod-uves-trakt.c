#include <math.h>

typedef struct {
    float theta;    /* оцінка кута, рад (стан)              */
    float bias;     /* зсув гіроскопа, рад/с                */
    float alpha;    /* вага довіри до гіроскопа, напр. 0.98 */
} Comp;

static void comp_init(Comp *c, float bias, float alpha)
{
    c->theta = 0.0f;
    c->bias  = bias;
    c->alpha = alpha;
}

/* Один такт зшивання.
   raw  — сирий відлік гіро по осі повороту;
   ax,az — осі акселерометра у площині цього нахилу, м/с²;
   dt   — реальний крок часу, с.                              */
static void comp_step(Comp *c, int16_t raw, float ax, float az, float dt)
{
    /* 1) гіроскоп: у рад/с, прибрати зсув, проінтегрувати */
    float w = gyro_rate_rad(raw) - c->bias;
    float theta_gyro = c->theta + w * dt;

    /* 2) акселерометр: абсолютний нахил із проєкцій тяжіння */
    float theta_acc = atan2f(ax, az);

    /* 3) зшити: майже все від гіро, дрібка від акселя */
    c->theta = c->alpha * theta_gyro + (1.0f - c->alpha) * theta_acc;
}
