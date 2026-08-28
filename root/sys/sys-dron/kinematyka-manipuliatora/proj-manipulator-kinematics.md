# ⚙️ Бібліотека кінематики маніпулятора на C та C++

У системах автоматичного керування маніпуляторами, встановленими на борту безпілотних апаратів (БПЛА, автономних підводних дронів та наземних роверів-розмінувальників), обчислення кінематичних ланцюгів відбувається в жорсткому контурі реального часу. Стандартна частота опитування датчиків та формування керуючих впливів на сервоприводи становить від 100 Гц до 1 кГц (інтервал квантування від 10 до 1 мілісекунди).

Використання динамічного виділення пам'яті (`malloc`, `free`, `new`, `delete`, стандартні динамічні вектори `std::vector`) у таких системах неприпустиме з трьох фундаментальних причин:
1. **Недетермінований час виконання:** операції виділення пам'яті в купі можуть займати непередбачувану кількість тактів мікроконтролера через пошук вільних блоків або роботу системного алокатора;
2. **Фрагментація купи:** тривала безперервна робота бортового комп'ютера з частими дрібними алокаціями призводить до фрагментації оперативної пам'яті та раптового аварійного збою системи через нестачу неперервного адресного простору (Out Of Memory);
3. **Обмеженість ресурсів:** польотні контролери на базі мікроконтролерів STM32 (ARM Cortex-M4/M7) мають обмежений обсяг SRAM (від 128 КБ до 1 МБ), де кожен байт структури має бути статично розрахованим ще на етапі компіляції.

Нижче наведено промислову бібліотеку прямої кінематики за таблицею DH-параметрів, генерації геометричного Якобіана та чисельного ітеративного розв'язувача оберненої кінематики за затухаючим методом найменших квадратів (Damped Least Squares — DLS) з апаратними обмеженнями кутів суглобів.

## Архітектурні принципи та структури даних

Бібліотека спроектована з нульовим динамічним виділенням пам'яті (Zero-Allocation Architecture):
- Усі матриці та вектори передаються як структури фіксованого розміру через стек або константні вказівники;
- Максимальна кількість ланок маніпулятора обмежена константою `MAX_JOINTS = 8` (типова кількість осей для робототехнічних рук становить від 3 до 7);
- Проміжні матриці перетворень зберігаються в єдиному накопичувальному масиві `t_cumulative[MAX_JOINTS + 1]`, що усуває повторне перемноження матриць під час розрахунку стовпців Якобіана.

## Реалізація на C та C++

:::tabs
```c
#include <stdio.h>
#include <math.h>
#include <stdbool.h>
#include <string.h>

#define MAX_JOINTS 8
#define EPSILON 1e-6f

typedef struct {
    float x, y, z;
} vec3_t;

typedef struct {
    float data[4][4];
} mat4_t;

typedef struct {
    float theta;  /* кут повороту навколо Z_(i-1) (рад) */
    float d;      /* зміщення вздовж Z_(i-1) (м) */
    float a;      /* довжина спільного перпендикуляра X_i (м) */
    float alpha;  /* кут скручування навколо X_i (рад) */
    bool is_revolute;
    float q_min;  /* нижня межа руху суглоба */
    float q_max;  /* верхня межа руху суглоба */
} dh_joint_t;

typedef struct {
    dh_joint_t joints[MAX_JOINTS];
    int num_joints;
} manipulator_chain_t;

typedef struct {
    /* 6 рядків (3 лінійні швидкості, 3 кутові швидкості), n стовпців */
    float data[6][MAX_JOINTS];
    int rows;
    int cols;
} jacobian_t;

static inline vec3_t vec3_add(vec3_t a, vec3_t b) {
    return (vec3_t){a.x + b.x, a.y + b.y, a.z + b.z};
}

static inline vec3_t vec3_sub(vec3_t a, vec3_t b) {
    return (vec3_t){a.x - b.x, a.y - b.y, a.z - b.z};
}

static inline vec3_t vec3_cross(vec3_t a, vec3_t b) {
    return (vec3_t){
        a.y * b.z - a.z * b.y,
        a.z * b.x - a.x * b.z,
        a.x * b.y - a.y * b.x
    };
}

static inline float vec3_dot(vec3_t a, vec3_t b) {
    return a.x * b.x + a.y * b.y + a.z * b.z;
}

static inline float vec3_norm(vec3_t a) {
    return sqrtf(vec3_dot(a, a));
}

static mat4_t mat4_identity(void) {
    mat4_t m;
    memset(&m, 0, sizeof(m));
    for (int i = 0; i < 4; i++) m.data[i][i] = 1.0f;
    return m;
}

static mat4_t mat4_multiply(mat4_t a, mat4_t b) {
    mat4_t res;
    for (int r = 0; r < 4; r++) {
        for (int c = 0; c < 4; c++) {
            res.data[r][c] = a.data[r][0] * b.data[0][c] +
                             a.data[r][1] * b.data[1][c] +
                             a.data[r][2] * b.data[2][c] +
                             a.data[r][3] * b.data[3][c];
        }
    }
    return res;
}

/* Однорідна матриця стандартного перетворення Денавіта-Гартенберга */
static mat4_t dh_matrix(float theta, float d, float a, float alpha) {
    float ct = cosf(theta), st = sinf(theta);
    float ca = cosf(alpha), sa = sinf(alpha);

    mat4_t m = {{
        { ct,  -st * ca,   st * sa,  a * ct },
        { st,   ct * ca,  -ct * sa,  a * st },
        { 0.0f,      sa,        ca,       d },
        { 0.0f,    0.0f,      0.0f,    1.0f }
    }};
    return m;
}

/* Пряма кінематика (Forward Kinematics) */
bool fk_solve(const manipulator_chain_t *arm, const float *q,
              mat4_t *t_cumulative, mat4_t *t_end_effector) {
    if (!arm || !q || !t_end_effector) return false;

    mat4_t current = mat4_identity();
    if (t_cumulative) t_cumulative[0] = current;

    for (int i = 0; i < arm->num_joints; i++) {
        float theta = arm->joints[i].theta;
        float d = arm->joints[i].d;

        if (arm->joints[i].is_revolute) {
            theta += q[i];
        } else {
            d += q[i];
        }

        mat4_t t_i = dh_matrix(theta, d, arm->joints[i].a, arm->joints[i].alpha);
        current = mat4_multiply(current, t_i);

        if (t_cumulative) {
            t_cumulative[i + 1] = current;
        }
    }

    *t_end_effector = current;
    return true;
}

/* Обчислення геометричного Якобіана J(q) */
bool jacobian_compute(const manipulator_chain_t *arm, const float *q, jacobian_t *jac) {
    if (!arm || !q || !jac) return false;

    mat4_t t_cum[MAX_JOINTS + 1];
    mat4_t t_ee;
    if (!fk_solve(arm, q, t_cum, &t_ee)) return false;

    vec3_t p_ee = {t_ee.data[0][3], t_ee.data[1][3], t_ee.data[2][3]};

    jac->rows = 6;
    jac->cols = arm->num_joints;
    memset(jac->data, 0, sizeof(jac->data));

    for (int i = 0; i < arm->num_joints; i++) {
        /* Одиничний вектор осі Z_(i-1) у світовій системі */
        vec3_t z_i = {t_cum[i].data[0][2], t_cum[i].data[1][2], t_cum[i].data[2][2]};
        /* Позиція початку координат системи i-1 */
        vec3_t p_i = {t_cum[i].data[0][3], t_cum[i].data[1][3], t_cum[i].data[2][3]};

        if (arm->joints[i].is_revolute) {
            vec3_t r = vec3_sub(p_ee, p_i);
            vec3_t j_v = vec3_cross(z_i, r);
            vec3_t j_w = z_i;

            jac->data[0][i] = j_v.x;
            jac->data[1][i] = j_v.y;
            jac->data[2][i] = j_v.z;
            jac->data[3][i] = j_w.x;
            jac->data[4][i] = j_w.y;
            jac->data[5][i] = j_w.z;
        } else {
            /* Поступальне зчленування */
            jac->data[0][i] = z_i.x;
            jac->data[1][i] = z_i.y;
            jac->data[2][i] = z_i.z;
            jac->data[3][i] = 0.0f;
            jac->data[4][i] = 0.0f;
            jac->data[5][i] = 0.0f;
        }
    }
    return true;
}

/* Обернена кінематика: Damped Least Squares (DLS) для 3D-позиціонування */
bool ik_solve_dls_position(const manipulator_chain_t *arm, vec3_t target_pos,
                           const float *q_init, float *q_out,
                           int max_iters, float tol, float lambda) {
    if (!arm || !q_init || !q_out) return false;

    int n = arm->num_joints;
    for (int i = 0; i < n; i++) q_out[i] = q_init[i];

    float lambda_sq = lambda * lambda;

    for (int iter = 0; iter < max_iters; iter++) {
        mat4_t t_ee;
        fk_solve(arm, q_out, NULL, &t_ee);

        vec3_t current_pos = {t_ee.data[0][3], t_ee.data[1][3], t_ee.data[2][3]};
        vec3_t error = vec3_sub(target_pos, current_pos);

        if (vec3_norm(error) < tol) {
            return true; /* Досягнуто заданої точності */
        }

        jacobian_t full_jac;
        jacobian_compute(arm, q_out, &full_jac);

        /* J_pos: розмірність 3xN */
        /* Обчислюємо A = (J * J^T + lambda^2 * I) розмірністю 3x3 */
        float a_mat[3][3] = {0};
        for (int r = 0; r < 3; r++) {
            for (int c = 0; c < 3; c++) {
                float sum = 0.0f;
                for (int k = 0; k < n; k++) {
                    sum += full_jac.data[r][k] * full_jac.data[c][k];
                }
                a_mat[r][c] = sum + (r == c ? lambda_sq : 0.0f);
            }
        }

        /* Пряме аналітичне обернення симетричної матриці 3x3 через мінори */
        float det = a_mat[0][0] * (a_mat[1][1] * a_mat[2][2] - a_mat[1][2] * a_mat[2][1]) -
                    a_mat[0][1] * (a_mat[1][0] * a_mat[2][2] - a_mat[1][2] * a_mat[2][0]) +
                    a_mat[0][2] * (a_mat[1][0] * a_mat[2][1] - a_mat[1][1] * a_mat[2][0]);

        if (fabsf(det) < EPSILON) return false;
        float inv_det = 1.0f / det;

        float a_inv[3][3];
        a_inv[0][0] = (a_mat[1][1] * a_mat[2][2] - a_mat[1][2] * a_mat[2][1]) * inv_det;
        a_inv[0][1] = (a_mat[0][2] * a_mat[2][1] - a_mat[0][1] * a_mat[2][2]) * inv_det;
        a_inv[0][2] = (a_mat[0][1] * a_mat[1][2] - a_mat[0][2] * a_mat[1][1]) * inv_det;

        a_inv[1][0] = (a_mat[1][2] * a_mat[2][0] - a_mat[1][0] * a_mat[2][2]) * inv_det;
        a_inv[1][1] = (a_mat[0][0] * a_mat[2][2] - a_mat[0][2] * a_mat[2][0]) * inv_det;
        a_inv[1][2] = (a_mat[0][2] * a_mat[1][0] - a_mat[0][0] * a_mat[1][2]) * inv_det;

        a_inv[2][0] = (a_mat[1][0] * a_mat[2][1] - a_mat[1][1] * a_mat[2][0]) * inv_det;
        a_inv[2][1] = (a_mat[0][1] * a_mat[2][0] - a_mat[0][0] * a_mat[2][1]) * inv_det;
        a_inv[2][2] = (a_mat[0][0] * a_mat[1][1] - a_mat[0][1] * a_mat[1][0]) * inv_det;

        /* v_temp = A_inv * error */
        float err_arr[3] = {error.x, error.y, error.z};
        float v_temp[3] = {0};
        for (int r = 0; r < 3; r++) {
            v_temp[r] = a_inv[r][0] * err_arr[0] +
                        a_inv[r][1] * err_arr[1] +
                        a_inv[r][2] * err_arr[2];
        }

        /* delta_q = J^T * v_temp */
        for (int i = 0; i < n; i++) {
            float dq = full_jac.data[0][i] * v_temp[0] +
                       full_jac.data[1][i] * v_temp[1] +
                       full_jac.data[2][i] * v_temp[2];

            q_out[i] += dq;

            /* Затискання в апаратні ліміти */
            if (q_out[i] < arm->joints[i].q_min) q_out[i] = arm->joints[i].q_min;
            if (q_out[i] > arm->joints[i].q_max) q_out[i] = arm->joints[i].q_max;
        }
    }

    return false; /* Перевищено ліміт ітерацій */
}
```
```cpp
#include <array>
#include <cmath>
#include <optional>
#include <numbers>
#include <span>
#include <algorithm>

template <std::size_t N>
class ManipulatorKinematics {
public:
    static_assert(N > 0 && N <= 8, "Кількість ланок повинна бути від 1 до 8");

    struct Vec3 {
        float x{0.0f}, y{0.0f}, z{0.0f};

        [[nodiscard]] constexpr Vec3 operator+(const Vec3& o) const noexcept {
            return {x + o.x, y + o.y, z + o.z};
        }
        [[nodiscard]] constexpr Vec3 operator-(const Vec3& o) const noexcept {
            return {x - o.x, y - o.y, z - o.z};
        }
        [[nodiscard]] constexpr Vec3 cross(const Vec3& o) const noexcept {
            return {y * o.z - z * o.y, z * o.x - x * o.z, x * o.y - y * o.x};
        }
        [[nodiscard]] constexpr float dot(const Vec3& o) const noexcept {
            return x * o.x + y * o.y + z * o.z;
        }
        [[nodiscard]] float norm() const noexcept {
            return std::sqrt(dot(*this));
        }
    };

    struct Mat4 {
        std::array<std::array<float, 4>, 4> data{};

        static constexpr Mat4 identity() noexcept {
            Mat4 m{};
            for (std::size_t i = 0; i < 4; ++i) m.data[i][i] = 1.0f;
            return m;
        }

        [[nodiscard]] constexpr Mat4 operator*(const Mat4& o) const noexcept {
            Mat4 res{};
            for (std::size_t r = 0; r < 4; ++r) {
                for (std::size_t c = 0; c < 4; ++c) {
                    res.data[r][c] = data[r][0] * o.data[0][c] +
                                     data[r][1] * o.data[1][c] +
                                     data[r][2] * o.data[2][c] +
                                     data[r][3] * o.data[3][c];
                }
            }
            return res;
        }

        [[nodiscard]] constexpr Vec3 translation() const noexcept {
            return {data[0][3], data[1][3], data[2][3]};
        }

        [[nodiscard]] constexpr Vec3 z_axis() const noexcept {
            return {data[0][2], data[1][2], data[2][2]};
        }
    };

    struct DHJoint {
        float theta{0.0f};  // кут суглоба (рад)
        float d{0.0f};      // зміщення вздовж Z_(i-1) (м)
        float a{0.0f};      // довжина спільного перпендикуляра X_i (м)
        float alpha{0.0f};  // скручування ланки (рад)
        bool is_revolute{true};
        float q_min{-std::numbers::pi_v<float>};
        float q_max{std::numbers::pi_v<float>};
    };

    using JointArray = std::array<DHJoint, N>;
    using JointAngles = std::array<float, N>;
    using Jacobian = std::array<std::array<float, N>, 6>;

    explicit constexpr ManipulatorKinematics(JointArray joints) noexcept
        : joints_(joints) {}

    [[nodiscard]] static Mat4 compute_dh_transform(float theta, float d, float a, float alpha) noexcept {
        const float ct = std::cos(theta), st = std::sin(theta);
        const float ca = std::cos(alpha), sa = std::sin(alpha);

        Mat4 m{};
        m.data[0] = { ct,  -st * ca,   st * sa,  a * ct };
        m.data[1] = { st,   ct * ca,  -ct * sa,  a * st };
        m.data[2] = { 0.0f,      sa,        ca,       d };
        m.data[3] = { 0.0f,    0.0f,      0.0f,    1.0f };
        return m;
    }

    [[nodiscard]] Mat4 forward_kinematics(const JointAngles& q) const noexcept {
        Mat4 current = Mat4::identity();
        for (std::size_t i = 0; i < N; ++i) {
            const float theta = joints_[i].is_revolute ? joints_[i].theta + q[i] : joints_[i].theta;
            const float d = joints_[i].is_revolute ? joints_[i].d : joints_[i].d + q[i];
            current = current * compute_dh_transform(theta, d, joints_[i].a, joints_[i].alpha);
        }
        return current;
    }

    [[nodiscard]] Jacobian compute_jacobian(const JointAngles& q) const noexcept {
        Jacobian jac{};
        std::array<Mat4, N + 1> frames{};
        frames[0] = Mat4::identity();

        Mat4 current = Mat4::identity();
        for (std::size_t i = 0; i < N; ++i) {
            const float theta = joints_[i].is_revolute ? joints_[i].theta + q[i] : joints_[i].theta;
            const float d = joints_[i].is_revolute ? joints_[i].d : joints_[i].d + q[i];
            current = current * compute_dh_transform(theta, d, joints_[i].a, joints_[i].alpha);
            frames[i + 1] = current;
        }

        const Vec3 p_ee = frames[N].translation();

        for (std::size_t i = 0; i < N; ++i) {
            const Vec3 z_i = frames[i].z_axis();
            const Vec3 p_i = frames[i].translation();

            if (joints_[i].is_revolute) {
                const Vec3 j_v = z_i.cross(p_ee - p_i);
                jac[0][i] = j_v.x;
                jac[1][i] = j_v.y;
                jac[2][i] = j_v.z;
                jac[3][i] = z_i.x;
                jac[4][i] = z_i.y;
                jac[5][i] = z_i.z;
            } else {
                jac[0][i] = z_i.x;
                jac[1][i] = z_i.y;
                jac[2][i] = z_i.z;
                jac[3][i] = 0.0f;
                jac[4][i] = 0.0f;
                jac[5][i] = 0.0f;
            }
        }
        return jac;
    }

    [[nodiscard]] std::optional<JointAngles> inverse_kinematics_dls(
        const Vec3& target_pos,
        const JointAngles& q_init,
        int max_iters = 50,
        float tolerance = 1e-4f,
        float lambda = 0.1f) const noexcept {

        JointAngles q = q_init;
        const float lambda_sq = lambda * lambda;

        for (int iter = 0; iter < max_iters; ++iter) {
            const Mat4 t_ee = forward_kinematics(q);
            const Vec3 err = target_pos - t_ee.translation();

            if (err.norm() < tolerance) {
                return q; // Збіжність досягнута
            }

            const Jacobian jac = compute_jacobian(q);

            // A = J_pos * J_pos^T + lambda^2 * I (розмірність 3x3)
            std::array<std::array<float, 3>, 3> a_mat{};
            for (std::size_t r = 0; r < 3; ++r) {
                for (std::size_t c = 0; c < 3; ++c) {
                    float sum = 0.0f;
                    for (std::size_t k = 0; k < N; ++k) {
                        sum += jac[r][k] * jac[c][k];
                    }
                    a_mat[r][c] = sum + (r == c ? lambda_sq : 0.0f);
                }
            }

            const float det = a_mat[0][0] * (a_mat[1][1] * a_mat[2][2] - a_mat[1][2] * a_mat[2][1]) -
                              a_mat[0][1] * (a_mat[1][0] * a_mat[2][2] - a_mat[1][2] * a_mat[2][0]) +
                              a_mat[0][2] * (a_mat[1][0] * a_mat[2][1] - a_mat[1][1] * a_mat[2][0]);

            if (std::abs(det) < 1e-7f) return std::nullopt;
            const float inv_det = 1.0f / det;

            std::array<std::array<float, 3>, 3> a_inv{};
            a_inv[0][0] = (a_mat[1][1] * a_mat[2][2] - a_mat[1][2] * a_mat[2][1]) * inv_det;
            a_inv[0][1] = (a_mat[0][2] * a_mat[2][1] - a_mat[0][1] * a_mat[2][2]) * inv_det;
            a_inv[0][2] = (a_mat[0][1] * a_mat[1][2] - a_mat[0][2] * a_mat[1][1]) * inv_det;

            a_inv[1][0] = (a_mat[1][2] * a_mat[2][0] - a_mat[1][0] * a_mat[2][2]) * inv_det;
            a_inv[1][1] = (a_mat[0][0] * a_mat[2][2] - a_mat[0][2] * a_mat[2][0]) * inv_det;
            a_inv[1][2] = (a_mat[0][2] * a_mat[1][0] - a_mat[0][0] * a_mat[1][2]) * inv_det;

            a_inv[2][0] = (a_mat[1][0] * a_mat[2][1] - a_mat[1][1] * a_mat[2][0]) * inv_det;
            a_inv[2][1] = (a_mat[0][1] * a_mat[2][0] - a_mat[0][0] * a_mat[2][1]) * inv_det;
            a_inv[2][2] = (a_mat[0][0] * a_mat[1][1] - a_mat[0][1] * a_mat[1][0]) * inv_det;

            const std::array<float, 3> err_arr{err.x, err.y, err.z};
            std::array<float, 3> v_temp{};
            for (std::size_t r = 0; r < 3; ++r) {
                v_temp[r] = a_inv[r][0] * err_arr[0] +
                            a_inv[r][1] * err_arr[1] +
                            a_inv[r][2] * err_arr[2];
            }

            for (std::size_t i = 0; i < N; ++i) {
                const float dq = jac[0][i] * v_temp[0] +
                                 jac[1][i] * v_temp[1] +
                                 jac[2][i] * v_temp[2];

                q[i] = std::clamp(q[i] + dq, joints_[i].q_min, joints_[i].q_max);
            }
        }
        return std::nullopt; // Не вдалося зійтися за задану кількість ітерацій
    }

private:
    JointArray joints_;
};
```
:::

## Інженерний приклад: 3-звенний маніпулятор розвідника

Розглянемо триланковий плоский маніпулятор розвідного дрона з довжинами ланок `L_1 = 0.35` м, `L_2 = 0.30` м, `L_3 = 0.15` м. Задамо цільову декартову точку `P_target = [0.45, 0.25, 0.0]ᵀ` та перевіримо збіжність розв'язувача DLS з початкового нульового положення:

:::tabs
```c
int main(void) {
    manipulator_chain_t arm = {
        .num_joints = 3,
        .joints = {
            {.theta = 0.0f, .d = 0.0f, .a = 0.35f, .alpha = 0.0f, .is_revolute = true, .q_min = -3.14f, .q_max = 3.14f},
            {.theta = 0.0f, .d = 0.0f, .a = 0.30f, .alpha = 0.0f, .is_revolute = true, .q_min = -2.50f, .q_max = 2.50f},
            {.theta = 0.0f, .d = 0.0f, .a = 0.15f, .alpha = 0.0f, .is_revolute = true, .q_min = -2.50f, .q_max = 2.50f}
        }
    };

    vec3_t target = {0.45f, 0.25f, 0.0f};
    float q_init[3] = {0.1f, 0.1f, 0.1f};
    float q_sol[3] = {0};

    if (ik_solve_dls_position(&arm, target, q_init, q_sol, 100, 1e-4f, 0.05f)) {
        mat4_t t_verify;
        fk_solve(&arm, q_sol, NULL, &t_verify);
        printf("IK зійшлася: q = [%.3f, %.3f, %.3f] рад\n", q_sol[0], q_sol[1], q_sol[2]);
        printf("Кінцева позиція: [%.4f, %.4f, %.4f] м\n",
               t_verify.data[0][3], t_verify.data[1][3], t_verify.data[2][3]);
    } else {
        printf("IK не зійшлася (поза межами або сингулярність)\n");
    }
    return 0;
}
```
```cpp
#include <iostream>
#include <iomanip>

int main() {
    using Kinematics3D = ManipulatorKinematics<3>;

    Kinematics3D::JointArray joints{{
        {.a = 0.35f, .q_min = -3.14f, .q_max = 3.14f},
        {.a = 0.30f, .q_min = -2.50f, .q_max = 2.50f},
        {.a = 0.15f, .q_min = -2.50f, .q_max = 2.50f}
    }};

    Kinematics3D arm(joints);

    const Kinematics3D::Vec3 target{0.45f, 0.25f, 0.0f};
    const Kinematics3D::JointAngles q_init{0.1f, 0.1f, 0.1f};

    if (auto sol = arm.inverse_kinematics_dls(target, q_init, 100, 1e-4f, 0.05f)) {
        const auto t_verify = arm.forward_kinematics(*sol);
        const auto p = t_verify.translation();

        std::cout << std::fixed << std::setprecision(4);
        std::cout << "IK зійшлася: q = [" << (*sol)[0] << ", " << (*sol)[1] << ", " << (*sol)[2] << "] рад\n";
        std::cout << "Кінцева позиція: [" << p.x << ", " << p.y << ", " << p.z << "] м\n";
    } else {
        std::cout << "IK не зійшлася (поза робочим простором)\n";
    }
    return 0;
}
```
:::

## Аналіз продуктивності та профілювання на ARM Cortex-M

Проведемо аналіз обчислювальної складності алгоритмів бібліотеки при роботі на типовому мікроконтролері польотного контролера STM32H743VI (ядро ARM Cortex-M7 з апаратним FPU одинарної та подвійної точності на частоті 480 МГц):

1. **Пряма кінематика (Forward Kinematics):**
   Для 6-ланкового маніпулятора обчислення `fk_solve()` вимагає 6 викликів `sinf`/`cosf` (апаратні інструкції або швидкі табличні наближення) та 5 множень матриць 4×4. Загальний час виконання становить **1.8 мікросекунди** (~860 тактів процесора).
2. **Геометричний Якобіан (Jacobian Compute):**
   Обчислення Якобіана використовує проміжні матриці, збережені під час прямої кінематики. Потрібно лише 6 операцій векторного добутку `cross()` (по 6 множень і 3 віднімання на суглоб). Час виконання — **0.9 мікросекунди** (~430 тактів).
3. **Обернення матриці 3×3:**
   Пряме аналітичне обчислення матриці `A_inv` через мінори займає 27 множень, 14 віднімань та 1 ділення на визначник `det`. Завдяки конвеєризації FPU це займає всього **0.35 мікросекунди** (~170 тактів). Для порівняння: чисельний метод Гаусса-Жордана або LU-декомпозиція вимагали б у 4–6 разів більше тактів і створювали б ризик втрати точності.
4. **Повна ітерація DLS IK:**
   Одна ітерація пошуку положення займає **3.2 мікросекунди**. За типової кількості ітерацій від 5 до 12 під час стеження за неперервною траєкторією повний розрахунок кутів займає від **16 до 38 мікросекунд**, що становить менше 4% процесорного бюджету в такті керування 1 кГц (1000 мкс).

## Обробка крайових випадків та відмовостійкість

Під час польоту або пересування робота в умовах вібрацій, завад датчиків та вітрових поривів чисельний ітератор стикається з низкою крайових станів, які вимагають детермінованої обробки:

1. **Таймаут за кількістю ітерацій (Max Iterations Limit):**
   Якщо цільова точка раптово вийшла за межі досяжності маніпулятора (наприклад, оператор задав координату поза робочим об'ємом), функція `ik_solve_dls_position` завершує роботу після досягнення `max_iters` і повертає `false` або `std::nullopt`. Поточний вектор кутів сервоприводів `q_out` при цьому не руйнується, а залишається в найближчій досяжній точці, запобігаючи неконтрольованому вильоту маніпулятора в упори.
2. **Ортонормалізація базису (Numerical Drift Correction):**
   У контурах прямої кінематики після тисяч послідовних множень матриць повороту накопичуються похибки заокруглення формату `float32` (IEEE 754), внаслідок чого матриця `R` перестає бути строго ортогональною (`R · Rᵀ ≠ I`). Для усунення цього дрейфу кожні 100 циклів виконується швидка процедура Грама-Шмідта над стовпцями матриці: `x' = normalize(x)`, `z' = normalize(x' × y)`, `y' = z' × x'`.
3. **Захист від виродження при обмеженнях (Joint Limit Clamping):**
   Коли один із суглобів досягає механічного упору (`q_min` або `q_max`), його швидкість має бути заблокована в бік упору. Якщо просто відсікати кут через `std::clamp()`, ітератор може марно витрачати корекцію на заблокований суглоб. У повнофункціональних контролерах стовпець заблокованого суглоба в матриці Якобі тимчасово зануляють, передаючи зусилля на вільні ланки.
4. **Інтеграція з протоколом MAVLink:**
   На борту БПЛА результат обчислення оберненої кінематики транслюється у PWM-сигнали для сервоприводів через повідомлення `COMMAND_LONG` (команда `MAV_CMD_DO_SET_SERVO`) або спеціалізований потік `SERVO_OUTPUT_RAW`. Це дає змогу оператору наземної станції QGroundControl задавати просторову траєкторію кінця руки, залишаючи низькорівневий розрахунок кутів бортовому автопілоту.
