#include <math.h>
#include <stdio.h>

#define DEG 0.017453292519943295    /* градус у радіанах */

typedef struct {
    double fx, fy, cx, cy;          /* внутрішні параметри, пікселі */
    double k1, k2, k3, p1, p2;      /* дисторсія, у нормованих координатах */
} Camera;

typedef struct { double roll, pitch, yaw; } Euler;   /* радіани, порядок Z-Y-X */

typedef struct {
    double u, v;        /* піксель, куди навів оператор */
    Camera cam;         /* калібрування об'єктива */
    Euler  body;        /* AHRS: корпус відносно «північ, схід, вниз» */
    Euler  gimbal;      /* енкодери підвісу: камера відносно корпуса */
    Euler  bore;        /* вивірка: сталий залишок в осях камери */
    double lat0, lon0;  /* радіани — фазовий центр антени GNSS */
    double h0;          /* метри над ЕЛІПСОЇДОМ, не над рівнем моря */
    double lever[3];    /* антена → камера в осях корпуса: вперед, праворуч, вниз */
} Shot;
