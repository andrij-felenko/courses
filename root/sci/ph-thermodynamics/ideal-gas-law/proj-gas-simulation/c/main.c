#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>

#define M_PI_VAL 3.14159265358979323846

typedef struct {
    double x, y;
    double vx, vy;
} Particle;

typedef struct {
    double lx, ly;
    double particle_mass;
    double kb;
    int num_particles;
} GasSimConfig;

void init_particles(Particle *p, int count, double lx, double ly, double target_temp, double mass, double kb) {
    // В 2D: <E_k> = m * v_sq / 2 = k_B * T  =>  v_rms = sqrt(2 * k_B * T / m)
    double v_rms = sqrt(2.0 * kb * target_temp / mass);
    int grid_size = (int)ceil(sqrt((double)count));
    double dx = (lx - 0.4) / grid_size;
    double dy = (ly - 0.4) / grid_size;

    int idx = 0;
    for (int i = 0; i < grid_size && idx < count; i++) {
        for (int j = 0; j < grid_size && idx < count; j++) {
            p[idx].x = 0.2 + i * dx;
            p[idx].y = 0.2 + j * dy;

            double angle = ((double)rand() / RAND_MAX) * 2.0 * M_PI_VAL;
            p[idx].vx = v_rms * cos(angle);
            p[idx].vy = v_rms * sin(angle);
            idx++;
        }
    }
}

double step_simulation(Particle *p, int count, double lx, double ly, double mass, double dt) {
    double impulse_transferred = 0.0;

    for (int i = 0; i < count; i++) {
        // Оновлення координат
        p[i].x += p[i].vx * dt;
        p[i].y += p[i].vy * dt;

        // Пружні зіткнення з вертикальними стінками (x = 0 та x = lx)
        if (p[i].x <= 0.0) {
            p[i].x = -p[i].x;
            impulse_transferred += 2.0 * mass * fabs(p[i].vx);
            p[i].vx = -p[i].vx;
        } else if (p[i].x >= lx) {
            p[i].x = 2.0 * lx - p[i].x;
            impulse_transferred += 2.0 * mass * fabs(p[i].vx);
            p[i].vx = -p[i].vx;
        }

        // Пружні зіткнення з горизонтальними стінками (y = 0 та y = ly)
        if (p[i].y <= 0.0) {
            p[i].y = -p[i].y;
            impulse_transferred += 2.0 * mass * fabs(p[i].vy);
            p[i].vy = -p[i].vy;
        } else if (p[i].y >= ly) {
            p[i].y = 2.0 * ly - p[i].y;
            impulse_transferred += 2.0 * mass * fabs(p[i].vy);
            p[i].vy = -p[i].vy;
        }
    }
    return impulse_transferred;
}

int main(void) {
    srand((unsigned int)time(NULL));

    GasSimConfig cfg = {
        .lx = 10.0,
        .ly = 10.0,
        .particle_mass = 4.0e-26, // Маса атома гелію (кг)
        .kb = 1.380649e-23,        // Стала Больцмана
        .num_particles = 1000
    };

    double target_temp = 300.0; // 300 К
    double dt = 1.0e-5;
    int total_steps = 100000;

    Particle *particles = (Particle *)malloc(sizeof(Particle) * (size_t)cfg.num_particles);
    if (!particles) {
        fprintf(stderr, "Помилка виділення пам'яті\n");
        return 1;
    }

    init_particles(particles, cfg.num_particles, cfg.lx, cfg.ly, target_temp, cfg.particle_mass, cfg.kb);

    double total_impulse = 0.0;
    for (int step = 0; step < total_steps; step++) {
        total_impulse += step_simulation(particles, cfg.num_particles, cfg.lx, cfg.ly, cfg.particle_mass, dt);
    }

    // Обчислення виміряної кінетичної енергії та температури
    double sum_v_sq = 0.0;
    for (int i = 0; i < cfg.num_particles; i++) {
        sum_v_sq += particles[i].vx * particles[i].vx + particles[i].vy * particles[i].vy;
    }
    double mean_v_sq = sum_v_sq / cfg.num_particles;
    double t_sim = (cfg.particle_mass * mean_v_sq) / (2.0 * cfg.kb);

    // Периметр та площа 2D посудини
    double perimeter = 2.0 * (cfg.lx + cfg.ly);
    double area = cfg.lx * cfg.ly;
    double total_time = total_steps * dt;

    // Макроскопічний тиск: Сила / Довжина стінок
    double p_sim = total_impulse / (perimeter * total_time);

    // Коефіцієнт стискуваності Z = (P * V) / (N * k_B * T)
    double z_factor = (p_sim * area) / (cfg.num_particles * cfg.kb * t_sim);

    printf("=== Результати чисельного моделювання ідеального газу ===\n");
    printf("Кількість частинок N : %d\n", cfg.num_particles);
    printf("Задана температура T0: %.2f K\n", target_temp);
    printf("Виміряна темп. T_sim : %.2f K\n", t_sim);
    printf("Розрахований тиск P  : %.6e Па·м\n", p_sim);
    printf("Коефіцієнт Z (PV/NkT): %.4f (Теорія: 1.0000)\n", z_factor);

    free(particles);
    return 0;
}
