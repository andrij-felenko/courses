# ⚙️ Розрахунок геометрії та паразитної індуктивності зворотного струму

Аналіз цілісності сигналів (Signal Integrity) та електромагнітної сумісності (EMC) вимагає кількісної оцінки петлі зворотного струму. Інженер не може спиратися лише на якісні правила «не ріж площину» або «став перехідні отвори поруч»: під час проєктування високошвидкісних інтерфейсів (DDR, PCIe, USB, Gigabit Ethernet) необхідно точно знати частоту переходу `f_c` між резистивним та індуктивним режимами, паразитну індуктивність обходу розрізів `ΔL`, додаткову індуктивність сигнальних via без зворотних отворів та очікуване зростання електромагнітного випромінювання у децибелах.

Цей інструмент розраховує повний електромагнітний профіль зворотного шляху на друкованій платі:
1. **Частоту кросоверу `f_c`** — границю, вище якої струм припиняє розтікатися по шляху найменшого активного опору `R` і стягується під сигнальну доріжку за законом найменшої індуктивності `L`.
2. **Паразитну індуктивність мікросмужки над суцільною площиною проти обходу розрізу** — точну додаткову індуктивність `ΔL` петлі та амплітуду дзвону `V = L · (di/dt)` при заданій крутизні фронту перемикання.
3. **Індуктивність переходу між шарами (Via Transition)** — порівняння конфігурацій без зворотного отвору, з одним, двома та чотирма симетричними return via (G-S-G та квадро-кільце).
4. **Різницю напруженості випромінюваного поля `ΔEMI`** — розрахунок зростання випромінювання контуру як магнітного диполя у децибелах.

## Математичні основи розрахунку

### 1. Частота переходу між режимами R та L

Повний імпеданс контуру дорівнює:

```text
Z(f) = √(R_dc² + (2π · f · L_loop)²)
```

Частота переходу `f_c`, на якій реактивний індуктивний опір зрівнюється з активним омічним опором (`2π · f · L = R`), обчислюється як:

```text
f_c = R_dc / (2π · L_loop)
```

Де:
- `R_dc` — сумарний активний опір прямого провідника та розподіленого шару міді (Ом);
- `L_loop` — петльова індуктивність контуру (Гн).

Для типової мікросмужки на платі FR-4 товщиною діелектрика 0.2 мм активний опір доріжки шириною 0.35 мм і довжиною 25 мм становить близько 35 мОм, а петльова індуктивність над суцільною площиною — близько 7.5 нГн. Звідси частота кросоверу:

```text
f_c = 0.035 / (2π · 7.5 · 10⁻⁹) ≈ 742 кГц
```

Будь-який цифровий сигнал із фронтом наростання `t_r ≤ 5` нс має ефективну смугу частот `f_knee ≈ 0.35 / t_r ≥ 70` МГц, що на два порядки перевищує `f_c`. Отже, такий струм повертається виключно шляхом найменшої індуктивності.

### 2. Паразитна індуктивність обходу розрізу

Коли сигнальна лінія перетинає щілину шириною `w_slot`, зворотний струм огинає розріз, долаючи додаткову довжину обходу `s`. Додаткова паразитна індуктивність петлі обходу `ΔL` розраховується за формулою власної часткової індуктивності прямокутного контуру:

```text
ΔL ≈ (μ₀ · s / 2π) · [ ln(2s / r_eff) - 0.75 ]
```

де `r_eff = 0.2235 · (w + t)` — ефективний радіус зворотного каналу на краю розрізу, а `μ₀ = 4π · 10⁻⁷` Гн/м.

При типовому обході `s = 12` мм додаткова індуктивність `ΔL` складає від 10 до 18 нГн. При комутації струму 50 мА за час фронту `t_r = 500` пс (`di/dt = 0.1` А/нс) сплеск напруги на петлі дорівнює:

```text
V_bounce = ΔL · (di/dt) = 15 · 10⁻⁹ · 10⁸ = 1.5 В
```

Для логічного сигналу 3.3 В або 1.8 В сплеск амплітудою 1.5 В призводить до повного спотворення логічного рівня або помилкового спрацьовування тригера.

### 3. Індуктивність переходу між шарами з різною кількістю Return Via

Для сигнального via висотою `h_via` та радіусом `r_via` за відсутності зворотного via струм замикається через випадковий отвір на середній відстані `D_iso` (типово 5–15 мм). Індуктивність петлі переходу становить:

```text
L_via_single ≈ (μ₀ · h_via / 2π) · [ ln(2 · D_iso / r_via) + 0.25 ]
```

Якщо на відстані `S_ret` (типово 0.5–1.0 мм) розміщено `N` симетричних зворотних via до землі, еквівалентна індуктивність переходу зменшується за рахунок паралельного з'єднання та взаємної компенсації полів:

```text
L_via_stitched ≈ (μ₀ · h_via / 2π) · [ ln(S_ret / r_via) / N + (1 / (4 · N)) ]
```

При висоті переходу `h_via = 1.2` мм (перехід між зовнішніми шарами 4-шарової плати):
- Без зворотного via (`D_iso = 10` мм): `L ≈ 1.25` нГн;
- З одним return via (`S_ret = 0.7` мм): `L ≈ 0.38` нГн (зменшення у 3.3 раза);
- З двома return via (`S_ret = 0.7` мм): `L ≈ 0.20` нГн (зменшення у 6.2 раза);
- З чотирма return via (квадро-кільце): `L ≈ 0.11` нГн (зменшення у 11.3 раза).

### 4. Оцінка випромінювання дипольної петлі (EMI)

Напруженість електричного поля випромінювання дипольного контуру в дальній зоні у вільному просторі описується виразом:

```text
E(f) = (μ₀ · π · f² · I · A) / (c · r)
```

Збільшення площі петлі від номінального значення `A_solid` (суцільна площина) до роздутого значення `A_split` (обхід розрізу або відсутність via) призводить до збільшення випромінювання на величину:

```text
ΔEMI_dB = 20 · log10(A_split / A_solid)
```

Роздуття площі петлі у 20 разів еквівалентне зростанню випромінювання завад на `+26` дБ, що перетворює тиху плату на джерело радіозавад, яке гарантовано провалює лабораторний тест на відповідність стандарту CISPR 32 / FCC Part 15 Class B.

## Реалізація аналізатора

Програма приймає геометричні параметри трасування друкованої плати, розраховує всі критичні величини зворотного струму та виводить структурований інженерний звіт.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define PI 3.14159265358979323846
#define MU_0 (4.0 * PI * 1e-7)  // Магнітна стала, Гн/м

typedef struct {
    double trace_w;      // Ширина сигнальної доріжки, мм
    double trace_t;      // Товщина міді, мм (наприклад, 0.035 для 1 oz)
    double trace_len;    // Довжина доріжки, мм
    double diel_h;       // Висота діелектрика до опорного шару, мм
    double diel_er;      // Відносна діелектрична проникність (4.2 для FR-4)
    double sig_i_ma;     // Амплітуда струму сигналу, мА
    double sig_tr_ns;    // Час наростання фронту сигналу, нс
    double slot_detour;  // Довжина обходу розрізу в площині, мм
    double via_h;        // Висота сигнального via, мм
    double via_d;        // Діаметр отвору via, мм
    double via_ret_dist; // Відстань до зворотного return via, мм
    double iso_ret_dist; // Відстань до випадкового via без пари, мм
} pcb_params_t;

typedef struct {
    double f_crossover_khz;
    double l_solid_nh;
    double l_detour_nh;
    double v_bounce_solid_v;
    double v_bounce_detour_v;
    double l_via_iso_nh;
    double l_via_1ret_nh;
    double l_via_2ret_nh;
    double l_via_4ret_nh;
    double emi_increase_db;
} return_path_result_t;

void calculate_return_path(const pcb_params_t *p, return_path_result_t *res) {
    // 1. Опір постійному струму (мідь: питомий опір 1.72e-8 Ом*м)
    double rho_cu = 1.72e-8;
    double area_m2 = (p->trace_w * 1e-3) * (p->trace_t * 1e-3);
    double r_dc = rho_cu * (p->trace_len * 1e-3) / area_m2;

    // 2. Індуктивність мікросмужки над суцільною площиною (апроксимація IPC-2141)
    // L ≈ 2e-7 * len * ln(5.98 * h / (0.8 * w + t))
    double w_eff = 0.8 * p->trace_w + p->trace_t;
    double l_per_meter = (MU_0 / (2.0 * PI)) * log(5.98 * p->diel_h / w_eff);
    if (l_per_meter < 1e-7) l_per_meter = 1e-7;
    double l_solid_h = l_per_meter * (p->trace_len * 1e-3);
    res->l_solid_nh = l_solid_h * 1e9;

    // 3. Частота кросоверу f_c = R / (2*pi*L)
    res->f_crossover_khz = (r_dc / (2.0 * PI * l_solid_h)) / 1e3;

    // 4. Паразитна індуктивність обходу розрізу
    // s - довжина обходу, r_eff - радіус каналу
    double s_m = p->slot_detour * 1e-3;
    double r_eff = 0.2235 * ((p->trace_w + p->trace_t) * 1e-3);
    double delta_l_h = (MU_0 * s_m / (2.0 * PI)) * (log(2.0 * s_m / r_eff) - 0.75);
    if (delta_l_h < 0.0) delta_l_h = 0.0;
    res->l_detour_nh = res->l_solid_nh + (delta_l_h * 1e9);

    // 5. Викид напруги V = L * (di/dt)
    double didt = (p->sig_i_ma * 1e-3) / (p->sig_tr_ns * 1e-9); // А/с
    res->v_bounce_solid_v = l_solid_h * didt;
    res->v_bounce_detour_v = (l_solid_h + delta_l_h) * didt;

    // 6. Індуктивність переходу через via
    double via_h_m = p->via_h * 1e-3;
    double via_r_m = (p->via_d * 0.5) * 1e-3;
    double d_iso_m = p->iso_ret_dist * 1e-3;
    double s_ret_m = p->via_ret_dist * 1e-3;

    // Без return via (ізольований via)
    double l_via_iso = (MU_0 * via_h_m / (2.0 * PI)) * (log(2.0 * d_iso_m / via_r_m) + 0.25);
    res->l_via_iso_nh = l_via_iso * 1e9;

    // З 1 return via
    double l_via_1 = (MU_0 * via_h_m / (2.0 * PI)) * (log(s_ret_m / via_r_m) + 0.25);
    res->l_via_1ret_nh = l_via_1 * 1e9;

    // З 2 return vias
    double l_via_2 = (MU_0 * via_h_m / (2.0 * PI)) * (log(s_ret_m / via_r_m) / 2.0 + 0.125);
    res->l_via_2ret_nh = l_via_2 * 1e9;

    // З 4 return vias (квадро-кільце)
    double l_via_4 = (MU_0 * via_h_m / (2.0 * PI)) * (log(s_ret_m / via_r_m) / 4.0 + 0.0625);
    res->l_via_4ret_nh = l_via_4 * 1e9;

    // 7. Зростання випромінювання EMI
    double a_solid = p->trace_len * p->diel_h;
    double a_split = a_solid + (p->slot_detour * p->slot_detour * 0.25);
    res->emi_increase_db = 20.0 * log10(a_split / a_solid);
}

int main(void) {
    pcb_params_t p = {
        .trace_w = 0.35,
        .trace_t = 0.035,
        .trace_len = 30.0,
        .diel_h = 0.20,
        .diel_er = 4.2,
        .sig_i_ma = 40.0,
        .sig_tr_ns = 0.8,
        .slot_detour = 14.0,
        .via_h = 1.2,
        .via_d = 0.30,
        .via_ret_dist = 0.70,
        .iso_ret_dist = 12.0
    };

    return_path_result_t res;
    calculate_return_path(&p, &res);

    printf("===============================================================\n");
    printf("   АНАЛІЗАТОР ПЕТЛІ ЗВОРОТНОГО СТРУМУ ДРУКОВАНОЇ ПЛАТИ        \n");
    printf("===============================================================\n");
    printf("Вхідні параметри:\n");
    printf("  Доріжка: довжина = %.1f мм, ширина = %.2f мм, висота h = %.2f мм\n",
           p.trace_len, p.trace_w, p.diel_h);
    printf("  Сигнал: струм = %.1f мА, час наростання t_r = %.2f нс (di/dt = %.2f А/нс)\n",
           p.sig_i_ma, p.sig_tr_ns, (p.sig_i_ma * 1e-3) / (p.sig_tr_ns));
    printf("  Розріз: обхід = %.1f мм | Via: висота = %.2f мм, d = %.2f мм\n",
           p.slot_detour, p.via_h, p.via_d);
    printf("---------------------------------------------------------------\n");
    printf("1. РЕЖИМИ ТЕЧІЇ СТРУМУ:\n");
    printf("  Частота кросоверу f_c (R vs L):  %.2f кГц\n", res.f_crossover_khz);
    printf("  (Вище %.0f кГц зворотний струм повністю стягується під доріжку)\n\n",
           res.f_crossover_khz);

    printf("2. ПАРАЗИТНА ІНДУКТИВНІСТЬ ТА ДЗВІН ПРИ РОЗРІЗІ ПЛОЩИНИ:\n");
    printf("  Індуктивність над суцільною площиною:  %6.2f нГн  (V_drop = %5.1f мВ)\n",
           res.l_solid_nh, res.v_bounce_solid_v * 1e3);
    printf("  Індуктивність при обході розрізу:      %6.2f нГн  (V_drop = %5.1f мВ)\n",
           res.l_detour_nh, res.v_bounce_detour_v * 1e3);
    printf("  Зростання випромінювання петлі (EMI):  +%5.1f дБ\n\n",
           res.emi_increase_db);

    printf("3. ІНДУКТИВНІСТЬ ПЕРЕХОДУ МІЖ ШАРАМИ (VIA TRANSITION):\n");
    printf("  Без return via (d_iso = %.1f мм):      %6.2f нГн\n", p.iso_ret_dist, res.l_via_iso_nh);
    printf("  З 1 return via (відстань %.2f мм):     %6.2f нГн  (x%.1f менше)\n",
           p.via_ret_dist, res.l_via_1ret_nh, res.l_via_iso_nh / res.l_via_1ret_nh);
    printf("  З 2 return vias (симетричні):          %6.2f нГн  (x%.1f менше)\n",
           res.l_via_2ret_nh, res.l_via_iso_nh / res.l_via_2ret_nh);
    printf("  З 4 return vias (квадро-кільце):       %6.2f нГн  (x%.1f менше)\n",
           res.l_via_4ret_nh, res.l_via_iso_nh / res.l_via_4ret_nh);
    printf("===============================================================\n");

    return 0;
}
```
```cpp
#include <iostream>
#include <iomanip>
#include <cmath>
#include <numbers>
#include <string_view>

struct PcbGeometry {
    double trace_w_mm{0.35};       // Ширина доріжки
    double trace_t_mm{0.035};      // Товщина фольги (1 oz)
    double trace_len_mm{30.0};     // Довжина доріжки
    double diel_h_mm{0.20};        // Висота діелектрика
    double diel_er{4.2};           // Діелектрична проникність FR-4
    double sig_i_ma{40.0};         // Струм сигналу
    double sig_tr_ns{0.8};         // Час наростання фронту
    double slot_detour_mm{14.0};   // Довжина обходу розрізу
    double via_h_mm{1.2};          // Висота сигнального via
    double via_d_mm{0.30};         // Діаметр via
    double via_ret_dist_mm{0.70};  // Відстань до return via
    double iso_ret_dist_mm{12.0};  // Відстань до випадкового via без пари
};

struct ReturnPathMetrics {
    double f_crossover_khz;
    double l_solid_nh;
    double l_detour_nh;
    double v_bounce_solid_mv;
    double v_bounce_detour_mv;
    double l_via_iso_nh;
    double l_via_1ret_nh;
    double l_via_2ret_nh;
    double l_via_4ret_nh;
    double emi_increase_db;
};

class ReturnPathAnalyzer {
public:
    static constexpr double mu_0 = 4.0 * std::numbers::pi * 1e-7;
    static constexpr double rho_copper = 1.72e-8; // Ом*м

    [[nodiscard]] static ReturnPathMetrics analyze(const PcbGeometry& g) noexcept {
        ReturnPathMetrics m{};

        // Опір постійному струму
        const double area_m2 = (g.trace_w_mm * 1e-3) * (g.trace_t_mm * 1e-3);
        const double r_dc = rho_copper * (g.trace_len_mm * 1e-3) / area_m2;

        // Індуктивність мікросмужки над суцільною площиною
        const double w_eff = 0.8 * g.trace_w_mm + g.trace_t_mm;
        const double l_per_meter = (mu_0 / (2.0 * std::numbers::pi)) * 
                                   std::log(5.98 * g.diel_h_mm / w_eff);
        const double l_solid_h = std::max(l_per_meter, 1e-7) * (g.trace_len_mm * 1e-3);
        m.l_solid_nh = l_solid_h * 1e9;

        // Частота кросоверу f_c = R / (2*pi*L)
        m.f_crossover_khz = (r_dc / (2.0 * std::numbers::pi * l_solid_h)) / 1e3;

        // Індуктивність обходу розрізу
        const double s_m = g.slot_detour_mm * 1e-3;
        const double r_eff = 0.2235 * ((g.trace_w_mm + g.trace_t_mm) * 1e-3);
        const double delta_l_h = std::max(0.0, 
            (mu_0 * s_m / (2.0 * std::numbers::pi)) * (std::log(2.0 * s_m / r_eff) - 0.75));
        m.l_detour_nh = m.l_solid_nh + (delta_l_h * 1e9);

        // Падіння напруги / викид V = L * di/dt
        const double didt = (g.sig_i_ma * 1e-3) / (g.sig_tr_ns * 1e-9);
        m.v_bounce_solid_mv = (l_solid_h * didt) * 1e3;
        m.v_bounce_detour_mv = ((l_solid_h + delta_l_h) * didt) * 1e3;

        // Індуктивність сигнального перехідного отвору
        const double via_h_m = g.via_h_mm * 1e-3;
        const double via_r_m = (g.via_d_mm * 0.5) * 1e-3;
        const double d_iso_m = g.iso_ret_dist_mm * 1e-3;
        const double s_ret_m = g.via_ret_dist_mm * 1e-3;

        m.l_via_iso_nh = ((mu_0 * via_h_m / (2.0 * std::numbers::pi)) * 
                          (std::log(2.0 * d_iso_m / via_r_m) + 0.25)) * 1e9;

        m.l_via_1ret_nh = ((mu_0 * via_h_m / (2.0 * std::numbers::pi)) * 
                           (std::log(s_ret_m / via_r_m) + 0.25)) * 1e9;

        m.l_via_2ret_nh = ((mu_0 * via_h_m / (2.0 * std::numbers::pi)) * 
                           (std::log(s_ret_m / via_r_m) / 2.0 + 0.125)) * 1e9;

        m.l_via_4ret_nh = ((mu_0 * via_h_m / (2.0 * std::numbers::pi)) * 
                           (std::log(s_ret_m / via_r_m) / 4.0 + 0.0625)) * 1e9;

        // Зростання випромінювання петлі EMI (дБ)
        const double a_solid = g.trace_len_mm * g.diel_h_mm;
        const double a_split = a_solid + (g.slot_detour_mm * g.slot_detour_mm * 0.25);
        m.emi_increase_db = 20.0 * std::log10(a_split / a_solid);

        return m;
    }
};

int main() {
    constexpr PcbGeometry geom{};
    const auto res = ReturnPathAnalyzer::analyze(geom);

    std::cout << std::fixed << std::setprecision(2);
    std::cout << "===============================================================\n";
    std::cout << "   АНАЛІЗАТОР ПЕТЛІ ЗВОРОТНОГО СТРУМУ ДРУКОВАНОЇ ПЛАТИ (C++20) \n";
    std::cout << "===============================================================\n";
    std::cout << "1. РЕЖИМИ ТЕЧІЇ СТРУМУ:\n";
    std::cout << "  Частота кросоверу f_c (R vs L):  " << res.f_crossover_khz << " кГц\n\n";

    std::cout << "2. ПАРАЗИТНА ІНДУКТИВНІСТЬ ТА ДЗВІН ПРИ РОЗРІЗІ ПЛОЩИНИ:\n";
    std::cout << "  Індуктивність над суцільною площиною:  " << std::setw(6) << res.l_solid_nh 
              << " нГн  (V_drop = " << std::setw(5) << res.v_bounce_solid_mv << " мВ)\n";
    std::cout << "  Індуктивність при обході розрізу:      " << std::setw(6) << res.l_detour_nh 
              << " нГн  (V_drop = " << std::setw(5) << res.v_bounce_detour_mv << " мВ)\n";
    std::cout << "  Зростання випромінювання петлі (EMI):  +" << res.emi_increase_db << " дБ\n\n";

    std::cout << "3. ІНДУКТИВНІСТЬ ПЕРЕХОДУ МІЖ ШАРАМИ (VIA TRANSITION):\n";
    std::cout << "  Без return via (d_iso = " << geom.iso_ret_dist_mm << " мм):      " 
              << std::setw(6) << res.l_via_iso_nh << " нГн\n";
    std::cout << "  З 1 return via (відстань " << geom.via_ret_dist_mm << " мм):     " 
              << std::setw(6) << res.l_via_1ret_nh << " нГн  (x" 
              << (res.l_via_iso_nh / res.l_via_1ret_nh) << " менше)\n";
    std::cout << "  З 2 return vias (симетричні):          " 
              << std::setw(6) << res.l_via_2ret_nh << " нГн  (x" 
              << (res.l_via_iso_nh / res.l_via_2ret_nh) << " менше)\n";
    std::cout << "  З 4 return vias (квадро-кільце):       " 
              << std::setw(6) << res.l_via_4ret_nh << " нГн  (x" 
              << (res.l_via_iso_nh / res.l_via_4ret_nh) << " менше)\n";
    std::cout << "===============================================================\n";

    return 0;
}
```
:::

## Інженерний аналіз результатів розрахунку

1. **Кросовер `f_c` на практиці**: Для типових геометрій друкованих плат частота переходу становить лише 500–800 кГц. Оскільки навіть повільні цифрові шини (UART, I2C, SPI) комутуються вихідними каскадами мікроконтролерів із часом наростання `t_r ≈ 1–3` нс, їхній спектр містить гармоніки до сотень мегагерц. Отже, **жоден цифровий сигнал не повертається шляхом найменшого опору** — усі вони підпорядковані геометрії найменшої індуктивності.
2. **Ціна розрізу площини**: Обхід розрізу додає понад 15 нГн індуктивності, що збільшує падіння напруги на петлі з 0.3 В до майже 1.5 В. Це прямо пояснює, чому трасування швидкісних ліній над розрізами землі викликає незрозумілі збої та подвійне спрацьовування тригерів.
3. **Ефективність Return Vias**: Додавання навіть одного земляного перехідного отвору поруч із сигнальним знижує індуктивність переходу втричі (з 1.25 нГн до 0.38 нГн), а пара симетричних отворів збиває її у 6 разів, повністю усуваючи паразитний резонансний дзвін.
