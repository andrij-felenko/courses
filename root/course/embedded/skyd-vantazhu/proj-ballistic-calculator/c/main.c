#include <stdbool.h>
#include <math.h>

#define MAX_BALLISTIC_STEPS 300
#define GRAVITY_MSS 9.80665f
#define AIR_DENSITY_KG_M3 1.225f

typedef struct {
    float x; // North (м)
    float y; // East (м)
    float z; // Down (м, додатне значення — вниз)
} Vec3f;

typedef struct {
    float mass_kg;
    float cd;
    float area_m2;
} PayloadSpec;

typedef struct {
    Vec3f pos;
    Vec3f vel;
} KinematicState;

typedef struct {
    Vec3f wind_vel; // Швидкість вітру (North, East, Down = 0)
    float target_z; // Висота площини скиду / цілі (Down)
    float actuator_delay_s; // Затримка серво/соленоїда (с)
} EnvironmentParams;

typedef struct {
    Vec3f impact_pos;     // Точка торкання поверхні цілі
    Vec3f release_offset; // Вектор виносу скиду від точки скиду до цілі
    float time_of_fall_s; // Час падіння вантажу
    float ttr_s;          // Час до перетину лінії скиду (Time-to-Release)
    float dist_to_rel_m;  // Горизонтальна відстань до точки скиду
    bool  in_release_gate;// Чи перебуває апарат у вікні скиду
} CcrpResult;

static inline Vec3f vec3_add(Vec3f a, Vec3f b) {
    return (Vec3f){a.x + b.x, a.y + b.y, a.z + b.z};
}

static inline Vec3f vec3_sub(Vec3f a, Vec3f b) {
    return (Vec3f){a.x - b.x, a.y - b.y, a.z - b.z};
}

static inline Vec3f vec3_scale(Vec3f v, float k) {
    return (Vec3f){v.x * k, v.y * k, v.z * k};
}

static inline float vec3_norm(Vec3f v) {
    return sqrtf(v.x * v.x + v.y * v.y + v.z * v.z);
}

// Похідні стану для інтегратора: d(pos)/dt = vel, d(vel)/dt = g - drag_accel
static void state_derivative(const KinematicState *state, const PayloadSpec *spec,
                             const Vec3f *wind, KinematicState *deriv) {
    deriv->pos = state->vel;

    Vec3f v_rel = vec3_sub(state->vel, *wind);
    float speed_rel = vec3_norm(v_rel);

    // k_drag = (1/2) * rho * C_d * A / m
    float k_drag = 0.5f * AIR_DENSITY_KG_M3 * spec->cd * spec->area_m2 / spec->mass_kg;
    float drag_factor = k_drag * speed_rel;

    deriv->vel.x = -drag_factor * v_rel.x;
    deriv->vel.y = -drag_factor * v_rel.y;
    deriv->vel.z = GRAVITY_MSS - drag_factor * v_rel.z;
}

// Чисельне інтегрування траєкторії падіння вантажу методом RK4
bool ballistic_calculate_impact(const KinematicState *uav_state,
                                const PayloadSpec *spec,
                                const EnvironmentParams *env,
                                Vec3f *out_impact,
                                float *out_tof) {
    KinematicState cur = *uav_state;
    float dt = 0.05f;
    float t = 0.0f;

    if (cur.pos.z >= env->target_z) {
        return false; // БПЛА нижче або на рівні цілі
    }

    for (int step = 0; step < MAX_BALLISTIC_STEPS; ++step) {
        KinematicState prev = cur;
        float prev_t = t;

        // Рунге-Кутта 4-го порядку (RK4)
        KinematicState k1, k2, k3, k4, temp;

        state_derivative(&cur, spec, &env->wind_vel, &k1);

        temp.pos = vec3_add(cur.pos, vec3_scale(k1.pos, dt * 0.5f));
        temp.vel = vec3_add(cur.vel, vec3_scale(k1.vel, dt * 0.5f));
        state_derivative(&temp, spec, &env->wind_vel, &k2);

        temp.pos = vec3_add(cur.pos, vec3_scale(k2.pos, dt * 0.5f));
        temp.vel = vec3_add(cur.vel, vec3_scale(k2.vel, dt * 0.5f));
        state_derivative(&temp, spec, &env->wind_vel, &k3);

        temp.pos = vec3_add(cur.pos, vec3_scale(k3.pos, dt));
        temp.vel = vec3_add(cur.vel, vec3_scale(k3.vel, dt));
        state_derivative(&temp, spec, &env->wind_vel, &k4);

        cur.pos.x += (dt / 6.0f) * (k1.pos.x + 2.0f * k2.pos.x + 2.0f * k3.pos.x + k4.pos.x);
        cur.pos.y += (dt / 6.0f) * (k1.pos.y + 2.0f * k2.pos.y + 2.0f * k3.pos.y + k4.pos.y);
        cur.pos.z += (dt / 6.0f) * (k1.pos.z + 2.0f * k2.pos.z + 2.0f * k3.pos.z + k4.pos.z);

        cur.vel.x += (dt / 6.0f) * (k1.vel.x + 2.0f * k2.vel.x + 2.0f * k3.vel.x + k4.vel.x);
        cur.vel.y += (dt / 6.0f) * (k1.vel.y + 2.0f * k2.vel.y + 2.0f * k3.vel.y + k4.vel.y);
        cur.vel.z += (dt / 6.0f) * (k1.vel.z + 2.0f * k2.vel.z + 2.0f * k3.vel.z + k4.vel.z);

        t += dt;

        // Перевірка досягнення площини поверхні цілі
        if (cur.pos.z >= env->target_z) {
            float dz = cur.pos.z - prev.pos.z;
            float ratio = (fabsf(dz) > 1e-4f) ? (env->target_z - prev.pos.z) / dz : 1.0f;

            out_impact->x = prev.pos.x + ratio * (cur.pos.x - prev.pos.x);
            out_impact->y = prev.pos.y + ratio * (cur.pos.y - prev.pos.y);
            out_impact->z = env->target_z;
            *out_tof = prev_t + ratio * dt;
            return true;
        }
    }

    return false; // Вичерпано ліміт кроків інтегратора
}

// Розрахунок параметрів точки скиду CCRP
bool ccrp_evaluate(const KinematicState *uav,
                   const Vec3f *target_pos,
                   const PayloadSpec *spec,
                   const EnvironmentParams *env,
                   float gate_radius_m,
                   CcrpResult *res) {
    Vec3f impact;
    float tof = 0.0f;

    if (!ballistic_calculate_impact(uav, spec, env, &impact, &tof)) {
        return false;
    }

    res->impact_pos = impact;
    res->time_of_fall_s = tof;

    // Вектор балістичного зміщення від поточної точки БПЛА до розрахункового падіння
    res->release_offset = vec3_sub(impact, uav->pos);

    // Урахування апаратної затримки відкриття замка
    Vec3f actuator_lead = vec3_scale(uav->vel, env->actuator_delay_s);
    Vec3f total_lead = vec3_add(res->release_offset, actuator_lead);

    // Розрахункова точка, в якій має перебувати БПЛА для скиду
    Vec3f ideal_release_pos = (Vec3f){
        target_pos->x - total_lead.x,
        target_pos->y - total_lead.y,
        uav->pos.z
    };

    // Вектор відстані від БПЛА до точки скиду
    Vec3f to_release = vec3_sub(ideal_release_pos, uav->pos);
    float dist_h = sqrtf(to_release.x * to_release.x + to_release.y * to_release.y);
    res->dist_to_rel_m = dist_h;

    // Проекція швидкості на лінію до точки скиду
    float ground_speed = sqrtf(uav->vel.x * uav->vel.x + uav->vel.y * uav->vel.y);
    if (ground_speed > 0.5f) {
        float dot = (to_release.x * uav->vel.x + to_release.y * uav->vel.y) / ground_speed;
        res->ttr_s = dot / ground_speed;
    } else {
        res->ttr_s = 999.0f;
    }

    // Перевірка перебування у вікні скиду
    res->in_release_gate = (dist_h <= gate_radius_m) && (res->ttr_s >= -0.1f && res->ttr_s <= 0.15f);

    return true;
}

// Розрахунок зрізу тяги під час скидання 30–50% MTOW
float calculate_throttle_feedforward(float hover_throttle, float uav_mass_kg, float payload_mass_kg) {
    if (uav_mass_kg <= payload_mass_kg || uav_mass_kg <= 0.1f) {
        return hover_throttle;
    }
    float mass_ratio = (uav_mass_kg - payload_mass_kg) / uav_mass_kg;
    return hover_throttle * mass_ratio;
}
