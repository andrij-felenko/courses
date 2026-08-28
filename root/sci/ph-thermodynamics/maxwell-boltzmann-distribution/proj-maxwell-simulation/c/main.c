/* Симулятор релаксації швидкостей молекул (C99) */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>

#define NUM_PARTICLES 100000
#define NUM_COLLISIONS 2000000
#define NUM_BINS 40
#define MASS 4.65e-26     /* Маса молекули азоту N2, кг */
#define KB 1.380649e-23   /* Постійна Больцмана, Дж/К */
#define TARGET_TEMP 300.0 /* Цільова температура, К */

typedef struct {
    double vx;
    double vy;
    double vz;
} Particle;

/* Генерація рівномірного випадкового числа в [0, 1) */
static double rand_uniform(void) {
    return (double)rand() / ((double)RAND_MAX + 1.0);
}

/* Симуляція пружного зіткнення двох частинок у 3D */
static void collide(Particle *p1, Particle *p2) {
    /* Обчислення швидкості центру мас */
    double cm_vx = 0.5 * (p1->vx + p2->vx);
    double cm_vy = 0.5 * (p1->vy + p2->vy);
    double cm_vz = 0.5 * (p1->vz + p2->vz);

    /* Відносна швидкість до зіткнення */
    double rel_vx = p1->vx - p2->vx;
    double rel_vy = p1->vy - p2->vy;
    double rel_vz = p1->vz - p2->vz;
    double v_rel_mag = sqrt(rel_vx * rel_vx + rel_vy * rel_vy + rel_vz * rel_vz);

    /* Генерація випадкового напрямку у 3D (ізотропне розсіювання) */
    double cos_theta = 2.0 * rand_uniform() - 1.0;
    double sin_theta = sqrt(fmax(0.0, 1.0 - cos_theta * cos_theta));
    double phi = 2.0 * M_PI * rand_uniform();

    double new_rel_vx = v_rel_mag * sin_theta * cos(phi);
    double new_rel_vy = v_rel_mag * sin_theta * sin(phi);
    double new_rel_vz = v_rel_mag * cos_theta;

    /* Оновлення швидкостей частинок */
    p1->vx = cm_vx + 0.5 * new_rel_vx;
    p1->vy = cm_vy + 0.5 * new_rel_vy;
    p1->vz = cm_vz + 0.5 * new_rel_vz;

    p2->vx = cm_vx - 0.5 * new_rel_vx;
    p2->vy = cm_vy - 0.5 * new_rel_vy;
    p2->vz = cm_vz - 0.5 * new_rel_vz;
}

int main(void) {
    srand((unsigned int)time(NULL));

    Particle *particles = (Particle *)malloc(NUM_PARTICLES * sizeof(Particle));
    if (!particles) {
        fprintf(stderr, "Помилка виділення пам'яті!\n");
        return 1;
    }

    /* Значення моноенергетичної швидкості v0 для заданої T */
    double v0 = sqrt(3.0 * KB * TARGET_TEMP / MASS);

    /* Ініціалізація: всі частинки мають однакову швидкість v0, але випадкові напрямки */
    for (int i = 0; i < NUM_PARTICLES; i++) {
        double cos_t = 2.0 * rand_uniform() - 1.0;
        double sin_t = sqrt(fmax(0.0, 1.0 - cos_t * cos_t));
        double p = 2.0 * M_PI * rand_uniform();

        particles[i].vx = v0 * sin_t * cos(p);
        particles[i].vy = v0 * sin_t * sin(p);
        particles[i].vz = v0 * cos_t;
    }

    printf("=== Симуляція молекулярних зіткнень (C99) ===\n");
    printf("Частинок: %d | Зіткнень: %d | T_початкова: %.1f K\n", 
           NUM_PARTICLES, NUM_COLLISIONS, TARGET_TEMP);

    /* Основний цикл парних зіткнень */
    for (int col = 0; col < NUM_COLLISIONS; col++) {
        int idx1 = rand() % NUM_PARTICLES;
        int idx2 = rand() % NUM_PARTICLES;
        if (idx1 != idx2) {
            collide(&particles[idx1], &particles[idx2]);
        }
    }

    /* Побудова гістограми швидкостей */
    double max_speed = 3.0 * v0;
    double bin_width = max_speed / NUM_BINS;
    int histogram[NUM_BINS] = {0};

    double sum_v = 0.0;
    double sum_v2 = 0.0;

    for (int i = 0; i < NUM_PARTICLES; i++) {
        double speed = sqrt(particles[i].vx * particles[i].vx +
                            particles[i].vy * particles[i].vy +
                            particles[i].vz * particles[i].vz);
        sum_v += speed;
        sum_v2 += speed * speed;

        int bin = (int)(speed / bin_width);
        if (bin >= 0 && bin < NUM_BINS) {
            histogram[bin]++;
        }
    }

    double v_avg_sim = sum_v / NUM_PARTICLES;
    double v_rms_sim = sqrt(sum_v2 / NUM_PARTICLES);

    /* Теоретичні значення */
    double v_p_theory = sqrt(2.0 * KB * TARGET_TEMP / MASS);
    double v_avg_theory = sqrt(8.0 * KB * TARGET_TEMP / (M_PI * MASS));
    double v_rms_theory = sqrt(3.0 * KB * TARGET_TEMP / MASS);

    printf("\n--- Статистика після релаксації ---\n");
    printf("v_сер (модель): %6.1f м/с | v_сер (теорія): %6.1f м/с\n", v_avg_sim, v_avg_theory);
    printf("v_кв  (модель): %6.1f м/с | v_кв  (теорія): %6.1f м/с\n", v_rms_sim, v_rms_theory);
    printf("v_p   (теорія): %6.1f м/с\n", v_p_theory);

    printf("\n--- Гістограма швидкостей (зірочки = частка) ---\n");
    for (int b = 0; b < NUM_BINS; b += 2) {
        double v_center = (b + 0.5) * bin_width;
        double fraction = (double)histogram[b] / NUM_PARTICLES;
        int stars = (int)(fraction * 400.0);

        printf("%4.0f м/с | ", v_center);
        for (int s = 0; s < stars; s++) printf("*");
        printf("\n");
    }

    free(particles);
    return 0;
}
