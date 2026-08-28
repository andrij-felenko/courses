#include <stdio.h>
#include <stdbool.h>

typedef enum {
    MOTOR_TYPE_BDC,
    MOTOR_TYPE_STEPPER,
    MOTOR_TYPE_BLDC,
    MOTOR_TYPE_SERVO
} MotorType;

typedef struct {
    MotorType type;
    double max_torque_nm;      // Максимальний паспортний момент
    double max_speed_rpm;      // Максимальна кутова швидкість
    double rated_current_a;    // Номінальний струм фази
    double resistance_ohm;     // Опір обмотки
    double thermal_r_c_per_w;  // Тепловий опір корпус-середовище (°C/Вт)
} MotorSpecs;

typedef struct {
    double load_torque_nm;
    double load_inertia_kgm2;
    double target_speed_rpm;
    double accel_time_s;
    double ambient_temp_c;
} MotionTask;

bool verify_motor_selection(const MotorSpecs* m, const MotionTask* task, double* out_peak_torque, double* out_temp_c) {
    double rad_per_s = task->target_speed_rpm * (2.0 * 3.1415926535 / 60.0);
    double alpha = rad_per_s / task->accel_time_s;
    
    // Динамічний момент T = T_load + J * alpha
    double t_dynamic = task->load_torque_nm + (task->load_inertia_kgm2 * alpha);
    *out_peak_torque = t_dynamic;

    // Перевірка запасу по моменту
    double safety_factor = (m->type == MOTOR_TYPE_STEPPER) ? 2.0 : 1.3;
    if (t_dynamic * safety_factor > m->max_torque_nm) {
        return false; // Ризик зриву кроків або заклинювання
    }

    if (task->target_speed_rpm > m->max_speed_rpm) {
        return false; // Перевищення межі швидкості
    }

    // Тепловий розрахунок втрат P = I^2 * R
    double i_effective = m->rated_current_a;
    if (m->type == MOTOR_TYPE_BDC) {
        i_effective *= (t_dynamic / m->max_torque_nm);
    }
    
    double p_heat = i_effective * i_effective * m->resistance_ohm;
    if (m->type == MOTOR_TYPE_STEPPER) {
        p_heat *= 2.0; // Дві фази під струмом
    } else if (m->type == MOTOR_TYPE_BLDC) {
        p_heat *= 1.5; // Три фази в режимі FOC
    }

    *out_temp_c = task->ambient_temp_c + (p_heat * m->thermal_r_c_per_w);
    return (*out_temp_c < 105.0); // Межа температури ізоляції
}
