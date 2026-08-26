# ⚙️ Практичний драйвер 6-DOF фільтра Махоні на мікроконтролері

У реальних автопілотах безпілотних літальних апаратів і контролерах робототехніки орієнтаційний фільтр виконується у виділеній високопріоритетній задачі операційної системи реального часу (RTOS) або безпосередньо в обробнику апаратного переривання готовності даних датчика (DRDY — Data Ready) із фіксованою частотою від 500 Гц до 2 кГц.

Повна реалізація бортового оцінювача орієнтації складається з чотирьох послідовних етапів:
1. **Статичне калібрування початкового зміщення нуля гіроскопа** під час увімкнення живлення апарата.
2. **Селективна фільтрація прискорень (Acceleration Gating)** для відсікання лінійних перевантажень під час маневрів.
3. **Обчислення пропорційно-інтегральної корекції орієнтації** у системі координат корпусу.
4. **Чисельне інтегрування та перенормування кватерніона стану**.

### Процедура передпольотного калібрування нуля гіроскопа

Під час старту апарата прошивка зобов'язана оцінити початкове зміщення нуля (англ. *static bias*). Якщо дрон у цей момент рухається або тремтить на вітрі, калібрування зафіксує хибне зміщення, що призведе до катастрофічного перекидання після зльоту.

Процедура передпольотної ініціалізації працює за таким алгоритмом:
1. Накопичується масив із 1000 послідовних вимірювань гіроскопа з інтервалом 1 мс (загальна тривалість 1 секунда).
2. Обчислюється вибіркова дисперсія (варіація) вимірів за кожною з трьох осей:

```
var_axis = (1 / N) · ∑ (ω_raw[i] - mean_ω)²
```

3. Якщо дисперсія за будь-якою віссю перевищує поріг спокою (наприклад, `var > 0.0005 (рад/с)²`), станція фіксує рух платформи, скидає накопичувач і починає вимірювання спочатку.
4. Якщо дисперсія в межах норми, середні значення `mean_ω_x, mean_ω_y, mean_ω_z` фіксуються в енергонезалежній структурі як сталі зміщення нуля `b_0` і віднімаються від кожного наступного «сирого» відліку датчика.

### Динамічний гейтинг прискорень (Acceleration Gating)

У польоті, коли дрон різко прискорюється вперед, гальмує або входить у крутий віраж, повний модуль вектора питомої сили суттєво відхиляється від стандартного земного прискорення 1.0 g (9.81 м/с²). Якщо подати такий вектор в орієнтаційний фільтр, він змістить оцінку вертикалі в бік вектора лінійного прискорення.

Тому алгоритм перевіряє умову довіри до акселерометра:

```
0.85 g ≤ ‖a_meas‖ ≤ 1.15 g
```

Якщо довжина вектора виходить за межі цього діапазону (наприклад, під час різкого набору висоти прискорення становить 1.8 g), вага корекції акселерометра динамічно зменшується або повністю обнуляється (`halfex = halfey = halfez = 0`). Автопілот тимчасово утримує оцінку просторової орієнтації виключно за рахунок інтегрування гіроскопа доти, доки перевантаження не повернеться до одиничного гравітаційного значення.

### Реалізація 6-DOF фільтра Махоні

Нижче наведено оптимізовану для вбудованих систем реалізацію 6-осьового орієнтаційного фільтра Махоні з пропорційно-інтегральною компенсацією дрейфу гіроскопа.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <math.h>

typedef struct {
    float q0, q1, q2, q3;    /* Одиничний кватерніон орієнтації */
    float integralFBx;       /* Інтегратор похибки осі X (компенсація bias) */
    float integralFBy;       /* Інтегратор похибки осі Y */
    float integralFBz;       /* Інтегратор похибки осі Z */
    float twoKp;             /* Подвоєний пропорційний коефіцієнт (2 * Kp) */
    float twoKi;             /* Подвоєний інтегральний коефіцієнт (2 * Ki) */
} MahonyFilter_t;

static inline float inv_sqrtf(float x) {
    return 1.0f / sqrtf(x);
}

void mahony_init(MahonyFilter_t *filter, float kp, float ki) {
    filter->q0 = 1.0f;
    filter->q1 = 0.0f;
    filter->q2 = 0.0f;
    filter->q3 = 0.0f;
    filter->integralFBx = 0.0f;
    filter->integralFBy = 0.0f;
    filter->integralFBz = 0.0f;
    filter->twoKp = 2.0f * kp;
    filter->twoKi = 2.0f * ki;
}

void mahony_update_6dof(MahonyFilter_t *filter,
                        float gx, float gy, float gz,
                        float ax, float ay, float az,
                        float dt) {
    float recipNorm;
    float halfvx, halfvy, halfvz;
    float halfex, halfey, halfez;
    float qa, qb, qc;

    /* 1. Перевірка валідності вектора акселерометра */
    float a_norm_sq = ax * ax + ay * ay + az * az;
    if (a_norm_sq > 0.0001f) {
        /* Нормалізація вимірів акселерометра */
        recipNorm = inv_sqrtf(a_norm_sq);
        ax *= recipNorm;
        ay *= recipNorm;
        az *= recipNorm;

        /* Динамічний гейтинг прискорень: перевірка діапазону 0.8g .. 1.2g */
        float a_mag = 1.0f / recipNorm;
        if (a_mag > 0.80f && a_mag < 1.20f) {
            /* Очікуваний напрямок гравітації у зв'язаній системі координат */
            halfvx = filter->q1 * filter->q3 - filter->q0 * filter->q2;
            halfvy = filter->q0 * filter->q1 + filter->q2 * filter->q3;
            halfvz = filter->q0 * filter->q0 - 0.5f + filter->q3 * filter->q3;

            /* Векторний добуток виміряного та очікуваного векторів гравітації */
            halfex = (ay * halfvz - az * halfvy);
            halfey = (az * halfvx - ax * halfvz);
            halfez = (ax * halfvy - ay * halfvx);

            /* Інтегральна складова корекції гіроскопа (bias tracking) */
            if (filter->twoKi > 0.0f) {
                filter->integralFBx += filter->twoKi * halfex * dt;
                filter->integralFBy += filter->twoKi * halfey * dt;
                filter->integralFBz += filter->twoKi * halfez * dt;
                gx += filter->integralFBx;
                gy += filter->integralFBy;
                gz += filter->integralFBz;
            }

            /* Пропорційна складова корекції */
            gx += filter->twoKp * halfex;
            gy += filter->twoKp * halfey;
            gz += filter->twoKp * halfez;
        }
    }

    /* 2. Інтегрування рівняння кінематики кватерніона */
    gx *= (0.5f * dt);
    gy *= (0.5f * dt);
    gz *= (0.5f * dt);
    qa = filter->q0;
    qb = filter->q1;
    qc = filter->q2;

    filter->q0 += (-qb * gx - qc * gy - filter->q3 * gz);
    filter->q1 += ( qa * gx + qc * gz - filter->q3 * gy);
    filter->q2 += ( qa * gy - qb * gz + filter->q3 * gx);
    filter->q3 += ( qa * gz + qb * gy - qc * gx);

    /* 3. Унітарна нормалізація кватерніона */
    recipNorm = inv_sqrtf(filter->q0 * filter->q0 +
                          filter->q1 * filter->q1 +
                          filter->q2 * filter->q2 +
                          filter->q3 * filter->q3);
    filter->q0 *= recipNorm;
    filter->q1 *= recipNorm;
    filter->q2 *= recipNorm;
    filter->q3 *= recipNorm;
}

void mahony_get_euler(const MahonyFilter_t *filter, float *roll, float *pitch, float *yaw) {
    float q0 = filter->q0, q1 = filter->q1, q2 = filter->q2, q3 = filter->q3;
    *roll  = atan2f(2.0f * (q0 * q1 + q2 * q3), 1.0f - 2.0f * (q1 * q1 + q2 * q2));
    *pitch = asinf(2.0f * (q0 * q2 - q3 * q1));
    *yaw   = atan2f(2.0f * (q0 * q3 + q1 * q2), 1.0f - 2.0f * (q2 * q2 + q3 * q3));
}
```
```cpp
#include <array>
#include <cmath>
#include <concepts>
#include <numbers>
#include <algorithm>

struct EulerAngles {
    float roll{};   // Крен (рад)
    float pitch{};  // Тангаж (рад)
    float yaw{};    // Курс (рад)
};

struct Quaternion {
    float w{1.0f};
    float x{0.0f};
    float y{0.0f};
    float z{0.0f};

    [[nodiscard]] constexpr float normSquare() const noexcept {
        return w * w + x * x + y * y + z * z;
    }

    void normalize() noexcept {
        const float invNorm = 1.0f / std::sqrt(normSquare());
        w *= invNorm;
        x *= invNorm;
        y *= invNorm;
        z *= invNorm;
    }
};

class MahonyAttitudeFilter {
public:
    explicit constexpr MahonyAttitudeFilter(float kp = 1.0f, float ki = 0.05f) noexcept
        : twoKp_{2.0f * kp}, twoKi_{2.0f * ki} {}

    void update(const std::array<float, 3>& gyroRadSec,
                const std::array<float, 3>& accelG,
                float dt) noexcept {
        float gx = gyroRadSec[0];
        float gy = gyroRadSec[1];
        float gz = gyroRadSec[2];
        float ax = accelG[0];
        float ay = accelG[1];
        float az = accelG[2];

        const float aNormSq = ax * ax + ay * ay + az * az;
        if (aNormSq > 0.0001f) {
            const float recipNorm = 1.0f / std::sqrt(aNormSq);
            ax *= recipNorm;
            ay *= recipNorm;
            az *= recipNorm;

            const float aMag = 1.0f / recipNorm;
            // Динамічний гейтинг прискорень під час активних перевантажень
            if (aMag >= 0.80f && aMag <= 1.20f) {
                const float halfvx = q_.x * q_.z - q_.w * q_.y;
                const float halfvy = q_.w * q_.x + q_.y * q_.z;
                const float halfvz = q_.w * q_.w - 0.5f + q_.z * q_.z;

                const float halfex = ay * halfvz - az * halfvy;
                const float halfey = az * halfvx - ax * halfvz;
                const float halfez = ax * halfvy - ay * halfvx;

                if (twoKi_ > 0.0f) {
                    integralBias_[0] += twoKi_ * halfex * dt;
                    integralBias_[1] += twoKi_ * halfey * dt;
                    integralBias_[2] += twoKi_ * halfez * dt;
                    gx += integralBias_[0];
                    gy += integralBias_[1];
                    gz += integralBias_[2];
                }

                gx += twoKp_ * halfex;
                gy += twoKp_ * halfey;
                gz += twoKp_ * halfez;
            }
        }

        gx *= (0.5f * dt);
        gy *= (0.5f * dt);
        gz *= (0.5f * dt);

        const float qw = q_.w;
        const float qx = q_.x;
        const float qy = q_.y;
        const float qz = q_.z;

        q_.w += (-qx * gx - qy * gy - qz * gz);
        q_.x += ( qw * gx + qy * gz - qz * gy);
        q_.y += ( qw * gy - qx * gz + qz * gx);
        q_.z += ( qw * gz + qx * gy - qy * gx);

        q_.normalize();
    }

    [[nodiscard]] EulerAngles toEuler() const noexcept {
        return EulerAngles{
            .roll  = std::atan2(2.0f * (q_.w * q_.x + q_.y * q_.z), 1.0f - 2.0f * (q_.x * q_.x + q_.y * q_.y)),
            .pitch = std::asin(std::clamp(2.0f * (q_.w * q_.y - q_.z * q_.x), -1.0f, 1.0f)),
            .yaw   = std::atan2(2.0f * (q_.w * q_.z + q_.x * q_.y), 1.0f - 2.0f * (q_.y * q_.y + q_.z * q_.z))
        };
    }

    [[nodiscard]] const Quaternion& quaternion() const noexcept { return q_; }
    [[nodiscard]] const std::array<float, 3>& gyroBias() const noexcept { return integralBias_; }

private:
    Quaternion q_{};
    std::array<float, 3> integralBias_{0.0f, 0.0f, 0.0f};
    float twoKp_{2.0f};
    float twoKi_{0.1f};
};
```
:::

### Апаратне тактування, FPU та мінімізація фазової затримки

Для досягнення максимальної якості стабілізації апарата орієнтаційний фільтр повинен вносити мінімальну **фазову затримку** (англ. *phase lag*). Якщо затримка між фізичним моментом вимірювання датчика та моментом оновлення кватерніона становить 2 мс, на частоті коливань контуру стабілізації 30 Гц це створює запізнення фази на 21.6° (`360° · 30 Гц · 0.002 с`), що різко знижує запас стійкості ПІД-регулятора та провокує високочастотну автогенерацію двигунів.

Для усунення фазових затримок у реальних вбудованих системах впроваджують такі рішення:
1. **Зчитування за апаратним перериванням через SPI DMA**. Вивід готовності даних IMU (`INT` або `DRDY`) налаштовується на зовнішнє апаратне переривання EXTI. Обробник переривання запускає транзакцію SPI через контролер прямого доступу до пам'яті (DMA), розвантажуючи процесорне ядро від очікування байтів шини.
2. **Апаратний блок обчислень із плаваючою комою (FPU)**. У мікроконтролерах ARM Cortex-M4F/M7 або RISC-V із розширенням 'F' обов'язково активують співпроцесор FPU у системному регістрі `SCB->CPACR` перед запуском алгоритму. Виконання інструкцій `VADD.F32`, `VMUL.F32` та `VSQRT.F32` займає 1–14 тактів замість сотень тактів при програмній емуляції soft-float.
3. **Захист від нечислових значень (NaN) та переповнення**. Якщо на вхід алгоритму випадково надійде нульовий вектор прискорення або відбудеться збій живлення шини I2C/SPI, операція нормалізації може викликати ділення на нуль і згенерувати значення `NaN`. Прошивка повинна контролювати валідність результату й у разі виявлення `isnan(q0)` автоматично скидати кватерніон у безпечний початковий стан `[1, 0, 0, 0]ᵀ`.

### Типові пастки інтеграції та оптимізація продуктивності

1. **Неузгодженість фізичних одиниць вимірювання**. Якщо передати у функцію вимірювання гіроскопа в градусах за секунду (`°/s`) замість радіанів за секунду (`rad/s`), коефіцієнт інтегрування буде завищено у 57.3 раза (`180 / π`), що миттєво викличе чисельну нестійкість і переповнення кватерніона.
2. **Джиттер періоду дискретизації `dt`**. Використання номінального значення `dt = 0.001f` при реальному джиттері виклику переривань у діапазоні 0.8–1.4 мс спричиняє штучне накопичення похибки орієнтації. Для точного розрахунку необхідно вимірювати тривалість між спрацьовуваннями таймером мікроконтролера високої роздільності (DWT cycle counter у Cortex-M або 32-бітний апаратний таймер TIM).
3. **Неправильна орієнтація осей датчика**. Якщо осі акселерометра та гіроскопа не вирівняні за правилом правої трійки осей (Right-Hand Rule) або чип запаяний під кутом до плати, перехресний векторний добуток працюватиме як позитивний зворотний зв'язок і призведе до миттєвого перекидання оцінки просторового стану.
4. **Апаратне насичення датчиків під час удару (Sensor Clipping)**. Якщо кутова швидкість обертання перевищує максимальний діапазон гіроскопа (наприклад, ±2000°/с), вихідний регістр фіксує граничне значення. Інтегратор не отримує інформації про реальний розгін, що створює кутову похибку до 90°. Прошивка автопілота повинна детектувати стан насичення регістрів і тимчасово збільшувати коефіцієнт корекції `Kp` після виходу з перевантаження.
5. **Антиаліасинг і цифрова фільтрація низьких частот (DLPF)**. Акустичні та механічні вібрації пропелерів на частотах 150–400 Гц не повинні потрапляти у вхідні регістри АЦП датчика без попередньої фільтрації. У конфігураційному регістрі IMU (наприклад, `CONFIG` або `GYRO_CONFIG` у датчиках InvenSense/TDK) обов'язково активують апаратний низькочастотний фільтр DLPF зі зрізом 42–98 Гц. Це усуває паразитне накладання високочастотних вібраційних гармонік на спектр корисного сигналу кутового руху.

