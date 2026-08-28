# ⚙️ Програмне виявлення аварії та екстрене вимкнення моторів

Програмний захист від аварійного блокування моторів дозволяє врятувати силові транзистори регуляторів швидкості (ESC) від теплового пробою в перші мілісекунди після жорсткого удару об перешкоду.

## Чому заблокований мотор спалює регулятор

Під час нормального обертання безколекторного мотора (BLDC) у його обмотках індукується проти-ЕРС (Back-EMF `E = K_e · ω`), яка протидіє напрузі живлення `V_bat`. Ефективна напруга на фазі дорівнює різниці `V_eff = V_bat - E`.

Коли гвинт врізається в ґрунт чи гілку і миттєво зупиняється (`ω = 0`), проти-ЕРС зникає (`E = 0`). До активного опору мідного дроту обмоток `R_phase ≈ 0.06 Ом` прикладається повна напруга батареї (наприклад, `25.2 В` для 6S LiPo).

Струм короткого замикання фази сягає пікових значень:

```
I_stall = V_bat / R_phase
= 25.2 / 0.06
= 420 А
```

Силові польові транзистори (MOSFET) плати ESC 4-in-1, розраховані на тривалий струм 45–55 А, витримують такий струм не довше 20–40 мілісекунд, після чого кристал кремнію перегрівається вище 175 °C і вибухає з пробоєм переходу «стік-витік» (Drain-Source short).

Якщо польотний контролер виявляє піковий удар за даними акселерометра та аномальне кутове сповільнення гіроскопа, він формує сигнал екстреного роззброєння (`Emergency Disarm`), примусово скидаючи шпаруватість ШІМ на нуль до того, як транзистори перегріються.

---

## Виклики розпізнавання: пілотаж проти аварії

Головна складність проєктування детектора аварій полягає в уникненні хибних спрацьовувань (*false positive triggers*) під час виконання екстремальних акробатичних фігур (Freestyle / Racing). Під час виконання різких фліпів (snap rolls) кутова швидкість обертання дрона може досягати 1500–2000°/с, а відцентрове прискорення на кінцях променів — до 8–10 g.

Для надійного розділення польотних маневрів та аварійного зіткнення алгоритм використовує комбінацію трьох незалежних критеріїв:

1. **Векторний сплеск перевантаження (Linear G-Spike):**
   Обчислюється модуль повної просторової акселерації `|a| = √(a_x² + a_y² + a_z²)`. Під час польоту навіть при максимальній тязі вектор `|a|` рідко перевищує 4–6 g. Удар об тверду поверхню генерує короткий високоамплітудний імпульс понад 15–25 g з крутим фронтом наростання.

2. **Помилка відстеження кутової швидкості (Setpoint Error Anomaly):**
   Алгоритм порівнює виміряну гіроскопом швидкість `ω_meas` із бажаною швидкістю від стіків керування пілота `ω_setpoint`. Якщо дрон швидко обертається за командою пілота (`|ω_meas - ω_setpoint| < Δω_tol`), це нормальний маневр. Якщо ж виникає раптове кутове сповільнення `dω/dt > 5000°/с²` при відсутності команди на зупинку, це свідчить про фізичний удар променя об перешкоду.

3. **Фільтр підтвердження (Debounce Window):**
   Високочастотні вібрації від розбалансованого пропелера можуть створювати поодинокі вибіркові шуми в цифровому інтерфейсі SPI акселерометра. Щоб уникнути помилкового вимкнення мотора в польоті, перевантаження повинно фіксуватися протягом щонайменше `N` послідовних циклів обчислення (наприклад, 3 вибірки при частоті 1 кГц відповідають тривалості 3 мс, що є типовою тривалістю механічного удару).

---

## Реалізація детектора аварійного зіткнення

Нижче наведено модуль фільтрації аварійних станів, призначений для виконання в основному циклі польотного контролера.

:::tabs
```c
#include <stdbool.h>
#include <stdint.h>
#include <math.h>

#define CRASH_ACCEL_THRESHOLD_G     15.0f   /* Поріг перевантаження (g) */
#define CRASH_GYRO_THRESHOLD_DPS    1200.0f /* Поріг кутової швидкості (град/с) */
#define CRASH_DEBOUNCE_SAMPLES      3       /* Кількість вибірок для підтвердження */

typedef struct {
    float ax_g;
    float ay_g;
    float az_g;
    float gx_dps;
    float gy_dps;
    float gz_dps;
} imu_sensor_data_t;

typedef struct {
    uint8_t impact_counter;
    bool is_crashed;
    bool disarm_latched;
} crash_detector_t;

void crash_detector_init(crash_detector_t *detector) {
    if (!detector) return;
    detector->impact_counter = 0;
    detector->is_crashed = false;
    detector->disarm_latched = false;
}

bool crash_detector_update(crash_detector_t *detector, 
                           const imu_sensor_data_t *imu,
                           bool is_armed) {
    if (!detector || !imu || !is_armed) {
        if (detector) detector->impact_counter = 0;
        return false;
    }

    if (detector->disarm_latched) {
        return true; /* Стан аварії зафіксовано до ручного скидання */
    }

    /* 1. Обчислення модуля сумарного лінійного перевантаження */
    float accel_sq = (imu->ax_g * imu->ax_g) + 
                     (imu->ay_g * imu->ay_g) + 
                     (imu->az_g * imu->az_g);
    float accel_mag = sqrtf(accel_sq);

    /* 2. Обчислення максимальної кутової швидкості */
    float gyro_max = fabsf(imu->gx_dps);
    if (fabsf(imu->gy_dps) > gyro_max) gyro_max = fabsf(imu->gy_dps);
    if (fabsf(imu->gz_dps) > gyro_max) gyro_max = fabsf(imu->gz_dps);

    /* 3. Критерій зіткнення: сильний удар або неконтрольоване обертання */
    bool condition_impact = (accel_mag >= CRASH_ACCEL_THRESHOLD_G);
    bool condition_spin = (gyro_max >= CRASH_GYRO_THRESHOLD_DPS);

    if (condition_impact || condition_spin) {
        if (detector->impact_counter < 255) {
            detector->impact_counter++;
        }
    } else {
        if (detector->impact_counter > 0) {
            detector->impact_counter--;
        }
    }

    /* 4. Спрацьовування захисту при досягненні лічильника */
    if (detector->impact_counter >= CRASH_DEBOUNCE_SAMPLES) {
        detector->is_crashed = true;
        detector->disarm_latched = true;
        return true;
    }

    return false;
}

void crash_detector_reset(crash_detector_t *detector) {
    if (!detector) return;
    detector->impact_counter = 0;
    detector->is_crashed = false;
    detector->disarm_latched = false;
}
```
```cpp
#include <array>
#include <cmath>
#include <algorithm>
#include <cstdint>

struct ImuSample {
    float ax_g{0.0f};
    float ay_g{0.0f};
    float az_g{0.0f};
    float gx_dps{0.0f};
    float gy_dps{0.0f};
    float gz_dps{0.0f};
};

class CrashDetector {
public:
    struct Config {
        float accel_threshold_g{15.0f};
        float gyro_threshold_dps{1200.0f};
        uint8_t debounce_samples{3};
    };

    explicit constexpr CrashDetector(Config cfg = Config{}) : config_(cfg) {}

    [[nodiscard]] bool update(const ImuSample& imu, bool is_armed) noexcept {
        if (!is_armed) {
            impact_counter_ = 0;
            return false;
        }

        if (disarm_latched_) {
            return true;
        }

        const float accel_sq = (imu.ax_g * imu.ax_g) + 
                               (imu.ay_g * imu.ay_g) + 
                               (imu.az_g * imu.az_g);
        const float accel_mag = std::sqrt(accel_sq);

        const float gyro_max = std::max({std::abs(imu.gx_dps), 
                                         std::abs(imu.gy_dps), 
                                         std::abs(imu.gz_dps)});

        const bool is_impact = (accel_mag >= config_.accel_threshold_g);
        const bool is_spin = (gyro_max >= config_.gyro_threshold_dps);

        if (is_impact || is_spin) {
            if (impact_counter_ < 255) {
                ++impact_counter_;
            }
        } else if (impact_counter_ > 0) {
            --impact_counter_;
        }

        if (impact_counter_ >= config_.debounce_samples) {
            is_crashed_ = true;
            disarm_latched_ = true;
            return true;
        }

        return false;
    }

    [[nodiscard]] bool is_crashed() const noexcept { return is_crashed_; }
    [[nodiscard]] bool is_latched() const noexcept { return disarm_latched_; }

    void reset() noexcept {
        impact_counter_ = 0;
        is_crashed_ = false;
        disarm_latched_ = false;
    }

private:
    Config config_;
    uint8_t impact_counter_{0};
    bool is_crashed_{false};
    bool disarm_latched_{false};
};
```
:::

---

## Інтеграція в контур керування та апаратні захисти

Коли детектор підтверджує аварійний стан, стек керування виконує багаторівневу послідовність безпечного глушіння:

1. **Аварійне переривання генерації DShot (Zero-Throttle Override):**
   Контролер негайно припиняє передачу робочих значень газу по протоколу DShot300/DShot600 і відправляє команду `DShot Command 0` (Motor Stop). Це гарантує скидання ШІМ на рівні прошивки ESC менш ніж за 1.5 мс.

2. **Апаратне блокування затворів MOSFET (Hardware Gate Disable):**
   На платах регуляторів із виділеним піном увімкнення драйвера затворів (`DRV_EN` або `DIS_GATE`) мікроконтролер переводить лінію в низький логічний рівень. Затвори всіх верхніх і нижніх польових транзисторів заземлюються через внутрішні підтягувальні резистори 10 кОм, виключаючи наскрізні струми при руйнуванні обмоток.

3. **Апаратний струмовий захист (Current Shunt Trip):**
   Сучасні плати ESC містять токові шунти опором `R_shunt ≈ 0.5 мОм` на кожній півмостовій фазі або загальній шині живлення. При падінні напруги на шунті понад порогове значення (наприклад, понад 100 мВ, що відповідає струму 200 А) вбудований апаратний компаратор мікроконтролера ESC переводить виходи ШІМ у високоімпедансний стан (Hi-Z) апаратно, без участі процесора, менш ніж за 200 наносекунд.

4. **Захист у режимі перевертання (Turtle Mode Interlock):**
   Якщо пілот намагається перевернути впалий апарат у режимі «черепахи» (Crash Flip Over After Crash), коли один із пропелерів затиснутий у траві або гілках, алгоритм відстежує зворотну телеметрію обертів (Bidirectional DShot RPM telemetry). Якщо за поданої шпаруватості 30% оберти мотора залишаються рівними нулю протягом 300 мс, цей канал негайно блокується для запобігання згорянню ESC на землі.

5. **Діагностичне логування в Blackbox:**
   Останні 100 мс телеметрії перед спрацьовуванням детектора зберігаються в енергонезалежну Flash-пам'ять із встановленням прапорця `DISARM_REASON_CRASH_DETECTED`, що дозволяє інженерам під час аналізу логів відрізнити падіння через відмову живлення від механічного удару.

---

## Налаштування порогів під типорозмір апарата

Пороги спрацьовування повинні калібруватися під інерційні характеристики рами:

```
Клас апарата            Маса      Поріг перевантаження G    Поріг кутової швидкості    Дебаунс
───────────────────────────────────────────────────────────────────────────────────────────────
Micro / Whoop (2-3")    40–120 г          8–10 g                    800°/с             2 вибірки
Freestyle (5")         550–850 г         15–18 g                   1200°/с             3 вибірки
Cinelifter / 7-10"    1.8–3.5 кг         10–12 g                    600°/с             4 вибірки
```

Для важких апаратів (Cinelifter) поріг за кутовою швидкістю знижують, оскільки велика інерція маси фізично унеможливлює швидке обертання без зовнішнього руйнівного контакту.
