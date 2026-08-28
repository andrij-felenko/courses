# ⚙️ Алгоритм і прошивка калібрування Compass-Mot

Програмна компенсація магнітних завад за струмом споживання (відома в автопілотах ArduPilot та PX4 як **Compass-Mot** або *Current-based Mag Compensation*) — це фундаментальний алгоритм усунення динамічних електромагнітних наведень на цифровий компас у режимі реального часу.

Якщо статичні спотворення від намагнічених металевих деталей (Hard Iron та Soft Iron) усуваються одноразовим калібруванням обертанням дрона в повітрі на землі, то динамічні поля від струмів моторів змінюються щомілісекунди. Вони прямо пропорційні миттєвому струму силової батареї `I(t)` або квадрату газу двигунів `Throttle²`. Нижче наведено повний інженерний цикл розрахунку: фізичну модель, протокол стендового прогону, математичний апарат лінійної регресії, станковий автомат калібрування, аналіз логів та робочий код на C і C++.

---

## 1. Математична модель динамічної завади

Сумарний тривимірний вектор магнітної індукції `B_meas(t)`, що надходить із виходу мікросхеми магнітометра, складається з трьох незалежних фізичних компонентів:

```
B_meas(t) = B_static + B_earth(t) + B_current(t) + B_voltage(t) + ε(t)
```

де:
- `B_static` — постійний вектор твердого заліза (Hard Iron) та матриця спотворення м'якого заліза (Soft Iron), які залишаються незмінними за будь-якого струму;
- `B_earth(t)` — шукане геомагнітне поле Землі, орієнтоване вздовж магнітного меридіана;
- `B_current(t)` — динамічна складова електромагнітної завади від струму живлення моторів;
- `B_voltage(t)` — вторинний вплив падіння напруги силової шини (зміна струмів підтяжок, драйверів і перетворювачів);
- `ε(t)` — високочастотний вимірювальний шум чутливого моста давача.

За законом Біо — Савара — Лапласа напруженість магнітного поля в будь-якій точці простору строго лінійно залежить від сили струму в навколишніх провідниках. Тому векторну заваду `B_current(t)` описують через вектор чутливості осей `k_I = [k_x, k_y, k_z]ᵀ`:

```
B_current(t) = k_I · I(t) = [ k_x · I(t),  k_y · I(t),  k_z · I(t) ]ᵀ
```

Коефіцієнти `k_x, k_y, k_z` мають розмірність `мкТл / А` (або `mGauss / A`). Вони інтегрують у собі всю геометрію прокладання силових дротів, взаємне просторове розташування ключів MOSFET, доріжок плати PDB та орієнтацію осей кристала магнітометра.

Під час польоту кожен сирий вимір компаса очищається простим векторним відніманням:

```
B_clean(t) = B_meas(t) − k_I · I_filt(t)
```

де `I_filt(t)` — струм батареї, пропущений крізь цифровий фільтр низьких частот для узгодження групової затримки давача струму та дециматора магнітометра.

---

## 2. Протокол наземного стендового калібрування

Процедура Compass-Mot вимагає запуску двигунів на високих обертах при нерухомому корпусі апарата. Щоб гарантувати безпеку інженера та цілісність конструкції, калібрування виконується за суворим регламентом.

### Заходи безпеки та підготовка

1. **Фіксація апарата:** Дрон жорстко кріпиться до важкої дерев'яної чи алюмінієвої платформи за допомогою текстильних строп або струбцин. Заборонено використовувати сталеві магнітні кріплення (тиски, важкі залізні плити), які створюють локальну магнітну аномалію та спотворюють базовий вектор `B_earth`.
2. **Перевертання пропелерів (Inverted Props):** Гвинти знімають і встановлюють опуклим боком донизу (або міняють місцями пропелери прямого CW та зворотного CCW обертання без зміни напрямку обертання моторів). Завдяки цьому при додаванні газу тяга спрямовується **вниз**, притискаючи апарат до столу, а не піднімаючи його в повітря.
3. **Підключення живлення:** Використовують повністю заряджений акумулятор, що відповідає робочій конфігурації дрона (наприклад, 6S LiPo). Калібрування від слабкого лабораторного блока живлення неприпустиме, оскільки блок не здатний видати пікові струми 80–150 А.

### Кінцевий автомат калібрувального циклу (FSM)

```
[ IDLE ] ──► [ BASELINE ] ──► [ RAMP UP ] ──► [ PEAK HOLD ] ──► [ RAMP DOWN ] ──► [ OLS SOLVE ] ──► [ FLASH SAVE ]
 (0% газу)     (2 сек, 0 А)    (0% -> 85%)     (1.5 сек)         (85% -> 0%)       (розрахунок k)      (EEPROM/FRAM)
```

1. **Етап BASELINE (0% газу, `I ≈ 0 А`):** Протягом `2.0` секунд автопілот зчитує показники магнітометра при зупинених двигунах і розраховує опорний вектор геомагнітного поля:
```
B_base = [ (1/M)·∑ B_x,0 ,  (1/M)·∑ B_y,0 ,  (1/M)·∑ B_z,0 ]ᵀ
```
2. **Етап RAMP UP:** Автопілот формує ступінчастий ШІМ-сигнал на мотори, збільшуючи газ від 0% до 80–90% кроками по 10% із витримкою по 1.0–1.5 секунди на кожній сходинці.
3. **Накопичення вибірок:** На кожному кроці синхронно записуються пари даних: миттєвий струм `I_k` (з вимірювального шунта Power Module) та тривісне відхилення поля `ΔB_k = B_meas,k − B_base`.
4. **Етап RAMP DOWN:** Газ плавно скидається до нуля для запобігання стрибкам зворотної ЕРС на індуктивностях двигунів.
5. **Етап OLS SOLVE:** Алгоритм регресії обчислює коефіцієнти `k_x, k_y, k_z`, оцінює якість підгонки та відсоток інтерференції.

---

## 3. Математичний метод розрахунку: регресія найменших квадратів (OLS)

Для кожної з трьох осей `X, Y, Z` формується одновимірна лінійна регресійна модель відхилення поля `ΔB_axis` від струму `I`:

```
ΔB_x,k = k_x · I_k + ε_x,k
ΔB_y,k = k_y · I_k + ε_y,k
ΔB_z,k = k_z · I_k + ε_z,k
```

Мінімізуємо суму квадратів похибок для кожної осі:

```
S(k_x) = ∑ [k=1...N] (ΔB_x,k − k_x · I_k)²  ──►  min
```

Беручи частинну похідну за `k_x` і прирівнюючи її до нуля:

```
dS / dk_x = − 2 · ∑ [k=1...N] I_k · (ΔB_x,k − k_x · I_k) = 0
```

Розкриваємо дужки й отримуємо аналітичний розв'язок для кутового коефіцієнта нахилу `k_x`:

```
k_x = (N · ∑ (I_k · ΔB_x,k) − (∑ I_k) · (∑ ΔB_x,k)) / (N · ∑ (I_k²) − (∑ I_k)²)
```

Аналогічно обчислюються коефіцієнти для осей `Y` та `Z`:

```
k_y = (N · ∑ (I_k · ΔB_y,k) − (∑ I_k) · (∑ ΔB_y,k)) / (N · ∑ (I_k²) − (∑ I_k)²)
k_z = (N · ∑ (I_k · ΔB_z,k) − (∑ I_k) · (∑ ΔB_z,k)) / (N · ∑ (I_k²) − (∑ I_k)²)
```

### Критерій оцінки інтерференції (Interference Ratio)

Для перевірки безпеки компоновки розраховують максимальне відносне відхилення вектора магнітного поля при максимальному робочому струмі `I_max`:

```
||ΔB_max|| = I_max · √(k_x² + k_y² + k_z²)
||B_base|| = √(B_x0² + B_y0² + B_z0²)
Interference_pct = (||ΔB_max|| / ||B_base||) · 100%
```

Інтерпретація результатів:
- **`Interference < 10%`:** Відмінна компоновка. Компас розташований далеко від силових трас, програмна компенсація зводить похибку курсу майже до нуля (< 0.5°).
- **`10% ≤ Interference ≤ 30%`:** Помірна завада, типова для компактних рам. Compass-Mot ефективно виправляє дрейф курсу до величини < 1.5°.
- **`Interference > 30%`:** Критичний рівень завади. Сенсор розташований занадто близько до ESC чи акумуляторних дротів. Хоча алгоритм покращить стабільність, EKF може періодично бракувати вимірювання. Рекомендується збільшити висоту щогли компаса.

---

## 4. Промислова реалізація модулів на C та C++

Нижче наведено повністю працездатний, протестований код для мікроконтролерів польотного стека (STM32, ESP32, nRF).

:::tabs
```c
/* compass_mot.h - C99 Implementation of Compass-Mot Calibration and In-Flight Engine */
#ifndef COMPASS_MOT_H
#define COMPASS_MOT_H

#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#define COMPASS_MOT_MAX_SAMPLES 1024

/* Конфігурація та робочий стан потокового фільтра */
typedef struct {
    float k_x;              /* Коефіцієнт компенсації осі X (мкТл/А) */
    float k_y;              /* Коефіцієнт компенсації осі Y (мкТл/А) */
    float k_z;              /* Коефіцієнт компенсації осі Z (мкТл/А) */
    float current_lpf_alpha;/* Коефіцієнт згладжування фільтра струму */
    float current_filtered; /* Поточний фільтрований струм (А) */
    float max_current_limit;/* Граничний струм для відсікання помилок давача */
    bool  is_enabled;       /* Прапорець активності компенсації */
} compass_mot_t;

/* Структура накопичувача статистики для процедури калібрування OLS */
typedef struct {
    float sum_i;            /* Сума струмів ∑ I */
    float sum_i2;           /* Сума квадратів струмів ∑ I² */
    float sum_bx;           /* Сума відхилень ∑ ΔBx */
    float sum_by;           /* Сума відхилень ∑ ΔBy */
    float sum_bz;           /* Сума відхилень ∑ ΔBz */
    float sum_i_bx;         /* Сума добутків ∑ (I · ΔBx) */
    float sum_i_by;         /* Сума добутків ∑ (I · ΔBy) */
    float sum_i_bz;         /* Сума добутків ∑ (I · ΔBz) */
    uint32_t sample_count;  /* Кількість зібраних вибірок */
    float b_baseline[3];    /* Опорне геомагнітне поле [Bx0, By0, Bz0] */
} compass_mot_calibrator_t;

/**
 * Ініціалізація структури компенсатора
 */
static inline void compass_mot_init(compass_mot_t *cm, float kx, float ky, float kz,
                                    float dt_sec, float cutoff_hz) {
    cm->k_x = kx;
    cm->k_y = ky;
    cm->k_z = kz;
    cm->current_filtered = 0.0f;
    cm->max_current_limit = 250.0f;
    cm->is_enabled = (fabsf(kx) > 1e-5f || fabsf(ky) > 1e-5f || fabsf(kz) > 1e-5f);

    /* Розрахунок коефіцієнта фільтра низьких частот першого порядку */
    float rc = 1.0f / (2.0f * 3.14159265f * cutoff_hz);
    cm->current_lpf_alpha = dt_sec / (rc + dt_sec);
}

/**
 * Старт калібрувального прогону
 */
static inline void compass_mot_calib_start(compass_mot_calibrator_t *cal, const float b_zero[3]) {
    cal->sum_i = 0.0f;
    cal->sum_i2 = 0.0f;
    cal->sum_bx = 0.0f;
    cal->sum_by = 0.0f;
    cal->sum_bz = 0.0f;
    cal->sum_i_bx = 0.0f;
    cal->sum_i_by = 0.0f;
    cal->sum_i_bz = 0.0f;
    cal->sample_count = 0;
    cal->b_baseline[0] = b_zero[0];
    cal->b_baseline[1] = b_zero[1];
    cal->b_baseline[2] = b_zero[2];
}

/**
 * Додавання вимірювання в накопичувач OLS
 */
static inline void compass_mot_calib_feed(compass_mot_calibrator_t *cal,
                                         float current_amps,
                                         const float b_raw[3]) {
    if (cal->sample_count >= COMPASS_MOT_MAX_SAMPLES || current_amps < 0.0f) {
        return;
    }

    float delta_bx = b_raw[0] - cal->b_baseline[0];
    float delta_by = b_raw[1] - cal->b_baseline[1];
    float delta_bz = b_raw[2] - cal->b_baseline[2];

    cal->sum_i    += current_amps;
    cal->sum_i2   += current_amps * current_amps;
    cal->sum_bx   += delta_bx;
    cal->sum_by   += delta_by;
    cal->sum_bz   += delta_bz;
    cal->sum_i_bx += current_amps * delta_bx;
    cal->sum_i_by += current_amps * delta_by;
    cal->sum_i_bz += current_amps * delta_bz;
    cal->sample_count++;
}

/**
 * Завершення калібрування: розрахунок коефіцієнтів OLS та відсотка завади
 */
static inline bool compass_mot_calib_finish(const compass_mot_calibrator_t *cal,
                                            compass_mot_t *cm,
                                            float *interference_pct) {
    if (cal->sample_count < 30) {
        return false;
    }

    float n = (float)cal->sample_count;
    float denom = n * cal->sum_i2 - cal->sum_i * cal->sum_i;
    if (fabsf(denom) < 1e-6f) {
        return false;
    }

    cm->k_x = (n * cal->sum_i_bx - cal->sum_i * cal->sum_bx) / denom;
    cm->k_y = (n * cal->sum_i_by - cal->sum_i * cal->sum_by) / denom;
    cm->k_z = (n * cal->sum_i_bz - cal->sum_i * cal->sum_bz) / denom;
    cm->is_enabled = true;

    /* Розрахунок відносного рівня завади при розрахунковому струмі 100 А */
    float base_norm = sqrtf(cal->b_baseline[0]*cal->b_baseline[0] +
                            cal->b_baseline[1]*cal->b_baseline[1] +
                            cal->b_baseline[2]*cal->b_baseline[2]);
    float comp_norm = sqrtf(cm->k_x*cm->k_x + cm->k_y*cm->k_y + cm->k_z*cm->k_z) * 100.0f;

    if (base_norm > 1.0f) {
        *interference_pct = (comp_norm / base_norm) * 100.0f;
    } else {
        *interference_pct = 0.0f;
    }
    return true;
}

/**
 * Потокова компенсація вимірювання компаса в кожному такті польотного циклу
 */
static inline void compass_mot_apply(compass_mot_t *cm,
                                     float raw_current_amps,
                                     const float b_in[3],
                                     float b_out[3]) {
    if (!cm->is_enabled || raw_current_amps < 0.0f || raw_current_amps > cm->max_current_limit) {
        b_out[0] = b_in[0];
        b_out[1] = b_in[1];
        b_out[2] = b_in[2];
        return;
    }

    /* Фільтрація струму для збігу фази з буфером магнітометра */
    cm->current_filtered += cm->current_lpf_alpha * (raw_current_amps - cm->current_filtered);

    /* Векторне віднімання динамічної завади */
    b_out[0] = b_in[0] - cm->k_x * cm->current_filtered;
    b_out[1] = b_in[1] - cm->k_y * cm->current_filtered;
    b_out[2] = b_in[2] - cm->k_z * cm->current_filtered;
}

#endif /* COMPASS_MOT_H */
```
```cpp
/* CompassMotCompensator.hpp - Idiomatic C++20 Compass-Mot Engine */
#pragma once

#include <array>
#include <cmath>
#include <cstdint>
#include <numbers>
#include <optional>
#include <span>

namespace navigation {

struct Vector3f {
    float x{0.0f};
    float y{0.0f};
    float z{0.0f};

    [[nodiscard]] constexpr Vector3f operator-(const Vector3f& other) const noexcept {
        return {x - other.x, y - other.y, z - other.z};
    }

    [[nodiscard]] constexpr Vector3f operator*(float scalar) const noexcept {
        return {x * scalar, y * scalar, z * scalar};
    }

    [[nodiscard]] float length() const noexcept {
        return std::sqrt(x * x + y * y + z * z);
    }
};

class CompassMotCompensator {
public:
    struct CalibrationResult {
        Vector3f coefficients{};
        float interference_percent{0.0f};
        uint32_t sample_count{0};
    };

    explicit CompassMotCompensator(Vector3f coeffs = {},
                                  float dt_seconds = 0.01f,
                                  float filter_cutoff_hz = 15.0f,
                                  float max_current_limit = 250.0f) noexcept
        : k_current_(coeffs),
          max_current_(max_current_limit),
          is_active_(coeffs.length() > 1e-5f) {
        update_filter_alpha(dt_seconds, filter_cutoff_hz);
    }

    void set_filter_parameters(float dt_seconds, float filter_cutoff_hz) noexcept {
        update_filter_alpha(dt_seconds, filter_cutoff_hz);
    }

    void set_coefficients(const Vector3f& coeffs) noexcept {
        k_current_ = coeffs;
        is_active_ = (k_current_.length() > 1e-5f);
    }

    [[nodiscard]] constexpr const Vector3f& coefficients() const noexcept {
        return k_current_;
    }

    [[nodiscard]] constexpr bool is_active() const noexcept {
        return is_active_;
    }

    void reset() noexcept {
        current_lpf_ = 0.0f;
    }

    /* Потокова корекція вимірювання за струмом */
    [[nodiscard]] Vector3f compensate(const Vector3f& raw_field,
                                      float measured_current_amps) noexcept {
        if (!is_active_ || measured_current_amps < 0.0f || measured_current_amps > max_current_) {
            return raw_field;
        }

        // Оновлення IIR фільтра струму для усунення високочастотного шуму шунта
        current_lpf_ += lpf_alpha_ * (measured_current_amps - current_lpf_);

        return {
            raw_field.x - k_current_.x * current_lpf_,
            raw_field.y - k_current_.y * current_lpf_,
            raw_field.z - k_current_.z * current_lpf_
        };
    }

    /* Клас-накопичувач для проведення наземного регресійного калібрування */
    class Calibrator {
    public:
        explicit Calibrator(const Vector3f& baseline_field) noexcept
            : baseline_(baseline_field) {}

        void feed(float current_amps, const Vector3f& mag_reading) noexcept {
            if (current_amps < 0.0f) return;

            const Vector3f delta = mag_reading - baseline_;
            sum_i_    += current_amps;
            sum_i2_   += current_amps * current_amps;
            sum_bx_   += delta.x;
            sum_by_   += delta.y;
            sum_bz_   += delta.z;
            sum_i_bx_ += current_amps * delta.x;
            sum_i_by_ += current_amps * delta.y;
            sum_i_bz_ += current_amps * delta.z;
            ++count_;
        }

        [[nodiscard]] std::optional<CalibrationResult> solve() const noexcept {
            if (count_ < 30) {
                return std::nullopt;
            }

            const float n = static_cast<float>(count_);
            const float denom = n * sum_i2_ - sum_i_ * sum_i_;
            if (std::abs(denom) < 1e-6f) {
                return std::nullopt;
            }

            CalibrationResult res;
            res.coefficients.x = (n * sum_i_bx_ - sum_i_ * sum_bx_) / denom;
            res.coefficients.y = (n * sum_i_by_ - sum_i_ * sum_by_) / denom;
            res.coefficients.z = (n * sum_i_bz_ - sum_i_ * sum_bz_) / denom;
            res.sample_count = count_;

            const float base_mag = baseline_.length();
            const float test_current = 100.0f; // Оцінка при струмі форсажу 100 А
            if (base_mag > 1.0f) {
                res.interference_percent = (res.coefficients.length() * test_current / base_mag) * 100.0f;
            }

            return res;
        }

    private:
        Vector3f baseline_;
        float sum_i_{0.0f};
        float sum_i2_{0.0f};
        float sum_bx_{0.0f};
        float sum_by_{0.0f};
        float sum_bz_{0.0f};
        float sum_i_bx_{0.0f};
        float sum_i_by_{0.0f};
        float sum_i_bz_{0.0f};
        uint32_t count_{0};
    };

private:
    void update_filter_alpha(float dt_sec, float cutoff_hz) noexcept {
        const float rc = 1.0f / (2.0f * std::numbers::pi_v<float> * cutoff_hz);
        lpf_alpha_ = dt_sec / (rc + dt_sec);
    }

    Vector3f k_current_{};
    float lpf_alpha_{0.5f};
    float current_lpf_{0.0f};
    float max_current_{250.0f};
    bool is_active_{false};
};

} // namespace navigation
```
:::

---

## 5. Граблі та діагностика в логах Dataflash

Під час розбору телеметрії польоту (файли `.bin` або `.tlog` у Mission Planner чи Plot.ly) якість роботи Compass-Mot перевіряють за такими ознаками:

1. **Кореляція `MagX/MagY` зі струмом `CURR.Curr`:** Якщо до калібрування на графіку чітко видно повторення форми кривої струму на графіку магнітного поля, то після коректного Compass-Mot крива поля `B_clean` стає практично горизонтальною з амплітудою випадкових флуктуацій менше `1.5 мкТл`.
2. **Аномальні викиди через відсутність фільтрації струму:** Якщо графік скоригованого поля дає різкі тонкі піки в моменти миттєвого відкриття газу, це вказує на завищену частоту зрізу `cutoff_hz`. Зменшення частоти фільтра низьких частот струму до `10–12 Гц` усуває фазовий розрив.
3. **Несправність або зміщення нуля струмового сенсора:** Якщо давач струму має власний температурний зсув нуля (наприклад, показує 3 А при вимкнених моторах), калібрування зсуне базове поле. Рекомендується калібрувати зсув нуля струмового шунта (Current Offset) перед запуском процедури Compass-Mot.
