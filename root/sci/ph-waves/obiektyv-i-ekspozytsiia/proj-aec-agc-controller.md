# ⚙️ Модуль автоматичного регулювання експозиції та підсилення AEC/AGC

Вбудовані системи технічного зору, камери дронів та промислові сенсори потребують неперервного підтримання оптимальної фотометричної яскравості зображення при динамічній зміні освітленості сцени. Якщо об'єкт переміщується з яскравого сонячного світла в тінь, контур автоекспозиції (AEC — Auto Exposure Control) та автопідсилення (AGC — Auto Gain Control) зобов'язаний скоригувати параметри сенсора за мінімальну кількість кадрів без виникнення автоколивань, перерегулювання та розривів у роботі алгоритмів просторового трекінгу.

Нижче наведено модульну архітектуру, теоретичний аналіз передавальних функцій та повний робочий код контролера AEC/AGC мовами C та C++20, що реалізує зважений за центром збір фотометричної статистики, пропорційно-інтегральну фільтрацію похибки з гістерезисною зоною нечутливості, пріоритетний розподіл ресурсу між витримкою й аналоговим підсиленням та апаратний захист від мерехтіння освітлення (Anti-Flicker).

## Архітектура та логіка роботи контролера

Контролер обробляє кожен вхідний кадр за чотири послідовні фази:

```
[Вхідний кадр] ──> 1. Зважена яскравість ──> 2. Обчислення ΔEV ──> 3. Розподіл (t_exp, Gain) ──> 4. Квантування Anti-Flicker ──> [Регістри сенсора]
```

1. **Збір статистики (Center-Weighted Luminance)**: Кадр дискретизується на сітку блоків `8 × 8` або `16 × 16`. Для кожного пікселя чи блоку обчислюється яскравість `Y = 0.299·R + 0.587·G + 0.114·B`. Центральні блоки зважуються вищими коефіцієнтами за гаусовою маскою, що запобігає впливу яскравого фону по краях кадру.
2. **Фільтрація похибки та розрахунок зсуву `ΔEV`**:
   - Похибка регулювання: `e = Y_target - Y_current`.
   - Зона нечутливості: якщо `|e| ≤ Deadband`, зміна параметрів блокується (`ΔEV = 0`), що усуває паразитичне тремтіння яскравості між сусідніми кадрами.
   - Якщо похибка виходить за межі зони нечутливості, розраховується логарифмічний крок корекції експозиції з коефіцієнтом демпфування `K_p`:
     ```
     ΔEV = K_p · log₂(Y_target / max(Y_current, 1.0))
     ```
3. **Пріоритетний розподіл (Exposure Scheduling)**:
   - Новий коефіцієнт експозиції масштабується множником `Scale = 2^(ΔEV)`.
   - Загальний запит на експозицію `Exposure_Total = t_exp · Gain · Scale`.
   - **Пріоритет витримки**: якщо світла достатньо, час витримки зменшується до необхідного значення, а підсилення утримується на мінімумі `Gain = 1.0` (ISO 100).
   - При нестачі світла час витримки збільшується до заданого ліміту проти змазу руху `t_max_motion` (наприклад, `8333 мкс` для камери зі швидкістю 120 FPS).
   - Якщо витримка досягла ліміту `t_max_motion`, подальший запит експозиції передається на аналоговий підсилювач матриці `G_ana` (в межах від `1.0` до `16.0`).
   - Якщо аналогове підсилення також досягає стелі `G_ana_max`, контур задіює цифровий помножувач `G_dig` (до `4.0`).
4. **Квантування частоти мерехтіння (Anti-Flicker)**:
   - Якщо увімкнено режим придушення мерехтіння (50 Гц для європейської електромережі або 60 Гц для американської), час витримки примусово округлюється до найближчого цілого числа напівперіодів мережі:
     ```
     T_flicker = 1 / (2 · f_grid)    [10 000 мкс для 50 Гц або 8 333 мкс для 60 Гц]
     ```

## Апаратне відображення параметрів на регістри CMOS-сенсора

У промислових камерах (наприклад, на базі сенсорів Sony Pregius або OmniVision) витримка та підсилення не задаються безпосередньо в секундах чи децибелах, а переводяться в цілочисельні значення регістрів таймінгу рядків (Row Time) та коди підсилювача:
- **Регістр тривалості інтеграції (Coarse Shutter Width — `SHS`)**: задається у кількості рядкових періодів `T_line`:
  ```
  SHS_lines = t_exp / T_line    [кількість рядків експонування]
  ```
  Якщо кадр має повний період кадрової розгортки `VMAX` рядків (включаючи кадровий гасячий інтервал Vertical Blanking), фактичний час витримки обмежується умовою `SHS ≤ VMAX - 4`.
- **Аналоговий код підсилення (Analog Gain Code)**: для багатьох сенсорів залежність коду `Gain_Reg` від фізичного коефіцієнта `G_ana` є дробово-раціональною, наприклад:
  ```
  Gain_Reg = 2048 - (2048 / G_ana)    [для сенсорів Sony IMX]
  ```
  або логарифмічною: `Gain_dB = 20 · log₁₀(G_ana)`.

## Програмна реалізація контролера AEC/AGC

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#define AEC_GRID_COLS 8
#define AEC_GRID_ROWS 8

typedef enum {
    AEC_FLICKER_OFF = 0,
    AEC_FLICKER_50HZ = 50,
    AEC_FLICKER_60HZ = 60
} aec_flicker_mode_t;

typedef struct {
    /* Конфігураційні ліміти */
    uint32_t min_exposure_us;
    uint32_t max_exposure_us;
    uint32_t max_motion_exposure_us; /* Ліміт витримки для запобігання Motion Blur */
    float min_analog_gain;
    float max_analog_gain;
    float min_digital_gain;
    float max_digital_gain;

    /* Параметри регулятора */
    float target_luma;               /* Цільова середня яскравість (зазвичай 118.0) */
    float deadband_luma;             /* Зона нечутливості (зазвичай 3.0) */
    float kp;                        /* Пропорційний коефіцієнт демпфування (0.2 - 0.5) */
    aec_flicker_mode_t flicker_mode; /* Режим захисту від мерехтіння */

    /* Поточний стан сенсора */
    uint32_t current_exposure_us;
    float current_analog_gain;
    float current_digital_gain;
} aec_controller_t;

/* Вагова матриця 8x8 (Center-Weighted Gaussian Mask) */
static const uint8_t g_center_weights[AEC_GRID_ROWS][AEC_GRID_COLS] = {
    { 1,  1,  2,  2,  2,  2,  1,  1 },
    { 1,  2,  4,  4,  4,  4,  2,  1 },
    { 2,  4,  8, 12, 12,  8,  4,  2 },
    { 2,  4, 12, 16, 16, 12,  4,  2 },
    { 2,  4, 12, 16, 16, 12,  4,  2 },
    { 2,  4,  8, 12, 12,  8,  4,  2 },
    { 1,  2,  4,  4,  4,  4,  2,  1 },
    { 1,  1,  2,  2,  2,  2,  1,  1 }
};

void aec_init(aec_controller_t *ctrl) {
    if (!ctrl) return;

    ctrl->min_exposure_us = 50;           /* 1/20000 с */
    ctrl->max_exposure_us = 33333;        /* 1/30 с */
    ctrl->max_motion_exposure_us = 8333;  /* 1/120 с */
    ctrl->min_analog_gain = 1.0f;
    ctrl->max_analog_gain = 16.0f;
    ctrl->min_digital_gain = 1.0f;
    ctrl->max_digital_gain = 4.0f;

    ctrl->target_luma = 118.0f;           /* 18% сіра карта при гаммі 2.2 */
    ctrl->deadband_luma = 3.0f;
    ctrl->kp = 0.35f;
    ctrl->flicker_mode = AEC_FLICKER_50HZ;

    ctrl->current_exposure_us = 10000;
    ctrl->current_analog_gain = 1.0f;
    ctrl->current_digital_gain = 1.0f;
}

float aec_compute_weighted_luma(const uint8_t grid_luma[AEC_GRID_ROWS][AEC_GRID_COLS]) {
    uint32_t weighted_sum = 0;
    uint32_t total_weight = 0;

    for (int r = 0; r < AEC_GRID_ROWS; ++r) {
        for (int c = 0; c < AEC_GRID_COLS; ++c) {
            uint32_t w = g_center_weights[r][c];
            weighted_sum += (uint32_t)grid_luma[r][c] * w;
            total_weight += w;
        }
    }

    if (total_weight == 0) return 1.0f;
    return (float)weighted_sum / (float)total_weight;
}

static uint32_t aec_apply_antiflicker(uint32_t exp_us, aec_flicker_mode_t mode, uint32_t min_exp, uint32_t max_exp) {
    if (mode == AEC_FLICKER_OFF) return exp_us;

    uint32_t step_us = (mode == AEC_FLICKER_50HZ) ? 10000 : 8333;

    if (exp_us < step_us) {
        return exp_us; /* При надкоротких витримках Anti-Flicker не застосовується */
    }

    /* Квантування до найближчого кроку періоду мережі */
    uint32_t steps = (exp_us + (step_us / 2)) / step_us;
    if (steps == 0) steps = 1;

    uint32_t quantized = steps * step_us;
    if (quantized < min_exp) quantized = min_exp;
    if (quantized > max_exp) quantized = max_exp;

    return quantized;
}

bool aec_update(aec_controller_t *ctrl, float measured_luma) {
    if (!ctrl) return false;

    if (measured_luma < 1.0f) measured_luma = 1.0f;

    float error = ctrl->target_luma - measured_luma;

    /* Перевірка зони нечутливості (Deadband) */
    if (fabsf(error) <= ctrl->deadband_luma) {
        return false; /* Параметри стабільні, коригування не потрібне */
    }

    /* Логарифмічний розрахунок зсуву експозиційного числа EV */
    float luma_ratio = ctrl->target_luma / measured_luma;
    float delta_ev = ctrl->kp * (logf(luma_ratio) / 0.693147f); /* log2(x) = ln(x)/ln(2) */

    /* Обмеження максимальної швидкості зміни за один кадр (максимум +-1.5 EV) */
    if (delta_ev > 1.5f) delta_ev = 1.5f;
    if (delta_ev < -1.5f) delta_ev = -1.5f;

    float exposure_scale = exp2f(delta_ev);

    /* Сумарний фотометричний ресурс */
    float current_total = (float)ctrl->current_exposure_us *
                          ctrl->current_analog_gain *
                          ctrl->current_digital_gain;

    float desired_total = current_total * exposure_scale;

    /* Пріоритетний розподіл: 1) Shutter -> 2) Analog Gain -> 3) Digital Gain */
    uint32_t target_exp = ctrl->min_exposure_us;
    float target_ana_gain = ctrl->min_analog_gain;
    float target_dig_gain = ctrl->min_digital_gain;

    float budget = desired_total;

    /* Фаза 1: Керування витримкою при одиничному підсиленні */
    float max_shutter_budget = (float)ctrl->max_motion_exposure_us * ctrl->min_analog_gain * ctrl->min_digital_gain;

    if (budget <= max_shutter_budget) {
        target_exp = (uint32_t)(budget / (ctrl->min_analog_gain * ctrl->min_digital_gain));
        target_ana_gain = ctrl->min_analog_gain;
        target_dig_gain = ctrl->min_digital_gain;
    } else {
        /* Витримка досягла порогу захисту від змазу */
        target_exp = ctrl->max_motion_exposure_us;
        budget /= (float)target_exp;

        /* Фаза 2: Нарощування аналогового підсилення */
        if (budget <= ctrl->max_analog_gain) {
            target_ana_gain = budget;
            target_dig_gain = ctrl->min_digital_gain;
        } else {
            /* Аналогове підсилення досягло максимуму */
            target_ana_gain = ctrl->max_analog_gain;
            budget /= target_ana_gain;

            /* Фаза 3: Цифрове підсилення */
            if (budget <= ctrl->max_digital_gain) {
                target_dig_gain = budget;
            } else {
                /* Екстремальна темрява: подовження витримки понад ліміт руху */
                target_dig_gain = ctrl->max_digital_gain;
                float remaining = budget / ctrl->max_digital_gain;
                uint32_t extended_exp = (uint32_t)((float)target_exp * remaining);
                if (extended_exp > ctrl->max_exposure_us) extended_exp = ctrl->max_exposure_us;
                target_exp = extended_exp;
            }
        }
    }

    /* Застосування фільтра Anti-Flicker */
    target_exp = aec_apply_antiflicker(target_exp, ctrl->flicker_mode,
                                       ctrl->min_exposure_us, ctrl->max_exposure_us);

    /* Апаратне обмеження меж */
    if (target_exp < ctrl->min_exposure_us) target_exp = ctrl->min_exposure_us;
    if (target_exp > ctrl->max_exposure_us) target_exp = ctrl->max_exposure_us;
    if (target_ana_gain < ctrl->min_analog_gain) target_ana_gain = ctrl->min_analog_gain;
    if (target_ana_gain > ctrl->max_analog_gain) target_ana_gain = ctrl->max_analog_gain;
    if (target_dig_gain < ctrl->min_digital_gain) target_dig_gain = ctrl->min_digital_gain;
    if (target_dig_gain > ctrl->max_digital_gain) target_dig_gain = ctrl->max_digital_gain;

    ctrl->current_exposure_us = target_exp;
    ctrl->current_analog_gain = target_ana_gain;
    ctrl->current_digital_gain = target_dig_gain;

    return true;
}
```
```cpp
#include <cstdint>
#include <cmath>
#include <array>
#include <span>
#include <algorithm>

namespace vision::isp {

enum class AntiFlickerMode : uint32_t {
    Disabled = 0,
    Mains50Hz = 50,
    Mains60Hz = 60
};

struct ExposureLimits {
    uint32_t minExposureUs{50};
    uint32_t maxExposureUs{33333};
    uint32_t maxMotionExposureUs{8333};
    float minAnalogGain{1.0f};
    float maxAnalogGain{16.0f};
    float minDigitalGain{1.0f};
    float maxDigitalGain{4.0f};
};

struct ExposureSettings {
    uint32_t exposureUs{10000};
    float analogGain{1.0f};
    float digitalGain{1.0f};
};

class AutoExposureController {
public:
    static constexpr size_t GridRows = 8;
    static constexpr size_t GridCols = 8;

    explicit AutoExposureController(const ExposureLimits& limits = ExposureLimits{})
        : limits_(limits) {}

    void setTargetLuminance(float target, float deadband = 3.0f) noexcept {
        targetLuma_ = target;
        deadband_ = deadband;
    }

    void setDampingFactor(float kp) noexcept {
        kp_ = std::clamp(kp, 0.05f, 1.0f);
    }

    void setAntiFlicker(AntiFlickerMode mode) noexcept {
        flickerMode_ = mode;
    }

    [[nodiscard]] const ExposureSettings& currentSettings() const noexcept {
        return current_;
    }

    [[nodiscard]] static float computeWeightedLuminance(
        std::span<const uint8_t, GridRows * GridCols> gridData) noexcept {
        
        static constexpr std::array<uint8_t, GridRows * GridCols> CenterWeights = {
            1,  1,  2,  2,  2,  2,  1,  1,
            1,  2,  4,  4,  4,  4,  2,  1,
            2,  4,  8, 12, 12,  8,  4,  2,
            2,  4, 12, 16, 16, 12,  4,  2,
            2,  4, 12, 16, 16, 12,  4,  2,
            2,  4,  8, 12, 12,  8,  4,  2,
            1,  2,  4,  4,  4,  4,  2,  1,
            1,  1,  2,  2,  2,  2,  1,  1
        };

        uint32_t weightedSum = 0;
        uint32_t totalWeight = 0;

        for (size_t i = 0; i < gridData.size(); ++i) {
            uint32_t w = CenterWeights[i];
            weightedSum += static_cast<uint32_t>(gridData[i]) * w;
            totalWeight += w;
        }

        if (totalWeight == 0) return 1.0f;
        return static_cast<float>(weightedSum) / static_cast<float>(totalWeight);
    }

    bool update(float measuredLuma) noexcept {
        measuredLuma = std::max(measuredLuma, 1.0f);
        float error = targetLuma_ - measuredLuma;

        if (std::abs(error) <= deadband_) {
            return false;
        }

        float lumaRatio = targetLuma_ / measuredLuma;
        float deltaEv = kp_ * std::log2(lumaRatio);
        deltaEv = std::clamp(deltaEv, -1.5f, 1.5f);

        float scale = std::exp2(deltaEv);
        float currentTotal = static_cast<float>(current_.exposureUs) *
                             current_.analogGain * current_.digitalGain;
        float desiredTotal = currentTotal * scale;

        allocateParameters(desiredTotal);
        return true;
    }

private:
    void allocateParameters(float desiredTotal) noexcept {
        uint32_t expUs = limits_.minExposureUs;
        float anaGain = limits_.minAnalogGain;
        float digGain = limits_.minDigitalGain;

        float maxShutterBudget = static_cast<float>(limits_.maxMotionExposureUs) *
                                 limits_.minAnalogGain * limits_.minDigitalGain;

        if (desiredTotal <= maxShutterBudget) {
            expUs = static_cast<uint32_t>(desiredTotal / (limits_.minAnalogGain * limits_.minDigitalGain));
        } else {
            expUs = limits_.maxMotionExposureUs;
            float budget = desiredTotal / static_cast<float>(expUs);

            if (budget <= limits_.maxAnalogGain) {
                anaGain = budget;
            } else {
                anaGain = limits_.maxAnalogGain;
                budget /= anaGain;

                if (budget <= limits_.maxDigitalGain) {
                    digGain = budget;
                } else {
                    digGain = limits_.maxDigitalGain;
                    float remaining = budget / digGain;
                    uint32_t extended = static_cast<uint32_t>(static_cast<float>(expUs) * remaining);
                    expUs = std::min(extended, limits_.maxExposureUs);
                }
            }
        }

        expUs = applyAntiFlicker(expUs);

        current_.exposureUs = std::clamp(expUs, limits_.minExposureUs, limits_.maxExposureUs);
        current_.analogGain = std::clamp(anaGain, limits_.minAnalogGain, limits_.maxAnalogGain);
        current_.digitalGain = std::clamp(digGain, limits_.minDigitalGain, limits_.maxDigitalGain);
    }

    [[nodiscard]] uint32_t applyAntiFlicker(uint32_t expUs) const noexcept {
        if (flickerMode_ == AntiFlickerMode::Disabled) return expUs;

        uint32_t stepUs = (flickerMode_ == AntiFlickerMode::Mains50Hz) ? 10000 : 8333;
        if (expUs < stepUs) return expUs;

        uint32_t steps = (expUs + (stepUs / 2)) / stepUs;
        steps = std::max(steps, 1u);

        uint32_t quantized = steps * stepUs;
        return std::clamp(quantized, limits_.minExposureUs, limits_.maxExposureUs);
    }

    ExposureLimits limits_;
    ExposureSettings current_{};
    float targetLuma_{118.0f};
    float deadband_{3.0f};
    float kp_{0.35f};
    AntiFlickerMode flickerMode_{AntiFlickerMode::Mains50Hz};
};

} // namespace vision::isp
```
:::

## Інженерні пастки та тонкощі налаштування

1. **Затримка застосування регістрів (Frame Latency)**: На відміну від софтверних алгоритмів, запис регістрів витримки та підсилення через інтерфейс I2C/SPI вступає в силу лише на початку наступного кадру (`N+1`) або через один кадр (`N+2` через конвеєр тіньових регістрів сенсора). Якщо алгоритм виконує корекцію на кожному кадрі з коефіцієнтом `K_p > 0.5`, виникає хвильова автогенерація (hunting): кадр стає по черзі то занадто світлим, то занадто темним. Правильний підхід — або обмежувати `K_p ≤ 0.35`, або робити паузу на час конвеєрної затримки матриці.
2. **Контрастні сцени з контурним світлом (Backlight Clipping)**: Якщо об'єкт розташований на тлі яскравого вікна або сонця, глобальна середня яскравість змусить контур закрити експозицію, перетворивши цільовий об'єкт на чорний силует. У системах комп'ютерного зору замість загальної маски застосовують експонометрію за виділеними зонами інтересу (ROI Metering), де маска ваг динамічно прив'язується до прямокутника виявленого об'єкта (Bounding Box детектора YOLO або трекера KCF).
3. **Квантовий шум при екстремальному підсиленні**: При перевищенні порогу аналогового підсилення `16x` (ISO 1600+) співвідношення сигнал/шум падає нижче `20 дБ`. Для уникнення деградації оптичного потоку (Optical Flow) контур автоекспозиції повинен узгоджуватися з модулем просторово-часової фільтрації шумів (3D-DNR), динамічно піднімаючи силу згладжування фільтра пропорційно поточному значенню `Gain`.
4. **Архітектури подвійного коефіцієнта перетворення (Dual Conversion Gain — DCG)**: Сучасні промислові BSI-сенсори мають два апаратні режими вузла плаваючого дифузійного переходу: LCG (Low Conversion Gain, велика ємність вузла `C_fd` для високого насичення вдень) та HCG (High Conversion Gain, мала ємність для мінімізації шуму зчитування вночі). Драйвер камери повинен автоматично перемикати біт `DCG_ENABLE` в момент, коли контур автопідсилення перетинає поріг `Gain ≥ 4.0x`, що знижує рівень шуму зчитування `σ_read` з `2.5 e⁻` до `0.8 e⁻` без погіршення витримки.
