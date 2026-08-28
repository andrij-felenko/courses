#include <stdio.h>
#include <math.h>

#define MU_0 1.25663706212e-6  /* Гн/м — магнітна стала */
#define PI   3.14159265358979323846

typedef struct {
    double x, y, z;
} Vector3;

/* Скалярний добуток */
static inline double vec_dot(Vector3 a, Vector3 b) {
    return a.x * b.x + a.y * b.y + a.z * b.z;
}

/* Модуль вектора */
static inline double vec_norm(Vector3 v) {
    return sqrt(vec_dot(v, v));
}

/* Обчислення вектора магнітної індукції диполя */
Vector3 dipole_magnetic_field(Vector3 dipole_mu, Vector3 pos_r) {
    double r_len = vec_norm(pos_r);
    Vector3 B = {0.0, 0.0, 0.0};
    
    if (r_len < 1e-12) {
        /* Захист від сингулярності в центрі диполя */
        return B;
    }

    Vector3 r_hat = {pos_r.x / r_len, pos_r.y / r_len, pos_r.z / r_len};
    double mu_dot_rhat = vec_dot(dipole_mu, r_hat);
    double factor = (MU_0 / (4.0 * PI * r_len * r_len * r_len));

    B.x = factor * (3.0 * mu_dot_rhat * r_hat.x - dipole_mu.x);
    B.y = factor * (3.0 * mu_dot_rhat * r_hat.y - dipole_mu.y);
    B.z = factor * (3.0 * mu_dot_rhat * r_hat.z - dipole_mu.z);

    return B;
}

/* Симуляція траєкторії частинки у градієнтному полі (Штерн - Герлах) */
typedef struct {
    double z_pos;
    double z_vel;
} ParticleState;

ParticleState simulate_stern_gerlach_step(ParticleState current, double mu_z, 
                                           double mass, double dBz_dz, double dt) {
    ParticleState next;
    /* Сила F_z = mu_z * (dBz / dz) */
    double force_z = mu_z * dBz_dz;
    double accel_z = force_z / mass;

    /* Метод Ейлера — Кромера для збереження енергії */
    next.z_vel = current.z_vel + accel_z * dt;
    next.z_pos = current.z_pos + next.z_vel * dt;

    return next;
}

int main(void) {
    /* 1. Розрахунок поля диполя */
    Vector3 mu = {0.0, 0.0, 9.274e-24}; /* 1 магнетон Бора вздовж Z [А·м²] */
    Vector3 r  = {0.05, 0.0, 0.05};     /* 5 см по X, 5 см по Z */

    Vector3 B = dipole_magnetic_field(mu, r);
    printf("Поле диполя на r=(0.05, 0, 0.05) м:
");
    printf("  Bx = %.3e Тл
  By = %.3e Тл
  Bz = %.3e Тл

", B.x, B.y, B.z);

    /* 2. Моделювання розщеплення пучка атомів срібла */
    double mass_Ag = 1.79e-25;     /* Маса атома срібла [кг] */
    double mu_Ag_z = 9.274e-24;    /* Проекція спінового моменту [А·м²] */
    double dBz_dz  = 1000.0;       /* Градієнт поля [Тл/м] */
    double dt      = 1e-6;         /* Крок за часом [с] */

    ParticleState state_up   = {0.0, 0.0};
    ParticleState state_down = {0.0, 0.0};

    for (int step = 0; step < 100; ++step) {
        state_up   = simulate_stern_gerlach_step(state_up,   +mu_Ag_z, mass_Ag, dBz_dz, dt);
        state_down = simulate_stern_gerlach_step(state_down, -mu_Ag_z, mass_Ag, dBz_dz, dt);
    }

    printf("Відхилення атома срібла через 100 мкс:
");
    printf("  Спін вгору (+mu_z):  z = %+.3f мм, vz = %+.3f м/с
", state_up.z_pos * 1000.0, state_up.z_vel);
    printf("  Спін вниз  (-mu_z):  z = %+.3f мм, vz = %+.3f м/с
", state_down.z_pos * 1000.0, state_down.z_vel);

    return 0;
}
