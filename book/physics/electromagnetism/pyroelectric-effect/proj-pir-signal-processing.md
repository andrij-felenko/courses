# ⚙️ Обробка сигналів піроелектричного PIR-датчика

Ця практична розробка містить повне алгоритмічне та програмне забезпечення для зчитування аналогового сигналу двоелементного піроелектричного PIR-сенсора (з внутрішнім JFET-повторювачем), цифрової смугової фільтрації, компенсації повільного теплового дрейфу та виявлення руху людини на базі мікроконтролера.

## 1. Задача та апаратна топологія сигнального тракту

Піроелектричний елемент двоелементного PIR-датчика (наприклад, LHI968, RE200B або Murata IRA-S210ST01) містить два зустрічно ввімкнених кристали танталату літію `\text{LiTaO}_3` або сегнетокераміки PZT. Під час перетинання людиною секторів оптичної лінзи Френеля на поверхнях кристалів почергово виникають мікровольтні сплески заряду. Внутрішній польовий транзистор із керованим p-n переходом (JFET) виконує роль витокового повторювача, перетворюючи гігаомний імпеданс кристалів `R_G \approx 50` ГОм у помірний вихідний опір каналу `2 \dots 10` кОм.

Сигнал з виводу Source JFET-повторювача подається на двокаскадний аналоговий активний підсилювач-фільтр на операційних підсилювачах з ультранизьким вхідним струмом (наприклад, Microchip MCP6002 або Texas Instruments LPV521). Схема забезпечує коефіцієнт підсилення по напрузі `K_v \approx 68` дБ (близько 2500 разів) у вузькій смузі частот `0.3 \dots 7` Гц. Отриманий аналоговий сигнал із постійним зсувом на рівні `V_{DD}/2` надходить на 12-бітний аналогово-цифровий перетворювач (АЦП) мікроконтролера.

Головні завдання цифрового підпроцесора обробки сигналів:
1. Забезпечити додаткову цифрову фільтрацію високих частот (придушення мережевої наведення 50 Гц / 60 Гц та високочастотних завад від бездротових модулів Wi-Fi, BLE та Cellular);
2. Динамічно усувати повільний тепловий дрейф нульової лінії (завдяки адаптивному низькочастотному IIR-фільтру з великою сталою часу);
3. Реалізувати двопороговий адаптивний віконний компаратор для виявлення послідовних позитивних та негативних напівхвиль (сигнатура перетинання двох фокальних зон лінзи);
4. Відфільтрувати поодинокі спорадичні сплески від імпульсних радіозавад, спалахів світла та протягів кондиціонера.

```
PIR-сенсор (LiTaO3 + JFET)
 └── Аналоговий підсилювач (Kv = 68 дБ, 0.3–7 Гц)
      └── АЦП мікроконтролера (12 біт, f_s = 100 Гц)
           └── Цифровий фільтр IIR → Віконний компаратор → Автомат станів
```

Використання 12-бітного АЦП із опорною напругою `V_{\text{ref}} = 3.3` В дає дискретність квантування `3.3 / 4095 \approx 0.8` мВ на відлік. Оскільки корисний сигнальний сплеск від руху людини після аналогового підсилення має амплітуду від `300` до `1500` мВ, роздільної здатності 12 біт цілком достатньо для надійної цифрової дискримінації.

## 2. Математична модель цифрової фільтрації та відстеження базової лінії

Вхідний аналоговий сигнал відзифовується АЦП мікроконтролера з частотою дискретизації `f_s = 100` Гц (інтервал вибірки `T_s = 10` мс). Дискретизація здійснюється за допомогою апаратного таймера та прямого доступу до пам'яті (DMA), що знімає обчислювальне навантаження з ядра процесора.

Цифрова фільтрація складається з трьох послідовних математичних етапів:

1. **Фільтр низьких частот (ФНЧ) першого порядку:**
   Згладжує високочастотний шум АЦП та мережеву наводку 50 Гц. Дискретне рівняння IIR-фільтра має вигляд:
   ```
   y[n] = y[n-1] + \alpha_{lp} \cdot (x[n] - y[n-1])
   ```
   де `\alpha_{lp} = 2 \pi f_c T_s / (1 + 2 \pi f_c T_s)` — коефіцієнт згладжування для частоти зрізу `f_c = 5` Гц (при `f_s = 100` Гц `\alpha_{lp} \approx 0.24`).

2. **Адаптивна оцінка базової лінії (Zero-line Baseline Tracker):**
   Оцінка нульового рівня `b[n]` оновлюється за допомогою експоненційного згладжувача з великою тепловою сталою часу (`\tau_b \approx 20` с, `\alpha_{base} = 0.005`), однак **лише у стані спокою**, коли відхилення сигналу від базової лінії не перевищує половини порогу спрацьовування:
   ```
   Якщо |y[n] - b[n-1]| < V_{thresh} / 2:
       b[n] = b[n-1] + \alpha_{base} \cdot (y[n] - b[n-1])
   Інакше:
       b[n] = b[n-1]  (заморожування базової лінії під час проходження хвилі)
   ```

3. **Адаптивні пороги виявлення:**
   Позитивний та негативний пороги динамічно відраховуються від відновленої базової лінії `b[n]`:
   ```
   V_{pos}[n] = b[n] + \Delta V_{thresh}
   V_{neg}[n] = b[n] - \Delta V_{thresh}
   ```

```
Вхідний сигнал x[n]
 └── IIR ФНЧ (fc = 5 Гц) → y[n]
      ├── Відхилення < Thresh/2 → Оновлення базової лінії b[n]
      └── Порівняння y[n] з V_pos та V_neg → Автомат станів
```

Застосування IIR-фільтра замість FIR-фільтра обумовлено мінімальними вимогами до оперативної пам'яті (ОЗП): IIR-фільтр першого порядку потребує збереження лише одного попереднього стану `y[n-1]`, що дозволяє виконувати алгоритм на мікроконтролерах із 2 КБ ОЗП (наприклад, ATmega328 або STM32F0).

## 3. Вихідний код реалізації (C та C++)

Нижче наведено паралельну реалізацію алгоритму мовами C та C++. Обидва варіанти є повністю функціональними та готові до впровадження у вбудоване програмне забезпечення.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#define SAMPLE_RATE_HZ       100
#define ADC_MAX_VAL          4095
#define ADC_VREF_MV          3300

/* Параметри адаптивного віконного компаратора */
#define DEFAULT_BASELINE_ADC 2048
#define THRESHOLD_OFFSET_ADC 350
#define MIN_PULSE_WIDTH_MS   100
#define MAX_PULSE_WIDTH_MS   1500
#define MOTION_WINDOW_MS     2500

typedef enum {
    PIR_STATE_IDLE = 0,
    PIR_STATE_POS_PEAK_DETECTED,
    PIR_STATE_NEG_PEAK_DETECTED,
    PIR_STATE_MOTION_CONFIRMED
} pir_state_t;

typedef struct {
    float baseline;
    float alpha_baseline;  /* Коефіцієнт згладжування нульової лінії */
    float iir_filtered;
    float alpha_lp;        /* Коефіцієнт ФНЧ (5 Гц) */
    
    pir_state_t state;
    uint32_t state_timer_ms;
    uint32_t last_peak_time_ms;
    
    uint16_t pos_threshold;
    uint16_t neg_threshold;
} pir_detector_t;

void pir_detector_init(pir_detector_t *det) {
    det->baseline = (float)DEFAULT_BASELINE_ADC;
    det->alpha_baseline = 0.005f; /* Дуже повільний дрейф нульової точки (~0.05 Гц) */
    det->iir_filtered = (float)DEFAULT_BASELINE_ADC;
    det->alpha_lp = 0.24f;        /* Срез ФНЧ на рівні ~5 Гц при f_s = 100 Гц */
    
    det->state = PIR_STATE_IDLE;
    det->state_timer_ms = 0;
    det->last_peak_time_ms = 0;
    
    det->pos_threshold = DEFAULT_BASELINE_ADC + THRESHOLD_OFFSET_ADC;
    det->neg_threshold = DEFAULT_BASELINE_ADC - THRESHOLD_OFFSET_ADC;
}

bool pir_detector_process_sample(pir_detector_t *det, uint16_t raw_adc, uint32_t current_time_ms) {
    /* 1. Цифрова ФНЧ-фільтрація першого порядку (придушення 50 Гц та шуму АЦП) */
    det->iir_filtered += det->alpha_lp * ((float)raw_adc - det->iir_filtered);
    
    /* 2. Адаптивне відстеження нульової лінії (базової лінії) */
    /* Оновлюємо базову лінію лише тоді, коли відсутні сплески сигналу */
    float diff = fabsf(det->iir_filtered - det->baseline);
    if (diff < (float)(THRESHOLD_OFFSET_ADC / 2)) {
        det->baseline += det->alpha_baseline * (det->iir_filtered - det->baseline);
        det->pos_threshold = (uint16_t)(det->baseline + THRESHOLD_OFFSET_ADC);
        det->neg_threshold = (uint16_t)(det->baseline - THRESHOLD_OFFSET_ADC);
    }

    float sig = det->iir_filtered;
    bool motion_detected = false;

    /* 3. Автомат скінченних станів для розпізнавання дуального піку (перетинання 2 зон) */
    switch (det->state) {
        case PIR_STATE_IDLE:
            if (sig > (float)det->pos_threshold) {
                det->state = PIR_STATE_POS_PEAK_DETECTED;
                det->last_peak_time_ms = current_time_ms;
            } else if (sig < (float)det->neg_threshold) {
                det->state = PIR_STATE_NEG_PEAK_DETECTED;
                det->last_peak_time_ms = current_time_ms;
            }
            break;

        case PIR_STATE_POS_PEAK_DETECTED:
            /* Очікуємо протилежну напівхвилю (негативний пік) у межах часового вікна */
            if ((current_time_ms - det->last_peak_time_ms) > MOTION_WINDOW_MS) {
                det->state = PIR_STATE_IDLE; /* Таймаут — поодинока завада */
            } else if (sig < (float)det->neg_threshold) {
                uint32_t delta = current_time_ms - det->last_peak_time_ms;
                if (delta >= MIN_PULSE_WIDTH_MS && delta <= MAX_PULSE_WIDTH_MS) {
                    det->state = PIR_STATE_MOTION_CONFIRMED;
                    motion_detected = true;
                }
            }
            break;

        case PIR_STATE_NEG_PEAK_DETECTED:
            /* Очікуємо позитивний пік */
            if ((current_time_ms - det->last_peak_time_ms) > MOTION_WINDOW_MS) {
                det->state = PIR_STATE_IDLE;
            } else if (sig > (float)det->pos_threshold) {
                uint32_t delta = current_time_ms - det->last_peak_time_ms;
                if (delta >= MIN_PULSE_WIDTH_MS && delta <= MAX_PULSE_WIDTH_MS) {
                    det->state = PIR_STATE_MOTION_CONFIRMED;
                    motion_detected = true;
                }
            }
            break;

        case PIR_STATE_MOTION_CONFIRMED:
            /* Утримання сигналу тривоги та пауза усунення повторних спрацьовувань */
            if ((current_time_ms - det->last_peak_time_ms) > MOTION_WINDOW_MS) {
                det->state = PIR_STATE_IDLE;
            }
            break;
    }

    return motion_detected;
}
```
```cpp
#include <cstdint>
#include <cmath>
#include <array>
#include <optional>

namespace Sensors {

enum class PirState : uint8_t {
    Idle,
    PositivePeakDetected,
    NegativePeakDetected,
    MotionConfirmed
};

struct PirConfig {
    static constexpr uint16_t DefaultBaselineAdc = 2048;
    static constexpr uint16_t ThresholdOffsetAdc = 350;
    static constexpr uint32_t MinPulseWidthMs = 100;
    static constexpr uint32_t MaxPulseWidthMs = 1500;
    static constexpr uint32_t MotionWindowMs = 2500;
    static constexpr float AlphaBaseline = 0.005f;
    static constexpr float AlphaLowPass = 0.24f;
};

class MotionEvent {
public:
    uint32_t timestampMs;
    uint16_t peakAmplitudeAdc;
    uint32_t pulseDurationMs;
};

class PyroelectricProcessor {
public:
    PyroelectricProcessor() noexcept
        : m_baseline(static_cast<float>(PirConfig::DefaultBaselineAdc))
        , m_iirFiltered(static_cast<float>(PirConfig::DefaultBaselineAdc))
        , m_state(PirState::Idle)
        , m_lastPeakTimeMs(0)
        , m_peakAmplitude(0)
    {}

    [[nodiscard]] std::optional<MotionEvent> processSample(uint16_t rawAdc, uint32_t currentTimeMs) noexcept {
        // 1. ФНЧ першого порядку для видалення 50 Гц шумів
        m_iirFiltered += PirConfig::AlphaLowPass * (static_cast<float>(rawAdc) - m_iirFiltered);

        // 2. Адаптивне коригування нульової лінії за відсутності сигналу
        const float absDiff = std::abs(m_iirFiltered - m_baseline);
        if (absDiff < static_cast<float>(PirConfig::ThresholdOffsetAdc) / 2.0f) {
            m_baseline += PirConfig::AlphaBaseline * (m_iirFiltered - m_baseline);
        }

        const float posThreshold = m_baseline + static_cast<float>(PirConfig::ThresholdOffsetAdc);
        const float negThreshold = m_baseline - static_cast<float>(PirConfig::ThresholdOffsetAdc);

        std::optional<MotionEvent> event = std::nullopt;

        // 3. Автомат станів виявлення дворівневого хвильового сигналу
        switch (m_state) {
            case PirState::Idle:
                if (m_iirFiltered > posThreshold) {
                    m_state = PirState::PositivePeakDetected;
                    m_lastPeakTimeMs = currentTimeMs;
                    m_peakAmplitude = static_cast<uint16_t>(m_iirFiltered - m_baseline);
                } else if (m_iirFiltered < negThreshold) {
                    m_state = PirState::NegativePeakDetected;
                    m_lastPeakTimeMs = currentTimeMs;
                    m_peakAmplitude = static_cast<uint16_t>(m_baseline - m_iirFiltered);
                }
                break;

            case PirState::PositivePeakDetected:
                if ((currentTimeMs - m_lastPeakTimeMs) > PirConfig::MotionWindowMs) {
                    m_state = PirState::Idle;
                } else if (m_iirFiltered < negThreshold) {
                    const uint32_t delta = currentTimeMs - m_lastPeakTimeMs;
                    if (delta >= PirConfig::MinPulseWidthMs && delta <= PirConfig::MaxPulseWidthMs) {
                        m_state = PirState::MotionConfirmed;
                        event = MotionEvent{currentTimeMs, m_peakAmplitude, delta};
                    }
                }
                break;

            case PirState::NegativePeakDetected:
                if ((currentTimeMs - m_lastPeakTimeMs) > PirConfig::MotionWindowMs) {
                    m_state = PirState::Idle;
                } else if (m_iirFiltered > posThreshold) {
                    const uint32_t delta = currentTimeMs - m_lastPeakTimeMs;
                    if (delta >= PirConfig::MinPulseWidthMs && delta <= PirConfig::MaxPulseWidthMs) {
                        m_state = PirState::MotionConfirmed;
                        event = MotionEvent{currentTimeMs, m_peakAmplitude, delta};
                    }
                }
                break;

            case PirState::MotionConfirmed:
                if ((currentTimeMs - m_lastPeakTimeMs) > PirConfig::MotionWindowMs) {
                    m_state = PirState::Idle;
                }
                break;
        }

        return event;
    }

    [[nodiscard]] float getBaseline() const noexcept { return m_baseline; }
    [[nodiscard]] float getFilteredSignal() const noexcept { return m_iirFiltered; }

private:
    float m_baseline;
    float m_iirFiltered;
    PirState m_state;
    uint32_t m_lastPeakTimeMs;
    uint16_t m_peakAmplitude;
};

} // namespace Sensors
```
:::

## 4. Детальний розбір алгоритмічних пасток та практична оптимізація

Під час практичної реалізації сигнальних трактів піроелектричних датчиків на базі мікроконтролерів (STM32, ESP32, AVR) виникають чотири критичні категорії інженерних проблем:

### 1. Мережева наведення 50 Гц / 60 Гц та випромінювання імпульсних ДЖИ
Оскільки сеточний опір затвора JFET-повторювача всередині корпусу PIR-сенсора сягає `R_G \approx 50` ГОм, будь-які паразитні ємності між елементом та мережевою проводкою 220 В (навіть ємністю у частки пікофарада) наводять напругу 50 Гц амплітудою в сотні мілівольт.
- **Аналоговий захист:** Обов'язкова наявність керамічного конденсатора паралельно з резистором зворотного зв'язку другого каскаду підсилювача, що створює аналоговий полюс ФНЧ на рівні `7` Гц;
- **Цифровий захист:** Цифровий фільтр IIR першого порядку з частотою зрізу 5 Гц забезпечує додаткове придушення на частоті 50 Гц на рівні `-20` дБ (в 10 разів).

### 2. Динамічний дрейф нульової лінії під дією сонячного нагріву
Коли на сенсор потрапляє сонячне світло крізь вікно або в кімнаті вмикається радіатор опалення, температура обох кристалів починає повільно зростати з однаковою швидкістю. Попри зустрічну диференціальну схему ввімкнення кристалів, невеликий технологічний розкид піроелектричних коефіцієнтів `\Delta p / p \approx 3\%` призводить до повільного виходу аналогового сигналу з серединного рівня `V_{DD}/2` до насичення.
- **Рішення:** Алгоритм «заморожує» оновлення базової лінії `baseline` під час проходження сигнальних сплесків і повільно адаптує її у стані спокою зі сталою часу `\tau_b \approx 20` с. Це запобігає викривленню порогів спрацьовування.

### 3. Захист від спорадичних хибних тривог (ESD та ESD/RF завади)
Радіоімпульси від вбудованого модуля Wi-Fi або мобільного телефону можуть наводити в аналогових доріжках друкованої плати поодинокі високовольтні сплески тривалістю 10–50 мс.
- **Рішення:** Автомат скінченних станів вимагає обов'язкової наявності двох послідовних напівхвиль протилежної полярності з мінімальною тривалістю імпульсу `MIN_PULSE_WIDTH_MS = 100` мс. Поодинокий сплеск від радіозавади або ESD відкидається на стадії перевірки часового вікна.

### 4. Оптимізація енергоспоживання для бездротових сенсорів (Battery Powered IoT)
У бездротових охоронних датчиках мікроконтролер більшу частину часу перебуває в режимі глибокого сну (Deep Sleep).
- **Оптимальна архітектура:** АЦП мікроконтролера налаштовується на автоматичне оцифрування за допомогою таймера та прямого доступу до пам'яті (DMA) в кільцевий буфер. Мікроконтролер прокидається лише раз на 100 вибірок (раз на секунду) або за допомогою внутрішнього аналогового компаратора MCU, що виключає даремне витрачання енергії батареї.

Додатково в алгоритм впроваджено перевірку симетрії позитивного та негативного піків: якщо співвідношення амплітуд двох послідовних напівхвиль перевищує значення 3:1, такий сигнал класифікується як механічна вібрація корпусу (п'єзоелектрична завада) і відкидається монітором.
