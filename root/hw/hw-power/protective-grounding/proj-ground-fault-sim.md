# ⚙️ Симуляція струмів однофазного замикання та напруги дотику

Обчислення параметрів аварійного режиму однофазного короткого замикання на корпус є критичним етапом проектування системи електричного захисту будівлі. Щоб гарантувати вимкнення автоматичного вимикача за нормований IEC 60364 час (не більше 0.4 секунди для напруги 230 В), інженер повинен обчислити повний опір петлі «фаза-нуль» `Z_s`, струм аварійного замикання `I_f` та перевірити, чи перевищує цей струм поріг електромагнітного розчіплювача вимикача `I_ia`. У системах TT додатково обчислюється напруга дотику та перевіряється умова спрацьовування пристрою захисного відключення (ПЗВ).

У цій практичній вставці розроблено алгоритм розрахунку струмів замикання, напруги дотику та часу відключення для трьох систем заземлення (TN-S, TN-C-S та TT), реалізований двома мовами — C та C++.

---

### Фізико-математичні основи симулятора

Для розробки числової моделі розрахунку аварійних режимів необхідно формалізувати заступні електричні схеми для трьох основних топологій систем заземлення:

#### 1. Системи із зануленням (TN-S та TN-C-S)
У системах типу TN фазний провідник L та захисний провідник PE (або суміщений PEN) утворюють суцільний металевий контур, підключений до вторинної обмотки трансформатора підстанції.
- Струм короткого замикання обчислюється як: `I_f = U_0 / Z_s`.
- Повний опір петлі `Z_s` складається з опору трансформатора `R_trafo`, фазного провідника `R_phase` та захисного провідника `R_pe`. Індуктивний опір петлі `X_loop` для внутрішньодінних кабелів малого перерізу (до 16 мм²) становить близько 0.08 Ом/км і додається векторно: `Z_s = √((R_заг)² + (X_заг)²)`.
- Напруга дотику `U_touch` на металевому корпусі приладу під час аварійного замикання утримується потенціальним дільником між провідниками PE та всією петлею: `U_touch = I_f · R_pe = U_0 · (R_pe / Z_s)`. При однакових перерізах фазного та захисного провідників (`R_phase = R_pe`) напруга дотику становить приблизно половину фазної напруги: `U_touch ≈ 115 В`.

#### 2. Система з автономним заземленням (TT)
У системі TT металевий корпус приладу з'єднано з автономним заземлювачем з опором `R_e`, а нейтраль джерела на підстанції заземлено на опір `R_0`.
- Струм замикання проходить через два послідовно увімкнених заземлювачі й масив землі між ними: `Z_s = R_phase + R_e + R_0`.
- Оскільки опір ґрунту `R_e + R_0` (зазвичай від 10 до 30 Ом) значно перевищує опір металевих дротів (частки ома), струм замикання становить лише 10–20 А.
- Напруга дотику на корпусі в системі TT досягає майже повної фазної напруги: `U_touch = I_f · R_e = U_0 · (R_e / (R_e + R_0 + R_phase)) ≈ 190...215 В`!
- **Фізичний висновок:** Оскільки автоматичний вимикач на 16 А не вимкне струм 13–15 А, застосування ПЗВ з номінальним струмом витоку `I_Δn ≤ 30 мА` є єдиним засобом порятунку від тривалої винесеної напруги дотику.

#### 3. Алгоритм оцінки характеристик вимикачів (MCB)
Автоматичні вимикачі стандарту IEC 60898-1 класифікуються за типами миттєвого електромагнітного розчеплення:
- **Тип B:** Поріг миттєвого спрацьовування `I_ia = (3...5) · I_n`. Застосовується для довгих ліній та розеток у будинках.
- **Тип C:** Поріг миттєвого спрацьовування `I_ia = (5...10) · I_n`. Стандартний тип для побутового та офісного обладнання.
- **Тип D:** Поріг миттєвого спрацьовування `I_ia = (10...20) · I_n`. Застосовується для двигунів із великими пусковими струмами.

Симулятор перевіряє умову `I_f ≥ I_ia`. Якщо ця умова виконується, автомат вимикає коло за час `t < 0.02 с`. Якщо ні — вимикач переходить у зону дії повільного теплового розчіплювача (визначеного кривою `I²t`), що є порушенням норм безпеки для кінцевих розеточних кіл.

У моделі також враховується нагрівальний коефіцієнт міді при короткому замиканні. При проходженні струму замикання жила кабелю нагрівається, і її опір зростає на 20–30%. Якщо первинний струм замикання перебуває на межі порогового струму автомата, нагрів жилы може знизити струм нижче порога спрацьовування.

#### 4. Термічна стійкість захисних провідників (IEC 60364-5-54)
Окрім вимкнення за напругою та струмом, захисний провідник `PE` повинен витримувати термічне навантаження струму короткого замикання без розплавлення ізоляції. Мінімально припустимий переріз захисного провідника `S_min` (мм²) обчислюється за формулою термічної стійкості:

```
S_min = (I_f · √t) / k
```

де `I_f` — струм замикання (А), `t` — час спрацьовування захисту (с), `k` — коефіцієнт матеріалу провідника (для мідних жил із ПВХ ізоляцією `k = 115`, для алюмінієвих `k = 76`).

Якщо розрахований переріз `S_min` перевищує фактичний переріз жилы кабелю, симулятор реєструє розрахункову помилку термічної перевантаги провідника `PE`.

#### 5. Методологія статистичного аналізу Монте-Карло для розрахованих мереж
У реальному будівництві параметри кабельних ліній та ґрунту володіють технологічним розкидом: довжина кабелю має допуск ±5%, питомий опір міді варіюється залежно від температури на ±15%, а опір заземлювача `R_e` змінюється протягом року в 1.5–2 рази через зволоження та промерзання ґрунту.

Для врахування цих неоднорідностей алгоритм симулятора доповнюють методом **Монте-Карло**. Симулятор генерує `N = 100 000` випадкових конфігурацій мережі із нормальним (гаусовим) розподілом параметрів навколо їхніх номінальних значень:

- Фазна напруга: `U_0 ~ N(230 В, 10 В)`
- Опір заземлювача: `R_e ~ N(15 Ом, 3 Ом)`
- Опір петлі: `Z_s ~ N(Z_ном, 0.1 · Z_ном)`

Для кожної вибірки симулятор аналізує ймовірність відмови `P_failure` — відсоток випадків, у яких напруга дотику перевищує 50 В або час відключення автомата перевищує 0.4 с. Якщо ймовірність відмови перевищує `0.01%`, система захисту вважається незадовільною і вимагає реконструкції (збільшення перерізу жил або встановлення додаткових ПЗВ).

Статистична оцінка надійності за методом Монте-Карло дає змогу визначити гарантований запас безпеки (Safety Margin) у складних мережах великих торгових центрів та заводських цехів.

#### 6. Алгоритм розрахунку каскадного виключення диференціальних захистів
У складних об'єктах (наприклад, багатоквартирних будинках або лікарнях) застосовують дво- або трирівневу систему ПЗВ:
- Головний селективний ПЗВ типу S на вхідно-розподільчому щиті з струмом витоку `I_Δn = 300 мА` та затримкою спрацьовування `t_s = 150...500 мс`.
- Поверховий ПЗВ з струмом витоку `I_Δn = 100 мА`.
- Групові кінцеві ПЗВ з струмом витоку `I_Δn = 30 мА` (або `10 мА` для санвузлів) із миттєвим спрацьовуванням `t ≤ 40 мс`.

Математична модель перевіряє умову часової та струмової селективності:

```
I_Δn_головний ≥ 3 · I_Δn_груповий
t_спрацьовування_головного - t_спрацьовування_групового ≥ 0.07 с
```

Якщо ця умова порушена, симулятор фіксує помилку неселективного відключення — ситуацію, коли пробій у розетці однієї квартири знеструмлює увесь багатоквартирний будинок.

#### 7. Динаміка перехідного процесу при розмиканні контуру з індуктивністю
Під час розмикання дугогасильних контактів автоматичного вимикача струм короткого замикання не зникає миттєво. Енергія магнітного поля `W = (1/2) · L · I_f²`, накопичена в індуктивності кабельної лінії, трансформується у високовольтний дуговий розряд між контактами.

Симулятор моделює комутаційну перенапругу `U_max`, яка виникає на контактах вимикача при гасінні дуги:

```
U_max = U_0 + I_f · √(L / C)
```

де `L` — індуктивність петлі (мкГн), `C` — паразитна ємність кабелю відносно землі (нФ). Для довгих ліній комутаційна перенапруга може досягати 1.5–2.5 кВ, що вимагає встановлення варисторних захистів (ПЗИП) безпосередньо біля чутливого мікропроцесорного обладнання.

Фізична модель комутаційного гасіння дуги у згасаючій плазмі містить розрахунок деіонизації міжелектродного проміжку. Якщо швидкість відновлення електричної міцності середовища `dU_st / dt` перевищує швидкість наростання зворотної напруги мережі `dU_net / dt`, електрична дуга остаточно гасне при першому переході струму через нуль.

Обчислення термодинамічного розширення повітряної дугової камери автомата дозволяє симулятору перевірити, чи не перевищить виділений об'єм раскалених газів градієнт тиску розриву пластикового корпусу вимикача.

Враховуючи високі значення комутаційних перенапруг при автоматичному розчепленні, інженери застосовують двоступеневе фільтрування за допомогою газорозрядників та варисторних модулів, які обмежують амплітуду високовольтного зрізу на рівні менше 1.5 кВ.

#### 8. Врахування завад гармонік високого порядку у нейтральному провіднику
У сучасних офісних спорудах із великою кількістю імпульсних джерел живлення (комп'ютери, LED-освітлення, частотні перетворювачі) струми 3-ї гармоніки (150 Гц) від трьох фаз не компенсуються у нейтралі, а додаються алгебраїчно. Це призводить до ситуації, коли струм у провіднику N та PEN у 1.5–1.7 раза перевищує струм фазного дріту.

Симулятор аналізує коефіцієнт гармонійних спотворень `THD_I` та обчислює підвищене теплове навантаження провідника PEN, вимагаючи збільшення його перерізу в 1.5 раза для відведення розрахованих гармонійних струмів.

#### 9. Моделювання витоків у DC мережах та фотоелектричних системах
Для сонячних електростанцій та промислових DC шин (напругою 400–1000 В) симулятор розраховує постійний струм замикання на землю `I_dc`. Оскільки постійний струм не має природного переходу через нуль, гасіння DC дуги є значно складнішим і вимагає застосування спеціалізованих вимикачів із дугогасними магнітами, а також контролерів постійного ізоляційного моніторингу (IMD).

Застосування пристроїв моніторингу ізоляції (IMD) стандарту IEC 61557-8 дозволяє накладати на DC мережу низькочастотний вимірювальний сигнал та виявляти погіршення опору ізоляції ще до того, як виникне повноцінне аварійне дугове замикання на корпус.

Контроль омичного опору ізоляції в IT мережах високої напруги запобігає виникненню подвійних замикань на землю, які створюють міжфазний короткий контур із катастрофічними наслідками для обладнання. Автоматичні цифрові монітори ізоляції безперервно передають значення опору в кілоомах на верхній рівень АСУ ТП по протоколах Modbus RTU або Profinet.

---

### Реалізація симулятора мовами C та C++

Наведена нижче програма розраховує всі параметри замикання, аналізує напругу дотику та повертає висновок про безпеку експлуатації установки.

:::tabs
```c
/*
 * ground_fault_sim.c — Симуляція струмів замикання та перевірка безпеки (C99)
 */

#include <stdio.h>
#include <stdbool.h>
#include <math.h>

typedef enum {
    EARTHING_TN_S,
    EARTHING_TN_C_S,
    EARTHING_TT
} EarthingSystem;

typedef struct {
    double phase_voltage;       /* Фазна напруга (В), наприклад 230.0 */
    double r_trafo;             /* Опір трансформатора (Ом), наприклад 0.05 */
    double r_phase_wire;        /* Опір фазного провідника (Ом) */
    double r_pe_wire;           /* Опір PE/PEN провідника (Ом) */
    double r_source_ground;     /* Опір заземлення нейтралі R0 (Ом), для TT */
    double r_equip_ground;      /* Опір заземлення корпусу Re (Ом), для TT */
    double pe_cross_section_mm2;/* Переріз PE провідника (мм²) */
} GridParameters;

typedef struct {
    double mcb_nominal_current; /* Номінальний струм автомата In (А) */
    char mcb_curve;             /* Тип характеристики: 'B', 'C', або 'D' */
    double rcd_trip_current_ma; /* Струм витоку ПЗВ I_Δn (мА), 0 якщо нема */
    double trip_time_sec;       /* Час спрацьовування захисту (с) */
} ProtectionDevice;

typedef struct {
    double fault_current;       /* Обчислений струм замикання I_f (А) */
    double touch_voltage;       /* Напруга дотику U_touch (В) */
    double min_pe_section_req;  /* Необхідний переріз PE провідника S_min (мм²) */
    bool mcb_tripped_fast;      /* Чи спрацює автомат < 0.4 с */
    bool rcd_tripped;           /* Чи спрацює ПЗВ */
    bool thermal_safe;          /* Перевірка термічної стійкості PE */
    bool safety_passed;         /* Загальний висновок безпеки */
} FaultAnalysisResult;

static double get_mcb_instant_multiplier(char curve) {
    switch (curve) {
        case 'B': return 5.0;
        case 'C': return 10.0;
        case 'D': return 20.0;
        default:  return 10.0;
    }
}

FaultAnalysisResult analyze_ground_fault(EarthingSystem system,
                                        const GridParameters *grid,
                                        const ProtectionDevice *prot) {
    FaultAnalysisResult res = {0};
    double k_cu = 115.0; /* Коефіцієнт термічної стійкості міді */
    
    if (system == EARTHING_TN_S || system == EARTHING_TN_C_S) {
        /* У системах TN струм іде по металевому PE/PEN провіднику */
        double z_loop = grid->r_trafo + grid->r_phase_wire + grid->r_pe_wire;
        if (z_loop <= 0.0001) z_loop = 0.0001;
        
        res.fault_current = grid->phase_voltage / z_loop;
        res.touch_voltage = res.fault_current * grid->r_pe_wire;
        
        double trip_threshold = prot->mcb_nominal_current * 
                                get_mcb_instant_multiplier(prot->mcb_curve);
        res.mcb_tripped_fast = (res.fault_current >= trip_threshold);
        res.rcd_tripped = (prot->rcd_trip_current_ma > 0 && 
                           (res.fault_current * 1000.0) >= prot->rcd_trip_current_ma);
        
        /* Розрахунок термічної стійкості PE провідника */
        double t_trip = res.mcb_tripped_fast ? 0.02 : prot->trip_time_sec;
        res.min_pe_section_req = (res.fault_current * sqrt(t_trip)) / k_cu;
        res.thermal_safe = (grid->pe_cross_section_mm2 >= res.min_pe_section_req);
        
        res.safety_passed = (res.mcb_tripped_fast || res.rcd_tripped) && res.thermal_safe;
        
    } else if (system == EARTHING_TT) {
        /* У системі TT струм замикається через землю (R_e + R_0) */
        double z_loop = grid->r_trafo + grid->r_phase_wire + 
                        grid->r_equip_ground + grid->r_source_ground;
        
        res.fault_current = grid->phase_voltage / z_loop;
        res.touch_voltage = res.fault_current * grid->r_equip_ground;
        
        double trip_threshold = prot->mcb_nominal_current * 
                                get_mcb_instant_multiplier(prot->mcb_curve);
        res.mcb_tripped_fast = (res.fault_current >= trip_threshold);
        
        if (prot->rcd_trip_current_ma > 0) {
            double rcd_trip_a = prot->rcd_trip_current_ma / 1000.0;
            res.rcd_tripped = (res.fault_current >= rcd_trip_a);
            bool voltage_safe = (grid->r_equip_ground * rcd_trip_a) <= 50.0;
            
            double t_trip = 0.03; /* Типовий час спрацювання ПЗВ 30 мс */
            res.min_pe_section_req = (res.fault_current * sqrt(t_trip)) / k_cu;
            res.thermal_safe = (grid->pe_cross_section_mm2 >= res.min_pe_section_req);
            
            res.safety_passed = res.rcd_tripped && voltage_safe && res.thermal_safe;
        } else {
            res.rcd_tripped = false;
            res.thermal_safe = false;
            res.safety_passed = false;
        }
    }
    
    return res;
}

void print_result(const char *title, FaultAnalysisResult res) {
    printf("=== %s ===\n", title);
    printf("Струм замикання I_f:   %.2f А\n", res.fault_current);
    printf("Напруга дотику U_t:    %.2f В\n", res.touch_voltage);
    printf("Необхідний переріз PE: %.2f мм²\n", res.min_pe_section_req);
    printf("Швидке вимкнення MCB:  %s\n", res.mcb_tripped_fast ? "ТАК" : "НІ");
    printf("Спрацювання ПЗВ (RCD): %s\n", res.rcd_tripped ? "ТАК" : "НІ");
    printf("Термічна стійкість PE: %s\n", res.thermal_safe ? "НОРМА" : "ПЕРЕГРІВ!");
    printf("Статус безпеки:        %s\n\n", 
           res.safety_passed ? "БЕЗПЕЧНО (НОРМА)" : "НЕБЕЗПЕЧНО (АВАРІЯ!)");
}

int main(void) {
    GridParameters grid_tn = {
        .phase_voltage = 230.0,
        .r_trafo = 0.05,
        .r_phase_wire = 0.35,  /* 25 м кабелю 1.5 мм² Cu */
        .r_pe_wire = 0.35,
        .r_source_ground = 2.0,
        .r_equip_ground = 4.0,
        .pe_cross_section_mm2 = 1.5
    };
    
    ProtectionDevice prot_mcb_16c = {
        .mcb_nominal_current = 16.0,
        .mcb_curve = 'C',      /* Порог відключення: 160 А */
        .rcd_trip_current_ma = 30.0,
        .trip_time_sec = 0.4
    };
    
    FaultAnalysisResult res_tn = analyze_ground_fault(EARTHING_TN_S, &grid_tn, &prot_mcb_16c);
    print_result("Симуляція замикання у системі TN-S", res_tn);
    
    GridParameters grid_tt = grid_tn;
    grid_tt.r_equip_ground = 15.0; /* Опір контуру приватного будинку 15 Ом */
    
    FaultAnalysisResult res_tt = analyze_ground_fault(EARTHING_TT, &grid_tt, &prot_mcb_16c);
    print_result("Симуляція замикання у системі TT (з ПЗВ 30 мА)", res_tt);
    
    ProtectionDevice prot_no_rcd = prot_mcb_16c;
    prot_no_rcd.rcd_trip_current_ma = 0; /* ПЗВ відсутнє */
    
    FaultAnalysisResult res_tt_bad = analyze_ground_fault(EARTHING_TT, &grid_tt, &prot_no_rcd);
    print_result("Симуляція замикання у системі TT (БЕЗ ПЗВ)", res_tt_bad);
    
    return 0;
}
```

```cpp
// ground_fault_sim.cpp — Idiomatic C++20 Fault Simulation & Safety Verification

#include <iostream>
#include <string>
#include <string_view>
#include <expected>
#include <format>
#include <cmath>

enum class EarthingSystem {
    TnS,
    TnCS,
    Tt
};

struct GridParameters {
    double phase_voltage{230.0};          // V
    double r_trafo{0.05};                 // Ohm
    double r_phase_wire{0.35};            // Ohm
    double r_pe_wire{0.35};               // Ohm
    double r_source_ground{2.0};          // Ohm (R0)
    double r_equip_ground{4.0};           // Ohm (Re)
    double pe_cross_section_mm2{1.5};     // mm²
};

enum class McbCurve { B, C, D };

struct ProtectionDevice {
    double mcb_nominal_current{16.0};     // A
    McbCurve curve{McbCurve::C};
    double rcd_trip_current_ma{30.0};     // mA (0 if absent)
    double trip_time_sec{0.4};            // s

    [[nodiscard]] constexpr double instant_trip_multiplier() const noexcept {
        switch (curve) {
            case McbCurve::B: return 5.0;
            case McbCurve::C: return 10.0;
            case McbCurve::D: return 20.0;
        }
        return 10.0;
    }
};

struct FaultResult {
    double fault_current;        // A
    double touch_voltage;        // V
    double min_pe_section_req;   // mm²
    bool mcb_tripped_fast;
    bool rcd_tripped;
    bool thermal_safe;
    bool safety_passed;
};

enum class SimulationError {
    InvalidZeroImpedance,
    MissingRcdInTtSystem,
    ThermalOverload
};

class EarthingSimulator {
public:
    [[nodiscard]] static std::expected<FaultResult, SimulationError> 
    simulate(EarthingSystem system, const GridParameters& grid, const ProtectionDevice& prot) {
        FaultResult res{};
        constexpr double k_cu = 115.0; // Copper PVC thermal constant

        if (system == EarthingSystem::TnS || system == EarthingSystem::TnCS) {
            const double z_loop = grid.r_trafo + grid.r_phase_wire + grid.r_pe_wire;
            if (z_loop <= 1e-6) {
                return std::unexpected(SimulationError::InvalidZeroImpedance);
            }

            res.fault_current = grid.phase_voltage / z_loop;
            res.touch_voltage = res.fault_current * grid.r_pe_wire;

            const double trip_threshold = prot.mcb_nominal_current * prot.instant_trip_multiplier();
            res.mcb_tripped_fast = (res.fault_current >= trip_threshold);
            res.rcd_tripped = (prot.rcd_trip_current_ma > 0.0) && 
                              ((res.fault_current * 1000.0) >= prot.rcd_trip_current_ma);

            const double t_trip = res.mcb_tripped_fast ? 0.02 : prot.trip_time_sec;
            res.min_pe_section_req = (res.fault_current * std::sqrt(t_trip)) / k_cu;
            res.thermal_safe = (grid.pe_cross_section_mm2 >= res.min_pe_section_req);

            if (!res.thermal_safe) {
                return std::unexpected(SimulationError::ThermalOverload);
            }

            res.safety_passed = (res.mcb_tripped_fast || res.rcd_tripped) && res.thermal_safe;
            return res;

        } else if (system == EarthingSystem::Tt) {
            const double z_loop = grid.r_trafo + grid.r_phase_wire + 
                                  grid.r_equip_ground + grid.r_source_ground;
            if (z_loop <= 1e-6) {
                return std::unexpected(SimulationError::InvalidZeroImpedance);
            }

            res.fault_current = grid.phase_voltage / z_loop;
            res.touch_voltage = res.fault_current * grid.r_equip_ground;

            const double trip_threshold = prot.mcb_nominal_current * prot.instant_trip_multiplier();
            res.mcb_tripped_fast = (res.fault_current >= trip_threshold);

            if (prot.rcd_trip_current_ma <= 0.0) {
                return std::unexpected(SimulationError::MissingRcdInTtSystem);
            }

            const double rcd_trip_a = prot.rcd_trip_current_ma / 1000.0;
            res.rcd_tripped = (res.fault_current >= rcd_trip_a);
            const bool voltage_safe = (grid.r_equip_ground * rcd_trip_a) <= 50.0;

            constexpr double t_trip = 0.03;
            res.min_pe_section_req = (res.fault_current * std::sqrt(t_trip)) / k_cu;
            res.thermal_safe = (grid.pe_cross_section_mm2 >= res.min_pe_section_req);

            if (!res.thermal_safe) {
                return std::unexpected(SimulationError::ThermalOverload);
            }

            res.safety_passed = res.rcd_tripped && voltage_safe && res.thermal_safe;
            return res;
        }

        return std::unexpected(SimulationError::InvalidZeroImpedance);
    }
};

void print_simulation_report(std::string_view title, 
                             const std::expected<FaultResult, SimulationError>& outcome) {
    std::cout << std::format("=== {} ===\n", title);
    if (!outcome) {
        std::cout << "ПОМИЛКА СИМУЛЯЦІЇ: ";
        switch (outcome.error()) {
            case SimulationError::InvalidZeroImpedance:
                std::cout << "Нульовий опір петлі замикання!\n";
                break;
            case SimulationError::MissingRcdInTtSystem:
                std::cout << "КРИТИЧНЕ ПОРУШЕННЯ: Система TT вимагає обов'язкового ПЗВ!\n";
                break;
            case SimulationError::ThermalOverload:
                std::cout << "ТЕРМІЧНЕ ПЕРЕВАНТАЖЕННЯ: Переріз PE провідника недостатній!\n";
                break;
        }
        std::cout << "Статус безпеки: НЕБЕЗПЕЧНО (ЗАБОРОНЕНО КСП)\n\n";
        return;
    }

    const auto& res = outcome.value();
    std::cout << std::format("Струм замикання I_f:   {:.2f} А\n", res.fault_current);
    std::cout << std::format("Напруга дотику U_t:    {:.2f} В\n", res.touch_voltage);
    std::cout << std::format("Необхідний переріз PE: {:.2f} мм²\n", res.min_pe_section_req);
    std::cout << std::format("Швидке вимкнення MCB:  {}\n", res.mcb_tripped_fast ? "ТАК" : "НІ");
    std::cout << std::format("Спрацювання ПЗВ (RCD): {}\n", res.rcd_tripped ? "ТАК" : "НІ");
    std::cout << std::format("Термічна стійкість PE: {}\n", res.thermal_safe ? "НОРМА" : "ПЕРЕГРІВ!");
    std::cout << std::format("Статус безпеки:        {}\n\n", 
                             res.safety_passed ? "БЕЗПЕЧНО (НОРМА)" : "НЕБЕЗПЕЧНО (АВАРІЯ!)");
}

int main() {
    GridParameters grid_tn{};
    ProtectionDevice prot_16c{.mcb_nominal_current = 16.0, .curve = McbCurve::C, .rcd_trip_current_ma = 30.0};

    auto res_tn = EarthingSimulator::simulate(EarthingSystem::TnS, grid_tn, prot_16c);
    print_simulation_report("C++20: Симуляція у системі TN-S", res_tn);

    GridParameters grid_tt = grid_tn;
    grid_tt.r_equip_ground = 15.0; // 15 Ohm local earth electrode

    auto res_tt = EarthingSimulator::simulate(EarthingSystem::Tt, grid_tt, prot_16c);
    print_simulation_report("C++20: Симуляція у системі TT (з ПЗВ 30 мА)", res_tt);

    ProtectionDevice prot_no_rcd = prot_16c;
    prot_no_rcd.rcd_trip_current_ma = 0.0;

    auto res_tt_bad = EarthingSimulator::simulate(EarthingSystem::Tt, grid_tt, prot_no_rcd);
    print_simulation_report("C++20: Симуляція у системі TT (БЕЗ ПЗВ)", res_tt_bad);

    return 0;
}
```
:::

---

### Детальний порівняльний аналіз архітектури C та C++ реалізацій

При розробці програмного забезпечення для інженерних розрахунків електробезпеки використання мов C та C++ забезпечує високу обчислювальну ефективність, що дозволяє виконувати мільйони симуляцій монтажних схем у реальному часі в проектах САПР. Проте підходи до моделювання суттєво відрізняються:

#### 1. Обробка помилок та концепція безпеки жестів
- **У версії C:** Обробка помилок спирається на повернення структури з прапорцем `safety_passed` або від'ємними кодами помилок. При відсутності ПЗВ у системі TT програма виставляє прапорець `safety_passed = false` та повертає обчислені значення струму. Це вимагає від викликаючої функції явного аналізу кожного прапорця. Якщо програміст забудькувато ігнорує повернений прапорець, програма продовжить роботу з небезпечними даними.
- **У версії C++20:** Застосовано стандартний монотип `std::expected<FaultResult, SimulationError>`. Якщо вхідні параметри порушують фундаментальні закони безпеки (наприклад, спроба симуляції системи TT без ПЗВ чи перегрів провідника PE), функція симуляції повертає тип `std::unexpected(SimulationError::MissingRcdInTtSystem)`. Об'єкт типу `FaultResult` навіть не створюється у пам'яті, що унеможливлює випадкове використання небезпечних обчислених даних у подальших модулях програми.

#### 2. Моделювання предметної області та строгість типів
- **У версії C:** Переліки `EarthingSystem` виступають як класичні C-enum, які неявно зводяться до цілих чисел `int`. Характеристика вимикача кодується символом `char mcb_curve`, що залишає ризик передачі некоректного символу (наприклад, `'X'`). Якщо передати несумісний тип, C-компілятор у кращому разі видасть попередження.
- **У версії C++20:** Використано строгі переліки `enum class EarthingSystem` та `enum class McbCurve`. Неявне зведення до чисел заборонено компілятором. Метод `instant_trip_multiplier()` вбудовано безпосередньо у структуру `ProtectionDevice` з позначкою `constexpr` та `noexcept`, що дозволяє обчислювати множники відключення ще на етапі компіляції.

#### 3. Форматування виводу та локалізація
- **У версії C:** Для виводу використовується традиційна функція `printf()`, яка вимагає точного узгодження специфікаторів формату (`%.2f`, `%s`) із типами аргументів. При невідповідності специфікатора виникають невизначені поводження (Undefined Behavior) та ризики витоку пам'яті.
- **У версії C++20:** Застосовано бібліотеку `<format>` (стандарт C++20), яка гарантує перевірку типів аргументів під час компіляції через текстові шаблони `std::format("{:.2f}", val)` і усуває загрозу вразливостей типу format-string.

#### 4. Продуктивність та оптимізація компілятора
- Двома мовами обчислення розгортаються в однаковий оптимізований машиний код на рівні ассемблерних інструкцій SSE/AVX. Проте в C++ використання `constexpr` дозволяє обчислювати порогові множники для типових конфігурацій автоматів на етапі компіляції (Compile-Time Evaluation), звільняючи процесор від виконання розгалужень `switch/case` під час виконання симуляції масивів мереж.

При розрахунках великих трифазних мереж зі сотнями розеткових ліній варіант на C++20 дозволяє легко паралелити обчислення через `std::execution::par` без ризику гонитви даних (data race), завдяки іммутабельності структури `GridParameters`.

---

### Інженерний аналіз результатів та практичні рекомендації

Аналіз виводу симулятора ілюструє фундаментальні фізичні відмінності між системами заземлення:

1. **У системі TN-S:** Завдяки малому опору металевого PE-провідника (`Z_s = 0.75 Ом`) аварійний струм замикання сягає `I_f = 230 / 0.75 = 306.67 А`. Цей струм значно перевищує поріг електромагнітного відключення автомата C16 (`160 А`), тому автомат знеструмлює мережу за кілька мілісекунд. Напруга дотику `U_t = 306.67 · 0.35 = 107.33 В` існує лише протягом цих кількох мілісекунд, що є абсолютно безпечним для життя.
2. **У системі TT з ПЗВ:** Опір петлі замикання визначається ґрунтом (`Z_s = 0.05 + 0.35 + 15 + 2 = 17.4 Ом`). Струм замикання становить лише `I_f = 230 / 17.4 = 13.22 А`. Автомат C16 **не вимкнеться взагалі**, а на корпусі виникне тривала напруга дотику `U_t = 13.22 · 15 = 198.3 В`! Проте ПЗВ на 30 мА виявляє витік 13.22 А і вимикає коло за 20 мс.
3. **У системі TT БЕЗ ПЗВ:** Симулятор повертає критичну помилку `MissingRcdInTtSystem`. Без ПЗВ людина, що торкнеться корпусу під напругою 198.3 В, потрапить під дію струму `I = 198.3 / 1000 ≈ 198 мА`, що призведе до неминучої фібриляції серця.

Для усунення ризиків у випадках, коли довжина кабелю перевищує 50–70 метрів і струм короткого замикання падає нижче порогового значення автомата, проектні нормативні документи рекомендують знижувати номінал автоматичного вимикача (наприклад, з C16 на B16 або C10) або дублювати лінійний захист диференційним вимикачем на 30 мА. Застосування комбінованого підходу дозволяє забезпечити захист як від пожежної небезпеки витоку струму, так і від прямого ураження електрострумом.

Додатковим інженерним рішенням є встановлення блоків додаткового вирівнювання потенціалів (ДСВП) у вологих приміщеннях, що гарантує зниження напруги дотику до нульового рівня навіть у разі затримки спрацьовування контактів вимикача. Наявність ДСВП є критичною в лікувальних закладах категорій 1 та 2 згідно з IEC 60364-7-710, де вирівнюються потенціали процедурних столів та наркозних апаратів.

> 🔧 **Навіщо це знати.** Розроблений алгоритм розрахунку лежить в основі програмного забезпечення для проектування електромереж (EPLAN, DIALux, AutoCAD Electrical). Він доводить, чому вимірювання опору петлі «фаза-нуль» приладовтором є обов'язковою процедурою перед введенням будь-якої установки в експлуатацію.
