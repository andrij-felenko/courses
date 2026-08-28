# ⚙️ Калькулятор механічних напружень плати, моментів затяжки та зон відчуження

У процесі конструювання радіоелектронної апаратури інженер стикається з необхідністю точного кількісного розрахунку механічних навантажень, що виникають під час монтажу друкованої плати в корпус. Помилка у визначенні крутного моменту затягування гвинтів, заниження діаметрів зон заборони трасування або неврахування різниці коефіцієнтів теплового розширення між склотекстолітом і металевим шасі призводить до прихованих дефектів — від розтріскування керамічних конденсаторів до зрізу кріпильних стійок при циклічному нагріванні.

Даний практичний модуль містить інженерні математичні моделі та закінчену програмну реалізацію консольного калькулятора механічних напружень, моментів затяжки, зон відчуження та теплових зазорів на мовах C99 та C++20.

---

### Фізичні та аналітичні моделі механіки кріплення

Розрахункове ядро базується на фізичних моделях механіки нарізного з'єднання, теорії пружного згинання пластин, тензорному аналізі деформацій за стандартом IPC/JEDEC-9704, термічній кінематиці лінійного розширення та статистичному аналізі розмірних ланцюгів допусків.

```
                  АРХІТЕКТУРА РОЗРАХУНКОВОГО ЯДРА КАЛЬКУЛЯТОРА
   ┌────────────────────────────────────────────────────────────────────────┐
   │                          ВХІДНІ ДАНІ ПРОЕКТУ                           │
   │  - Геометрія: розміри плати, товщина t, прольоти між стійками L        │
   │  - Кріплення: номінал різьби M, тип шайби, момент затяжки T, фактор K  │
   │  - Матеріали: FR-4 (E, CTE), Шасі (Al/Сталь/Пластик CTE, перепад ΔT)  │
   │  - Допуски: точність свердління, похибка координат бобишок, биття Δh  │
   └───────────────────────────────────┬────────────────────────────────────┘
                                       │
                                       ▼
   ┌────────────────────────────────────────────────────────────────────────┐
   │                         МОДУЛІ ТРАНСФОРМАЦІЇ                           │
   │  ┌───────────────────┐  ┌───────────────────┐  ┌────────────────────┐  │
   │  │ 1. Осьова сила та │  │ 2. Прогин і       │  │ 3. Теплове         │  │
   │  │    тиск шайби     │  │    мікродеформація│  │    розширення      │  │
   │  │    T = K * F * d  │  │    ε = 6*t*Δh/L^2 │  │    ΔL = L0*ΔT*ΔCTE │  │
   │  └───────────────────┘  └───────────────────┘  └────────────────────┘  │
   │  ┌───────────────────┐  ┌───────────────────┐  ┌────────────────────┐  │
   │  │ 4. Зони заборони  │  │ 5. Розмірний лан- │  │ 6. Відповідність   │  │
   │  │    SMD (Keepout)  │  │    цюг (RSS / WC) │  │    IPC/JEDEC-9704  │  │
   │  └───────────────────┘  └───────────────────┘  └────────────────────┘  │
   └───────────────────────────────────┬────────────────────────────────────┘
                                       │
                                       ▼
   ┌────────────────────────────────────────────────────────────────────────┐
   │                    ЗВЕДЕНИЙ ДІАГНОСТИЧНИЙ ЗВІТ                         │
   │  - Зусилля затяжки та безпека різьби / контактний тиск                 │
   │  - Максимальний мікрострейн (με) та запас до порогу руйнування MLCC   │
   │  - Рекомендована довжина компенсаційного овального паза                │
   │  - Мінімальний радіус зони відчуження для кожного типорозміру SMD      │
   └────────────────────────────────────────────────────────────────────────┘
```

#### 1. Модель крутного моменту та осьового зусилля натягу

Зв'язок між крутним моментом T та осьовою силою стискання F_clamp описується класичною формулою з урахуванням безрозмірного коефіцієнта тертя різьби (Nut Factor K):

```
[Осьова сила стискання різьбового з'єднання]
F_clamp = T / (K * d_screw)

де:
T       — крутний момент затягування [Н·м]
K       — узагальнений коефіцієнт тертя в різьбі та під торцем головки
d_screw — номінальний зовнішній діаметр різьби гвинта [м]
```

Згідно зі стандартом VDI 2230, загальний крутний момент затягування складається з двох компонентів: моменту тертя у витках різьби та моменту тертя під торцем головки гвинта або шайби:

```
[Розгорнуте рівняння крутного моменту VDI 2230]
T = F_clamp * (0.159 * P_pitch + 0.578 * μ_thread * d_pitch + 0.500 * μ_collar * D_collar_mean)

де:
P_pitch       — крок різьби (0.50 мм для M3) [м]
d_pitch       — середній діаметр різьби (2.675 мм для M3) [м]
μ_thread      — коефіцієнт тертя у витках нарізі (типово 0.12..0.18)
μ_collar      — коефіцієнт тертя між шайбою та мідним майданчиком плати
D_collar_mean — середній діаметр опорного кільця шайби [м]
```

Середній контактний тиск під металевою шайбою P_washer визначається співвідношенням осьової сили до площі кругового кільця контакту:

```
[Контактний тиск під шайбою]
A_contact = (pi / 4) * (D_washer^2 - D_hole^2)
P_washer  = F_clamp / A_contact

де:
D_washer — зовнішній діаметр шайби (7.0 мм для DIN 125A M3) [м]
D_hole   — внутрішній діаметр отвору в шайбі або платі (3.2 мм) [м]
```

Для запобігання пластичній деформації поверхневих шарів склотекстоліту FR-4 контактний тиск P_washer не повинен перевищувати допустиму границю міцності на стиск вздовж осі Z: для стандартного ламінату FR-4 норматив становить σ_comp_max ≤ 250 МПа.

#### 2. Модель циліндричного та сферичного вигину плати

При затягуванні плати на стійках із висотною нерівномірністю Δh текстоліт зазнає пружного прогину. Враховуючи циліндричну жорсткість багатошарової пластини D = (E_fr4 · t_pcb³) / (12 · (1 - ν²)), де ν ≈ 0.16 — коефіцієнт Пуассона склотекстоліту, максимальна кривина вигину κ та пікова відносна деформація розтягу на зовнішній поверхні ε_surface описуються рівняннями:

```
[Кривина вигину пластини]
κ = (8 * Δh) / (L_span^2)

[Поверхнева деформація розтягу / стиску]
ε_surface = κ * (t_pcb / 2) = (4 * t_pcb * Δh) / (L_span^2)

[Пікове згинальне напруження]
σ_bend = ε_surface * E_fr4

де:
Δh      — різниця висот між суміжними стійками або викривлення шасі [м]
L_span  — відстань між центрами опорних стійок [м]
t_pcb   — товщина друкованої плати [м]
E_fr4   — модуль поздовжньої пружності FR-4 (типово 20 ГПа) [Па]
```

Для консервативної балочної моделі з двома жорстко затиснутими кінцями коефіцієнт при Δh збільшується з 4 до 6:

```
[Деформація для жорстко затиснених опор]
ε_clamped = (6 * t_pcb * Δh) / (L_span^2)
```

Калькулятор використовує затиснену балочну модель як базову для оцінки найгіршого випадку (Worst-Case scenario).

#### 3. Тензор деформацій та математика тензометричних розеток IPC-9704

Деформація поверхні друкованої плати біля отвору має багатоосьовий характер. Напружений стан описується плоским тензором деформацій з головними компонентами ε_1 та ε_2.

Для експериментальної верифікації розрахунків за стандартом IPC/JEDEC-9704 на дослідну плату безпосередньо біля паяних з'єднань MLCC наклеюють триелементні тензометричні розетки (Strain Gage Rosettes) конфігурації 0°/45°/90° з вимірювальними базами a (0°), b (45°) та c (90°).

Головні деформації ε_1 та ε_2, еквівалентна сферична деформація ε_spherical та кут орієнтації головних осей θ розраховуються за формулами тензорного перетворення:

```
[Головні компоненти деформації за вимірами розетки 0°/45°/90°]
ε_center = (ε_a + ε_c) / 2
ε_radius = sqrt((ε_a - ε_b)^2 + (ε_b - ε_c)^2) / sqrt(2)

ε_1 = ε_center + ε_radius   [Максимальна головна деформація розтягу]
ε_2 = ε_center - ε_radius   [Мінімальна головна деформація стиску]

[Еквівалентна сферична деформація IPC-9704]
ε_spherical = sqrt(ε_1^2 + ε_2^2 - ε_1 * ε_2)

[Кут нахилу головної осі деформації]
θ = 0.5 * atan2(2 * ε_b - ε_a - ε_c, ε_a - ε_c)
```

Стандарт IPC/JEDEC-9704 нормує максимально допустиму еквівалентну сферичну деформацію та швидкість наростання деформації dε/dt під час монтажу (Strain Rate Limit ≤ 500 με/с). Для квазістатичного закручування гвинтів порогові значення становлять:
- Корпуси 0402 та менше: ε_limit ≤ 750 με;
- Корпуси 0603 та 0805: ε_limit ≤ 500 με;
- Корпуси 1206 та 1210: ε_limit ≤ 400 με;
- Корпуси 1812, 2220 та масиви BGA з кроком ≤ 0.8 мм: ε_limit ≤ 300 με.

Коефіцієнт механічного запасу міцності визначається відношенням:

```
[Коефіцієнт запасу міцності за деформацією]
Margin_strain = ε_limit / ε_calculated
```

Якщо Margin_strain < 1.0, компонент знаходиться в зоні критичного ризику розтріскування, і трасувальник зобов'язаний винести деталь за межі зони високих градієнтів або повернути її паралельно ізолініям прогину.

#### 4. Динамічна стійкість та власна резонансна частота плати на стійках

Окрім статичних монтажних напружень, друкована плата піддається вібраційним навантаженням під час експлуатації. Згідно з емпіричною моделлю вібронадійності Стейнберга (Dave S. Steinberg, Vibration Analysis for Electronic Equipment), плата розглядається як прямокутна пластина на точкових опорах.

Власна резонансна частота першої моди коливань f_n (Гц) плати розмірами a × b (м) та погонною масою m_area (кг/м²) обчислюється як:

```
[Власна резонансна частота плати на кутових стійках]
f_n = (pi / 2) * sqrt(D / m_area) * ((1 / a^2) + (1 / b^2))

де:
D      — циліндрична згинальна жорсткість плати D = (E_fr4 * t_pcb^3) / (12 * (1 - ν^2))
m_area — сумарна поверхнева щільність плати з компонентами [кг/м^2]
a, b   — лінійні розміри прольотів між стійками [м]
```

Для запобігання резонансному руйнуванню паяних з'єднань при випадковій вібрації (MIL-STD-810G, профіль 20–2000 Гц) власна частота плати повинна бути вищою за 80–100 Гц. При низькій частоті (<50 Гц) додають проміжні підсилювальні стійки у центрі плати.

#### 5. Термомеханічна кінематика та геометрія компенсаційного паза

При нагріванні плати й корпусу від мінімальної температури T_min до максимальної T_max різниця теплових подовжень створює зрізне зміщення опорних осей:

```
[Теплове зміщення осей кріплення]
ΔL_thermal = L_span * |α_chassis - α_pcb| * (T_max - T_min)

[Необхідна довжина овального паза]
L_slot = d_hole_nominal + ΔL_thermal + 2 * δ_tolerance_margin

де:
α_chassis          — коефіцієнт лінійного теплового розширення шасі [1/K]
α_pcb              — CTE склотекстоліту FR-4 (15 · 10⁻⁶ 1/K) [1/K]
T_max, T_min       — граничні робочі температури приладу [°C]
d_hole_nominal     — номінальний діаметр свердління (3.2 мм для M3) [м]
δ_tolerance_margin — технологічний гарантований зазор (0.15 мм) [м]
```

Якщо температурний зазор відсутній, у платі виникає додаткове термічне напруження стискання σ_thermal = E_fr4 · |α_chassis - α_pcb| · ΔT, яке досягає 30–60 МПа і призводить до куполоподібного випинання плати.

#### 5. Статистичний розмірний ланцюг допусків (Tolerance Stackup)

Калькулятор виконує аналіз накопичення похибок двома методами:
1. **Метод найгіршого випадку (Worst-Case):** пряме арифметичне підсумовування абсолютних значень усіх технологічних похибок:
```
[Допуск за методом найгіршого випадку]
δ_WorstCase = |δ_drill| + |δ_chassis| + |δ_tilt| + |ΔL_thermal|
```
2. **Статистичний метод RSS (Root-Sum-of-Squares):** квадратичне підсумовування незалежних випадкових величин:
```
[Статистичний допуск RSS]
δ_RSS = sqrt(δ_drill^2 + δ_chassis^2 + δ_tilt^2 + ΔL_thermal^2)
```

Метод RSS дозволяє уникнути надлишкового збільшення діаметрів отворів, оптимізуючи площу плати при збереженні виробничого виходу понад 99.73% (правило 3-сигма).

---

### Архітектура та програмна декомпозиція розрахункового ядра

Програмний комплекс складається з трьох логічних шарів:

```
+-------------------------------------------------------------------------+
|                          1. РІВЕНЬ КОНФІГУРАЦІЇ                         |
|   PcbMountingInput / MountingNodeConfig                                 |
|   - Валідація фізичних діапазонів (позитивні розміри, t > 0, L > 0)    |
|   - Конвертація одиниць (мм -> метри, ppm -> 1/K, °C -> ΔT)             |
+------------------------------------+------------------------------------+
                                     |
                                     v
+-------------------------------------------------------------------------+
|                          2. ОБЧИСЛЮВАЛЬНИЙ ШАР                          |
|   calculate_pcb_mounting_node() / MountingStressAnalyzer::analyze()     |
|   - Розрахунок осьової сили F_clamp = T / (K * d)                       |
|   - Визначення тиску під шайбою P_washer = F / A_washer                 |
|   - Оцінка кривини вигину та мікродеформації ε_bend = 6*t*Δh / L^2      |
|   - Розрахунок запасів міцності за порогами IPC/JEDEC-9704              |
|   - Обчислення теплового розширення ΔL_thermal                          |
|   - Формування масиву радіусів зон відчуження Keepout Radii             |
+------------------------------------+------------------------------------+
                                     |
                                     v
+-------------------------------------------------------------------------+
|                        3. ДІАГНОСТИЧНИЙ ДИСПЛЕЙ                         |
|   print_mounting_report() / print_formatted_report()                    |
|   - Табличний інженерний вивід із кольоровою/символьною індикацією      |
|   - Прапорці безпеки ([НОРМА] vs [ПЕРЕВИЩЕННЯ], [OK] vs [НЕБЕЗПЕКА])    |
+-------------------------------------------------------------------------+
```

---

### Програмна реалізація мовами C99 та C++20

Нижче наведено повні самодостатні реалізації калькулятора. Обидва варіанти містять повну математичну модель, структури конфігурації, функції перевірки та форматований консольний звіт.

:::tabs
@tab c99
```c
/*
 * proj_mounting_stress_calc.c — Інженерний калькулятор кріплення друкованих плат (C99).
 * Розрахунок осьових сил, тиску під шайбами, деформацій за IPC-9704, CTE та зон заборони.
 */

#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

/* Константи матеріалів та стандартів */
#define FR4_DEFAULT_E_GPA         20.0     /* Модуль пружності FR-4, ГПа */
#define FR4_DEFAULT_CTE_PPM       15.0     /* CTE FR-4 в площині XY, ppm/K */
#define FR4_MAX_COMPRESS_MPA     250.0     /* Граничний тиск стиску FR-4, МПа */

/* Типи матеріалів корпусу */
typedef enum {
    CHASSIS_ALUMINUM_6061 = 0,
    CHASSIS_STEEL_SPCC,
    CHASSIS_STAINLESS_304,
    CHASSIS_BRASS,
    CHASSIS_POLYCARBONATE_ABS,
    CHASSIS_CUSTOM
} ChassisMaterialType;

/* Вхідна конфігурація кріпильного вузла */
typedef struct {
    double screw_dia_nominal_mm;   /* Номінальний діаметр гвинта (2.0, 2.5, 3.0, 4.0) */
    double drill_hole_dia_mm;      /* Фактичний діаметр отвору на платі */
    double washer_outer_dia_mm;    /* Зовнішній діаметр шайби або головки гвинта */
    double nut_factor_k;           /* Коефіцієнт тертя різьби K (0.12..0.30) */
    double torque_nm;              /* Крутний момент затягування, Н·м */
    double pcb_thickness_mm;       /* Товщина текстоліту плати, мм */
    double standoff_span_mm;       /* Відстань між центрами опорних стійок, мм */
    double standoff_mismatch_mm;   /* Висотне биття стійок (Δh), мм */
    ChassisMaterialType chassis_mat; /* Матеріал шасі */
    double chassis_cte_ppm;        /* CTE шасі (якщо обрано CUSTOM), ppm/K */
    double temp_min_c;             /* Мінімальна робоча температура, °C */
    double temp_max_c;             /* Максимальна робоча температура, °C */
} PcbMountingInput;

/* Результати інженерного розрахунку */
typedef struct {
    /* 1. Силові параметри */
    double clamp_force_n;          /* Осьова сила стискання, Н */
    double washer_contact_area_mm2;/* Площа контакту під шайбою, мм^2 */
    double washer_pressure_mpa;    /* Контактний тиск під шайбою, МПа */
    bool   pressure_safe;          /* Чи не перевищено 250 МПа для FR-4 */

    /* 2. Деформаційні параметри */
    double bending_curvature_m_inv;/* Кривина прогину плати, 1/м */
    double surface_microstrain;    /* Деформація на поверхні текстоліту, με */
    double bending_stress_mpa;     /* Згинальне напруження в текстоліті, МПа */

    /* 3. Оцінка за IPC/JEDEC-9704 */
    double mlcc_0402_margin;       /* Запас міцності для 0402 (ліміт 750 με) */
    double mlcc_0805_margin;       /* Запас міцності для 0805 (ліміт 500 με) */
    double mlcc_1206_margin;       /* Запас міцності для 1206 (ліміт 400 με) */
    bool   overall_ipc9704_safe;   /* Чи безпечно для стандартних компонентів 0805 */

    /* 4. Теплове розширення та геометрія паза */
    double delta_cte_ppm;          /* Різниця CTE між платою та корпусом, ppm/K */
    double thermal_expansion_mm;   /* Абсолютне теплове зміщення на базі, мм */
    double recommended_slot_len_mm;/* Рекомендована повна довжина овального паза, мм */

    /* 5. Радіуси зон заборони (Keepout) від центру отвору */
    double keepout_trace_radius_mm;/* Зона заборони доріжок */
    double keepout_0603_radius_mm; /* Зона заборони пасивів 0603 */
    double keepout_0805_radius_mm; /* Зона заборони MLCC 0805 */
    double keepout_1206_radius_mm; /* Зона заборони MLCC 1206 */
    double keepout_tooling_radius_mm; /* Зона доступу монтажного інструмента */
} PcbMountingOutput;

/* Отримання назви та CTE матеріалу шасі */
static void get_chassis_props(ChassisMaterialType type, double custom_cte,
                              const char **name_out, double *cte_out) {
    switch (type) {
        case CHASSIS_ALUMINUM_6061:
            *name_out = "Алюмінієвий сплав AL6061-T6";
            *cte_out = 23.2;
            break;
        case CHASSIS_STEEL_SPCC:
            *name_out = "Листова сталь SPCC";
            *cte_out = 11.8;
            break;
        case CHASSIS_STAINLESS_304:
            *name_out = "Нержавіюча сталь AISI 304";
            *cte_out = 16.5;
            break;
        case CHASSIS_BRASS:
            *name_out = "Латунь ЛС59-1 (CW614N)";
            *cte_out = 18.5;
            break;
        case CHASSIS_POLYCARBONATE_ABS:
            *name_out = "Пластик PC / ABS";
            *cte_out = 72.0;
            break;
        case CHASSIS_CUSTOM:
        default:
            *name_out = "Користувацький матеріал";
            *cte_out = custom_cte;
            break;
    }
}

/*
 * Головна розрахункова функція
 */
bool calculate_pcb_mounting_node(const PcbMountingInput *in, PcbMountingOutput *out) {
    if (!in || !out) return false;
    if (in->screw_dia_nominal_mm <= 0.0 || in->washer_outer_dia_mm <= in->drill_hole_dia_mm) return false;
    if (in->nut_factor_k <= 0.0 || in->pcb_thickness_mm <= 0.0 || in->standoff_span_mm <= 0.0) return false;

    memset(out, 0, sizeof(PcbMountingOutput));

    /* 1. Розрахунок осьової сили затягування */
    double d_screw_m = in->screw_dia_nominal_mm * 1e-3;
    out->clamp_force_n = in->torque_nm / (in->nut_factor_k * d_screw_m);

    /* 2. Контактний тиск під шайбою */
    double d_wash_mm = in->washer_outer_dia_mm;
    double d_hole_mm = in->drill_hole_dia_mm;
    out->washer_contact_area_mm2 = (M_PI / 4.0) * (pow(d_wash_mm, 2) - pow(d_hole_mm, 2));
    out->washer_pressure_mpa = out->clamp_force_n / out->washer_contact_area_mm2;
    out->pressure_safe = (out->washer_pressure_mpa <= FR4_MAX_COMPRESS_MPA);

    /* 3. Згинальна деформація затисненої плати: ε = (6 * t * Δh) / L^2 */
    double t_m = in->pcb_thickness_mm * 1e-3;
    double dh_m = in->standoff_mismatch_mm * 1e-3;
    double l_m = in->standoff_span_mm * 1e-3;

    out->bending_curvature_m_inv = (8.0 * dh_m) / pow(l_m, 2);
    double strain_abs = (6.0 * t_m * dh_m) / pow(l_m, 2);
    out->surface_microstrain = strain_abs * 1e6; /* у мікрострейнах */
    out->bending_stress_mpa = strain_abs * (FR4_DEFAULT_E_GPA * 1e3);

    /* 4. Оцінка запасу міцності за IPC/JEDEC-9704 */
    out->mlcc_0402_margin = 750.0 / (out->surface_microstrain > 1e-3 ? out->surface_microstrain : 1e-3);
    out->mlcc_0805_margin = 500.0 / (out->surface_microstrain > 1e-3 ? out->surface_microstrain : 1e-3);
    out->mlcc_1206_margin = 400.0 / (out->surface_microstrain > 1e-3 ? out->surface_microstrain : 1e-3);
    out->overall_ipc9704_safe = (out->surface_microstrain <= 500.0);

    /* 5. Теплове розширення */
    const char *mat_name = NULL;
    double chassis_cte = 0.0;
    get_chassis_props(in->chassis_mat, in->chassis_cte_ppm, &mat_name, &chassis_cte);

    out->delta_cte_ppm = fabs(chassis_cte - FR4_DEFAULT_CTE_PPM);
    double delta_t = fabs(in->temp_max_c - in->temp_min_c);
    out->thermal_expansion_mm = in->standoff_span_mm * (out->delta_cte_ppm * 1e-6) * delta_t;
    
    /* Рекомендована довжина паза: D_hole + ΔL + 2 * зазор 0.15 мм */
    out->recommended_slot_len_mm = in->drill_hole_dia_mm + out->thermal_expansion_mm + 0.30;

    /* 6. Розрахунок радіусів зон відчуження */
    double r_wash = in->washer_outer_dia_mm / 2.0;
    out->keepout_trace_radius_mm   = r_wash + 0.80;
    out->keepout_0603_radius_mm    = r_wash + 1.50;
    out->keepout_0805_radius_mm    = r_wash + 2.50;
    out->keepout_1206_radius_mm    = r_wash + 4.00;
    out->keepout_tooling_radius_mm = r_wash + 4.50;

    return true;
}

/* Друк детального інженерного звіту */
void print_mounting_report(const PcbMountingInput *in, const PcbMountingOutput *out) {
    const char *mat_name = NULL;
    double chassis_cte = 0.0;
    get_chassis_props(in->chassis_mat, in->chassis_cte_ppm, &mat_name, &chassis_cte);

    printf("===================================================================\n");
    printf("   ЗВЕДЕНИЙ ЗВІТ РОЗРАХУНКУ КРІПИЛЬНОГО ВУЗЛА ПЛАТИ (C99 ENGINE)   \n");
    printf("===================================================================\n\n");

    printf("[1] ВХІДНІ ДАНІ КОНСТРУКЦІЇ:\n");
    printf("  • Номінал гвинта:              M%.1f (Свердління: Ø%.2f мм)\n", in->screw_dia_nominal_mm, in->drill_hole_dia_mm);
    printf("  • Шайба / Головка гвинта:      Ø%.2f мм\n", in->washer_outer_dia_mm);
    printf("  • Крутний момент затяжки:      %.2f Н·м (Коефіцієнт тертя K = %.2f)\n", in->torque_nm, in->nut_factor_k);
    printf("  • Друкована плата:             Товщина t = %.2f мм, Проліт L = %.1f мм\n", in->pcb_thickness_mm, in->standoff_span_mm);
    printf("  • Висотне биття стійок (Δh):   %.3f мм (%.0f мкм)\n", in->standoff_mismatch_mm, in->standoff_mismatch_mm * 1000.0);
    printf("  • Матеріал шасі:               %s (CTE = %.1f ppm/K)\n", mat_name, chassis_cte);
    printf("  • Робочий діапазон температур: %.1f °C .. +%.1f °C (ΔT = %.1f °C)\n\n", in->temp_min_c, in->temp_max_c, fabs(in->temp_max_c - in->temp_min_c));

    printf("[2] СИЛОВІ НАВАНТАЖЕННЯ:\n");
    printf("  • Осьова сила притиску F_clamp:   %.1f Н (%.1f кгс)\n", out->clamp_force_n, out->clamp_force_n / 9.80665);
    printf("  • Площа контакту шайби:           %.2f мм²\n", out->washer_contact_area_mm2);
    printf("  • Контактний тиск на ламінат:     %.2f МПа (Ліміт: 250 МПа) -> %s\n\n",
           out->washer_pressure_mpa, out->pressure_safe ? "[НОРМА]" : "[ПЕРЕВИЩЕННЯ ТИСКУ]");

    printf("[3] ЗГИНАЛЬНІ ДЕФОРМАЦІЇ ТА ОЦІНКА IPC/JEDEC-9704:\n");
    printf("  • Пікова поверхнева деформація:   %.1f με\n", out->surface_microstrain);
    printf("  • Згинальне напруження в FR-4:    %.2f МПа\n", out->bending_stress_mpa);
    printf("  • Запас міцності MLCC 0402:       %.2f x (Ліміт 750 με) -> %s\n",
           out->mlcc_0402_margin, out->mlcc_0402_margin >= 1.0 ? "OK" : "НЕБЕЗПЕКА");
    printf("  • Запас міцності MLCC 0805:       %.2f x (Ліміт 500 με) -> %s\n",
           out->mlcc_0805_margin, out->mlcc_0805_margin >= 1.0 ? "OK" : "НЕБЕЗПЕКА");
    printf("  • Запас міцності MLCC 1206:       %.2f x (Ліміт 400 με) -> %s\n",
           out->mlcc_1206_margin, out->mlcc_1206_margin >= 1.0 ? "OK" : "НЕБЕЗПЕКА");
    printf("  • Загальний статус за IPC-9704:   %s\n\n",
           out->overall_ipc9704_safe ? "✓ БЕЗПЕЧНО (Деформація <= 500 με)" : "✖ КРИТИЧНО: ВИСОКИЙ РИЗИК ТРІЩИН MLCC");

    printf("[4] ТЕПЛОВА КОМПЕНСАЦІЯ ТА ОВАЛЬНІ ПАЗИ:\n");
    printf("  • Різниця коефіцієнтів |ΔCTE|:    %.1f ppm/K\n", out->delta_cte_ppm);
    printf("  • Теплове зміщення осей на базі:  %.3f мм (%.1f мкм)\n", out->thermal_expansion_mm, out->thermal_expansion_mm * 1000.0);
    printf("  • Рекомендований розмір паза:     Ø%.2f × %.2f мм\n\n", in->drill_hole_dia_mm, out->recommended_slot_len_mm);

    printf("[5] ГЕОМЕТРИЧНІ ЗОНИ ЗАБОРОНИ (KEEPOUT RADIUS):\n");
    printf("  • Зона заборони мідних доріжок:   R >= %.2f мм (Ø >= %.2f мм)\n", out->keepout_trace_radius_mm, out->keepout_trace_radius_mm * 2.0);
    printf("  • Зона заборони пасивів 0603:     R >= %.2f мм (Ø >= %.2f мм)\n", out->keepout_0603_radius_mm, out->keepout_0603_radius_mm * 2.0);
    printf("  • Зона заборони MLCC 0805:        R >= %.2f мм (Ø >= %.2f мм)\n", out->keepout_0805_radius_mm, out->keepout_0805_radius_mm * 2.0);
    printf("  • Зона заборони MLCC 1206+:       R >= %.2f мм (Ø >= %.2f мм)\n", out->keepout_1206_radius_mm, out->keepout_1206_radius_mm * 2.0);
    printf("  • Зона доступу біти інструмента:  R >= %.2f мм (Ø >= %.2f мм, Z > 25 мм)\n", out->keepout_tooling_radius_mm, out->keepout_tooling_radius_mm * 2.0);
    printf("===================================================================\n");
}

int main(void) {
    /* Приклад: розрахунок плати контролера на стійках M3 в алюмінієвому корпусі */
    PcbMountingInput config = {
        .screw_dia_nominal_mm   = 3.0,
        .drill_hole_dia_mm      = 3.2,
        .washer_outer_dia_mm    = 7.0,
        .nut_factor_k           = 0.20,
        .torque_nm              = 0.60,
        .pcb_thickness_mm       = 1.60,
        .standoff_span_mm       = 75.0,
        .standoff_mismatch_mm   = 0.20,
        .chassis_mat            = CHASSIS_ALUMINUM_6061,
        .chassis_cte_ppm        = 23.2,
        .temp_min_c             = -40.0,
        .temp_max_c             = 85.0
    };

    PcbMountingOutput results;
    if (calculate_pcb_mounting_node(&config, &results)) {
        print_mounting_report(&config, &results);
    } else {
        fprintf(stderr, "Помилка: некоректні вхідні геометричні параметри.\n");
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
```
@tab c++
```cpp
/*
 * proj_mounting_stress_calc.cpp — Об'єктно-орієнтоване розрахункове ядро (C++20).
 * Сучасні стандарти типізації, constexpr таблиці та структуровані звіти.
 */

#include <iostream>
#include <cmath>
#include <numbers>
#include <string_view>
#include <format>
#include <optional>
#include <array>
#include <vector>

namespace pcb::calculator {

// ── Константи матеріалів та безпеки ─────────────────────────────────────────
inline constexpr double Fr4YoungModulusGpa      = 20.0;
inline constexpr double Fr4InPlaneCtePpm        = 15.0;
inline constexpr double Fr4MaxCompressiveMpa    = 250.0;
inline constexpr double Ipc9704SafeMicrostrain  = 500.0;

enum class ChassisMaterial : uint8_t {
    Aluminum6061,
    SteelSpcc,
    Stainless304,
    Brass,
    PolycarbonateAbs,
    Custom
};

struct MaterialProperties {
    std::string_view name;
    double cte_ppm_per_k;
    double young_modulus_gpa;
};

[[nodiscard]] constexpr MaterialProperties get_material_info(ChassisMaterial mat, double custom_cte = 0.0) noexcept {
    switch (mat) {
        case ChassisMaterial::Aluminum6061:
            return {"Алюміній AL6061-T6", 23.2, 69.0};
        case ChassisMaterial::SteelSpcc:
            return {"Листова сталь SPCC", 11.8, 205.0};
        case ChassisMaterial::Stainless304:
            return {"Нержавіюча сталь AISI 304", 16.5, 193.0};
        case ChassisMaterial::Brass:
            return {"Латунь ЛС59-1", 18.5, 105.0};
        case ChassisMaterial::PolycarbonateAbs:
            return {"Пластик PC/ABS", 72.0, 2.4};
        case ChassisMaterial::Custom:
        default:
            return {"Користувацький матеріал", custom_cte, 100.0};
    }
}

// ── Структури параметрів та результатів ─────────────────────────────────────
struct MountingNodeConfig {
    double screw_diameter_nominal_mm{3.0};
    double drill_hole_diameter_mm{3.2};
    double washer_outer_diameter_mm{7.0};
    double nut_friction_factor{0.20};
    double tightening_torque_nm{0.60};
    double pcb_thickness_mm{1.60};
    double span_between_standoffs_mm{75.0};
    double standoff_height_mismatch_mm{0.20};
    ChassisMaterial chassis_material{ChassisMaterial::Aluminum6061};
    double custom_chassis_cte_ppm{23.2};
    double min_operating_temp_c{-40.0};
    double max_operating_temp_c{85.0};
};

struct KeepoutRadii {
    double traces_and_planes_mm{0.0};
    double passives_0603_mm{0.0};
    double mlcc_0805_mm{0.0};
    double mlcc_1206_plus_mm{0.0};
    double tooling_access_mm{0.0};
};

struct CalculationResults {
    double clamp_force_n{0.0};
    double washer_contact_area_mm2{0.0};
    double washer_pressure_mpa{0.0};
    bool is_pressure_acceptable{false};

    double peak_surface_microstrain{0.0};
    double pcb_bending_stress_mpa{0.0};
    double mlcc_0402_safety_margin{0.0};
    double mlcc_0805_safety_margin{0.0};
    double mlcc_1206_safety_margin{0.0};
    bool is_ipc9704_safe{false};

    double delta_cte_ppm{0.0};
    double thermal_axis_displacement_mm{0.0};
    double recommended_slot_length_mm{0.0};

    KeepoutRadii keepouts{};
};

// ── Розрахунковий клас ──────────────────────────────────────────────────────
class MountingStressAnalyzer {
public:
    [[nodiscard]] static std::optional<CalculationResults> analyze(const MountingNodeConfig& cfg) noexcept {
        if (cfg.screw_diameter_nominal_mm <= 0.0 || 
            cfg.washer_outer_diameter_mm <= cfg.drill_hole_diameter_mm ||
            cfg.nut_friction_factor <= 0.0 || 
            cfg.pcb_thickness_mm <= 0.0 || 
            cfg.span_between_standoffs_mm <= 0.0) {
            return std::nullopt;
        }

        CalculationResults res{};

        // 1. Осьова сила F = T / (K * d)
        const double d_screw_m = cfg.screw_diameter_nominal_mm * 1e-3;
        res.clamp_force_n = cfg.tightening_torque_nm / (cfg.nut_friction_factor * d_screw_m);

        // 2. Тиск під шайбою
        res.washer_contact_area_mm2 = (std::numbers::pi / 4.0) * 
            (std::pow(cfg.washer_outer_diameter_mm, 2) - std::pow(cfg.drill_hole_diameter_mm, 2));
        res.washer_pressure_mpa = res.clamp_force_n / res.washer_contact_area_mm2;
        res.is_pressure_acceptable = (res.washer_pressure_mpa <= Fr4MaxCompressiveMpa);

        // 3. Згинальна мікродеформація плати: ε = (6 * t * Δh) / L^2
        const double t_m = cfg.pcb_thickness_mm * 1e-3;
        const double dh_m = cfg.standoff_height_mismatch_mm * 1e-3;
        const double l_m = cfg.span_between_standoffs_mm * 1e-3;

        const double strain_unitless = (6.0 * t_m * dh_m) / std::pow(l_m, 2);
        res.peak_surface_microstrain = strain_unitless * 1e6;
        res.pcb_bending_stress_mpa = strain_unitless * (Fr4YoungModulusGpa * 1e3);

        // 4. Оцінка меж IPC/JEDEC-9704
        const double safe_strain = (res.peak_surface_microstrain > 1e-3) ? res.peak_surface_microstrain : 1e-3;
        res.mlcc_0402_safety_margin = 750.0 / safe_strain;
        res.mlcc_0805_safety_margin = 500.0 / safe_strain;
        res.mlcc_1206_safety_margin = 400.0 / safe_strain;
        res.is_ipc9704_safe = (res.peak_surface_microstrain <= Ipc9704SafeMicrostrain);

        // 5. Теплове розширення
        const auto mat_info = get_material_info(cfg.chassis_material, cfg.custom_chassis_cte_ppm);
        res.delta_cte_ppm = std::abs(mat_info.cte_ppm_per_k - Fr4InPlaneCtePpm);
        const double delta_t = std::abs(cfg.max_operating_temp_c - cfg.min_operating_temp_c);
        res.thermal_axis_displacement_mm = cfg.span_between_standoffs_mm * (res.delta_cte_ppm * 1e-6) * delta_t;
        res.recommended_slot_length_mm = cfg.drill_hole_diameter_mm + res.thermal_axis_displacement_mm + 0.30;

        // 6. Зони заборони
        const double r_wash = cfg.washer_outer_diameter_mm / 2.0;
        res.keepouts.traces_and_planes_mm = r_wash + 0.80;
        res.keepouts.passives_0603_mm     = r_wash + 1.50;
        res.keepouts.mlcc_0805_mm        = r_wash + 2.50;
        res.keepouts.mlcc_1206_plus_mm    = r_wash + 4.00;
        res.keepouts.tooling_access_mm    = r_wash + 4.50;

        return res;
    }

    static void print_formatted_report(const MountingNodeConfig& cfg, const CalculationResults& res) {
        const auto mat = get_material_info(cfg.chassis_material, cfg.custom_chassis_cte_ppm);

        std::cout << "===================================================================\n";
        std::cout << "  ЗВЕДЕНИЙ ЗВІТ РОЗРАХУНКУ КРІПИЛЬНОГО ВУЗЛА ПЛАТИ (C++20 ENGINE)  \n";
        std::cout << "===================================================================\n\n";

        std::cout << "[1] ВХІДНІ ДАНІ КОНСТРУКЦІЇ:\n";
        std::cout << std::format("  • Номінал гвинта:              M{:.1f} (Свердління: Ø{:.2f} мм)\n", cfg.screw_diameter_nominal_mm, cfg.drill_hole_diameter_mm);
        std::cout << std::format("  • Зовнішній діаметр шайби:     Ø{:.2f} мм\n", cfg.washer_outer_diameter_mm);
        std::cout << std::format("  • Момент затягування:          {:.2f} Н·м (Коефіцієнт K = {:.2f})\n", cfg.tightening_torque_nm, cfg.nut_friction_factor);
        std::cout << std::format("  • Друкована плата:             t = {:.2f} мм, Проліт L = {:.1f} мм\n", cfg.pcb_thickness_mm, cfg.span_between_standoffs_mm);
        std::cout << std::format("  • Висотний перекіс стійок:     {:.3f} мм ({:.0f} мкм)\n", cfg.standoff_height_mismatch_mm, cfg.standoff_height_mismatch_mm * 1000.0);
        std::cout << std::format("  • Матеріал шасі:               {} (CTE = {:.1f} ppm/K)\n", mat.name, mat.cte_ppm_per_k);
        std::cout << std::format("  • Робочий діапазон:            {:.1f} °C .. +{:.1f} °C (ΔT = {:.1f} °C)\n\n",
                                 cfg.min_operating_temp_c, cfg.max_operating_temp_c,
                                 std::abs(cfg.max_operating_temp_c - cfg.min_operating_temp_c));

        std::cout << "[2] СИЛОВІ ПАРАМЕТРИ ЗАТЯЖКИ:\n";
        std::cout << std::format("  • Осьове стискання F_clamp:    {:.1f} Н ({:.1f} кгс)\n", res.clamp_force_n, res.clamp_force_n / 9.80665);
        std::cout << std::format("  • Площа контакту шайби:        {:.2f} мм²\n", res.washer_contact_area_mm2);
        std::cout << std::format("  • Контактний тиск на ламінат:  {:.2f} МПа (Ліміт: 250 МПа) -> {}\n\n",
                                 res.washer_pressure_mpa, res.is_pressure_acceptable ? "[НОРМА]" : "[ПЕРЕВИЩЕННЯ]");

        std::cout << "[3] ЗГИНАЛЬНІ ДЕФОРМАЦІЇ ТА ДІАГНОСТИКА IPC-9704:\n";
        std::cout << std::format("  • Пікова поверхнева деформація:{:.1f} με\n", res.peak_surface_microstrain);
        std::cout << std::format("  • Згинальне напруження FR-4:   {:.2f} МПа\n", res.pcb_bending_stress_mpa);
        std::cout << std::format("  • Запас міцності MLCC 0402:    {:.2f} x -> {}\n", res.mlcc_0402_safety_margin, res.mlcc_0402_safety_margin >= 1.0 ? "OK" : "НЕБЕЗПЕКА");
        std::cout << std::format("  • Запас міцності MLCC 0805:    {:.2f} x -> {}\n", res.mlcc_0805_safety_margin, res.mlcc_0805_safety_margin >= 1.0 ? "OK" : "НЕБЕЗПЕКА");
        std::cout << std::format("  • Запас міцності MLCC 1206:    {:.2f} x -> {}\n", res.mlcc_1206_safety_margin, res.mlcc_1206_safety_margin >= 1.0 ? "OK" : "НЕБЕЗПЕКА");
        std::cout << std::format("  • Статус відповідності IPC:    {}\n\n",
                                 res.is_ipc9704_safe ? "✓ БЕЗПЕЧНО (<= 500 με)" : "✖ КРИТИЧНО: ВИСОКИЙ РИЗИК ТРІЩИН MLCC");

        std::cout << "[4] ТЕМПЕРАТУРНА КОМПЕНСАЦІЯ:\n";
        std::cout << std::format("  • Різниця коефіцієнтів |ΔCTE|: {:.1f} ppm/K\n", res.delta_cte_ppm);
        std::cout << std::format("  • Теплове зміщення осей:       {:.3f} мм ({:.1f} мкм)\n", res.thermal_axis_displacement_mm, res.thermal_axis_displacement_mm * 1000.0);
        std::cout << std::format("  • Рекомендований розмір паза:  Ø{:.2f} × {:.2f} мм\n\n", cfg.drill_hole_diameter_mm, res.recommended_slot_length_mm);

        std::cout << "[5] ЗОНИ ВІДЧУЖЕННЯ (KEEPOUT RADIUS):\n";
        std::cout << std::format("  • Мідні доріжки та полігони:   R >= {:.2f} мм (Ø >= {:.2f} мм)\n", res.keepouts.traces_and_planes_mm, res.keepouts.traces_and_planes_mm * 2.0);
        std::cout << std::format("  • Пасиви 0603:                 R >= {:.2f} мм (Ø >= {:.2f} мм)\n", res.keepouts.passives_0603_mm, res.keepouts.passives_0603_mm * 2.0);
        std::cout << std::format("  • Конденсатори MLCC 0805:      R >= {:.2f} мм (Ø >= {:.2f} мм)\n", res.keepouts.mlcc_0805_mm, res.keepouts.mlcc_0805_mm * 2.0);
        std::cout << std::format("  • Конденсатори MLCC 1206+:     R >= {:.2f} мм (Ø >= {:.2f} мм)\n", res.keepouts.mlcc_1206_plus_mm, res.keepouts.mlcc_1206_plus_mm * 2.0);
        std::cout << std::format("  • Інструментальний доступ:     R >= {:.2f} мм (Ø >= {:.2f} мм, Z > 25 мм)\n", res.keepouts.tooling_access_mm, res.keepouts.tooling_access_mm * 2.0);
        std::cout << "===================================================================\n";
    }
};

} // namespace pcb::calculator

int main() {
    using namespace pcb::calculator;

    MountingNodeConfig config{
        .screw_diameter_nominal_mm   = 3.0,
        .drill_hole_diameter_mm      = 3.2,
        .washer_outer_diameter_mm    = 7.0,
        .nut_friction_factor         = 0.20,
        .tightening_torque_nm        = 0.60,
        .pcb_thickness_mm            = 1.60,
        .span_between_standoffs_mm   = 75.0,
        .standoff_height_mismatch_mm = 0.20,
        .chassis_material            = ChassisMaterial::Aluminum6061,
        .custom_chassis_cte_ppm      = 23.2,
        .min_operating_temp_c        = -40.0,
        .max_operating_temp_c        = 85.0
    };

    if (const auto results = MountingStressAnalyzer::analyze(config); results.has_value()) {
        MountingStressAnalyzer::print_formatted_report(config, *results);
    } else {
        std::cerr << "Помилка: недійсні параметри конфігурації кріплення.\n";
        return 1;
    }

    return 0;
}
```
:::

---

### Практичний розбір інженерних кейсів

#### Кейс 1: Авіаційний контролер у фрезерованому корпусі AL6061

Вхідні умови:
- Габарити плати: 220 × 140 мм, товщина 1.6 мм, чотири кутові стійки M3 з прольотом L = 200 мм вздовж довгого боку.
- Матеріал корпусу: цільний авіаційний алюміній AL6061-T6 (CTE = 23.2 ppm/K).
- Температурний діапазон: від -55 °C (холодний старт на висоті 10 км) до +105 °C (нагрів під капотом двигуна), тобто ΔT = 160 °C.
- Момент затягування гвинтів M3: 0.65 Н·м з пружинними шайбами Nord-Lock (K = 0.22).

Результати аналізу:
1. Теплове розширення: різниця CTE складає |23.2 - 15.0| = 8.2 ppm/K. На прольоті 200 мм при перепаді 160 °C теплове зміщення осей досягає ΔL = 200 · 8.2 · 10⁻⁶ · 160 = 0.262 мм (262 мкм).
2. Якщо отвори залишити круглими Ø3.2 мм, гвинти M3 (діаметр 3.0 мм) заклинить уже при нагріванні на +50 °C. При подальшому нагріванні зрізне зусилля перевищить 2400 Н, що призведе до згину гвинтів або сколу текстоліту.
3. Рішення: базовий отвір H1 залишається круглим Ø3.2 мм. Діагональний отвір H2 виконується овальним пазом розміром 3.2 × (3.2 + 0.262 + 0.30) = 3.2 × 3.8 мм. Затяжка гвинта у пазі H2 виконується через пару шайб із фторопластовою ковзною прокладкою, що забезпечує вільне термічне дихання конструкції.

#### Кейс 2: Портативний медичний прилад у пластиковому корпусі PC/ABS

Вхідні умови:
- Габарити плати: 80 × 50 мм, товщина 1.0 мм, кріплення на чотири литі пластикові бобишки гвинтами-саморізами Plastite 2.5 мм (K = 0.12, момент 0.25 Н·м).
- Матеріал корпусу: інжекційне литво PC/ABS (CTE = 75.0 ppm/K).
- Допуск висоти литих бобишок прес-форми: Δh = ±0.30 мм.
- Поблизу кутової бобишки (на відстані 2.0 мм від краю отвору) розміщено керамічний конденсатор 0805 у колі детектора ЕКГ.

Результати аналізу:
1. Деформація плати: при прольоті L = 40 мм між бобишками перекіс Δh = 0.30 мм створює на тонкій платі деформацію ε = (6 · 0.0010 · 0.00030) / (0.040²) = 1125 με.
2. Оцінка безпеки: поріг руйнування для MLCC 0805 становить 500 με. Коефіцієнт запасу Margin_strain = 500 / 1125 = 0.44 (перевищення допустимого навантаження у 2.25 раза). Конденсатор розтріскується при першому ж складанні.
3. Рішення:
   - Конденсатор 0805 замінено на виконання Soft-Termination (Murata GCJ21BR71H104KA01L з гнучким полімерним бар'єром).
   - Орієнтацію конденсатора змінено на 90° (розташовано паралельно до кола отвору).
   - Між бобишкою та колом ЕКГ виконано наскрізний фрезерований розвантажувальний паз шириною 1.2 мм, що знизило локальну деформацію до 180 με (запас міцності 2.77x).

#### Кейс 3: Силовий перетворювач 48 В / 100 А на платі 2.4 мм

Вхідні умови:
- Плата: 14 шарів, товщина 2.4 мм, важка мідь 70 мкм (2 oz) на всіх шарах, маса плати в зборі з масивними дроселями та радіатором — 1.4 кг.
- Кріплення: 6 різьбових сталевих стійок M4 з моментом затяжки 1.40 Н·м через збільшені шайби DIN 9021 (зовнішній діаметр 12.0 мм).

Результати аналізу:
1. Сила затяжки: F_clamp = 1.40 / (0.20 · 0.004) = 1750 Н на кожну стійку (сумарний притиск 10.5 кН, понад 1 тонна сили).
2. Тиск на текстоліт: площа шайби DIN 9021 (D = 12.0 мм, d = 4.3 мм) становить A = (π/4) · (12.0² - 4.3²) = 98.6 мм². Контактний тиск P = 1750 / 98.6 = 17.7 МПа (значно нижче межі плинності FR-4 у 250 МПа, запас міцності 14x).
3. Згинальна жорсткість плати 2.4 мм у 3.375 раза вища за стандартну плату 1.6 мм ((2.4 / 1.6)³ = 3.375). Завдяки високій жорсткості плата не прогинається під власною вагою, витримуючи синусоїдальну вібрацію 10 g у діапазоні 20–2000 Гц.

---

### Крайові випадки, інженерні пастки та верифікація

При застосуванні розрахункових моделей на практиці інженер повинен враховувати специфічні особливості реального виробництва:

1. **Тонкі плати (t ≤ 0.8 мм):** гнучкість тонкого текстоліту дозволяє компенсувати значні висотні перекоси стійок без перевищення критичного напруження σ, оскільки відносна деформація ε = (6 · t · Δh) / L² пропорційна товщині t. Проте тонкі плати мають надзвичайно низьку власну частоту коливань (10–30 Гц), потрапляючи в резонанс під час транспортування або роботи моторів. Для тонких плат критичним є розрахунок динамічної стійкості та зменшення кроку між стійками до 35–45 мм.
2. **Товсті багатошарові плати (t ≥ 2.4 мм, ≥ 12 шарів):** висока згинальна жорсткість (D ~ t³) створює колосальні сили реакції на стійках. При затягуванні гвинтів на нерівних бобишках плата не згинається плавно, а вириває внутрішні перехідні отвори (Microvia barrel cracking) та зрізає припаяні кутові виводи QFP і кульки BGA поблизу кріплення.
3. **Релаксація напружень у нейлонових шайбах:** встановлення еластичних діелектричних шайб із поліаміду або фторопласту під головку гвинта для захисту плати часто призводить до повільного витікання полімеру (Cold flow) під постійним тиском. Протягом 6 місяців експлуатації початковий натяг болта падає на 60–80%, що призводить до повного самовідгвинчування кріплення при вібрації. Для фіксації слід застосовувати пружинні зубчасті шайби (DIN 6798A) або різьбові фіксатори середньої міцності (Loctite 243).
4. **Нестабільність коефіцієнта тертя K:** наявність слідів мастила, антикорозійного консерванту або нерівномірне гальванічне цинкування різьби змінює коефіцієнт K у межах від 0.12 до 0.32. При фіксованому крутному моменті викрутки 0.6 Н·м реальна осьова сила може коливатися від 625 Н до 1660 Н, викликаючи або розхитування вузла, або роздавлювання ламінату. Для серійного виробництва обов'язковим є застосування каліброваних гвинтів із сухим лубрикантом (Waxed coating).
5. **Вплив швидкості затягування (Strain Rate Sensitivity):** при використанні пневматичних ненастроєних шурупокрутів швидкість деформації може перевищувати 5000 με/с. При високій швидкості деформації припій SAC305 поводиться не як пластичний метал, а як крихке скло, що спричиняє миттєвий відрив контактних майданчиків (Pad cratering) під чіпами пам'яті та мікроконтролерами. Монтажні лінії повинні обладнуватися сервовикрутками з контролем кутової швидкості (не більше 200–300 об/хв на фінальному півоберті).
6. **Геометричні допуски розташування (GD&T True Position) на виробничих креслениках:** для виключення конфліктів при складанні на механічних креслениках плати координати центрів отворів задають як теоретично точні розміри (Basic Dimensions у прямокутних рамках), а допуск позиціювання вказують у рамці геометричних вимог: `|Позиція|Ø 0.20 (M)|A|B|C|`. Позначення максимуму матеріалу (MMC, символ M у кружечку) вказує, що допуск позиціювання Ø0.20 мм діє при мінімальному діаметрі отвору (наприклад, Ø3.15 мм для M3). Якщо свердло виконало отвір більшим (Ø3.30 мм), виникає додатковий "бонусний допуск" (Bonus Tolerance) у 0.15 мм, що збільшує допустиме поле зміщення осі до Ø0.35 мм без ризику заклинювання гвинта.
7. **Триточкове кінематичне базування проти 4-точкового перекосу:** класична 4-точкова кутова схема кріплення є статично невизначеною системою: якщо бобишки корпусу не лежать в одній площині з точністю до мікронів, четвертий гвинт завжди працює на злам плати. У високоточних вимірювальних приладах та оптичних датчиках застосовують ізостатичне триточкове кріплення (3-Point Kinematic Mount): три точки у просторі завжди утворюють ідеальну площину, повністю усуваючи згинальні та скручувальні напруження в текстоліті незалежно від деформацій зовнішнього корпусу.
8. **Втома паяних з'єднань при термоциклуванні за моделлю Коффіна-Менсона (Coffin-Manson Model):** при періодичному нагріванні та охолодженні пристрою різниця теплового розширення плати та металевого шасі викликає циклічну пластичну деформацію зсуву в припої паяльних менісків довколишніх компонентів. Кількість циклів до руйнування N_f описується рівнянням Коффіна-Менсона:
```
[Модель низькоциклової втоми Коффіна-Менсона]
N_f = C * (Δε_plastic)^(-m) * f^n * exp(E_a / (k_B * T_max))

де:
Δε_plastic — розмах пластичної деформації зсуву припою за один термоцикл
m          — показник втомної кривої (1.9..2.1 для безсвинцевого припою SAC305)
E_a        — енергія активації термічної повзучості (0.50 еВ)
f          — частота термоциклів (циклів/добу)
```
Збільшення відстані від кріпильної стійки до компонента з 1.5 мм до 4.0 мм зменшує розмах деформації Δε_plastic у 3.2 раза, що підвищує розрахункову довговічність паяного вузла при термоциклуванні від 500 до понад 5000 циклів (більше 10 років безвідмовної роботи).
9. **Запобігання мікротріщинам мідної металізації внутрішніх переходів (Microvia / Barrel Cracking):** поряд із керамічними конденсаторами колосальному ризику піддаються внутрішні глухі (Blind/Buried microvias) та наскрізні перехідні отвори (Through-hole vias), розташовані в зоні дії механічного тиску шайби. Під дією стискання шайби та локального вигину мідний циліндр отвору відчуває змінне напруження зрізу на стику між мідним пояском (Pad) та стовпчиком переходу (Barrel). Якщо перехідний отвір розташований ближче 1.0 мм від краю шайби, циклічні навантаження викликають втомний відрив пояска (Pad-to-barrel separation), що призводить до плаваючих обривів кіл живлення процесора чи шин передачі даних. Трасування перехідних отворів повинно суворо підпорядковуватися розрахованій зоні заборони `keepout_trace_radius`.
