#ifndef MOTOR_H
#define MOTOR_H

#include <stdbool.h>

/* Модель приводу: паспорт мотора, редуктор і вся фізика, яку з них рахують —
   доступний момент на швидкості, струм під моментом, мідні втрати й нагрів. */

typedef enum {
    MOTOR_BDC = 0,   /* колекторний: комутація щітками */
    MOTOR_STEPPER,   /* кроковий: дві фази, чоппер тримає струм */
    MOTOR_BLDC,      /* безколекторний із векторним керуванням */
    MOTOR_SERVO      /* інтегрований сервопривід: паспорт уже на вихідному валу */
} MotorFamily;

typedef struct {
    const char *name;
    MotorFamily family;
    double rated_torque_nm;       /* тривалий момент; у крокового — момент утримання */
    double no_load_speed_rpm;     /* холостий хід (BDC) або паспортна межа обертів */
    double corner_speed_rpm;      /* кроковий: злам кривої моменту; BLDC: базова швидкість */
    double rated_current_a;       /* номінальний струм фази (амплітуда) */
    double phase_resistance_ohm;  /* активний опір обмотки */
    double rotor_inertia_kgm2;
    double thermal_r_c_per_w;     /* тепловий опір «обмотка — середовище» */
    double supply_v;
    double hold_current_frac;     /* кроковий у спокої: частка номіналу (standstill reduction) */
    double step_resolution_deg;   /* дискрет положення на валу; 0 — давача немає */
} MotorSpecs;

typedef struct {
    double ratio;         /* N = w_motor / w_load */
    double efficiency;    /* ККД передачі, 0 < eta <= 1 */
    double backlash_deg;  /* бічний зазор зубців на вихідному валу */
} Gearbox;

double rpm_to_rad_s(double rpm);
double rad_s_to_rpm(double rad_s);
const char *motor_family_name(MotorFamily family);

double motor_torque_constant(const MotorSpecs *m);              /* k_t = T / I, Н·м/А */
double motor_available_torque(const MotorSpecs *m, double omega_rad_s);
double motor_current_for_torque(const MotorSpecs *m, double torque_nm);
double motor_stall_current(const MotorSpecs *m);
double motor_copper_loss_w(const MotorSpecs *m, double torque_nm, bool standstill);
double motor_winding_temp_c(const MotorSpecs *m, double average_loss_w, double ambient_c);

double gearbox_reflect_torque(const Gearbox *g, double load_torque_nm);
double gearbox_reflect_inertia(const Gearbox *g, double load_inertia_kgm2);
double gearbox_heat_loss_w(const Gearbox *g, double output_power_w);

/* NULL — паспорт несуперечливий; інакше рядок із причиною. */
const char *motor_specs_problem(const MotorSpecs *m);
const char *gearbox_problem(const Gearbox *g);

#endif /* MOTOR_H */
