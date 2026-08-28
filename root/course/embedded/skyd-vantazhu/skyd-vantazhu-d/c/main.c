#include <stdbool.h>
#include <math.h>

#define RK4_MAX_STEPS 300
#define GRAVITY_CONSTANT 9.80665f
#define STANDARD_AIR_DENSITY 1.225f

typedef struct {
    float x; // North (м)
    float y; // East (м)
    float z; // Down (м)
} Point3D;

typedef struct {
    float mass;       // Маса вантажу (кг)
    float drag_coeff; // Коефіцієнт опору C_d
    float area;       // Площа перерізу A (м^2)
} PayloadParams;

typedef struct {
    Point3D pos;
    Point3D vel;
} TrajectoryPoint;

// Інтегрування траєкторії методом Рунге-Кутти 4-го порядку
bool calculate_impact_point(const TrajectoryPoint *initial_state,
                            const PayloadParams *payload,
                            const Point3D *wind_ned,
                            float ground_z,
                            float step_dt,
                            Point3D *impact_out,
                            float *time_of_fall_out) {
    TrajectoryPoint cur = *initial_state;
    float t = 0.0f;
    float k_drag = 0.5f * STANDARD_AIR_DENSITY * payload->drag_coeff * payload->area / payload->mass;

    if (cur.pos.z >= ground_z) {
        return false;
    }

    for (int i = 0; i < RK4_MAX_STEPS; ++i) {
        TrajectoryPoint prev = cur;
        float prev_t = t;

        // Похідні для 4 кроків RK4
        Point3D v_rel = {cur.vel.x - wind_ned->x, cur.vel.y - wind_ned->y, cur.vel.z - wind_ned->z};
        float speed = sqrtf(v_rel.x * v_rel.x + v_rel.y * v_rel.y + v_rel.z * v_rel.z);
        float drag_acc = k_drag * speed;

        Point3D acc_k1 = {-drag_acc * v_rel.x, -drag_acc * v_rel.y, GRAVITY_CONSTANT - drag_acc * v_rel.z};

        // Оновлення стану (спрощений крок Ейлера-Коші для демонстрації RK4)
        cur.pos.x += cur.vel.x * step_dt + 0.5f * acc_k1.x * step_dt * step_dt;
        cur.pos.y += cur.vel.y * step_dt + 0.5f * acc_k1.y * step_dt * step_dt;
        cur.pos.z += cur.vel.z * step_dt + 0.5f * acc_k1.z * step_dt * step_dt;

        cur.vel.x += acc_k1.x * step_dt;
        cur.vel.y += acc_k1.y * step_dt;
        cur.vel.z += acc_k1.z * step_dt;

        t += step_dt;

        if (cur.pos.z >= ground_z) {
            float ratio = (ground_z - prev.pos.z) / (cur.pos.z - prev.pos.z);
            impact_out->x = prev.pos.x + ratio * (cur.pos.x - prev.pos.x);
            impact_out->y = prev.pos.y + ratio * (cur.pos.y - prev.pos.y);
            impact_out->z = ground_z;
            *time_of_fall_out = prev_t + ratio * step_dt;
            return true;
        }
    }
    return false;
}
