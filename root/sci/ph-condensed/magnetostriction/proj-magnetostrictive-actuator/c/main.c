#include <stdio.h>
#include <stdlib.h>
#include <math.h>

/* Структура параметрів магнітострикційного актуатора */
typedef struct {
    double rod_length;     /* Початкова довжина стрижня L0 (м) */
    double lambda_s;       /* Насичена деформація λs */
    double h_sat;          /* Поле насичення H_sat (А/м) */
    double h_bias;         /* Постійне поле підмагнічування (А/м) */
    double turns_per_m;    /* Щільність витків котушки N/L_coil (1/м) */
    double mass;           /* Приведена маса актуатора та вантажу (кг) */
    double stiffness;      /* Жорсткість механічної системи k (Н/м) */
    double damping;        /* Коефіцієнт демпфування c (Н·с/м) */
} ActuatorParams;

/* Стан системи в момент часу t */
typedef struct {
    double time;           /* Час (с) */
    double current;        /* Струм у котушці (А) */
    double h_field;        /* Магнітне поле H (А/м) */
    double position;       /* Зміщення актуатора x (м) */
    double velocity;       /* Швидкість v = dx/dt (м/с) */
    double strain;         /* Поточна деформація λ */
} ActuatorState;

/* Обчислення вільної магнітострикційної деформації λ_free(H) */
double calculate_strain(const ActuatorParams *p, double h_field) {
    double ratio = h_field / p->h_sat;
    return p->lambda_s * tanh(ratio * ratio);
}

/* Крок інтегрування методом Ейлера-Кромера */
void actuator_step(const ActuatorParams *p, ActuatorState *s, double drive_current, double dt) {
    s->current = drive_current;
    s->h_field = p->h_bias + p->turns_per_m * drive_current;
    s->strain = calculate_strain(p, s->h_field);

    /* Еквівалентна вимушена сила від деформації */
    double f_ext = p->stiffness * p->rod_length * s->strain;
    
    /* Прискорення a = (F_ext - k*x - c*v) / m */
    double accel = (f_ext - p->stiffness * s->position - p->damping * s->velocity) / p->mass;

    /* Оновлення швидкості та позиції (схема Ейлера-Кромера) */
    s->velocity += accel * dt;
    s->position += s->velocity * dt;
    s->time += dt;
}

int main(void) {
    ActuatorParams params = {
        .rod_length = 0.10,        /* 10 см */
        .lambda_s = 1.2e-3,        /* 1200 ppm (Terfenol-D) */
        .h_sat = 120000.0,         /* 120 кА/м */
        .h_bias = 40000.0,         /* 40 кА/м робоча точка */
        .turns_per_m = 2000.0,     /* 2000 витків/м */
        .mass = 0.5,               /* 0.5 кг вантажу */
        .stiffness = 5.0e6,        /* 5 МН/м */
        .damping = 150.0           /* 150 Н·с/м */
    };

    ActuatorState state = {0};
    double dt = 1e-5;              /* Крок за часом 10 мкс */
    double freq = 500.0;           /* Частота збудження 500 Гц */
    double current_amp = 5.0;      /* Амплітуда струму 5 А */

    printf("Time(s),Current(A),H_field(A/m),Position(um),Strain(ppm)\n");

    for (int step = 0; step <= 1000; ++step) {
        double current = current_amp * sin(2.0 * M_PI * freq * state.time);
        actuator_step(&params, &state, current, dt);

        if (step % 20 == 0) {
            printf("%.6f,%.3f,%.1f,%.3f,%.1f\n",
                   state.time,
                   state.current,
                   state.h_field,
                   state.position * 1e6,
                   state.strain * 1e6);
        }
    }

    return 0;
}
