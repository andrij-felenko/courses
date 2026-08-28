#include <stdio.h>
#include <stdlib.h>
#include <math.h>

/* Параметри п'єзоактуатора та механічного навантаження */
typedef struct {
    double d33;          /* П'єзомодуль, м/В (наприклад, 400e-12) */
    double K_p;          /* Власна жорсткість стека, Н/м (наприклад, 50e6) */
    double C0;           /* Електрична ємність стека, Ф (наприклад, 1.5e-6) */
    int num_layers;      /* Кількість шарів N (наприклад, 100) */
    double mass;         /* Маса навантаження m, кг (наприклад, 0.5) */
    double damping;      /* Коефіцієнт демпфування c_ext, Н·с/м (наприклад, 150) */
    double k_ext;        /* Зовнішня жорсткість k_ext, Н/м (наприклад, 5e6) */
    /* Параметри гістерезису Бука-Вена */
    double bw_alpha;
    double bw_beta;
    double bw_gamma;
    double bw_n;
} PiezoParams;

/* Динамічний стан системи */
typedef struct {
    double position;     /* Зсув x, м */
    double velocity;     /* Швидкість v = dx/dt, м/с */
    double hyst_state;   /* Внутрішня змінна гістерезису h */
    double charge;       /* Накопичений заряд Q, Кл */
} ActuatorState;

/* Ініціалізація параметрів за замовчуванням для PZT-стека */
PiezoParams piezo_init_default(void) {
    PiezoParams p;
    p.d33 = 450e-12;
    p.K_p = 40e6;
    p.C0 = 2.2e-6;
    p.num_layers = 120;
    p.mass = 0.25;
    p.damping = 200.0;
    p.k_ext = 2e6;
    p.bw_alpha = 0.25;
    p.bw_beta = 0.15;
    p.bw_gamma = 0.10;
    p.bw_n = 1.0;
    return p;
}

/* Одинарний крок інтегрування методом Ейлера-Кромара */
void piezo_step(const PiezoParams* p, ActuatorState* s, double voltage_in, double dt) {
    /* 1. Обчислення прямої п'єзосили */
    double F_piezo = p->num_layers * p->d33 * p->K_p * voltage_in;

    /* 2. Оновлення нелінійної сили гістерезису (модель Бука-Вена) */
    double v = s->velocity;
    double h = s->hyst_state;
    double dh_dt = p->bw_alpha * v - p->bw_beta * fabs(v) * h - p->bw_gamma * v * fabs(h);
    s->hyst_state += dh_dt * dt;

    /* 3. Сумарна сила */
    double F_net = F_piezo - (p->K_p + p->k_ext) * s->position - p->damping * v - s->hyst_state * p->K_p * 0.1;

    /* 4. Прискорення та інтегрування швидкості й координати */
    double accel = F_net / p->mass;
    s->velocity += accel * dt;
    s->position += s->velocity * dt;
    
    /* 5. Накопичення заряду Q = C0 * V + N * d33 * F */
    s->charge = p->C0 * voltage_in + p->num_layers * p->d33 * (p->K_p * s->position);
}

int main(void) {
    PiezoParams params = piezo_init_default();
    ActuatorState state = {0.0, 0.0, 0.0, 0.0};

    double dt = 1e-6;            /* Крок за часом 1 мкс */
    double t_max = 0.01;         /* Симуляція на 10 мс */
    double freq = 200.0;         /* Синусоїдальний сигнал 200 Гц */
    double V_amplitude = 100.0;  /* Амплітуда напруги 100 В */

    int steps = (int)(t_max / dt);
    printf("Час(мс), Напруга(В), Зсув(мкм), Заряд(мкКл)\n");

    for (int i = 0; i < steps; ++i) {
        double t = i * dt;
        double V_in = V_amplitude * sin(2.0 * M_PI * freq * t);

        piezo_step(&params, &state, V_in, dt);

        if (i % 500 == 0) {
            printf("%.3f, %.2f, %.4f, %.4f\n", 
                   t * 1000.0, V_in, state.position * 1e6, state.charge * 1e6);
        }
    }

    return 0;
}
