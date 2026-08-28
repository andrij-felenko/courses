#include <stdio.h>
#include <stdbool.h>
#include <math.h>

#define PI 3.14159265358979323846
#define GRAVITY 9.80665

typedef struct {
    double mass_kg;             // Повна маса ровера з корисним вантажем
    double wheel_radius_m;      // Радіус колеса
    int    total_wheels;        // Загальна кількість коліс
    int    drive_wheels;        // Кількість тягових коліс (ведучих)
    double c_rr;                // Коефіцієнт опору коченню
    double mu_traction;         // Коефіцієнт зчеплення з поверхнею
    double slope_deg;           // Кут схилу в градусах
    double target_speed_mps;    // Максимальна робоча швидкість
    double target_accel_mps2;   // Лінійне прискорення розгону
    double safety_factor;       // Коефіцієнт інженерного запасу
} RoverChassisConfig;

typedef struct {
    double gear_ratio;          // Передавальне число редуктора i
    double gearbox_efficiency;  // ККД редуктора eta (0.0 .. 1.0)
    double kv_rpm_per_volt;     // Константа швидкості двигуна KV
    double phase_resistance_ohm;// Опір обмотки фази R
    double rated_torque_nm;     // Номінальний тривалий момент двигуна
    double stall_torque_nm;     // Пусковий / стопорний момент двигуна
    double thermal_res_c_per_w; // Тепловий опір корпус-середовище (°C/Вт)
    double max_winding_temp_c;  // Гранична температура ізоляції обмотки
    double ambient_temp_c;      // Температура навколишнього середовища
} MotorGearboxConfig;

typedef struct {
    double f_rr_n;
    double f_slope_n;
    double f_accel_n;
    double f_total_n;
    double t_wheel_nm;
    double t_motor_nm;
    double wheel_rpm;
    double motor_rpm;
    double p_mech_per_motor_w;
    double p_mech_total_w;
    double est_current_a;
    double copper_loss_w;
    double steady_temp_c;
    double max_grip_force_n;
    bool   torque_ok;
    bool   stall_margin_ok;
    bool   traction_ok;
    bool   thermal_ok;
} SizingResult;

SizingResult calculate_rover_drive(const RoverChassisConfig *chassis, 
                                  const MotorGearboxConfig *motor) {
    SizingResult res = {0};
    
    double theta_rad = chassis->slope_deg * (PI / 180.0);
    double cos_theta = cos(theta_rad);
    double sin_theta = sin(theta_rad);
    
    // 1. Розрахунок сил
    res.f_rr_n    = chassis->c_rr * chassis->mass_kg * GRAVITY * cos_theta;
    res.f_slope_n = chassis->mass_kg * GRAVITY * sin_theta;
    
    // Врахування еквівалентної інерції обертання (~1.20 для типових роверів)
    double rot_factor = 1.20;
    res.f_accel_n = chassis->mass_kg * rot_factor * chassis->target_accel_mps2;
    res.f_total_n = res.f_rr_n + res.f_slope_n + res.f_accel_n;
    
    // 2. Момент і швидкість колеса
    double force_per_wheel = res.f_total_n / chassis->drive_wheels;
    res.t_wheel_nm = force_per_wheel * chassis->wheel_radius_m * chassis->safety_factor;
    
    double omega_wheel = chassis->target_speed_mps / chassis->wheel_radius_m;
    res.wheel_rpm = (omega_wheel * 60.0) / (2.0 * PI);
    
    // 3. Вимоги до двигуна через редуктор
    res.t_motor_nm = res.t_wheel_nm / (motor->gear_ratio * motor->gearbox_efficiency);
    res.motor_rpm  = res.wheel_rpm * motor->gear_ratio;
    double omega_motor = omega_wheel * motor->gear_ratio;
    
    res.p_mech_per_motor_w = res.t_motor_nm * omega_motor;
    res.p_mech_total_w     = res.p_mech_per_motor_w * chassis->drive_wheels;
    
    // 4. Електричні втрати та температура
    double kt = 60.0 / (motor->kv_rpm_per_volt * 2.0 * PI);
    res.est_current_a = res.t_motor_nm / kt;
    
    res.copper_loss_w  = res.est_current_a * res.est_current_a * motor->phase_resistance_ohm;
    res.steady_temp_c  = motor->ambient_temp_c + (res.copper_loss_w * motor->thermal_res_c_per_w);
    
    // 5. Перевірка зчеплення з ґрунтом
    double normal_per_wheel = (chassis->mass_kg * GRAVITY * cos_theta) / chassis->total_wheels;
    res.max_grip_force_n    = chassis->mu_traction * normal_per_wheel;
    
    res.torque_ok       = (res.t_motor_nm <= motor->rated_torque_nm);
    res.stall_margin_ok = (res.t_motor_nm <= 0.70 * motor->stall_torque_nm);
    res.traction_ok     = (force_per_wheel <= res.max_grip_force_n);
    res.thermal_ok      = (res.steady_temp_c < motor->max_winding_temp_c);
    
    return res;
}

void print_sizing_report(const SizingResult *r) {
    printf("============================================================\n");
    printf("         ЗВІТ РОЗРАХУНКУ ПРИВОДУ РОВЕРА                    \n");
    printf("============================================================\n");
    printf("Сила опору коченню F_rr:      %7.2f Н\n", r->f_rr_n);
    printf("Сила подолання схилу F_slope:  %7.2f Н\n", r->f_slope_n);
    printf("Динамічна сила розгону F_acc: %7.2f Н\n", r->f_accel_n);
    printf("СУМАРНА ПОТРІБНА ТЯГА:        %7.2f Н\n", r->f_total_n);
    printf("------------------------------------------------------------\n");
    printf("Момент на 1 колесі:           %7.3f Н·м  (%5.1f RPM)\n", r->t_wheel_nm, r->wheel_rpm);
    printf("Потрібний момент мотора:      %7.4f Н·м  (%5.0f RPM)\n", r->t_motor_nm, r->motor_rpm);
    printf("Механічна потужність (1 двиг):%7.2f Вт\n", r->p_mech_per_motor_w);
    printf("Механічна потужність (сумарна):%6.2f Вт\n", r->p_mech_total_w);
    printf("------------------------------------------------------------\n");
    printf("Оціночний струм фази:         %7.2f А\n", r->est_current_a);
    printf("Теплові втрати в міді I²·R:   %7.2f Вт\n", r->copper_loss_w);
    printf("Стала температура обмотки:    %7.1f °C\n", r->steady_temp_c);
    printf("------------------------------------------------------------\n");
    printf("ПЕРЕВІРКИ БЕЗПЕКИ ТА ПРАЦЕЗДАТНОСТІ:\n");
    printf(" [ %s ] Номінальний момент мотора  (T_req <= T_rated)\n", r->torque_ok ? "OK" : "ПЕРЕВАНТАЖЕННЯ");
    printf(" [ %s ] Запас до стопора (>30%%)    (T_req <= 0.70*T_stall)\n", r->stall_margin_ok ? "OK" : "НЕБЕЗПЕКА СТОПОРА");
    printf(" [ %s ] Зчеплення з ґрунтом        (F_req <= F_grip_max)\n", r->traction_ok ? "OK" : "ПРОБУКСОВУВАННЯ");
    printf(" [ %s ] Тепловий режим обмотки     (T_steady < T_max)\n", r->thermal_ok ? "OK" : "ПЕРЕГРІВ");
    printf("============================================================\n");
}

int main(void) {
    RoverChassisConfig chassis = {
        .mass_kg           = 16.0,
        .wheel_radius_m    = 0.075,
        .total_wheels      = 4,
        .drive_wheels      = 4,
        .c_rr              = 0.08,
        .mu_traction       = 0.55,
        .slope_deg         = 20.0,
        .target_speed_mps  = 1.5,
        .target_accel_mps2 = 0.75,
        .safety_factor     = 1.25
    };
    
    MotorGearboxConfig motor = {
        .gear_ratio           = 36.0,
        .gearbox_efficiency   = 0.80,
        .kv_rpm_per_volt      = 520.0,
        .phase_resistance_ohm = 0.28,
        .rated_torque_nm      = 0.12,
        .stall_torque_nm      = 0.45,
        .thermal_res_c_per_w  = 2.4,
        .max_winding_temp_c   = 130.0,
        .ambient_temp_c       = 25.0
    };
    
    SizingResult res = calculate_rover_drive(&chassis, &motor);
    print_sizing_report(&res);
    
    return 0;
}
