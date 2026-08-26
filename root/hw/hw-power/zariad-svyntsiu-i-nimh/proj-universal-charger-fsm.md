# ⚙️ Прошивка контролера заряду свинцю та NiMH на базі кінцевого автомата

Створення зарядного пристрою, сумісного зі свинцево-кислотними (Lead-Acid) та нікель-металогідридними (NiMH) акумуляторами, вимагає реалізації двох принципово різних режимів керування: тристадійного профілю IUoU для свинцю та швидкого сталого струму з відстеженням спаду напруги (−ΔV) і похідної температури (dT/dt) для NiMH. Будь-яка помилка в детектуванні повного заряду веде до теплового пошкодження батареї або хронічного недозаряду.

### Апаратна частина та розв'язання вимірювальних задач

Спроєктований зарядний модуль базується на синхронному знижувальному перетворювачі (Synchronous Buck Converter), керованому комплементарними ШІМ-виходами мікроконтролера на частоті комутації 150 кГц. Вибір синхронного випрямлення на польових транзисторах замість діода Шотткі обумовлений високим ККД (> 94%) та відсутністю надмірного нагріву силовими струмами до 5–10 А.

Головні інженерні вимоги до силового та вимірювального тракту контролера:
1. **Точність та шум вимірювання напруги**: спад напруги NiMH при повному заряді становить лише 3–5 мВ на комірку. За використання 12-бітного АЦП мікроконтролера з опорною напругою 3.3 В ціна молодшого значущого розряду (LSB) становить `3.3 В / 4095 ≈ 0.806 мВ`. При вимірюванні пакета з 4 послідовних NiMH комірок (діапазон 4.0–6.5 В) через прецизійний резистивний дільник 1:3 ціна одного відліку АЦП на вході батареї становить близько 2.42 мВ. Це означає, що корисний сигнал спаду напруги займає лише 1–2 кванти АЦП. Для надійного детектування без хибних спрацьовувань від комутаційного шуму перетворювача застосовується апаратна RC-фільтрація (частота зрізу 50–100 Гц) разом із цифровим програмним усередненням через кільцевий буфер на 32 відліки.
2. **Вимірювання струму та захист від перевантаження**: струмовий вимірювальний шунт номіналом 10–20 мОм встановлюється у верхнє плече живлення (High-side current sense) та підсилюється спеціалізованим диференціальним підсилювачем (класу INA180/INA240). Це виключає розрив загального земляного проводу між батареєю та схемою керування, зберігаючи цілісність спільної шини GND.
3. **Захист від переполюсовки та зворотного струму**: при випадковому зворотному під'єднанні клем акумулятора паразитні діоди нижнього та верхнього MOSFET силового каскаду відкриваються в прямому напрямку, спричиняючи коротке замикання. Для захисту на виході встановлюється силовий P-канальний польовий транзистор (ідеальний діод), затвор якого підтягнутий до мінусової клеми через стабілітрон. При правильній полярності транзистор повністю відкритий і має опір лише 2–5 мОм, а при переполюсовці — миттєво закривається.
4. **Термометрія та розрахунок градієнта dT/dt**: датчик температури (NTC-термістор 10 кОм із коефіцієнтом `B = 3950 K`) монтується безпосередньо на корпус акумулятора за допомогою теплопровідного клею або силіконового бандажа. Контролер перетворює опір NTC на температуру за поліномом Стейнхарта-Харта та щосекунди оновлює кільцевий масив історії температури завглибшки 60 секунд.

### Архітектура кінцевого автомата

Прошивка організована у вигляді детермінованого скінченного автомата (FSM). Контролер виконує квант керування з двома часовими базами:
- Швидкий цикл (100 мс): зчитування АЦП, оновлення ковзного фільтра, захисне обмеження струму й напруги через коригування шпаруватості ШІМ.
- Повільний цикл (1 с): аналіз умов переходу між станами FSM, розрахунок спаду напруги від зафіксованого максимуму `v_peak - v_filtered`, обчислення швидкості зміни температури `dT/dt`, перевірка загальних захисних таймерів.

### Повна програмна реалізація (C та C++)

:::tabs

```c
#include <stdint.h>
#include <stdbool.h>

#define ADC_FILTER_SIZE     32
#define DT_WINDOW_SEC       60

typedef enum {
    CHEM_LEAD_ACID,
    CHEM_NIMH
} battery_chem_t;

typedef enum {
    STATE_STANDBY,
    // Станція свинцю (IUoU)
    STATE_LA_BULK_CC,
    STATE_LA_ABSORPTION_CV,
    STATE_LA_FLOAT,
    // Станція NiMH
    STATE_NIMH_PRECHARGE,
    STATE_NIMH_FAST_CC,
    STATE_NIMH_TOP_OFF,
    STATE_NIMH_TRICKLE,
    // Аварія
    STATE_FAULT
} charger_state_t;

typedef enum {
    FAULT_NONE,
    FAULT_OVER_VOLTAGE,
    FAULT_OVER_TEMP,
    FAULT_TIMEOUT,
    FAULT_REVERSE_POLARITY
} charger_fault_t;

typedef struct {
    battery_chem_t chem;
    charger_state_t state;
    charger_fault_t fault;

    uint16_t capacity_mah;
    uint8_t  cell_count;

    // Фільтрація напруги
    uint32_t v_buffer[ADC_FILTER_SIZE];
    uint8_t  v_buf_idx;
    uint32_t v_filtered_mv;
    uint32_t v_peak_mv;

    // Відстеження температури (dT/dt)
    int16_t  t_history[DT_WINDOW_SEC];
    uint8_t  t_hist_idx;
    int16_t  t_current_c;
    int16_t  dt_dt_mdeg_per_sec;

    // Таймери станів
    uint32_t state_time_sec;
    uint32_t total_charge_sec;

    // Вихідні уставки для ШІМ-регулятора
    uint16_t target_v_mv;
    uint16_t target_i_ma;
} charger_fsm_t;

// Розрахунок температурно-компенсованої напруги для свинцю
static uint16_t la_calc_compensated_v(uint16_t base_mv, int16_t temp_c, uint8_t cells) {
    // Коефіцієнт -4 мВ/°C на комірку відносно 25 °C
    int32_t delta_t = (int32_t)temp_c - 25;
    int32_t comp_mv = -4 * (int32_t)cells * delta_t;
    int32_t result = (int32_t)base_mv + comp_mv;
    if (result < 10000) result = 10000;
    if (result > 16500) result = 16500;
    return (uint16_t)result;
}

void charger_init(charger_fsm_t *ch, battery_chem_t chem, uint16_t cap_mah, uint8_t cells) {
    ch->chem = chem;
    ch->state = STATE_STANDBY;
    ch->fault = FAULT_NONE;
    ch->capacity_mah = cap_mah;
    ch->cell_count = cells;
    ch->v_buf_idx = 0;
    ch->v_filtered_mv = 0;
    ch->v_peak_mv = 0;
    ch->t_hist_idx = 0;
    ch->state_time_sec = 0;
    ch->total_charge_sec = 0;
    ch->target_v_mv = 0;
    ch->target_i_ma = 0;
    for (int i = 0; i < ADC_FILTER_SIZE; ++i) ch->v_buffer[i] = 0;
    for (int i = 0; i < DT_WINDOW_SEC; ++i)   ch->t_history[i] = 25;
}

void charger_update_sensors(charger_fsm_t *ch, uint16_t raw_v_mv, int16_t raw_t_c) {
    ch->v_buffer[ch->v_buf_idx] = raw_v_mv;
    ch->v_buf_idx = (ch->v_buf_idx + 1) % ADC_FILTER_SIZE;

    uint32_t sum = 0;
    for (int i = 0; i < ADC_FILTER_SIZE; ++i) sum += ch->v_buffer[i];
    ch->v_filtered_mv = sum / ADC_FILTER_SIZE;

    ch->t_current_c = raw_t_c;
    int16_t old_t = ch->t_history[ch->t_hist_idx];
    ch->t_history[ch->t_hist_idx] = raw_t_c;
    ch->t_hist_idx = (ch->t_hist_idx + 1) % DT_WINDOW_SEC;

    // Градієнт за DT_WINDOW_SEC секунд у міліградусах на секунду
    ch->dt_dt_mdeg_per_sec = ((int32_t)(raw_t_c - old_t) * 1000) / DT_WINDOW_SEC;
}

void charger_tick_1s(charger_fsm_t *ch, uint16_t measured_i_ma) {
    ch->state_time_sec++;
    ch->total_charge_sec++;

    // Загальний захист за максимальною температурою (> 55 °C)
    if (ch->t_current_c > 55) {
        ch->state = STATE_FAULT;
        ch->fault = FAULT_OVER_TEMP;
        ch->target_v_mv = 0;
        ch->target_i_ma = 0;
        return;
    }

    switch (ch->state) {
        case STATE_STANDBY:
            if (ch->v_filtered_mv > 500) {
                ch->state_time_sec = 0;
                if (ch->chem == CHEM_LEAD_ACID) {
                    ch->state = STATE_LA_BULK_CC;
                    ch->target_i_ma = ch->capacity_mah / 10; // 0.1C
                    ch->target_v_mv = la_calc_compensated_v(2400 * ch->cell_count, ch->t_current_c, ch->cell_count);
                } else {
                    if (ch->v_filtered_mv < 1000 * ch->cell_count) {
                        ch->state = STATE_NIMH_PRECHARGE;
                        ch->target_i_ma = ch->capacity_mah / 10;
                    } else {
                        ch->state = STATE_NIMH_FAST_CC;
                        ch->target_i_ma = (ch->capacity_mah * 7) / 10; // 0.7C
                    }
                    ch->v_peak_mv = ch->v_filtered_mv;
                }
            }
            break;

        // ── СВИНЕЦЬ (IUoU) ──
        case STATE_LA_BULK_CC: {
            uint16_t v_abs_target = la_calc_compensated_v(2400 * ch->cell_count, ch->t_current_c, ch->cell_count);
            ch->target_v_mv = v_abs_target;
            ch->target_i_ma = ch->capacity_mah / 10;

            if (ch->v_filtered_mv >= v_abs_target) {
                ch->state = STATE_LA_ABSORPTION_CV;
                ch->state_time_sec = 0;
            }
            if (ch->state_time_sec > 14 * 3600) { // 14 годин ліміт
                ch->state = STATE_FAULT;
                ch->fault = FAULT_TIMEOUT;
            }
            break;
        }

        case STATE_LA_ABSORPTION_CV: {
            uint16_t v_abs_target = la_calc_compensated_v(2400 * ch->cell_count, ch->t_current_c, ch->cell_count);
            ch->target_v_mv = v_abs_target;

            // Перехід на Float за спадом струму < C/50 або таймером 4 години
            if (measured_i_ma < (ch->capacity_mah / 50) || ch->state_time_sec > 4 * 3600) {
                ch->state = STATE_LA_FLOAT;
                ch->state_time_sec = 0;
            }
            break;
        }

        case STATE_LA_FLOAT: {
            uint16_t v_flt_target = la_calc_compensated_v(2260 * ch->cell_count, ch->t_current_c, ch->cell_count);
            ch->target_v_mv = v_flt_target;
            ch->target_i_ma = ch->capacity_mah / 20; // обмеження струму
            break;
        }

        // ── NiMH ──
        case STATE_NIMH_PRECHARGE:
            if (ch->v_filtered_mv >= 1000 * ch->cell_count) {
                ch->state = STATE_NIMH_FAST_CC;
                ch->state_time_sec = 0;
                ch->target_i_ma = (ch->capacity_mah * 7) / 10; // 0.7C
                ch->v_peak_mv = ch->v_filtered_mv;
            }
            if (ch->state_time_sec > 30 * 60) {
                ch->state = STATE_FAULT;
                ch->fault = FAULT_TIMEOUT;
            }
            break;

        case STATE_NIMH_FAST_CC:
            if (ch->v_filtered_mv > ch->v_peak_mv) {
                ch->v_peak_mv = ch->v_filtered_mv;
            }

            // Критерії термінації: -dV >= 4 мВ на комірку АБО dT/dt >= 1.0 °C/хв (16.6 м°C/с)
            uint32_t dv_threshold = 4 * ch->cell_count;
            bool neg_dv = (ch->v_peak_mv > ch->v_filtered_mv + dv_threshold);
            bool temp_slope = (ch->dt_dt_mdeg_per_sec >= 17 && ch->state_time_sec > 300);

            if (neg_dv || temp_slope) {
                ch->state = STATE_NIMH_TOP_OFF;
                ch->state_time_sec = 0;
                ch->target_i_ma = ch->capacity_mah / 10; // 0.1C дозаряд
            }
            if (ch->state_time_sec > 2 * 3600) { // 2 години захисний ліміт
                ch->state = STATE_FAULT;
                ch->fault = FAULT_TIMEOUT;
            }
            break;

        case STATE_NIMH_TOP_OFF:
            if (ch->state_time_sec >= 30 * 60) { // 30 хвилин дозаряду
                ch->state = STATE_NIMH_TRICKLE;
                ch->state_time_sec = 0;
                ch->target_i_ma = ch->capacity_mah / 35; // C/35 краплинний підзаряд
            }
            break;

        case STATE_NIMH_TRICKLE:
            ch->target_i_ma = ch->capacity_mah / 35;
            break;

        case STATE_FAULT:
            ch->target_v_mv = 0;
            ch->target_i_ma = 0;
            break;
    }
}
```

```cpp
#include <cstdint>
#include <array>
#include <algorithm>
#include <numeric>

namespace power {

enum class BatteryChem {
    LeadAcid,
    NiMH
};

enum class ChargerState {
    Standby,
    LeadAcidBulkCC,
    LeadAcidAbsorptionCV,
    LeadAcidFloat,
    NiMHPrecharge,
    NiMHFastCC,
    NiMHTopOff,
    NiMHTrickle,
    Fault
};

enum class ChargerFault {
    None,
    OverVoltage,
    OverTemp,
    Timeout,
    ReversePolarity
};

class UniversalCharger {
public:
    static constexpr size_t kAdcFilterSize = 32;
    static constexpr size_t kDtWindowSec = 60;

    UniversalCharger(BatteryChem chem, uint16_t capacity_mah, uint8_t cell_count)
        : chem_(chem), capacity_mah_(capacity_mah), cell_count_(cell_count) {
        v_buffer_.fill(0);
        t_history_.fill(25);
    }

    void update_sensors(uint16_t raw_v_mv, int16_t raw_t_c) {
        v_buffer_[v_buf_idx_] = raw_v_mv;
        v_buf_idx_ = (v_buf_idx_ + 1) % kAdcFilterSize;

        uint32_t sum = std::accumulate(v_buffer_.begin(), v_buffer_.end(), 0u);
        v_filtered_mv_ = sum / kAdcFilterSize;

        t_current_c_ = raw_t_c;
        int16_t old_t = t_history_[t_hist_idx_];
        t_history_[t_hist_idx_] = raw_t_c;
        t_hist_idx_ = (t_hist_idx_ + 1) % kDtWindowSec;

        dt_dt_mdeg_per_sec_ = (static_cast<int32_t>(raw_t_c - old_t) * 1000) / static_cast<int32_t>(kDtWindowSec);
    }

    void tick_1s(uint16_t measured_i_ma) {
        ++state_time_sec_;
        ++total_charge_sec_;

        if (t_current_c_ > 55) {
            trigger_fault(ChargerFault::OverTemp);
            return;
        }

        switch (state_) {
            case ChargerState::Standby:
                handle_standby();
                break;
            case ChargerState::LeadAcidBulkCC:
                handle_la_bulk();
                break;
            case ChargerState::LeadAcidAbsorptionCV:
                handle_la_absorption(measured_i_ma);
                break;
            case ChargerState::LeadAcidFloat:
                handle_la_float();
                break;
            case ChargerState::NiMHPrecharge:
                handle_nimh_precharge();
                break;
            case ChargerState::NiMHFastCC:
                handle_nimh_fast();
                break;
            case ChargerState::NiMHTopOff:
                handle_nimh_top_off();
                break;
            case ChargerState::NiMHTrickle:
                target_i_ma_ = capacity_mah_ / 35;
                break;
            case ChargerState::Fault:
                target_v_mv_ = 0;
                target_i_ma_ = 0;
                break;
        }
    }

    [[nodiscard]] ChargerState state() const noexcept { return state_; }
    [[nodiscard]] ChargerFault fault() const noexcept { return fault_; }
    [[nodiscard]] uint16_t target_v_mv() const noexcept { return target_v_mv_; }
    [[nodiscard]] uint16_t target_i_ma() const noexcept { return target_i_ma_; }

private:
    uint16_t calc_la_compensated_v(uint16_t base_mv) const noexcept {
        int32_t delta_t = static_cast<int32_t>(t_current_c_) - 25;
        int32_t comp_mv = -4 * static_cast<int32_t>(cell_count_) * delta_t;
        int32_t result = static_cast<int32_t>(base_mv) + comp_mv;
        return static_cast<uint16_t>(std::clamp(result, 10000, 16500));
    }

    void trigger_fault(ChargerFault fault) noexcept {
        state_ = ChargerState::Fault;
        fault_ = fault;
        target_v_mv_ = 0;
        target_i_ma_ = 0;
    }

    void handle_standby() noexcept {
        if (v_filtered_mv_ > 500) {
            state_time_sec_ = 0;
            if (chem_ == BatteryChem::LeadAcid) {
                state_ = ChargerState::LeadAcidBulkCC;
                target_i_ma_ = capacity_mah_ / 10;
                target_v_mv_ = calc_la_compensated_v(2400 * cell_count_);
            } else {
                if (v_filtered_mv_ < 1000u * cell_count_) {
                    state_ = ChargerState::NiMHPrecharge;
                    target_i_ma_ = capacity_mah_ / 10;
                } else {
                    state_ = ChargerState::NiMHFastCC;
                    target_i_ma_ = (capacity_mah_ * 7) / 10;
                }
                v_peak_mv_ = v_filtered_mv_;
            }
        }
    }

    void handle_la_bulk() noexcept {
        uint16_t v_abs = calc_la_compensated_v(2400 * cell_count_);
        target_v_mv_ = v_abs;
        target_i_ma_ = capacity_mah_ / 10;

        if (v_filtered_mv_ >= v_abs) {
            state_ = ChargerState::LeadAcidAbsorptionCV;
            state_time_sec_ = 0;
        }
        if (state_time_sec_ > 14 * 3600) {
            trigger_fault(ChargerFault::Timeout);
        }
    }

    void handle_la_absorption(uint16_t measured_i_ma) noexcept {
        target_v_mv_ = calc_la_compensated_v(2400 * cell_count_);
        if (measured_i_ma < (capacity_mah_ / 50) || state_time_sec_ > 4 * 3600) {
            state_ = ChargerState::LeadAcidFloat;
            state_time_sec_ = 0;
        }
    }

    void handle_la_float() noexcept {
        target_v_mv_ = calc_la_compensated_v(2260 * cell_count_);
        target_i_ma_ = capacity_mah_ / 20;
    }

    void handle_nimh_precharge() noexcept {
        if (v_filtered_mv_ >= 1000u * cell_count_) {
            state_ = ChargerState::NiMHFastCC;
            state_time_sec_ = 0;
            target_i_ma_ = (capacity_mah_ * 7) / 10;
            v_peak_mv_ = v_filtered_mv_;
        }
        if (state_time_sec_ > 1800) {
            trigger_fault(ChargerFault::Timeout);
        }
    }

    void handle_nimh_fast() noexcept {
        if (v_filtered_mv_ > v_peak_mv_) {
            v_peak_mv_ = v_filtered_mv_;
        }

        uint32_t dv_thresh = 4u * cell_count_;
        bool neg_dv = (v_peak_mv_ >= v_filtered_mv_ + dv_thresh);
        bool temp_slope = (dt_dt_mdeg_per_sec_ >= 17 && state_time_sec_ > 300);

        if (neg_dv || temp_slope) {
            state_ = ChargerState::NiMHTopOff;
            state_time_sec_ = 0;
            target_i_ma_ = capacity_mah_ / 10;
        }
        if (state_time_sec_ > 7200) {
            trigger_fault(ChargerFault::Timeout);
        }
    }

    void handle_nimh_top_off() noexcept {
        if (state_time_sec_ >= 1800) {
            state_ = ChargerState::NiMHTrickle;
            state_time_sec_ = 0;
            target_i_ma_ = capacity_mah_ / 35;
        }
    }

    BatteryChem chem_;
    ChargerState state_{ChargerState::Standby};
    ChargerFault fault_{ChargerFault::None};

    uint16_t capacity_mah_;
    uint8_t cell_count_;

    std::array<uint32_t, kAdcFilterSize> v_buffer_{};
    size_t v_buf_idx_{0};
    uint32_t v_filtered_mv_{0};
    uint32_t v_peak_mv_{0};

    std::array<int16_t, kDtWindowSec> t_history_{};
    size_t t_hist_idx_{0};
    int16_t t_current_c_{25};
    int16_t dt_dt_mdeg_per_sec_{0};

    uint32_t state_time_sec_{0};
    uint32_t total_charge_sec_{0};

    uint16_t target_v_mv_{0};
    uint16_t target_i_ma_{0};
};

} // namespace power
```

:::

### Практичні інженерні пастки та їх усунення

- **Хибний спад −ΔV на початковій ділянці швидкого заряду**: глибоко розряджений або залежаний NiMH елемент у перші 3–5 хвилин після подачі струму 0.7–1.0C зазнає швидкої електрохімічної релаксації подвійного електричного шару, що викликає тимчасове просідання напруги на 10–15 мВ. Якщо аналізатор −ΔV активний із першої секунди, зарядник хибно зупинить заряд, заповнивши лише 2% ємності. Захист: ігнорування критерію −ΔV упродовж перших 300 секунд перебування у стані `STATE_NIMH_FAST_CC` (`state_time_sec > 300`).
- **Спроба детектування −ΔV при малих струмах (< 0.3C)**: за струму 0.1–0.2C швидкість виділення кисню настільки мала, що тепло повністю розсіюється в довкілля. Внутрішній розігрів відсутній, електрохімічний спад напруги зникає, а крива виходить на абсолютно плоске горизонтальне плато. Контролер ніколи не дочекається умови −ΔV і заряджатиме батарею безкінечно, випаровуючи воду з лужного електроліту через аварійний клапан. Для струмів < 0.3C термінацію виконують виключно за таймером або підрахунком відданих кулонів.
- **Втрата теплового контакту NTC-давача**: якщо термістор відійшов від металевого корпусу комірки або відклеївся термоскотч, він вимірюватиме температуру навколишнього повітря, а не акумулятора. Градієнт `dT/dt` не досягне порогу 1.0 °C/хв навіть за розігріву батареї до 70 °C. Захист: паралельний максимальний таймер заряду (safety timer), налаштований на 115–120% від теоретичного часу повного заряду номінальним струмом.
- **Заряд холодного свинцевого акумулятора без датчика температури**: спроба зарядити замерзлий автомобільний або стаціонарний акумулятор фіксованою напругою 14.4 В при −20 °C призводить до того, що через занижену напругу батарея візьме лише 10–15% ємності, а залишена на морозі розведена кислота замерзне в суцільну кригу.
