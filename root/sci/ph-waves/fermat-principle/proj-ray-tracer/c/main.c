#include <stdio.h>
#include <stdlib.h>
#include <math.h>

// Вектор стану променя у 2D просторі: (x, y, px, py)
typedef struct {
    double x;
    double y;
    double px;
    double py;
} RayState;

// Фізичні параметри атмосфери
typedef struct {
    double n0;  // показник заломлення гарячого повітря біля землі
    double dn;  // перепад показника заломлення з висотою
    double y0;  // характерний масштаб висоти (м)
} AtmosphereModel;

// Обчислення локального показника заломлення n(x, y)
double get_refractive_index(const AtmosphereModel* env, double x, double y) {
    (void)x;
    if (y < 0.0) y = 0.0;
    return env->n0 + env->dn * (1.0 - exp(-y / env->y0));
}

// Обчислення векторного градієнта ∇n = (dn/dx, dn/dy)
void get_index_gradient(const AtmosphereModel* env, double x, double y, double* dndx, double* dndy) {
    (void)x;
    *dndx = 0.0;
    if (y < 0.0) y = 0.0;
    *dndy = (env->dn / env->y0) * exp(-y / env->y0);
}

// Прави частини системи ЗДР: dState/ds = F(State)
RayState ray_derivatives(const AtmosphereModel* env, RayState state) {
    double n = get_refractive_index(env, state.x, state.y);
    double dndx, dndy;
    get_index_gradient(env, state.x, state.y, &dndx, &dndy);

    RayState deriv;
    deriv.x  = state.px / n;
    deriv.y  = state.py / n;
    deriv.px = dndx;
    deriv.py = dndy;
    return deriv;
}

// Крок чисельного інтегрування методом Рунге-Кутти 4-го порядку (RK4)
RayState rk4_step(const AtmosphereModel* env, RayState state, double ds) {
    RayState k1 = ray_derivatives(env, state);

    RayState s_k2 = {
        state.x  + 0.5 * ds * k1.x,
        state.y  + 0.5 * ds * k1.y,
        state.px + 0.5 * ds * k1.px,
        state.py + 0.5 * ds * k1.py
    };
    RayState k2 = ray_derivatives(env, s_k2);

    RayState s_k3 = {
        state.x  + 0.5 * ds * k2.x,
        state.y  + 0.5 * ds * k2.y,
        state.px + 0.5 * ds * k2.px,
        state.py + 0.5 * ds * k2.py
    };
    RayState k3 = ray_derivatives(env, s_k3);

    RayState s_k4 = {
        state.x  + ds * k3.x,
        state.y  + ds * k3.y,
        state.px + ds * k3.px,
        state.py + ds * k3.py
    };
    RayState k4 = ray_derivatives(env, s_k4);

    RayState next_state;
    next_state.x  = state.x  + (ds / 6.0) * (k1.x  + 2.0 * k2.x  + 2.0 * k3.x  + k4.x);
    next_state.y  = state.y  + (ds / 6.0) * (k1.y  + 2.0 * k2.y  + 2.0 * k3.y  + k4.y);
    next_state.px = state.px + (ds / 6.0) * (k1.px + 2.0 * k2.px + 2.0 * k3.px + k4.px);
    next_state.py = state.py + (ds / 6.0) * (k1.py + 2.0 * k2.py + 2.0 * k3.py + k4.py);

    return next_state;
}

int main(void) {
    AtmosphereModel env = { .n0 = 1.00026, .dn = 0.00030, .y0 = 1.5 };

    // Початкові умови трасування: джерело світла на висоті 1.2 м
    double start_x = 0.0;
    double start_y = 1.2;
    double angle_deg = -1.5; // кут нахилу -1.5° до горизонту
    double angle_rad = angle_deg * (M_PI / 180.0);

    double n_start = get_refractive_index(&env, start_x, start_y);
    RayState current = {
        .x = start_x,
        .y = start_y,
        .px = n_start * cos(angle_rad),
        .py = n_start * sin(angle_rad)
    };

    double ds = 0.1;           // крок за довжиною дуги (метрів)
    double max_length = 150.0; // максимальна довжина прогону
    double opl = 0.0;          // накопичена оптична довжина шляху

    printf("# Tracing ray in GRIN atmosphere (Mirage Simulation)\n");
    printf("# s(m)\tx(m)\ty(m)\tpx\tpy\tn\tOPL(m)\n");

    for (double s = 0.0; s < max_length; s += ds) {
        double n_curr = get_refractive_index(&env, current.x, current.y);
        opl += n_curr * ds;

        printf("%.1f\t%.3f\t%.4f\t%.6f\t%.6f\t%.6f\t%.4f\n",
               s, current.x, current.y, current.px, current.py, n_curr, opl);

        if (current.y <= 0.0 && current.py < 0.0) {
            // Гранична умова дзеркального відбиття від землі при досягненні нуля
            current.py = -current.py;
        }

        current = rk4_step(&env, current, ds);
    }

    return 0;
}
