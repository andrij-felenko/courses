# Моделювання DC-bias дератингу та стабільності імпульсного перетворювача

Розрахунок вихідного фільтра імпульсного DC-DC перетворювача або лінійного стабілізатора за номінальною ємністю конденсаторів із каталогу — класична причина зриву стійкості живлення на макеті. Якщо інженер закладає два конденсатори номіналом 22 мкФ у корпусі 0603 на вихід 5 В, перетворювач у реальності працює не з 44 мкФ, а з ледь 11–14 мкФ. Цей проектний модуль реалізує інструмент для моделювання нелінійного спаду ємності багатошарових керамічних конденсаторів (MLCC) під дією постійної напруги зміщення (DC-bias) і розраховує дійсні динамічні параметри вихідного каскаду: реальні пульсації напруги, динамічне просідання при стрибку навантаження та зсув власного резонансного полюса вихідного LC-фільтра.

## Фізико-математична основа розрахунку

Ємність сегнетоелектричного конденсатора класу II (X5R, X7R, X8R) та класу III (Y5V, Z5U) під дією постійного електричного поля `E = V_dc / d` деградує внаслідок насичення поляризації доменів титанату барію (`BaTiO₃`). У міру зростання зовнішньої напруги спонтанні диполі кристалічної решітки примусово орієнтуються вздовж силових ліній поля, доменні стінки іммобілізуються (затискаються), і діелектрик втрачає здатність поляризуватися у відповідь на невеликий змінний сигнал пульсацій. Диференційна поляризовність `dP/dE` спадає, що призводить до обвалу ефективної діелектричної проникності `ε_r(E)`.

Для інженерного моделювання спаду ємності від прикладеної постійної напруги `V_dc` використовується модифікована емпірична функція насичення (гіперболічна апроксимація кривих насичення Ланжевена-Дебая):

```
C_eff(V_dc) = C_nom / (1 + (V_dc / V_half)^γ)
```

У цій математичній моделі:
- `C_nom` — початкова номінальна ємність, виміряна за стандартних умов (напруга зміщення `V_dc = 0 В`, змінний тестовий сигнал `0.5 В` або `1.0 В_rms` на частоті 1 кГц або 100 кГц);
- `V_half` — характерна напруга напівспаду, за якої ємність конденсатора знижується рівно вдвічі від початкового значення (`C_eff / C_nom = 0.50`);
- `γ` — коефіцієнт крутизни насичення, що відображає ступінь однорідності розміру кристалічних зерен і доменної структури кераміки.

Параметр `V_half` визначається напруженістю внутрішнього поля `E_half = V_half / d`, де `d` — товщина одного шару діелектрика між електродами MLCC. Оскільки в компактних корпусах площа пластин `A` мала, виробники змушені зменшувати `d` до 0.8–1.5 мкм задля збереження високої ємності `C = N · ε₀ · ε_r · A / d`. Через це у дрібних типорозмірах напруженість поля різко зростає при тих самих вольтах, а відношення `V_half / V_rated` суттєво зменшується.

На основі узагальнення масивів експериментальних вимірювань виробників пасивних компонентів поведінка класів діелектрика та типорозмірів нормується такими співвідношеннями:
- **Клас I (C0G / NP0):** параелектричний діелектрик на основі цирконату кальцію (`CaZrO₃`) не має спонтанної поляризації доменів. Втрати ємності відсутні (`V_half → ∞`, `C_eff(V_dc) = C_nom` у всьому діапазоні до напруги пробою).
- **Клас II (X7R):** оптимізований склад із легуючими добавками рідкоземельних елементів, що розмивають пік Кюрі. Коефіцієнт крутизни `γ ≈ 1.35...1.45`. Для великих корпусів (1206, 1210) `V_half ≈ 0.85...1.10 · V_rated`; для середніх (0805) `V_half ≈ 0.60 · V_rated`; для дрібних (0603) `V_half ≈ 0.45 · V_rated`.
- **Клас II (X5R):** високоємна кераміка з гранично тонкими діелектричними шарами. Крутизна `γ ≈ 1.60...1.70`, а напруга напівспаду знижена на 15–20% відносно X7R (для 0402 `V_half ≈ 0.25...0.30 · V_rated`).
- **Клас III (Y5V):** нелегований титанат барію з гігантською початковою проникністю (`ε_r > 15000`), що перебуває в критичному стані біля точки Кюрі. Спад має катастрофічний характер: `γ ≈ 2.2...2.5`, а `V_half ≈ 0.15...0.20 · V_rated`.

Після обчислення ефективної ємності окремого елемента сумарна ємність вихідної батареї з `N` паралельно з'єднаних однакових конденсаторів становить:

```
C_total = N · C_eff(V_dc)
```

При паралельному з'єднанні кількох MLCC еквівалентна паразитна індуктивність (ESL) зменшується пропорційно кількості корпусів: `ESL_total = ESL_unit / N`. Це розширює смугу ефективного шунтування комутаційних завад до десятків мегагерц. Проте монтаж вимагає симетричного розміщення компонентів на платі: якщо один конденсатор розташований впритул до виводу дроселя, а інший — за довгими тонкими доріжками, високочастотний струм пульсацій піде виключно крізь найближчий корпус, викликаючи його підвищений саморозігрів та прискорену деградацію.

## Вплив на перетворювач живлення: формули та ланцюжки розрахунку

Вихідний каскад понижувального (Buck) перетворювача містить силовий дросель індуктивністю `L` та вихідний ємнісний фільтр `C_total` з еквівалентним послідовним опором `ESR_total = ESR_unit / N`. Програма розраховує чотири взаємопов'язані фізичні показники роботи перетворювача:

1. **Розмах пульсацій струму в силовому дроселі (`ΔI_L`):**
   Під час замкненого стану верхнього ключа струм дроселя лінійно наростає під дією різниці напруг `(V_in − V_out)`. За період комутації `T_sw = 1 / f_sw` розмах струму становить:
   ```
   ΔI_L = (V_in − V_out) · V_out / (f_sw · L · V_in)
   ```

2. **Амплітуда пульсацій вихідної напруги (`ΔV_out`):**
   Змінна складова струму дроселя замикається крізь вихідний конденсаторний фільтр. Пульсація напруги складається з двох ортогональних часток — інтегрування струму ємністю та падіння на активному опорі втрат (ESR):
   ```
   ΔV_cap = ΔI_L / (8 · f_sw · C_total)
   ΔV_esr = ΔI_L · (ESR_unit / N)
   ΔV_out = ΔV_cap + ΔV_esr
   ```
   Для керамічних конденсаторів частка `ΔV_esr` зазвичай мала (одиниці міліом), тому саме ємнісна складова `ΔV_cap` домінує на виході. Падіння `C_total` у 4 рази призводить до майже чотирикратного зростання пульсацій напруги на живильній шині.

3. **Зсув резонансного полюса вихідного фільтра (`f_p`):**
   Силовий контур утворює комплексно-спряжену пару полюсів другого порядку (або домінантний полюс навантаження у разі струмового керування Peak Current Mode Control). Частота LC-резонансу дорівнює:
   ```
   f_p = 1 / (2 · π · √(L · C_total))
   ```
   Якщо номінальна ємність забезпечувала полюс на частоті `f_p_nom = 8 кГц`, а під робочою напругою ємність просіла на 75% (`C_total = 0.25 · C_nom`), нова частота полюса становить:
   ```
   f_p_actual = f_p_nom / √(0.25) = 2 · f_p_nom = 16 кГц
   ```
   Зсув полюса вдвічі вище за частотою розширює смугу пропускання контуру зворотного зв'язку, але компенсаційний ланцюг зворотного зв'язку (Type II або Type III), налаштований на `f_p_nom`, не встигає підняти фазу. У точці одиничного підсилення фазовий зсув підходить до −180°, запас фази (`Phase Margin`) падає нижче критичних 30°, викликаючи високочастотний дзвін вихідної напруги або повний перехід у режим незгасаючих автоколивань.

4. **Динамічне просідання напруги під час стрибка навантаження (`ΔV_sag`):**
   При різкому переході процесора або радіомодуля з режиму сну в активний стан навантаження стрибкоподібно зростає на величину `ΔI_step`. Контур стабілізації перетворювача через обмежену смугу пропускання реагує із затримкою `t_resp ≈ 1 / (2 · π · f_cross)` (зазвичай 5–15 мкс). Протягом цього часу весь дефіцит струму компенсується виключно зарядом вихідних конденсаторів:
   ```
   ΔV_sag = ΔI_step · t_resp / C_total
   ```
   Якщо ефективна ємність зменшилася вчетверо, глибина просідання напруги зростає вчетверо, що гарантовано спричиняє спрацьовування захисту від зниження напруги (UVLO) та аварійне перезавантаження мікроконтролера.

## Компенсація контуру зворотного зв'язку за умов нестабільної ємності

Коли вихідна ємність `C_total(V_dc)` залежить від робочої напруги й температури, інженер постає перед дилемою: під яку саме ємність розраховувати компенсаційний підсилювач помилки?

У перетворювачах з керуванням за піковим струмом (Current-Mode Control) силовий каскад перетворюється на кероване джерело струму, а вихідний полюс стає полюсом першого порядку:

```
f_p_load = 1 / (2 · π · R_load · C_total)
```

де `R_load = V_out / I_out`. Якщо навантаження змінюється від холостого ходу до максимуму, а ємність деградує від запуску (`V_out = 0 В`) до номіналу (`V_out = 5 В`), положення полюса блукає в діапазоні двох-трьох декад частоти.

Щоб запобігти зриву стійкості:
1. Нуль компенсатора Type II `f_z_comp = 1 / (2 · π · R_comp · C_comp)` встановлюють на частоту найнижчого можливого положення полюса (при максимальній ємності на старті та повному навантаженні).
2. Високочастотний полюс компенсатора `f_p_comp = 1 / (2 · π · R_comp · C_hf)` розміщують на половині частоти комутації `0.5 · f_sw`, щоб гасити комутаційні шуми, але не зачіпати фазу на частоті зрізу `f_cross`.
3. Частоту одиничного підсилення `f_cross` обирають консервативно: не вище `f_sw / 10` (для найгіршого випадку найменшої залишкової ємності), забезпечуючи запас фази не менше 60° у всьому діапазоні напруг.

## Струм саморозігріву та обмеження за змінним струмом

Крім падіння ємності під постійною напругою, конденсатори у вихідному фільтрі зазнають дії високочастотного змінного струму пульсацій `I_rms ≈ ΔI_L / √12`. Цей струм протікає крізь еквівалентний послідовний опір `ESR`, розсіюючи активну теплову потужність:

```
P_loss = I_rms² · ESR_unit
```

Теплова потужність викликає підвищення температури керамічного тіла конденсатора:

```
ΔT = P_loss · R_th_ja
```

де `R_th_ja` — тепловий опір від кристала конденсатора до навколишнього повітря крізь мідні полігони плати (становить близько 80–120 °C/Вт для 0805 і 50–70 °C/Вт для 1206). Саморозігрів навіть на 15–20 °C є критичним: він зсуває робочу точку кераміки X5R/X7R ближче до точки фазового переходу, що посилює падіння ємності через термо-bias взаємодію. Проектуючи фільтр, необхідно перевіряти, щоб дійсний струм через один MLCC не перевищував каталожного ліміту виробника (зазвичай 1.5–2.5 А_rms для 0805/1206).

## Оптимізація специфікації компонентів (BOM Optimization)

Розглянемо практичний приклад оптимізації шини живлення сучасного мікропроцесора або SoC (напруга 1.2 В, струм до 6 А, допустимий розмах пульсацій до 15 мВ).

**Помилковий підхід (мініатюризація за каталожним номіналом):**
Інженер встановлює шість конденсаторів номіналом 10 мкФ 6.3V у корпусі 0402 X5R. За каталогом сумарна ємність становить 60 мкФ. Проте під напругою 1.2 В (близько 20% від `V_rated`) кожен конденсатор 0402 втрачає близько 35% ємності, забезпечуючи реальні 6.5 мкФ. Сумарна ємність становить лише 39 мкФ. При переході процесора в робочий стан просідання напруги перевищує 40 мВ, викликаючи збій обчислень ядра.

**Оптимальний підхід (гібридна фільтрація):**
Інженер встановлює один танталово-полімерний конденсатор 47 мкФ 6.3V (корпус 3528, нульовий DC-bias ефект, низький ESR 25 мОм) паралельно з двома керамічними конденсаторами 10 мкФ 25V у корпусі 0805 X7R.
- Танталово-полімерний конденсатор гарантовано утримує повні 47 мкФ постійної ємності під будь-якою напругою, повністю покриваючи дефіцит заряду при стрибках струму;
- Керамічні MLCC 0805 25V під напругою 1.2 В працюють при менш ніж 5% від номіналу напруги, зберігаючи понад 95% своєї ємності (сумарно 19 мкФ) і забезпечуючи наднизький імпеданс на частоті перемикання 1–2 МГц для фільтрації високочастотних комутаційних голок.

Така гібридна комбінація забезпечує сумарні 66 мкФ дійсного запасу заряду, стабільну роботу контуру в будь-яких температурних режимах і займає на платі меншу площу, ніж десяток розсипних MLCC.

## Покроковий розбір структури програми

Програма побудована за модульним принципом із чітким розділенням фізичної моделі компонентів, конфігурації силовой топології та алгоритму оцінки стабільності:

1. `DielectricClass` та `PackageSize` — типізовані переліки, що інкапсулюють класи кераміки та стандартні геометричні розміри корпусів EIA (від 0402 до 1210).
2. `compute_dc_bias_factor()` — обчислювальне ядро дератингу, яке за параметрами корпусу й матеріалу розраховує коефіцієнт утримання ємності `k_bias = C_eff / C_nom`.
3. `simulate_buck_output()` — симулятор силовой секції, що перетворює електричні характеристики перетворювача та конденсаторної батареї на комплексний масив метрик (розмах струму дроселя, дійсні пульсації напруги, динамічне просідання та зсув полюса).
4. `print_analysis_report()` — генератор інженерного звіту з виділенням зон ризику та прямими рекомендаціями щодо зміни типорозміру чи технології конденсаторів.

## Реалізація на C та C++

У наведеному коді реалізовано повний розрахунковий модуль. Програма містить математичні моделі дератингу, аналізує конфігурацію перетворювача та порівнює два інженерні рішення для шини 5.0 В: бюджетні дрібні конденсатори 0603 X5R 10V проти оптимізованих компонентів 1206 X7R 25V та прецизійних C0G 50V.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef enum {
    DIELECTRIC_C0G,
    DIELECTRIC_X7R,
    DIELECTRIC_X5R,
    DIELECTRIC_Y5V
} DielectricClass;

typedef enum {
    PKG_0402,
    PKG_0603,
    PKG_0805,
    PKG_1206,
    PKG_1210
} PackageSize;

typedef struct {
    double nom_cap_uf;       /* Номінальна ємність одного конденсатора, мкФ */
    double rated_voltage;    /* Номінальна гранична напруга за каталогом, В */
    DielectricClass dielectric;
    PackageSize package_size;
    double esr_mohm;         /* Еквівалентний послідовний опір (ESR), мОм */
    int count;               /* Кількість паралельно з'єднаних конденсаторів */
} MlccArray;

typedef struct {
    double v_in;             /* Вхідна напруга живлення, В */
    double v_out;            /* Вихідна стабілізована напруга, В */
    double f_sw_khz;         /* Частота комутації перетворювача, кГц */
    double l_ind_uh;         /* Індуктивність силового дроселя, мкГн */
    double i_step_a;         /* Величина динамічного стрибка струму навантаження, А */
    double t_resp_us;        /* Характерний час реакції контуру зворотного зв'язку, мкс */
} BuckCircuit;

typedef struct {
    double eff_cap_per_unit_uf;
    double eff_total_cap_uf;
    double cap_retention_pct;
    double inductor_ripple_a;
    double v_ripple_nom_mv;
    double v_ripple_actual_mv;
    double pole_nom_khz;
    double pole_actual_khz;
    double v_sag_actual_mv;
    bool is_stable;
} SimulationResult;

static const char* dielectric_to_str(DielectricClass d) {
    switch (d) {
        case DIELECTRIC_C0G: return "C0G/NP0 (Клас I)";
        case DIELECTRIC_X7R: return "X7R (Клас II)";
        case DIELECTRIC_X5R: return "X5R (Клас II)";
        case DIELECTRIC_Y5V: return "Y5V (Клас III)";
        default:             return "Невідомий";
    }
}

static const char* package_to_str(PackageSize p) {
    switch (p) {
        case PKG_0402: return "0402 (1.0x0.5 мм)";
        case PKG_0603: return "0603 (1.6x0.8 мм)";
        case PKG_0805: return "0805 (2.0x1.25 мм)";
        case PKG_1206: return "1206 (3.2x1.6 мм)";
        case PKG_1210: return "1210 (3.2x2.5 мм)";
        default:       return "Невідомий";
    }
}

/* Обчислення відносного залишку ємності за моделлю насичення поляризації */
static double compute_dc_bias_factor(DielectricClass d, PackageSize p, double v_dc, double v_rated) {
    if (d == DIELECTRIC_C0G || v_dc <= 0.0) {
        return 1.0;
    }

    double v_half_ratio;
    double gamma;

    /* Геометричний фактор: більший корпус має товстіший діелектричний шар d */
    switch (p) {
        case PKG_0402: v_half_ratio = 0.30; break;
        case PKG_0603: v_half_ratio = 0.45; break;
        case PKG_0805: v_half_ratio = 0.60; break;
        case PKG_1206: v_half_ratio = 0.85; break;
        case PKG_1210: v_half_ratio = 1.10; break;
        default:       v_half_ratio = 0.50; break;
    }

    /* Фізико-хімічний фактор сегнетоелектричного матеріалу */
    switch (d) {
        case DIELECTRIC_X7R:
            gamma = 1.40;
            break;
        case DIELECTRIC_X5R:
            gamma = 1.65;
            v_half_ratio *= 0.85;
            break;
        case DIELECTRIC_Y5V:
            gamma = 2.40;
            v_half_ratio *= 0.40;
            break;
        default:
            gamma = 1.50;
            break;
    }

    double v_half = v_rated * v_half_ratio;
    double normalized = v_dc / v_half;
    double derating = 1.0 / (1.0 + pow(normalized, gamma));

    /* Нижнє фізичне плато залишкової ємності */
    if (derating < 0.02) {
        derating = 0.02;
    }
    return derating;
}

SimulationResult simulate_buck_output(const MlccArray* cap, const BuckCircuit* ckt) {
    SimulationResult res;
    double v_dc = ckt->v_out;
    double derate_factor = compute_dc_bias_factor(cap->dielectric, cap->package_size, v_dc, cap->rated_voltage);

    res.eff_cap_per_unit_uf = cap->nom_cap_uf * derate_factor;
    res.eff_total_cap_uf = res.eff_cap_per_unit_uf * (double)cap->count;
    res.cap_retention_pct = derate_factor * 100.0;

    double nom_total_cap_uf = cap->nom_cap_uf * (double)cap->count;

    /* Розрахунок струму пульсацій силового дроселя */
    double f_sw_hz = ckt->f_sw_khz * 1e3;
    double l_h = ckt->l_ind_uh * 1e-6;
    res.inductor_ripple_a = (ckt->v_in - ckt->v_out) * ckt->v_out / (f_sw_hz * l_h * ckt->v_in);

    /* Пульсації напруги при ідеальній номінальній ємності */
    double c_nom_f = nom_total_cap_uf * 1e-6;
    double esr_total_ohm = (cap->esr_mohm * 1e-3) / (double)cap->count;
    double v_rip_cap_nom = res.inductor_ripple_a / (8.0 * f_sw_hz * c_nom_f);
    double v_rip_esr = res.inductor_ripple_a * esr_total_ohm;
    res.v_ripple_nom_mv = (v_rip_cap_nom + v_rip_esr) * 1e3;

    /* Пульсації напруги з урахуванням реального DC-bias дератингу */
    double c_eff_f = res.eff_total_cap_uf * 1e-6;
    double v_rip_cap_act = res.inductor_ripple_a / (8.0 * f_sw_hz * c_eff_f);
    res.v_ripple_actual_mv = (v_rip_cap_act + v_rip_esr) * 1e3;

    /* Розрахунок резонансної частоти LC-полюса */
    res.pole_nom_khz = (1.0 / (2.0 * M_PI * sqrt(l_h * c_nom_f))) * 1e-3;
    res.pole_actual_khz = (1.0 / (2.0 * M_PI * sqrt(l_h * c_eff_f))) * 1e-3;

    /* Динамічне просідання напруги під час стрибка навантаження */
    double t_resp_s = ckt->t_resp_us * 1e-6;
    res.v_sag_actual_mv = (ckt->i_step_a * t_resp_s / c_eff_f) * 1e3;

    /* Інженерний критерій стійкості: зсув полюса фільтра не більше ніж у 1.6 раза */
    res.is_stable = (res.pole_actual_khz / res.pole_nom_khz) <= 1.60;

    return res;
}

void print_analysis_report(const MlccArray* cap, const BuckCircuit* ckt, const SimulationResult* res) {
    printf("==================================================================\n");
    printf("  АНАЛІЗ DC-BIAS ЕФЕКТУ ДЛЯ ВИХІДНОГО ФІЛЬТРА DCDC ПЕРЕТВОРЮВАЧА\n");
    printf("==================================================================\n");
    printf("Конфігурація перетворювача:\n");
    printf("  Вхідна / Вихідна напруга:     %.1f В -> %.2f В\n", ckt->v_in, ckt->v_out);
    printf("  Частота комутації / Дросель:   %.0f кГц / %.2f мкГн\n", ckt->f_sw_khz, ckt->l_ind_uh);
    printf("  Стрибок струму / Час реакції:  %.1f А / %.1f мкс\n\n", ckt->i_step_a, ckt->t_resp_us);

    printf("Конденсаторна батарея (вихід):\n");
    printf("  Кількість та тип:             %d x %.1f мкФ (%s, %s)\n",
           cap->count, cap->nom_cap_uf, dielectric_to_str(cap->dielectric), package_to_str(cap->package_size));
    printf("  Номінальна напруга MLCC:      %.1f В\n", cap->rated_voltage);
    printf("  Номінальна сумарна ємність:   %.2f мкФ\n\n", cap->nom_cap_uf * (double)cap->count);

    printf("Результати розрахунку під робочою напругою %.2f В:\n", ckt->v_out);
    printf("  Залишок ємності (DC-bias):    %.1f %% від номіналу\n", res->cap_retention_pct);
    printf("  Ефективна ємність одиниці:    %.2f мкФ (номінал %.1f мкФ)\n",
           res->eff_cap_per_unit_uf, cap->nom_cap_uf);
    printf("  Сумарна ефективна ємність:    %.2f мкФ\n", res->eff_total_cap_uf);
    printf("  Пульсації вихідної напруги:   %.1f мВ (номінально мало бути %.1f мВ)\n",
           res->v_ripple_actual_mv, res->v_ripple_nom_mv);
    printf("  Просідання при навантаженні:  %.1f мВ\n", res->v_sag_actual_mv);
    printf("  Частота полюса LC-фільтра:    %.2f кГц -> %.2f кГц (зсув у %.2fx)\n",
           res->pole_nom_khz, res->pole_actual_khz, res->pole_actual_khz / res->pole_nom_khz);

    if (res->is_stable) {
        printf("  Оцінка стійкості контуру:     [ ДОБРЕ: запас фази збережено ]\n");
    } else {
        printf("  Оцінка стійкості контуру:     [ КРИТИЧНО: ризик генерації/дзвону! ]\n");
        printf("  Рекомендація:                 збільшити корпус до 1206 або додати паралельні MLCC.\n");
    }
    printf("==================================================================\n\n");
}

int main(void) {
    BuckCircuit buck = {
        .v_in = 12.0,
        .v_out = 5.0,
        .f_sw_khz = 1000.0,
        .l_ind_uh = 2.2,
        .i_step_a = 1.5,
        .t_resp_us = 8.0
    };

    /* Сценарій 1: Популярний, але небезпечний вибір — 0603 X5R 22uF 10V */
    MlccArray small_cap = {
        .nom_cap_uf = 22.0,
        .rated_voltage = 10.0,
        .dielectric = DIELECTRIC_X5R,
        .package_size = PKG_0603,
        .esr_mohm = 4.0,
        .count = 2
    };

    /* Сценарій 2: Інженерно грамотний вибір — 1206 X7R 22uF 25V */
    MlccArray robust_cap = {
        .nom_cap_uf = 22.0,
        .rated_voltage = 25.0,
        .dielectric = DIELECTRIC_X7R,
        .package_size = PKG_1206,
        .esr_mohm = 3.0,
        .count = 2
    };

    printf("ТЕСТ 1: Компактні конденсатори 0603 на шині 5 В\n");
    SimulationResult r1 = simulate_buck_output(&small_cap, &buck);
    print_analysis_report(&small_cap, &buck, &r1);

    printf("ТЕСТ 2: Оптимізовані за DC-bias конденсатори 1206 25V на шині 5 В\n");
    SimulationResult r2 = simulate_buck_output(&robust_cap, &buck);
    print_analysis_report(&robust_cap, &buck, &r2);

    return 0;
}
```
```cpp
#include <iostream>
#include <iomanip>
#include <string_view>
#include <cmath>
#include <numbers>
#include <vector>
#include <span>

enum class DielectricClass {
    C0G,
    X7R,
    X5R,
    Y5V
};

enum class PackageSize {
    Pkg0402,
    Pkg0603,
    Pkg0805,
    Pkg1206,
    Pkg1210
};

struct MlccSpec {
    double nominal_cap_uf{10.0};
    double rated_voltage{16.0};
    DielectricClass dielectric{DielectricClass::X7R};
    PackageSize package_size{PackageSize::Pkg0805};
    double esr_mohm{3.0};
    int count{1};
};

struct BuckParams {
    double v_in{12.0};
    double v_out{5.0};
    double f_sw_khz{1000.0};
    double l_ind_uh{2.2};
    double i_step_a{1.5};
    double t_resp_us{8.0};
};

struct OutputMetrics {
    double eff_cap_per_unit_uf;
    double eff_total_cap_uf;
    double retention_pct;
    double inductor_ripple_a;
    double v_ripple_nom_mv;
    double v_ripple_actual_mv;
    double pole_nom_khz;
    double pole_actual_khz;
    double v_sag_actual_mv;
    bool is_stable;
};

class MlccBiasAnalyzer {
public:
    [[nodiscard]] static constexpr std::string_view to_string(DielectricClass d) noexcept {
        switch (d) {
            case DielectricClass::C0G: return "C0G/NP0 (Клас I)";
            case DielectricClass::X7R: return "X7R (Клас II)";
            case DielectricClass::X5R: return "X5R (Клас II)";
            case DielectricClass::Y5V: return "Y5V (Клас III)";
        }
        return "Невідомий";
    }

    [[nodiscard]] static constexpr std::string_view to_string(PackageSize p) noexcept {
        switch (p) {
            case PackageSize::Pkg0402: return "0402 (1.0x0.5 мм)";
            case PackageSize::Pkg0603: return "0603 (1.6x0.8 мм)";
            case PackageSize::Pkg0805: return "0805 (2.0x1.25 мм)";
            case PackageSize::Pkg1206: return "1206 (3.2x1.6 мм)";
            case PackageSize::Pkg1210: return "1210 (3.2x2.5 мм)";
        }
        return "Невідомий";
    }

    [[nodiscard]] static double calculate_retention(const MlccSpec& spec, double v_dc) noexcept {
        if (spec.dielectric == DielectricClass::C0G || v_dc <= 0.0) {
            return 1.0;
        }

        double v_half_ratio = 0.50;
        switch (spec.package_size) {
            case PackageSize::Pkg0402: v_half_ratio = 0.30; break;
            case PackageSize::Pkg0603: v_half_ratio = 0.45; break;
            case PackageSize::Pkg0805: v_half_ratio = 0.60; break;
            case PackageSize::Pkg1206: v_half_ratio = 0.85; break;
            case PackageSize::Pkg1210: v_half_ratio = 1.10; break;
        }

        double gamma = 1.40;
        switch (spec.dielectric) {
            case DielectricClass::X7R:
                gamma = 1.40;
                break;
            case DielectricClass::X5R:
                gamma = 1.65;
                v_half_ratio *= 0.85;
                break;
            case DielectricClass::Y5V:
                gamma = 2.40;
                v_half_ratio *= 0.40;
                break;
            default:
                break;
        }

        const double v_half = spec.rated_voltage * v_half_ratio;
        const double normalized = v_dc / v_half;
        const double retention = 1.0 / (1.0 + std::pow(normalized, gamma));

        return std::max(retention, 0.02);
    }

    [[nodiscard]] static OutputMetrics evaluate(const MlccSpec& cap, const BuckParams& pwr) noexcept {
        const double retention = calculate_retention(cap, pwr.v_out);
        const double eff_unit = cap.nominal_cap_uf * retention;
        const double eff_total = eff_unit * cap.count;
        const double nom_total = cap.nominal_cap_uf * cap.count;

        const double f_sw_hz = pwr.f_sw_khz * 1e3;
        const double l_h = pwr.l_ind_uh * 1e-6;
        const double i_rip = (pwr.v_in - pwr.v_out) * pwr.v_out / (f_sw_hz * l_h * pwr.v_in);

        const double c_nom_f = nom_total * 1e-6;
        const double c_eff_f = eff_total * 1e-6;
        const double esr_total_ohm = (cap.esr_mohm * 1e-3) / cap.count;

        const double v_rip_esr = i_rip * esr_total_ohm;
        const double v_rip_nom = (i_rip / (8.0 * f_sw_hz * c_nom_f) + v_rip_esr) * 1e3;
        const double v_rip_act = (i_rip / (8.0 * f_sw_hz * c_eff_f) + v_rip_esr) * 1e3;

        const double pole_nom = (1.0 / (2.0 * std::numbers::pi * std::sqrt(l_h * c_nom_f))) * 1e-3;
        const double pole_act = (1.0 / (2.0 * std::numbers::pi * std::sqrt(l_h * c_eff_f))) * 1e-3;

        const double t_resp_s = pwr.t_resp_us * 1e-6;
        const double v_sag_act = (pwr.i_step_a * t_resp_s / c_eff_f) * 1e3;

        const bool stable = (pole_act / pole_nom) <= 1.60;

        return {
            .eff_cap_per_unit_uf = eff_unit,
            .eff_total_cap_uf = eff_total,
            .retention_pct = retention * 100.0,
            .inductor_ripple_a = i_rip,
            .v_ripple_nom_mv = v_rip_nom,
            .v_ripple_actual_mv = v_rip_act,
            .pole_nom_khz = pole_nom,
            .pole_actual_khz = pole_act,
            .v_sag_actual_mv = v_sag_act,
            .is_stable = stable
        };
    }

    static void print_report(const MlccSpec& cap, const BuckParams& pwr, const OutputMetrics& m) {
        std::cout << "==================================================================\n"
                  << "  АНАЛІЗ DC-BIAS ДЕРАТИНГУ ДЛЯ ВИХОДУ DCDC (C++20)\n"
                  << "==================================================================\n"
                  << "Конфігурація: " << pwr.v_in << " В -> " << pwr.v_out << " В, "
                  << pwr.f_sw_khz << " кГц, L = " << pwr.l_ind_uh << " мкГн\n"
                  << "Конденсатори: " << cap.count << " x " << cap.nominal_cap_uf << " мкФ "
                  << to_string(cap.dielectric) << " " << to_string(cap.package_size)
                  << " (" << cap.rated_voltage << " В номінал)\n\n"
                  << std::fixed << std::setprecision(2)
                  << "Результати моделювання:\n"
                  << "  Залишок ємності:              " << m.retention_pct << " %\n"
                  << "  Сумарна ефективна ємність:    " << m.eff_total_cap_uf << " мкФ (номінал "
                  << (cap.nominal_cap_uf * cap.count) << " мкФ)\n"
                  << "  Пульсації напруги (робочі):   " << m.v_ripple_actual_mv << " мВ (номінальні "
                  << m.v_ripple_nom_mv << " мВ)\n"
                  << "  Просідання при стрибку 1.5 А: " << m.v_sag_actual_mv << " мВ\n"
                  << "  Зсув резонансного полюса:     " << m.pole_nom_khz << " кГц -> "
                  << m.pole_actual_khz << " кГц (x" << (m.pole_actual_khz / m.pole_nom_khz) << ")\n"
                  << "  Статус стабільності контуру:  "
                  << (m.is_stable ? "[ СТІЙКИЙ ]" : "[ КРИТИЧНИЙ ЗСУВ ПОЛЮСА / РИЗИК ДЗВОНУ ]")
                  << "\n==================================================================\n\n";
    }
};

int main() {
    const BuckParams buck_cfg{
        .v_in = 12.0,
        .v_out = 5.0,
        .f_sw_khz = 1000.0,
        .l_ind_uh = 2.2,
        .i_step_a = 1.5,
        .t_resp_us = 8.0
    };

    const std::vector<MlccSpec> test_suite = {
        { .nominal_cap_uf = 22.0, .rated_voltage = 10.0, .dielectric = DielectricClass::X5R, .package_size = PackageSize::Pkg0603, .esr_mohm = 4.0, .count = 2 },
        { .nominal_cap_uf = 22.0, .rated_voltage = 25.0, .dielectric = DielectricClass::X7R, .package_size = PackageSize::Pkg1206, .esr_mohm = 3.0, .count = 2 },
        { .nominal_cap_uf = 10.0, .rated_voltage = 50.0, .dielectric = DielectricClass::C0G, .package_size = PackageSize::Pkg1210, .esr_mohm = 2.0, .count = 4 }
    };

    for (const auto& cap : test_suite) {
        const auto metrics = MlccBiasAnalyzer::evaluate(cap, buck_cfg);
        MlccBiasAnalyzer::print_report(cap, buck_cfg, metrics);
    }

    return 0;
}
```
:::

## Динамічна верифікація на випробувальному стенді

Для експериментального підтвердження розрахунків на фізичній платі застосовують метод перехідної характеристики навантаження (Transient Step Response):

1. **Підключення швидкого електронного навантаження:** На вихід перетворювача підключають транзисторний комутатор струму з часом наростання фронту `t_rise ≤ 100 нс`.
2. **Осцилографічний контроль:** Щуп осцилографа обов'язково підключають через коротку пружинну заземлювальну насадку безпосередньо до вихідних контактів MLCC, увімкнувши вхідне відкрите коло по змінному струму (AC Coupling).
3. **Оцінка дзвону за формою сигналу:**
   - Якщо напруга після стрибка струму здійснює лише одне плавне повернення до стабілізованого рівня без переходів через нуль (аперіодичний процес), запас фази перевищує 60°.
   - Якщо спостерігаються 2–3 затухаючі коливання, запас фази становить 35°–45°.
   - Якщо виникає тривалий дзвін із понад 5 періодів коливань або незгасаюча генерація, ефективна ємність вихідного фільтра під напругою виявилася занизькою, і схема перебуває на межі аварії.

## Інженерні пастки при вимірюванні та верифікації

1. **Рівень вимірювального AC-сигналу в LCR-метрах.**
   Стандартні лабораторні місткові вимірювачі подають змінну напругу `V_ac = 0.5 В` або `1.0 В_rms` на частоті 1 кГц при нульовому постійному зміщенні (`V_dc = 0 В`). За цих умов прилад показує повний номінал. Якщо ввімкнути внутрішнє джерело DC-bias LCR-метра на 5 В, показання миттєво падають до значень, обчислених вище. Вимірювання без зовнішнього постійного зміщення є головною причиною пропуску дефекту на етапі вхідного контролю компонентів.

2. **Кумулятивний ефект температури й напруги (Thermal-Bias Coupling).**
   Падіння ємності через DC-bias накладається на температурний коефіцієнт (TCC). При нагріванні MLCC класу X5R до 85 °C усередині герметичного корпусу приладу початкова ємність зменшується на 15% через температуру, а потім ще на 75% через напругу живлення. Сумарний залишок ємності може складати менше 15–20% від початкового каталожного значення. Розрахунок надійності вимагає перемноження температурного коефіцієнта на коефіцієнт напруги зміщення.

3. **Ефект старіння кераміки (Aging Rate).**
   Титанат барію після проходження точки Кюрі (під час паяння в печі оплавлення при 260 °C) зазнає спонтанного фазового переходу. З плином часу доменні стінки самовільно перегруповуються в енергетично вигідніші конфігурації, що супроводжується втратою ємності зі швидкістю 1.5–3.0% на кожну декаду годин (Aging per decade hour). Конденсатор, який щойно вийшов із печі, має на 10–15% вищу ємність, ніж той самий компонент після 1000 годин роботи на платі.

4. **Акустичний п'єзоефект (Piezoelectric Singing Capacitor).**
   Сегнетоелектрична природа BaTiO3 наділяє кераміку класу II вираженими п'єзоелектричними властивостями. Під дією пульсацій напруги `ΔV_out` конденсатор механічно стискається й розширюється на частоті пульсацій. Якщо частота перемикання або періодичного навантаження потрапляє в чутний діапазон (20 Гц — 20 кГц), плата починає видавати виразний високочастотний писк. Використання полімерних танталових конденсаторів або кераміки C0G повністю усуває цей паразитичний акустичний шум.

5. **Інтеграція в SPICE-симулятори (LTspice, QSPICE, NGspice).**
   Більшість стандартних бібліотек SPICE моделюють конденсатор як ідеальну лінійну ємність `C`. Для коректного моделювання схеми необхідно або вручну прописувати залишкове значення `C_eff`, обчислене за наведеним алгоритмом, або використовувати поведінкові нелінійні моделі джерела заряду `Q = C_nom · V_half · arctan(V / V_half)` чи офіційні динамічні `.subckt` макромоделі виробників (Murata, TDK).
