#include <stdint.h>
#include <stdbool.h>
#include <math.h>
#include <stdlib.h>
#include <string.h>

// Внутрішні параметри камери
typedef struct {
    double fx;      // фокусна відстань за віссю X (у пікселях)
    double fy;      // фокусна відстань за віссю Y (у пікселях)
    double cx;      // координата X головної точки (оптичного центру)
    double cy;      // координата Y головної точки (оптичного центру)
} CameraIntrinsics;

// Коефіцієнти дисторсії Брауна–Конраді
typedef struct {
    double k1, k2, k3;  // радіальна дисторсія
    double p1, p2;      // тангенціальна дисторсія
} DistortionCoeffs;

// Двовимірна точка
typedef struct {
    double x, y;
} Point2D;

// Тривимірна точка
typedef struct {
    double x, y, z;
} Point3D;
