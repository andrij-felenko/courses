# ⚙️ Програмна обробка сигналу 4–20 мА та діагностика лінії за стандартом NAMUR NE 43

Зчитування аналогового сигналу 4–20 мА у вбудованих системах вимагає не простого перетворення коду АЦП на число в пам'яті, а побудови надійного вимірювального тракту, здатного працювати в умовах промислових завад, захищати вхідні кола від перенапруг і здійснювати безперервну діагностику кабельної лінії. Стандарт NAMUR NE 43 визначає чіткі межі струмів для розпізнавання обриву дроту, виходу за межі вимірювання та короткого замикання чутливого елемента. Цей проект охоплює повний цикл: від схемотехнічного розрахунку захисного каскаду до цифрової фільтрації, калібрування за двома точками та програмної машини станів мовами C та C++.

## 1. Апаратний тракт та узгодження з АЦП

Промисловий струм петлі I_loop (4–20 мА) перетворюється на напругу за допомогою прецизійного шунта R_shunt. Номінал шунта обирають залежно від опорної напруги АЦП мікроконтролера:

- **Для АЦП з опорною напругою V_ref = 3.30 В:** оптимальним є шунт R_shunt = 100.0 Ом. За струму 4.0 мА напруга становить 0.40 В, за струму 20.0 мА — 2.00 В, а за аварійного струму перевантаження 21.0 мА — 2.10 В, що залишає комфортний запас до верхньої межі живлення АЦП;
- **Для систем з опорною напругою V_ref = 5.00 В:** традиційно застосовують шунт R_shunt = 250.0 Ом, що перетворює діапазон 4–20 мА на зручну шкалу 1.00–5.00 В.

Вимоги до резистора шунта є критичними для метрології: точність номіналу не гірша 0.1%, а температурний коефіцієнт опору (ТКС) — не більше 25 ppm/°C. Звичайний вуглецевий резистор із ТКС 200 ppm/°C при нагріванні всередині промислової шафи на 40 °C створить додаткову температурну похибку 0.8%, що повністю зруйнує клас точності давача.

Перед входом аналогово-цифрового перетворювача обов'язково встановлюють симетричний низькочастотний RC-фільтр, який захищає вхід від високочастотних імпульсних наведень та забезпечує антиаліасинг (протизгинну фільтрацію).

## 2. Межі струмів та діагностика за стандартом NAMUR NE 43

Стандарт міжнародної асоціації користувачів автоматизації NAMUR NE 43 регламентує поділ струмового діапазону на функціональні зони для уніфікації взаємодії між польовими приладами та контролерами:

```
Струм (мА)   Статус лінії за NAMUR NE 43      Дія керуючої програми
-------------------------------------------------------------------------------------
I < 3.6      Обрив лінії (Wire Break)         Аварія каналу, блокування регулятора
3.6 ≤ I < 3.8 Нижня зона нечутливості (Under) Попередження, фіксація на шкалі 0%
3.8 ≤ I ≤ 20.5 Робочий діапазон (Valid range)  Нормальне масштабування у фіз. одиниці
20.5 < I ≤ 21.0 Верхня зона перевантаження     Попередження, фіксація на шкалі 100%
I > 21.0     Аварія сенсора / Коротке замкн.  Аварія каналу, перехід у безпечний стан
```

Щоб запобігти брязкоту (flapping) статусів на межах діапазонів, алгоритм обробки повинен реалізувати програмний гістерезис (зазвичай 0.05–0.10 мА) або лічильник підтвердження виходу за межі тривалістю кілька послідовних вибірок.

## 3. Математична модель цифрової фільтрації та масштабування

Виміряна вибірка коду АЦП перетворюється на напругу на шунті:

```
V_adc = ( raw_adc / ADC_MAX ) · V_ref       [миттєва напруга на вході АЦП]
```

Для придушення промислової завади 50/100 Гц та шуму квантування сигнал пропускають крізь цифровий експоненційний фільтр нижніх частот першого порядку:

```
V_filtered[k] = V_filtered[k-1] + α · ( V_adc[k] − V_filtered[k-1] )
```

Коефіцієнт згладжування α обирають з урахуванням частоти виклику функції обробки f_sample та бажаної сталої часу фільтрації τ:

```
α = dt / ( τ + dt ) = (1 / f_sample) / ( τ + (1 / f_sample) )
```

Наприклад, при частоті опитування 100 Гц (dt = 10 мс) та бажаній сталій часу τ = 100 мс коефіцієнт становить α ≈ 0.09.

Після обчислення згладженого струму I_loop = (V_filtered / R_shunt) · 1000 лінійна інтерполяція у фізичну величину (наприклад, тиск у барах або рівень у метрах) виконується за формулою:

```
Scale_Fraction = ( I_loop − 4.0 ) / ( 20.0 − 4.0 )
Physical_Value = Phys_Zero + Scale_Fraction · ( Phys_Span − Phys_Zero )
```

## 4. Реалізація драйвера каналу мовами C та C++

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>

// Діагностичні стани лінії за стандартом NAMUR NE 43
typedef enum {
    CURRENT_LOOP_OK = 0,
    CURRENT_LOOP_WARN_UNDER_RANGE,
    CURRENT_LOOP_WARN_OVER_RANGE,
    CURRENT_LOOP_ERROR_WIRE_BREAK,
    CURRENT_LOOP_ERROR_SHORT_CIRCUIT
} CurrentLoopStatus;

// Структура конфігурації вимірювального каналу
typedef struct {
    float r_shunt_ohms;       // Опір вимірювального шунта (100.0 або 250.0 Ом)
    float v_ref_volts;        // Опорна напруга АЦП (3.30 або 5.00 В)
    uint32_t adc_max_ticks;   // Максимальний код АЦП (4095 для 12 біт)
    float filter_alpha;       // Вага експоненційного фільтра (0.05..0.20)
    float phys_zero;          // Фізичне значення при 4.0 мА (наприклад, 0.0 бар)
    float phys_span;          // Фізичне значення при 20.0 мА (наприклад, 16.0 бар)
    
    // Внутрішній стан фільтрації та калібрування
    float filtered_voltage;   // Поточна згладжена напруга на шунті
    bool is_initialized;      // Прапорець первинного прогріву фільтра
} CurrentLoopChannel;

// Структура результату обробки
typedef struct {
    float current_ma;         // Струм петлі в міліамперах
    float physical_value;     // Обчислена фізична величина
    CurrentLoopStatus status; // Діагностичний стан лінії
} LoopMeasurement;

void current_loop_init(CurrentLoopChannel *ch, float r_shunt, float v_ref, 
                       uint32_t adc_max, float alpha, float p_zero, float p_span) {
    ch->r_shunt_ohms = r_shunt;
    ch->v_ref_volts = v_ref;
    ch->adc_max_ticks = adc_max;
    ch->filter_alpha = alpha;
    ch->phys_zero = p_zero;
    ch->phys_span = p_span;
    ch->filtered_voltage = 0.0f;
    ch->is_initialized = false;
}

LoopMeasurement current_loop_process(CurrentLoopChannel *ch, uint16_t raw_adc) {
    LoopMeasurement result;
    
    // Перетворення вибірки АЦП на напругу шунта
    float raw_voltage = ((float)raw_adc / (float)ch->adc_max_ticks) * ch->v_ref_volts;
    
    // Експоненційне згладжування завад
    if (!ch->is_initialized) {
        ch->filtered_voltage = raw_voltage;
        ch->is_initialized = true;
    } else {
        ch->filtered_voltage += ch->filter_alpha * (raw_voltage - ch->filtered_voltage);
    }
    
    // Розрахунок струму в міліамперах: I = (U / R) * 1000
    float current_ma = (ch->filtered_voltage / ch->r_shunt_ohms) * 1000.0f;
    result.current_ma = current_ma;
    
    // Класифікація стану згідно з NAMUR NE 43
    if (current_ma < 3.60f) {
        result.status = CURRENT_LOOP_ERROR_WIRE_BREAK;
        result.physical_value = ch->phys_zero;
    } else if (current_ma < 3.80f) {
        result.status = CURRENT_LOOP_WARN_UNDER_RANGE;
        result.physical_value = ch->phys_zero;
    } else if (current_ma > 21.00f) {
        result.status = CURRENT_LOOP_ERROR_SHORT_CIRCUIT;
        result.physical_value = ch->phys_span;
    } else if (current_ma > 20.50f) {
        result.status = CURRENT_LOOP_WARN_OVER_RANGE;
        result.physical_value = ch->phys_span;
    } else {
        result.status = CURRENT_LOOP_OK;
        // Лінійна інтерполяція в діапазоні 4.0..20.0 мА
        float fraction = (current_ma - 4.0f) / (20.0f - 4.0f);
        result.physical_value = ch->phys_zero + fraction * (ch->phys_span - ch->phys_zero);
    }
    
    return result;
}
```
```cpp
#include <cstdint>
#include <algorithm>

namespace embedded {

enum class LoopStatus : uint8_t {
    Ok,
    WarningUnderRange,
    WarningOverRange,
    ErrorWireBreak,
    ErrorShortCircuit
};

struct LoopConfig {
    float r_shunt_ohms{100.0f};
    float v_ref_volts{3.30f};
    uint32_t adc_max_ticks{4095};
    float filter_alpha{0.10f};
    float phys_zero{0.0f};
    float phys_span{16.0f};
};

struct MeasurementResult {
    float current_ma;
    float physical_value;
    LoopStatus status;
};

class CurrentLoopReceiver {
public:
    explicit constexpr CurrentLoopReceiver(const LoopConfig& config) noexcept
        : config_{config}, filtered_voltage_{0.0f}, initialized_{false} {}

    [[nodiscard]] MeasurementResult update(uint16_t raw_adc) noexcept {
        const float raw_voltage = (static_cast<float>(raw_adc) / 
                                   static_cast<float>(config_.adc_max_ticks)) * config_.v_ref_volts;
        
        if (!initialized_) {
            filtered_voltage_ = raw_voltage;
            initialized_ = true;
        } else {
            filtered_voltage_ += config_.filter_alpha * (raw_voltage - filtered_voltage_);
        }

        const float current_ma = (filtered_voltage_ / config_.r_shunt_ohms) * 1000.0f;
        const auto status = evaluate_namur(current_ma);
        const float phys_val = scale_to_physics(current_ma);

        return MeasurementResult{
            .current_ma = current_ma,
            .physical_value = phys_val,
            .status = status
        };
    }

    void reset() noexcept {
        initialized_ = false;
        filtered_voltage_ = 0.0f;
    }

private:
    [[nodiscard]] static constexpr LoopStatus evaluate_namur(float current_ma) noexcept {
        if (current_ma < 3.60f) return LoopStatus::ErrorWireBreak;
        if (current_ma < 3.80f) return LoopStatus::WarningUnderRange;
        if (current_ma > 21.00f) return LoopStatus::ErrorShortCircuit;
        if (current_ma > 20.50f) return LoopStatus::WarningOverRange;
        return LoopStatus::Ok;
    }

    [[nodiscard]] constexpr float scale_to_physics(float current_ma) const noexcept {
        const float clamped_current = std::clamp(current_ma, 4.0f, 20.0f);
        const float normalized = (clamped_current - 4.0f) / 16.0f;
        return config_.phys_zero + normalized * (config_.phys_span - config_.phys_zero);
    }

    LoopConfig config_;
    float filtered_voltage_;
    bool initialized_;
};

} // namespace embedded
```
:::

## 5. Практичні підводні камені та захист обладнання

1. **Пусковий кидок струму давача (Inrush Current)**: У момент підключення живлення до петлі 24 В вхідні конденсатори польового давача заряджаються, викликаючи короткочасний сплеск струму силою до 50–100 мА тривалістю 2–5 мс. Програмна система діагностики не повинна негайно піднімати аварійний прапорець `ErrorShortCircuit`: перші 100–200 мс після подачі напруги контролер повинен перебувати у стані ініціалізації.
2. **Захист шунта від випадкового короткого замикання на шину 24 В**: Якщо монтажник під час пусконалагодження випадково підключить сигнальний провід приймача напряму до шини живлення 24 В, струм крізь шунт 100 Ом складе I = 24 / 100 = 0.24 А. Потужність, що виділятиметься на резисторі: P = I² · R = (0.24)² · 100 = 5.76 Вт. Стандартний SMD-резистор типорозміру 0805 чи 1206 вигорить за кілька секунд. Щоб уникнути пошкодження плати, послідовно з лінією встановлюють самовідновний полімерний запобіжник (PPTC PolySwitch) на струм 50 мА, а паралельно до шунта — потужний супресор TVS на 3.6 В.
3. **Калібрування за двома точками**: Щоб компенсувати технологічний розкид номіналу шунта R_shunt та похибку опорної напруги АЦП V_ref, на виробництві проводять калібрування каналу за допомогою калібратора струмової петлі. Подають точний струм 4.000 мА і записують отриманий код АЦП як `ADC_Zero`, потім подають 20.000 мА і записують `ADC_Span`. Формула лінійного перерахунку використовує ці калібрувальні коефіцієнти, що зберігаються в енергонезалежній пам'яті (EEPROM/Flash), повністю усуваючи апаратні похибки пасивних компонентів.
