# ⚙️ Автоматизований стендовий бігун приймального контролю батарейних пакетів (FAT Runner)

Приймальний контроль щойно зібраного акумуляторного пакета на виробничій лінії або в дослідній лабораторії не можна довіряти ручним діям оператора з мультиметром. Людський фактор неминуче пропускає мілівольтові розбіжності між сусідніми паралелями, не встигає зафіксувати динаміку нагріву зварного шва під час короткого струмового імпульсу або не помічає неприпустиму затримку спрацьовування захисту AFE при виході за межі безпечної робочої зони. Для надійної та повторюваної валідації застосовують автоматизований стендовий контролер (англ. *Test Jig Controller*), який через цифрові інтерфейси синхронно керує програмованим джерелом живлення, електронним навантаженням та шиною зв'язку BMS (CAN/UART/SMBus), виконуючи послідовність випробувань за суворим детермінованим регламентом.

Головна мета автоматизованого стенда полягає не просто у фіксації статусу «Pass/Fail», а у вимірюванні фізичних параметрів збірки під керованим навантаженням із прив'язкою до часу. Будь-яке відхилення градієнта температури, швидкості зростання напруги на окремій паралелі чи контактного опору зварювання фіксується в цифровому паспорті батареї, унеможливлюючи вихід бракованого або потенційно небезпечного виробу за межі цеху.

### Архітектура стендового комплексу

Стенд об'єднує силову частину та вимірювально-діагностичний контур. Програмоване джерело постійного струму (PSU) забезпечує контрольований зарядний профіль із точним обмеженням вихідної напруги та струму. Програмоване електронне навантаження (DC Load) формує калібровані імпульси струму розряду для оцінки просідання напруги та перевірки реакції системи струмового захисту. Окремий багатоканальний блок прецизійного збору даних на базі 24-бітного сигма-дельта АЦП підмикається безпосередньо до вузлів зварювання через Кельвін-контакти.

```
       ┌───────────────────────────────────────────────────────────┐
       │                Автоматизований стенд FAT                  │
       │                                                           │
       │  ┌────────────────┐  ┌────────────────┐  ┌─────────────┐  │
       │  │ Програмоване   │  │   Електронне   │  │  Кельвін-   │  │
       │  │ джерело (PSU)  │  │ навантаження   │  │  мікро-     │  │
       │  │  0..60 В / 20 А│  │  0..60 В / 50 А│  │ вольтметр   │  │
       │  └───────┬────────┘  └───────┬────────┘  └──────┬──────┘  │
       │          │                   │                  │         │
       │          └─────────────┬─────┴──────────────────┘         │
       │                        │ Силова шина                      │
       │                        ▼                                  │
       │               ┌─────────────────┐                         │
       │               │ Досліджуваний   │◄──── CAN-шина ────┐     │
       │               │ батарейний стек │   (телеметрія AFE)│     │
       │               └─────────────────┘                   │     │
       │                                                     │     │
       │  ┌───────────────────────────────────────────────┐  │     │
       │  │ Стендовий контролер / керуюча станція (FAT)   ├──┘     │
       │  │   Скінченний автомат: OCV → R_weld → CC/CV    │        │
       │  └───────────────────────────────────────────────┘        │
       └───────────────────────────────────────────────────────────┘
```

Керуюча програма реалізує скінченний автомат (FSM), у якому кожен крок є умовою переходу до наступного. У разі порушення будь-якого ліміту (наприклад, перегрів NTC понад 45 °C при заряді, дельта напруг понад 25 мВ або контактний опір шва понад 0.7 мОм) автомат миттєво знеструмлює силові реле стенда, надсилає в BMS команду аварійного блокування та переходить у стан ізоляції помилки `FAT_STATE_FAILED`.

### Програмна реалізація автомата тестування

Нижче наведено модульну реалізацію логіки тестування. Код на C орієнтований на виконання на вбудованому стендовому мікроконтролері або промисловому контролері PLC, тоді як варіант на C++20 надає строго типізований інтерфейс з обробкою результатів через `std::expected` для керуючої станції стенда.

:::tabs
```c
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define MAX_CELLS 16
#define MAX_NTC   4

typedef enum {
    FAT_STATE_IDLE,
    FAT_STATE_OCV_CHECK,
    FAT_STATE_WELD_RESISTANCE_TEST,
    FAT_STATE_PRECHARGE_QUALIFICATION,
    FAT_STATE_CC_CV_CHARGE_TEST,
    FAT_STATE_SAFETY_TRIP_VERIFICATION,
    FAT_STATE_PASSED,
    FAT_STATE_FAILED
} fat_state_t;

typedef enum {
    FAT_ERR_NONE = 0,
    FAT_ERR_OCV_OUT_OF_BOUNDS,
    FAT_ERR_CELL_IMBALANCE_TOO_HIGH,
    FAT_ERR_WELD_RESISTANCE_EXCESSIVE,
    FAT_ERR_TEMPERATURE_GRADIENT_HIGH,
    FAT_ERR_OVERVOLTAGE_PROTECTION_FAILED,
    FAT_ERR_COMMUNICATION_TIMEOUT
} fat_error_t;

typedef struct {
    uint16_t min_cell_mv;
    uint16_t max_cell_mv;
    uint16_t max_imbalance_mv;
    uint32_t max_weld_resistance_uohm;
    int16_t  max_temp_c;
    int16_t  max_temp_gradient_c;
    uint16_t ovp_trip_threshold_mv;
} fat_limits_t;

typedef struct {
    uint8_t  cell_count;
    uint8_t  ntc_count;
    uint16_t cell_mv[MAX_CELLS];
    int16_t  temp_c[MAX_NTC];
    uint32_t weld_res_uohm[MAX_CELLS];
    int32_t  current_ma;
    bool     bms_chg_mosfet_active;
    bool     bms_dsg_mosfet_active;
} pack_telemetry_t;

typedef struct {
    fat_state_t      state;
    fat_error_t      last_error;
    fat_limits_t     limits;
    pack_telemetry_t telemetry;
    uint32_t         step_timer_ms;
} fat_runner_t;

void fat_runner_init(fat_runner_t *runner, const fat_limits_t *limits) {
    memset(runner, 0, sizeof(fat_runner_t));
    runner->state = FAT_STATE_IDLE;
    runner->limits = *limits;
}

fat_error_t fat_evaluate_ocv(fat_runner_t *runner) {
    uint16_t min_v = 0xFFFF;
    uint16_t max_v = 0;
    
    for (uint8_t i = 0; i < runner->telemetry.cell_count; ++i) {
        uint16_t v = runner->telemetry.cell_mv[i];
        if (v < runner->limits.min_cell_mv || v > runner->limits.max_cell_mv) {
            return FAT_ERR_OCV_OUT_OF_BOUNDS;
        }
        if (v < min_v) min_v = v;
        if (v > max_v) max_v = v;
    }
    
    if ((max_v - min_v) > runner->limits.max_imbalance_mv) {
        return FAT_ERR_CELL_IMBALANCE_TOO_HIGH;
    }
    return FAT_ERR_NONE;
}

fat_error_t fat_evaluate_weld_resistance(fat_runner_t *runner) {
    for (uint8_t i = 0; i < runner->telemetry.cell_count; ++i) {
        if (runner->telemetry.weld_res_uohm[i] > runner->limits.max_weld_resistance_uohm) {
            return FAT_ERR_WELD_RESISTANCE_EXCESSIVE;
        }
    }
    return FAT_ERR_NONE;
}

fat_error_t fat_evaluate_thermal(fat_runner_t *runner) {
    int16_t min_t = 30000;
    int16_t max_t = -30000;
    
    for (uint8_t i = 0; i < runner->telemetry.ntc_count; ++i) {
        int16_t t = runner->telemetry.temp_c[i];
        if (t > runner->limits.max_temp_c) {
            return FAT_ERR_TEMPERATURE_GRADIENT_HIGH;
        }
        if (t < min_t) min_t = t;
        if (t > max_t) max_t = t;
    }
    
    if ((max_t - min_t) > runner->limits.max_temp_gradient_c) {
        return FAT_ERR_TEMPERATURE_GRADIENT_HIGH;
    }
    return FAT_ERR_NONE;
}

void fat_runner_tick(fat_runner_t *runner, uint32_t dt_ms) {
    runner->step_timer_ms += dt_ms;
    
    switch (runner->state) {
        case FAT_STATE_IDLE:
            runner->state = FAT_STATE_OCV_CHECK;
            runner->step_timer_ms = 0;
            break;
            
        case FAT_STATE_OCV_CHECK: {
            fat_error_t err = fat_evaluate_ocv(runner);
            if (err != FAT_ERR_NONE) {
                runner->last_error = err;
                runner->state = FAT_STATE_FAILED;
            } else {
                runner->state = FAT_STATE_WELD_RESISTANCE_TEST;
                runner->step_timer_ms = 0;
            }
            break;
        }
        
        case FAT_STATE_WELD_RESISTANCE_TEST: {
            fat_error_t err = fat_evaluate_weld_resistance(runner);
            if (err != FAT_ERR_NONE) {
                runner->last_error = err;
                runner->state = FAT_STATE_FAILED;
            } else {
                runner->state = FAT_STATE_CC_CV_CHARGE_TEST;
                runner->step_timer_ms = 0;
            }
            break;
        }
        
        case FAT_STATE_CC_CV_CHARGE_TEST: {
            fat_error_t th_err = fat_evaluate_thermal(runner);
            if (th_err != FAT_ERR_NONE) {
                runner->last_error = th_err;
                runner->state = FAT_STATE_FAILED;
                break;
            }
            if (runner->step_timer_ms >= 5000) {
                runner->state = FAT_STATE_SAFETY_TRIP_VERIFICATION;
                runner->step_timer_ms = 0;
            }
            break;
        }
        
        case FAT_STATE_SAFETY_TRIP_VERIFICATION: {
            if (!runner->telemetry.bms_chg_mosfet_active) {
                runner->state = FAT_STATE_PASSED;
            } else if (runner->step_timer_ms > 2000) {
                runner->last_error = FAT_ERR_OVERVOLTAGE_PROTECTION_FAILED;
                runner->state = FAT_STATE_FAILED;
            }
            break;
        }
        
        case FAT_STATE_PASSED:
        case FAT_STATE_FAILED:
        default:
            break;
    }
}
```
```cpp
#include <iostream>
#include <vector>
#include <span>
#include <expected>
#include <algorithm>
#include <numeric>
#include <chrono>
#include <cstdint>

enum class FatState {
    Idle,
    OcvCheck,
    WeldResistanceTest,
    PrechargeQualification,
    CcCvChargeTest,
    SafetyTripVerification,
    Passed,
    Failed
};

enum class FatError {
    None,
    OcvOutOfBounds,
    CellImbalanceTooHigh,
    WeldResistanceExcessive,
    TemperatureGradientHigh,
    OvervoltageProtectionFailed,
    CommunicationTimeout
};

struct FatLimits {
    uint16_t min_cell_mv{2800};
    uint16_t max_cell_mv{4250};
    uint16_t max_imbalance_mv{25};
    uint32_t max_weld_resistance_uohm{700};
    int16_t  max_temp_c{50};
    int16_t  max_temp_gradient_c{6};
    uint16_t ovp_trip_threshold_mv{4280};
};

struct PackTelemetry {
    std::vector<uint16_t> cell_mv;
    std::vector<int16_t>  temp_c;
    std::vector<uint32_t> weld_res_uohm;
    int32_t               current_ma{0};
    bool                  bms_chg_mosfet_active{true};
    bool                  bms_dsg_mosfet_active{true};
};

class FatRunner {
public:
    explicit FatRunner(FatLimits limits) : limits_(limits) {}

    void set_telemetry(PackTelemetry telemetry) {
        telemetry_ = std::move(telemetry);
    }

    [[nodiscard]] FatState state() const noexcept { return state_; }
    [[nodiscard]] FatError last_error() const noexcept { return last_error_; }

    void tick(std::chrono::milliseconds dt) {
        step_timer_ += dt;

        switch (state_) {
            case FatState::Idle:
                state_ = FatState::OcvCheck;
                step_timer_ = std::chrono::milliseconds{0};
                break;

            case FatState::OcvCheck:
                if (auto res = evaluate_ocv(); !res) {
                    last_error_ = res.error();
                    state_ = FatState::Failed;
                } else {
                    state_ = FatState::WeldResistanceTest;
                    step_timer_ = std::chrono::milliseconds{0};
                }
                break;

            case FatState::WeldResistanceTest:
                if (auto res = evaluate_weld_resistance(); !res) {
                    last_error_ = res.error();
                    state_ = FatState::Failed;
                } else {
                    state_ = FatState::CcCvChargeTest;
                    step_timer_ = std::chrono::milliseconds{0};
                }
                break;

            case FatState::CcCvChargeTest:
                if (auto res = evaluate_thermal(); !res) {
                    last_error_ = res.error();
                    state_ = FatState::Failed;
                } else if (step_timer_ >= std::chrono::milliseconds{5000}) {
                    state_ = FatState::SafetyTripVerification;
                    step_timer_ = std::chrono::milliseconds{0};
                }
                break;

            case FatState::SafetyTripVerification:
                if (!telemetry_.bms_chg_mosfet_active) {
                    state_ = FatState::Passed;
                } else if (step_timer_ > std::chrono::milliseconds{2000}) {
                    last_error_ = FatError::OvervoltageProtectionFailed;
                    state_ = FatState::Failed;
                }
                break;

            case FatState::Passed:
            case FatState::Failed:
                break;
        }
    }

private:
    [[nodiscard]] std::expected<void, FatError> evaluate_ocv() const {
        if (telemetry_.cell_mv.empty()) {
            return std::unexpected(FatError::CommunicationTimeout);
        }

        const auto [min_it, max_it] = std::minmax_element(
            telemetry_.cell_mv.begin(), telemetry_.cell_mv.end());

        if (*min_it < limits_.min_cell_mv || *max_it > limits_.max_cell_mv) {
            return std::unexpected(FatError::OcvOutOfBounds);
        }

        if (static_cast<uint16_t>(*max_it - *min_it) > limits_.max_imbalance_mv) {
            return std::unexpected(FatError::CellImbalanceTooHigh);
        }

        return {};
    }

    [[nodiscard]] std::expected<void, FatError> evaluate_weld_resistance() const {
        for (const auto r_uohm : telemetry_.weld_res_uohm) {
            if (r_uohm > limits_.max_weld_resistance_uohm) {
                return std::unexpected(FatError::WeldResistanceExcessive);
            }
        }
        return {};
    }

    [[nodiscard]] std::expected<void, FatError> evaluate_thermal() const {
        if (telemetry_.temp_c.empty()) {
            return {};
        }

        const auto [min_it, max_it] = std::minmax_element(
            telemetry_.temp_c.begin(), telemetry_.temp_c.end());

        if (*max_it > limits_.max_temp_c) {
            return std::unexpected(FatError::TemperatureGradientHigh);
        }

        if (static_cast<int16_t>(*max_it - *min_it) > limits_.max_temp_gradient_c) {
            return std::unexpected(FatError::TemperatureGradientHigh);
        }

        return {};
    }

    FatLimits limits_;
    PackTelemetry telemetry_;
    FatState state_{FatState::Idle};
    FatError last_error_{FatError::None};
    std::chrono::milliseconds step_timer_{0};
};
```
:::

### Пастки та інженерні крайові випадки проектування стенда

При розробці апаратного стендового устаткування та алгоритмів контролю необхідно враховувати низку прихованих паразитарних ефектів:

1. **Падіння напруги на вимірювальних лініях під час активного балансування.** Якщо стенд опитує напруги паралелей через тонкий балансувальний шлейф, доки внутрішні шунти BMS розсіюють струм 100 мА, опір дроту шлейфа `0.3 Ом` створює похибку `ΔU = 0.1 А · 0.3 Ом = 30 мВ`. Це призводить до помилкового бракування пакета за хибним критерієм дисбалансу напруг. Правильний стендовий протокол обов'язково тимчасово деактивує ключі балансування за 200 мс до зняття високоточних відліків АЦП (англ. *Quiet Measurement Window*).
2. **Паразитна індуктивність дротів і комутаційні викиди.** Перемикання електронного навантаження зі струму 0 А на 40 А з високою крутизною наростання (`di/dt > 10 А/мкс`) збуджує паразитну індуктивність силових дротів стенда, генеруючи зворотний сплеск напруги `L · di/dt`. Цей піковий сплеск здатний перевищити апаратний ліміт OVP у BMS або навіть пробити захисні TVS-діоди на платі керування. Для усунення цього ефекту на клемах стенда встановлюють силові RC-демпфери (снібери) та обмежують максимальну швидкість наростання струму навантаження (Slew Rate Limit) на рівні не більше 1–2 А/мкс.
3. **Термоелектрорушійна сила (термо-ЕРС) у 4-провідних лініях.** Вимірювання перехідного опору точкового зварювання оперує спадами напруги в діапазоні 0.5–5.0 мВ. Контакт мідних щупів Кельвіна з нікелевою або нікель-мідною стрічкою утворює біметалеву термопару з коефіцієнтом Зеєбека близько `15 мкВ/°C`. Якщо наконечник щупа нагрівається від попередніх випробувань на 10 °C відносно кімнатної температури, похибка термо-ЕРС сягає `150 мкВ`, що становить до 10–20% від вимірюваного сигналу. Для компенсації цього дрейфу стендовий контролер застосовує метод комутаційного реверсування струму: вимірювання виконуються двічі з протилежною полярністю струму, після чого результати віднімаються, що повністю нівелює постійну складову термо-ЕРС.
4. **Контроль стану ізоляції при високій напрузі.** Під час тестування високовольтних стеків (наприклад, 16S..24S) вимірювання опору ізоляції від силових полюсів до монтажного шасі (Hi-Pot test) повинно проводитися ДО підключення низьковольтного порту зв'язку BMS до ПК стенда. Пробій високої напруги на загальну шину через паразитно замкнений гвинт кріплення здатний випалити цифрові інтерфейси стендового ПК та створити загрозу ураження оператора електричним струмом.
5. **Калібрування нульового зміщення струмового шунта (Zero-offset Nulling).** Перед кожним пуском тестового циклу стендовий контролер зчитує показання струмового шунта BMS за розімкнених зовнішніх контакторів стенда. Будь-який ненульовий струм (вище 10–20 мА) свідчить про апаратний зсув нуля підсилювача шунта або витік через напівпровідникові ключі. Стенд автоматично надсилає калібрувальну команду обнулення в енергонезалежну пам'ять BMS, гарантуючи точність підрахунку кулонів (кулонівський лічильник SOC) у наступних циклах експлуатації.
