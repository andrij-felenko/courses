# ⚙️ Калькулятор параметрів TVS-діодів та розрахунку Clamping Voltage

Практичний інструмент призначений для точного розрахунку перехідних процесів обмеження напруги (Clamping Voltage) напівпровідниковими TVS-діодами, моделювання розподілу розрядних струмів за методологією SEED (System-Efficient ESD Design) та оцінки деградації швидкісних інтерфейсів через паразитну ємність p-n переходу. Програма моделює форми імпульсів електростатичного розряду за стандартами IEC 61000-4-2 (системний рівень 8–15 кВ), ANSI/ESDA/JEDEC JS-001 (модель людського тіла HBM) та ANSI/ESDA/JEDEC JS-002 (модель зарядженого приладу CDM), враховуючи динамічний опір діода, ефект Snapback та паразитну індуктивність друкованих провідників на платі.

---

## Інженерна постановка задачі

При проектуванні захисту сучасних високоінтегрованих мікросхем інженер стикається з фундаментальним інженерним компромісом між трьома критичними критеріями:

1. **Захисна здатність та динамічне обмеження напруги (Clamping Efficiency):** Залишкова пікова напруга на виводі мікросхеми `V_pin_IC(t)` під час системного розряду 8 кВ (піковий струм до 30 А з часом наростання менше 1 нс) не повинна перевищувати критичну напругу пробою діелектрика затвора вхідних польових транзисторів `V_fail_IC` (типово 10–14 В для 3.3 В КМОН-логіки та 5–7 В для субмікронних технологій 1.8 В / 1.2 В).
2. **Безпека навантаження та стійкість до замикання (Latch-up Immunity):** Якщо для покращення обмеження напруги застосовується TVS-діод зі структурою зворотного зриву напруги (Snapback / SCR), його напруга утримання `V_hold` повинна бути строго вищою за максимальну напругу джерела живлення захищуваної сигнальної лінії або шини живлення `V_supply_max` з інженерним запасом не менше 10–15%. Якщо ця умова порушується, діод після зняття високовольтного імпульсу залишиться у відкритому низькоомному стані за рахунок струму від джерела живлення, що призведе до незворотного вигоряння друкованої плати.
3. **Високочастотна сигнальна цілісність (Signal Integrity):** Власна бар'єрна ємність p-n переходу діода `C_j` діє як паразитна шунтувальна ємність сигнальної лінії з хвильовим імпедансом `Z_0`. Для інтерфейсів передачі даних надвисокої швидкості (USB 3.2 Gen2 зі швидкістю 10 Гбіт/с, PCIe 4.0/5.0 зі швидкістю 16–32 ГТ/с, HDMI 2.1 з пропускною здатністю 48 Гбіт/с) навіть паразитна ємність понад 0.3–0.5 пФ спричиняє завалювання фронтів цифрових імпульсів, катастрофічне розмиття очної діаграми (Eye Diagram Closure) та неприпустимий ріст міжсимвольної інтерференції (ISI).

Для створення надійної друкованої плати інженер зобов'язаний розрахувати часову форму струму розряду `i(t)`, падіння напруги на напівпровідниковій структурі TVS з урахуванням його динамічного опору `R_dyn`, індуктивний стрибок напруги на друкованих провідниках `L_trace · (di/dt)`, струм, що проникає у внутрішні захисні діоди кристала `I_IC`, та високочастотні втрати прямої передачі сигналу `S_21(f)`.

---

## Математичні моделі розрядних хвиль та фізичні процеси

### 1. Модель розряду за стандартом IEC 61000-4-2

Стандартний тестовий імпульс системного рівня IEC 61000-4-2 є результатом накладання двох фізичних процесів: субнаносекундного розряду паразитної ємності металевого наконечника розрядного пістолета та руки оператора (ємність 10–30 пФ) і тривалого розряду основного накопичувального конденсатора ємністю 150 пФ через внутрішній опір тіла 330 Ом.

Математично форма імпульсу описується чотирипараметричним аналітичним виразом:

```text
i_IEC(t) = i_1(t) + i_2(t)

i_1(t) = [ I_1 / k_1 ] · [ (t / τ_1)^n / (1 + (t / τ_1)^n) ] · exp(-t / τ_2)
i_2(t) = [ I_2 / k_2 ] · [ (t / τ_3)^n / (1 + (t / τ_3)^n) ] · exp(-t / τ_4)
```

де:
- `I_1` та `I_2` — базові амплітудні коефіцієнти струму першого та другого піків;
- `k_1` та `k_2` — коефіцієнти корекції пікової амплітуди через взаємний вплив експоненційних функцій:
  
  ```text
  k_1 = exp( -(τ_1 / τ_2) · (n · τ_2 / τ_1)^(1/n) )
  k_2 = exp( -(τ_3 / τ_4) · (n · τ_4 / τ_3)^(1/n) )
  ```
- `τ_1` — постійна часу наростання фронту першого піку (`τ_1 ≈ 0.6` нс, що забезпечує час наростання від 10% до 90% у діапазоні `0.7..1.0` нс);
- `τ_2` — постійна часу релаксації першого піку (`τ_2 ≈ 1.6` нс);
- `τ_3` — постійна часу наростання другого піку (`τ_3 ≈ 12.0` нс);
- `τ_4` — постійна часу затухання основного розряду тіла (`τ_4 ≈ 47.0` нс);
- `n` — емпіричний показник крутизни фронту (`n = 1.8`).

Для стандартного випробувального рівня 4 (напруга контактного розряду `V_ESD = 8` кВ):
- Амплітуда першого піку струму: `I_peak_1 = 8 кВ · 3.75 А/кВ = 30.0 А ± 15%`;
- Струм на позначці 30 нс: `I(30 нс) = 16.0 А ± 30%`;
- Струм на позначці 60 нс: `I(60 нс) = 8.0 А ± 30%`.

```
                  Форма хвилі струму IEC 61000-4-2 (8 кВ)
   Струм I, А
      30 ┼      ▲ (Перший пік: I_pk = 30 А при t = 0.8 нс)
         │     ╱ ╲
      20 ┼    ╱   ╲
         │   ╱     ╲____
      16 ┼  ╱           ╲ (Другий пік: I_30ns = 16 А при t = 30 нс)
         │ ╱             ╲───────────
       8 ┼╱                          ╲ (I_60ns = 8 А)
         │                                    ╲─────────
       0 ┴─────┴─────────┴───────────┴─────────┴─────────┴───> Час t, нс
         0    0.8        10          30        60        100
```

---

### 2. Модель людського тіла HBM (ANSI/ESDA/JEDEC JS-001)

Модель HBM моделює розряд людини безпосередньо на вивід компонента під час виробничих операцій монтажу. Контур являє собою послідовний RC-ланцюг (`C_HBM = 100` пФ, `R_HBM = 1500` Ом).

Миттєвий струм описується різницею двох експонент із нормованим часом наростання та релаксації:

```text
i_HBM(t) = I_peak_HBM · [ 1 - exp(-t / τ_rise) ] · exp(-t / τ_decay)

I_peak_HBM = V_HBM / R_HBM = V_HBM / 1500 Ом
τ_rise = t_rise / 2.2 ≈ 5.0 нс / 2.2 ≈ 2.27 нс
τ_decay = R_HBM · C_HBM = 1500 Ом · 100 · 10⁻¹² Ф = 150 нс
```

Для випробувальної напруги 2000 В (Class 2): `I_peak_HBM = 2000 / 1500 ≈ 1.33` А. Струм на порядки менший, ніж у стандарті IEC 61000-4-2, а швидкість наростання `di/dt` становить лише `0.15..0.25` А/нс.

---

### 3. Модель зарядженого приладу CDM (ANSI/ESDA/JEDEC JS-002)

Модель CDM відображає надшвидкий розряд заряду, накопиченого безпосередньо на металевих виводах та кремнієвому кристалі інтегральної мікросхеми при її контакті із заземленою поверхнею виробничого автомата. Оскільки опір у колі розряду обмежений лише опором самої іскри (`R_spark < 1` Ом), процес має вигляд надшвидкого ударного імпульсу:

```text
i_CDM(t) = I_peak_CDM · (t / t_peak) · exp(1.0 - (t / t_peak))

t_peak = 0.25 нс (250 пікосекунд)
I_peak_CDM = V_CDM / √(L_pkg / C_pkg)
```

При ємності корпусу `C_pkg = 4` пФ та індуктивності іскрового розряду `L_pkg = 1.5` нГн для напруги `V_CDM = 500` В піковий струм сягає `12.0..15.0` А при часі наростання фронту менше 200–300 пікосекунд. Швидкість наростання струму `di/dt` перевищує `50..80` А/нс.

---

### 4. Динаміка обмеження напруги TVS-діодом та індуктивний стрибок на платі

Повна напруга `V_node_total(t)`, яка виникає на вхідному контактному майданчику друкованої плати, складається з напівпровідникової напруги обмеження TVS-діода та паразитного індуктивного викиду:

```text
V_node_total(t) = V_TVS(i_TVS(t)) + V_inductive(t)
```

Напруга на переході самого TVS-діода описується кусочно-лінійною моделлю TLP:
- **Для класичного лавинного TVS (Zener/Avalanche):**
  
  ```text
  V_TVS(i) = V_BR + i_TVS(t) · R_dyn
  ```
- **Для TVS-діода зі структурою Snapback (SCR):**
  
  ```text
  V_TVS(i) = V_hold + i_TVS(t) · R_dyn   [при i_TVS > I_hold]
  ```

Індуктивне падіння напруги генерується струмом розряду, що протікає крізь сумарну індуктивність виводів корпусу діода `L_pkg` та друкованих провідників плати `L_trace`:

```text
V_inductive(t) = (L_pkg + L_trace) · (di_total(t) / dt)
```

Якщо індуктивність провідника становить 1.5 нГн, а струм розряду наростає зі швидкістю `di/dt = 30` А/нс, індуктивний викид складе:

```text
V_inductive = 1.5 · 10⁻⁹ Гн · (30 · 10⁹ А/с) = 45.0 В
```

Цей індуктивний сплеск амплітудою 45 В додається до напруги обмеження TVS-переходу (наприклад, 6 В), утворюючи сумарний імпульс напруги `51 В` на вході плати, який безпосередньо діє на мікросхему протягом перших 500 пікосекунд розряду.

---

### 5. Методологія SEED та аналіз розподілу струмів

Методологія координації системного захисту SEED (System-Efficient ESD Design, стандарт **IEC 62215-3**) розглядає спільну паралельну роботу зовнішнього захисного діода на платі та внутрішніх ESD-структур на кристалі мікросхеми, розділених послідовним резистором друкованої плати `R_ser`.

```
                    Еквівалентна електрична схема вузла SEED
   
           i_total(t)
   ────────────────────────┬───────────────────────[ R_ser ]───────────> Вхід ІМС
                           │                                               │
                           ▼                                               ▼
                     ┌───────────┐                                   ┌───────────┐
                     │ TVS діод  │                                   │ On-Chip   │
                     │ V_hold    │                                   │ V_on_IC   │
                     │ R_dyn_TVS │                                   │ R_dyn_IC  │
                     └─────┬─────┘                                   └─────┬─────┘
                           │ i_TVS(t)                                      │ i_IC(t)
                           ▼                                               ▼
                       [ Земля ]                                       [ Земля ]
```

Складаючи рівняння електричної рівноваги за законами Кірхгофа:

```text
i_total(t) = i_TVS(t) + i_IC(t)
V_TVS(t) = V_hold_TVS + i_TVS(t) · R_dyn_TVS
V_pin_IC(t) = V_TVS(t) - i_IC(t) · R_ser = V_on_IC + i_IC(t) · R_dyn_IC
```

Підставляючи `i_TVS(t) = i_total(t) - i_IC(t)`, отримуємо точний аналітичний вираз для струму крізь кристал мікросхеми:

```text
i_IC(t) = [ V_hold_TVS + i_total(t) · R_dyn_TVS - V_on_IC ] / [ R_ser + R_dyn_IC + R_dyn_TVS ]
```

Звідси визначається мінімально необхідне значення послідовного захисного резистора `R_ser_min`, яке гарантує, що струм чипа не перевищить граничний струм термічного руйнування внутрішніх діодів `I_fail_IC`:

```text
R_ser_min = [ (V_hold_TVS + I_peak_total · R_dyn_TVS - V_on_IC) / I_fail_IC ] - R_dyn_IC - R_dyn_TVS
```

Якщо розрахункове значення `R_ser_min ≤ 0`, це означає, що зовнішній TVS має настільки низький динамічний опір та низьку напругу утримання, що навіть без додаткового резистора струм чипа залишається в межах безпечної зони.

---

### 6. ВЧ-моделювання та аналіз матриці розсіювання (S-параметри)

Паразитна бар'єрна ємність діода `C_j` підключена паралельно сигнальній лінії з хвильовим імпедансом `Z_0`. Комплексна провідність навантаження на круговій частоті `ω = 2 · π · f`:

```text
Y_L(jω) = j · ω · C_j
```

Нормована матриця розсіювання паралельного шунта визначає прямий коефіцієнт передачі `S_21`:

```text
S_21(jω) = 2 / [ 2 + Y_L(jω) · Z_0 ] = 2 / [ 2 + j · ω · C_j · Z_0 ]
```

Модуль коефіцієнта передачі:

```text
|S_21(f)| = 1 / √( 1 + (π · f · Z_0 · C_j)² )
```

Втрати передачі в логарифмічному масштабі (Insertion Loss, дБ):

```text
IL(f) = 20 · log10( |S_21(f)| ) = -10 · log10( 1 + (π · f · Z_0 · C_j)² )
```

Частота зрізу за рівнем −3 дБ (де потужність сигналу падає вдвічі):

```text
f_3dB = 1 / (π · Z_0 · C_j)
```

Групова затримка сигналу (Group Delay), яка показує частотну дисперсію та ризик фазового джитеру:

```text
τ_g(f) = - dφ(f) / dω = [ 2 · Z_0 · C_j ] / [ 4 + (ω · C_j · Z_0)² ]
```

---

## Чисельний алгоритм дискретного моделювання

Програмний комплекс виконує дискретне інтегрування за часом методом кінцевих різниць. Для коректного відтворення субнаносекундного фронту CDM та первинного піку IEC 61000-4-2 обрано крок дискретизації `Δt = 10` пікосекунд (`10⁻¹¹` с), що забезпечує не менше 20–80 розрахункових вузлів на передньому фронті наростання імпульсу, повністю усуваючи числову дисперсію та помилки обчислення похідної струму `di/dt`.

Поглинена енергія в кремнієвому об'ємі TVS-діода обчислюється чисельним інтегруванням методом трапецій:

```text
E_TVS = ∑ [ (V_TVS(k) · I_TVS(k) + V_TVS(k+1) · I_TVS(k+1)) / 2 ] · Δt
```

Це дозволяє перевірити розрахункову енергію на відповідність паспортній межі розсіювання діода за стандартом TLP або сплеску 8/20 мкс.

---

## Програмна реалізація аналізатора

Нижче наведено повні та взаємозамінні реалізації інструменту мовами C99 та C++20. Програма здійснює дискретну симуляцію в часовій області, інтегрує розсіяну енергію, обчислює SEED-координацію та формує структурований інженерний звіт.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>
#include <string.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

#define SIM_TIME_MAX_NS 120.0
#define SIM_TIME_STEP_NS 0.010 /* 10 пікосекунд */
#define SIM_POINTS_COUNT ((int)(SIM_TIME_MAX_NS / SIM_TIME_STEP_NS) + 1)

typedef enum {
    ESD_STD_IEC_61000_4_2 = 0,
    ESD_STD_HBM_JS_001    = 1,
    ESD_STD_CDM_JS_002    = 2
} EsdStandardType;

typedef struct {
    char name[32];
    double v_rwm;          /* Робоча максимальна зворотна напруга, В */
    double v_br;           /* Напруга лавинного пробою (при 1 мА), В */
    double v_hold;         /* Напруга утримання (для snapback), В */
    double v_trigger;      /* Тригерна напруга відкривання, В */
    double r_dyn;          /* Динамічний диференціальний опір, Ом */
    double c_j_pf;         /* Власна бар'єрна ємність переходу, пФ */
    double l_pkg_nh;       /* Внутрішня паразитна індуктивність виводів, нГн */
    bool   is_snapback;    /* Тип структури: true - Snapback SCR, false - Zener */
} TvsParameters;

typedef struct {
    double v_breakdown_oxide; /* Напруга пробою підзатворного діелектрика, В */
    double v_on_internal;     /* Напруга відкривання внутрішніх діодів, В */
    double r_dyn_internal;    /* Динамічний опір внутрішнього захисту, Ом */
    double i_fail_internal;   /* Граничний струм теплового руйнування діодів, А */
} IcTargetParameters;

typedef struct {
    double l_trace_nh;        /* Паразитна індуктивність доріжки роз'єм-TVS-GND, нГн */
    double r_series_ohm;      /* Послідовний захисний резистор між TVS та IC, Ом */
    double z0_line_ohm;       /* Хвильовий імпеданс лінії передачі, Ом */
    double signal_freq_ghz;   /* Робоча частота сигналу (Найквіст), ГГц */
} PcbLayoutParameters;

typedef struct {
    double i_peak_esd;        /* Максимальний струм первинного ESD-імпульсу, А */
    double v_tvs_clamp_peak;  /* Пікова напруга на переході самого TVS, В */
    double v_inductive_peak;  /* Максимальний індуктивний стрибок L*di/dt, В */
    double v_node_total_peak; /* Сумарна напруга на контакті TVS, В */
    double v_ic_pin_peak;     /* Пікова напруга безпосередньо на виводі IC, В */
    double i_ic_max;          /* Максимальний струм крізь внутрішній захист IC, А */
    double energy_tvs_mj;     /* Енергія, поглинута TVS-діодом, мДж */
    double cutoff_freq_ghz;   /* Частота зрізу -3 дБ через ємність C_j, ГГц */
    double s21_loss_db;       /* Втрати вхідного сигналу на робочій частоті, дБ */
    double r_series_min_safe; /* Мінімально необхідний послідовний опір для безпеки SEED, Ом */
    bool   is_oxide_safe;     /* Прапорець безпеки підзатворного оксиду */
    bool   is_current_safe;   /* Прапорець безпеки за внутрішнім струмом чипа */
    bool   is_latchup_safe;   /* Прапорець стійкості до ефекту Latch-up */
} SimulationMetrics;

/* Генерація миттєвого струму розряду IEC 61000-4-2 за формулою 4 експонент */
double calculate_iec_current(double t_ns, double v_kv) {
    if (t_ns <= 0.0) return 0.0;
    
    double scale = v_kv / 8.0; /* Нормування до 8 кВ */
    double i1_base = 16.6 * scale;
    double k1 = 0.925;
    double tau1 = 0.6;
    double tau2 = 1.6;
    double n = 1.8;
    
    double i2_base = 9.3 * scale;
    double k2 = 0.940;
    double tau3 = 12.0;
    double tau4 = 47.0;
    
    double t_tau1_n = pow(t_ns / tau1, n);
    double term1 = (i1_base / k1) * (t_tau1_n / (1.0 + t_tau1_n)) * exp(-t_ns / tau2);
    
    double t_tau3_n = pow(t_ns / tau3, n);
    double term2 = (i2_base / k2) * (t_tau3_n / (1.0 + t_tau3_n)) * exp(-t_ns / tau4);
    
    return term1 + term2;
}

/* Генерація миттєвого струму HBM JS-001 */
double calculate_hbm_current(double t_ns, double v_kv) {
    if (t_ns <= 0.0) return 0.0;
    double v_volts = v_kv * 1000.0;
    double i_peak = v_volts / 1500.0;
    double tau_rise = 2.27; /* t_r ≈ 5.0 нс */
    double tau_decay = 150.0;
    
    return i_peak * (1.0 - exp(-t_ns / tau_rise)) * exp(-t_ns / tau_decay);
}

/* Генерація миттєвого струму CDM JS-002 */
double calculate_cdm_current(double t_ns, double v_kv) {
    if (t_ns <= 0.0) return 0.0;
    double scale = v_kv / 0.500; /* Нормування до 500 В */
    double i_peak = 12.0 * scale;
    double t_peak = 0.25; /* 250 пікосекунд */
    
    return i_peak * (t_ns / t_peak) * exp(1.0 - (t_ns / t_peak));
}

void run_esd_simulation(
    const TvsParameters *tvs,
    const IcTargetParameters *ic,
    const PcbLayoutParameters *pcb,
    EsdStandardType std_type,
    double v_stress_kv,
    double v_supply_line_v,
    SimulationMetrics *out_metrics)
{
    memset(out_metrics, 0, sizeof(SimulationMetrics));
    
    double l_total_h = (tvs->l_pkg_nh + pcb->l_trace_nh) * 1e-9;
    double dt_s = SIM_TIME_STEP_NS * 1e-9;
    
    double prev_current = 0.0;
    double energy_joules = 0.0;
    
    out_metrics->v_tvs_clamp_peak = 0.0;
    out_metrics->v_inductive_peak = 0.0;
    out_metrics->v_node_total_peak = 0.0;
    out_metrics->v_ic_pin_peak = 0.0;
    out_metrics->i_ic_max = 0.0;
    out_metrics->i_peak_esd = 0.0;
    
    for (int step = 0; step < SIM_POINTS_COUNT; ++step) {
        double t_ns = step * SIM_TIME_STEP_NS;
        double i_total = 0.0;
        
        switch (std_type) {
            case ESD_STD_IEC_61000_4_2:
                i_total = calculate_iec_current(t_ns, v_stress_kv);
                break;
            case ESD_STD_HBM_JS_001:
                i_total = calculate_hbm_current(t_ns, v_stress_kv);
                break;
            case ESD_STD_CDM_JS_002:
                i_total = calculate_cdm_current(t_ns, v_stress_kv);
                break;
        }
        
        if (i_total > out_metrics->i_peak_esd) {
            out_metrics->i_peak_esd = i_total;
        }
        
        /* Швидкість зміни струму di/dt */
        double di_dt = (i_total - prev_current) / dt_s;
        prev_current = i_total;
        
        /* Індуктивний стрибок напруги */
        double v_ind = l_total_h * di_dt;
        if (v_ind < 0.0) v_ind = 0.0;
        if (v_ind > out_metrics->v_inductive_peak) {
            out_metrics->v_inductive_peak = v_ind;
        }
        
        /* Розподіл струмів SEED між TVS та внутрішнім ESD кристала */
        double v_base_tvs = tvs->is_snapback ? tvs->v_hold : tvs->v_br;
        
        /* Аналітичний розрахунок струму кристала */
        double num = v_base_tvs + (i_total * tvs->r_dyn) - ic->v_on_internal;
        double den = pcb->r_series_ohm + ic->r_dyn_internal + tvs->r_dyn;
        double i_ic = (num > 0.0) ? (num / den) : 0.0;
        if (i_ic > i_total) i_ic = i_total;
        
        double i_tvs = i_total - i_ic;
        if (i_tvs < 0.0) i_tvs = 0.0;
        
        /* Напруга на переході TVS */
        double v_tvs_semi = (i_tvs > 0.0) ? (v_base_tvs + i_tvs * tvs->r_dyn) : 0.0;
        if (v_tvs_semi > out_metrics->v_tvs_clamp_peak) {
            out_metrics->v_tvs_clamp_peak = v_tvs_semi;
        }
        
        /* Сумарна напруга на вході плати */
        double v_node_total = v_tvs_semi + v_ind;
        if (v_node_total > out_metrics->v_node_total_peak) {
            out_metrics->v_node_total_peak = v_node_total;
        }
        
        /* Напруга на виводі мікросхеми (після послідовного резистора) */
        double v_pin_ic = v_node_total - (i_ic * pcb->r_series_ohm);
        if (v_pin_ic > out_metrics->v_ic_pin_peak) {
            out_metrics->v_ic_pin_peak = v_pin_ic;
        }
        
        if (i_ic > out_metrics->i_ic_max) {
            out_metrics->i_ic_max = i_ic;
        }
        
        /* Інтегрування енергії в TVS: E = ∫ V(t) * I(t) dt */
        energy_joules += (v_tvs_semi * i_tvs) * dt_s;
    }
    
    out_metrics->energy_tvs_mj = energy_joules * 1000.0;
    
    /* Розрахунок частотних характеристик */
    double c_farads = tvs->c_j_pf * 1e-12;
    out_metrics->cutoff_freq_ghz = (1.0 / (M_PI * pcb->z0_line_ohm * c_farads)) * 1e-9;
    
    double f_hz = pcb->signal_freq_ghz * 1e9;
    double omega = 2.0 * M_PI * f_hz;
    double s21_mag_sq = 1.0 / (1.0 + pow(0.5 * omega * c_farads * pcb->z0_line_ohm, 2.0));
    out_metrics->s21_loss_db = 10.0 * log10(s21_mag_sq);
    
    /* Розрахунок мінімально необхідного R_series для безпеки SEED */
    double v_base_tvs = tvs->is_snapback ? tvs->v_hold : tvs->v_br;
    double r_req = ((v_base_tvs + out_metrics->i_peak_esd * tvs->r_dyn - ic->v_on_internal) 
                   / ic->i_fail_internal) - ic->r_dyn_internal - tvs->r_dyn;
    out_metrics->r_series_min_safe = (r_req > 0.0) ? r_req : 0.0;
    
    /* Критерії валідації безпеки */
    out_metrics->is_oxide_safe = (out_metrics->v_ic_pin_peak < ic->v_breakdown_oxide);
    out_metrics->is_current_safe = (out_metrics->i_ic_max < ic->i_fail_internal);
    
    if (tvs->is_snapback) {
        out_metrics->is_latchup_safe = (tvs->v_hold > (1.10 * v_supply_line_v));
    } else {
        out_metrics->is_latchup_safe = true;
    }
}

void print_engineering_report(
    const TvsParameters *tvs,
    const IcTargetParameters *ic,
    const PcbLayoutParameters *pcb,
    EsdStandardType std_type,
    double v_stress_kv,
    double v_supply_v,
    const SimulationMetrics *m)
{
    const char *std_names[] = {
        "IEC 61000-4-2 (Системний рівень)",
        "ANSI/ESDA/JEDEC JS-001 (HBM)",
        "ANSI/ESDA/JEDEC JS-002 (CDM)"
    };
    
    printf("\n======================================================================\n");
    printf("   ЗВІТ СИМУЛЯЦІЇ ESD-ЗАХИСТУ ТА РОЗРАХУНКУ ПАРАМЕТРІВ TVS-ДІОДА      \n");
    printf("======================================================================\n");
    printf(" 1. ПАРАМЕТРИ СТРЕСУ ТА СТАНДАРТУ:\n");
    printf("    • Стандарт випробування:   %s\n", std_names[std_type]);
    printf("    • Напруга випробування:    %.2f кВ\n", v_stress_kv);
    printf("    • Піковий струм розряду:   %.2f А\n", m->i_peak_esd);
    printf("    • Напруга шини живлення:   %.2f В\n", v_supply_v);
    printf("----------------------------------------------------------------------\n");
    printf(" 2. ПАРАМЕТРИ TVS-ДІОДА (%s):\n", tvs->name);
    printf("    • Робоча напруга V_RWM:    %.2f В\n", tvs->v_rwm);
    printf("    • Напруга пробою V_BR:     %.2f В\n", tvs->v_br);
    printf("    • Тип структури:           %s\n", tvs->is_snapback ? "Snapback SCR" : "Standard Zener");
    if (tvs->is_snapback) {
        printf("    • Напруга утримання V_h:   %.2f В (Тригер V_t1 = %.2f В)\n", tvs->v_hold, tvs->v_trigger);
    }
    printf("    • Динамічний опір R_dyn:   %.3f Ом\n", tvs->r_dyn);
    printf("    • Бар'єрна ємність C_j:    %.3f пФ\n", tvs->c_j_pf);
    printf("    • Індуктивність виводів:   %.2f нГн\n", tvs->l_pkg_nh);
    printf("----------------------------------------------------------------------\n");
    printf(" 3. ДРУКОВАНА ПЛАТА ТА ЦІЛЬОВА МІКРОСХЕМА (SEED КООРДИНАЦІЯ):\n");
    printf("    • Індуктивність доріжки:   %.2f нГн (L_trace)\n", pcb->l_trace_nh);
    printf("    • Послідовний резистор:    %.2f Ом (R_series)\n", pcb->r_series_ohm);
    printf("    • Межа пробою оксиду IC:   %.2f В (V_breakdown)\n", ic->v_breakdown_oxide);
    printf("    • Струмова межа чипа:      %.2f А (I_fail_internal)\n", ic->i_fail_internal);
    printf("----------------------------------------------------------------------\n");
    printf(" 4. РЕЗУЛЬТАТИ ДИНАМІЧНОГО РОЗРАХУНКУ НАПРУГ І СТРУМІВ:\n");
    printf("    • Індуктивний стрибок:     +%.2f В  [L * di/dt]\n", m->v_inductive_peak);
    printf("    • Напруга переходу TVS:    %.2f В  [V_semi]\n", m->v_tvs_clamp_peak);
    printf("    • Пікова напруга на платі: %.2f В  [V_node_total]\n", m->v_node_total_peak);
    printf("    • Напруга на виводі чипа:  %.2f В  [V_pin_IC]\n", m->v_ic_pin_peak);
    printf("    • Струм крізь кристал IC:  %.3f А  (%.1f%% від повного струму)\n", 
           m->i_ic_max, (m->i_ic_max / m->i_peak_esd) * 100.0);
    printf("    • Енергія в TVS-діоді:     %.3f мДж\n", m->energy_tvs_mj);
    printf("    • Мінімальний R_ser (SEED):%.2f Ом\n", m->r_series_min_safe);
    printf("----------------------------------------------------------------------\n");
    printf(" 5. СИГНАЛЬНА ЦІЛІСНІСТЬ (HIGH-SPEED SIGNAL INTEGRITY):\n");
    printf("    • Хвильовий імпеданс Z_0:  %.1f Ом\n", pcb->z0_line_ohm);
    printf("    • Частота зрізу (-3 дБ):   %.2f ГГц\n", m->cutoff_freq_ghz);
    printf("    • Втрати на частоті %.2f ГГц: %.3f дБ (S21)\n", pcb->signal_freq_ghz, m->s21_loss_db);
    printf("----------------------------------------------------------------------\n");
    printf(" 6. ПІДСУМКОВИЙ ІНЖЕНЕРНИЙ ВИСНОВОК:\n");
    printf("    [%s] 1. Стійкість діелектрика затвора (%.2f В < %.2f В)\n",
           m->is_oxide_safe ? " УСПІХ " : "ДЕФЕКТ", m->v_ic_pin_peak, ic->v_breakdown_oxide);
    printf("    [%s] 2. Струмове навантаження внутрішнього захисту (%.2f А < %.2f А)\n",
           m->is_current_safe ? " УСПІХ " : "ДЕФЕКТ", m->i_ic_max, ic->i_fail_internal);
    printf("    [%s] 3. Запобігання ефекту замикання Latch-up (%s)\n",
           m->is_latchup_safe ? " УСПІХ " : "ДЕФЕКТ", 
           tvs->is_snapback ? (m->is_latchup_safe ? "V_hold > 1.1*V_supply" : "V_hold <= V_supply!") : "Non-snapback (N/A)");
    printf("======================================================================\n\n");
}

int main(void) {
    /* 1. Конфігурація швидкісного TVS-діода (Snapback для USB 3.2 / HDMI 2.0) */
    TvsParameters tvs_snap = {
        .name = "ESD7383_Snapback",
        .v_rwm = 3.3,
        .v_br = 5.0,
        .v_hold = 3.8,
        .v_trigger = 7.5,
        .r_dyn = 0.22,
        .c_j_pf = 0.28,
        .l_pkg_nh = 0.35, /* DFN0603 */
        .is_snapback = true
    };
    
    /* 2. Конфігурація класичного TVS-діода (Zener для повільних шин / живлення) */
    TvsParameters tvs_zener = {
        .name = "SMAJ5.0A_Zener",
        .v_rwm = 5.0,
        .v_br = 6.4,
        .v_hold = 6.4,
        .v_trigger = 6.4,
        .r_dyn = 0.85,
        .c_j_pf = 15.0,
        .l_pkg_nh = 1.20, /* SMA package */
        .is_snapback = false
    };
    
    /* 3. Цільовий мікроконтролер / швидкісний PHY-трансивер */
    IcTargetParameters mcu_target = {
        .v_breakdown_oxide = 11.5, /* Пробій затвора при 11.5 В */
        .v_on_internal = 0.85,     /* Внутрішній діод відкривається при 0.85 В */
        .r_dyn_internal = 2.40,    /* Динамічний опір захисту кристала 2.4 Ом */
        .i_fail_internal = 1.50    /* Термічне руйнування при струмі понад 1.5 А */
    };
    
    /* 4. Параметри трасування друкованої плати */
    PcbLayoutParameters pcb_highspeed = {
        .l_trace_nh = 1.20,        /* 1.2 мм доріжки до перехідних отворів землі */
        .r_series_ohm = 15.0,      /* Послідовний демпфер 15 Ом */
        .z0_line_ohm = 50.0,       /* 50 Ом несиметрична лінія (90 Ом диференціальна) */
        .signal_freq_ghz = 5.0     /* 5 ГГц для USB 3.2 Gen2 */
    };
    
    SimulationMetrics metrics;
    
    /* Тест 1: Системний розряд 8 кВ IEC 61000-4-2 на швидкісну лінію з TVS Snapback */
    run_esd_simulation(&tvs_snap, &mcu_target, &pcb_highspeed, 
                       ESD_STD_IEC_61000_4_2, 8.0, 3.3, &metrics);
    print_engineering_report(&tvs_snap, &mcu_target, &pcb_highspeed, 
                             ESD_STD_IEC_61000_4_2, 8.0, 3.3, &metrics);
    
    /* Тест 2: Модель CDM 500 В на той самий вузол */
    run_esd_simulation(&tvs_snap, &mcu_target, &pcb_highspeed, 
                       ESD_STD_CDM_JS_002, 0.500, 3.3, &metrics);
    print_engineering_report(&tvs_snap, &mcu_target, &pcb_highspeed, 
                             ESD_STD_CDM_JS_002, 0.500, 3.3, &metrics);
    
    /* Тест 3: Порівняння зі звичайним Zener TVS без послідовного резистора (R_ser = 0) */
    pcb_highspeed.r_series_ohm = 0.0;
    run_esd_simulation(&tvs_zener, &mcu_target, &pcb_highspeed, 
                       ESD_STD_IEC_61000_4_2, 8.0, 3.3, &metrics);
    print_engineering_report(&tvs_zener, &mcu_target, &pcb_highspeed, 
                             ESD_STD_IEC_61000_4_2, 8.0, 3.3, &metrics);
    
    return 0;
}
```
```cpp
#include <iostream>
#include <iomanip>
#include <vector>
#include <string>
#include <string_view>
#include <cmath>
#include <numbers>
#include <algorithm>
#include <expected>

namespace esd {

enum class StandardType {
    Iec61000_4_2,
    HbmJs001,
    CdmJs002
};

struct TvsParameters {
    std::string name{"Generic_TVS"};
    double v_rwm{3.3};          // Робоча напруга, В
    double v_br{5.0};           // Напруга пробою, В
    double v_hold{3.8};         // Напруга утримання (Snapback), В
    double v_trigger{7.5};      // Тригерна напруга, В
    double r_dyn{0.22};         // Динамічний опір, Ом
    double c_j_pf{0.28};        // Бар'єрна ємність, пФ
    double l_pkg_nh{0.35};      // Паразитна індуктивність корпусу, нГн
    bool is_snapback{true};     // Структура Snapback
};

struct IcTargetParameters {
    double v_breakdown_oxide{11.5}; // Поріг руйнування діелектрика затвора, В
    double v_on_internal{0.85};     // Поріг відкривання внутрішніх діодів, В
    double r_dyn_internal{2.40};    // Динамічний опір внутрішнього захисту, Ом
    double i_fail_internal{1.50};   // Граничний безпечний струм кристала, А
};

struct PcbLayoutParameters {
    double l_trace_nh{1.20};      // Індуктивність підвідної траси, нГн
    double r_series_ohm{15.0};    // Послідовний резистор SEED, Ом
    double z0_line_ohm{50.0};     // Хвильовий опір лінії, Ом
    double signal_freq_ghz{5.0};  // Робоча частота сигналу, ГГц
};

struct SimulationMetrics {
    double i_peak_esd{0.0};
    double v_tvs_clamp_peak{0.0};
    double v_inductive_peak{0.0};
    double v_node_total_peak{0.0};
    double v_ic_pin_peak{0.0};
    double i_ic_max{0.0};
    double energy_tvs_mj{0.0};
    double cutoff_freq_ghz{0.0};
    double s21_loss_db{0.0};
    double r_series_min_safe{0.0};
    bool is_oxide_safe{false};
    bool is_current_safe{false};
    bool is_latchup_safe{false};
};

class WaveformGenerator {
public:
    [[nodiscard]] static double get_iec_current(double t_ns, double v_kv) noexcept {
        if (t_ns <= 0.0) return 0.0;
        const double scale = v_kv / 8.0;
        constexpr double i1_base = 16.6;
        constexpr double k1 = 0.925;
        constexpr double tau1 = 0.6;
        constexpr double tau2 = 1.6;
        constexpr double n = 1.8;

        constexpr double i2_base = 9.3;
        constexpr double k2 = 0.940;
        constexpr double tau3 = 12.0;
        constexpr double tau4 = 47.0;

        const double t_tau1_n = std::pow(t_ns / tau1, n);
        const double term1 = (i1_base * scale / k1) * (t_tau1_n / (1.0 + t_tau1_n)) * std::exp(-t_ns / tau2);

        const double t_tau3_n = std::pow(t_ns / tau3, n);
        const double term2 = (i2_base * scale / k2) * (t_tau3_n / (1.0 + t_tau3_n)) * std::exp(-t_ns / tau4);

        return term1 + term2;
    }

    [[nodiscard]] static double get_hbm_current(double t_ns, double v_kv) noexcept {
        if (t_ns <= 0.0) return 0.0;
        const double i_peak = (v_kv * 1000.0) / 1500.0;
        constexpr double tau_rise = 2.27;
        constexpr double tau_decay = 150.0;
        return i_peak * (1.0 - std::exp(-t_ns / tau_rise)) * std::exp(-t_ns / tau_decay);
    }

    [[nodiscard]] static double get_cdm_current(double t_ns, double v_kv) noexcept {
        if (t_ns <= 0.0) return 0.0;
        const double i_peak = 12.0 * (v_kv / 0.500);
        constexpr double t_peak = 0.25;
        return i_peak * (t_ns / t_peak) * std::exp(1.0 - (t_ns / t_peak));
    }
};

class ProtectionSimulator {
public:
    static constexpr double SIM_TIME_MAX_NS = 120.0;
    static constexpr double SIM_TIME_STEP_NS = 0.010;
    static constexpr std::size_t SIM_POINTS = static_cast<std::size_t>(SIM_TIME_MAX_NS / SIM_TIME_STEP_NS) + 1;

    [[nodiscard]] static std::expected<SimulationMetrics, std::string_view> evaluate(
        const TvsParameters& tvs,
        const IcTargetParameters& ic,
        const PcbLayoutParameters& pcb,
        StandardType std_type,
        double v_stress_kv,
        double v_supply_line_v) noexcept
    {
        if (v_stress_kv <= 0.0) {
            return std::unexpected("Напруга стресу повинна бути більшою за нуль.");
        }

        SimulationMetrics m{};
        const double l_total_h = (tvs.l_pkg_nh + pcb.l_trace_nh) * 1e-9;
        constexpr double dt_s = SIM_TIME_STEP_NS * 1e-9;

        double prev_i = 0.0;
        double energy_joules = 0.0;

        for (std::size_t step = 0; step < SIM_POINTS; ++step) {
            const double t_ns = step * SIM_TIME_STEP_NS;
            double i_total = 0.0;

            switch (std_type) {
                case StandardType::Iec61000_4_2:
                    i_total = WaveformGenerator::get_iec_current(t_ns, v_stress_kv);
                    break;
                case StandardType::HbmJs001:
                    i_total = WaveformGenerator::get_hbm_current(t_ns, v_stress_kv);
                    break;
                case StandardType::CdmJs002:
                    i_total = WaveformGenerator::get_cdm_current(t_ns, v_stress_kv);
                    break;
            }

            m.i_peak_esd = std::max(m.i_peak_esd, i_total);

            const double di_dt = (i_total - prev_i) / dt_s;
            prev_i = i_total;

            const double v_ind = std::max(0.0, l_total_h * di_dt);
            m.v_inductive_peak = std::max(m.v_inductive_peak, v_ind);

            const double v_base_tvs = tvs.is_snapback ? tvs.v_hold : tvs.v_br;
            const double num = v_base_tvs + (i_total * tvs.r_dyn) - ic.v_on_internal;
            const double den = pcb.r_series_ohm + ic.r_dyn_internal + tvs.r_dyn;

            double i_ic = (num > 0.0) ? (num / den) : 0.0;
            i_ic = std::clamp(i_ic, 0.0, i_total);
            const double i_tvs = std::max(0.0, i_total - i_ic);

            const double v_tvs_semi = (i_tvs > 0.0) ? (v_base_tvs + i_tvs * tvs.r_dyn) : 0.0;
            m.v_tvs_clamp_peak = std::max(m.v_tvs_clamp_peak, v_tvs_semi);

            const double v_node_total = v_tvs_semi + v_ind;
            m.v_node_total_peak = std::max(m.v_node_total_peak, v_node_total);

            const double v_pin_ic = v_node_total - (i_ic * pcb.r_series_ohm);
            m.v_ic_pin_peak = std::max(m.v_ic_pin_peak, v_pin_ic);
            m.i_ic_max = std::max(m.i_ic_max, i_ic);

            energy_joules += (v_tvs_semi * i_tvs) * dt_s;
        }

        m.energy_tvs_mj = energy_joules * 1000.0;

        const double c_farads = tvs.c_j_pf * 1e-12;
        m.cutoff_freq_ghz = (1.0 / (std::numbers::pi * pcb.z0_line_ohm * c_farads)) * 1e-9;

        const double f_hz = pcb.signal_freq_ghz * 1e9;
        const double omega = 2.0 * std::numbers::pi * f_hz;
        const double s21_sq = 1.0 / (1.0 + std::pow(0.5 * omega * c_farads * pcb.z0_line_ohm, 2.0));
        m.s21_loss_db = 10.0 * std::log10(s21_sq);

        const double v_base_tvs = tvs.is_snapback ? tvs.v_hold : tvs.v_br;
        const double r_req = ((v_base_tvs + m.i_peak_esd * tvs.r_dyn - ic.v_on_internal) 
                             / ic.i_fail_internal) - ic.r_dyn_internal - tvs.r_dyn;
        m.r_series_min_safe = std::max(0.0, r_req);

        m.is_oxide_safe = (m.v_ic_pin_peak < ic.v_breakdown_oxide);
        m.is_current_safe = (m.i_ic_max < ic.i_fail_internal);
        m.is_latchup_safe = !tvs.is_snapback || (tvs.v_hold > (1.10 * v_supply_line_v));

        return m;
    }
};

void print_report(
    const TvsParameters& tvs,
    const IcTargetParameters& ic,
    const PcbLayoutParameters& pcb,
    StandardType std_type,
    double v_stress_kv,
    double v_supply_v,
    const SimulationMetrics& m)
{
    constexpr std::string_view std_names[] = {
        "IEC 61000-4-2 (Системний рівень)",
        "ANSI/ESDA/JEDEC JS-001 (HBM)",
        "ANSI/ESDA/JEDEC JS-002 (CDM)"
    };

    std::cout << "\n======================================================================\n";
    std::cout << "   C++20 ЗВІТ СИМУЛЯЦІЇ ESD-ЗАХИСТУ ТА ОЦІНКИ SEED КООРДИНАЦІЇ        \n";
    std::cout << "======================================================================\n";
    std::cout << std::fixed << std::setprecision(2);
    std::cout << " 1. ПАРАМЕТРИ ВИПРОБУВАННЯ:\n";
    std::cout << "    • Стандарт:               " << std_names[static_cast<int>(std_type)] << '\n';
    std::cout << "    • Напруга стресу:         " << v_stress_kv << " кВ\n";
    std::cout << "    • Піковий струм імпульсу: " << m.i_peak_esd << " А\n";
    std::cout << "    • Напруга шини V_supply:  " << v_supply_v << " В\n";
    std::cout << "----------------------------------------------------------------------\n";
    std::cout << " 2. ХАРАКТЕРИСТИКИ TVS (" << tvs.name << "):\n";
    std::cout << "    • Робоча напруга V_RWM:   " << tvs.v_rwm << " В\n";
    std::cout << "    • Пробій V_BR / Тригер:   " << tvs.v_br << " В / " << tvs.v_trigger << " В\n";
    std::cout << "    • Тип напівпровідника:    " << (tvs.is_snapback ? "Snapback SCR" : "Zener Avalanche") << '\n';
    if (tvs.is_snapback) {
        std::cout << "    • Напруга утримання V_h:  " << tvs.v_hold << " В\n";
    }
    std::cout << std::setprecision(3);
    std::cout << "    • Динамічний опір R_dyn:  " << tvs.r_dyn << " Ом\n";
    std::cout << "    • Бар'єрна ємність C_j:   " << tvs.c_j_pf << " пФ\n";
    std::cout << std::setprecision(2);
    std::cout << "----------------------------------------------------------------------\n";
    std::cout << " 3. ДИНАМІЧНИЙ ВІДГУК ТА ПЕРЕНАПРУГИ:\n";
    std::cout << "    • Індуктивний викид:      +" << m.v_inductive_peak << " В  [L_total * di/dt]\n";
    std::cout << "    • Напруга TVS-переходу:   " << m.v_tvs_clamp_peak << " В  [V_semi]\n";
    std::cout << "    • Залишок на вході плати: " << m.v_node_total_peak << " В  [V_node]\n";
    std::cout << "    • Залишок на виводі IC:   " << m.v_ic_pin_peak << " В  [V_pin_IC]\n";
    std::cout << std::setprecision(3);
    std::cout << "    • Струм крізь кристал IC: " << m.i_ic_max << " А (" 
              << (m.i_ic_max / m.i_peak_esd) * 100.0 << "% від повного струму)\n";
    std::cout << "    • Поглинута енергія TVS:  " << m.energy_tvs_mj << " мДж\n";
    std::cout << std::setprecision(2);
    std::cout << "    • Безпечний R_series_min: " << m.r_series_min_safe << " Ом\n";
    std::cout << "----------------------------------------------------------------------\n";
    std::cout << " 4. ВИСОКОЧАСТОТНА СИГНАЛЬНА ЦІЛІСНІСТЬ:\n";
    std::cout << "    • Частота зрізу (-3 дБ):  " << m.cutoff_freq_ghz << " ГГц\n";
    std::cout << "    • Втрати на " << pcb.signal_freq_ghz << " ГГц:     " << m.s21_loss_db << " дБ (S21)\n";
    std::cout << "----------------------------------------------------------------------\n";
    std::cout << " 5. КРИТЕРІЇ ВАЛІДАЦІЇ СИСТЕМИ:\n";
    std::cout << "    [" << (m.is_oxide_safe ? " УСПІХ " : "ДЕФЕКТ") << "] Діелектрик затвора (" 
              << m.v_ic_pin_peak << " В < " << ic.v_breakdown_oxide << " В)\n";
    std::cout << "    [" << (m.is_current_safe ? " УСПІХ " : "ДЕФЕКТ") << "] Струм кристала (" 
              << m.i_ic_max << " А < " << ic.i_fail_internal << " А)\n";
    std::cout << "    [" << (m.is_latchup_safe ? " УСПІХ " : "ДЕФЕКТ") << "] Захист від Latch-up ("
              << (tvs.is_snapback ? (m.is_latchup_safe ? "V_hold > 1.1*V_supply" : "V_hold <= V_supply!") : "Zener N/A") << ")\n";
    std::cout << "======================================================================\n\n";
}

} // namespace esd

int main() {
    using namespace esd;

    const TvsParameters tvs_snap{
        .name = "TPD4E05U06_Snapback",
        .v_rwm = 3.3,
        .v_br = 5.5,
        .v_hold = 3.6,
        .v_trigger = 7.0,
        .r_dyn = 0.18,
        .c_j_pf = 0.25,
        .l_pkg_nh = 0.30,
        .is_snapback = true
    };

    const IcTargetParameters ic_target{
        .v_breakdown_oxide = 11.0,
        .v_on_internal = 0.80,
        .r_dyn_internal = 2.20,
        .i_fail_internal = 1.20
    };

    const PcbLayoutParameters pcb_layout{
        .l_trace_nh = 0.90,       // 0.9 мм компактної траси
        .r_series_ohm = 18.0,     // 18 Ом демпфувальний резистор
        .z0_line_ohm = 50.0,
        .signal_freq_ghz = 5.0    // USB 3.2 Gen2
    };

    // Випробування 8 кВ IEC 61000-4-2
    auto res_iec = ProtectionSimulator::evaluate(tvs_snap, ic_target, pcb_layout,
                                                 StandardType::Iec61000_4_2, 8.0, 3.3);
    if (res_iec) {
        print_report(tvs_snap, ic_target, pcb_layout, StandardType::Iec61000_4_2, 8.0, 3.3, *res_iec);
    } else {
        std::cerr << "Помилка: " << res_iec.error() << '\n';
    }

    // Випробування CDM 500 В
    auto res_cdm = ProtectionSimulator::evaluate(tvs_snap, ic_target, pcb_layout,
                                                 StandardType::CdmJs002, 0.500, 3.3);
    if (res_cdm) {
        print_report(tvs_snap, ic_target, pcb_layout, StandardType::CdmJs002, 0.500, 3.3, *res_cdm);
    }

    return 0;
}
```
:::

---

## Електродинаміка паразитної індуктивності друкованого монтажу

Найважливішим висновком із чисельного моделювання є те, що індуктивний стрибок напруги `V_inductive = L_total · (di/dt)` під час субнаносекундного фронту розряду часто перевищує власну напругу обмеження напівпровідникового кристала діода. 

Розглянемо фізичну структуру паразитної індуктивності друкованої плати. Сумарна індуктивність контуру захисту складається з трьох послідовних компонентів:

```text
L_total = L_in_trace + L_pkg + L_gnd_via
```

1. **Індуктивність сигнального провідника від роз'єму до площадки TVS (`L_in_trace`):**
   За стандартом IPC-2141 індуктивність мікросмужкового провідника прямокутного перерізу шириною `w`, товщиною міді `t` та довжиною `l`, розташованого на висоті `h` над опорним шаром землі, розраховується за формулою:
   
   ```text
   L_trace ≈ 0.2 · l · [ ln( 2 · l / (w + t) ) + 0.2235 · (w + t) / l + 0.5 ]  (нГн, де l, w, t в мм)
   ```
   
   Для стандартної геометрії плати (довжина провідника `l = 3` мм, ширина `w = 0.2` мм, товщина міді 35 мкм) індуктивність становить близько `2.4..2.8` нГн.
2. **Індуктивність виводів корпусу компонента (`L_pkg`):**
   - Корпуси для монтажу в отвори (DO-204 / DO-15): `L_pkg ≈ 3.0..5.0` нГн;
   - Класичні SMD-корпуси з довгими виводами (SOT-23, SMA/SMB): `L_pkg ≈ 1.2..2.0` нГн;
   - Безвивідні ультракомпактні корпуси (DFN0603, DFN1006, SOD-882, WLCSP): `L_pkg ≈ 0.2..0.4` нГн.
3. **Індуктивність заземлювальних перехідних отворів (`L_gnd_via`):**
   Власна індуктивність циліндричного перехідного отвору довжиною `h` (товщина плати) та діаметром отвору `d` визначається співвідношенням:
   
   ```text
   L_via ≈ (μ_0 · h / (2 · π)) · [ ln( 4 · h / d ) + 1 ]
   ```
   
   Для типової 4-шарової друкованої плати товщиною `h = 1.6` мм із діаметром перехідного отвору `d = 0.3` мм:
   
   ```text
   L_via ≈ (4 · π · 10⁻⁷ · 1.6 · 10⁻³ / (2 · π)) · [ ln( 4 · 1.6 / 0.3 ) + 1 ] ≈ 1.30 · 10⁻⁹ Гн = 1.30 нГн
   ```

Якщо земляний вивід TVS-діода підключений до внутрішнього опорного полігону GND через один такий перехідний отвір, струм розряду 30 А з наростанням за 0.8 нс (`di/dt = 37.5` А/нс) створює на самому перехідному отворі падіння напруги:

```text
V_via = 1.30 нГн · 37.5 А/нс = 48.75 В
```

Цей потенціал піднімає локальну землю діода відносно опорної землі плати, зводячи ефективність захисту до нуля.

### Оптимізація матриці перехідних отворів (Via Stitching Array)

Для зменшення індуктивності заземлення інженери застосовують паралельне з'єднання кількох перехідних отворів. Проте еквівалентна індуктивність `N` паралельних отворів **не дорівнює** простому діленню `L_via / N` через взаємну індуктивність `M` між сусідніми провідниками струму одного напрямку:

```text
L_equiv = (L_via + (N - 1) · M) / N
```

де коефіцієнт взаємної індуктивності `M` між двома паралельними циліндрами на відстані `s` один від одного наближено дорівнює:

```text
M ≈ (μ_0 · h / (2 · π)) · [ ln( 2 · h / s ) - 1 + s / h ]
```

Якщо розмістити два перехідні отвори занадто близько (наприклад, з відстанню між центрами `s = 0.5` мм при `h = 1.6` мм), взаємна індуктивність становить `M ≈ 0.65` нГн, а сумарна еквівалентна індуктивність пари складе:

```text
L_pair = (1.30 нГн + 0.65 нГн) / 2 = 0.975 нГн  (зменшення лише на 25% замість очікуваних 50%)
```

Щоб мінімізувати взаємну індуктивність, паралельні перехідні отвори заземлення слід розносити на відстань `s ≥ 1.5..2.0` мм або розміщувати їх симетрично з протилежних боків контактної площадки TVS безпосередньо в полігон GND.

---

## Нелінійна вольт-фарадна характеристика та інтермодуляція

У радіочастотних колах та широкосмугових трактах бар'єрна ємність p-n переходу `C_j` не є строго константною величиною. Зі зміною миттєвої напруги на сигнальній лінії `V(t)` ширина збідненої області p-n переходу `W_dep(V)` динамічно модулюється за законом:

```text
C_j(V) = C_j0 / ( 1 - V / V_bi )^m
```

де:
- `C_j0` — бар'єрна ємність при нульовій напрузі зміщення (`V = 0`);
- `V_bi` — внутрішній контактний потенціал кремнієвого переходу (`V_bi ≈ 0.7..0.9` В);
- `m` — коефіцієнт нелінійності профілю легування (`m ≈ 0.33` для плавного переходу та `m ≈ 0.50` для різкого ступеневого p-n переходу).

При передачі високочастотного сигналу великої амплітуди (наприклад, вихідного сигналу РЧ-передавача потужністю +20 дБм з амплітудою напруги `V_RF_peak ≈ 3.16` В) зміна ємності діода протягом періоду коливань призводить до параметричної модуляції фазової швидкості хвилі. Це породжує нелінійні гармонійні спотворення:
1. **Генерацію другої та третьої гармонік (Harmonic Distortion — HD2, HD3):** Сигнал частоти `f_0` створює паразитні гармонійні складові на частотах `2 · f_0` та `3 · f_0`, які можуть потрапляти у смугу приймання сусідніх бездротових каналів (наприклад, гармоніка Wi-Fi 2.4 ГГц потрапляє на 4.8 ГГц і 7.2 ГГц).
2. **Інтермодуляційні спотворення третього порядку (Third-Order Intermodulation — IMD3):** При одночасній присутності двох несучих частот `f_1` та `f_2` нелінійна ємність TVS генерує паразитні продукти інтермодуляції на частотах `2 · f_1 - f_2` та `2 · f_2 - f_1`. Точка перетину за інтермодуляцією третього порядку (Output Third-Order Intercept Point — OIP3) для захисного TVS-діода повинна перевищувати `+45..+55` дБм, щоб не погіршувати динамічний діапазон приймального тракту.

Для мінімізації нелінійних спотворень у високоякісних РЧ-трактах застосовують зустрічно-послідовне увімкнення двох TVS-діодів (Back-to-Back Configuration). При додатному напівперіоді сигналу ємність одного переходу зростає, тоді як ємність іншого падає, внаслідок чого сумарна еквівалентна ємність пари залишається майже ідеально стабільною:

```text
C_total_equiv(V) = (C_j1(V) · C_j2(-V)) / (C_j1(V) + C_j2(-V)) ≈ C_j0 / 2 = const
```

---

## Архітектура багатошарових стек-апів друкованих плат

Розподіл електромагнітних полів та ефективність розсіювання струму розряду критично залежать від структури шарів друкованої плати (PCB Stackup):

```
       Оптимальний 4-шаровий стек-ап для системної ESD-стійкості
   ─────────────────────────────────────────────────────────────────────────────
   Шар (Layer)            Тип шару       Товщина діелектрика   Призначення
   ─────────────────────────────────────────────────────────────────────────────
   L1 (Top Layer)         Сигнал + TVS   —                     Компоненти, роз'єми
   ───────────────── Діелектрик Prepreg (h1 = 0.075–0.100 мм) ───────────────────
   L2 (Inner Layer 1)     Суцільний GND  —                     Опорний полігон землі
   ───────────────── Діелектрик Core (h2 = 1.000–1.200 мм) ─────────────────────
   L3 (Inner Layer 2)     Полігон PWR    —                     Шини живлення
   ───────────────── Діелектрик Prepreg (h3 = 0.075–0.100 мм) ───────────────────
   L4 (Bottom Layer)      Сигнал         —                     Вторинні траси
   ─────────────────────────────────────────────────────────────────────────────
```

Ключові інженерні правила побудови стек-апу:
1. **Мінімальний зазор між L1 та L2 (`h1 ≤ 0.1` мм):** Опорний шар землі GND повинен розташовуватися безпосередньо під верхнім сигнальним шаром із мінімальною товщиною препрегу (75–100 мкм). Це зменшує площу контуру протікання струму розряду між сигнальною доріжкою та зворотним шляхом землі, пропорційно знижуючи паразитну індуктивність петлі та електромагнітне випромінювання на внутрішні шари.
2. **Усунення розривів полігону під TVS-діодами:** Опорний полігон GND на шарі L2 під контактними майданчиками роз'ємів та TVS-діодів повинен бути абсолютно суцільним. Будь-які вирізи, щілини або сигнальні траси в цьому шарі змушують зворотний високочастотний струм розряду огинати перешкоду, збільшуючи індуктивність контуру в десятки разів і перетворюючи плату на випромінювальну антену.
3. **Захисні клітки перехідних отворів (Ground Cages / Guard Stitching):** По периметру друкованої плати та вздовж країв зони вхідних роз'ємів формується масив перехідних отворів заземлення (Via Stitching), який з'єднує верхній крайовий полігон землі з шарами L2 та L4. Крок між перехідними отворами `d_via` обирається з умови придушення найвищої значущої гармоніки ESD-імпульсу (`f_max ≈ 3` ГГц):
   
   ```text
   d_via ≤ λ_eff / 20 = (c / (f_max · √ε_r)) / 20
   ```
   
   Для матеріалу FR-4 (`ε_r ≈ 4.3`):
   
   ```text
   d_via ≤ (3 · 10⁸ м/с / (3 · 10⁹ Гц · √4.3)) / 20 ≈ (0.1 м / 2.073) / 20 ≈ 0.0482 м / 20 ≈ 2.4 мм
   ```
   
   Встановлення отворів із кроком 1.5–2.0 мм формує еквівалентний електромагнітний екран (клітку Фарадея всередині друкованої плати), що запобігає бічному випромінюванню магнітного поля розряду вглиб пристрою.

---

## Методика лабораторної верифікації та калібрування стенда

Для підтвердження розрахункових результатів на практиці проводять лабораторні сертифікаційні випробування із суворим калібруванням генератора розрядів.

```
          Схема калібрування ESD-генератора на мішені Пеллегріні
   
   [ ESD Gun (8 кВ) ] ───( Розряд )───> [ 2-Омна мішень Фарадея (Pellegrini Target) ]
                                                            │
                                                     ( 50 Ом кабель )
                                                            │
                                                            ▼
                                           [ Осцилограф 2 ГГц / 20 ГВиб/с ]
```

### 1. Калібрування форми хвилі струму за IEC 61000-4-2

Перед початком тестування параметри імпульсу верифікують на стандартизованій резистивній коаксіальній мішені Фарадея (Pellegrini Target) опором 2.0 Ом, інтегрованій у суцільний металевий екран площею не менше 1.2 × 1.2 м.

Осцилограф із аналоговою смугою пропускання не менше 2 ГГц фіксує чотири обов'язкові параметри хвилі:
- **Час наростання фронту `t_r` (від 10% до 90%):** строго від 0.7 до 1.0 нс;
- **Піковий струм `I_peak`:** 30.0 А `± 15%` (діапазон 25.5–34.5 А при 8 кВ);
- **Струм на 30 нс:** 16.0 А `± 30%` (11.2–20.8 А);
- **Струм на 60 нс:** 8.0 А `± 30%` (5.6–10.4 А).

Паразитна індуктивність заземлювального ременя пістолета (довжина 2.0 м) становить близько `2.5..3.0` мкГн. Якщо під час випробувань ремінь укладати випадковими петлями, його індуктивність змінюється, спотворюючи форму другого піку. Стандарт вимагає розміщувати заземлювальний кабель на діелектричній підставці на відстані не менше 0.5 м від металевих поверхонь столу.

---

### 2. Методика виявлення прихованих дефектів (Latent Damage Detection)

Звичайне тестування, яке обмежується лише перевіркою базового цифрового функціоналу (наприклад, чи блимає світлодіод або чи надсилаються пакети UART), не здатне виявити мікропробої оксиду затвора. Частково пошкоджений кристал зберігає функціональність при кімнатній температурі, проте деградує за кілька тижнів роботи в реальному приладі.

Протокол точного аналізу деградації включає:
1. **Вимірювання струму споживання в режимі глибокого сну (Deep Sleep / Standby Current):** До подачі розрядів фіксується струм `I_sleep` мікроконтролера з точністю до наноамперів. Після серії з 50 контактних розрядів 8 кВ у роз'єм вимірювання повторюють. Дрейф струму спокою навіть на `+1..+5` мкА свідчить про утворення каналів витоку в підзатворному оксиді та є прямим критерієм бракування зразка.
2. **Аналіз вольт-фарадної характеристики захисних діодів:** Збільшення ємності вхідного піна або падіння пробивної напруги `V_BR` зовнішнього TVS більш ніж на 5% сигналізує про настання теплової втоми кристала.
3. **Локалізація теплових дефектів (Lock-in Thermography — LIT):** Прилад поміщають під інфрачервоний мікроскоп і подають змінну напругу зсуву. Зона субкритичного пробою виявляється як локальне джерело тепловиділення потужністю менше 100 мкВт.

---

## Поглиблений розбір практичних інженерних кейсів (Case Studies)

### Кейс 1: Захист надшвидкісної диференціальної пари USB 3.2 Gen2 (10 Гбіт/с)

**Вихідні дані:**
- Інтерфейс: USB 3.2 Gen2 Type-C (швидкість передачі 10 Гбіт/с, частота Найквіста `f_Nyquist = 5` ГГц);
- Диференціальний хвильовий імпеданс пари: `Z_diff = 90` Ом (`Z_0 = 45` Ом для кожного провідника);
- Допустимі втрати на захисному вузлі: `IL(5 ГГц) > -0.4` дБ;
- Максимально допустима напруга на вході приймача (SerDes PHY): `V_max_PHY = 6.0` В;
- Випробувальний рівень: IEC 61000-4-2 Level 4 (8 кВ контакт, піковий струм 30 А).

**Аналіз та інженерне рішення:**
1. **Обмеження на послідовний резистор `R_ser`:** На швидкості 10 Гбіт/с встановлення послідовного резистора номіналом навіть 10 Ом неприпустиме, оскільки разом із вхідною ємністю приймача (0.5 пФ) він утворює фільтр із постійною часу `τ = 5` пс, що спричиняє завал фронтів тривалістю 25 пс та призводить до повного закриття очної діаграми. Тому для USB 3.2 значення `R_ser = 0` Ом.
2. **SEED-координація при `R_ser = 0`:** Оскільки захисний опір відсутній, єдиний спосіб утримати напругу нижче 6.0 В — застосувати TVS-діод із глибоким Snapback, наднизькою напругою утримання `V_hold = 3.3..3.6` В та екстремально низьким динамічним опором `R_dyn < 0.15` Ом.
   
   Розрахунок напруги на напівпровіднику:
   
   ```text
   V_semi = V_hold + I_peak · R_dyn = 3.5 В + (30 А · 0.12 Ом) = 7.1 В
   ```
   
   Оскільки струм частково шунтується внутрішніми діодами чипа, при співвідношенні опорів `R_dyn_TVS = 0.12` Ом та `R_dyn_IC = 2.0` Ом на чип піде струм:
   
   ```text
   I_IC = 30 А · [ 0.12 / (0.12 + 2.0) ] ≈ 1.70 А
   ```
   
   Напруга на переході складе:
   
   ```text
   V_semi = 3.5 В + (28.3 А · 0.12 Ом) = 6.89 В
   ```
3. **Мінімізація індуктивності монтажу:** Щоб індуктивний сплеск `V_ind` не перевищив 1.0 В, сумарна індуктивність траси повинна задовольняти умову:
   
   ```text
   L_total ≤ V_ind_max / (di/dt) = 1.0 В / (37.5 · 10⁹ А/с) ≈ 0.026 нГн
   ```
   
   Для досягнення цього застосовують 4-канальну матрицю TVS у корпусі DFN1210 з прохідним трасуванням Feed-Through (доріжка шириною 0.25 мм проходить прямо крізь виводи діода без відгалужень), а земляний полігон діода з'єднується з опорним шаром GND безпосередньо під корпусом за допомогою масиву з 4 мікроотворів Micro-Via (індуктивність менше 0.1 нГн).
4. **Вибір ємності діода `C_j`:** Для втрат менше −0.3 дБ на 5 ГГц:
   
   ```text
   C_j_max = √( 10^(0.3/10) - 1 ) / ( π · 5 · 10⁹ Гц · 45 Ом ) ≈ 0.267 / ( 7.068 · 10¹¹ ) ≈ 0.37 пФ
   ```
   
   Обирається спеціалізована збірка TVS з ємністю `C_j = 0.15..0.20` пФ.

---

### Кейс 2: Захист промислової польової шини RS-485 / CAN-FD

**Вихідні дані:**
- Інтерфейс: CAN-FD (швидкість 5 Мбіт/с) або RS-485 (швидкість 10 Мбіт/с);
- Робоча синфазна напруга ліній: від −7 В до +12 В (для RS-485) та до +24 В (для промислових мереж 24 В);
- Випробувальний рівень: IEC 61000-4-2 Level 4 (15 кВ повітря, 8 кВ контакт) та сплески Surge IEC 61000-4-5 (1 кВ, 8/20 мкс);
- Максимальна напруга входу трансивера: `V_max_CAN = 36.0` В.

**Аналіз та інженерне рішення:**
1. **Вибір робочої напруги TVS:** Для запобігання помилковому відкриванню при максимальній робочій напрузі обирається двонаправлений (Bidirectional) TVS-діод з робочою напругою `V_RWM = 24.0` В та напругою пробою `V_BR = 26.5..28.0` В.
2. **Тип структури (Latch-up Immunity):** У промислових мережах існує ризик короткого замикання сигнальних ліній на джерело живлення 24 В DC (Fault Protection). Якщо застосувати TVS зі структурою Snapback (`V_hold = 15` В), при контакті з шиною 24 В діод увімкнеться і миттєво згорить. Тому для RS-485 та CAN **суворо заборонено використовувати глибокий Snapback** — застосовуються виключно класичні лавинні діоди Zener з `V_hold ≥ V_BR ≥ 26.5` В.
3. **Координація опору `R_ser` та вибір технології резистора:** Оскільки швидкість передачі CAN-FD становить лише 5 Мбіт/с (тривалість біта 200 нс), сигнальна лінія дозволяє встановлення послідовного резистора номіналом `R_ser = 10..22` Ом або керамічного позистора (PTC). 
   
   > ⚠️ **Технологічна вимога до резисторів:** У колах захисту від ESD категорично заборонено використовувати тонкоплівкові резистори (Thin Film), оскільки їхній резистивний шар товщиною менше 100 нм миттєво випаровується (Trim Cut Burnout) під дією імпульсної напруги понад 200 В. Слід застосовувати виключно товстоплівкові резистори підвищеної імпульсної стійкості (Thick Film Surge Resistors) або циліндричні MELF-резистори з великим об'ємом резистивного матеріалу.
   
   При `R_ser = 22` Ом навіть при залишковій напрузі TVS `V_clamp = 35` В струм крізь вхід трансивера обмежений величиною:
   
   ```text
   I_IC ≈ (35 В - 0.8 В) / (22 Ом + 2 Ом) ≈ 1.42 А
   ```
   
   що гарантує повне збереження трансивера без деградації.

---

### Кейс 3: Захист РЧ-тракту субгігагерцового радіомодуля (LoRa 868 МГц / 2.4 ГГц)

**Вихідні дані:**
- Інтерфейс: ВЧ-тракт антени з хвильовим імпедансом `Z_0 = 50` Ом;
- Робоча частота: 868 МГц (LoRa) або 2.4 ГГц (Bluetooth Low Energy / Zigbee);
- Потужність передавача: +14..+20 дБм (амплітуда РЧ-напруги до `V_RF_peak = 3.2` В);
- Максимально допустимі внесені втрати на антенному вході: `IL < 0.15` дБ.

**Аналіз та інженерне рішення:**
1. **Розрахунок ємності діода:** Втрати 0.15 дБ на частоті 2.4 ГГц:
   
   ```text
   C_j_max = √( 10^(0.15/10) - 1 ) / ( π · 2.4 · 10⁹ Гц · 50 Ом ) ≈ 0.187 / ( 3.77 · 10¹¹ ) ≈ 0.49 пФ
   ```
   
   Для збереження чутливості приймача обирається надмалоємнісний РЧ-діод із ємністю `C_j = 0.10..0.15` пФ.
2. **Компенсація паразитної ємності (T-Match Filter):** Для повної нейтралізації впливу бар'єрної ємності діода `C_j` на хвильовий імпеданс лінії її інтегрують у структуру Т-подібного низькочастотного фільтра Баттерворта або Бесселя 3-го порядку. З обох боків контактного майданчика TVS розраховуються короткі відрізки вузьких мікросмужкових доріжок підвищеного хвильового імпедансу (`Z_narrow = 85` Ом), які діють як послідовні індуктивності `L_comp`:
   
   ```text
   L_comp = C_j · Z_0² / 2 = 0.15 · 10⁻¹² Ф · (50 Ом)² / 2 ≈ 0.187 нГн
   ```
   
   Необхідна довжина компенсувальної ділянки мікросмужки довжиною `l_comp` при питомій індуктивності `L_0 ≈ 0.8` нГн/мм становить:
   
   ```text
   l_comp = L_comp / L_0 = 0.187 нГн / 0.8 нГн/мм ≈ 0.23 мм
   ```
   
   Ця індуктивність утворює узгоджену лінію штучної затримки з характеристичним імпедансом строго 50 Ом на робочій частоті, що зводить коефіцієнт стоячої хвилі (VSWR) до величини `VSWR < 1.05` та забезпечує ідеальну лінійність фази в смузі пропускання без спотворення форми РЧ-модульованих імпульсів.

---

### Кейс 4: Захист силової шини живлення USB Type-C Power Delivery (20 В / 5 А — 100 Вт)

**Вихідні дані:**
- Інтерфейс: Силова шина `V_BUS` стандарту USB Type-C PD (напруга перемикається між 5 В, 9 В, 15 В та 20 В, струм до 5 А);
- Випробувальний рівень: IEC 61000-4-2 Level 4 (8 кВ контакт) та перенапруги гарячого підключення (Hot-Plug LC Ringing);
- Максимальна напруга входу контролера живлення: `V_max_PMIC = 28.0` В.

**Аналіз та інженерне рішення:**
1. **Явище резонансного перенапруження при гарячому підключенні (Hot-Plug LC Ringing):** При підключенні довгого кабелю USB (індуктивність `L_cable ≈ 1..2` мкГн) до пристрою з керамічними конденсаторами на вході (`C_in ≈ 20` мкФ із надмалим ESR порядка 5 мОм) утворюється слабкозатухаючий коливальний контур. При подачі напруги 20 В стрибок напруги на конденсаторі досягає:
   
   ```text
   V_peak_ring = 2 · V_supply = 2 · 20 В = 40.0 В!
   ```
   
   Якщо TVS-діод має напругу пробою нижче 40 В, він спрацьовуватиме при кожному звичайному підключенні кабелю і згорить через велику накопичену енергію джерела живлення.
2. **Вибір робочої напруги TVS:** Для надійного розділення робочого діапазону та захисту обирається TVS-діод з робочою напругою `V_RWM = 24.0..26.0` В та напругою пробою `V_BR = 27.5..29.0` В.
3. **Заборона Snapback:** На силових шинах із струмом 5 А використання Snapback категорично неприпустиме через 100% ймовірність виникнення стійкого Latch-up. Застосовуються виключно потужні TVS-діоди лавинного типу в корпусах SMB/SMC або DFN2020 потужністю `P_pk ≥ 600..1500` Вт (імпульс 8/20 мкс).

---

## Інженерний чекліст контролю топології друкованої плати

Перед відправкою Gerber-файлів на фабрику перевірте топологію за наступним чеклістом:

- [ ] **1. Відстань до роз'єму:** TVS-діод розташований на відстані менше 3 мм від металевих контактів вхідного роз'єму.
- [ ] **2. Відсутність відгалужень (Zero Stub):** Сигнальна доріжка проходить строго крізь контактні площадки TVS за топологією Feed-Through.
- [ ] **3. Матриця перехідних отворів землі:** Земляний майданчик TVS підключений до полігону GND щонайменше 2–4 паралельними перехідними отворами з відстанню між отворами `≥ 1.5` мм.
- [ ] **4. Суцільність опорного шару:** На внутрішньому шарі L2 (GND) безпосередньо під TVS та роз'ємом відсутні сигнальні траси та вирізи.
- [ ] **5. Запас напруги Latch-up:** Для діодів зі структурою Snapback перевірено умову `V_hold > 1.10 · V_supply_max`.
- [ ] **6. Координація дроселів CMC:** TVS-діод розташований **перед** синфазним дроселем (з боку роз'єму), а не після нього.
- [ ] **7. Захисні клітки Guard Stitching:** По периметру плати навколо роз'ємів прошито заземлювальні отвори з кроком не більше 2.0 мм.
- [ ] **8. Смуга пропускання швидкісних ліній:** Для інтерфейсів зі швидкістю понад 5 Гбіт/с ємність діода `C_j` не перевищує 0.35 пФ.
- [ ] **9. Розділення земель:** Металевий корпус роз'єму підключений до землі шасі (Chassis GND) або ізольований через паралельний високовольтний ланцюг 1–10 нФ / 2 кВ + 1 МОм.
- [ ] **10. Послідовне демпфування SEED:** На лініях зі швидкістю до 480 Мбіт/с встановлено послідовний резистор номіналом 10–33 Ом між TVS та входом мікросхеми.

---

## Інструкція зі збирання, тестування та запуску програми

Для збирання та запуску симулятора використовуйте стандартні інструменти збірки GNU/Clang:

```bash
# 1. Збирання модуля мовою C99:
gcc -std=c99 -O3 -Wall -Wextra esd_designer.c -lm -o esd_designer_c

# 2. Збирання модуля мовою C++20:
g++ -std=c++20 -O3 -Wall -Wextra esd_designer.cpp -o esd_designer_cpp

# 3. Запуск симулятора та генерація звіту:
./esd_designer_cpp
```

Програма виконує перевірку всіх закладених математичних критеріїв, перевіряє сумісність з параметрами навантаження та виводить форматований інженерний протокол із зазначенням статусу проходження кожного тесту.
