# ⚙️ Бібліотека прямої та зворотної кінематики стабілізатора на C та C++

У системах оптико-електронного спостереження безпілотних апаратів, роботів та гіростабілізованих платформ тривісний безколекторний підвіс розв'язує дві фундаментальні задачі просторової геометрії:
1. **Пряма кінематика (Forward Kinematics)**: за поточними кутами моторів підвісу `(yaw, pitch, roll)` та інерціальною орієнтацією корпусу апарата визначити точний вектор візування камери у світових координатах (для геоприв'язки пікселів зображення до карти місцевості та розрахунку координат цілей).
2. **Зворотна кінематика та цілевказівка (Inverse Kinematics / Targeting)**: за географічними координатами цілі або бажаним інерціальним вектором погляду розрахувати необхідні кути для кожного з трьох моторів підвісу, миттєво компенсуючи крен, рискання та тангаж фюзеляжу літака.

Нижче наведено повну модульну бібліотеку перетворення координат та кінематики підвісу з аналітичним розрахунком матриць обертання, кватерніонним обчисленням помилки неузгодженості, захистом від сингулярності карданового замка та взаємною компенсацією поворотів носія.

## 1. Архітектура та математична модель перетворень

Підвіс розглядається як ланцюг із трьох послідовних поворотів за авіаційним стандартом Z-Y-X (Тейта–Браяна):
- **Рискання** `ψ` (зовнішній мотор) навколо осі Z корпусу.
- **Тангаж** `θ` (середній мотор) навколо повернутої осі Y.
- **Крен** `φ` (внутрішній мотор) навколо двічі поверненої осі X камери.

Взаємозв'язок між системою координат корпусу апарата `F_body`, системою координат підвісу `F_gimbal` та світовою навігаційною системою `F_world` (NED: North-East-Down) виражається матричними добутками:

```
R_cam = R_body · R_gimbal(ψ, θ, φ)
R_gimbal = R_bodyᵀ · R_cam
```

Якщо оптична вісь камери у власній рамці спрямована вздовж осі `X = [1, 0, 0]ᵀ`, то одиничний вектор напрямку погляду у світовому просторі `v_world` є першим стовпчиком повної матриці орієнтації `R_cam`.

### Геоприв'язка та цілевказівка (Targeting Pipeline)

Пайплайн наведення камери на наземний об'єкт складається з таких послідовних кроків:
1. **Розрахунок вектора лінії візування (Line of Sight, LOS)** у світовій системі координат:
```
v_target_world = (P_target − P_uav) / ‖P_target − P_uav‖
```
2. **Трансформація у власну рамку корпусу літака**:
```
v_body = R_bodyᵀ · v_target_world
```
3. **Аналітичне витягнення кутів підвісу**:
```
ψ_cmd = atan2(v_body.y, v_body.x)
θ_cmd = atan2(−v_body.z, √(v_body.x² + v_body.y²))
φ_cmd = 0  (для утримання лінії горизонту строго паралельно землі)
```

## 2. Кватерніонний розрахунок помилки стабілізації

Традиційний підхід обчислення помилки через різницю кутів Ейлера `e_euler = angles_target - angles_current` страждає на взаємний перехресний зв'язок осей та фазові стрибки на межах `±180°`. У високоточних контурах стабілізації бажану орієнтацію камери задають кватерніоном `q_desired`, а поточну орієнтацію платформи оцінюють кватерніоном `q_current`.

Кватерніон просторової помилки `q_error` розраховується як:

```
q_error = q_current* ⊗ q_desired = [q_e0,  q_evᵀ]ᵀ
```

Тривимірний вектор кутової помилки для векторного ПІД-регулятора швидкості формується без жодної тригонометричної функції:

```
e_rot = 2 · sgn(q_e0) · q_ev
```

Множник `sgn(q_e0)` гарантує вибір найкоротшого шляху повороту на одиничній сфері `S³` (оскільки кватерніони `q` та `−q` описують однаковий поворот у `SO(3)`). Отриманий вектор `e_rot` прямо задає миттєву вісь та кут неузгодженості, які подаються на внутрішній швидкісний контур двигунів.

## 3. Профілювання швидкості та обмеження ривків (Rate & S-Curve Limiting)

При миттєвій зміні цілевказівки (наприклад, перемиканні камери на нову розвідувальну ціль) ступінчаста зміна кутів викликає різкий стрибок похідної (*derivative kick*) та кидок струму в обмотках безколекторних моторів, що призводить до вібрацій конструкції та розмиття кадру.

Для запобігання перевантаженням у бібліотеку інтегрують трапецеподібний обмежувач швидкості та прискорення (*Rate Limiter*):
- Максимальна кутова швидкість перекидання: `ω_max ≈ 120–300°/с`.
- Максимальне кутове прискорення: `α_max ≈ 500–1500°/с²`.

На кожному кроці дискретизації `Δt` цільовий кут зміщується не стрибком, а плавно прирощується з урахуванням поточного обмеження прискорення та гальмівного шляху до цілі.

## 4. Реалізація бібліотеки на C та C++

У коді реалізовано:
- Побудову матриці обертання підвісу за кутами Ейлера `(yaw, pitch, roll)`.
- Пряму кінематику: розрахунок вектора лінії візування у світовій рамці.
- Зворотну кінематику: розрахунок цільових кутів моторів для супроводу світового вектора.
- Інерціальну компенсацію збурень корпусу: розрахунок матриці підвісу `R_g = R_bodyᵀ · R_desired`.
- Аналітичне витягнення кутів із матриці з детектуванням наближення до карданового замка (`|θ| > 88°`).

:::tabs
```c
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
```
```cpp
#include <array>
#include <cmath>
#include <numbers>
#include <optional>

namespace gimbal {

constexpr float Pi = std::numbers::pi_v<float>;
constexpr float PitchLimit = 88.0f * Pi / 180.0f;

struct Vec3 {
    float x{0.0f};
    float y{0.0f};
    float z{0.0f};

    [[nodiscard]] constexpr float norm() const noexcept {
        return std::sqrt(x * x + y * y + z * z);
    }

    [[nodiscard]] Vec3 normalized() const noexcept {
        const float n = norm();
        if (n < 1e-6f) {
            return Vec3{1.0f, 0.0f, 0.0f};
        }
        return Vec3{x / n, y / n, z / n};
    }
};

struct Angles {
    float yaw{0.0f};    // ψ навколо Z, радіани
    float pitch{0.0f};  // θ навколо Y, радіани
    float roll{0.0f};   // φ навколо X, радіани
};

class Mat3 {
public:
    std::array<std::array<float, 3>, 3> data{};

    constexpr Mat3() noexcept = default;

    [[nodiscard]] static Mat3 from_euler(const Angles& a) noexcept {
        const float cy = std::cos(a.yaw),   sy = std::sin(a.yaw);
        const float cp = std::cos(a.pitch), sp = std::sin(a.pitch);
        const float cr = std::cos(a.roll),  sr = std::sin(a.roll);

        Mat3 r;
        r.data[0][0] = cy * cp;
        r.data[0][1] = cy * sp * sr - sy * cr;
        r.data[0][2] = cy * sp * cr + sy * sr;

        r.data[1][0] = sy * cp;
        r.data[1][1] = sy * sp * sr + cy * cr;
        r.data[1][2] = sy * sp * cr - cy * sr;

        r.data[2][0] = -sp;
        r.data[2][1] = cp * sr;
        r.data[2][2] = cp * cr;
        return r;
    }

    [[nodiscard]] Mat3 transpose() const noexcept {
        Mat3 r;
        for (size_t i = 0; i < 3; ++i) {
            for (size_t j = 0; j < 3; ++j) {
                r.data[i][j] = data[j][i];
            }
        }
        return r;
    }

    [[nodiscard]] Angles to_euler() const noexcept {
        Angles out;
        float sp = -data[2][0];
        if (sp > 1.0f) sp = 1.0f;
        if (sp < -1.0f) sp = -1.0f;

        out.pitch = std::asin(sp);

        if (std::abs(out.pitch) > PitchLimit) {
            out.roll = 0.0f;
            out.yaw = std::atan2(-data[0][1], data[1][1]);
            return out;
        }

        out.roll = std::atan2(data[2][1], data[2][2]);
        out.yaw = std::atan2(data[1][0], data[0][0]);
        return out;
    }

    [[nodiscard]] friend Mat3 operator*(const Mat3& a, const Mat3& b) noexcept {
        Mat3 r;
        for (size_t i = 0; i < 3; ++i) {
            for (size_t j = 0; j < 3; ++j) {
                r.data[i][j] = a.data[i][0] * b.data[0][j] +
                               a.data[i][1] * b.data[1][j] +
                               a.data[i][2] * b.data[2][j];
            }
        }
        return r;
    }

    [[nodiscard]] friend Vec3 operator*(const Mat3& m, const Vec3& v) noexcept {
        return Vec3{
            m.data[0][0] * v.x + m.data[0][1] * v.y + m.data[0][2] * v.z,
            m.data[1][0] * v.x + m.data[1][1] * v.y + m.data[1][2] * v.z,
            m.data[2][0] * v.x + m.data[2][1] * v.y + m.data[2][2] * v.z
        };
    }
};

/* Пряма кінематика: розрахунок вектора лінії візування камери у світових координатах */
[[nodiscard]] inline Vec3 forward_kinematics(const Mat3& body_rot, const Angles& gimbal_angles) noexcept {
    const Mat3 gimbal_rot = Mat3::from_euler(gimbal_angles);
    const Mat3 cam_rot = body_rot * gimbal_rot;
    return cam_rot * Vec3{1.0f, 0.0f, 0.0f};
}

/* Зворотна кінематика: розрахунок кутів підвісу для спрямування камери на ціль */
[[nodiscard]] inline Angles inverse_targeting(const Mat3& body_rot, const Vec3& target_world) noexcept {
    const Mat3 body_inv = body_rot.transpose();
    const Vec3 target_norm = target_world.normalized();
    const Vec3 v_body = body_inv * target_norm;

    Angles angles;
    angles.yaw = std::atan2(v_body.y, v_body.x);
    
    const float hyp = std::sqrt(v_body.x * v_body.x + v_body.y * v_body.y);
    angles.pitch = std::atan2(-v_body.z, hyp);
    angles.roll = 0.0f;

    if (angles.pitch > PitchLimit) angles.pitch = PitchLimit;
    if (angles.pitch < -PitchLimit) angles.pitch = -PitchLimit;

    return angles;
}

/* Компенсація збурень корпусу: знаходження кутів підвісу для збереження інерціального положення */
[[nodiscard]] inline Angles stabilize_attitude(const Mat3& body_rot, const Mat3& desired_world_rot) noexcept {
    const Mat3 gimbal_rot = body_rot.transpose() * desired_world_rot;
    return gimbal_rot.to_euler();
}

} // namespace gimbal
```
:::

## 5. Інженерні пастки та крайові випадки вбудованого ПЗ

1. **Фазовий розрив на межі `[−π, +π]` (Angle Wrapping)**:
   Функція `atan2` повертає кути в діапазоні `(−π, π]`. Коли апарат перетинає напрямок на південь (180°), значення кута миттєво стрибає з `+3.14` на `−3.14`. Якщо передати цю різницю в пропорційний контур ПІД-регулятора напряму `e = target - current`, мотор спробує здійснити оберт на 359° замість найкоротшого повороту на 1°. Помилка кута обов'язково повинна нормалізуватися:
   ```
   error = atan2f(sinf(target - current), cosf(target - current))
   ```

2. **Втрата курсу в зенітній та надирній зонах (Nadir Blindspot)**:
   Коли ціль розташована строго під апаратом (`v_body.z ≈ −1.0`), проєкція вектора на горизонтальну площину `hyp = √(v_bx² + v_by²) → 0`. Кут `yaw` втрачає стійкість: шум акселерометра в соті частки g розвертає цільове рискання на 180°. У реальному прошиванні при `hyp < 0.05` алгоритм блокує зміну кута рискання, залишаючи попереднє значення курсу та керуючи виключно мотором тангажу.

3. **Компенсація транспортної затримки (Transport Latency Compensation)**:
   Польотний контролер передає оцінку орієнтації `R_body` на плату підвісу через цифрову шину (CAN, UART) із затримкою `t_delay ≈ 5–20 мс`. Якщо підвіс намагається компенсувати застарілу орієнтацію, виникає позитивний фазовий зсув, що розгойдує систему. Перед обчисленням матриці `R_g` поточну орієнтацію апарата екстраполюють уперед за виміряною гіроскопом кутовою швидкістю:
   ```
   R_body(t + t_delay) ≈ R_body(t) · (I + [ω_body ×] · t_delay)
   ```

4. **Ортогоналізація матриць орієнтації**:
   Числове інтегрування з рухомою комою одинарної точності (`float32`) порушує ортогональність матриці `Rᵀ · R = I`. Матрицю `R_body` необхідно періодично (кожні 100 циклів) ренормалізувати або переходити до розрахунків виключно в одиничних кватерніонах.
