#include <math.h>

/* Геометрія платформи */
typedef struct {
    double L;   /* Повна колісна база, м */
    double lr;  /* Відстань від задньої осі до CoM, м */
} ChassisGeometry;

/* Стан робота на площині */
typedef struct {
    double x;     /* Позиція X, м */
    double y;     /* Позиція Y, м */
    double theta; /* Курс, рад */
} Pose2D;

/* Один такт інтегрування позиції методом точної дуги */
void bicycle_integrate_step(
    Pose2D *pose,
    double v,
    double delta,
    double dt,
    const ChassisGeometry *geom)
{
    /* 1. Розрахунок кута зсуву швидкості beta */
    double beta = atan((geom->lr / geom->L) * tan(delta));

    /* 2. Розрахунок кутової швидкості обертання omega */
    double omega = (v / geom->L) * tan(delta) * cos(beta);
    double dtheta = omega * dt;

    /* 3. Оновлення координат залежно від наявності кривини */
    if (fabs(omega) > 1e-5) {
        double R = v / omega;
        double heading_start = pose->theta + beta;
        double heading_end = heading_start + dtheta;

        pose->x += R * (sin(heading_end) - sin(heading_start));
        pose->y += R * (cos(heading_start) - cos(heading_end));
    } else {
        /* Рух по прямій */
        double heading = pose->theta + beta;
        pose->x += v * cos(heading) * dt;
        pose->y += v * sin(heading) * dt;
    }

    pose->theta += dtheta;

    /* Нормалізація кута до діапазону [-pi, pi] */
    while (pose->theta > M_PI)  pose->theta -= 2.0 * M_PI;
    while (pose->theta < -M_PI) pose->theta += 2.0 * M_PI;
}
