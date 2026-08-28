#include <stdio.h>
#include <stdbool.h>
#include <math.h>

typedef struct {
    double x, y, z;
} Vec3;

typedef struct {
    double m[4][4];
} Mat4;

typedef struct {
    Vec3 normal;   // Одиничний вектор нормалі до площини кришки (A, B, C)
    double d;      // Параметр рівняння площини: A*x + B*y + C*z + d = 0
} Plane;

typedef struct {
    Vec3 min_pt;   // Мінімальний кут обмежувального паралелепіпеда (Bounding Box)
    Vec3 max_pt;   // Максимальний кут обмежувального паралелепіпеда
} BoundingBox3D;

static Vec3 mat4_transform_point(const Mat4 *mat, Vec3 pt) {
    Vec3 res;
    res.x = mat->m[0][0] * pt.x + mat->m[0][1] * pt.y + mat->m[0][2] * pt.z + mat->m[0][3];
    res.y = mat->m[1][0] * pt.x + mat->m[1][1] * pt.y + mat->m[1][2] * pt.z + mat->m[1][3];
    res.z = mat->m[2][0] * pt.x + mat->m[2][1] * pt.y + mat->m[2][2] * pt.z + mat->m[2][3];
    return res;
}

static double point_to_plane_distance(const Plane *plane, Vec3 pt) {
    double numerator = plane->normal.x * pt.x + plane->normal.y * pt.y + plane->normal.z * pt.z + plane->d;
    double denominator = sqrt(plane->normal.x * plane->normal.x +
                              plane->normal.y * plane->normal.y +
                              plane->normal.z * plane->normal.z);
    return (denominator > 1e-9) ? (numerator / denominator) : 0.0;
}

static bool check_component_clearance(const BoundingBox3D *comp_bbox, const Mat4 *board_transform,
                                     const Plane *chassis_lid, double min_allowed_clearance,
                                     double *out_actual_clearance) {
    // 8 вершин обмежувального паралелепіпеда деталі в локальній системі координат плати
    Vec3 local_vertices[8] = {
        {comp_bbox->min_pt.x, comp_bbox->min_pt.y, comp_bbox->min_pt.z},
        {comp_bbox->max_pt.x, comp_bbox->min_pt.y, comp_bbox->min_pt.z},
        {comp_bbox->min_pt.x, comp_bbox->max_pt.y, comp_bbox->min_pt.z},
        {comp_bbox->max_pt.x, comp_bbox->max_pt.y, comp_bbox->min_pt.z},
        {comp_bbox->min_pt.x, comp_bbox->min_pt.y, comp_bbox->max_pt.z},
        {comp_bbox->max_pt.x, comp_bbox->min_pt.y, comp_bbox->max_pt.z},
        {comp_bbox->min_pt.x, comp_bbox->max_pt.y, comp_bbox->max_pt.z},
        {comp_bbox->max_pt.x, comp_bbox->max_pt.y, comp_bbox->max_pt.z}
    };

    double min_dist = 1e9;

    for (int i = 0; i < 8; ++i) {
        Vec3 world_pt = mat4_transform_point(board_transform, local_vertices[i]);
        double dist = point_to_plane_distance(chassis_lid, world_pt);
        if (dist < min_dist) {
            min_dist = dist;
        }
    }

    *out_actual_clearance = min_dist;
    return (min_dist >= min_allowed_clearance);
}

int main(void) {
    // Матриця розміщення плати в корпусі: встановлена на стійках H = 5.0 мм
    Mat4 board_to_chassis = {{
        {1.0, 0.0, 0.0, 0.0},
        {0.0, 1.0, 0.0, 0.0},
        {0.0, 0.0, 1.0, 5.0}, // Зсув по осі Z на 5.0 мм вгору від дна корпусу
        {0.0, 0.0, 0.0, 1.0}
    }};

    // Верхня кришка корпусу розташована на висоті Z = 22.0 мм: 0*x + 0*y + (-1)*z + 22.0 = 0
    Plane chassis_lid = {
        .normal = {0.0, 0.0, -1.0},
        .d = 22.0
    };

    // Габарити електролітичного конденсатора: основа 10x10 мм, висота H = 15.5 мм
    BoundingBox3D cap_bbox = {
        .min_pt = {40.0, 20.0, 0.0},
        .max_pt = {50.0, 30.0, 15.5}
    };

    double min_req_clearance = 1.0; // Мінімальний зазор безпеки 1.0 мм
    double actual_clearance = 0.0;

    bool passed = check_component_clearance(&cap_bbox, &board_to_chassis, &chassis_lid,
                                           min_req_clearance, &actual_clearance);

    printf("=================================================================\n");
    printf("   АНАЛІЗ ПРОСТОРОВОГО ЗАЗОРУ КОМПОНЕНТА (CLEARANCE CHECK)      \n");
    printf("=================================================================\n");
    printf("Висота стійок плати:                  %6.2f мм\n", board_to_chassis.m[2][3]);
    printf("Висота деталі над платою:             %6.2f мм\n", cap_bbox.max_pt.z);
    printf("Абсолютна координата верхівки Z:      %6.2f мм\n", board_to_chassis.m[2][3] + cap_bbox.max_pt.z);
    printf("Положення кришки корпусу Z:           %6.2f мм\n", chassis_lid.d);
    printf("-----------------------------------------------------------------\n");
    printf("Фактичний зазор до кришки:            %6.2f мм\n", actual_clearance);
    printf("Мінімально допустимий зазор:          %6.2f мм\n", min_req_clearance);
    printf("Статус перевірки:                     %s\n", passed ? "[PASS] В НОРМІ" : "[FAIL] КОЛІЗІЯ!");
    printf("=================================================================\n");

    return passed ? 0 : 1;
}
