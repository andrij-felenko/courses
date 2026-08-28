/* ============================================================================
 * Симулятор траєкторій частинок у токамаку (C11)
 * ============================================================================ */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

#define CONST_E  1.602176634e-19
#define CONST_AMU 1.6605390666e-27

typedef struct {
    double x, y, z;
} Vec3;

typedef struct {
    double R0;        /* Великий радіус токамака (м) */
    double a0;        /* Малий радіус плазми (м) */
    double B_tor0;    /* Тороїдальне поле на осі (Тл) */
    double B_pol0;    /* Полоїдальне поле на краю (Тл) */
    double mass;      /* Маса частинки (кг) */
    double charge;    /* Заряд частинки (Кл) */
} TokamakConfig;

static inline Vec3 vec3_add(Vec3 a, Vec3 b) {
    return (Vec3){a.x + b.x, a.y + b.y, a.z + b.z};
}

static inline Vec3 vec3_scale(Vec3 a, double s) {
    return (Vec3){a.x * s, a.y * s, a.z * s};
}

static inline Vec3 vec3_cross(Vec3 a, Vec3 b) {
    return (Vec3){
        a.y * b.z - a.z * b.y,
        a.z * b.x - a.x * b.z,
        a.x * b.y - a.y * b.x
    };
}

static inline double vec3_dot(Vec3 a, Vec3 b) {
    return a.x * b.x + a.y * b.y + a.z * b.z;
}

static inline double vec3_norm(Vec3 a) {
    return sqrt(vec3_dot(a, a));
}

/* Обчислення магнітного поля в точці (x, y, z) */
Vec3 get_magnetic_field(const TokamakConfig* cfg, Vec3 pos) {
    double R = sqrt(pos.x * pos.x + pos.y * pos.y);
    if (R < 1e-6) return (Vec3){0, 0, 0};
    
    double cos_phi = pos.x / R;
    double sin_phi = pos.y / R;
    double z = pos.z;
    double r_local = sqrt((R - cfg->R0) * (R - cfg->R0) + z * z);
    
    /* Тороїдальне поле: B_phi = B0 * (R0 / R) */
    double B_phi = cfg->B_tor0 * (cfg->R0 / R);
    double B_x_tor = -B_phi * sin_phi;
    double B_y_tor =  B_phi * cos_phi;
    
    /* Полоїдальне поле */
    double B_pol_mag = cfg->B_pol0 * (r_local / cfg->a0) * (cfg->R0 / R);
    double B_R_pol = (r_local > 1e-6) ? -B_pol_mag * (z / r_local) : 0.0;
    double B_z_pol = (r_local > 1e-6) ?  B_pol_mag * ((R - cfg->R0) / r_local) : 0.0;
    
    double B_x_pol = B_R_pol * cos_phi;
    double B_y_pol = B_R_pol * sin_phi;
    
    return (Vec3){
        B_x_tor + B_x_pol,
        B_y_tor + B_y_pol,
        B_z_pol
    };
}

/* Крок інтегрування методом Бориса */
void boris_step(const TokamakConfig* cfg, Vec3* pos, Vec3* vel, double dt) {
    Vec3 B = get_magnetic_field(cfg, *pos);
    double q_m = cfg->charge / cfg->mass;
    
    /* t_vector = (q*B/m) * (dt/2) */
    Vec3 t = vec3_scale(B, q_m * 0.5 * dt);
    double t_sq = vec3_dot(t, t);
    
    /* s_vector = 2*t / (1 + t^2) */
    Vec3 s = vec3_scale(t, 2.0 / (1.0 + t_sq));
    
    /* v' = v + v x t */
    Vec3 v_prime = vec3_add(*vel, vec3_cross(*vel, t));
    
    /* v+ = v + v' x s */
    Vec3 v_plus = vec3_add(*vel, vec3_cross(v_prime, s));
    
    *vel = v_plus;
    *pos = vec3_add(*pos, vec3_scale(*vel, dt));
}

int main(void) {
    TokamakConfig cfg = {
        .R0 = 1.65,
        .a0 = 0.50,
        .B_tor0 = 2.50,
        .B_pol0 = 0.25,
        .mass = 2.0 * CONST_AMU,  /* Дейтрон */
        .charge = CONST_E
    };
    
    /* Початкові умови: іон з енергією 3 кеВ */
    double E_eV = 3000.0;
    double v_total = sqrt(2.0 * E_eV * CONST_E / cfg.mass);
    double pitch_angle_deg = 70.0; /* високий пітч-кут -> заперта частинка */
    double pitch_rad = pitch_angle_deg * M_PI / 180.0;
    
    Vec3 pos = {cfg.R0 + 0.20, 0.0, 0.0};
    Vec3 vel = {
        0.0,
        v_total * cos(pitch_rad),
        v_total * sin(pitch_rad)
    };
    
    double dt = 1.0e-9; /* 1 нс крок */
    int steps = 100000;
    
    double R_min = 1e9, R_max = -1e9;
    
    printf("=== Симуляція руху іона в токамаку (C11) ===\n");
    printf("Початковий радіус: R = %.3f м, E = %.1f кеВ, pitch = %.1f deg\n",
           pos.x, E_eV / 1000.0, pitch_angle_deg);
           
    for (int i = 0; i < steps; ++i) {
        boris_step(&cfg, &pos, &vel, dt);
        double R = sqrt(pos.x * pos.x + pos.y * pos.y);
        if (R < R_min) R_min = R;
        if (R > R_max) R_max = R;
    }
    
    double banana_width = R_max - R_min;
    printf("Результат інтегрування (%d кроків):\n", steps);
    printf("  R_min = %.4f м, R_max = %.4f м\n", R_min, R_max);
    printf("  Ширина бананної орбіти Δr_b = %.2f см\n", banana_width * 100.0);
    printf("  Тип орбіти: %s\n", (banana_width > 0.05) ? "Заперта (бананна)" : "Пролітна");
    
    return 0;
}
