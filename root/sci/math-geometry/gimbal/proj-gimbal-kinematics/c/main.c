#include <math.h>
#include <stdbool.h>

#define GIMBAL_PI 3.14159265358979323846f
#define GIMBAL_PITCH_LIMIT (88.0f * GIMBAL_PI / 180.0f)

typedef struct {
    float x;
    float y;
    float z;
} Vec3;

typedef struct {
    float m[3][3];
} Mat3;

typedef struct {
    float yaw;    /* ψ навколо Z, радіани */
    float pitch;  /* θ навколо Y, радіани */
    float roll;   /* φ навколо X, радіани */
} GimbalAngles;

/* Нормалізація тривимірного вектора */
Vec3 vec3_normalize(Vec3 v) {
    float norm = sqrtf(v.x * v.x + v.y * v.y + v.z * v.z);
    if (norm < 1e-6f) {
        Vec3 zero = {1.0f, 0.0f, 0.0f};
        return zero;
    }
    Vec3 r = {v.x / norm, v.y / norm, v.z / norm};
    return r;
}

/* Транспонування матриці (для ортогональних матриць Rᵀ = R⁻¹) */
Mat3 mat3_transpose(const Mat3* a) {
    Mat3 r;
    for (int i = 0; i < 3; ++i) {
        for (int j = 0; j < 3; ++j) {
            r.m[i][j] = a->m[j][i];
        }
    }
    return r;
}

/* Множення двох матриць 3x3: R = A · B */
Mat3 mat3_mul(const Mat3* a, const Mat3* b) {
    Mat3 r;
    for (int i = 0; i < 3; ++i) {
        for (int j = 0; j < 3; ++j) {
            r.m[i][j] = a->m[i][0] * b->m[0][j] +
                        a->m[i][1] * b->m[1][j] +
                        a->m[i][2] * b->m[2][j];
        }
    }
    return r;
}

/* Множення матриці 3x3 на вектор: v_out = M · v_in */
Vec3 mat3_mul_vec(const Mat3* m, Vec3 v) {
    Vec3 r;
    r.x = m->m[0][0] * v.x + m->m[0][1] * v.y + m->m[0][2] * v.z;
    r.y = m->m[1][0] * v.x + m->m[1][1] * v.y + m->m[1][2] * v.z;
    r.z = m->m[2][0] * v.x + m->m[2][1] * v.y + m->m[2][2] * v.z;
    return r;
}

/* Побудова матриці підвісу за кутами Z-Y-X: R = Rz(ψ) · Ry(θ) · Rx(φ) */
Mat3 gimbal_angles_to_matrix(GimbalAngles a) {
    float cy = cosf(a.yaw),   sy = sinf(a.yaw);
    float cp = cosf(a.pitch), sp = sinf(a.pitch);
    float cr = cosf(a.roll),  sr = sinf(a.roll);

    Mat3 r;
    r.m[0][0] = cy * cp;
    r.m[0][1] = cy * sp * sr - sy * cr;
    r.m[0][2] = cy * sp * cr + sy * sr;

    r.m[1][0] = sy * cp;
    r.m[1][1] = sy * sp * sr + cy * cr;
    r.m[1][2] = sy * sp * cr - cy * sr;

    r.m[2][0] = -sp;
    r.m[2][1] = cp * sr;
    r.m[2][2] = cp * cr;
    return r;
}

/* Витягнення кутів Z-Y-X із матриці обертання з обробкою сингулярності */
bool gimbal_matrix_to_angles(const Mat3* r, GimbalAngles* out) {
    float sp = -r->m[2][0];
    if (sp > 1.0f) sp = 1.0f;
    if (sp < -1.0f) sp = -1.0f;

    out->pitch = asinf(sp);

    /* Перевірка наближення до карданового замка */
    if (fabsf(out->pitch) > GIMBAL_PITCH_LIMIT) {
        /* При pitch ≈ ±90° yaw і roll зливаються: фіксуємо roll = 0 */
        out->roll = 0.0f;
        out->yaw = atan2f(-r->m[0][1], r->m[1][1]);
        return false; /* Повідомляємо про сингулярний стан */
    }

    out->roll = atan2f(r->m[2][1], r->m[2][2]);
    out->yaw = atan2f(r->m[1][0], r->m[0][0]);
    return true;
}

/* Пряма кінематика: обчислення напрямку погляду камери у світовій рамці */
Vec3 gimbal_forward_kinematics(const Mat3* r_body, GimbalAngles g_angles) {
    Mat3 r_gimbal = gimbal_angles_to_matrix(g_angles);
    Mat3 r_cam = mat3_mul(r_body, &r_gimbal);
    Vec3 cam_forward = {1.0f, 0.0f, 0.0f};
    return mat3_mul_vec(&r_cam, cam_forward);
}

/* Зворотна кінематика: розрахунок кутів підвісу для наведення на цільовий вектор */
GimbalAngles gimbal_inverse_targeting(const Mat3* r_body, Vec3 target_world) {
    Mat3 r_body_t = mat3_transpose(r_body);
    Vec3 v_target_norm = vec3_normalize(target_world);
    
    /* Переведення вектора цілі в систему координат корпусу */
    Vec3 v_body = mat3_mul_vec(&r_body_t, v_target_norm);

    GimbalAngles angles;
    angles.yaw = atan2f(v_body.y, v_body.x);
    
    float hyp = sqrtf(v_body.x * v_body.x + v_body.y * v_body.y);
    angles.pitch = atan2f(-v_body.z, hyp);
    
    /* Для наведення оптичної осі крен утримується нульовим (горизонт) */
    angles.roll = 0.0f;

    /* Обмеження тангажу безпечною робочою зоною */
    if (angles.pitch > GIMBAL_PITCH_LIMIT) angles.pitch = GIMBAL_PITCH_LIMIT;
    if (angles.pitch < -GIMBAL_PITCH_LIMIT) angles.pitch = -GIMBAL_PITCH_LIMIT;

    return angles;
}

/* Компенсація орієнтації: розрахунок кутів підвісу за бажаною матрицею камери */
GimbalAngles gimbal_stabilize_attitude(const Mat3* r_body, const Mat3* r_desired) {
    Mat3 r_body_t = mat3_transpose(r_body);
    Mat3 r_gimbal = mat3_mul(&r_body_t, r_desired);
    
    GimbalAngles angles;
    gimbal_matrix_to_angles(&r_gimbal, &angles);
    return angles;
}
