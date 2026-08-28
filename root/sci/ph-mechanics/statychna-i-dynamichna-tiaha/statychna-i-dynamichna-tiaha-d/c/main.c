#include <math.h>
#include <stdbool.h>
#include <stdio.h>

/* Параметри геометрії пропелера (усі одиниці в системі SI) */
typedef struct {
    double diameter_m;     /* Діаметр D, м */
    double pitch_m;        /* Геометричний крок P, м */
    double ct0;            /* Статичний коефіцієнт тяги при J = 0 */
    double cp0;            /* Коефіцієнт профільної потужності */
} PropellerSpec;

/* Результати аеродинамічного розрахунку в точці польоту */
typedef struct {
    double advance_ratio;  /* Коефіцієнт поступу J */
    double thrust_n;       /* Динамічна тяга T, Н */
    double power_w;        /* Механічна потужність на валу P, Вт */
    double efficiency;     /* Пропульсивний ККД eta (0.0 ... 1.0) */
    bool is_windmilling;   /* Чи перейшов гвинт у режим гальмування (T < 0) */
} PropellerState;

/* Обчислення динамічної тяги та характеристик гвинта */
bool calculate_propeller_state(
    const PropellerSpec* spec,
    double forward_speed_mps,  /* Швидкість польоту V0, м/с */
    double rpm,                /* Частота обертання, об/хв */
    double air_density,        /* Густина повітря rho, кг/м^3 */
    PropellerState* out_state
) {
    if (!spec || !out_state || spec->diameter_m <= 0.0 || rpm <= 0.0 || air_density <= 0.0) {
        return false;
    }

    const double n = rpm / 60.0;                    /* Оберти за секунду */
    const double d = spec->diameter_m;
    const double p = spec->pitch_m;
    const double v0 = (forward_speed_mps < 0.0) ? 0.0 : forward_speed_mps;

    /* Коефіцієнт поступу J = V0 / (n * D) */
    const double j = v0 / (n * d);

    /* Аеродинамічний коефіцієнт нульової тяги J_zero ≈ P / D */
    const double j_zero = p / d;

    /* Динамічний коефіцієнт тяги C_T(J) за лінійно-параболічною моделлю */
    double ct = 0.0;
    if (j_zero > 0.0) {
        ct = spec->ct0 * (1.0 - (j / j_zero));
    }

    /* Коефіцієнт потужності C_P(J) */
    double cp = spec->cp0;
    if (ct > 0.0) {
        /* Індукована складова потужності росте разом із корисною тягою */
        cp += 0.95 * j * ct;
    }

    /* Розрахунок фізичних величин сили та потужності */
    const double d4 = d * d * d * d;
    const double d5 = d4 * d;
    const double n2 = n * n;
    const double n3 = n2 * n;

    const double thrust = ct * air_density * n2 * d4;
    const double power = cp * air_density * n3 * d5;

    /* Пропульсивний ККД: eta = (T * V0) / P_shaft */
    double efficiency = 0.0;
    if (power > 1e-3 && thrust > 0.0 && v0 > 0.0) {
        efficiency = (thrust * v0) / power;
        if (efficiency > 0.90) {
            efficiency = 0.90; /* Реальне фізичне обмеження ККД лопаті */
        }
    }

    out_state->advance_ratio = j;
    out_state->thrust_n = thrust;
    out_state->power_w = power;
    out_state->efficiency = efficiency;
    out_state->is_windmilling = (thrust < 0.0);

    return true;
}

int main(void) {
    /* Приклад: карбоновий пропелер 10x4.5 дюйма (D=0.254м, P=0.1143м) */
    PropellerSpec prop = {
        .diameter_m = 0.254,
        .pitch_m = 0.1143,
        .ct0 = 0.098,
        .cp0 = 0.038
    };

    const double rpm = 8000.0;
    const double rho = 1.225;
    PropellerState state;

    printf("=== Продування гвинта 10x4.5 (P/D = %.2f) при %.0f RPM ===\n",
           prop.pitch_m / prop.diameter_m, rpm);
    printf(" V0 (м/с) |    J   | Тяга (Н) | Тяга (гс) | Потужність (Вт) |  ККД (%%)\n");
    printf("----------+--------+----------+-----------+-----------------+----------\n");

    for (double v = 0.0; v <= 20.0; v += 4.0) {
        if (calculate_propeller_state(&prop, v, rpm, rho, &state)) {
            printf("  %5.1f   |  %4.2f  |  %6.2f  |  %7.1f  |     %6.1f      |  %5.1f%%\n",
                   v,
                   state.advance_ratio,
                   state.thrust_n,
                   state.thrust_n * 101.97, /* Переведення Н у грам-сили */
                   state.power_w,
                   state.efficiency * 100.0);
        }
    }

    return 0;
}
