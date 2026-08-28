#include <stdio.h>
#include <stdbool.h>
#include <math.h>

typedef struct {
    double x;
    double y;
    double z;
} Vec3;

typedef struct {
    double N;           /* Навігаційний коефіцієнт (зазвичай 3.0 .. 4.5) */
    double a_max;       /* Максимальне нормальне прискорення [м/с^2] */
    double R_min;       /* Мінімальна дальність регуляризації [м] */
    double V_c_min;     /* Поріг швидкості зближення [м/с] */
    bool enable_apn;    /* Флаг компенсації прискорення цілі */
} PNConfig;

static inline Vec3 v_add(Vec3 a, Vec3 b) { return (Vec3){a.x + b.x, a.y + b.y, a.z + b.z}; }
static inline Vec3 v_sub(Vec3 a, Vec3 b) { return (Vec3){a.x - b.x, a.y - b.y, a.z - b.z}; }
static inline Vec3 v_mul(Vec3 a, double s) { return (Vec3){a.x * s, a.y * s, a.z * s}; }
static inline double v_dot(Vec3 a, Vec3 b) { return a.x * b.x + a.y * b.y + a.z * b.z; }
static inline double v_norm(Vec3 a) { return sqrt(v_dot(a, a)); }

static inline Vec3 v_cross(Vec3 a, Vec3 b) {
    return (Vec3){
        a.y * b.z - a.z * b.y,
        a.z * b.x - a.x * b.z,
        a.x * b.y - a.y * b.x
    };
}

static inline Vec3 v_clamp(Vec3 a, double max_len) {
    double len = v_norm(a);
    if (len > max_len && len > 1e-6) {
        return v_mul(a, max_len / len);
    }
    return a;
}

/**
 * @brief Розрахунок командного прискорення пропорційної навігації (True & Augmented PN).
 * 
 * @param cfg Параметри закону наведення
 * @param r_drone Позиція дрона в NED [м]
 * @param v_drone Швидкість дрона в NED [м/с]
 * @param r_target Оцінена позиція цілі в NED [м]
 * @param v_target Оцінена швидкість цілі в NED [м/с]
 * @param a_target Оцінене прискорення цілі в NED [м/с^2]
 * @return Vec3 Бажане векторне прискорення дрона [м/с^2]
 */
Vec3 compute_proportional_navigation(
    PNConfig cfg,
    Vec3 r_drone,
    Vec3 v_drone,
    Vec3 r_target,
    Vec3 v_target,
    Vec3 a_target
) {
    /* Вектор дальності R = r_t - r_d */
    Vec3 R_vec = v_sub(r_target, r_drone);
    double R = v_norm(R_vec);

    /* Захист від сингулярності на надмалих відстанях */
    if (R < cfg.R_min) {
        return (Vec3){0.0, 0.0, 0.0};
    }

    /* Одиничний вектор лінії візування e_los */
    Vec3 e_los = v_mul(R_vec, 1.0 / R);

    /* Вектор відносної швидкості V_r = v_t - v_d */
    Vec3 V_r = v_sub(v_target, v_drone);

    /* Швидкість зближення V_c = - (R · V_r) / ||R|| */
    double V_c = -v_dot(e_los, V_r);

    /* Захист від віддалення цілі (V_c <= 0) */
    if (V_c < cfg.V_c_min) {
        V_c = cfg.V_c_min;
    }

    /* Вектор кутової швидкості лінії візування: Ω = (R × V_r) / ||R||² */
    Vec3 cross_rv = v_cross(R_vec, V_r);
    Vec3 Omega = v_mul(cross_rv, 1.0 / (R * R));

    /* Базове командне прискорення TPN: a_pn = N * V_c * (Ω × e_los) */
    Vec3 omega_cross_los = v_cross(Omega, e_los);
    Vec3 a_cmd = v_mul(omega_cross_los, cfg.N * V_c);

    /* Компенсація прискорення маневру цілі (Augmented PN) */
    if (cfg.enable_apn) {
        Vec3 a_t_parallel = v_mul(e_los, v_dot(a_target, e_los));
        Vec3 a_t_perp = v_sub(a_target, a_t_parallel);
        Vec3 a_apn = v_mul(a_t_perp, cfg.N * 0.5);
        a_cmd = v_add(a_cmd, a_apn);
    }

    /* Обмеження максимального перевантаження */
    return v_clamp(a_cmd, cfg.a_max);
}
