#ifndef SAFETY_ARBITER_H
#define SAFETY_ARBITER_H

#include <stdbool.h>
#include <stdint.h>

/* Такт арбітра: 10 мс (100 Гц). Уся часова логіка міряється в тактах —
   на мікроконтролері це дешевше й детермінованіше за роботу з годинником. */
#define SAFETY_DT_SEC        0.010f

/* Скільки тактів поспіль перешкода має триматися за порогом,
   щоб дозволити повернення в менш небезпечну зону (200 мс). */
#define SAFETY_HOLD_TICKS    20u

/* Просторовий гістерезис деескалації, м. */
#define SAFETY_HYST_DIST_M   0.30f

/* Поріг сторожа планувальника = множник × очікуваний період планувальника.
   Менше 2.0 — і джитер USB-CDC чи завантаженого CAN дає хибні спрацювання. */
#define SAFETY_WATCHDOG_K    2.5f

typedef enum {
    ZONE_OBSERVATION = 0,  /* вільний рух за глобальним планом */
    ZONE_WARNING,          /* змішування векторів і гальмування */
    ZONE_ESTOP             /* аварійне переривання, повний стоп */
} SafetyZone;

/* Усі вектори арбітра — у зв'язаній системі координат апарата (body frame).
   Змішувати odom із body заборонено: див. пастку «неузгодженість фреймів». */
typedef struct {
    float x;
    float y;
} Vec2;

/* Поворот вектора з odom у body на кут курсу yaw.
   Зворотний перехід — той самий виклик із -yaw. */
Vec2 safety_odom_to_body(Vec2 v, float yaw_rad);

typedef struct {
    float max_accel;      /* гарантоване сповільнення на покритті, м/с² */
    float reaction_time;  /* затримка силового тракту, с */
    float planner_period; /* очікуваний період планувальника, с */
    float stop_margin;    /* геометричний зазор зупинки, м */
    float warn_buffer;    /* простір на бічний маневр, м */
} SafetyParams;

typedef struct {
    Vec2  v_plan;        /* бажаний вектор від планувальника, body */
    Vec2  v_react;       /* вектор ухиляння від рефлексу, body */
    float min_range_m;   /* мінімальна дальність по променях далекоміра */
    bool  range_valid;   /* false = давач не дав валідних даних цього такту */
    float current_speed; /* модуль поточної швидкості апарата, м/с */
} SafetyInput;

typedef struct {
    Vec2       v_cmd;             /* фінальна уставка, body */
    SafetyZone zone;
    float      alpha;             /* частка реактивного вектора, 0…1 */
    float      r_stop;            /* динамічна межа зони стопу, м */
    float      r_warn;            /* динамічна межа зони застереження, м */
    float      v_safe;            /* кінематична стеля швидкості зближення */
    bool       override_active;   /* сигнал регулятору скинути I-складову */
    bool       planner_timed_out; /* сторож планувальника спрацював */
} SafetyOutput;

typedef struct {
    SafetyParams params;
    SafetyZone   current_zone;
    uint32_t     hold_counter;
    uint32_t     planner_watchdog;
    uint32_t     watchdog_limit;
    Vec2         last_cmd_vel;
    bool         planner_timed_out;
} SafetyArbiter;

/* Повертає false, якщо параметри непридатні (нульове сповільнення, NaN тощо).
   Арбітр із такими числами порахував би межу зони як нескінченність. */
bool safety_arbiter_init(SafetyArbiter *arb, const SafetyParams *params);

/* Викликати на кожному пакеті від планувальника — скидає сторожа. */
void safety_arbiter_planner_heartbeat(SafetyArbiter *arb);

/* Один такт арбітражу. Викликається строго з періодом SAFETY_DT_SEC. */
SafetyOutput safety_arbiter_update(SafetyArbiter *arb, const SafetyInput *in);

const char *safety_zone_name(SafetyZone zone);

#endif /* SAFETY_ARBITER_H */
