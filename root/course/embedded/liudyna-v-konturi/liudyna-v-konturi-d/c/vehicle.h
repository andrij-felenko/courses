#ifndef VEHICLE_H
#define VEHICLE_H

#include <stdbool.h>

#include "pio.h"

/* Фізика однієї осі: I*d2(theta)/dt2 = M_кер + M_збур - b*d(theta)/dt */
typedef struct {
    float angle;       /* кут крену, рад */
    float rate;        /* кутова швидкість, рад/с */
    float inertia;     /* момент інерції, кг*м^2 */
    float damping;     /* в'язке тертя, Н*м*с */
    float torque_gain; /* ефективність моторів, Н*м на одиницю керування */
} Airframe;

void airframe_init(Airframe *a, float inertia, float damping, float torque_gain);
void airframe_step(Airframe *a, float control, float disturbance, float dt);

typedef enum { MODE_RATE, MODE_ANGLE } ControlMode;

/* Об'єкт очима оператора — те, під що людина підганяє власні параметри. */
typedef struct {
    float gain;        /* стік -> вихід об'єкта (рад/с або рад) */
    float lag_tc;      /* стала часу об'єкта, с */
    bool  integrating; /* стік задає ШВИДКІСТЬ: у контурі вільний інтегратор */
} ObjectDynamics;

typedef struct {
    ControlMode mode;
    float kp_angle;     /* зовнішній контур кута, 1/с */
    float kp_rate;      /* внутрішній контур кутової швидкості */
    float ki_rate;
    float max_rate;     /* повний хід стіка в режимі Rate, рад/с */
    float max_angle;    /* повний хід стіка в режимі Angle, рад */
    float torque_limit; /* насичення моторів, Н*м */
    float slew_limit;   /* максимум d(уставка)/dt, 1/с */
    bool  suppression;  /* динамічне демпфування стіка */
    float i_state;
    float setpoint;     /* уставка після згладжування фронту */
    float sens;         /* поточна чутливість пульта, 0.45…1.0 */
    PioMonitor stick_mon;
    int   steps;
    int   saturated;
} Autopilot;

void  autopilot_init(Autopilot *ap, ControlMode mode, float dt);
void  autopilot_enable_suppression(Autopilot *ap, bool on);
float autopilot_update(Autopilot *ap, float stick, const Airframe *a, float dt);
ObjectDynamics autopilot_object(const Autopilot *ap, const Airframe *a);
float autopilot_saturation(const Autopilot *ap);
float autopilot_sensitivity(const Autopilot *ap);

#endif /* VEHICLE_H */
