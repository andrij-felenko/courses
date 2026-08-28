#include <math.h>

#define TRACK_WIDTH_M   0.185f    // L: колія, м
#define STRAIGHT_EPS    1e-4f     // поріг |Δθ|, нижче якого крок вважаємо прямим

typedef struct { float x, y, theta; } pose_t;

// ds_left, ds_right — пройдений шлях кожного колеса за крок, м
void odometry_update_exact(pose_t *p, float ds_left, float ds_right)
{
    float ds     = 0.5f * (ds_right + ds_left);           // крок уперед
    float dtheta = (ds_right - ds_left) / TRACK_WIDTH_M;  // приріст курсу

    if (fabsf(dtheta) < STRAIGHT_EPS) {
        // Майже пряма: дуга виродилась, беремо прямий крок за поточним курсом
        p->x += ds * cosf(p->theta);
        p->y += ds * sinf(p->theta);
    } else {
        // Точна дуга: радіус R = ds/dtheta, зсув по хорді через кути кінців
        float R  = ds / dtheta;
        float th2 = p->theta + dtheta;
        p->x += R * (sinf(th2)  - sinf(p->theta));
        p->y += R * (cosf(p->theta) - cosf(th2));
    }
    p->theta += dtheta;

    // Тримати курс у (−π, π]
    if (p->theta >  (float)M_PI) p->theta -= 2.0f * (float)M_PI;
    if (p->theta <= -(float)M_PI) p->theta += 2.0f * (float)M_PI;
}
