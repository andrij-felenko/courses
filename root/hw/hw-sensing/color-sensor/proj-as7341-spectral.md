# ⚙️ Мультиспектральний спектрорадіометр та аналізатор світла на сенсорі AS7341

Трикамерні колориметри (RGB) здатні виміряти координати колірності `(x, y)` та корельовану колірну температуру, але вони принципово безсилі перед проблемою спектрального метамеризму: два джерела світла з однаковим CCT (наприклад, якісна лампа розжарювання 3000 K та дешевий люмінесцентний світильник 3000 K із провалами в червоній і бірюзовій зонах) для триканального датчика виглядають тотожно, проте освітлені ними кольорові предмети виглядатимуть по-різному. Щоб оцінити якість освітлення — індекс передачі кольору (CRI, від англ. *Color Rendering Index*) — або точно відновити неперервний спектральний розподіл потужності (SPD), необхідний багатоканальний мультиспектральний сенсор.

Мікросхема AS7341 фірми ams-OSRAM містить масив із 16 кремнієвих фотодіодів, на поверхню яких за допомогою тонкоплівкової технології нанесено діелектричні інтерференційні фільтри Фабрі-Перо. Сенсор формує 11 незалежних вимірювальних каналів: 8 вузькосмугових каналів видимого спектра (F1–F8: центральні довжини хвиль 415, 445, 480, 515, 555, 590, 630, 680 нм із шириною напіввисоти FWHM ~30–50 нм), широкосмуговий канал Clear, канал ближнього інфрачервоного діапазону NIR (910 нм) та окремий апаратний канал детекції мерехтіння світла (Flicker).

## Архітектура оптичного кристала та матриці SMUX

На кристалі AS7341 розташовано 16 окремих кремнієвих фотодіодів, організованих у матрицю 4×4. Проте мікросхема має лише 6 незалежних аналогових інтегрувальних АЦП (ADC0..ADC5). Щоб зчитати всі 11 спектральних смуг, використовується внутрішній аналоговий комутатор — матриця мультиплексування **SMUX** (англ. *Sensor Multiplexer*).

Матриця SMUX налаштовується шляхом запису 20 конфігураційних байтів у внутрішню пам'ять SMUX RAM (регістри `0x00..0x13`). Для отримання повного спектрального знімка мікроконтролер виконує два послідовні цикли перетворення:

1. **Банк конфігурації SMUX-1 (короткохвильові канали):**
   - ADC0 підключається до фотодіода `F1` (415 нм, фіолетовий);
   - ADC1 підключається до фотодіода `F2` (445 нм, індиго);
   - ADC2 підключається до фотодіода `F3` (480 нм, синій);
   - ADC3 підключається до фотодіода `F4` (515 нм, блакитний/зелений);
   - ADC4 підключається до фотодіода `Clear` (широкосмуговий з ІЧ-фільтром);
   - ADC5 підключається до фотодіода `NIR` (910 нм, ближнє інфрачервоне світло).

2. **Банк конфігурації SMUX-2 (довгохвильові канали):**
   - ADC0 підключається до фотодіода `F5` (555 нм, жовто-зелений);
   - ADC1 підключається до фотодіода `F6` (590 нм, жовтий);
   - ADC2 підключається до фотодіода `F7` (630 нм, помаранчево-червоний);
   - ADC3 підключається до фотодіода `F8` (680 нм, глибокий червоний);
   - ADC4 підключається до фотодіода `Clear` (повторний контроль освітленості);
   - ADC5 підключається до входу аналогового блоку `Flicker Engine` (детекція пульсацій).

Час перемикання SMUX між банками становить менше 50 мікросекунд, що дає змогу отримувати до 20 повних 11-канальних знімків спектра за секунду.

## Математичний алгоритм спектральної реконструкції

Після зчитування сирих 16-бітних кодів `Raw_i` вони приводяться до фізичної спектральної опроміненості `E(λ_i)` у міліватах на квадратний метр на нанометр (мВт/(м²·нм)):

```
E(λ_i) = (Raw_i · Cal_i) / (t_int · Gain)
```

де `Cal_i` — заводський калібрувальний коефіцієнт спектральної чутливості i-го каналу (визначається на монохроматорі), `t_int` — час інтегрування в мілісекундах, `Gain` — коефіцієнт аналогового підсилення.

Маючи 8 опорних точок `E(λ_1)..E(λ_8)`, неперервний спектр `S(λ)` від 380 до 720 нм апроксимують за допомогою кубічних сплайнів або розкладання за ортогональним базисом головних компонентів спектрів освітлення (PCA-базис Малінвельса-Парка):

```
S(λ) = S₀(λ) + w₁ · S₁(λ) + w₂ · S₂(λ)
```

Отриманий неперервний розподіл інтегрують із кривими `x̄(λ), ȳ(λ), z̄(λ)` для обчислення істинних координат CIE XYZ без апроксимаційних похибок 3-канальних сенсорів.

## Розрахунок загального індексу передачі кольору (CRI Ra)

Індекс передачі кольору CRI Ra стандартизовано методикою CIE 13.3-1995:
1. За координатами `(x, y)` тестового джерела обчислюють корельовану температуру CCT.
2. Обирають еталонний спектр порівняння `S_ref(λ)`: для `CCT < 5000 K` використовують спектр абсолютно чорного тіла Планка при тій самій температурі; для `CCT ≥ 5000 K` — стандартизовану модель денного світла CIE Daylight.
3. Розраховують колірні координати восьми стандартних зразків відбиття Манселла (TCS01..TCS08, пастельні кольори: від світло-рожевого до червонувато-бузкового) під досліджуваним джерелом та під еталоном.
4. Застосовують хроматичну адаптацію Фон Кріза для врахування зміни адаптації ока спостерігача.
5. Для кожного зразка обчислюють колориметричну колірну різницю `ΔE_i` у рівноконтрастному просторі CIE 1964 `(u*, v*, W*)` або CIELAB.
6. Частковий індекс для кожного зразка становить:
   ```
   R_i = 100 - 4.6 · ΔE_i
   ```
7. Загальний індекс передачі кольору `Ra` обчислюється як середнє арифметичне восьми часткових індексів:
   ```
   Ra = (1 / 8) · ∑ R_i   [для i від 1 до 8]
   ```

Для сонячного світла та якісних ламп розжарювання `Ra = 100`. Дешеві люмінесцентні лампи мають `Ra ≈ 60–75` через різкі емісійні піки ртуті та дефіцит червоного випромінювання. Професійні музейні та кінематографічні LED-світильники забезпечують `Ra > 95`.

## Апаратний блок детекції мерехтіння (Flicker Engine)

Канал Flicker підключає фотодіод до швидкодіючого аналогового тракту зі смуговим фільтром та лічильником переходів через нуль. Блок детектує коливання світлового потоку на частотах 50 Гц, 60 Гц, 100 Гц, 120 Гц та вище (до 1 кГц).

Виявлення частоти мерехтіння виконується повністю апаратно: після завершення циклу вимірювання мікроконтролер читає статусний регістр `0xDB` (`FD_STATUS`), де встановлюються біти виявлення 100 Гц або 120 Гц. Це дає змогу камері смартфону або промисловому зору автоматично встановити час експозиції затвора, кратний періоду мерехтіння, уникаючи смуг на зображенні (banding).

## Реалізація спектрорадіометра та аналізатора CRI на C та C++

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#define AS7341_I2C_ADDR         0x39

/* Регістри керування AS7341 */
#define AS7341_REG_ENABLE       0x80
#define AS7341_REG_ATIME        0x81
#define AS7341_REG_ASTEP_L      0xCA
#define AS7341_REG_ASTEP_H      0xCB
#define AS7341_REG_CFG_1        0xAA
#define AS7341_REG_STATUS       0x71
#define AS7341_REG_CH0_DATA_L   0x95

/* Структура 11 каналів сенсора AS7341 */
typedef struct {
    uint16_t f1_415nm;
    uint16_t f2_445nm;
    uint16_t f3_480nm;
    uint16_t f4_515nm;
    uint16_t f5_555nm;
    uint16_t f6_590nm;
    uint16_t f7_630nm;
    uint16_t f8_680nm;
    uint16_t clear;
    uint16_t nir;
    uint8_t  flicker_freq_hz;
} as7341_raw_data_t;

/* Результати спектрального аналізу */
typedef struct {
    float x;
    float y;
    float cct_kelvin;
    float lux;
    float cri_ra;
    float spd_mw_m2_nm[8];  /* Спектральна густина для 8 смуг */
} as7341_spectral_result_t;

/* Обчислення колірної температури за формулою МакКамі */
static float calculate_cct_mccamy(float x, float y) {
    if (fabsf(0.1858f - y) < 1e-5f) return 0.0f;
    float n = (x - 0.3320f) / (0.1858f - y);
    float n2 = n * n;
    float n3 = n2 * n;
    return 449.0f * n3 + 3525.0f * n2 + 6823.3f * n + 5520.33f;
}

/* Наближений розрахунок CRI Ra за 8 спектральними смугами */
static float estimate_cri_ra(const float spd[8], float cct) {
    /* Базове порівняння енергії в червоній (F7, F8) та синьо-зеленій зоні */
    float blue_sum = spd[0] + spd[1] + spd[2];
    float green_sum = spd[3] + spd[4];
    float red_sum = spd[5] + spd[6] + spd[7];
    float total = blue_sum + green_sum + red_sum;

    if (total < 1e-4f) return 0.0f;

    /* Штраф за спектральні провали відносно гладкого теплового спектра */
    float r_ratio = red_sum / total;
    float g_ratio = green_sum / total;
    float b_ratio = blue_sum / total;

    /* Для теплого світла < 4000 K брак червоного (R9/F7/F8) різко знижує CRI */
    float penalty = 0.0f;
    if (cct < 3500.0f && r_ratio < 0.35f) {
        penalty += (0.35f - r_ratio) * 150.0f;
    }
    if (g_ratio > 0.55f) { /* Типовий пік дешевих люмінесцентних ламп 546 нм */
        penalty += (g_ratio - 0.55f) * 120.0f;
    }

    float ra = 100.0f - penalty;
    if (ra > 100.0f) ra = 100.0f;
    if (ra < 0.0f) ra = 0.0f;
    return ra;
}

/* Повний конвеєр обробки сирих даних AS7341 */
void as7341_process_spectrum(const as7341_raw_data_t *raw, float atime_ms, float gain, as7341_spectral_result_t *res) {
    float norm_factor = (atime_ms * gain > 0.0f) ? (1.0f / (atime_ms * gain)) : 1.0f;

    /* Коефіцієнти калібрування каналів (відгук у мкВт/см²/відлік) */
    const float cal[8] = { 0.12f, 0.10f, 0.09f, 0.085f, 0.080f, 0.075f, 0.070f, 0.082f };

    res->spd_mw_m2_nm[0] = (float)raw->f1_415nm * norm_factor * cal[0];
    res->spd_mw_m2_nm[1] = (float)raw->f2_445nm * norm_factor * cal[1];
    res->spd_mw_m2_nm[2] = (float)raw->f3_480nm * norm_factor * cal[2];
    res->spd_mw_m2_nm[3] = (float)raw->f4_515nm * norm_factor * cal[3];
    res->spd_mw_m2_nm[4] = (float)raw->f5_555nm * norm_factor * cal[4];
    res->spd_mw_m2_nm[5] = (float)raw->f6_590nm * norm_factor * cal[5];
    res->spd_mw_m2_nm[6] = (float)raw->f7_630nm * norm_factor * cal[6];
    res->spd_mw_m2_nm[7] = (float)raw->f8_680nm * norm_factor * cal[7];

    /* Матрична згортка у координати CIE 1931 XYZ (матриця чутливості 3x8) */
    float X = 0.05f * res->spd_mw_m2_nm[0] + 0.35f * res->spd_mw_m2_nm[1] + 0.15f * res->spd_mw_m2_nm[2] +
              0.02f * res->spd_mw_m2_nm[3] + 0.30f * res->spd_mw_m2_nm[4] + 0.85f * res->spd_mw_m2_nm[5] +
              1.05f * res->spd_mw_m2_nm[6] + 0.35f * res->spd_mw_m2_nm[7];

    float Y = 0.01f * res->spd_mw_m2_nm[0] + 0.05f * res->spd_mw_m2_nm[1] + 0.14f * res->spd_mw_m2_nm[2] +
              0.55f * res->spd_mw_m2_nm[3] + 0.98f * res->spd_mw_m2_nm[4] + 0.75f * res->spd_mw_m2_nm[5] +
              0.25f * res->spd_mw_m2_nm[6] + 0.02f * res->spd_mw_m2_nm[7];

    float Z = 0.95f * res->spd_mw_m2_nm[0] + 1.85f * res->spd_mw_m2_nm[1] + 0.85f * res->spd_mw_m2_nm[2] +
              0.05f * res->spd_mw_m2_nm[3];

    float sum = X + Y + Z;
    if (sum > 1e-4f) {
        res->x = X / sum;
        res->y = Y / sum;
    } else {
        res->x = 0.3127f;
        res->y = 0.3290f;
    }

    res->lux = 683.0f * Y;
    res->cct_kelvin = calculate_cct_mccamy(res->x, res->y);
    res->cri_ra = estimate_cri_ra(res->spd_mw_m2_nm, res->cct_kelvin);
}
```
```cpp
#include <cstdint>
#include <cmath>
#include <array>
#include <optional>
#include <span>
#include <algorithm>

namespace sensors {

struct RawSpectralChannels {
    uint16_t f1_415nm{0};
    uint16_t f2_445nm{0};
    uint16_t f3_480nm{0};
    uint16_t f4_515nm{0};
    uint16_t f5_555nm{0};
    uint16_t f6_590nm{0};
    uint16_t f7_630nm{0};
    uint16_t f8_680nm{0};
    uint16_t clear{0};
    uint16_t nir{0};
    uint8_t  flicker_freq_hz{0};
};

struct SpectralAnalysisResult {
    float x{0.3127f};
    float y{0.3290f};
    float cct_kelvin{6504.0f};
    float lux{0.0f};
    float cri_ra{100.0f};
    std::array<float, 8> spd_density{};
};

class AS7341SpectralAnalyzer {
public:
    static constexpr uint8_t I2C_ADDRESS = 0x39;

    [[nodiscard]] static constexpr float calculateCctMcCamy(float x, float y) noexcept {
        if (std::abs(0.1858f - y) < 1e-5f) return 0.0f;
        const float n = (x - 0.3320f) / (0.1858f - y);
        const float n2 = n * n;
        const float n3 = n2 * n;
        return 449.0f * n3 + 3525.0f * n2 + 6823.3f * n + 5520.33f;
    }

    [[nodiscard]] static SpectralAnalysisResult process(const RawSpectralChannels& raw,
                                                         float integration_time_ms,
                                                         float analog_gain) noexcept {
        SpectralAnalysisResult result{};
        const float norm = (integration_time_ms * analog_gain > 0.0f)
                         ? (1.0f / (integration_time_ms * analog_gain))
                         : 1.0f;

        constexpr std::array<float, 8> CALIBRATION_RESPONSIVITY = {
            0.120f, 0.100f, 0.090f, 0.085f, 0.080f, 0.075f, 0.070f, 0.082f
        };

        const std::array<uint16_t, 8> raw_bands = {
            raw.f1_415nm, raw.f2_445nm, raw.f3_480nm, raw.f4_515nm,
            raw.f5_555nm, raw.f6_590nm, raw.f7_630nm, raw.f8_680nm
        };

        for (size_t i = 0; i < 8; ++i) {
            result.spd_density[i] = static_cast<float>(raw_bands[i]) * norm * CALIBRATION_RESPONSIVITY[i];
        }

        // Згортка 8 смуг у тристимулус CIE 1931 XYZ
        const float X = 0.05f * result.spd_density[0] + 0.35f * result.spd_density[1] +
                        0.15f * result.spd_density[2] + 0.02f * result.spd_density[3] +
                        0.30f * result.spd_density[4] + 0.85f * result.spd_density[5] +
                        1.05f * result.spd_density[6] + 0.35f * result.spd_density[7];

        const float Y = 0.01f * result.spd_density[0] + 0.05f * result.spd_density[1] +
                        0.14f * result.spd_density[2] + 0.55f * result.spd_density[3] +
                        0.98f * result.spd_density[4] + 0.75f * result.spd_density[5] +
                        0.25f * result.spd_density[6] + 0.02f * result.spd_density[7];

        const float Z = 0.95f * result.spd_density[0] + 1.85f * result.spd_density[1] +
                        0.85f * result.spd_density[2] + 0.05f * result.spd_density[3];

        const float sum = X + Y + Z;
        if (sum > 1e-4f) {
            result.x = X / sum;
            result.y = Y / sum;
        }

        result.lux = 683.0f * Y;
        result.cct_kelvin = calculateCctMcCamy(result.x, result.y);
        result.cri_ra = estimateCri(result.spd_density, result.cct_kelvin);

        return result;
    }

private:
    [[nodiscard]] static float estimateCri(std::span<const float, 8> spd, float cct) noexcept {
        const float blue_sum = spd[0] + spd[1] + spd[2];
        const float green_sum = spd[3] + spd[4];
        const float red_sum = spd[5] + spd[6] + spd[7];
        const float total = blue_sum + green_sum + red_sum;

        if (total < 1e-4f) return 0.0f;

        const float r_ratio = red_sum / total;
        const float g_ratio = green_sum / total;

        float penalty = 0.0f;
        if (cct < 3500.0f && r_ratio < 0.35f) {
            penalty += (0.35f - r_ratio) * 150.0f;
        }
        if (g_ratio > 0.55f) {
            penalty += (g_ratio - 0.55f) * 120.0f;
        }

        return std::clamp(100.0f - penalty, 0.0f, 100.0f);
    }
};

} // namespace sensors
```
:::

Мультиспектральний підхід усуває головний дефект триканальних сенсорів — нездатність виявити вузькосмугові піки люмінофорів та дефіцит глибокого червоного кольору (смуга R9, 680 нм), що робить його незамінним для медичної діагностики, тепличного освітлення рослин (контроль спектрів фотосинтезу PAR) та калібрування професійних поліграфічних панелей.
