#include <math.h>

// Геометрія робота — з креслення шасі
#define TRACK_WIDTH_M   0.185f   // L: відстань між колесами, м

typedef struct {
    float x;      // координата середини осі, м
    float y;      // координата середини осі, м
    float theta;  // курс, рад (0 = уздовж осі X світу)
} pose_t;

// ds_left, ds_right — пройдений шлях кожного колеса за цей цикл, м
// dt — тривалість циклу, с (для швидкостей)
void odometry_update(pose_t *p, float ds_left, float ds_right, float dt,
                     float *v_out, float *w_out)
{
    // Пряма кінематика в приростах шляху
    float ds     = 0.5f * (ds_right + ds_left);          // крок уперед
    float dtheta = (ds_right - ds_left) / TRACK_WIDTH_M; // приріст курсу

    // Проєкція кроку в світові координати за ПОТОЧНИМ курсом
    p->x     += ds * cosf(p->theta);
    p->y     += ds * sinf(p->theta);
    p->theta += dtheta;

    // Тримати курс у діапазоні (−π, π], щоб він не ріс без меж
    if (p->theta >  (float)M_PI) p->theta -= 2.0f * (float)M_PI;
    if (p->theta <= -(float)M_PI) p->theta += 2.0f * (float)M_PI;

    // Принагідно — фактичні швидкості корпуса для верхнього контуру
    *v_out = ds     / dt;   // м/с
    *w_out = dtheta / dt;   // рад/с
}
