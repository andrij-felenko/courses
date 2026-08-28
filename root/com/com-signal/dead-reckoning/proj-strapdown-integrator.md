# ⚙️ Дискретний модуль БІНС із компенсацією гравітації та ZUPT

Цей проектний розбір містить повну, оптимізовану для вбудованих систем реалізацію алгоритму дискретної безплатформної інерціальної навігації (Strapdown INS Mechanization) мовами C та C++. Модуль перетворює потік сирих вимірювань тривісного акселерометра та тривісного гіроскопа на неперервну тривимірну оцінку траєкторії апарата у локальній географічній системі координат NED (North-East-Down — Північ-Схід-Вниз).

## Архітектура та математичний конвеєр

Розрахунковий цикл виконується на кожному кроці надходження даних з давача `IMU` з фіксованим інтервалом дискретизації `Δt` (зазвичай від 100 до 1000 Гц). Обчислювальний конвеєр побудований на 5 послідовних математичних перетвореннях.

### 1. Калібрування та зняття зміщень нуля

Перед виконанням кінематичних розрахунків сирі вимірювання датчиків очищуються від заздалегідь визначених або оцінених у процесі роботи систематичних зміщень нуля (bias):

```
ω_cor = ω_raw − b_gyro
f_cor = f_raw − b_accel
```

У реальних прошивках мікроконтролерів дані з IMU надходять у вигляді 16-бітних цілих чисел (LSB) через шини SPI або I2C. Перед обчисленнями ці відліки масштабуються у фізичні одиниці Міжнародної системи (СІ) — `м/с²` для акселерометра та `рад/с` для гіроскопа відповідно до встановленого діапазону вимірювань (наприклад, `±16g` та `±2000 °/с`).

### 2. Інтегрування кутової швидкості (Кінематика орієнтації)

Обчислюється вектор приросту кута повороту за крок дискретизації `Δθ = ω_cor · Δt`. За модулем вектору кута `||Δθ|| = √(Δθ_x² + Δθ_y² + Δθ_z²)` формується кватерніон приросту повороту `Δq`:

```
Δq = [ cos(||Δθ|| / 2),  (sin(||Δθ|| / 2) / ||Δθ||) · Δθ ]ᵀ
```

Якщо кутовий приріст надзвичайно малий (`||Δθ|| < 10⁻⁸`), тригонометричні функції замінюються на перші члени ряду Тейлора для запобігання діленню на нуль і втраті точності:

```
Δq ≈ [ 1,  1/2 · Δθ_x,  1/2 · Δθ_y,  1/2 · Δθ_z ]ᵀ
```

Поточний кватерніон орієнтації `q` оновлюється кватерніонним множенням `q_new = q_old ⊗ Δq`, після чого виконується обов'язкова евклідова нормалізація `q_new = q_new / ||q_new||`. Це запобігає накопиченню похибок округлення чисел із плаваючою комою, які з часом руйнують унітарність кватерніона.

### 3. Перетворення координат питомої сили

За оновленим кватерніоном будується ортогональна матриця напрямних косинусів `R_bⁿ` (матриця повороту з системи корпусу в навігаційну систему):

```
         [ 1 - 2(y²+z²)    2(xy - wz)    2(xz + wy) ]
R_bⁿ =   [   2(xy + wz)  1 - 2(x²+z²)    2(yz - wx) ]
         [   2(xz - wy)    2(yz + wx)  1 - 2(x²+y²) ]
```

Виміряний акселерометром вектор питомої сили переводиться у навігаційну систему: `fⁿ = R_bⁿ · f_cor`.

### 4. Компенсація сили тяжіння

У системі координат NED вісь Z спрямована до центру Землі, тому вектор сили тяжіння дорівнює `gⁿ = [0, 0, +9.80665]ᵀ м/с²`. Коли апарат нерухомий, акселерометр вимірює реакцію опори вгору (`f_z = −9.80665 м/с²`). Справжнє прискорення знаходиться додаванням вектору гравітації:

```
aⁿ = fⁿ + gⁿ
```

### 5. Трапецеїдальне числове інтегрування

Для мінімізації фазового запізнення та числової похибки застосовується інтегратор другого порядку (метод трапецій), який використовує середнє арифметичне прискорень на межах інтервалу:

```
a_avg = 1/2 · (a[k] + a[k+1])
v[k+1] = v[k] + a_avg · Δt
v_avg = 1/2 · (v[k] + v[k+1])
p[k+1] = p[k] + v_avg · Δt
```

Найпростіший прямокутний метод Ейлера (`v[k+1] = v[k] + a[k] · Δt`) має перший порядок точності `O(Δt)` і вносить штучне фазове запізнення на `Δt / 2`. Під час коливальних рухів або вібрацій це запізнення спричиняє паразитичне накачування енергії в розрахунковий контур, через що амплітуда розрахункової швидкості безпідставно зростає. Трапецеїдальний метод має другий порядок точності `O(Δt²)` і зберігає стійкість системи на високих частотах дискретизації.

### 6. Детектор зупинки та корекція ZUPT (Zero-Velocity Update)

Під час зупинки об'єкта або фази контакту ноги робота з поверхнею справжня швидкість дорівнює нулю. Детектор аналізує норму кутової швидкості `||ω_raw|| < ε_ω` та відхилення норми прискорення від величини `g`: `| ||f_raw|| − g | < ε_a`. Якщо обидві умови виконуються протягом кількох послідовних кроків, швидкість примусово скидається до нуля, запобігаючи квадратичному накопиченню дрейфу положення під час зупинок.

## Повна реалізація алгоритму на C та C++

:::tabs
```c
#include <stdio.h>
#include <math.h>
#include <stdbool.h>

#define GRAVITY_MSS 9.80665f

typedef struct {
    float x, y, z;
} Vec3;

typedef struct {
    float w, x, y, z;
} Quat;

typedef struct {
    float m[3][3];
} Mat3;

typedef struct {
    Vec3 pos;       /* Позиція [м] (North, East, Down) */
    Vec3 vel;       /* Швидкість [м/с] (North, East, Down) */
    Quat q;         /* Орієнтація (кватерніон повороту з body в nav) */
    Vec3 prev_acc;  /* Прискорення попереднього кроку для трапецеїдального інтеграла */
    Vec3 gyro_bias; /* Калібрувальне зміщення нуля гіроскопа [рад/с] */
    Vec3 accel_bias;/* Калібрувальне зміщення нуля акселерометра [м/с²] */
} InsState;

static inline Vec3 vec3_add(Vec3 a, Vec3 b) {
    return (Vec3){a.x + b.x, a.y + b.y, a.z + b.z};
}

static inline Vec3 vec3_sub(Vec3 a, Vec3 b) {
    return (Vec3){a.x - b.x, a.y - b.y, a.z - b.z};
}

static inline Vec3 vec3_scale(Vec3 v, float s) {
    return (Vec3){v.x * s, v.y * s, v.z * s};
}

static inline float vec3_norm(Vec3 v) {
    return sqrtf(v.x * v.x + v.y * v.y + v.z * v.z);
}

static inline Quat quat_norm(Quat q) {
    float n = sqrtf(q.w * q.w + q.x * q.x + q.y * q.y + q.z * q.z);
    if (n < 1e-8f) return (Quat){1.0f, 0.0f, 0.0f, 0.0f};
    float inv = 1.0f / n;
    return (Quat){q.w * inv, q.x * inv, q.y * inv, q.z * inv};
}

static inline Quat quat_mult(Quat a, Quat b) {
    return (Quat){
        a.w * b.w - a.x * b.x - a.y * b.y - a.z * b.z,
        a.w * b.x + a.x * b.w + a.y * b.z - a.z * b.y,
        a.w * b.y - a.x * b.z + a.y * b.w + a.z * b.x,
        a.w * b.z + a.x * b.y - a.y * b.x + a.z * b.w
    };
}

static inline Mat3 quat_to_dcm(Quat q) {
    Mat3 r;
    float qw = q.w, qx = q.x, qy = q.y, qz = q.z;
    float qx2 = qx * qx, qy2 = qy * qy, qz2 = qz * qz;

    r.m[0][0] = 1.0f - 2.0f * (qy2 + qz2);
    r.m[0][1] = 2.0f * (qx * qy - qw * qz);
    r.m[0][2] = 2.0f * (qx * qz + qw * qy);

    r.m[1][0] = 2.0f * (qx * qy + qw * qz);
    r.m[1][1] = 1.0f - 2.0f * (qx2 + qz2);
    r.m[1][2] = 2.0f * (qy * qz - qw * qx);

    r.m[2][0] = 2.0f * (qx * qz - qw * qy);
    r.m[2][1] = 2.0f * (qy * qz + qw * qx);
    r.m[2][2] = 1.0f - 2.0f * (qx2 + qy2);
    return r;
}

static inline Vec3 mat3_mult_vec3(Mat3 m, Vec3 v) {
    return (Vec3){
        m.m[0][0] * v.x + m.m[0][1] * v.y + m.m[0][2] * v.z,
        m.m[1][0] * v.x + m.m[1][1] * v.y + m.m[1][2] * v.z,
        m.m[2][0] * v.x + m.m[2][1] * v.y + m.m[2][2] * v.z
    };
}

void ins_init(InsState *ins, Vec3 init_pos, Vec3 init_vel, Quat init_q) {
    ins->pos = init_pos;
    ins->vel = init_vel;
    ins->q = quat_norm(init_q);
    ins->prev_acc = (Vec3){0.0f, 0.0f, 0.0f};
    ins->gyro_bias = (Vec3){0.0f, 0.0f, 0.0f};
    ins->accel_bias = (Vec3){0.0f, 0.0f, 0.0f};
}

void ins_update(InsState *ins, Vec3 raw_acc, Vec3 raw_gyro, float dt) {
    /* 1. Компенсація зміщень нуля (Bias) */
    Vec3 unb_gyro = vec3_sub(raw_gyro, ins->gyro_bias);
    Vec3 unb_acc  = vec3_sub(raw_acc, ins->accel_bias);

    /* 2. Інтегрування орієнтації через приріст кватерніона */
    Vec3 d_theta = vec3_scale(unb_gyro, dt);
    float angle = vec3_norm(d_theta);

    Quat dq;
    if (angle > 1e-8f) {
        float half_angle = 0.5f * angle;
        float factor = sinf(half_angle) / angle;
        dq = (Quat){cosf(half_angle), d_theta.x * factor, d_theta.y * factor, d_theta.z * factor};
    } else {
        dq = (Quat){1.0f, 0.5f * d_theta.x, 0.5f * d_theta.y, 0.5f * d_theta.z};
    }
    ins->q = quat_norm(quat_mult(ins->q, dq));

    /* 3. Поворот виміряної питомої сили у навігаційну систему NED */
    Mat3 dcm = quat_to_dcm(ins->q);
    Vec3 f_nav = mat3_mult_vec3(dcm, unb_acc);

    /* 4. Компенсація сили тяжіння: a_nav = f_nav + [0, 0, g] */
    Vec3 g_nav = {0.0f, 0.0f, GRAVITY_MSS};
    Vec3 cur_acc = vec3_add(f_nav, g_nav);

    /* 5. Трапецеїдальне інтегрування швидкості та позиції */
    Vec3 avg_acc = vec3_scale(vec3_add(ins->prev_acc, cur_acc), 0.5f);
    Vec3 next_vel = vec3_add(ins->vel, vec3_scale(avg_acc, dt));
    Vec3 avg_vel = vec3_scale(vec3_add(ins->vel, next_vel), 0.5f);

    ins->pos = vec3_add(ins->pos, vec3_scale(avg_vel, dt));
    ins->vel = next_vel;
    ins->prev_acc = cur_acc;
}

bool ins_check_and_apply_zupt(InsState *ins, Vec3 raw_acc, Vec3 raw_gyro, float gyro_thresh, float acc_thresh) {
    float g_diff = fabsf(vec3_norm(raw_acc) - GRAVITY_MSS);
    float w_norm = vec3_norm(raw_gyro);

    if (g_diff < acc_thresh && w_norm < gyro_thresh) {
        /* Детектор спокою: апарат стоїть на місці */
        ins->vel = (Vec3){0.0f, 0.0f, 0.0f};
        ins->prev_acc = (Vec3){0.0f, 0.0f, 0.0f};
        return true;
    }
    return false;
}

int main(void) {
    InsState ins;
    ins_init(&ins, (Vec3){0.0f, 0.0f, 0.0f}, (Vec3){0.0f, 0.0f, 0.0f}, (Quat){1.0f, 0.0f, 0.0f, 0.0f});

    float dt = 0.01f; /* 100 Гц */
    printf("=== Тест дискретної БІНС (100 Гц) ===\n");

    /* Симуляція: розгін уздовж осі X (North) з прискоренням 2.0 м/с² протягом 2 секунд */
    for (int i = 0; i < 200; ++i) {
        Vec3 acc = {2.0f, 0.0f, -GRAVITY_MSS}; /* Питома сила акселерометра */
        Vec3 gyro = {0.0f, 0.0f, 0.0f};
        ins_update(&ins, acc, gyro, dt);
    }

    printf("Після 2 с розгону: Pos=(%.3f, %.3f, %.3f) м, Vel=(%.3f, %.3f, %.3f) м/с\n",
           ins.pos.x, ins.pos.y, ins.pos.z, ins.vel.x, ins.vel.y, ins.vel.z);

    /* Рівномірний рух протягом 3 секунд */
    for (int i = 0; i < 300; ++i) {
        Vec3 acc = {0.0f, 0.0f, -GRAVITY_MSS};
        Vec3 gyro = {0.0f, 0.0f, 0.0f};
        ins_update(&ins, acc, gyro, dt);
    }

    printf("Після 3 с круїзу: Pos=(%.3f, %.3f, %.3f) м, Vel=(%.3f, %.3f, %.3f) м/с\n",
           ins.pos.x, ins.pos.y, ins.pos.z, ins.vel.x, ins.vel.y, ins.vel.z);

    return 0;
}
```
```cpp
#include <iostream>
#include <cmath>
#include <array>
#include <optional>

namespace nav {

constexpr float GRAVITY_MSS = 9.80665f;

struct Vector3 {
    float x{0.0f};
    float y{0.0f};
    float z{0.0f};

    constexpr Vector3 operator+(const Vector3& o) const noexcept {
        return {x + o.x, y + o.y, z + o.z};
    }
    constexpr Vector3 operator-(const Vector3& o) const noexcept {
        return {x - o.x, y - o.y, z - o.z};
    }
    constexpr Vector3 operator*(float s) const noexcept {
        return {x * s, y * s, z * s};
    }
    [[nodiscard]] float norm() const noexcept {
        return std::sqrt(x * x + y * y + z * z);
    }
};

struct Quaternion {
    float w{1.0f};
    float x{0.0f};
    float y{0.0f};
    float z{0.0f};

    [[nodiscard]] Quaternion normalized() const noexcept {
        const float n = std::sqrt(w * w + x * x + y * y + z * z);
        if (n < 1e-8f) return {1.0f, 0.0f, 0.0f, 0.0f};
        const float inv = 1.0f / n;
        return {w * inv, x * inv, y * inv, z * inv};
    }

    [[nodiscard]] constexpr Quaternion operator*(const Quaternion& b) const noexcept {
        return {
            w * b.w - x * b.x - y * b.y - z * b.z,
            w * b.x + x * b.w + y * b.z - z * b.y,
            w * b.y - x * b.z + y * b.w + z * b.x,
            w * b.z + x * b.y - y * b.x + z * b.w
        };
    }

    [[nodiscard]] std::array<std::array<float, 3>, 3> to_rotation_matrix() const noexcept {
        const float qx2 = x * x, qy2 = y * y, qz2 = z * z;
        return {{
            {1.0f - 2.0f * (qy2 + qz2), 2.0f * (x * y - w * z), 2.0f * (x * z + w * y)},
            {2.0f * (x * y + w * z), 1.0f - 2.0f * (qx2 + qz2), 2.0f * (y * z - w * x)},
            {2.0f * (x * z - w * y), 2.0f * (y * z + w * x), 1.0f - 2.0f * (qx2 + qy2)}
        }};
    }
};

class StrapdownIns {
public:
    struct ImuSample {
        Vector3 accel_ms2;  /* Сира питома сила корпусу [м/с²] */
        Vector3 gyro_rads;   /* Сира кутова швидкість корпусу [рад/с] */
        float dt_sec{0.01f}; /* Інтервал дискретизації */
    };

    struct Calibration {
        Vector3 accel_bias{0.0f, 0.0f, 0.0f};
        Vector3 gyro_bias{0.0f, 0.0f, 0.0f};
    };

    explicit StrapdownIns(Vector3 init_pos = {}, Vector3 init_vel = {}, Quaternion init_q = {}) noexcept
        : pos_{init_pos}, vel_{init_vel}, q_{init_q.normalized()} {}

    void set_calibration(const Calibration& calib) noexcept {
        calib_ = calib;
    }

    void update(const ImuSample& imu) noexcept {
        /* 1. Компенсація зміщень нуля давачів */
        const Vector3 unb_gyro = imu.gyro_rads - calib_.gyro_bias;
        const Vector3 unb_acc  = imu.accel_ms2 - calib_.accel_bias;

        /* 2. Інтегрування кватерніона орієнтації */
        const Vector3 d_theta = unb_gyro * imu.dt_sec;
        const float angle = d_theta.norm();

        Quaternion dq;
        if (angle > 1e-8f) {
            const float half_angle = 0.5f * angle;
            const float factor = std::sin(half_angle) / angle;
            dq = {std::cos(half_angle), d_theta.x * factor, d_theta.y * factor, d_theta.z * factor};
        } else {
            dq = {1.0f, 0.5f * d_theta.x, 0.5f * d_theta.y, 0.5f * d_theta.z};
        }
        q_ = (q_ * dq).normalized();

        /* 3. Поворот прискорення у навігаційну систему NED */
        const auto r = q_.to_rotation_matrix();
        const Vector3 f_nav{
            r[0][0] * unb_acc.x + r[0][1] * unb_acc.y + r[0][2] * unb_acc.z,
            r[1][0] * unb_acc.x + r[1][1] * unb_acc.y + r[1][2] * unb_acc.z,
            r[2][0] * unb_acc.x + r[2][1] * unb_acc.y + r[2][2] * unb_acc.z
        };

        /* 4. Компенсація сили тяжіння */
        const Vector3 cur_acc = f_nav + Vector3{0.0f, 0.0f, GRAVITY_MSS};

        /* 5. Трапецеїдальне чисельне інтегрування швидкості та координат */
        const Vector3 avg_acc = (prev_acc_ + cur_acc) * 0.5f;
        const Vector3 next_vel = vel_ + avg_acc * imu.dt_sec;
        const Vector3 avg_vel = (vel_ + next_vel) * 0.5f;

        pos_ = pos_ + avg_vel * imu.dt_sec;
        vel_ = next_vel;
        prev_acc_ = cur_acc;
    }

    bool check_and_apply_zupt(const Vector3& raw_acc, const Vector3& raw_gyro,
                              float gyro_thresh = 0.05f, float acc_thresh = 0.2f) noexcept {
        const float g_diff = std::abs(raw_acc.norm() - GRAVITY_MSS);
        const float w_norm = raw_gyro.norm();

        if (g_diff < acc_thresh && w_norm < gyro_thresh) {
            vel_ = {0.0f, 0.0f, 0.0f};
            prev_acc_ = {0.0f, 0.0f, 0.0f};
            return true;
        }
        return false;
    }

    [[nodiscard]] const Vector3& position() const noexcept { return pos_; }
    [[nodiscard]] const Vector3& velocity() const noexcept { return vel_; }
    [[nodiscard]] const Quaternion& orientation() const noexcept { return q_; }

private:
    Vector3 pos_{0.0f, 0.0f, 0.0f};
    Vector3 vel_{0.0f, 0.0f, 0.0f};
    Quaternion q_{1.0f, 0.0f, 0.0f, 0.0f};
    Vector3 prev_acc_{0.0f, 0.0f, 0.0f};
    Calibration calib_{};
};

} // namespace nav

int main() {
    nav::StrapdownIns ins;
    constexpr float dt = 0.01f;

    std::cout << "=== Тест StrapdownIns C++ (100 Гц) ===\n";

    /* Симуляція розгону 2.0 м/с² по осі North протягом 2 с */
    for (int i = 0; i < 200; ++i) {
        ins.update({{2.0f, 0.0f, -nav::GRAVITY_MSS}, {0.0f, 0.0f, 0.0f}, dt});
    }

    const auto p1 = ins.position();
    const auto v1 = ins.velocity();
    std::cout << "Після 2 с розгону: Pos=(" << p1.x << ", " << p1.y << ", " << p1.z
              << ") м, Vel=(" << v1.x << ", " << v1.y << ", " << v1.z << ") м/с\n";

    /* Симуляція рівномірного руху протягом 3 с */
    for (int i = 0; i < 300; ++i) {
        ins.update({{0.0f, 0.0f, -nav::GRAVITY_MSS}, {0.0f, 0.0f, 0.0f}, dt});
    }

    const auto p2 = ins.position();
    const auto v2 = ins.velocity();
    std::cout << "Після 3 с круїзу: Pos=(" << p2.x << ", " << p2.y << ", " << p2.z
              << ") м, Vel=(" << v2.x << ", " << v2.y << ", " << v2.z << ") м/с\n";

    return 0;
}
```
:::

## Інженерні особливості реалізації у вбудованих системах

Під час перенесення інерціального алгоритму на мікроконтролери польотних контролерів (STM32H7, ESP32-S3 чи Cortex-M4) необхідно враховувати специфічні апаратні та алгоритмічні фактори:

### 1. Високочастотні ефекти вібрацій: конічний та гребковий рух

У реальних безпілотниках і транспортних засобах двигуни створюють механічні вібрації високої частоти (50–500 Гц). Якщо корпус здійснює одночасні коливання по двох кутових осях (наприклад, по крену й тангажу з фазовим зсувом 90°), виникає так званий **конічний рух** (англ. *coning motion*). Пряме інтегрування низької частоти пропускає постійний нелінійний зсув орієнтації.

Аналогічно, кореляція між високочастотними кутовими коливаннями та лінійними вібраціями породжує **гребковий ефект** (англ. *sculling motion*), коли алгоритм реєструє неіснуюче постійне лінійне прискорення. Для боротьби з конічними та гребковими ефектами розрахунок орієнтації та компенсації гравітації виносять у високопріоритетне апаратне переривання таймера з частотою від 500 Гц до 2 кГц, застосовуючи багатокрокові алгоритми компенсації Бортца.

### 2. Втрата розрядності чисел із плаваючою комою

При частоті опитування 1 кГц приріст положення за один такт `Δp = v · Δt` при швидкості 1 м/с становить лише `1 мм = 0.001 м`. Якщо для накопичення координат `pos` використовується стандартний 32-бітний тип `float` (формат IEEE 754 з 24 бітами мантиси), то при досягненні відстані `1000 метрів` ціна наймолодшого розряду складає `1000 / 2²⁴ ≈ 0.06 мм`. При подальшому віддаленні від точки старту малі прирости `Δp` починають повністю обнулятися через машинне округлення.

Тому для інтеграторів положення у вбудованих системах діє суворе правило: **кути, швидкість і прискорення обчислюються у `float`, а координати накопичуються виключно у `double` або 64-бітних цілих числах з фіксованою комою**.

### 3. Часова синхронізація та джитер кроку `Δt`

У багатьох недосконалих реалізаціях крок часу `dt` задається фіксованою константою (наприклад, `0.01f`). Проте в реальній операційній системі реального часу (FreeRTOS чи PX4 NuttX) періодичність виклику задачі може коливатися на `±10–20%` через переривання від інших периферійних модулів (радіоканал, телеметрія, керування моторами).

Якщо обчислювати інтеграл за фіксованим `dt = 0.01 с`, тоді як реальний проміжок між вимірюваннями становив `0.012 с`, виникає систематична похибка інтегрування швидкості до 20%. Для запобігання цьому на апаратному рівні використовують апаратний лічильник тактів процесора (наприклад, регістр `DWT->CYCCNT` у ядрах ARM Cortex-M) і фіксують точний фізичний час приходу кожного пакету даних від IMU за лінією апаратного переривання Data Ready (DRDY).

### 4. Ортогоналізація матриці повороту та стабільність норми кватерніона

Навіть за наявності нормалізації на кожному кроці кватерніонні операції через скінченну точність мантиси поступово накопичують неортогональність. Якщо в коді використовується матриця повороту `R`, її періодично (кожні 100–1000 кроків) піддають процедурі ортогоналізації Грама-Шмідта або ітераційному виправленню:

```
R = 1/2 · (R + (R⁻¹)ᵀ) = R − 1/2 · (R · Rᵀ − I) · R
```
