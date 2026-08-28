# ⚙️ Калькулятор собівартості корпусу та вибору технології виготовлення

Інженерний вибір технології виготовлення корпусу для електронного пристрою безпосередньо визначає фінансову життєздатність та технічну надійність апаратного проекту. Помилка у виборі виробничого маршруту тягне за собою або катастрофічне зростання початкових витрат на оснастку (NRE), коли дорога сталева прес-форма замовляється для неперевіреної ринком ревізії плати, або багаторазове перевитрачання бюджету на одиницю виробу, коли малі серії фрезеруються з суцільного алюмінієвого моноліту замість доопрацювання готових промислових коробок чи друку на MJF-комплексах.

Поданий нижче консольний інструмент розраховує повну матрицю собівартості (TCO — Total Cost of Ownership) для чотирьох головних виробничих маршрутів: 3D-друку (FDM та промислового MJF), ЧПУ-фрезерування з алюмінію 6061-T6, доопрацювання стандартних корпусів (Gainta / Hammond) та серійного лиття під тиском (Injection Molding). Програма враховує геометричні габарити виробу, товщину стінок, об'єм вибірки матеріалу, нормо-години роботи обладнання, підготовку CAM-програм, вартість прес-форм, фінішну хіміко-термічну обробку (анодування, текстурування) та перевіряє фізико-технічні обмеження щодо тепловідведення й герметичності за класом IP67.

---

## Фізико-математичні моделі розрахунку виробничих процесів

Розрахунок собівартості базується на декомпозиції повних виробничих витрат на незворотні одноразові інженерні витрати (NRE), витрати на підготовку партії (Setup), вартість матеріалу (Raw), машинний час обробки (Machine), фінішні операції (Post-processing) та ручну працю оператора (Labor).

```
[Структура загальних витрат на партію з N одиниць]
C_total(N) = C_NRE + C_setup + N * (C_raw + C_machine + C_post + C_labor)

Питома собівартість одного корпусу:
C_unit(N)  = C_total(N) / N
```

Залежність питомої вартості від тиражу має виражений нелінійний гіперболічний характер: для технологій із великим NRE (лиття під тиском) крива стрімко падає при збільшенні обсягу, тоді як для адитивних технологій крива залишається майже горизонтальною, оскільки вартість кожної наступної деталі визначається фіксованим машинним часом вирощування.

```
[Виробничі складові технологічних маршрутів]
Технологічний процес  Головні фактори NRE                 Джерела питомої вартості одиниці
3D-друк FDM           Відсутні (NRE = 0 USD)              Машинний час екструзії, латунні вставки, постобробка
3D-друк MJF PA12      Підготовка файлів (NRE = 0..35 USD) Маса поліаміду PA12, амортизація камери, парове згладжування
ЧПУ фрезерування Al   CAM траєкторії, оснастка (180..300) Заготовка Al 6061-T6, час фрезерування, анодування
Готовий дороблений    CAM фрезерування панелей (50..100)  Базовий бокс Gainta/Hammond, фрезерування отворів, маркування
Лиття під тиском (IM) Сталева/алюмінієва форма (8k..35k)  Гранулят ABS/PC, цикл ТПА, охолодження форми, амортизація
```

---

### 1. Моделювання адитивного виробництва (FDM та MJF)

Маса нетто корпусу розраховується через сумарну площу зовнішньої поверхні оболонки S_shell та номінальну товщину стінки t_wall. Об'єм нетто V_net визначається як різниця між зовнішнім габаритним об'ємом паралелепіпеда та об'ємом внутрішньої порожнини:

```
[Розрахунок геометрії та маси пластику]
L_cm = L / 10,  W_cm = W / 10,  H_cm = H / 10,  t_cm = t_wall / 10
S_ext = 2 * (L_cm * W_cm + L_cm * H_cm + W_cm * H_cm)             [см²]
V_ext = L_cm * W_cm * H_cm                                        [см³]
V_int = (L_cm - 2*t_cm) * (W_cm - 2*t_cm) * (H_cm - 2*t_cm)       [см³]
V_net = V_ext - V_int                                             [см³]
M_part = V_net * rho_polymer                                      [г]
```

Для технології пошарового наплавлення (FDM) машинний час T_print залежить від максимальної об'ємної швидкості плавлення екструдера Q_vol (для стандартного хотенда з соплом 0.4 мм Q_vol ≈ 8...15 см³/год з урахуванням уповільнень на кутах та друку зовнішніх контурів):

```
[Машинний час FDM друку]
T_print = V_net / Q_vol                                           [год]
C_machine_fdm = T_print * Rate_fdm_hour                           [USD]
```

Додатково для FDM враховуються витрати на встановлення латунних різьбових вставок (Heat-set inserts). Ручна праця оператора включає очищення підтримок (T_clean ≈ 6 хв) та термічне запресовування кожної втулки паяльником (T_insert ≈ 1.2 хв):

```
[Витрати на ручну постобробку та кріплення FDM]
C_post_fdm = N_inserts * Cost_insert_brass                        [USD]
T_labor_fdm = 0.10 + (N_inserts * 0.02)                           [год]
C_labor_fdm = T_labor_fdm * Rate_labor_hour                       [USD]
```

Для технології промислового спікання Multi Jet Fusion (MJF) від HP розрахунок враховує витрату дрібнодисперсного порошку поліаміду PA12 (C_mat ≈ 0.35 USD за см³ спеченого об'єму з урахуванням коефіцієнта оновлення неспеченого порошку 80/20) та фіксовану амортизаційну частку роботи установки за одну деталь у камері побудови (C_chamber ≈ 5.00 USD). Якщо виріб вимагає відповідності класу IP67, обов'язково додається операція хімічного парового згладжування (Vapor Smoothing у парах розчинника), яка розплавляє поверхневі мікропори й коштує близько 6.50 USD на деталь.

---

### 2. Моделювання ЧПУ-фрезерування з алюмінію 6061-T6

Субтрактивна обробка полягає у послідовному зрізанні шарів металу обертовою кінцевою фрезою з суцільної прямокутної заготовки (Billet). Габарити заготовки формуються додаванням технологічних припусків на обробку торців та затискання у лещатах ЧПУ-верстата (по 5 мм на довжину і ширину, 6 мм по висоті):

```
[Габарити заготовки та розрахунок зняття металу]
L_stock = L + 10,  W_stock = W + 10,  H_stock = H + 6             [мм]
V_stock = (L_stock * W_stock * H_stock) * 10^-3                   [см³]
M_stock = (V_stock * rho_aluminum) / 1000                         [кг, rho = 2.7 г/см³]
C_raw_cnc = M_stock * Cost_al6061_per_kg                          [USD]

Об'єм металу, що перетворюється на стружку:
V_removed = V_stock - V_net                                       [см³]
```

Тривалість різання складається з трьох послідовних технологічних фаз:
1. **Чорнова вибірка порожнини (Roughing):** видалення основного масиву кишені високопродуктивною тороїдальною або кінцевою фрезою діаметром 10–12 мм. Швидкість зняття матеріалу (MRR — Material Removal Rate) для сплаву 6061-T6 на шпинделі потужністю 12 кВт досягає MRR ≈ 60...100 см³/хв.
2. **Чистова обробка стінок і дна (Finishing):** проходження контурів дрібними фрезами (3–6 мм) з малим кроком для досягнення шорсткості Ra <= 1.6...3.2 мкм. Час чистової обробки пропорційний площі поверхні: T_finish ≈ S_ext * 0.05 хв/см².
3. **Обробка отворів, нарізання різьби та зміна інструмента:** свердління, зенкування та нарізання мікрорізьб M2–M4 мітчиком або різьбофрезою (2.5 хв на кожне вікно роз'єму, 1.0 хв на кожен різьбовий отвір, плюс 8.0 хв на базове базування та зміну інструментів).

```
[Загальний машинний час фрезерування]
T_rough   = V_removed / MRR                                       [хв]
T_finish  = S_ext * 0.05                                          [хв]
T_details = (N_cutouts * 2.5) + (N_inserts * 1.0) + 8.0           [хв]
T_total   = T_rough + T_finish + T_details                        [хв]
C_machine_cnc = (T_total / 60) * Rate_cnc_hour                    [USD]
```

Фінішна обробка алюмінію включає піскоструминну або дробоструминну обробку скляними мікрокульками для матування та електрохімічне анодне оксидування Type II (Sulfuric Anodizing). Вартість анодування розраховується за площею розгортки деталі:

```
[Вартість анодування та матування]
Area_dm2 = S_ext / 100.0                                          [дм²]
C_post_cnc = Area_dm2 * Cost_anodize_per_dm2                      [USD, мін. 4.00 USD]
```

Одноразові інженерні витрати C_NRE для ЧПУ-фрезерування включають створення 3D-траєкторій у CAM-системі, симуляцію зіткнень інструмента та виготовлення індивідуальних м'яких губок (Soft Jaws) для затискання тонкостінної деталі при обробці другого установа: C_NRE ≈ 180...300 USD.

---

### 3. Моделювання доопрацювання готових серійних корпусів (Gainta / Hammond)

Використання готових стандартних корпусів (литих алюмінієвих коробок Hammond 1590 або пластикових боксів Gainta G2xx/G3xx) усуває необхідність виготовлення корпусу з нуля.

Собівартість сировини C_raw дорівнює гуртовій ціні каталожного корпусу, яка залежить від його внутрішнього об'єму та наявності сертифікованого ущільнювального шнура IP67:

```
[Оцінка вартості стандартного боксу]
Volume_liters = (L * W * H) / 10^6                                [л]
Base_cost = 6.0 + (Volume_liters * 18.0)                          [USD]
Якщо потрібен IP67: Base_cost += 4.50 (силіконовий ущільнювач)    [USD]
C_raw_offshelf = Base_cost
```

Обробка зводиться до швидкісного фрезерування вікон під роз'єми, отворів під світлодіоди та кабельні вводи на передній і задній стінках. Оскільки різання виконується по тонких плоских панелях (товщина 1.5–2.5 мм), час роботи верстата мінімальний:

```
[Машинний час та маркування стандартного корпусу]
T_mod_min = (N_cutouts * 1.5) + 3.0                               [хв]
C_machine_offshelf = (T_mod_min / 60) * Rate_cnc_hour             [USD]
C_post_offshelf = 1.50 (лазерне маркування позначень портів)      [USD]
C_labor_offshelf = 0.05 * Rate_labor_hour                         [USD]
```

Одноразові витрати NRE мінімальні (C_NRE ≈ 50.00 USD), а переналагодження верстата перед партією займає не більше 20–30 хвилин (C_setup ≈ 25.00 USD).

---

### 4. Моделювання серійного лиття під тиском (Injection Molding)

Лиття термопластів під тиском базується на впорскуванні розплавленого грануляту (ABS, PC, поліамід) під гідравлічним тиском 80–150 МПа у прецизійну закриту металеву форму з наступним інтенсивним водяним охолодженням.

#### Оцінка вартості прес-форми (NRE)
Вартість оснастки C_mold масштабується залежно від площі проекції деталі, габаритів плити матриці та кількості рухомих бокових повзунів (Side Sliders). Якщо корпус містить порти на бокових гранях (перпендикулярних до напрямку розмикання форми), введення кожного механічного повзуна збільшує вартість форми на 2 000...2 500 USD:

```
[Розрахунок вартості прес-форми]
C_mold_base = 10000.0 + (S_ext * 12.0)                            [USD]
Якщо N_sliders > 0: C_mold_base += N_sliders * 2200.0             [USD]
C_nre_im = C_mold_base
C_setup_im = 250.0 (монтаж форми на ТПА, вихід на терморежим)     [USD]
```

#### Розрахунок тривалості робочого циклу ТПА
Час одного циклу T_cycle лімітується швидкістю відведення тепла крізь пластикову стінку товщиною t_wall у охолоджувальні канали форми за рівнянням нестаціонарної теплопровідності Фур'є:

```
[Час охолодження деталі у прес-формі]
T_cool = (t_wall^2 / (pi^2 * alpha)) * ln((4/pi) * (T_melt - T_mold) / (T_eject - T_mold))

де:
alpha   — коефіцієнт термодифузії полімеру (0.09 мм²/с для ABS);
T_melt  — температура розплаву (+240 °C);
T_mold  — температура стінки прес-форми (+50 °C);
T_eject — температура виштовхування деталі (+90 °C).
```

Для стінки товщиною 2.5 мм час охолодження становить близько 15–20 с, а повний цикл роботи термопластавтомата разом із змиканням, впорскуванням і виштовхуванням складає T_cycle ≈ 25...35 с.

```
[Питомі витрати на одну відливку]
M_abs_kg = (V_net * rho_abs * 1.15) / 1000                        [кг, +15% ливникова система]
C_raw_im = M_abs_kg * Cost_abs_granule_per_kg                    [USD]
C_machine_im = (T_cycle / 3600) * Rate_im_machine_hour            [USD]
C_post_im = N_inserts * 0.15 (ультразвукове запресовування)       [USD]
C_labor_im = (T_cycle / 3600) * Rate_labor_hour * 0.30            [USD]
```

---

## Реалізація калькулятора на C99 та C++20

Програмний комплекс приймає параметри габаритів корпусу, вимоги до тепловідведення, кількість вирізів та наявність ущільнення IP67. Він автоматично розраховує структуру собівартості, генерує зведену матрицю TCO для тиражів від 1 до 20 000 одиниць і видає однозначну інженерну рекомендацію щодо оптимального технологічного маршруту для кожного розміру партії.

:::tabs

@tab C99

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <math.h>

#define PI 3.14159265358979323846

/* Фізичні та технологічні константи */
#define DENSITY_PETG_G_CM3      1.27
#define DENSITY_ABS_G_CM3       1.05
#define DENSITY_PA12_G_CM3      1.01
#define DENSITY_AL6061_G_CM3    2.70

#define COST_FILAMENT_KG_USD    24.0
#define COST_MJF_PA12_CM3_USD   0.35
#define COST_AL6061_KG_USD      8.50
#define COST_ABS_GRANULE_KG_USD 3.20

#define RATE_FDM_HOUR_USD       4.50
#define RATE_CNC_HOUR_USD       55.0
#define RATE_LABOR_HOUR_USD     25.0
#define RATE_IM_MACHINE_HOUR    45.0

typedef enum {
    TECH_FDM_3D_PRINT = 0,
    TECH_MJF_PA12_PRINT,
    TECH_CNC_ALUMINUM,
    TECH_OFF_SHELF_MODIFIED,
    TECH_INJECTION_MOLDING,
    TECH_COUNT
} TechType;

static const char *TECH_NAMES[TECH_COUNT] = {
    "3D-друк FDM (PETG/ABS)",
    "3D-друк MJF (PA12 Nylon)",
    "ЧПУ фрезерування (Al 6061-T6)",
    "Готовий корпус з доробкою",
    "Лиття під тиском (Injection)"
};

typedef struct {
    double length_mm;
    double width_mm;
    double height_mm;
    double wall_thickness_mm;
    int num_cutouts;
    int num_threaded_inserts;
    int num_side_sliders;
    double thermal_dissipation_watts;
    bool require_ip67;
} EnclosureSpecs;

typedef struct {
    double nre_cost_usd;
    double setup_cost_usd;
    double unit_raw_cost_usd;
    double unit_machine_cost_usd;
    double unit_post_cost_usd;
    double unit_labor_cost_usd;
    bool technically_feasible;
    char feasibility_note[128];
} TechCostBreakdown;

/* Розрахунок площі зовнішньої поверхні (см2) та об'єму матеріалу стінок (см3) */
static void calc_geometry(const EnclosureSpecs *sp, double *out_surface_cm2, double *out_volume_net_cm3) {
    double l_cm = sp->length_mm / 10.0;
    double w_cm = sp->width_mm / 10.0;
    double h_cm = sp->height_mm / 10.0;
    double t_cm = sp->wall_thickness_mm / 10.0;

    double s_ext = 2.0 * (l_cm * w_cm + l_cm * h_cm + w_cm * h_cm);
    double v_ext = l_cm * w_cm * h_cm;
    double v_int = (l_cm - 2.0 * t_cm) * (w_cm - 2.0 * t_cm) * (h_cm - 2.0 * t_cm);
    if (v_int < 0.0) v_int = 0.0;

    double v_net = v_ext - v_int;
    *out_surface_cm2 = s_ext;
    *out_volume_net_cm3 = v_net;
}

/* 1. Модель FDM 3D-друку */
static TechCostBreakdown eval_fdm(const EnclosureSpecs *sp) {
    TechCostBreakdown b;
    memset(&b, 0, sizeof(b));
    b.technically_feasible = true;

    double s_cm2, v_net_cm3;
    calc_geometry(sp, &s_cm2, &v_net_cm3);

    double mass_g = v_net_cm3 * DENSITY_PETG_G_CM3;
    b.unit_raw_cost_usd = (mass_g / 1000.0) * COST_FILAMENT_KG_USD;

    /* Об'ємна швидкість друку 12 см3/год */
    double print_hours = v_net_cm3 / 12.0;
    if (print_hours < 0.5) print_hours = 0.5;
    b.unit_machine_cost_usd = print_hours * RATE_FDM_HOUR_USD;

    /* Латунні вставки та зняття підтримок */
    b.unit_post_cost_usd = sp->num_threaded_inserts * 0.25;
    double labor_hours = 0.10 + (sp->num_threaded_inserts * 0.02);
    b.unit_labor_cost_usd = labor_hours * RATE_LABOR_HOUR_USD;

    b.nre_cost_usd = 0.0;
    b.setup_cost_usd = 10.0;

    if (sp->thermal_dissipation_watts > 8.0) {
        b.technically_feasible = false;
        snprintf(b.feasibility_note, sizeof(b.feasibility_note),
                 "Тепловідвід %.1f Вт перевищує ліміт пластику FDM (макс 8 Вт)",
                 sp->thermal_dissipation_watts);
    } else if (sp->require_ip67) {
        b.technically_feasible = false;
        snprintf(b.feasibility_note, sizeof(b.feasibility_note),
                 "Мікропористість FDM шарів не гарантує герметичність IP67");
    } else {
        snprintf(b.feasibility_note, sizeof(b.feasibility_note), "OK для макетів та прототипів");
    }
    return b;
}

/* 2. Модель MJF PA12 3D-друку */
static TechCostBreakdown eval_mjf(const EnclosureSpecs *sp) {
    TechCostBreakdown b;
    memset(&b, 0, sizeof(b));
    b.technically_feasible = true;

    double s_cm2, v_net_cm3;
    calc_geometry(sp, &s_cm2, &v_net_cm3);

    b.unit_raw_cost_usd = v_net_cm3 * COST_MJF_PA12_CM3_USD;
    b.unit_machine_cost_usd = 5.0; /* Амортизація камери за деталь */
    b.unit_post_cost_usd = (sp->require_ip67 ? 6.50 : 2.00) + sp->num_threaded_inserts * 0.25;
    b.unit_labor_cost_usd = 0.08 * RATE_LABOR_HOUR_USD;

    b.nre_cost_usd = 0.0;
    b.setup_cost_usd = 35.0;

    if (sp->thermal_dissipation_watts > 12.0) {
        b.technically_feasible = false;
        snprintf(b.feasibility_note, sizeof(b.feasibility_note),
                 "Поліамід PA12 не забезпечує розсіювання %.1f Вт",
                 sp->thermal_dissipation_watts);
    } else {
        snprintf(b.feasibility_note, sizeof(b.feasibility_note),
                 sp->require_ip67 ? "Вимагає парового згладжування (Vapor Polish)" : "OK для серійних корпусів");
    }
    return b;
}

/* 3. Модель ЧПУ-фрезерування (Алюміній 6061-T6) */
static TechCostBreakdown eval_cnc(const EnclosureSpecs *sp) {
    TechCostBreakdown b;
    memset(&b, 0, sizeof(b));
    b.technically_feasible = true;

    double s_cm2, v_net_cm3;
    calc_geometry(sp, &s_cm2, &v_net_cm3);

    double stock_l_cm = (sp->length_mm + 10.0) / 10.0;
    double stock_w_cm = (sp->width_mm + 10.0) / 10.0;
    double stock_h_cm = (sp->height_mm + 6.0) / 10.0;
    double v_stock_cm3 = stock_l_cm * stock_w_cm * stock_h_cm;
    double mass_stock_kg = (v_stock_cm3 * DENSITY_AL6061_G_CM3) / 1000.0;

    b.unit_raw_cost_usd = mass_stock_kg * COST_AL6061_KG_USD;

    double v_removed_cm3 = v_stock_cm3 - v_net_cm3;
    double mrr_cm3_min = 75.0; /* Швидкість вибірки Al 6061 */
    double t_rough_min = v_removed_cm3 / mrr_cm3_min;
    double t_finish_min = s_cm2 * 0.05;
    double t_holes_min = (sp->num_cutouts * 2.5) + (sp->num_threaded_inserts * 1.0);
    double t_total_min = t_rough_min + t_finish_min + t_holes_min + 8.0;

    b.unit_machine_cost_usd = (t_total_min / 60.0) * RATE_CNC_HOUR_USD;
    /* Анодування Type II + піскоструй: $0.20 за дм2 */
    double area_dm2 = s_cm2 / 100.0;
    b.unit_post_cost_usd = area_dm2 * 0.20 * 100.0;
    if (b.unit_post_cost_usd < 4.0) b.unit_post_cost_usd = 4.0;
    b.unit_labor_cost_usd = 0.10 * RATE_LABOR_HOUR_USD;

    b.nre_cost_usd = 180.0; /* CAM програмування та нульові точки */
    b.setup_cost_usd = 60.0;

    snprintf(b.feasibility_note, sizeof(b.feasibility_note),
             "Ідеальне тепловідведення (167 Вт/(м·К)) та повне ЕМС екранування");
    return b;
}

/* 4. Модель готового корпусу з доробкою (Gainta / Hammond) */
static TechCostBreakdown eval_off_shelf(const EnclosureSpecs *sp) {
    TechCostBreakdown b;
    memset(&b, 0, sizeof(b));
    b.technically_feasible = true;

    /* Оцінка вартості стандартного боксу від габаритів */
    double volume_liters = (sp->length_mm * sp->width_mm * sp->height_mm) / 1e6;
    double base_catalog_cost = 6.0 + (volume_liters * 18.0);
    if (sp->require_ip67) base_catalog_cost += 4.50;

    b.unit_raw_cost_usd = base_catalog_cost;

    /* Фрезерування вирізів у кришці/панелях */
    double t_mod_min = (sp->num_cutouts * 1.5) + 3.0;
    b.unit_machine_cost_usd = (t_mod_min / 60.0) * RATE_CNC_HOUR_USD;
    b.unit_post_cost_usd = 1.50; /* Лазерне маркування портів */
    b.unit_labor_cost_usd = 0.05 * RATE_LABOR_HOUR_USD;

    b.nre_cost_usd = 50.0;
    b.setup_cost_usd = 25.0;

    if (sp->thermal_dissipation_watts > 25.0) {
        b.technically_feasible = false;
        snprintf(b.feasibility_note, sizeof(b.feasibility_note),
                 "Стандартний бокс вимагає зовнішнього радіатора для %.1f Вт",
                 sp->thermal_dissipation_watts);
    } else {
        snprintf(b.feasibility_note, sizeof(b.feasibility_note),
                 "Оптимальний баланс ціни та швидкості запуску для малих серій");
    }
    return b;
}

/* 5. Модель лиття під тиском (Injection Molding) */
static TechCostBreakdown eval_injection_molding(const EnclosureSpecs *sp) {
    TechCostBreakdown b;
    memset(&b, 0, sizeof(b));
    b.technically_feasible = true;

    double s_cm2, v_net_cm3;
    calc_geometry(sp, &s_cm2, &v_net_cm3);

    double mass_g = v_net_cm3 * DENSITY_ABS_G_CM3;
    b.unit_raw_cost_usd = (mass_g / 1000.0) * COST_ABS_GRANULE_KG_USD * 1.15; /* +15% ливники */

    /* Цикл лиття залежно від товщини стінки */
    double cycle_sec = 12.0 + (sp->wall_thickness_mm * sp->wall_thickness_mm * 2.5);
    b.unit_machine_cost_usd = (cycle_sec / 3600.0) * RATE_IM_MACHINE_HOUR;
    b.unit_post_cost_usd = sp->num_threaded_inserts * 0.15;
    b.unit_labor_cost_usd = (cycle_sec / 3600.0) * RATE_LABOR_HOUR_USD * 0.3;

    /* Вартість прес-форми */
    double base_mold = 10000.0 + (s_cm2 * 12.0);
    if (sp->num_side_sliders > 0) {
        base_mold += sp->num_side_sliders * 2200.0;
    }
    b.nre_cost_usd = base_mold;
    b.setup_cost_usd = 250.0;

    if (sp->thermal_dissipation_watts > 10.0) {
        b.technically_feasible = false;
        snprintf(b.feasibility_note, sizeof(b.feasibility_note),
                 "Лиття пластику не відведе %.1f Вт без внутрішніх металевих тепловідводів",
                 sp->thermal_dissipation_watts);
    } else {
        snprintf(b.feasibility_note, sizeof(b.feasibility_note),
                 "Мінімальна ціна деталі для великих серій (>2 000 шт)");
    }
    return b;
}

static double calc_unit_tco(const TechCostBreakdown *b, int batch_size) {
    if (batch_size <= 0) return 0.0;
    double nre_share = b->nre_cost_usd / (double)batch_size;
    double setup_share = b->setup_cost_usd / (double)batch_size;
    double per_unit = b->unit_raw_cost_usd + b->unit_machine_cost_usd +
                      b->unit_post_cost_usd + b->unit_labor_cost_usd;
    return nre_share + setup_share + per_unit;
}

int main(int argc, char **argv) {
    EnclosureSpecs sp = {
        .length_mm = 120.0,
        .width_mm = 80.0,
        .height_mm = 35.0,
        .wall_thickness_mm = 2.5,
        .num_cutouts = 4,
        .num_threaded_inserts = 4,
        .num_side_sliders = 1,
        .thermal_dissipation_watts = 5.0,
        .require_ip67 = true
    };

    printf("================================================================================\n");
    printf("     АНАЛІЗАТОР СОБІВАРТОСТІ ТА ВИБОРУ ТЕХНОЛОГІЇ ВИГОТОВЛЕННЯ КОРПУСУ\n");
    printf("================================================================================\n");
    printf("Параметри корпусу: %.1f x %.1f x %.1f мм, стінка %.1f мм\n",
           sp.length_mm, sp.width_mm, sp.height_mm, sp.wall_thickness_mm);
    printf("Вимоги: Вирізів: %d, Вставок: %d, Тепло: %.1f Вт, IP67: %s\n\n",
           sp.num_cutouts, sp.num_threaded_inserts, sp.thermal_dissipation_watts,
           sp.require_ip67 ? "ТАК" : "НІ");

    TechCostBreakdown breaks[TECH_COUNT];
    breaks[TECH_FDM_3D_PRINT]       = eval_fdm(&sp);
    breaks[TECH_MJF_PA12_PRINT]     = eval_mjf(&sp);
    breaks[TECH_CNC_ALUMINUM]       = eval_cnc(&sp);
    breaks[TECH_OFF_SHELF_MODIFIED] = eval_off_shelf(&sp);
    breaks[TECH_INJECTION_MOLDING]  = eval_injection_molding(&sp);

    /* Друк структури витрат */
    printf("--------------------------------------------------------------------------------\n");
    printf("%-30s | %-8s | %-8s | %-8s | %-8s\n", "Технологічний процес", "NRE ($)", "Raw ($)", "Mach ($)", "Feasible?");
    printf("--------------------------------------------------------------------------------\n");
    for (int i = 0; i < TECH_COUNT; ++i) {
        printf("%-30s | %8.1f | %8.2f | %8.2f | %-8s\n",
               TECH_NAMES[i],
               breaks[i].nre_cost_usd,
               breaks[i].unit_raw_cost_usd,
               breaks[i].unit_machine_cost_usd,
               breaks[i].technically_feasible ? "ТАК" : "НІ");
    }
    printf("--------------------------------------------------------------------------------\n\n");

    /* Аналіз собівартості залежно від тиражу партії */
    int batches[] = { 1, 10, 50, 100, 500, 1000, 5000, 20000 };
    int n_batches = sizeof(batches) / sizeof(batches[0]);

    printf("ПОРІВНЯЛЬНА ТАБЛИЦЯ ПИТОМОЇ СОБІВАРТОСТІ 1 КОРПУСУ (USD / шт):\n");
    printf("--------------------------------------------------------------------------------\n");
    printf("%-26s", "Тираж партії (шт):");
    for (int b = 0; b < n_batches; ++b) {
        printf(" | %6d", batches[b]);
    }
    printf("\n--------------------------------------------------------------------------------\n");

    for (int i = 0; i < TECH_COUNT; ++i) {
        printf("%-26s", TECH_NAMES[i]);
        for (int b = 0; b < n_batches; ++b) {
            double cost = calc_unit_tco(&breaks[i], batches[b]);
            if (!breaks[i].technically_feasible) {
                printf(" |   N/A ");
            } else if (cost > 999.0) {
                printf(" | >$999 ");
            } else {
                printf(" | %6.2f", cost);
            }
        }
        printf("\n");
    }
    printf("--------------------------------------------------------------------------------\n\n");

    /* Визначення оптимальної технології для кожного тиражу */
    printf("РЕКОМЕНДАЦІЇ ТЕХНОЛОГІЧНОГО МАРШРУТУ ЗА РОЗМІРОМ ПАРТІЇ:\n");
    for (int b = 0; b < n_batches; ++b) {
        int best_tech = -1;
        double min_cost = 1e9;

        for (int i = 0; i < TECH_COUNT; ++i) {
            if (!breaks[i].technically_feasible) continue;
            double c = calc_unit_tco(&breaks[i], batches[b]);
            if (c < min_cost) {
                min_cost = c;
                best_tech = i;
            }
        }

        if (best_tech >= 0) {
            printf("  Тираж %5d шт: -> %-30s ($%.2f / шт)\n",
                   batches[b], TECH_NAMES[best_tech], min_cost);
        } else {
            printf("  Тираж %5d шт: -> Жодна технологія не задовольняє вимоги\n", batches[b]);
        }
    }
    printf("================================================================================\n");

    return 0;
}
```

@tab C++20

```cpp
#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <format>
#include <optional>
#include <cmath>
#include <algorithm>
#include <numbers>

namespace EnclosureCost {

struct MaterialProperties {
    std::string_view name;
    double density_g_cm3;
    double cost_per_kg_usd;
    double thermal_conductivity_w_mk;
    double max_continuous_temp_c;
};

inline constexpr MaterialProperties MAT_PETG   { "PETG",          1.27, 24.0, 0.20,  70.0 };
inline constexpr MaterialProperties MAT_ABS    { "ABS",           1.05, 22.0, 0.18,  90.0 };
inline constexpr MaterialProperties MAT_PA12   { "PA12 (Nylon)",  1.01, 65.0, 0.25, 120.0 };
inline constexpr MaterialProperties MAT_AL6061 { "Al 6061-T6",    2.70,  8.5, 167.0, 200.0 };

enum class ManufacturingTechnology {
    Fdm3DPrinting,
    MjfPa12Printing,
    CncMillingAl6061,
    OffTheShelfModified,
    InjectionMolding
};

struct EnclosureDesign {
    double length_mm{ 120.0 };
    double width_mm{ 80.0 };
    double height_mm{ 35.0 };
    double wall_thickness_mm{ 2.5 };
    int num_port_cutouts{ 4 };
    int num_threaded_inserts{ 4 };
    int num_side_sliders{ 1 };
    double thermal_load_watts{ 5.0 };
    bool require_ip67{ true };

    [[nodiscard]] constexpr double surface_area_cm2() const noexcept {
        double l_cm = length_mm / 10.0;
        double w_cm = width_mm / 10.0;
        double h_cm = height_mm / 10.0;
        return 2.0 * (l_cm * w_cm + l_cm * h_cm + w_cm * h_cm);
    }

    [[nodiscard]] constexpr double net_volume_cm3() const noexcept {
        double l_cm = length_mm / 10.0;
        double w_cm = width_mm / 10.0;
        double h_cm = height_mm / 10.0;
        double t_cm = wall_thickness_mm / 10.0;

        double v_ext = l_cm * w_cm * h_cm;
        double v_int = std::max(0.0, (l_cm - 2.0 * t_cm) * (w_cm - 2.0 * t_cm) * (h_cm - 2.0 * t_cm));
        return v_ext - v_int;
    }
};

struct CostBreakdown {
    ManufacturingTechnology tech;
    std::string_view tech_name;
    double nre_tooling_cost_usd{ 0.0 };
    double batch_setup_cost_usd{ 0.0 };
    double unit_raw_material_usd{ 0.0 };
    double unit_machining_usd{ 0.0 };
    double unit_post_process_usd{ 0.0 };
    double unit_labor_usd{ 0.0 };
    bool is_feasible{ true };
    std::string feasibility_note{ "OK" };

    [[nodiscard]] constexpr double unit_production_cost() const noexcept {
        return unit_raw_material_usd + unit_machining_usd + unit_post_process_usd + unit_labor_usd;
    }

    [[nodiscard]] double total_unit_cost(int batch_size) const noexcept {
        if (batch_size <= 0) return 0.0;
        double amortized_nre = nre_tooling_cost_usd / static_cast<double>(batch_size);
        double amortized_setup = batch_setup_cost_usd / static_cast<double>(batch_size);
        return amortized_nre + amortized_setup + unit_production_cost();
    }
};

class CostEstimator {
public:
    static CostBreakdown evaluate_fdm(const EnclosureDesign& design) {
        CostBreakdown cb{
            .tech = ManufacturingTechnology::Fdm3DPrinting,
            .tech_name = "3D-друк FDM (PETG/ABS)"
        };

        double v_net = design.net_volume_cm3();
        double mass_g = v_net * MAT_PETG.density_g_cm3;
        cb.unit_raw_material_usd = (mass_g / 1000.0) * MAT_PETG.cost_per_kg_usd;

        double print_hours = std::max(0.5, v_net / 12.0); // 12 см3/год
        cb.unit_machining_usd = print_hours * 4.50; // 4.50 USD/год машинного часу
        cb.unit_post_process_usd = design.num_threaded_inserts * 0.25;
        cb.unit_labor_usd = (0.10 + design.num_threaded_inserts * 0.02) * 25.0;

        cb.nre_tooling_cost_usd = 0.0;
        cb.batch_setup_cost_usd = 10.0;

        if (design.thermal_load_watts > 8.0) {
            cb.is_feasible = false;
            cb.feasibility_note = std::format("Теплове навантаження {:.1f} Вт перевищує ліміт пластику", design.thermal_load_watts);
        } else if (design.require_ip67) {
            cb.is_feasible = false;
            cb.feasibility_note = "Мікропористість шарів FDM не забезпечує IP67";
        }
        return cb;
    }

    static CostBreakdown evaluate_mjf(const EnclosureDesign& design) {
        CostBreakdown cb{
            .tech = ManufacturingTechnology::MjfPa12Printing,
            .tech_name = "3D-друк MJF (PA12 Nylon)"
        };

        double v_net = design.net_volume_cm3();
        cb.unit_raw_material_usd = v_net * 0.35; // 0.35 USD/см3 з урахуванням порошку
        cb.unit_machining_usd = 5.00;
        cb.unit_post_process_usd = (design.require_ip67 ? 6.50 : 2.00) + design.num_threaded_inserts * 0.25;
        cb.unit_labor_usd = 0.08 * 25.0;

        cb.nre_tooling_cost_usd = 0.0;
        cb.batch_setup_cost_usd = 35.0;

        if (design.thermal_load_watts > 12.0) {
            cb.is_feasible = false;
            cb.feasibility_note = std::format("Низька теплопровідність PA12 для {:.1f} Вт", design.thermal_load_watts);
        } else {
            cb.feasibility_note = design.require_ip67 ? "Потрібне парове згладжування для IP67" : "Повністю ізотропний корпус";
        }
        return cb;
    }

    static CostBreakdown evaluate_cnc_aluminum(const EnclosureDesign& design) {
        CostBreakdown cb{
            .tech = ManufacturingTechnology::CncMillingAl6061,
            .tech_name = "ЧПУ фрезерування (Al 6061-T6)"
        };

        double stock_l_cm = (design.length_mm + 10.0) / 10.0;
        double stock_w_cm = (design.width_mm + 10.0) / 10.0;
        double stock_h_cm = (design.height_mm + 6.0) / 10.0;
        double v_stock = stock_l_cm * stock_w_cm * stock_h_cm;
        double v_net = design.net_volume_cm3();
        double s_area = design.surface_area_cm2();

        double mass_stock_kg = (v_stock * MAT_AL6061.density_g_cm3) / 1000.0;
        cb.unit_raw_material_usd = mass_stock_kg * MAT_AL6061.cost_per_kg_usd;

        double v_removed = v_stock - v_net;
        double mrr = 75.0; // 75 см3/хв
        double t_mach_min = (v_removed / mrr) + (s_area * 0.05) + (design.num_port_cutouts * 2.5) + 8.0;

        cb.unit_machining_usd = (t_mach_min / 60.0) * 55.0; // 55 USD/год ЧПУ
        double area_dm2 = s_area / 100.0;
        cb.unit_post_process_usd = std::max(4.0, area_dm2 * 20.0); // Анодування Type II
        cb.unit_labor_usd = 0.10 * 25.0;

        cb.nre_tooling_cost_usd = 180.0; // CAM програмування
        cb.batch_setup_cost_usd = 60.0;

        cb.feasibility_note = "Виняткове тепловідведення (167 Вт/(м·К)) та ЕМС захист";
        return cb;
    }

    static CostBreakdown evaluate_off_shelf(const EnclosureDesign& design) {
        CostBreakdown cb{
            .tech = ManufacturingTechnology::OffTheShelfModified,
            .tech_name = "Готовий корпус з доробкою"
        };

        double volume_liters = (design.length_mm * design.width_mm * design.height_mm) / 1e6;
        double catalog_base = 6.0 + (volume_liters * 18.0) + (design.require_ip67 ? 4.50 : 0.0);

        cb.unit_raw_material_usd = catalog_base;
        double t_mod_min = (design.num_port_cutouts * 1.5) + 3.0;
        cb.unit_machining_usd = (t_mod_min / 60.0) * 55.0;
        cb.unit_post_process_usd = 1.50; // Лазерне маркування
        cb.unit_labor_usd = 0.05 * 25.0;

        cb.nre_tooling_cost_usd = 50.0;
        cb.batch_setup_cost_usd = 25.0;

        if (design.thermal_load_watts > 25.0) {
            cb.is_feasible = false;
            cb.feasibility_note = "Потрібний додатковий зовнішній радіатор";
        } else {
            cb.feasibility_note = "Швидкий вихід на ринок для малих партій";
        }
        return cb;
    }

    static CostBreakdown evaluate_injection_molding(const EnclosureDesign& design) {
        CostBreakdown cb{
            .tech = ManufacturingTechnology::InjectionMolding,
            .tech_name = "Лиття під тиском (Injection)"
        };

        double v_net = design.net_volume_cm3();
        double mass_g = v_net * MAT_ABS.density_g_cm3;
        cb.unit_raw_material_usd = (mass_g / 1000.0) * 3.20 * 1.15; // ABS гранули + 15% ливники

        double cycle_sec = 12.0 + (design.wall_thickness_mm * design.wall_thickness_mm * 2.5);
        cb.unit_machining_usd = (cycle_sec / 3600.0) * 45.0;
        cb.unit_post_process_usd = design.num_threaded_inserts * 0.15;
        cb.unit_labor_usd = (cycle_sec / 3600.0) * 25.0 * 0.3;

        double mold_nre = 10000.0 + (design.surface_area_cm2() * 12.0);
        if (design.num_side_sliders > 0) {
            mold_nre += design.num_side_sliders * 2200.0;
        }
        cb.nre_tooling_cost_usd = mold_nre;
        cb.batch_setup_cost_usd = 250.0;

        if (design.thermal_load_watts > 10.0) {
            cb.is_feasible = false;
            cb.feasibility_note = "Пластик вимагає металевих теплових вставок";
        } else {
            cb.feasibility_note = "Найнижча собівартість при тиражі від 1 500 шт";
        }
        return cb;
    }
};

} // namespace EnclosureCost

int main() {
    using namespace EnclosureCost;

    EnclosureDesign specs{
        .length_mm = 120.0,
        .width_mm = 80.0,
        .height_mm = 35.0,
        .wall_thickness_mm = 2.5,
        .num_port_cutouts = 4,
        .num_threaded_inserts = 4,
        .num_side_sliders = 1,
        .thermal_load_watts = 5.0,
        .require_ip67 = true
    };

    std::cout << "================================================================================\n";
    std::cout << "     АНАЛІЗАТОР СОБІВАРТОСТІ ТА ВИБОРУ ТЕХНОЛОГІЇ ВИГОТОВЛЕННЯ КОРПУСУ\n";
    std::cout << "================================================================================\n";
    std::cout << std::format("Параметри корпусу: {:.1f} x {:.1f} x {:.1f} мм, стінка {:.1f} мм\n",
                             specs.length_mm, specs.width_mm, specs.height_mm, specs.wall_thickness_mm);
    std::cout << std::format("Вимоги: Вирізів: {}, Вставок: {}, Тепло: {:.1f} Вт, IP67: {}\n\n",
                             specs.num_port_cutouts, specs.num_threaded_inserts, specs.thermal_load_watts,
                             specs.require_ip67 ? "ТАК" : "НІ");

    std::vector<CostBreakdown> breakdowns = {
        CostEstimator::evaluate_fdm(specs),
        CostEstimator::evaluate_mjf(specs),
        CostEstimator::evaluate_cnc_aluminum(specs),
        CostEstimator::evaluate_off_shelf(specs),
        CostEstimator::evaluate_injection_molding(specs)
    };

    std::cout << "--------------------------------------------------------------------------------\n";
    std::cout << std::format("{:<30} | {:<8} | {:<8} | {:<8} | {:<8}\n",
                             "Технологічний процес", "NRE ($)", "Raw ($)", "Mach ($)", "Feasible?");
    std::cout << "--------------------------------------------------------------------------------\n";

    for (const auto& b : breakdowns) {
        std::cout << std::format("{:<30} | {:8.1f} | {:8.2f} | {:8.2f} | {:<8}\n",
                                 b.tech_name, b.nre_tooling_cost_usd, b.unit_raw_material_usd,
                                 b.unit_machining_usd, b.is_feasible ? "ТАК" : "НІ");
    }
    std::cout << "--------------------------------------------------------------------------------\n\n";

    const std::vector<int> batches = { 1, 10, 50, 100, 500, 1000, 5000, 20000 };

    std::cout << "ПОРІВНЯЛЬНА ТАБЛИЦЯ ПИТОМОЇ СОБІВАРТОСТІ 1 КОРПУСУ (USD / шт):\n";
    std::cout << "--------------------------------------------------------------------------------\n";
    std::cout << std::format("{:<26}", "Тираж партії (шт):");
    for (int count : batches) {
        std::cout << std::format(" | {:6d}", count);
    }
    std::cout << "\n--------------------------------------------------------------------------------\n";

    for (const auto& b : breakdowns) {
        std::cout << std::format("{:<26}", b.tech_name);
        for (int count : batches) {
            if (!b.is_feasible) {
                std::cout << " |   N/A ";
            } else {
                double cost = b.total_unit_cost(count);
                if (cost > 999.0) {
                    std::cout << " | >$999 ";
                } else {
                    std::cout << std::format(" | {:6.2f}", cost);
                }
            }
        }
        std::cout << "\n";
    }
    std::cout << "--------------------------------------------------------------------------------\n\n";

    std::cout << "РЕКОМЕНДАЦІЇ ТЕХНОЛОГІЧНОГО МАРШРУТУ ЗА РОЗМІРОМ ПАРТІЇ:\n";
    for (int count : batches) {
        std::optional<CostBreakdown> best;
        double min_cost = 1e9;

        for (const auto& b : breakdowns) {
            if (!b.is_feasible) continue;
            double cost = b.total_unit_cost(count);
            if (cost < min_cost) {
                min_cost = cost;
                best = b;
            }
        }

        if (best.has_value()) {
            std::cout << std::format("  Тираж {:5d} шт: -> {:<30} (${:.2f} / шт)\n",
                                     count, best->tech_name, min_cost);
        } else {
            std::cout << std::format("  Тираж {:5d} шт: -> Жодна технологія не задовольняє вимоги\n", count);
        }
    }
    std::cout << "================================================================================\n";

    return 0;
}
```

:::

---

## Детальний розбір алгоритмів та крайових інженерних випадків

Програмний аналізатор виконує багаторівневу валідацію вихідних даних. Порушення фізичних або технологічних обмежень блокує вибір відповідного методу навіть у випадках, коли його фінансова вартість є формально найнижчою.

### 1. Теплове обмеження полімерних матеріалів

Полімерні оболонки (FDM, SLA, MJF, литий ABS/PC) мають надзвичайно низький коефіцієнт теплопровідності (k ≈ 0.18...0.25 Вт/(м·К)), що майже у 800 разів гірше за алюмінієвий сплав 6061-T6 (k = 167 Вт/(м·К)).

У повністю закритому герметичному корпусі без примусової конвекції всередині утворюється застійна теплова зона. Тепловий потік від гарячих компонентів плати (процесора, DC-DC перетворювача, силових ключів) передається до стінок корпусу лише через теплопровідність нерухомого повітря (k_air ≈ 0.026 Вт/(м·К)). Перепад температур між внутрішнім об'ємом і довкіллям описується залежністю:

```
[Оцінка внутрішнього перегріву замкненого корпусу]
Delta_T = P_thermal / (h_conv * S_ext)

де:
P_thermal — розсіювана потужність, Вт;
h_conv    — коефіцієнт природної конвекції та випромінювання (6..10 Вт/(м²·К));
S_ext     — повна площа поверхні корпусу, м².
```

Для корпусу розміром 120 x 80 x 35 мм площа поверхні становить близько S_ext ≈ 0.0332 м². При розсіюванні потужності P_thermal = 10 Вт внутрішній перегрів досягає:

```
Delta_T = 10 / (8.0 * 0.0332) ≈ 37.6 °C
```

Якщо прилад експлуатується при температурі довкілля +40 °C, внутрішня температура повітря досягне +77.6 °C, що перевищує температуру склування PETG (+70 °C) та призводить до пластичної деформації бонок і розгерметизації стиків. Якщо ж потужність перевищує 15–20 Вт, пластикові оболонки повністю дискваліфікуються: тепло повинно відводитися безпосередньо через металевий фрезерований корпус або зовнішній алюмінієвий радіатор.

---

### 2. Подолання мікропористості та капілярного проникнення вологи (IP67)

У FDM-друці екструдована нитка утворює овальний профіль. Між сусідніми шарами та периметрами залишаються мікроскопічні трикутні канали (капіляри).

Під час сертифікаційного тесту за класом IP67 прилад занурюють у воду на глибину 1 метр, що створює надлишковий гідростатичний тиск P = 9.81 кПа. Вода під дією капілярного тиску та зовнішнього напору просочується крізь стінку товщиною 2–3 мм за 5–15 хвилин, незалежно від наявності ущільнювального кільця на фланці. Тому калькулятор маркує FDM-друк як technically_feasible = false для вимоги require_ip67 = true.

Для деталей з поліаміду PA12, виготовлених на установках Multi Jet Fusion (MJF), окремі зерна порошку спікаються рідким агентом і лампою нагріву. Хоча деталь візуально монолітна, залишкова мікропористість матеріалу становить 1.5–3.0 об'ємних відсотків. Програма враховує обов'язкове хімічне парове згладжування (Vapor Smoothing): у герметичній камері пари спеціального розчинника розчиняють поверхневий шар поліаміду на глибину 10–20 мкм, затягуючи всі пори під дією сил поверхневого натягу, що утворює гладку глянцеву гідрофобну плівку, повністю непроникну для води.

---

### 3. Складність розімкнення прес-форм та бокові піднутрення

При проектуванні деталей під лиття термопластів під тиском (Injection Molding) рух рухомої плити термопластавтомата відбувається строго вздовж однієї осі Z.

Будь-який отвір під роз'єм (Type-C, RJ45, вимикач), розташований на боковій стінці, утворює так зване піднутрення (Undercut): застиглий пластик блокує розмикання матриці й пуансона. Для формування такого отвору прес-форма оснащується боковим механічним або гідравлічним повзуном (Side Slider / Core Pull), який перед розмиканням форми відводиться убік за допомогою похилих напрямних колонок (Angle Pins).

Кожен повзун є прецизійним механічним вузлом із загартованої інструментальної сталі H13 або S136, що вимагає індивідуального шліфування, підгонки клинових замків (Heel Blocks) та встановлення кінцевих вимикачів безпеки. У коді калькулятора параметр num_side_sliders збільшує вартість NRE прес-форми на 2 200 USD за кожен незалежний напрямок руху повзуна. Якщо корпус вимагає отворів на всіх чотирьох бокових гранях, вартість форми зростає з базових 10 000 USD до 18 800 USD, що суттєво зміщує точку беззбитковості праворуч по шкалі тиражу.

---

### 4. Вплив геометрії кишень на вібрації та стійкість інструмента (ЧПУ)

При фрезеруванні глибоких тонкостінних корпусів із суцільного моноліту Al 6061-T6 критичним параметром стає виліт різального інструмента (виліт фрези з цангового патрона).

Згинальна жорсткість циліндричної фрези як балки, затисненої з одного кінця, описується формулою:

```
[Згинальна жорсткість кінцевої фрези]
K_tool = (3 * E * I) / L_stickout^3 = (3 * E * pi * d_tool^4) / (64 * L_stickout^3)
```

де E — модуль Юнга матеріалу фрези (твердий сплав ВК8 / карбід вольфраму, E ≈ 550 ГПа), а L_stickout — виліт фрези. Жорсткість інструмента падає пропорційно кубу його вильоту (L^3) і зростає пропорційно четвертому ступеню діаметра (d^4).

Якщо глибина внутрішньої кишені корпусу становить H = 50 мм, а радіус внутрішніх кутів закладено R = 2.0 мм (що вимагає фрези діаметром d = 4.0 мм), співвідношення вильоту до діаметра досягає L/d = 50/4 = 12.5. За такого співвідношення фреза зазнає катастрофічного відхилення під дією сили різання, виникає автоколивальний резонанс (Chatter), що призводить до поломки інструмента та неприпустимої шорсткості стінок.

Щоб запобігти цьому, оператор ЧПУ змушений:
1. Зменшувати глибину різання за один прохід (a_p) з 5.0 мм до 0.3 мм, що збільшує машинний час чорнової вибірки у 8–10 разів.
2. Проводити обробку у два етапи: вибірка основного об'єму жорсткою короткою фрезою діаметром 12–16 мм (L/d <= 3), а потім чистове підчищання кутів довгою тонкою фрезою на мінімальній подачі.

Калькулятор закладає усереднену швидкість зняття матеріалу MRR = 75 см³/хв, яка відповідає збалансованому інженерному проектуванню з радіусами кутів R >= 3.0 мм та співвідношенням глибини кишені до ширини не більше 3:1.

---

### 5. Температурний дрейф розмірів та різниця коефіцієнтів розширення (CTE)

Невідповідність коефіцієнтів лінійного теплового розширення (CTE — Coefficient of Thermal Expansion) між матеріалом друкованої плати та корпусом створює критичні зрізувальні напруження на стійках кріплення та паяних контактах.

```
[Коефіцієнти лінійного теплового розширення матеріалів]
Матеріал                CTE (alpha), 10^-6 1/K   Розширення на довжині 100 мм при Delta_T = 50 °C
Склотекстоліт FR-4 (XY) 14 .. 17                 0.075 .. 0.085 мм
Алюміній 6061-T6        23.0                     0.115 мм
Нержавіюча сталь 304    16.0                     0.080 мм
Полікарбонат (PC)       65.0                     0.325 мм
ABS пластик             75 .. 90                 0.375 .. 0.450 мм
```

Якщо друкована плата довжиною 150 мм жорстко затиснута чотирма кутовими гвинтами M3 у бонки пластикового ABS-корпусу, при нагріванні від +20 °C до +70 °C (Delta_T = 50 °C) корпус розширюється на Delta_L_case = 150 * 80 * 10^-6 * 50 = 0.60 мм, тоді як плата FR-4 розширюється лише на Delta_L_pcb = 150 * 15 * 10^-6 * 50 = 0.11 мм.

Різниця зміщень delta = 0.60 - 0.11 = 0.49 мм діє як згинальне плече на пластикові бонки та текстоліт. За відсутності компенсаційних зазорів у кріпильних отворах плати (овальні пази або отвори діаметром 3.6 мм під гвинт M3 за стандартом IPC-2221) бонки відламуються біля основи, або текстоліт розшаровується навколо металізації кріпильного отвору.

---

## Інженерний регламент переходу між виробничими етапами

Для мінімізації фінансових ризиків апаратного стартапу або промислового підприємства рекомендується дотримуватися суворого поетапного регламенту вибору корпусу:

```
[Поетапна еволюція технологічного процесу корпусу]
Етап 1: НДДКР і компонування (1..5 шт)     -> FDM 3D-друк (PETG/ABS) або SLA
Етап 2: Валідація та сертифікація (10..50 шт) -> MJF 3D-друк (PA12) або дороблений алюмінієвий бокс
Етап 3: Пілотна серія (50..300 шт)          -> ЧПУ-фрезерування Al 6061 або доробка боксів Gainta/Hammond
Етап 4: Серійне виробництво (300..1 500 шт)   -> ЧПУ-фрезерування мультидетальними плитами або Soft-Tooling IM
Етап 5: Масова серія (від 1 500 шт і більше) -> Сталева прес-форма Hard Tooling P20/H13
```

1. **Фаза валідації концепту (1–5 шт):** друк виконується виключно на локальних FDM/SLA принтерах. Головна мета — фізична перевірка монтажу плати, сумісності роз'ємів із кабелями у реальних умовах та перевірка відсутності колізій із високими SMD-компонентами (трансформаторами, дроселями, електролітичними конденсаторами). Витрати: 20–50 USD.
2. **Фаза польових випробувань та попередньої сертифікації (10–50 шт):** використання промислового друку MJF PA12 або доопрацювання стандартних литих корпусів Hammond/Gainta. Вироби отримують необхідну ударостійкість, стійкість до ультрафіолету та базовий захист від вологи. Витрати: 25–45 USD за одиницю при NRE до 100 USD.
3. **Фаза дрібної комерційної серії (50–500 шт):** ЧПУ-фрезерування з алюмінію 6061-T6 з кольоровим анодуванням та лазерним гравіюванням забезпечує преміальний зовнішній вигляд, бездоганне тепловідведення та захист від вібрацій і перешкод. Собівартість складає 35–65 USD за штуку, що повністю перекривається маржинальністю комерційного обладнання без необхідності заморожування десятків тисяч доларів у прес-формах.
4. **Фаза масового масштабування (понад 1 500–2 000 шт):** після повної фіксації схемотехніки та контуру плати замовляється багатомісна сталева прес-форма з ресурсом 500 000 циклів. Питома ціна деталі миттєво знижується до 1.50–3.00 USD, а NRE амортизується до часток цента на один прилад.
