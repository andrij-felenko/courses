# ⚙️ Програмний конвеєр триосьового вимірювача напруженості поля

Вимірювання напруженості електромагнітного поля на мікроконтролері вимагає поєднання трьох обчислювальних кроків: багатоканального зчитування аналогових напруг з ортогональних датчиків, калібрувальної лінеаризації за таблицями чинника антени `AF(f)` і температурного дрейфу, та ковзного середньоквадратичного усереднення для оцінки відповідності санітарним нормам ICNIRP / IEEE C95.1.

## Архітектура та організація пам'яті вбудованого модуля

Конвеєр обробки польових даних проектується з урахуванням жорстких вимог до детермінізму вбудованого коду (відповідність стандартам безпеки функціональної надійності типу IEC 61508 або MISRA C:2012). Усі структури даних мають фіксований розмір, динамічне виділення пам'яті в купі (`malloc` / `new`) повністю виключено, а обчислювальна складність кожного циклу обробки становить строго `O(N)` від кількості точок калібрувальної таблиці.

Повний алгоритмічний конвеєр містить шість послідовних кроків обробки:

1. **Багатоканальне аналого-цифрове перетворення:**
   Зчитування миттєвих напруг з трьох диференційних каналів АЦП, підключених до виходів детекторів осей X, Y, Z, а також допоміжного каналу термодавача, розташованого безпосередньо всередині вимірювальної головки. Для запобігання фазовим похибкам під час модульованого випромінювання застосовується режим одночасного вибіркового фіксування (Simultaneous Sampling).

2. **Температурна компенсація та лінеаризація нуля:**
   Діоди Шотткі без зміщення мають значну температурну залежність прямого падіння напруги (типово від `-1.8` до `-2.2 мВ/°C`). Прошивка фіксує відхилення поточної температури `T` від температури первинного заводського калібрування `T_cal` і виконує лінійну корекцію напруги. Напруга зміщення операційних підсилювачів та шуми квантування відтинаються на рівні апаратного порога чутливості (Noise Floor Gate).

3. **Ортогональна корекція просторового базису:**
   Через виробничі допуски кути між трьома диполями можуть відхилятися від ідеальних 90°. Вектор компенсованих напруг множиться на заздалегідь розраховану інверсну матрицю зв'язку `M⁻¹` розміром 3×3, що усуває взаємний паразитний вплив осей.

4. **Частотна інтерполяція антенного фактора AF(f):**
   Оскільки зонд є широкосмуговим, його чутливість залежить від частоти випромінювання. У флеш-пам'яті приладу зберігається таблиця чинника антени `AF_dB`, отримана під час повірки в еталонній ТЕМ-камері (Transverse Electro-Magnetic cell). Драйвер виконує кусочно-лінійну інтерполяцію коефіцієнта для поточної обраної користувачем частоти передавача.

5. **Просторове векторне підсумовування:**
   Обчислення напруженості для кожної осі: `E_k = V_k · 10^(AF/20)`. Модуль сумарного вектора поля розраховується через корінь із суми квадратів: `E_total = √(E_x² + E_y² + E_z²)`, а густина потоку потужності Пойнтінга — через хвильовий опір вакууму: `S = E_total² / 376.73`.

6. **Кільцевий RMS-буфер усереднення та контроль безпеки:**
   Санітарні стандарти ICNIRP / IEEE C95.1 вимагають оцінки не миттєвого піку, а теплового еквівалента — середньоквадратичного значення (Root Mean Square) за ковзне вікно тривалістю 6 хвилин (360 секунд). Для ефективного розрахунку на кожному кроці оновлюється біжуча сума квадратів `∑ E²` у кільцевому буфері зі складністю `O(1)`.

Нижче наведено повну реалізацію обчислювального ядра на мовах C та C++.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#define FIELD_METER_CAL_POINTS_MAX 32
#define FIELD_METER_RMS_WINDOW_SIZE 360  /* 360 вибірок по 1 с = 6 хвилин вікна ICNIRP */
#define WAVE_IMPEDANCE_FREE_SPACE 376.730313f

typedef struct {
    float freq_mhz;
    float af_db;        /* Антенний фактор у дБ(1/м) */
} CalPoint;

typedef struct {
    CalPoint cal_table[FIELD_METER_CAL_POINTS_MAX];
    uint16_t cal_count;
    float ortho_matrix[3][3];    /* Матриця компенсації неортогональності M^-1 */
    float temp_coeff_v_per_c;    /* Температурний дрейф детектора, В/°C */
    float t_cal_celsius;         /* Температура заводського калібрування */
    float v_offset[3];           /* Напруга зміщення нуля каналів, В */
} FieldProbeConfig;

typedef struct {
    float e_x;          /* Напруженість E_x, В/м */
    float e_y;          /* Напруженість E_y, В/м */
    float e_z;          /* Напруженість E_z, В/м */
    float e_total;      /* Повна напруженість E_tot, В/м */
    float s_power_wm2;  /* Густина потоку потужності Пойнтінга, Вт/м² */
    float e_rms_6min;   /* Середньоквадратичне значення за вікно 6 хв, В/м */
    float exposure_pct; /* Відсоток від ліміту безпеки ICNIRP, % */
    bool is_valid;
} FieldMeasurement;

typedef struct {
    FieldProbeConfig config;
    float ring_buffer[FIELD_METER_RMS_WINDOW_SIZE];
    uint16_t ring_head;
    uint16_t ring_count;
    float ring_sum_sq;
} FieldMeterDriver;

void field_meter_init(FieldMeterDriver *meter, const FieldProbeConfig *cfg) {
    if (!meter || !cfg) return;
    meter->config = *cfg;
    meter->ring_head = 0;
    meter->ring_count = 0;
    meter->ring_sum_sq = 0.0f;
    for (int i = 0; i < FIELD_METER_RMS_WINDOW_SIZE; i++) {
        meter->ring_buffer[i] = 0.0f;
    }
}

/* Інтерполяція антенного фактора AF (дБ/м) за робочою частотою */
static float interpolate_af_db(const FieldProbeConfig *cfg, float freq_mhz) {
    if (cfg->cal_count == 0) return 0.0f;
    if (freq_mhz <= cfg->cal_table[0].freq_mhz) return cfg->cal_table[0].af_db;
    if (freq_mhz >= cfg->cal_table[cfg->cal_count - 1].freq_mhz) {
        return cfg->cal_table[cfg->cal_count - 1].af_db;
    }

    for (uint16_t i = 0; i < cfg->cal_count - 1; i++) {
        if (freq_mhz >= cfg->cal_table[i].freq_mhz && freq_mhz <= cfg->cal_table[i + 1].freq_mhz) {
            float f0 = cfg->cal_table[i].freq_mhz;
            float f1 = cfg->cal_table[i + 1].freq_mhz;
            float af0 = cfg->cal_table[i].af_db;
            float af1 = cfg->cal_table[i + 1].af_db;
            float t = (freq_mhz - f0) / (f1 - f0);
            return af0 + t * (af1 - af0);
        }
    }
    return cfg->cal_table[0].af_db;
}

/* Розрахунок гранично допустимого рівня напруженості поля за ICNIRP 2020 (населення) */
static float get_icnirp_general_limit(float freq_mhz) {
    if (freq_mhz < 0.1f) return 614.0f;
    if (freq_mhz <= 1.0f) return 87.0f / (float)sqrt(freq_mhz);
    if (freq_mhz <= 30.0f) return 87.0f / (float)sqrt(freq_mhz);
    if (freq_mhz <= 400.0f) return 28.0f;  /* Зона резонансу людського тіла */
    if (freq_mhz <= 2000.0f) return 1.375f * (float)sqrt(freq_mhz);
    return 61.0f; /* 2 ГГц - 300 ГГц */
}

FieldMeasurement field_meter_process(FieldMeterDriver *meter, 
                                    const float v_raw[3], 
                                    float temp_celsius, 
                                    float target_freq_mhz) {
    FieldMeasurement res = {0};
    if (!meter || !v_raw) return res;

    /* 1. Температурна компенсація та усунення зміщення нуля */
    float temp_delta = temp_celsius - meter->config.t_cal_celsius;
    float v_comp[3];
    for (int i = 0; i < 3; i++) {
        float v_zero_corrected = v_raw[i] - meter->config.v_offset[i];
        v_comp[i] = v_zero_corrected - (temp_delta * meter->config.temp_coeff_v_per_c);
        if (v_comp[i] < 0.0f) v_comp[i] = 0.0f;
    }

    /* 2. Ортогональна корекція: V_ortho = M^-1 * V_comp */
    float v_ortho[3] = {0};
    for (int r = 0; r < 3; r++) {
        for (int c = 0; c < 3; c++) {
            v_ortho[r] += meter->config.ortho_matrix[r][c] * v_comp[c];
        }
        if (v_ortho[r] < 0.0f) v_ortho[r] = 0.0f;
    }

    /* 3. Отримання антенного фактора та переведення в лінійний масштаб */
    float af_db = interpolate_af_db(&meter->config, target_freq_mhz);
    float af_linear = (float)pow(10.0, af_db / 20.0);

    /* 4. Розрахунок польових величин */
    res.e_x = v_ortho[0] * af_linear;
    res.e_y = v_ortho[1] * af_linear;
    res.e_z = v_ortho[2] * af_linear;

    float e_sq = res.e_x * res.e_x + res.e_y * res.e_y + res.e_z * res.e_z;
    res.e_total = (float)sqrt(e_sq);
    res.s_power_wm2 = e_sq / WAVE_IMPEDANCE_FREE_SPACE;

    /* 5. Оновлення ковзного кільцевого RMS-буфера */
    if (meter->ring_count == FIELD_METER_RMS_WINDOW_SIZE) {
        meter->ring_sum_sq -= meter->ring_buffer[meter->ring_head];
    } else {
        meter->ring_count++;
    }

    meter->ring_buffer[meter->ring_head] = e_sq;
    meter->ring_sum_sq += e_sq;
    if (meter->ring_sum_sq < 0.0f) meter->ring_sum_sq = 0.0f;

    meter->ring_head = (meter->ring_head + 1) % FIELD_METER_RMS_WINDOW_SIZE;
    res.e_rms_6min = (float)sqrt(meter->ring_sum_sq / (float)meter->ring_count);

    /* 6. Оцінка експозиції за нормами безпеки */
    float limit = get_icnirp_general_limit(target_freq_mhz);
    res.exposure_pct = (res.e_rms_6min / limit) * 100.0f;
    res.is_valid = true;

    return res;
}
```
```cpp
#include <array>
#include <span>
#include <cmath>
#include <concepts>
#include <optional>
#include <algorithm>

constexpr float WAVE_IMPEDANCE_VACUUM = 376.730313f;
constexpr std::size_t DEFAULT_RMS_WINDOW = 360; // 6 хвилин при 1 Гц

struct CalPoint {
    float freq_mhz;
    float af_db;
};

struct FieldMetrics {
    float e_x{0.0f};
    float e_y{0.0f};
    float e_z{0.0f};
    float e_total{0.0f};
    float s_power_wm2{0.0f};
    float e_rms_window{0.0f};
    float exposure_pct{0.0f};
};

template <std::size_t CalPointsMax = 32, std::size_t WindowSize = DEFAULT_RMS_WINDOW>
class FieldMeterProcessor {
public:
    struct Config {
        std::array<CalPoint, CalPointsMax> cal_table{};
        std::size_t cal_count{0};
        std::array<std::array<float, 3>, 3> ortho_matrix{
            std::array<float, 3>{1.0f, 0.0f, 0.0f},
            std::array<float, 3>{0.0f, 1.0f, 0.0f},
            std::array<float, 3>{0.0f, 0.0f, 1.0f}
        };
        float temp_coeff_v_per_c{0.0f};
        float t_cal_celsius{25.0f};
        std::array<float, 3> v_offset{0.0f, 0.0f, 0.0f};
    };

    explicit constexpr FieldMeterProcessor(Config config) noexcept 
        : config_(std::move(config)) {}

    [[nodiscard]] std::optional<FieldMetrics> process(
        std::span<const float, 3> v_raw, 
        float temp_celsius, 
        float target_freq_mhz) noexcept 
    {
        if (config_.cal_count == 0 || target_freq_mhz <= 0.0f) {
            return std::nullopt;
        }

        // 1. Температурна компенсація
        const float temp_delta = temp_celsius - config_.t_cal_celsius;
        std::array<float, 3> v_comp{};
        for (std::size_t i = 0; i < 3; ++i) {
            float v_adj = (v_raw[i] - config_.v_offset[i]) - (temp_delta * config_.temp_coeff_v_per_c);
            v_comp[i] = std::max(0.0f, v_adj);
        }

        // 2. Ортогоналізація
        std::array<float, 3> v_ortho{0.0f, 0.0f, 0.0f};
        for (std::size_t r = 0; r < 3; ++r) {
            for (std::size_t c = 0; c < 3; ++c) {
                v_ortho[r] += config_.ortho_matrix[r][c] * v_comp[c];
            }
            v_ortho[r] = std::max(0.0f, v_ortho[r]);
        }

        // 3. Інтерполяція антенного фактора
        const float af_db = interpolate_af(target_freq_mhz);
        const float af_lin = std::pow(10.0f, af_db / 20.0f);

        // 4. Обчислення векторних компонентів
        FieldMetrics m{};
        m.e_x = v_ortho[0] * af_lin;
        m.e_y = v_ortho[1] * af_lin;
        m.e_z = v_ortho[2] * af_lin;

        const float e_sq = m.e_x * m.e_x + m.e_y * m.e_y + m.e_z * m.e_z;
        m.e_total = std::sqrt(e_sq);
        m.s_power_wm2 = e_sq / WAVE_IMPEDANCE_VACUUM;

        // 5. Кільцевий RMS акумулятор
        update_rms(e_sq);
        m.e_rms_window = std::sqrt(ring_sum_sq_ / static_cast<float>(ring_count_));

        // 6. Санітарний ліміт ICNIRP 2020
        const float limit = calculate_icnirp_limit(target_freq_mhz);
        m.exposure_pct = (m.e_rms_window / limit) * 100.0f;

        return m;
    }

    void reset_rms() noexcept {
        ring_head_ = 0;
        ring_count_ = 0;
        ring_sum_sq_ = 0.0f;
        ring_buffer_.fill(0.0f);
    }

private:
    [[nodiscard]] float interpolate_af(float freq_mhz) const noexcept {
        const auto& table = config_.cal_table;
        if (freq_mhz <= table[0].freq_mhz) return table[0].af_db;
        if (freq_mhz >= table[config_.cal_count - 1].freq_mhz) {
            return table[config_.cal_count - 1].af_db;
        }

        for (std::size_t i = 0; i < config_.cal_count - 1; ++i) {
            if (freq_mhz >= table[i].freq_mhz && freq_mhz <= table[i + 1].freq_mhz) {
                const float t = (freq_mhz - table[i].freq_mhz) / 
                                (table[i + 1].freq_mhz - table[i].freq_mhz);
                return table[i].af_db + t * (table[i + 1].af_db - table[i].af_db);
            }
        }
        return table[0].af_db;
    }

    void update_rms(float e_sq) noexcept {
        if (ring_count_ == WindowSize) {
            ring_sum_sq_ -= ring_buffer_[ring_head_];
        } else {
            ++ring_count_;
        }
        ring_buffer_[ring_head_] = e_sq;
        ring_sum_sq_ = std::max(0.0f, ring_sum_sq_ + e_sq);
        ring_head_ = (ring_head_ + 1) % WindowSize;
    }

    [[nodiscard]] static constexpr float calculate_icnirp_limit(float freq_mhz) noexcept {
        if (freq_mhz < 0.1f) return 614.0f;
        if (freq_mhz <= 30.0f) return 87.0f / std::sqrt(freq_mhz);
        if (freq_mhz <= 400.0f) return 28.0f;
        if (freq_mhz <= 2000.0f) return 1.375f * std::sqrt(freq_mhz);
        return 61.0f;
    }

    Config config_;
    std::array<float, WindowSize> ring_buffer_{};
    std::size_t ring_head_{0};
    std::size_t ring_count_{0};
    float ring_sum_sq_{0.0f};
};
```
:::

## Інженерні пастки та тонкощі практичної реалізації

Практична експлуатація вимірювача напруженості поля в умовах складної радіообстановки виявляє низку апаратних і програмних крайових випадків:

1. **Аліасинг імпульсних радіосигналів (TDMA / Radar):**
   У мережах GSM/LTE та імпульсних радіолокаторах передавач випромінює короткими пачками тривалістю від одиниць мікросекунд до 577 мкс з високою шпаруватістю (duty cycle 1:8 або 1:100). Якщо АЦП мікроконтролера здійснює вибірку із частотою 10–100 Гц, більшість вибірок потрапить у паузу між радіоімпульсами, занижуючи виміряну напруженість поля в десятки разів. 
   *Інженерне рішення:* Застосування на виході детектора апаратного інтегрувального ФНЧ із постійною часу `τ ~ 20-50 мс` або використання швидкодіючого АЦП із частотою дискретизації понад 50 кГц із програмним захопленням пікових значень (Peak Hold).

2. **Температурний дрейф напівпровідникового бар'єра:**
   Пряме падіння напруги діода Шотткі має температурний коефіцієнт близько `-2 мВ/°C`. За слабких полів, коли випрямлена корисна напруга становить лише одиниці мікровольтів, зміна температури корпусу приладу на 1 °C спричиняє уявний сплеск напруженості поля на десятки вольтів на метр.
   *Інженерне рішення:* Обов'язкове розміщення прецизійного цифрового термодавача безпосередньо всередині екранованого відсіку вимірювальної головки біля детекторів і застосування матриці індивідуальної температурної корекції.

3. **Синхронність зчитування трьох осей:**
   Якщо три канали X, Y, Z оцифровуються послідовно через один спільний АЦП із тривалою затримкою комутації, швидке просторове обертання зонда або амплітудна модуляція сигналу спотворять сумарний вектор `E_total`. Триосьове вимірювання вимагає або мікросхеми АЦП з одночасним вибірковим фіксуванням (Simultaneous Sampling ADC), або частоти мультиплексування, яка на порядки перевищує смугу модуляції вимірюваного поля.

4. **Паразитне наведення на сигнальні провідники:**
   Якщо лінії передачі від датчиків до підсилювача виконані зі звичайного мідного дроту або коаксіального кабелю, вони самі резонують у полі високої частоти й створюють струми наведення, що на порядки перевищують сигнал від вимірювальних диполів.
   *Інженерне рішення:* Застосування високовольтної резистивної плівки (вуглецеві або ніхромові доріжки з опором ~100 кОм/м), яка повністю прозора для падаючої радіохвилі й не вносить спотворень у діаграму спрямованості зонда.
