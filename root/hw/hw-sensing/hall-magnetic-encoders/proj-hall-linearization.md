# ⚙️ Повна система зчитування, багатооборотного розгортання та гармонійної фільтрації кута

Для прецизійного сервопривода чи системи векторного керування (FOC) зчитування сирого кута з магнітного енкодера — лише перший крок. Реальна прошивка повинна безперервно розгортати кут через границю 360° (Phase Unwrapping) для збереження багатооборотного положення, компенсувати гармонійні нелінійності монтажу та оцінювати кутову швидкість без шуму чисельного диференціювання.

Нижче наведено повну архітектуру вбудованого модуля: від драйвера SPI з перевіркою парності до альфа-бета фільтра стеження, аналізу затримок та відновлення після збоїв.

## Архітектура обробки сигналу кута

```
[ AS5048A SPI ]
      │ (16-бітний кадр із парністю)
      ▼
[ Перевірка парності та прапорців помилок ] ──(Помилка)──► [ Відновлення / ERRFL ]
      │ (14-бітний сирий кут: 0..16383)
      ▼
[ Багатооборотне розгортання кута (Unwrap) ]
      │ (Неперервний кут: θ_raw ∈ (-∞, +∞))
      ▼
[ Гармонійна лінеаризація Фур'є (1-ша і 2-га гармоніки) ]
      │ (Очищений кут: θ_cal)
      ▼
[ Альфа-бета фільтр стеження (Tracking Observer) ]
      │
      ├───────────────────────────┬───────────────────────────┐
      ▼                           ▼                           ▼
[ Фільтрований кут θ ]   [ Кутова швидкість ω ]      [ Прискорення α ]
```

## Проблема оцінки швидкості та фільтр стеження (Tracking Observer)

У контурах швидкості сервоприводів наївна оцінка кутової швидкості через кінцеву різницю положення `ω_num = (θ[k] - θ[k-1]) / dt` призводить до катастрофічного зростання шуму. Оскільки енкодер квантує кут із роздільністю 14 біт (`Δθ_LSB ≈ 0.022° = 0.000383` рад), при високій частоті опитування контуру (наприклад, `dt = 100 мкс`, `10 кГц`) зміна положення всього на 1 LSB за один крок породжує сплеск швидкості:

```
Δω = 0.000383 рад / 0.0001 с = 3.83 рад/с ≈ 36.6 об/хв
```

Такий шум квантування, потрапляючи на пропорційно-диференціальний (ПД) регулятор струму, викликає сильний високочастотний писк двигуна, додаткові динамічні втрати та перегрів силових транзисторів інвертора.

Для отримання чистої оцінки швидкості застосовують **дискретний альфа-бета фільтр стеження** (Luenberger Observer другого порядку). Фільтр підтримує внутрішню модель кінематики обертання:

```
1. Прогноз стану на наступний крок:
   θ_pred[k] = θ_est[k-1] + ω_est[k-1] · dt

2. Нев'язка вимірювання (помилка прогнозу):
   e[k] = θ_meas[k] - θ_pred[k]

3. Корекція стану за вимірюванням:
   θ_est[k] = θ_pred[k] + α · e[k]
   ω_est[k] = ω_est[k-1] + (β / dt) · e[k]
```

Параметри `α` та `β` обираються виходячи з бажаної смуги пропускання спостерігача `ω_n` та коефіцієнта демпфування `ζ` (зазвичай `ζ = 0.707` для оптимального балансу між швидкістю реакції та фільтрацією шумів):

```
α = 1 - exp(- 2 · ζ · ω_n · dt)
β = 2 · (1 - exp(- ζ · ω_n · dt) · cos(ω_n · dt · √(1 - ζ²))) - α
```

При такому підході оцінка швидкості виходить абсолютно гладкою без фазового запізнення традиційних низькочастотних фільтрів першого порядку.

## Реалізація модуля мовами C та C++

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#define AS5048_CMD_READ_ANGLE   0xFFFF
#define AS5048_CMD_CLEAR_ERR    0x4001
#define AS5048_CMD_READ_AGC     0x7FFD
#define AS5048_CPR              16384
#define M_TWOPI                 (2.0 * 3.14159265358979323846)

typedef struct {
    int16_t turns;
    uint16_t prev_raw_angle;
    bool initialized;
    
    // Калібрувальні гармонійні коефіцієнти
    float offset_rad;
    float a1, b1; // 1-ша гармоніка (ексцентриситет)
    float a2, b2; // 2-га гармоніка (нахил / неортогональність)
    
    // Змінні стану альфа-бета фільтра
    float est_pos_rad;
    float est_vel_rad_s;
    float alpha;
    float beta;
} magnetic_encoder_t;

// Обчислення біта парності (Even Parity)
static inline bool check_even_parity(uint16_t word) {
    uint16_t count = 0;
    for (int i = 0; i < 16; i++) {
        if ((word >> i) & 1) count++;
    }
    return (count % 2) == 0;
}

// Ініціалізація структури енкодера
void encoder_init(magnetic_encoder_t *enc, float sample_time_s) {
    enc->turns = 0;
    enc->prev_raw_angle = 0;
    enc->initialized = false;
    enc->offset_rad = 0.0f;
    enc->a1 = 0.0f; enc->b1 = 0.0f;
    enc->a2 = 0.0f; enc->b2 = 0.0f;
    
    // Налаштування коефіцієнтів фільтра стеження для смуги 50 Гц
    float dt = sample_time_s;
    enc->alpha = 0.25f;
    enc->beta = 0.05f / dt;
    enc->est_pos_rad = 0.0f;
    enc->est_vel_rad_s = 0.0f;
}

// Запис гармонійних коефіцієнтів лінеаризації
void encoder_set_calibration(magnetic_encoder_t *enc, float offset, 
                             float a1, float b1, float a2, float b2) {
    enc->offset_rad = offset;
    enc->a1 = a1; enc->b1 = b1;
    enc->a2 = a2; enc->b2 = b2;
}

// Обробка сирого фрейму SPI
bool encoder_process_raw_frame(magnetic_encoder_t *enc, uint16_t rx_frame, 
                               float dt, float *out_pos_rad, float *out_vel_rad_s) {
    // 1. Перевірка парності
    if (!check_even_parity(rx_frame)) {
        return false; // Помилка лінії зв'язку
    }
    
    // 2. Перевірка прапорця помилки (Bit 14)
    if (rx_frame & 0x4000) {
        return false; // Помилка енкодера (Error Flag)
    }
    
    // 3. Вилучення 14-бітного значення кута (0..16383)
    uint16_t raw = rx_frame & 0x3FFF;
    
    if (!enc->initialized) {
        enc->prev_raw_angle = raw;
        enc->turns = 0;
        enc->initialized = true;
        enc->est_pos_rad = ((float)raw / (float)AS5048_CPR) * (float)M_TWOPI;
    }
    
    // 4. Багатооборотне розгортання кута (Unwrapping)
    int32_t delta = (int32_t)raw - (int32_t)enc->prev_raw_angle;
    if (delta > (AS5048_CPR / 2)) {
        enc->turns--;
    } else if (delta < -(AS5048_CPR / 2)) {
        enc->turns++;
    }
    enc->prev_raw_angle = raw;
    
    // 5. Неперервний розгорнутий кут в радіанах
    float total_counts = (float)enc->turns * (float)AS5048_CPR + (float)raw;
    float uncalibrated_rad = (total_counts / (float)AS5048_CPR) * (float)M_TWOPI;
    
    // 6. Гармонійна корекція за кутом одного оберту theta_single
    float theta_single = ((float)raw / (float)AS5048_CPR) * (float)M_TWOPI;
    float sin1 = sinf(theta_single), cos1 = cosf(theta_single);
    float sin2 = sinf(2.0f * theta_single), cos2 = cosf(2.0f * theta_single);
    
    float error_correction = enc->offset_rad 
                           + (enc->a1 * cos1 + enc->b1 * sin1)
                           + (enc->a2 * cos2 + enc->b2 * sin2);
    
    float calibrated_pos_rad = uncalibrated_rad - error_correction;
    
    // 7. Альфа-бета фільтрація кута та оцінка швидкості
    float pred_pos = enc->est_pos_rad + enc->est_vel_rad_s * dt;
    float residual = calibrated_pos_rad - pred_pos;
    
    enc->est_pos_rad = pred_pos + enc->alpha * residual;
    enc->est_vel_rad_s = enc->est_vel_rad_s + (enc->beta * dt) * residual;
    
    if (out_pos_rad) *out_pos_rad = enc->est_pos_rad;
    if (out_vel_rad_s) *out_vel_rad_s = enc->est_vel_rad_s;
    
    return true;
}
```
```cpp
#include <cstdint>
#include <cmath>
#include <optional>
#include <numbers>
#include <span>

class MagneticEncoderAS5048 {
public:
    static constexpr uint16_t Cpr = 16384;
    static constexpr double TwoPi = std::numbers::pi_v<double> * 2.0;

    struct HarmonicCalibration {
        float offsetRad{0.0f};
        float a1{0.0f}, b1{0.0f}; // 1-ша гармоніка (ексцентриситет)
        float a2{0.0f}, b2{0.0f}; // 2-га гармоніка (кутовий нахил)
    };

    struct State {
        float positionRad{0.0f};
        float velocityRadS{0.0f};
        int32_t totalTurns{0};
    };

    explicit MagneticEncoderAS5048(float sampleTimeS, HarmonicCalibration cal = {})
        : dt_{sampleTimeS}, cal_{cal} {
        alpha_ = 0.25f;
        beta_ = 0.05f / dt_;
    }

    // Обробка 16-бітного SPI кадру з поверненням фільтрованого стану
    [[nodiscard]] std::optional<State> processFrame(uint16_t rxFrame) noexcept {
        if (!verifyEvenParity(rxFrame)) {
            return std::nullopt; // Помилка парності
        }
        if (rxFrame & 0x4000) {
            return std::nullopt; // Error Flag мікросхеми
        }

        const auto raw = static_cast<uint16_t>(rxFrame & 0x3FFF);

        if (!initialized_) {
            prevRaw_ = raw;
            initialized_ = true;
            state_.positionRad = (static_cast<float>(raw) / static_cast<float>(Cpr)) * static_cast<float>(TwoPi);
        }

        // Розгортання переходу через 0 (Unwrap)
        const auto delta = static_cast<int32_t>(raw) - static_cast<int32_t>(prevRaw_);
        if (delta > (Cpr / 2)) {
            state_.totalTurns--;
        } else if (delta < -(Cpr / 2)) {
            state_.totalTurns++;
        }
        prevRaw_ = raw;

        // Розрахунок неперервного кута
        const float totalCounts = static_cast<float>(state_.totalTurns) * static_cast<float>(Cpr) + static_cast<float>(raw);
        const float uncalibratedRad = (totalCounts / static_cast<float>(Cpr)) * static_cast<float>(TwoPi);

        // Гармонійна корекція
        const float thetaSingle = (static_cast<float>(raw) / static_cast<float>(Cpr)) * static_cast<float>(TwoPi);
        const float sin1 = std::sin(thetaSingle), cos1 = std::cos(thetaSingle);
        const float sin2 = std::sin(2.0f * thetaSingle), cos2 = std::cos(2.0f * thetaSingle);

        const float error = cal_.offsetRad 
                          + (cal_.a1 * cos1 + cal_.b1 * sin1)
                          + (cal_.a2 * cos2 + cal_.b2 * sin2);

        const float calibratedRad = uncalibratedRad - error;

        // Альфа-бета фільтрація
        const float predPos = state_.positionRad + state_.velocityRadS * dt_;
        const float residual = calibratedRad - predPos;

        state_.positionRad = predPos + alpha_ * residual;
        state_.velocityRadS += (beta_ * dt_) * residual;

        return state_;
    }

    void updateCalibration(const HarmonicCalibration& cal) noexcept {
        cal_ = cal;
    }

    void resetTurns(int32_t initialTurn = 0) noexcept {
        state_.totalTurns = initialTurn;
    }

private:
    static constexpr bool verifyEvenParity(uint16_t word) noexcept {
        uint16_t count = 0;
        for (int i = 0; i < 16; ++i) {
            if ((word >> i) & 1) ++count;
        }
        return (count % 2) == 0;
    }

    float dt_;
    HarmonicCalibration cal_;
    float alpha_{0.25f};
    float beta_{10.0f};
    uint16_t prevRaw_{0};
    bool initialized_{false};
    State state_{};
};
```
:::

## Калібрування гармонійних коефіцієнтів у реальній системі

Для знаходження коефіцієнтів `(a1, b1, a2, b2)` вал мотора плавно повертають на один повний оберт із постійною малою швидкістю або звіряють відліки магнітного енкодера з високоточним еталонним оптичним енкодером (Reference Encoder).

Масив різниці відліків `e[k] = θ_meas[k] - θ_ref[k]` для `N` точок обробляється дискретним перетворенням Фур'є (DFT):

```
a_n = (2 / N) · ∑ [ e[k] · cos(n · θ_ref[k]) ]
b_n = (2 / N) · ∑ [ e[k] · sin(n · θ_ref[k]) ]
```

Якщо еталонного енкодера немає, застосовують метод вільного вибігу (Coast-down test) або повільне обертання відкритою петлею крокового режиму: при сталому струмі у фазах реальне положення ротора в першому наближенні лінійне за часом `θ_ideal(t) = ω · t + θ₀`, і відхилення від ідеальної прямої дає шукану періодичну похибку монтажу.

Отримані значення коефіцієнтів `(a1, b1, a2, b2)` завантажуються в енергонезалежну пам'ять (Flash / NVS) мікроконтролера при старті системи.

## Крайові випадки та обмеження алгоритму розгортання

Алгоритм розгортання кута спирається на припущення критерію Найквіста: за один період опитування `dt` вал не повинен повертатися більш ніж на пів оберту (`Δθ < 180° = π` рад = 8192 LSB).

Максимальна кутова швидкість, яку здатен коректно розгортати алгоритм:

```
ω_max = (π / dt)  [рад / с]
RPM_max = (30 / dt)  [обертів за хвилину]
```

Для періоду опитування `dt = 100 мкс` (10 кГц) максимальна швидкість становить `300 000 об/хв`, що з великим запасом перекриває можливості будь-яких електродвигунів. Проте при рідкісному опитуванні (наприклад, у сплячих автономних датчиках із `dt = 100 мс`) гранична швидкість падає до `300 об/хв`, і швидкий рух вала вручну викличе пропуск обертів. У таких системах обробку енкодера виносять на апаратний таймерний вхід або мікроспоживаючий співпроцесор низького рівня (ULP).

## Часова діаграма та бюджет затримок контуру FOC

У контурах векторного керування (FOC) з частотою комутації ШІМ 20–40 кГц критичним параметром є повний час від фізичного кута ротора до готовності результату в регістрі мікроконтролера:

1. **Час реакції датчиків Холла та фільтрація кристала:** 1–3 мкс (визначається смугою пропускання інтегрованих підсилювачів).
2. **Час обчислення CORDIC на кристалі:** 0.5–1.5 мкс.
3. **Час передачі SPI (16 біт на 10 МГц):** `16 × 100 нс = 1.6 мкс`.
4. **Обчислення гармонійної корекції та фільтра стеження на Cortex-M4/M7 (168–480 МГц):** 0.2–0.4 мкс.

Сумарна затримка тракту становить приблизно **3.5–6.5 мкс**. На швидкості обертання 10 000 об/хв (1047 рад/с) затримка 5 мкс призводить до динамічного кутового зсуву:

```
Δθ_delay = ω · t_delay = 1047 рад/с · 0.000005 с = 0.00523 рад ≈ 0.30°
```

Для високошвидкісних двигунів цей зсув легко компенсується в алгоритмі FOC додаванням динамічного кута випередження `θ_foc = θ_est + ω_est · t_delay`, відновлюючи максимальний крутний момент на валу.

## Відновлення після апаратних збоїв та електромагнітних завад

При комутації потужних індуктивних навантажень напруга на фазах мотора змінюється зі швидкістю `dV/dt > 10 В/нс`, що може створювати короткочасні наведення на сигнальні лінії SPI (MISO / MOSI / SCK) і викликати спотворення окремих бітів.

Стратегія надійної обробки збоїв:
- **Одиночна помилка парності (Parity Error):** Пакет із порушеною парністю відкидається. Замість сирого кута фільтр стеження використовує свій екстрапольований прогноз `θ_pred[k] = θ_est[k-1] + ω_est[k-1] · dt`. Якщо протягом наступних 2–3 тактів зв'язок відновлюється, сервопривід продовжує рух без ривка.
- **Серія з 3+ помилок підряд:** Контролер ініціює апаратне перезавантаження інтерфейсу SPI: піднімає лінію `CSn = 1` на 5 мкс, надсилає команду очищення помилок `ERRFL` (0x4001) та знижує тактову частоту SPI. Якщо зв'язок не відновився, система переходить у режим аварійного гальмування (Safe Torque Off), захищаючи силову частину від втрати синхронізації.
