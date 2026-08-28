#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define GRID_SIZE 200
#define NUM_STEPS 300
#define C_SPEED 3.0e8    /* швидкість світла у вакуумі (м/с) */
#define DZ 0.001         /* просторовий крок 1 мм */

/* Оновлення магнітного поля B за диференційним законом Фарадея */
void update_magnetic_field(double* Bx, const double* Ey, int size, double dt, double dz) {
    for (int k = 0; k < size - 1; ++k) {
        /* Bx[k] відповідає вузлу k + 1/2 */
        Bx[k] += (dt / dz) * (Ey[k + 1] - Ey[k]);
    }
}

/* Оновлення електричного поля E за законом Ампера-Максвелла */
void update_electric_field(double* Ey, const double* Bx, int size, double dt, double dz) {
    double c2 = C_SPEED * C_SPEED;
    for (int k = 1; k < size - 1; ++k) {
        Ey[k] += (c2 * dt / dz) * (Bx[k] - Bx[k - 1]);
    }
}

int main(void) {
    double dt = 0.99 * DZ / C_SPEED; /* крок по часу з умови Куранта */
    
    double* Ey = (double*)calloc(GRID_SIZE, sizeof(double));
    double* Bx = (double*)calloc(GRID_SIZE, sizeof(double));
    
    if (!Ey || !Bx) {
        fprintf(stderr, "Помилка виділення пам'яті!\n");
        return 1;
    }

    printf("Крок часу dt = %.3e с, просторовий крок dz = %.3e м\n", dt, DZ);

    /* Головний часовий цикл симуляції */
    for (int t = 0; t < NUM_STEPS; ++t) {
        /* Джерело гаусового імпульсу в центрі сітки */
        Ey[GRID_SIZE / 2] += exp(-pow((t - 40.0) / 12.0, 2.0));

        /* Крок 1: оновлення B з ротора E (Закон Фарадея) */
        update_magnetic_field(Bx, Ey, GRID_SIZE, dt, DZ);

        /* Крок 2: оновлення E з ротора B (Закон Ампера-Максвелла) */
        update_electric_field(Ey, Bx, GRID_SIZE, dt, DZ);
    }

    printf("Симуляцію успішно завершено. Поле Ey у центрі: %.4f B/м\n", Ey[GRID_SIZE / 2]);

    free(Ey);
    free(Bx);
    return 0;
}
