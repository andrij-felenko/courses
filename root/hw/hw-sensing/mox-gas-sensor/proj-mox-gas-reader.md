# ⚙️ Програмний рушій MOX-давача: компенсація вологості та трекер базової лінії

Отримання сирих даних від напівпровідникового газового давача (як-от Sensirion SGP40, Bosch BME680 чи ScioSense CCS811) — це лише перший крок низькорівневої обробки. Необроблений електричний опір чутливого шару SnO₂ або сирі 16-бітні відліки внутрішнього АЦП постійно плавають разом із вологістю навколишнього повітря й незворотно дрейфують через термічне старіння нагрівача та перекристалізацію зерен. Щоб перетворити нестабільний фізичний сигнал на надійний цифровий індекс якості повітря (VOC Index 0–500) та оцінку eCO₂, вбудованій системі потрібен спеціалізований математичний рушій компенсації.

Тут реалізовано повний програмний конвеєр обробки сигналу MOX: валідація пакетів шини I2C із підрахунком контрольної суми CRC-8, розрахунок абсолютної вологості за формулою Магнуса-Тетенса, експоненційна температурно-вологісна компенсація опору, асиметричний трекер базової лінії (Baseline Tracker) та генератор безрозмірного індексу летких органічних сполук.

## Фізико-математична модель конвеєра обробки

Сирий опір газочутливого шару `R_s` зменшується не лише під дією відновлювальних газів (VOC), але й при зростанні вологості довкілля, оскільки пари води `H2O` конкурують із киснем за центри хемосорбції на розпеченій поверхні напівпровідника, вивільняючи додаткові електрони в зону провідності.

1. **Розрахунок абсолютної вологості `AH` (г/м³):**
   Відносна вологість `RH` (%) показує лише ступінь насичення повітря за поточної температури, але кінетика поверхневих реакцій на гарячому кристалі (300 °C) залежить від фізичної кількості молекул води в одиниці об'єму. За температурою `T` (°C) та відносною вологістю `RH` (%) спочатку обчислюється тиск насиченої водяної пари `P_sat` (гПа) за наближенням Магнуса-Тетенса:
```
P_sat(T) = 6.112 · exp( (17.62 · T) / (243.12 + T) )
P_vapor = P_sat(T) · (RH / 100)
AH(T, RH) = 216.7 · (P_vapor / (273.15 + T))
```

2. **Експоненційна компенсація опору за абсолютною вологістю:**
   Знаючи поточну абсолютну вологість `AH` та стандартну опорну точку `AH_ref` (зазвичай 10.0 г/м³, що відповідає комфортним умовам 25 °C і 50% RH), скоригований опір `R_comp` знаходиться за формулою:
```
R_comp = R_s · exp( K_H · (AH - AH_ref) )
```
   де `K_H` — емпіричний коефіцієнт вологочутливості оксиду (типово `0.02..0.04` м³/г). Завдяки цій корекції добові коливання вологості (наприклад, увімкнення зволожувача повітря) не сприймаються алгоритмом як хімічне забруднення.

3. **Асиметричне відстеження базової лінії `R_base`:**
   Базова лінія відповідає опору давача у найчистішому повітрі за останні 24–72 години. Оскільки опір чистого повітря дрейфує протягом місяців через старіння нагрівача, алгоритм постійно коригує `R_base`. Якщо повітря стає чистішим (`R_comp > R_base`), фільтр адаптується швидко (постійна часу `τ_up ≈ 10–20` хвилин), щоб зафіксувати провітрювання приміщення. Якщо повітря бруднішає (`R_comp < R_base`), опір падає, але базова лінія не повинна падати вслід за газом, тому вона коригується надзвичайно повільно (`τ_down ≈ 24–72` години):
```
Якщо R_comp > R_base:  R_base = R_base + α_up · (R_comp - R_base)
Якщо R_comp ≤ R_base:  R_base = R_base + α_down · (R_comp - R_base)
```
   де `α = 1 - exp(-Δt / τ)`. При частоті дискретизації 1 Гц (`Δt = 1` с), `α_up ≈ 0.001`, а `α_down ≈ 0.00002`.

4. **Обчислення логарифмічного VOC Index (шкала 0–500):**
   Безрозмірний індекс представляє логарифмічне відхилення поточного скоригованого опору від адаптивної базової лінії:
```
Ratio = log( R_base / R_comp )
VOC_Index = clamp( 100 + S_gain · Ratio, 0, 500 )
```
   Точка `100` позначає типове фонове повітря в приміщенні, значення нижче 100 відповідають винятково чистій атмосфері, а значення понад 200 сигналізують про появу джерел забруднення (розчинників, спирту, диму).

## Програмна реалізація драйвера та рушія

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#define CRC8_POLYNOMIAL 0x31
#define CRC8_INIT       0xFF

/* Перевірка та розрахунок CRC-8 (поліном 0x31, x^8 + x^5 + x^4 + 1) */
uint8_t mox_crc8(const uint8_t *data, size_t len) {
    uint8_t crc = CRC8_INIT;
    for (size_t i = 0; i < len; i++) {
        crc ^= data[i];
        for (uint8_t bit = 0; bit < 8; bit++) {
            if (crc & 0x80) {
                crc = (crc << 1) ^ CRC8_POLYNOMIAL;
            } else {
                crc = (crc << 1);
            }
        }
    }
    return crc;
}

/* Розрахунок абсолютної вологості в г/м^3 */
float mox_calc_absolute_humidity(float temp_c, float rh_percent) {
    if (rh_percent < 0.0f) rh_percent = 0.0f;
    if (rh_percent > 100.0f) rh_percent = 100.0f;

    /* Формула Магнуса для тиску насиченої водяної пари в гПа */
    float p_sat = 6.112f * expf((17.62f * temp_c) / (243.12f + temp_c));
    float p_vapor = p_sat * (rh_percent / 100.0f);
    float abs_humidity = 216.7f * (p_vapor / (273.15f + temp_c));
    return abs_humidity;
}

typedef struct {
    float r_baseline;       /* Поточна оцінка базової лінії (кОм) */
    float alpha_up;         /* Коефіцієнт швидкої адаптації до чистого повітря */
    float alpha_down;       /* Коефіцієнт повільної деградації базової лінії */
    float k_humidity;       /* Чутливість до абсолютної вологості */
    float ref_humidity;     /* Опорна абсолютна вологість (10.0 г/м3) */
    float voc_gain;         /* Коефіцієнт масштабування логарифмічного відгуку */
    bool  is_warmed_up;     /* Прапорець завершення початкового прогріву */
    uint32_t sample_count;  /* Лічильник оброблених вимірів */
} MoxEngine;

void mox_engine_init(MoxEngine *eng, float initial_baseline_kohm) {
    eng->r_baseline = (initial_baseline_kohm > 1.0f) ? initial_baseline_kohm : 100.0f;
    /* При частоті виклику 1 Гц: */
    eng->alpha_up = 0.001f;      /* tau ~ 1000 секунд (16.6 хв) */
    eng->alpha_down = 0.00002f;  /* tau ~ 50000 секунд (13.8 год) */
    eng->k_humidity = 0.035f;    /* ~3.5% на 1 г/м3 вологи */
    eng->ref_humidity = 10.0f;   /* 25 °C, 50% RH */
    eng->voc_gain = 250.0f;
    eng->is_warmed_up = false;
    eng->sample_count = 0;
}

typedef struct {
    float r_compensated;   /* Опір сенсора з компенсацією вологості (кОм) */
    float r_baseline;      /* Поточний стан базової лінії (кОм) */
    int16_t voc_index;     /* Індекс VOC (0..500, норма = 100) */
    uint16_t eco2_ppm;     /* Розрахунковий eCO2 (400..60000 ppm) */
} MoxResult;

MoxResult mox_engine_process(MoxEngine *eng, float raw_r_kohm, float temp_c, float rh_percent) {
    MoxResult res;
    eng->sample_count++;

    /* Перші 60 секунд сенсор прогрівається */
    if (eng->sample_count > 60) {
        eng->is_warmed_up = true;
    }

    /* 1. Компенсація вологості */
    float ah = mox_calc_absolute_humidity(temp_c, rh_percent);
    float dh = ah - eng->ref_humidity;
    float comp_factor = expf(eng->k_humidity * dh);
    res.r_compensated = raw_r_kohm * comp_factor;

    /* 2. Асиметричний трекер базової лінії */
    if (eng->is_warmed_up) {
        if (res.r_compensated > eng->r_baseline) {
            /* Повітря чистіше за попередній фон: швидке підтягування базової лінії вгору */
            eng->r_baseline += eng->alpha_up * (res.r_compensated - eng->r_baseline);
        } else {
            /* Повітря брудніше (опір впав): надповільне сповзання вниз */
            eng->r_baseline += eng->alpha_down * (res.r_compensated - eng->r_baseline);
        }
    } else {
        /* Під час прогріву просто ініціалізуємо базову лінію */
        eng->r_baseline = res.r_compensated;
    }

    res.r_baseline = eng->r_baseline;

    /* 3. Обчислення логарифмічного VOC Index */
    float ratio = 0.0f;
    if (res.r_compensated > 0.001f && eng->r_baseline > 0.001f) {
        ratio = logf(eng->r_baseline / res.r_compensated);
    }

    float raw_index = 100.0f + eng->voc_gain * ratio;
    if (raw_index < 0.0f) raw_index = 0.0f;
    if (raw_index > 500.0f) raw_index = 500.0f;
    res.voc_index = (int16_t)(raw_index + 0.5f);

    /* 4. Емпіричний розрахунок еквівалентного CO2 (eCO2) */
    if (ratio <= 0.0f) {
        res.eco2_ppm = 400;
    } else {
        float eco2_calc = 400.0f + 1200.0f * powf(ratio, 1.45f);
        if (eco2_calc > 60000.0f) eco2_calc = 60000.0f;
        res.eco2_ppm = (uint16_t)eco2_calc;
    }

    return res;
}
```
```cpp
#include <cstdint>
#include <cmath>
#include <span>
#include <algorithm>
#include <expected>

namespace mox {

/* Розрахунок CRC-8 (поліном 0x31) з безпечним використанням std::span */
[[nodiscard]] constexpr uint8_t calculate_crc8(std::span<const uint8_t> data) noexcept {
    constexpr uint8_t polynomial = 0x31;
    uint8_t crc = 0xFF;
    for (uint8_t byte : data) {
        crc ^= byte;
        for (uint8_t bit = 0; bit < 8; ++bit) {
            crc = (crc & 0x80) ? static_cast<uint8_t>((crc << 1) ^ polynomial)
                               : static_cast<uint8_t>(crc << 1);
        }
    }
    return crc;
}

/* Модель вихідних метрик газового сенсора */
struct SensorMetrics {
    float compensated_resistance_kohm;
    float baseline_resistance_kohm;
    int16_t voc_index;     // 0..500, типовий фон = 100
    uint16_t eco2_ppm;     // 400..60000 ppm eCO2
};

enum class EngineError {
    SensorNotReady,
    InvalidSensorReading,
    HumidityOutOfRange
};

class GasProcessingEngine {
public:
    explicit constexpr GasProcessingEngine(float initial_baseline_kohm = 100.0f) noexcept
        : baseline_{std::max(1.0f, initial_baseline_kohm)} {}

    /* Обчислення абсолютної вологості за формулою Магнуса (г/м^3) */
    [[nodiscard]] static float absolute_humidity(float temp_c, float rh_percent) noexcept {
        const float clamped_rh = std::clamp(rh_percent, 0.0f, 100.0f);
        const float p_sat = 6.112f * std::exp((17.62f * temp_c) / (243.12f + temp_c));
        const float p_vapor = p_sat * (clamped_rh / 100.0f);
        return 216.7f * (p_vapor / (273.15f + temp_c));
    }

    /* Оновлення конвеєра вимірювання */
    [[nodiscard]] std::expected<SensorMetrics, EngineError> process_sample(
        float raw_resistance_kohm,
        float temp_c,
        float rh_percent) noexcept
    {
        if (raw_resistance_kohm <= 0.001f) {
            return std::unexpected(EngineError::InvalidSensorReading);
        }

        ++sample_count_;
        if (sample_count_ > warmup_threshold_) {
            is_warmed_up_ = true;
        }

        // 1. Вологісна компенсація
        const float ah = absolute_humidity(temp_c, rh_percent);
        const float delta_h = ah - reference_humidity_;
        const float comp_factor = std::exp(k_humidity_ * delta_h);
        const float comp_resistance = raw_resistance_kohm * comp_factor;

        // 2. Адаптація базової лінії
        if (is_warmed_up_) {
            if (comp_resistance > baseline_) {
                baseline_ += alpha_up_ * (comp_resistance - baseline_);
            } else {
                baseline_ += alpha_down_ * (comp_resistance - baseline_);
            }
        } else {
            baseline_ = comp_resistance;
        }

        // 3. Формування логарифмічного VOC Index
        const float ratio = std::log(baseline_ / comp_resistance);
        const float raw_voc = 100.0f + voc_gain_ * ratio;
        const auto clamped_voc = static_cast<int16_t>(std::clamp(raw_voc, 0.0f, 500.0f) + 0.5f);

        // 4. Оцінка eCO2
        uint16_t eco2 = 400;
        if (ratio > 0.0f) {
            const float calculated_eco2 = 400.0f + 1200.0f * std::pow(ratio, 1.45f);
            eco2 = static_cast<uint16_t>(std::clamp(calculated_eco2, 400.0f, 60000.0f));
        }

        return SensorMetrics{
            .compensated_resistance_kohm = comp_resistance,
            .baseline_resistance_kohm = baseline_,
            .voc_index = clamped_voc,
            .eco2_ppm = eco2
        };
    }

    [[nodiscard]] float get_baseline() const noexcept { return baseline_; }
    void restore_baseline(float saved_baseline_kohm) noexcept {
        if (saved_baseline_kohm > 1.0f) {
            baseline_ = saved_baseline_kohm;
            is_warmed_up_ = true;
        }
    }

private:
    float baseline_{100.0f};
    static constexpr float alpha_up_{0.001f};       // Швидкий ріст до чистого фону
    static constexpr float alpha_down_{0.00002f};   // Повільний спад
    static constexpr float k_humidity_{0.035f};     // Коефіцієнт впливу вологи
    static constexpr float reference_humidity_{10.0f};
    static constexpr float voc_gain_{250.0f};
    static constexpr uint32_t warmup_threshold_{60};
    uint32_t sample_count_{0};
    bool is_warmed_up_{false};
};

} // namespace mox
```
:::

## Інженерні пастки та взаємодія з енергонезалежною пам'яттю (NVS)

1. **Втрата базової лінії при перезавантаженні (Cold Start Amnesia):**
   Якщо прилад вимкнути з живлення та увімкнути заново в кімнаті з високим рівнем летких сполук (наприклад, у накуреному приміщенні або під час готування їжі), сенсор без збереженої історії ініціалізує нову базову лінію за поточним брудним повітрям і присвоїть йому індекс «100». Коли кімнату згодом провітрять, опір зросте, сенсор покаже нефізичний індекс 10–20 (надчисте повітря) і протягом наступних діб буде повністю сліпим до нових помірних забруднень.
   *Інженерне рішення:* організувати циклічне збереження значення `r_baseline` у Flash/EEPROM мікроконтролера кожні 1–2 години з перевіркою контрольної суми CRC32. Під час холодного старту прошивка завантажує збережене значення через метод `restore_baseline()`, що скорочує час виходу приладу на номінальний робочий режим із 24 годин до 60 секунд.

2. **Захист пам'яті Flash від зносу (Wear Leveling):**
   Запис базової лінії безпосередньо в один і той самий сектор Flash-пам'яті щогодини вичерпає ресурс у 10 000–100 000 циклів перезапису за кілька років експлуатації. Рекомендується застосовувати кільцевий буфер записів (NVS ring buffer) або бібліотеки збереження стану key-value (як-от ESP-IDF NVS чи Zephyr NVS), які розподіляють записи по всьому виділеному сектору пам'яті.

3. **Температурний шок і конденсат:**
   При раптовій зміні вологості (наприклад, перенесення приладу з холодної вулиці в теплий дім) на холодних стінках корпусу та захисній сітці утворюється мікроконденсат. Якщо рідка вода замкне вимірювальні доріжки на кристалі, опір впаде практично до нуля. Прошивка повинна містити санітарний фільтр: значення сирого опору `R_s < 100 Ом` або розрахункова абсолютна вологість `AH > 50 г/м³` маркуються як апаратна помилка `InvalidSensorReading`, блокуючи оновлення базової лінії.

4. **Період стабілізації нового сенсора (Burn-in Time):**
   Новий MOX-сенсор після монтажу на заводі містить сліди органічних розчинників із паяльної пасти та напруження в плівці оксиду. Виробники вимагають обов'язкового безперервного термічного тренування (burn-in) протягом 24–48 годин за номінальної температури 350 °C перед проведенням фінального калібрування приладу.
