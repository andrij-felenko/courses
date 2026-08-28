/* test_simulation.c - Числова перевірка динаміки повернення на лінію на C */
#include <stdio.h>
#include "l1_controller.h"

int main(void) {
    l1_state_t ctrl;
    l1_init(&ctrl, 18.0f, 30.0f);

    l1_vec2_t pos = {0.0f, 60.0f};  /* Початкове зміщення 60 м */
    l1_vec2_t wa = {0.0f, 0.0f};
    l1_vec2_t wb = {2000.0f, 0.0f};

    const float wind_y = 6.0f;      /* Боковий вітер 6 м/с */
    const float airspeed = 20.0f;
    float heading = 0.0f;           /* Початковий курс на схід */
    const float dt = 0.1f;

    printf("Час(с) | X(м)    | Y(м)   | CTE(м) | Крен(град) | L1(м)\n");
    printf("--------------------------------------------------------\n");

    for (int step = 0; step <= 250; ++step) {
        const float t = step * dt;

        /* Шляхова швидкість з урахуванням вітру */
        l1_vec2_t vel = {
            airspeed * cosf(heading),
            airspeed * sinf(heading) + wind_y
        };

        l1_update_line(&ctrl, pos, vel, wa, wb, dt);

        /* Динаміка розвороту літака за кутом крену */
        const float turn_rate = (L1_GRAVITY / airspeed) * tanf(ctrl.roll_cmd);
        heading += turn_rate * dt;

        /* Інтегрування положення */
        pos.x += vel.x * dt;
        pos.y += vel.y * dt;

        if (step % 25 == 0) {
            printf("%6.1f | %7.1f | %6.2f | %6.2f | %10.1f | %5.1f\n",
                   t, pos.x, pos.y, ctrl.cross_track_err,
                   ctrl.roll_cmd * (180.0f / L1_PI), ctrl.lookahead_dist);
        }
    }

    return 0;
}
