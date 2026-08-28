#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

// Структура конфігурації симулятора
typedef struct {
    double length;      // Довжина стрижня [м]
    int num_points;     // Кількість вузлів сітки
    double alpha;       // Коефіцієнт температуропровідності [м²/с]
    double t_left;      // Гранична температура зліва [°C] (Діріхле)
    double t_right;     // Гранична температура справа [°C] (Діріхле)
    double t_initial;   // Початкова температура всередині [°C]
} thermal_config_t;

// Основна функція розрахунку явної схеми
bool run_thermal_simulation(const thermal_config_t* cfg, double total_time, double dt) {
    if (!cfg || cfg->num_points < 3 || cfg->length <= 0.0) {
        printf("Помилка: Некоректні входні параметри.\n");
        return false;
    }

    double dx = cfg->length / (cfg->num_points - 1);
    double r = cfg->alpha * dt / (dx * dx);

    // Строга перевірка умови стійкості CFL
    if (r > 0.5) {
        printf("Помилка стійкості: r = %.4f перевищує 0.5!\n", r);
        printf("Максимально припустимий dt <= %.6f с\n", 0.5 * dx * dx / cfg->alpha);
        return false;
    }

    // Виділення пам'яті під подвійну буферизацію сітки
    double* u_curr = (double*)malloc(cfg->num_points * sizeof(double));
    double* u_next = (double*)malloc(cfg->num_points * sizeof(double));
    if (!u_curr || !u_next) {
        printf("Помилка виділення оперативної пам'яті.\n");
        free(u_curr);
        free(u_next);
        return false;
    }

    // Ініціалізація початкового стану сітки
    for (int i = 0; i < cfg->num_points; ++i) {
        u_curr[i] = cfg->t_initial;
    }
    u_curr[0] = cfg->t_left;
    u_curr[cfg->num_points - 1] = cfg->t_right;

    int steps = (int)(total_time / dt);
    for (int step = 0; step < steps; ++step) {
        // Фіксація граничних умов 1-го роду
        u_next[0] = cfg->t_left;
        u_next[cfg->num_points - 1] = cfg->t_right;

        // Обчислення внутрішніх вузлів за явною схемою
        for (int i = 1; i < cfg->num_points - 1; ++i) {
            u_next[i] = u_curr[i] + r * (u_curr[i + 1] - 2.0 * u_curr[i] + u_curr[i - 1]);
        }

        // Обмін буферів пам'яті
        for (int i = 0; i < cfg->num_points; ++i) {
            u_curr[i] = u_next[i];
        }
    }

    // Виведення результуючого профілю температури
    printf("--- Результати розрахунку (t = %.1f с, r = %.4f) ---\n", total_time, r);
    for (int i = 0; i < cfg->num_points; i += cfg->num_points / 5) {
        printf("Позиція x = %.3f м : Температура T = %.2f °C\n", i * dx, u_curr[i]);
    }

    free(u_curr);
    free(u_next);
    return true;
}

int main(void) {
    thermal_config_t config = {
        .length = 0.5,
        .num_points = 51,
        .alpha = 9.7e-5,    // Алюміній: α ≈ 9.7e-5 м²/с
        .t_left = 100.0,
        .t_right = 20.0,
        .t_initial = 20.0
    };

    double dt = 0.0005;     // Крок часу підібрано під умову CFL
    double total_time = 10.0;

    if (!run_thermal_simulation(&config, total_time, dt)) {
        return 1;
    }
    return 0;
}
