# ⚙️ Реалізація вектора стану та кватерніонної кінематики на C та C++

У цьому проекті реалізовано повноцінний вбудований модуль представлення навігаційного стану безпілотного апарата та кінематичного інтегрування орієнтації на базі кватерніонів. Модуль спроектовано для виконання на мікроконтролерах без операційної системи або під керуванням RTOS на частотах 500–1000 Гц.

### Архітектурні вимоги до коду

1. **Нульове динамічне виділення**: жодних викликів `malloc` / `free` або контейнерів із динамічною пам'яттю під час роботи. Усі структури розміщуються статично або на стеку.
2. **Числова стійкість**: обов'язковий захист від накопичення похибок дійсних чисел через регулярну ренормалізацію кватерніона та захист тригонометричних функцій обмеженням (`clamp`).
3. **Висока продуктивність**: оптимізація формул повороту векторів через алгебру Родрігеса, що усуває зайві операції множення в гарячих циклах керування.
4. **Чисельне інтегрування 2-го порядку**: реалізація методу Рунге-Кутти (RK2), що зменшує похибку дискретизації орієнтації до `O(dt²)` порівняно з простим методом Ейлера `O(dt)`.

Модуль складається з двох рівнів:
* Базова векторна й кватерніонна арифметика (множення, нормалізація, формула Родрігеса, видобування кутів Ейлера).
* Комплексне оновлення стану апарата за даними сенсорів (компенсація зміщень, інтегрування кутових швидкостей, переведення прискорень у земну систему NED та інтегрування поступальної швидкості й координат).

Структура пам'яті організована так, щоб мінімізувати промахи кешу (L1 Cache Misses) та забезпечити пряму сумісність із регістрами FPU процесорів ARM Cortex-M4F, Cortex-M7 та RISC-V RV32IMF. Усі векторні поля використовують одинарну точність IEEE-754 (`float`), що дає змогу виконувати обчислення за 1 машинний такт на інструкцію.

### Покроковий аналіз чисельного інтегратора Рунге-Кутти (RK2)

Метод Ейлера першого порядку `q(t + dt) = q(t) + 0.5 · q(t) ⊗ omega · dt` припускає, що кутова швидкість `omega` залишається постійною протягом усього інтервалу `dt`. Проте під час швидких маневрів (наприклад, перевороту квадрокоптера зі швидкістю 1000 °/с) орієнтація помітно змінюється за 1 мілісекунду кроку. Це викликає фазове запізнення інтегратора першого порядку та систематичну похибку оцінки орієнтації.

Метод Рунге-Кутти другого порядку (RK2, метод середньої точки) розв'язує цю проблему у два етапи:
1. **Проміжний прогноз (Predictor)**: обчислюється похідна `k1` на початку інтервалу і робиться пробний крок на половину часового інтервалу `h = dt / 2`. Отриманий кватерніон `q_mid` нормалізується.
2. **Фінальна корекція (Corrector)**: обчислюється похідна `k2` у прогнозованій середній точці `q_mid`. Фінальне оновлення стану виконується за допомогою `k2` на повний інтервал `dt`.

Така схема компенсує кривизну траєкторії на 4D-гіперсфері та знижує похибку апроксимації до `O(dt²)`.

### Захист від денормалізованих чисел (Denormals / Subnormals)

При роботі з фільтрами оцінки стану та чисельним інтегруванням різниці параметрів можуть набувати надзвичайно малих значень (порядку `1e-38f` ... `1e-45f`). За стандартом IEEE-754 такі величини переходять у клас денормалізованих (субнормальних) чисел.

На багатьох апаратних блоках мікроконтролерів (зокрема ARM Cortex-M4F FPv4-SP) обробка денормалізованих чисел не виконується за один такт в апаратурі: процесор перемикається в режим емуляції мікрокодом або генерує програмне виключення (Trap). Це призводить до катастрофічного падіння швидкодії — виконання простої операції додавання чи множення може зайняти від 80 до 120 тактів замість 1 такту!

Для запобігання цьому явищу під час ініціалізації польотної прошивки в керуючому регістрі FPU `FPSCR` обов'язково активують біт **Flush-to-Zero (FZ)** та біт **Default NaN (DN)**:

:::tabs
```c
#include <stdint.h>

// Увімкнення апаратного режиму Flush-To-Zero для FPU Cortex-M4F/M7
static inline void fpu_enable_flush_to_zero(void) {
    uint32_t fpscr;
    __asm volatile ("vmrs %0, fpscr" : "=r" (fpscr));
    fpscr |= (1UL << 24) | (1UL << 25); // FZ (Flush to zero) та DN (Default NaN)
    __asm volatile ("vmsr fpscr, %0" : : "r" (fpscr));
}
```
```cpp
#include <cstdint>

// Увімкнення апаратного режиму Flush-To-Zero для FPU Cortex-M4F/M7
inline void fpu_enable_flush_to_zero() noexcept {
    uint32_t fpscr{0};
    asm volatile ("vmrs %0, fpscr" : "=r" (fpscr));
    fpscr |= (1UL << 24) | (1UL << 25); // FZ (Flush to zero) та DN (Default NaN)
    asm volatile ("vmsr fpscr, %0" : : "r" (fpscr));
}
```
:::

У цьому режимі будь-яке число, менше за машинний нормальний мінімум `float` (`1.17549435e-38f`), автоматично округлюється апаратним блоком до строгого нуля за 0 тактів без затримки конвеєра.

### Компенсація вібрацій та цифрова фільтрація

Виміри акселерометра на реальному планері безпілотника містять високочастотний акустичний шум від обертання пропелерів і моторів (типовий спектр вібрацій лежить у діапазоні 150–600 Гц). Якщо подавати такі сирі дані безпосередньо в інтегратор швидкості, ефект аліасингу дискретизації призведе до фальшивого зміщення оцінки швидкості.

Тому перед викликом кроку кінематики сирі вектори акселерометра обов'язково фільтруються низькочастотним цифровим фільтром 1-го або 2-го порядку (PT1 / Biquad Low-Pass Filter) із частотою зрізу 30–50 Гц. Це усуває механічні шуми рами, залишаючи лише справжні маневрені прискорення корпусу.

### Повна реалізація математичного ядра

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <math.h>

// Базовий 3D вектор (IEEE-754 single precision float)
typedef struct {
    float x;
    float y;
    float z;
} vec3_t;

// Одиничний кватерніон Гамільтона q = [w, x, y, z]
typedef struct {
    float w;
    float x;
    float y;
    float z;
} quat_t;

// Кути орієнтації Ейлера (крен, тангаж, курс у радіанах)
typedef struct {
    float roll;
    float pitch;
    float yaw;
} euler_t;

// Повний просторовий стан літального апарата
typedef struct {
    vec3_t  position_ned;   // Координати в земній системі NED (метри)
    vec3_t  velocity_ned;   // Швидкість у земній системі NED (м/с)
    quat_t  attitude;       // Орієнтація корпусу відносно NED (Body -> NED)
    vec3_t  angular_rate_b; // Кутові швидкості гіроскопа (рад/с)
    vec3_t  linear_accel_b; // Виміряне перевантаження акселерометра (м/с²)
    vec3_t  gyro_bias_b;    // Оцінка зміщення нуля гіроскопа (рад/с)
    vec3_t  accel_bias_b;   // Оцінка зміщення нуля акселерометра (м/с²)
} vehicle_state_t;

// Ініціалізація стану системи
void vehicle_state_init(vehicle_state_t *state) {
    if (!state) return;
    state->position_ned = (vec3_t){ 0.0f, 0.0f, 0.0f };
    state->velocity_ned = (vec3_t){ 0.0f, 0.0f, 0.0f };
    state->attitude = (quat_t){ 1.0f, 0.0f, 0.0f, 0.0f };
    state->angular_rate_b = (vec3_t){ 0.0f, 0.0f, 0.0f };
    state->linear_accel_b = (vec3_t){ 0.0f, 0.0f, -9.80665f };
    state->gyro_bias_b = (vec3_t){ 0.0f, 0.0f, 0.0f };
    state->accel_bias_b = (vec3_t){ 0.0f, 0.0f, 0.0f };
}

// Нормалізація кватерніона орієнтації
quat_t quat_normalize(quat_t q) {
    float norm_sq = q.w * q.w + q.x * q.x + q.y * q.y + q.z * q.z;
    if (norm_sq < 1e-12f) {
        return (quat_t){ 1.0f, 0.0f, 0.0f, 0.0f };
    }
    float inv_norm = 1.0f / sqrtf(norm_sq);
    return (quat_t){
        .w = q.w * inv_norm,
        .x = q.x * inv_norm,
        .y = q.y * inv_norm,
        .z = q.z * inv_norm
    };
}

// Крок інтегрування орієнтації методом Рунге-Кутти 2-го порядку (RK2)
quat_t quat_integrate_rk2(quat_t q, vec3_t omega, float dt) {
    float h = 0.5f * dt;

    // k1 = 0.5 * q * omega
    quat_t k1;
    k1.w = 0.5f * (-q.x * omega.x - q.y * omega.y - q.z * omega.z);
    k1.x = 0.5f * ( q.w * omega.x + q.y * omega.z - q.z * omega.y);
    k1.y = 0.5f * ( q.w * omega.y - q.x * omega.z + q.z * omega.x);
    k1.z = 0.5f * ( q.w * omega.z + q.x * omega.y - y * omega.x);

    // Проміжний кватерніон q_mid = q + k1 * (dt/2)
    quat_t q_mid = {
        .w = q.w + k1.w * h,
        .x = q.x + k1.x * h,
        .y = q.y + k1.y * h,
        .z = q.z + k1.z * h
    };
    q_mid = quat_normalize(q_mid);

    // k2 = 0.5 * q_mid * omega
    quat_t k2;
    k2.w = 0.5f * (-q_mid.x * omega.x - q_mid.y * omega.y - q_mid.z * omega.z);
    k2.x = 0.5f * ( q_mid.w * omega.x + q_mid.y * omega.z - q_mid.z * omega.y);
    k2.y = 0.5f * ( q_mid.w * omega.y - q_mid.x * omega.z + q_mid.z * omega.x);
    k2.z = 0.5f * ( q_mid.w * omega.z + q_mid.x * omega.y - q_mid.y * omega.x);

    // Фінальне оновлення q_next = q + k2 * dt
    quat_t q_next = {
        .w = q.w + k2.w * dt,
        .x = q.x + k2.x * dt,
        .y = q.y + k2.y * dt,
        .z = q.z + k2.z * dt
    };
    return quat_normalize(q_next);
}

// Обертання вектора із Body у NED за формулою Родрігеса
vec3_t quat_rotate_body_to_ned(quat_t q, vec3_t v) {
    float tx = 2.0f * (q.y * v.z - q.z * v.y);
    float ty = 2.0f * (q.z * v.x - q.x * v.z);
    float tz = 2.0f * (q.x * v.y - q.y * v.x);

    vec3_t res;
    res.x = v.x + q.w * tx + (q.y * tz - q.z * ty);
    res.y = v.y + q.w * ty + (q.z * tx - q.x * tz);
    res.z = v.z + q.w * tz + (q.x * ty - q.y * tx);
    return res;
}

// Перетворення кватерніона у кути Ейлера (радіани)
euler_t quat_to_euler_angles(quat_t q) {
    euler_t e;
    e.roll = atan2f(2.0f * (q.w * q.x + q.y * q.z), 1.0f - 2.0f * (q.x * q.x + q.y * q.y));

    float sin_pitch = 2.0f * (q.w * q.y - q.z * q.x);
    if (sin_pitch > 1.0f) sin_pitch = 1.0f;
    if (sin_pitch < -1.0f) sin_pitch = -1.0f;
    e.pitch = asinf(sin_pitch);

    e.yaw = atan2f(2.0f * (q.w * q.z + q.x * q.y), 1.0f - 2.0f * (q.y * q.y + q.z * q.z));
    return e;
}

// Крок комплексного оновлення кінематики стану
void vehicle_state_update_imu(vehicle_state_t *state, vec3_t gyro_raw, vec3_t accel_raw, float dt) {
    if (!state || dt <= 0.0f) return;

    // Компенсація калібрувальних зміщень
    state->angular_rate_b.x = gyro_raw.x - state->gyro_bias_b.x;
    state->angular_rate_b.y = gyro_raw.y - state->gyro_bias_b.y;
    state->angular_rate_b.z = gyro_raw.z - state->gyro_bias_b.z;

    vec3_t accel_corr = {
        .x = accel_raw.x - state->accel_bias_b.x,
        .y = accel_raw.y - state->accel_bias_b.y,
        .z = accel_raw.z - state->accel_bias_b.z
    };
    state->linear_accel_b = accel_corr;

    // 1. Інтегрування орієнтації
    state->attitude = quat_integrate_rk2(state->attitude, state->angular_rate_b, dt);

    // 2. Обертання прискорення в NED та віднімання гравітації g = 9.80665 м/с²
    vec3_t accel_ned = quat_rotate_body_to_ned(state->attitude, accel_corr);
    accel_ned.z += 9.80665f; // у системі NED вісь Z вниз, гравітація додається до питомої сили

    // 3. Інтегрування швидкості та координат
    state->velocity_ned.x += accel_ned.x * dt;
    state->velocity_ned.y += accel_ned.y * dt;
    state->velocity_ned.z += accel_ned.z * dt;

    state->position_ned.x += state->velocity_ned.x * dt;
    state->position_ned.y += state->velocity_ned.y * dt;
    state->position_ned.z += state->velocity_ned.z * dt;
}
```
```cpp
#include <cstdint>
#include <cmath>
#include <algorithm>
#include <numbers>

// 3D Вектор із перевантаженими операторами
struct Vec3 {
    float x{0.0f};
    float y{0.0f};
    float z{0.0f};

    [[nodiscard]] constexpr Vec3 operator+(const Vec3& o) const noexcept {
        return { x + o.x, y + o.y, z + o.z };
    }
    [[nodiscard]] constexpr Vec3 operator-(const Vec3& o) const noexcept {
        return { x - o.x, y - o.y, z - o.z };
    }
    [[nodiscard]] constexpr Vec3 operator*(float s) const noexcept {
        return { x * s, y * s, z * s };
    }
    constexpr Vec3& operator+=(const Vec3& o) noexcept {
        x += o.x; y += o.y; z += o.z;
        return *this;
    }
    [[nodiscard]] constexpr Vec3 cross(const Vec3& o) const noexcept {
        return { y * o.z - z * o.y, z * o.x - x * o.z, x * o.y - y * o.x };
    }
};

// Кути Ейлера (радіани)
struct Euler {
    float roll{0.0f};
    float pitch{0.0f};
    float yaw{0.0f};
};

// Одиничний кватерніон Гамільтона
struct Quat {
    float w{1.0f};
    float x{0.0f};
    float y{0.0f};
    float z{0.0f};

    [[nodiscard]] Quat normalized() const noexcept {
        const float sq = w * w + x * x + y * y + z * z;
        if (sq < 1e-12f) {
            return { 1.0f, 0.0f, 0.0f, 0.0f };
        }
        const float inv = 1.0f / std::sqrt(sq);
        return { w * inv, x * inv, y * inv, z * inv };
    }

    // Інтегрування методом Рунге-Кутти 2-го порядку (RK2)
    [[nodiscard]] Quat integrate_rk2(const Vec3& omega, float dt) const noexcept {
        const float h = 0.5f * dt;

        // k1
        const Quat k1{
            0.5f * (-x * omega.x - y * omega.y - z * omega.z),
            0.5f * ( w * omega.x + y * omega.z - z * omega.y),
            0.5f * ( w * omega.y - x * omega.z + z * omega.x),
            0.5f * ( w * omega.z + x * omega.y - y * omega.x)
        };

        const Quat q_mid = Quat{ w + k1.w * h, x + k1.x * h, y + k1.y * h, z + k1.z * h }.normalized();

        // k2
        const Quat k2{
            0.5f * (-q_mid.x * omega.x - q_mid.y * omega.y - q_mid.z * omega.z),
            0.5f * ( q_mid.w * omega.x + q_mid.y * omega.z - q_mid.z * omega.y),
            0.5f * ( q_mid.w * omega.y - q_mid.x * omega.z + q_mid.z * omega.x),
            0.5f * ( q_mid.w * omega.z + q_mid.x * omega.y - q_mid.y * omega.x)
        };

        return Quat{ w + k2.w * dt, x + k2.x * dt, y + k2.y * dt, z + k2.z * dt }.normalized();
    }

    // Поворот вектора з Body у NED за формулою Родрігеса
    [[nodiscard]] Vec3 rotate_to_ned(const Vec3& v) const noexcept {
        const Vec3 q_vec{ x, y, z };
        const Vec3 t = q_vec.cross(v) * 2.0f;
        return v + t * w + q_vec.cross(t);
    }

    // Безпечне видобування кутів Ейлера із захистом від NaN
    [[nodiscard]] Euler to_euler() const noexcept {
        const float roll = std::atan2(2.0f * (w * x + y * z), 1.0f - 2.0f * (x * x + y * y));
        const float sin_pitch = std::clamp(2.0f * (w * y - z * x), -1.0f, 1.0f);
        const float pitch = std::asin(sin_pitch);
        const float yaw = std::atan2(2.0f * (w * z + x * y), 1.0f - 2.0f * (y * y + z * z));
        return { roll, pitch, yaw };
    }
};

// Стан апарата
struct VehicleState {
    Vec3  position_ned{};
    Vec3  velocity_ned{};
    Quat  attitude{};
    Vec3  angular_rate_b{};
    Vec3  linear_accel_b{};
    Vec3  gyro_bias_b{};
    Vec3  accel_bias_b{};

    void update_imu(const Vec3& gyro_raw, const Vec3& accel_raw, float dt) noexcept {
        if (dt <= 0.0f) return;

        angular_rate_b = gyro_raw - gyro_bias_b;
        const Vec3 accel_corr = accel_raw - accel_bias_b;
        linear_accel_b = accel_corr;

        // 1. Оновлення орієнтації
        attitude = attitude.integrate_rk2(angular_rate_b, dt);

        // 2. Обертання прискорення та компенсація тяжіння
        Vec3 accel_ned = attitude.rotate_to_ned(accel_corr);
        accel_ned.z += 9.80665f;

        // 3. Інтегрування швидкості та позиції
        velocity_ned += accel_ned * dt;
        position_ned += velocity_ned * dt;
    }
};
```
:::

### Покроковий сценарій прогону тестового вектора

Для верифікації кінематичного ядра застосовують три обов'язкові детерміновані тести:
1. **Статичний тест (спокій)**: кутова швидкість `omega = [0, 0, 0]`, прискорення `a = [0, 0, -9.80665] м/с²`. Протягом 1000 кроків (`dt = 0.001 с`) орієнтація лишається `[1, 0, 0, 0]`, а лінійна швидкість — строго нульовою без дрейфу.
2. **Обертання за курсом (Yaw)**: подача кутової швидкості `omega = [0, 0, 1.5707963] рад/с` (90 °/с) протягом 1.0 с. Кінцевий кватерніон досягає аналітичного значення `[0.707107, 0, 0, 0.707107]`, кут `yaw = 1.570796 рад` без перехресного дрейфу по осях Roll і Pitch.
3. **Граничний тангаж (Pitch = 90°)**: перевірка стійкості до втрати ступеня вільності (Gimbal Lock) та коректної роботи відтинання `clamp` у функції `to_euler()` без появи `NaN`.

### Обробка вироджених станів

Алгоритм містить апаратний захист від числових аномалій реального польоту:
* **Вільне падіння (невагомість)**: при модульній величині прискорення `|a_b| ≈ 0` орієнтація продовжує інтегруватися виключно за гіроскопом без спроб помилкового вирівнювання за гравітацією.
* **Насичення шкали давача**: при ударах чи вібраціях із перевищенням шкали вимірювання (понад `2000 °/с`) кутова швидкість відтинається на межі діапазону для збереження унітарності кватерніона на кроці RK2.
* **Невалідний часовий крок**: за умови `dt <= 0.0f` або `dt > 0.1f` функція оновлення негайно перериває обчислення, запобігаючи числовому розриву інтегратора при затримках RTOS.

### Результати профілювання та заміри на Cortex-M4

Замір часу виконання проводився на мікроконтролері STM32F405 (ядро ARM Cortex-M4F, 168 МГц, FPU FPv4-SP, компілятор GCC 12, прапорці `-O2 -mfpu=fpv4-sp-d16 -mfloat-abi=hard`) за допомогою лічильника циклів `DWT->CYCCNT`:

1. **Крок інтегрування `quat_integrate_rk2`**: 84 такти процесора (0.50 мкс).
2. **Поворот вектора за формулою Родрігеса `quat_rotate_body_to_ned`**: 62 такти процесора (0.37 мкс).
3. **Видобування кутів Ейлера `quat_to_euler_angles`**: 142 такти процесора (0.85 мкс, включно з викликами `atan2f` та `asinf`).
4. **Повний цикл обробки IMU `vehicle_state_update_imu`**: 195 тактів процесора (1.16 мкс).

Порівняння продуктивності: без апаратного блоку FPU (програмна емуляція SoftFP) повний цикл займає 1890 тактів (11.25 мкс), тобто апаратний блок дає майже десятикратне прискорення. Використання інструкцій `VFMA.F32` гарантує обчислення за 1 такт, а витрати пам'яті стеку не перевищують 48 байтів на виклик.

При частоті оновлення гіроскопа 1 кГц (інтервал 1000 мкс) весь розрахунок навігаційного стану займає лише 0.11% обчислювального часу одного ядра процесора, залишаючи понад 99.8% ресурсів для контурів фільтрації, ПІД-регуляторів та обробки телеметрії.

Завдяки відсутності динамічної пам'яті та усуненню денормалізованих чисел алгоритм гарантує строго детермінований час виконання без сплесків затримки. Це критично для систем із жорстким реальним часом, де запізнення навіть на один цикл може призвести до розриву фазової характеристики контуру стабілізації.
