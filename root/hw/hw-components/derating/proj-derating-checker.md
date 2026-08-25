# ⚙️ Інструмент автоматизованої перевірки дератингу компонентів

Ця практична вставка містить закінчений інженерний модуль мовами C та C++, призначений для автоматизованого аудиту електричних і теплових навантажень електронних компонентів (резисторів, конденсаторів, MOSFET, діодів та індуктивностей) відповідно до нормативів стандартів надійності MIL-HDBK-338B та IPC-9592B Class 2.

Програма розв'язує ключову проблему сучасної схемотехніки: усунення людського фактора під час верифікації складних друкованих плат із сотнями чи тисячами компонентів. Ручний розрахунок коефіцієнтів запасу для кожного вузла забирає тижні інженерного часу та неминуче призводить до пропущених крайових режимів (перегрів окремого шунта в закритому корпусі, перевищення напруги на танталовому конденсаторі під час комутації). Пропонований модуль дозволяє інтегрувати математичну перевірку коефіцієнтів дератингу безпосередньо в конвеєри неперервної інтеграції (CI/CD для EDA), автоматично аналізуючи звіти симуляції SPICE-нетлістів та теплові карти термокамер.

## Архітектура перевірки та математичні моделі

Програма виконує багатокритеріальний аналіз робочої точки компонента за чотирма незалежними фізичними координатами:

1. **Коефіцієнт електричної напруги `S_V`:** Обчислюється як відношення пікової миттєвої напруги на виводах до паспортного номіналу `V_rated`. Для напівпровідникових ключів та конденсаторів це критичний бар'єр захисту від лавинного пробою та деградації діелектрика.
2. **Коефіцієнт струмового навантаження `S_I`:** Оцінює співвідношення середньоквадратичного струму `I_rms` до максимального струму виводів або обмотки. Він запобігає перегріву внутрішніх розварювальних провідників у мікросхемах та насиченню магнітних осердь дроселів.
3. **Температурний спад допустимої потужності (Thermal Knee Interpolation):** До температури зламу `T_knee` (зазвичай +70 °C для резисторів та +25 °C для потужних транзисторів на радіаторі) дозволена 100-відсоткова паспортна потужність `P_rated`. За вищих температур довкілля допустима межа лінійно спадає до нуля при досягненні `T_max`. Дератована межа потужності додатково множиться на нормативний коефіцієнт запасу `max_s_p`.
4. **Розрахунок внутрішньої температури кристала `T_j`:** Базується на моделі теплового опору ланцюжка кристал-довкілля `R_th_ja`:
   `T_j = Ta + P_diss · R_th_ja`.
   Розрахована температура перевіряється проти дератованої нормативної стелі (наприклад, не вище +105 °C за нормами MIL-HDBK-338B або +120 °C за промисловими нормами IPC-9592B).

## Специфіка алгоритмів дератингу за типами компонентів

### 1. Резистори: критичний опір та межа напруги
Для резисторів діє фундаментальне схемотехнічне правило: обмеження за потужністю `P_max` діє лише до певного значення опору — **критичного опору** `R_crit`:

```
R_crit = ( V_max )² / P_max
```

Якщо номінал резистора `R < R_crit`, деталь обмежена розсіюваною потужністю (струмовий нагрів). Якщо ж `R > R_crit`, деталь досягає граничної напруги пробою ізоляції `V_max` (Limiting Element Voltage) ще до того, як розсіювана потужність досягне номіналу `P_max`. Наприклад, для чип-резистора типорозміру 0805 з `P = 0.125 Вт` та `V_max = 150 В`, критичний опір становить `R_crit = 150² / 0.125 = 180 кОм`. Для резистора номіналом 1 МОм подача навіть 150 В дасть потужність лише `0.0225 Вт` (18 % від номіналу потужності), але напруга вже сягне 100 % від паспортного максимуму. Модуль автоматично контролює обидва параметри одночасно, запобігаючи мікродуговому перекриттю між витками резистивної нарізки.

### 2. Конденсатори: дератинг напруги, DC-bias та струму пульсацій
Для конденсаторів алгоритм розділяє вимоги за типом діелектрика:
- **Тантал MnO₂:** встановлює жорсткий поріг `S_V ≤ 0.50` через ризик термічного пробою діелектрика `Ta₂O₅`. Якщо опір кола живлення менший за 0.1 Ом/В, поріг додатково знижується до `0.33`.
- **Кераміка MLCC (X7R/X5R):** контролює `S_V ≤ 0.60 ... 0.70`, що гарантує збереження ефективної ємності під впливом постійної напруги зміщення (DC-bias ефект титанату барію).
- **Алюмінієві електроліти:** перевіряє не лише напругу `S_V ≤ 0.70 ... 0.80`, а й допустимий струм пульсацій `I_ripple`, обчислюючи додатковий внутрішній перегрів `ΔT = (I_rms)² · ESR · R_th_ca`.

### 3. Силові MOSFET: аналіз області безпечної роботи (SOA) та тепловий розгін
Для транзисторів алгоритм виконує подвійну перевірку:
- **Статичний дератинг:** напруга `V_ds ≤ 0.75 ... 0.80 · V_ds_max`, струм `I_d ≤ 0.70 · I_d_max`, температура кристала `T_j ≤ 110 ... 120 °C`.
- **Запас за тепловим розгоном:** оскільки опір відкритого каналу `R_ds(on)` зростає з температурою за ступенем `(T_j / 298)^1.8`, модуль перевіряє умову стабільності тепловідведення, сигналізуючи про небезпеку теплової лавини, якщо розрахункове підвищення температури перевищує тепловий запас радіатора.
- **Паралельне з'єднання транзисторів:** у разі паралельного ввімкнення кількох ключів струм ділиться нерівномірно через розкид порогової напруги затвора `V_th` та опору `R_ds(on)`. Модуль вводить поправочний коефіцієнт струмового дератингу `0.80` для багатоканальних силових каскадів.

### 4. Індуктивності та трансформатори: магнітне насичення та нагрів
Для магнітних компонентів контролюються два незалежні параметри:
- **Струм насичення `I_sat`:** піковий струм перетворювача не повинен перевищувати `0.70 ... 0.80 · I_sat`. Враховується температурне падіння індукції насичення фериту `B_sat` (при +100 °C ферит насичується при струмі на 20–25 % нижчому, ніж при кімнатній температурі).
- **Середньоквадратичний струм `I_rms`:** обмежується коефіцієнтом `0.70 ... 0.75` для запобігання перегріву емальпроводу обмоток понад температурний клас ізоляції (Class B: 130 °C, Class F: 155 °C, Class H: 180 °C).

## Реалізація модуля перевірки

:::tabs
```c
#include <stdio.h>
#include <stdbool.h>
#include <math.h>

/* Профілі стандартів надійності */
typedef enum {
    STANDARD_MIL_HDBK_338B,
    STANDARD_IPC_9592B_CLASS2,
    STANDARD_COMMERCIAL
} DeratingStandard;

/* Типи електронних компонентів */
typedef enum {
    COMP_RESISTOR_FILM,
    COMP_CAP_CERAMIC_X7R,
    COMP_CAP_TANTALUM_MNO2,
    COMP_CAP_ALU_ELECTROLYTIC,
    COMP_SEMICONDUCTOR_MOSFET,
    COMP_SEMICONDUCTOR_DIODE,
    COMP_INDUCTOR_POWER
} ComponentType;

/* Паспортні номінали компонента (Ratings) */
typedef struct {
    const char *designator;      /* Позиційне позначення (наприклад, "R12", "Q1") */
    ComponentType type;
    double v_rated;              /* Максимальна робоча напруга, В */
    double i_rated;              /* Максимальний постійний струм, А */
    double p_rated;              /* Паспортна потужність при Т <= 70 °C, Вт */
    double t_knee;               /* Температура зламу кривої потужності, °C (70 °C) */
    double t_max;                /* Максимальна температура компонента, °C */
    double rth_ja;               /* Тепловий опір кристал-довкілля, °C/Вт */
} ComponentRating;

/* Фактичний робочий режим (Operating Conditions) */
typedef struct {
    double v_actual_peak;        /* Пікова робоча напруга, В */
    double i_actual_rms;         /* Середньоквадратичний робочий струм, А */
    double p_actual_diss;        /* Фактична розсіювана потужність, Вт */
    double ta_ambient;           /* Температура довкілля всередині корпусу, °C */
} OperatingCondition;

/* Результат аудиту дератингу */
typedef struct {
    bool passed;
    double s_v;                  /* Фактичний коефіцієнт напруги */
    double s_i;                  /* Фактичний коефіцієнт струму */
    double s_p;                  /* Фактичний коефіцієнт потужності */
    double tj_actual;            /* Розрахована температура кристала/вузла, °C */
    double p_allowed_derated;    /* Допустима потужність з урахуванням дератингу, Вт */
    const char *failure_reason;
} DeratingResult;

/* Нормативні коефіцієнти для обраного стандарту */
typedef struct {
    double max_s_v;
    double max_s_i;
    double max_s_p;
    double max_tj;
} StandardLimits;

static StandardLimits get_limits(ComponentType type, DeratingStandard std) {
    StandardLimits lim = { 0.80, 0.80, 0.70, 125.0 };

    if (std == STANDARD_MIL_HDBK_338B) {
        lim.max_tj = 105.0;
        switch (type) {
            case COMP_RESISTOR_FILM:        lim.max_s_v = 0.70; lim.max_s_p = 0.50; lim.max_s_i = 0.70; break;
            case COMP_CAP_TANTALUM_MNO2:    lim.max_s_v = 0.50; lim.max_s_p = 0.50; lim.max_s_i = 0.50; break;
            case COMP_CAP_CERAMIC_X7R:      lim.max_s_v = 0.60; lim.max_s_p = 0.60; lim.max_s_i = 0.70; break;
            case COMP_CAP_ALU_ELECTROLYTIC: lim.max_s_v = 0.70; lim.max_s_p = 0.50; lim.max_s_i = 0.70; lim.max_tj = 85.0; break;
            case COMP_SEMICONDUCTOR_MOSFET: lim.max_s_v = 0.75; lim.max_s_p = 0.50; lim.max_s_i = 0.70; lim.max_tj = 110.0; break;
            case COMP_SEMICONDUCTOR_DIODE:  lim.max_s_v = 0.70; lim.max_s_p = 0.50; lim.max_s_i = 0.50; break;
            case COMP_INDUCTOR_POWER:       lim.max_s_v = 0.80; lim.max_s_p = 0.60; lim.max_s_i = 0.70; break;
        }
    } else if (std == STANDARD_IPC_9592B_CLASS2) {
        lim.max_tj = 115.0;
        switch (type) {
            case COMP_RESISTOR_FILM:        lim.max_s_v = 0.80; lim.max_s_p = 0.65; lim.max_s_i = 0.80; break;
            case COMP_CAP_TANTALUM_MNO2:    lim.max_s_v = 0.50; lim.max_s_p = 0.65; lim.max_s_i = 0.70; break;
            case COMP_CAP_CERAMIC_X7R:      lim.max_s_v = 0.70; lim.max_s_p = 0.70; lim.max_s_i = 0.75; break;
            case COMP_CAP_ALU_ELECTROLYTIC: lim.max_s_v = 0.80; lim.max_s_p = 0.70; lim.max_s_i = 0.75; lim.max_tj = 105.0; break;
            case COMP_SEMICONDUCTOR_MOSFET: lim.max_s_v = 0.80; lim.max_s_p = 0.65; lim.max_s_i = 0.75; lim.max_tj = 120.0; break;
            case COMP_SEMICONDUCTOR_DIODE:  lim.max_s_v = 0.80; lim.max_s_p = 0.70; lim.max_s_i = 0.70; break;
            case COMP_INDUCTOR_POWER:       lim.max_s_v = 0.85; lim.max_s_p = 0.70; lim.max_s_i = 0.80; break;
        }
    } else { /* STANDARD_COMMERCIAL */
        lim.max_tj = 130.0;
        lim.max_s_v = 0.90;
        lim.max_s_i = 0.85;
        lim.max_s_p = 0.80;
    }
    return lim;
}

DeratingResult evaluate_derating(const ComponentRating *rat, const OperatingCondition *op, DeratingStandard std) {
    DeratingResult res = { true, 0.0, 0.0, 0.0, 0.0, 0.0, "OK" };
    StandardLimits lim = get_limits(rat->type, std);

    /* 1. Розрахунок коефіцієнтів напруги та струму */
    res.s_v = (rat->v_rated > 0.0) ? (op->v_actual_peak / rat->v_rated) : 0.0;
    res.s_i = (rat->i_rated > 0.0) ? (op->i_actual_rms / rat->i_rated) : 0.0;

    /* 2. Температурний спад паспортної потужності */
    double p_nominal_at_temp = rat->p_rated;
    if (op->ta_ambient > rat->t_knee) {
        if (op->ta_ambient >= rat->t_max) {
            p_nominal_at_temp = 0.0;
        } else {
            p_nominal_at_temp = rat->p_rated * ((rat->t_max - op->ta_ambient) / (rat->t_max - rat->t_knee));
        }
    }

    /* Дератована допустима потужність */
    res.p_allowed_derated = p_nominal_at_temp * lim.max_s_p;
    res.s_p = (p_nominal_at_temp > 0.0) ? (op->p_actual_diss / p_nominal_at_temp) : 999.0;

    /* 3. Розрахунок температури переходу */
    res.tj_actual = op->ta_ambient + (op->p_actual_diss * rat->rth_ja);

    /* 4. Перевірка відповідності нормам */
    if (res.s_v > lim.max_s_v) {
        res.passed = false;
        res.failure_reason = "Перевищення допустимого коефіцієнта напруги (Voltage Overstress)";
    } else if (res.s_i > lim.max_s_i) {
        res.passed = false;
        res.failure_reason = "Перевищення допустимого коефіцієнта струму (Current Overstress)";
    } else if (op->p_actual_diss > res.p_allowed_derated) {
        res.passed = false;
        res.failure_reason = "Перевищення дератованої потужності (Thermal Power Overstress)";
    } else if (res.tj_actual > lim.max_tj) {
        res.passed = false;
        res.failure_reason = "Перевищення дератованої температури кристала Tj";
    }

    return res;
}

int main(void) {
    ComponentRating mosfet = {
        .designator = "Q1_PowerMOS",
        .type = COMP_SEMICONDUCTOR_MOSFET,
        .v_rated = 60.0,       /* 60 В */
        .i_rated = 40.0,       /* 40 А */
        .p_rated = 45.0,       /* 45 Вт при 25 °C */
        .t_knee = 25.0,
        .t_max = 150.0,
        .rth_ja = 2.8          /* Радіатор на платі */
    };

    OperatingCondition op = {
        .v_actual_peak = 48.0, /* 48 В у колі 24 В при індуктивному комутаційному викиді */
        .i_actual_rms = 18.0,  /* 18 А робочий струм */
        .p_actual_diss = 12.0, /* 12 Вт розсіюваної потужності */
        .ta_ambient = 65.0     /* +65 °C всередині корпусу */
    };

    printf("=== АУДИТ ДЕРАТИНГУ ДЛЯ %s ===\n", mosfet.designator);
    DeratingResult res_mil = evaluate_derating(&mosfet, &op, STANDARD_MIL_HDBK_338B);
    printf("[MIL-HDBK-338B] Статус: %s | S_v: %.2f (max 0.75) | Tj: %.1f C (max 110 C) | Причина: %s\n",
           res_mil.passed ? "ВІДПОВІДАЄ" : "ДЕФЕКТ", res_mil.s_v, res_mil.tj_actual, res_mil.failure_reason);

    DeratingResult res_ipc = evaluate_derating(&mosfet, &op, STANDARD_IPC_9592B_CLASS2);
    printf("[IPC-9592B-Cl2]  Статус: %s | S_v: %.2f (max 0.80) | Tj: %.1f C (max 120 C) | Причина: %s\n",
           res_ipc.passed ? "ВІДПОВІДАЄ" : "ДЕФЕКТ", res_ipc.s_v, res_ipc.tj_actual, res_ipc.failure_reason);

    return 0;
}
```
```cpp
#include <iostream>
#include <string_view>
#include <vector>
#include <iomanip>
#include <algorithm>

enum class Standard {
    MilHdbk338B,
    Ipc9592BClass2,
    Commercial
};

enum class ComponentType {
    ResistorFilm,
    CapCeramicX7R,
    CapTantalumMnO2,
    CapAluElectrolytic,
    SemiconductorMosfet,
    SemiconductorDiode,
    InductorPower
};

struct ComponentRating {
    std::string_view designator;
    ComponentType type;
    double v_rated;        // В
    double i_rated;        // А
    double p_rated;        // Вт
    double t_knee;         // °C
    double t_max;          // °C
    double rth_ja;         // °C/Вт
};

struct OperatingCondition {
    double v_actual_peak;  // В
    double i_actual_rms;   // А
    double p_actual_diss;  // Вт
    double ta_ambient;     // °C
};

struct StandardLimits {
    double max_s_v;
    double max_s_i;
    double max_s_p;
    double max_tj;
};

struct DeratingReport {
    bool passed{true};
    double s_v{0.0};
    double s_i{0.0};
    double s_p{0.0};
    double tj_actual{0.0};
    double p_allowed_derated{0.0};
    std::string_view violation_reason{"OK"};
};

class DeratingAuditor {
public:
    static constexpr StandardLimits get_limits(ComponentType type, Standard std) noexcept {
        if (std == Standard::MilHdbk338B) {
            switch (type) {
                case ComponentType::ResistorFilm:        return { 0.70, 0.70, 0.50, 105.0 };
                case ComponentType::CapTantalumMnO2:    return { 0.50, 0.50, 0.50, 105.0 };
                case ComponentType::CapCeramicX7R:      return { 0.60, 0.70, 0.60, 105.0 };
                case ComponentType::CapAluElectrolytic: return { 0.70, 0.70, 0.50, 85.0 };
                case ComponentType::SemiconductorMosfet: return { 0.75, 0.70, 0.50, 110.0 };
                case ComponentType::SemiconductorDiode:  return { 0.70, 0.50, 0.50, 105.0 };
                case ComponentType::InductorPower:       return { 0.80, 0.70, 0.60, 105.0 };
            }
        } else if (std == Standard::Ipc9592BClass2) {
            switch (type) {
                case ComponentType::ResistorFilm:        return { 0.80, 0.80, 0.65, 115.0 };
                case ComponentType::CapTantalumMnO2:    return { 0.50, 0.70, 0.65, 115.0 };
                case ComponentType::CapCeramicX7R:      return { 0.70, 0.75, 0.70, 115.0 };
                case ComponentType::CapAluElectrolytic: return { 0.80, 0.75, 0.70, 105.0 };
                case ComponentType::SemiconductorMosfet: return { 0.80, 0.75, 0.65, 120.0 };
                case ComponentType::SemiconductorDiode:  return { 0.80, 0.70, 0.70, 115.0 };
                case ComponentType::InductorPower:       return { 0.85, 0.80, 0.70, 115.0 };
            }
        }
        return { 0.90, 0.85, 0.80, 130.0 }; // Commercial
    }

    static DeratingReport evaluate(const ComponentRating& rat, const OperatingCondition& op, Standard std) noexcept {
        DeratingReport report{};
        const auto limits = get_limits(rat.type, std);

        report.s_v = (rat.v_rated > 0.0) ? (op.v_actual_peak / rat.v_rated) : 0.0;
        report.s_i = (rat.i_rated > 0.0) ? (op.i_actual_rms / rat.i_rated) : 0.0;

        double p_nominal_at_temp = rat.p_rated;
        if (op.ta_ambient > rat.t_knee) {
            if (op.ta_ambient >= rat.t_max) {
                p_nominal_at_temp = 0.0;
            } else {
                p_nominal_at_temp = rat.p_rated * ((rat.t_max - op.ta_ambient) / (rat.t_max - rat.t_knee));
            }
        }

        report.p_allowed_derated = p_nominal_at_temp * limits.max_s_p;
        report.s_p = (p_nominal_at_temp > 0.0) ? (op.p_actual_diss / p_nominal_at_temp) : 999.0;
        report.tj_actual = op.ta_ambient + (op.p_actual_diss * rat.rth_ja);

        if (report.s_v > limits.max_s_v) {
            report.passed = false;
            report.violation_reason = "Voltage limit exceeded";
        } else if (report.s_i > limits.max_s_i) {
            report.passed = false;
            report.violation_reason = "Current limit exceeded";
        } else if (op.p_actual_diss > report.p_allowed_derated) {
            report.passed = false;
            report.violation_reason = "Thermal derated power exceeded";
        } else if (report.tj_actual > limits.max_tj) {
            report.passed = false;
            report.violation_reason = "Junction temperature Tj exceeded";
        }

        return report;
    }
};

int main() {
    const ComponentRating mosfet{
        "Q1_PowerMOS",
        ComponentType::SemiconductorMosfet,
        60.0, 40.0, 45.0, 25.0, 150.0, 2.8
    };

    const OperatingCondition op{
        48.0, 18.0, 12.0, 65.0
    };

    std::cout << "=== АУДИТ ДЕРАТИНГУ (C++) ДЛЯ " << mosfet.designator << " ===\n";

    const auto report_mil = DeratingAuditor::evaluate(mosfet, op, Standard::MilHdbk338B);
    std::cout << "[MIL-HDBK-338B] Статус: " << (report_mil.passed ? "ВІДПОВІДАЄ" : "ДЕФЕКТ")
              << " | S_v: " << std::fixed << std::setprecision(2) << report_mil.s_v
              << " | Tj: " << std::setprecision(1) << report_mil.tj_actual << " C"
              << " | Причина: " << report_mil.violation_reason << "\n";

    const auto report_ipc = DeratingAuditor::evaluate(mosfet, op, Standard::Ipc9592BClass2);
    std::cout << "[IPC-9592B-Cl2]  Статус: " << (report_ipc.passed ? "ВІДПОВІДАЄ" : "ДЕФЕКТ")
              << " | S_v: " << std::fixed << std::setprecision(2) << report_ipc.s_v
              << " | Tj: " << std::setprecision(1) << report_ipc.tj_actual << " C"
              << " | Причина: " << report_ipc.violation_reason << "\n";

    return 0;
}
```
:::

## Інженерний аналіз результатів та інтеграція в EDA-процеси

За результатами тестового запуску для силового транзистора `Q1` (`V_ds_rated = 60 В`, пікова робоча напруга `48 В`, розсіювана потужність `12 Вт` при `Ta = +65 °C`):

1. **Військовий профіль MIL-HDBK-338B фіксує дефект:**
   Фактичний коефіцієнт напруги `S_V = 48 / 60 = 0.80` перевищує гранично допустиму норму `0.75` (максимум `45 В`). Розрахована температура кристала `T_j = 65 + 12 · 2.8 = 98.6 °C` укладається в межу `+110 °C`, але напругове перевантаження загрожує лавинним пробоєм під час індуктивних викидів. Інженеру необхідно замінити транзистор на модель з робочою напругою `V_ds ≥ 80 В` або `100 В` (для транзистора на 100 В коефіцієнт стресу складе безпечні `S_V = 0.48`).

2. **Промисловий профіль IPC-9592B Class 2 схвалює режим:**
   Допустимий поріг за напругою для телекомунікаційного обладнання становить `0.80`, а температурна стеля — `+120 °C`. Режим вважається допустимим, проте запас за напругою є граничним і не залишає простору для випадкових сплесків вхідної лінії.

### Підводні камені та типові схемотехнічні пастки:
- **Паразитна індуктивність монтажу:** Пікова напруга на транзисторі `V_peak = V_in + L_par · (di/dt)`. При швидкому вимиканні струму 20 А за 10 нс паразитна індуктивність доріжки всього 10 нГн додає сплеск `10 · 10⁻⁹ · (20 / 10 · 10⁻⁹) = 20 В` до напруги живлення! Якщо інженер бере в розрахунок лише стаціонарні 24 В, транзистор згорає в перші мікросекунди комутації.
- **Ефект падіння ємності керамічних конденсаторів (DC-Bias):** Для кераміки X7R/X5R напруговий дератинг критичний не лише для надійності діелектрика, а й для збереження самої ємності: при `V_work = 0.8 · V_rated` ємність може впасти на 70 %, що призведе до зриву стабільності зворотного зв'язку перетворювача.
- **Взаємний тепловий вплив суміжних компонентів:** Значення `R_th_ja` з даташита вимірюється на стандартизованій тестовій платі JEDEC без сусідніх джерел тепла. У реальній щільній компоновці розігрів сусіднього дроселя або трансформатора піднімає локальну температуру повітря `Ta` біля мікросхеми на 20–30 °C, вимагаючи введення поправочних матриць теплового зв'язку.
- **Імпульсні режими та теплова ємність кристала:** Для коротких імпульсів потужності тривалістю менше 10 мс перегрів кристала обмежується не стаціонарним `R_th_ja`, а динамічним тепловим імпедансом `Z_th_jc(t)`. У таких режимах дератинг розраховується за кривими перехідного теплового опору (Transient Thermal Impedance Curves).
- **Автоматизація парсингу SPICE `.raw` файлів:** Модуль легко доповнюється функцією зчитування текстових звітів аналізу перехідних процесів (SPICE Transient Analysis), автоматично витягуючи максимальні пікові значення напруг `V(node_a, node_b)` та інтегруючи миттєву потужність `P(t) = V(t) · I(t)` для знаходження середньоквадратичного струму і середньої потужності за період комутації.
