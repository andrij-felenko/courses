#include <math.h>

typedef struct { double cx, cy; double px_per_rad_x, px_per_rad_y; } cam_geom;

/* Деформація одного кадру: куди показаний піксель лягає у знятому.
   shift_x/shift_y — зсув вікна (пікс.), roll — кут повороту (рад). */
typedef struct { double shift_x, shift_y, roll; } warp;

static warp warp_for_frame(const att *a, const cam_geom *c)
{
    warp w;
    w.shift_x = -a->ay * c->px_per_rad_x;   /* рискання → горизонтальний зсув */
    w.shift_y = -a->ax * c->px_per_rad_y;   /* тангаж  → вертикальний зсув */
    w.roll    = -a->az;                      /* крен    → поворот навколо центра */
    return w;
}

/* Зворотне відображення: показаний піксель (xd,yd) → точка (sx,sy) у знятому
   кадрі, звідки взяти колір. Повертаємо й зсуваємо навколо центра. */
static void sample_src(const warp *w, const cam_geom *c,
                       double xd, double yd, double *sx, double *sy)
{
    double ca = cos(w->roll), sa = sin(w->roll);
    double ox = xd - c->cx, oy = yd - c->cy;       /* у координати від центра */
    double rx = ca * ox - sa * oy;                  /* поворот на roll */
    double ry = sa * ox + ca * oy;
    *sx = c->cx + rx + w->shift_x;                  /* назад + зсув вікна */
    *sy = c->cy + ry + w->shift_y;
}
