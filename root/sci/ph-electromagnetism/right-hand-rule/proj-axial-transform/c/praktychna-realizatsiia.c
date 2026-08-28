#include <stdio.h>
#include <stdbool.h>

typedef enum {
    VECTOR_POLAR = 0,
    VECTOR_AXIAL = 1
} VectorType;

typedef struct {
    double x;
    double y;
    double z;
    VectorType type;
} Vector3;

typedef struct {
    double m[3][3];
} Matrix3x3;

Vector3 vector3_create(double x, double y, double z, VectorType type) {
    Vector3 v = {x, y, z, type};
    return v;
}

double matrix3x3_determinant(const Matrix3x3* mat) {
    const double (*m)[3] = mat->m;
    return m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1])
         - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0])
         + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0]);
}

Vector3 vector3_cross(const Vector3* a, const Vector3* b) {
    double cx = a->y * b->z - a->z * b->y;
    double cy = a->z * b->x - a->x * b->z;
    double cz = a->x * b->y - a->y * b->x;

    /* Полярний × Полярний = Аксіальний; Полярний × Аксіальний = Полярний */
    VectorType result_type = (a->type == b->type) ? VECTOR_AXIAL : VECTOR_POLAR;
    return vector3_create(cx, cy, cz, result_type);
}

Vector3 vector3_transform(const Vector3* v, const Matrix3x3* mat) {
    const double (*m)[3] = mat->m;
    double rx = m[0][0] * v->x + m[0][1] * v->y + m[0][2] * v->z;
    double ry = m[1][0] * v->x + m[1][1] * v->y + m[1][2] * v->z;
    double rz = m[2][0] * v->x + m[2][1] * v->y + m[2][2] * v->z;

    if (v->type == VECTOR_AXIAL) {
        double det = matrix3x3_determinant(mat);
        rx *= det;
        ry *= det;
        rz *= det;
    }

    return vector3_create(rx, ry, rz, v->type);
}

void vector3_print(const char* label, const Vector3* v) {
    const char* type_str = (v->type == VECTOR_POLAR) ? "Полярний" : "Аксіальний";
    printf("%s [%s]: (%.2f, %.2f, %.2f)\n", label, type_str, v->x, v->y, v->z);
}

int main(void) {
    /* Вектор швидкості v (полярний) та магнітної індукції B (аксіальний) */
    Vector3 v = vector3_create(1.0, 2.0, 3.0, VECTOR_POLAR);
    Vector3 B = vector3_create(0.0, 0.0, 5.0, VECTOR_AXIAL);

    vector3_print("Початковий v", &v);
    vector3_print("Початкове B", &B);

    /* Обчислення сили Лоренца F = q (v × B), q = 1.0 */
    Vector3 F = vector3_cross(&v, &B);
    vector3_print("Сила Лоренца F = v × B", &F);

    /* Матриця просторової інверсії (дзеркальне віддзеркалення осей, det = -1) */
    Matrix3x3 inv_mat = {{{-1.0,  0.0,  0.0},
                          { 0.0, -1.0,  0.0},
                          { 0.0,  0.0, -1.0}}};

    printf("\n--- Трансформація при інверсії координат (det = -1) ---\n");
    Vector3 v_prime = vector3_transform(&v, &inv_mat);
    Vector3 B_prime = vector3_transform(&B, &inv_mat);
    Vector3 F_prime = vector3_transform(&F, &inv_mat);

    vector3_print("Трансформований v'", &v_prime);
    vector3_print("Трансформоване B'", &B_prime);
    vector3_print("Трансформована F'", &F_prime);

    /* Перевірка сили Лоренца у новій системі координат F_calc = v' × B' */
    Vector3 F_recalc = vector3_cross(&v_prime, &B_prime);
    vector3_print("Обчислена F_recalc = v' × B'", &F_recalc);

    return 0;
}
