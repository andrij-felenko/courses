#include <math.h>

typedef struct {
    double x, y;
} Vec2;

typedef struct {
    Vec2 p1, p2;     /* Кінці панелі */
    Vec2 cp;         /* Точка колокації */
    Vec2 normal;     /* Вектор нормалі */
    Vec2 tangent;    /* Вектор дотичної */
    double length;   /* Довжина відрізка */
} AirfoilPanel;

/* Обчислення швидкості, індукованої панеллю одиничної циркуляції */
void compute_induced_velocity(const AirfoilPanel *panel, double x, double y, double *u, double *v) {
    double dx = x - panel->p1.x;
    double dy = y - panel->p1.y;
    double ct = panel->tangent.x;
    double st = panel->tangent.y;

    double x_loc = dx * ct + dy * st;
    double y_loc = -dx * st + dy * ct;

    if (fabs(y_loc) < 1e-9 && x_loc >= 0.0 && x_loc <= panel->length) {
        *u = 0.0;
        *v = 0.0;
        return;
    }

    double r1_sq = x_loc * x_loc + y_loc * y_loc;
    double r2_sq = (x_loc - panel->length) * (x_loc - panel->length) + y_loc * y_loc;
    double th1 = atan2(y_loc, x_loc);
    double th2 = atan2(y_loc, x_loc - panel->length);

    double u_loc = -(1.0 / (2.0 * 3.141592653589793)) * (th2 - th1);
    double v_loc = (1.0 / (4.0 * 3.141592653589793)) * log(r2_sq / (r1_sq + 1e-15));

    *u = u_loc * ct - v_loc * st;
    *v = u_loc * st + v_loc * ct;
}
