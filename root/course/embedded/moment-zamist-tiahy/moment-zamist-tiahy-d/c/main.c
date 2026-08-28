#include <stdio.h>
#include <math.h>
#include <stdbool.h>

#define CONST_G 9.80665
#define CONST_PI 3.141592653589793

typedef struct {
    double mass_kg;
    double wheel_radius_m;
    int    drive_wheels;
    double crr;
    double mu_friction;
    double slope_degrees;
    double target_speed_mps;
    double target_accel_mps2;
    double safety_factor;
} ChassisSpec;

typedef struct {
    double gear_ratio;
    double gearbox_efficiency;
    double kv_rating;
    double phase_resistance;
    double rated_torque_nm;
    double stall_torque_nm;
} PowertrainSpec;

typedef struct {
    double total_traction_n;
    double wheel_torque_nm;
    double wheel_rpm;
    double motor_torque_nm;
    double motor_rpm;
    double motor_current_a;
    double mech_power_total_w;
    bool   traction_ok;
    bool   torque_ok;
} SizingSummary;

SizingSummary evaluate_powertrain(const ChassisSpec *ch, const PowertrainSpec *pt) {
    SizingSummary res;
    double theta = ch->slope_degrees * (CONST_PI / 180.0);
    
    // Розрахунок сил опору
    double f_rr    = ch->crr * ch->mass_kg * CONST_G * cos(theta);
    double f_slope = ch->mass_kg * CONST_G * sin(theta);
    double f_acc   = ch->mass_kg * 1.20 * ch->target_accel_mps2;
    res.total_traction_n = f_rr + f_slope + f_acc;
    
    // Момент і швидкість колеса
    double force_per_wheel = res.total_traction_n / ch->drive_wheels;
    res.wheel_torque_nm    = force_per_wheel * ch->wheel_radius_m * ch->safety_factor;
    double omega_wheel     = ch->target_speed_mps / ch->wheel_radius_m;
    res.wheel_rpm          = (omega_wheel * 60.0) / (2.0 * CONST_PI);
    
    // Параметри двигуна
    res.motor_torque_nm = res.wheel_torque_nm / (pt->gear_ratio * pt->gearbox_efficiency);
    res.motor_rpm       = res.wheel_rpm * pt->gear_ratio;
    
    double kt = 60.0 / (pt->kv_rating * 2.0 * CONST_PI);
    res.motor_current_a = res.motor_torque_nm / kt;
    
    double omega_motor = omega_wheel * pt->gear_ratio;
    res.mech_power_total_w = (res.motor_torque_nm * omega_motor) * ch->drive_wheels;
    
    // Перевірка обмежень
    double max_grip = ch->mu_friction * (ch->mass_kg * CONST_G * cos(theta) / ch->drive_wheels);
    res.traction_ok = (force_per_wheel <= max_grip);
    res.torque_ok   = (res.motor_torque_nm <= pt->rated_torque_nm);
    
    return res;
}

int main(void) {
    ChassisSpec ch = {
        .mass_kg = 16.0, .wheel_radius_m = 0.075, .drive_wheels = 4,
        .crr = 0.08, .mu_friction = 0.55, .slope_degrees = 20.0,
        .target_speed_mps = 1.5, .target_accel_mps2 = 0.75, .safety_factor = 1.30
    };
    
    PowertrainSpec pt = {
        .gear_ratio = 36.0, .gearbox_efficiency = 0.80, .kv_rating = 520.0,
        .phase_resistance = 0.32, .rated_torque_nm = 0.10, .stall_torque_nm = 0.42
    };
    
    SizingSummary s = evaluate_powertrain(&ch, &pt);
    
    printf("Тяга: %.2f Н | Момент колеса: %.3f Нм (%.0f RPM)\n", 
           s.total_traction_n, s.wheel_torque_nm, s.wheel_rpm);
    printf("Мотор: %.4f Нм (%.0f RPM) | Струм: %.2f А | Потужність: %.1f Вт\n",
           s.motor_torque_nm, s.motor_rpm, s.motor_current_a, s.mech_power_total_w);
    printf("Статус: Зчеплення: %s | Навантаження: %s\n", 
           s.traction_ok ? "OK" : "БУКСУВАННЯ", s.torque_ok ? "OK" : "ПЕРЕВАНТАЖЕННЯ");
    return 0;
}
