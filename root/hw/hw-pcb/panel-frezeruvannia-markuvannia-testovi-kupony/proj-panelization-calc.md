# ⚙️ Розрахунок розкладки панелі та міцності перфорованих перемичок

Автоматизований монтаж друкованих плат на швидкісних конвеєрних лініях вимагає об'єднання окремих плат у технологічні монтажні панелі (англ. *assembly panels / delivery pallets*). Проєктування панелі вимагає одночасного розв'язання двох протилежних інженерних задач: максимізації корисної площі склотекстоліту для зниження собівартості та забезпечення механічної міцності панелі під час проходження крізь трафаретний принтер, установник компонентів і піч оплавлення при збереженні контрольованого, безпечного зусилля руйнування перемичок під час фінальної депанелізації.

Якщо технологічні перемички (англ. *breakaway tabs*) спроєктовано занадто масивними, зусилля їх виламування створює в тілі друкованої плати механічні напруження вигину, що перевищують межу пружності керамічних конденсаторів (MLCC) і призводять до утворення прихованих мікротріщин. Якщо ж перемички зробити занадто слабкими, панель провисає під власною вагою та тиском ракеля, викликаючи дефекти нанесення паяльної пасти або передчасний розпад панелі безпосередньо в конвеєрі печі.

Нижче наведено математичний апарат, фізичні моделі деформацій, інженерний аналіз та повну програмну реалізацію калькулятора розкладки панелі та міцнісного аналізу перфорованих перемичок мовами C99 та C++20.

## Фізичні основи механіки склотекстоліту FR-4 та концентрації напружень

Склотекстоліт FR-4 не є ізотропним однорідним матеріалом. Він являє собою композит, складений із тканого скловолокна (ниток основи та утоку, англ. *warp and weft*) та термореактивної бром-епоксидної полімерної матриці.

### 1. Анізотропія механічних властивостей

Модуль пружності Юнга `E` та межа міцності при згині `sigma_flex` помітно різняться залежно від напрямку розкрою листа:
- Вздовж ниток основи (поздовжній напрямок склотканини): модуль пружності становить `E_warp ≈ 22 000–25 000 МПа`, а межа міцності на згин досягає `sigma_flex ≈ 400–450 МПа`.
- Впоперек ниток (напрямок утоку): модуль дещо нижчий і становить `E_weft ≈ 18 000–20 000 МПа` при межі міцності `sigma_flex ≈ 320–360 МПа`.
- По товщині (вісь Z): поведінку визначає виключно епоксидна смола, тому міцність на відрив шарів становить лише `40–60 МПа`.

Під час нагрівання в печі паяння оплавленням вище температури склування епоксидної смоли `T_g` (яка для стандартного FR-4 становить 130–140 °C, а для високотемпературного High-Tg FR-4 — 170–180 °C), полімерна матриця переходить із твердого склоподібного стану у високоеластичний. Модуль пружності смоли падає на порядок, а загальна жорсткість плати знижується в 5–8 разів. Якщо панель довжиною понад 200 мм має недостатню кількість або надто малу ширину перемичок, під час пікового нагріву (245–260 °C для безсвинцевих сплавів SAC305) вона зазнає незворотного прогину під вагою масивних компонентів (трансформаторів, електролітичних конденсаторів, дроселів).

### 2. Концентрація напружень у перфорованих перемичках (Mouse Bites)

Коли прямокутна перемичка послаблюється рядом круглих отворів свердління, розподіл механічних напружень перестає бути лінійним. За класичною теорією пружності Петерсона (Peterson's Stress Concentration Factors), поблизу бічних кромок круглих отворів лінії механічного потоку напружень стискаються, викликаючи різке локальне зростання напруження.

Теоретичний коефіцієнт концентрації напружень `K_t` визначається співвідношенням діаметра отвору `d_hole` до осьового кроку між отворами `p`:

```
K_t ≈ 3.0 - 3.13 · (d_hole / p) + 3.66 · (d_hole / p)^2 - 1.53 · (d_hole / p)^3
```

При типовому інженерному співвідношенні `d_hole = 0.60 мм` та `p = 1.00 мм` (`d_hole / p = 0.6`):

```
K_t ≈ 3.0 - 3.13 · (0.6) + 3.66 · (0.36) - 1.53 · (0.216) ≈ 2.11
```

Це означає, що при прикладанні згинального моменту пікове напруження на краю отвору в `2.11` раза перевищує номінальне напруження, розраховане для чистого поперечного перерізу. Саме ця концентрація напружень гарантує зародження первинної мікротріщини суворо по лінії центрів отворів перфорації та її лавиноподібне поширення вздовж заданої лінії зламу без викривлення в бік робочої плати.

## Математична модель розрахунку розкладки та міцності перемичок

Розрахунковий алгоритм виконує чотири взаємопов'язані аналітичні кроки:

### 1. Оптимізація матричного розміщення 2D-прямокутників

Для прямокутної плати з розмірами `L_board × W_board`, шириною технологічних рейок `W_rail` (5–10 мм), шириною паза кінцевої фрези `W_route` (зазвичай 2.0 мм або 2.4 мм) та граничними розмірами панелі за вимогами монтажного обладнання `L_panel_max × W_panel_max`, алгоритм оцінює два взаємно перпендикулярні варіанти укладання:

- **Варіант A (Пряма орієнтація 0°):**
```
N_x = floor((L_panel_max - 2 · W_rail + W_route) / (L_board + W_route))
N_y = floor((W_panel_max - 2 · W_rail + W_route) / (W_board + W_route))
N_total = N_x · N_y
L_panel = N_x · L_board + (N_x - 1) · W_route + 2 · W_rail
W_panel = N_y · W_board + (N_y - 1) · W_route + 2 · W_rail
```

- **Варіант B (Розвернута орієнтація 90°):**
```
N_x_rot = floor((L_panel_max - 2 · W_rail + W_route) / (W_board + W_route))
N_y_rot = floor((W_panel_max - 2 · W_rail + W_route) / (L_board + W_route))
N_total_rot = N_x_rot · N_y_rot
L_panel_rot = N_x_rot · W_board + (N_x_rot - 1) · W_route + 2 · W_rail
W_panel_rot = N_y_rot · L_board + (N_y_rot - 1) · W_route + 2 · W_rail
```

Коефіцієнт корисного використання площі склотекстоліту `Eta` обчислюється як:

```
Eta = (N_total · L_board · W_board) / (L_panel · W_panel) · 100%
```

Критерій вибору конфігурації: максимізація `N_total`, а при однаковій кількості плат — максимізація `Eta` та мінімізація площі відходів.

### 2. Геометричні та міцнісні характеристики перемички

Перемичка шириною `W_tab`, перфорована `n` отворами діаметром `d_hole`, має наступні геометричні параметри в перерізі осі перфорацій:

- Сумарна ширина залишку суцільного діелектрика (англ. *net solid width*):
```
W_net = W_tab - n · d_hole
```

- Площа чистого перерізу при зсуві:
```
A_net = W_net · T_pcb
```

- Момент інерції чистого перерізу відносно нейтральної осі вигину:
```
I_net = (W_net · T_pcb^3) / 12
```

- Момент опору чистого перерізу:
```
Z_net = (W_net · T_pcb^2) / 6
```

- Руйнівний згинальний момент перемички:
```
M_break = sigma_flex · Z_net
```

- Сила ручного або інструментального виламування `F_break` при плечі прикладання зусилля `L_lever`:
```
F_break = M_break / L_lever
```

- Гранична зсувна міцність перемички при чистому зрізі (наприклад, у штампових вирубних матрицях):
```
F_shear = tau_shear · A_net
```
де `tau_shear` — межа міцності FR-4 на міжшаровий зсув (типово `65–85 МПа`).

### 3. Розрахунок деформаційного поля та зон відчуження за IPC-9704

Стандарт IPC-9704 (та споріднений JEDEC JESD22-B111) визначає методику тензометричного контролю друкованих плат під час технологічних операцій складання, тестування на голчастих адаптерах ICT та депанелізації.

Механічний вигин краю плати під час злому перемички створює хвилю деформації, амплітуда якої на поверхні плати згасає за експоненційним законом у міру віддалення від точки прикладання навантаження:

```
epsilon(x) = (6 · F_break · L_lever) / (W_tab · T_pcb^2 · E_fr4) · exp(-x / (2 · T_pcb))
```

де:
- `epsilon(x)` — відносна деформація поверхні плати на відстані `x` від осі перемички (безрозмірна величина або мікрострейн `µε`);
- `E_fr4` — модуль пружності Юнга склотекстоліту FR-4 (`22 000 МПа`);
- `T_pcb` — товщина друкованої плати.

Прирівнюючи `epsilon(x)` до гранично допустимої деформації компонента `epsilon_limit`, отримуємо аналітичний вираз для мінімальної безпечної відстані розміщення компонента `d_keepout`:

```
d_keepout = 2 · T_pcb · ln((6 · F_break · L_lever) / (W_tab · T_pcb^2 · E_fr4 · epsilon_limit))
```

Граничні норми відносної деформації `epsilon_limit` згідно з IPC-9704 залежать від фізичних розмірів керамічного тіла компонента та товщини плати:
- **MLCC типорозміру 0402 (1005 Metric):** `epsilon_limit = 1000 µε` (0.10% подовження);
- **MLCC типорозміру 0603 (1608 Metric):** `epsilon_limit = 750 µε` (0.075% подовження);
- **MLCC типорозміру 0805 (2012 Metric):** `epsilon_limit = 500 µε` (0.050% подовження);
- **MLCC типорозміру 1206 (3216 Metric) та більше:** `epsilon_limit = 350 µε` (0.035% подовження);
- **BGA-мікросхеми з малим кроком кульок (Pitch ≤ 0.8 мм):** `epsilon_limit = 300 µε` (для запобігання мікротріщинам у кутових паяльних з'єднаннях та розшаруванню падів під чіпом — *pad cratering*).

Якщо обчислене значення `d_keepout` менше за мінімальний технологічний зазор паяльної маски та міді, приймається базовий технологічний відступ `0.5 мм`.
## Програмна реалізація розрахункового комплексу

Нижче наведено дві паралельні ідіоматичні реалізації інженерного калькулятора мовами C99 та C++20. Обидва модулі містять повний набір структур даних, математичні алгоритми 2D-упаковки, функції обчислення моментів опору, розрахунку концентрації напружень Петерсона, деформаційного аналізу за стандартом IPC-9704 та генерації вичерпного консольного інженерного звіту.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>
#include <math.h>

#define FR4_DEFAULT_FLEX_STRENGTH_MPA  380.0
#define FR4_DEFAULT_YOUNG_MODULUS_MPA 22000.0
#define FR4_DEFAULT_SHEAR_STRENGTH_MPA  75.0

typedef struct {
    double length_mm;
    double width_mm;
    double thickness_mm;
} PcbDimensions;

typedef struct {
    double max_length_mm;
    double max_width_mm;
    double rail_width_mm;
    double route_width_mm;
} PanelConstraints;

typedef struct {
    double tab_width_mm;
    double hole_diameter_mm;
    double hole_pitch_mm;
    int hole_count;
    double inset_mm;
    double lever_arm_mm;
} BreakawayTabConfig;

typedef enum {
    MLCC_0402 = 0,
    MLCC_0603,
    MLCC_0805,
    MLCC_1206,
    BGA_FINE_PITCH
} ComponentSensitivity;

typedef struct {
    int count_x;
    int count_y;
    int total_boards;
    double actual_length_mm;
    double actual_width_mm;
    double utilization_pct;
    bool is_rotated;
} PanelLayoutResult;

typedef struct {
    double solid_width_net_mm;
    double net_area_mm2;
    double section_modulus_mm3;
    double breaking_moment_n_mm;
    double breaking_force_n;
    double shear_force_n;
    double stress_concentration_kt;
    double safe_distance_mlcc0402_mm;
    double safe_distance_mlcc0805_mm;
    double safe_distance_mlcc1206_mm;
} TabMechanicalResult;

static double get_component_strain_limit(ComponentSensitivity comp) {
    switch (comp) {
        case MLCC_0402:       return 1000.0e-6;
        case MLCC_0603:       return 750.0e-6;
        case MLCC_0805:       return 500.0e-6;
        case MLCC_1206:       return 350.0e-6;
        case BGA_FINE_PITCH:  return 300.0e-6;
        default:              return 500.0e-6;
    }
}

static double calculate_peterson_kt(double d_hole, double pitch) {
    if (pitch <= 0.0 || d_hole <= 0.0) return 3.0;
    double ratio = d_hole / pitch;
    if (ratio > 0.9) ratio = 0.9;
    return 3.0 - 3.13 * ratio + 3.66 * (ratio * ratio) - 1.53 * (ratio * ratio * ratio);
}

static PanelLayoutResult optimize_panel_layout(const PcbDimensions* board, const PanelConstraints* panel) {
    PanelLayoutResult best = {0};

    // Варіант 1: Пряма орієнтація (0 deg)
    double avail_l1 = panel->max_length_mm - 2.0 * panel->rail_width_mm + panel->route_width_mm;
    double avail_w1 = panel->max_width_mm  - 2.0 * panel->rail_width_mm + panel->route_width_mm;

    int nx1 = (int)floor(avail_l1 / (board->length_mm + panel->route_width_mm));
    int ny1 = (int)floor(avail_w1 / (board->width_mm  + panel->route_width_mm));
    int total1 = (nx1 > 0 && ny1 > 0) ? (nx1 * ny1) : 0;

    double len1 = (nx1 > 0) ? (nx1 * board->length_mm + (nx1 - 1) * panel->route_width_mm + 2.0 * panel->rail_width_mm) : 0.0;
    double wid1 = (ny1 > 0) ? (ny1 * board->width_mm  + (ny1 - 1) * panel->route_width_mm + 2.0 * panel->rail_width_mm) : 0.0;
    double util1 = (len1 > 0.0 && wid1 > 0.0) ? ((total1 * board->length_mm * board->width_mm) / (len1 * wid1) * 100.0) : 0.0;

    // Варіант 2: Розвернута орієнтація (90 deg)
    int nx2 = (int)floor(avail_l1 / (board->width_mm  + panel->route_width_mm));
    int ny2 = (int)floor(avail_w1 / (board->length_mm + panel->route_width_mm));
    int total2 = (nx2 > 0 && ny2 > 0) ? (nx2 * ny2) : 0;

    double len2 = (nx2 > 0) ? (nx2 * board->width_mm  + (nx2 - 1) * panel->route_width_mm + 2.0 * panel->rail_width_mm) : 0.0;
    double wid2 = (ny2 > 0) ? (ny2 * board->length_mm + (ny2 - 1) * panel->route_width_mm + 2.0 * panel->rail_width_mm) : 0.0;
    double util2 = (len2 > 0.0 && wid2 > 0.0) ? ((total2 * board->length_mm * board->width_mm) / (len2 * wid2) * 100.0) : 0.0;

    if (total2 > total1 || (total2 == total1 && util2 > util1)) {
        best.count_x = nx2;
        best.count_y = ny2;
        best.total_boards = total2;
        best.actual_length_mm = len2;
        best.actual_width_mm = wid2;
        best.utilization_pct = util2;
        best.is_rotated = true;
    } else {
        best.count_x = nx1;
        best.count_y = ny1;
        best.total_boards = total1;
        best.actual_length_mm = len1;
        best.actual_width_mm = wid1;
        best.utilization_pct = util1;
        best.is_rotated = false;
    }

    return best;
}

static double calculate_component_keepout(double f_break, double lever, double tab_w, double thickness, double strain_limit) {
    if (strain_limit <= 0.0 || thickness <= 0.0 || tab_w <= 0.0) return 0.0;
    double nominal_moment = f_break * lever;
    double numerator = 6.0 * nominal_moment;
    double denominator = tab_w * thickness * thickness * FR4_DEFAULT_YOUNG_MODULUS_MPA * strain_limit;

    if (numerator <= denominator) {
        return 0.5; // Мінімальний технологічний зазор
    }

    double ratio = numerator / denominator;
    double d_keepout = 2.0 * thickness * log(ratio);
    return (d_keepout > 0.5) ? d_keepout : 0.5;
}

static TabMechanicalResult analyze_breakaway_tab(const BreakawayTabConfig* tab, double pcb_thickness) {
    TabMechanicalResult res = {0};

    double hole_subtraction = tab->hole_count * tab->hole_diameter_mm;
    res.solid_width_net_mm = tab->tab_width_mm - hole_subtraction;
    if (res.solid_width_net_mm < 0.2) res.solid_width_net_mm = 0.2;

    res.net_area_mm2 = res.solid_width_net_mm * pcb_thickness;
    res.section_modulus_mm3 = (res.solid_width_net_mm * pcb_thickness * pcb_thickness) / 6.0;

    res.breaking_moment_n_mm = FR4_DEFAULT_FLEX_STRENGTH_MPA * res.section_modulus_mm3;
    double lever = (tab->lever_arm_mm > 1.0) ? tab->lever_arm_mm : 15.0;
    res.breaking_force_n = res.breaking_moment_n_mm / lever;
    res.shear_force_n = FR4_DEFAULT_SHEAR_STRENGTH_MPA * res.net_area_mm2;

    res.stress_concentration_kt = calculate_peterson_kt(tab->hole_diameter_mm, tab->hole_pitch_mm);

    res.safe_distance_mlcc0402_mm = calculate_component_keepout(res.breaking_force_n, lever, tab->tab_width_mm, pcb_thickness, get_component_strain_limit(MLCC_0402));
    res.safe_distance_mlcc0805_mm = calculate_component_keepout(res.breaking_force_n, lever, tab->tab_width_mm, pcb_thickness, get_component_strain_limit(MLCC_0805));
    res.safe_distance_mlcc1206_mm = calculate_component_keepout(res.breaking_force_n, lever, tab->tab_width_mm, pcb_thickness, get_component_strain_limit(MLCC_1206));

    return res;
}

static void print_engineering_report(const PcbDimensions* board, const PanelConstraints* panel,
                                     const BreakawayTabConfig* tab, const PanelLayoutResult* layout,
                                     const TabMechanicalResult* mech) {
    printf("================================================================================\n");
    printf("  ЗВІТ ІНЖЕНЕРНОГО РОЗРАХУНКУ ПАНЕЛІ ТА ПЕРЕМИЧОК ДРУКОВАНИХ ПЛАТ\n");
    printf("================================================================================\n\n");

    printf("1. ВИХІДНІ ДАНІ РОБОЧОЇ ПЛАТИ:\n");
    printf("   Габарити плати (L x W):          %.2f x %.2f мм\n", board->length_mm, board->width_mm);
    printf("   Товщина склотекстоліту (T):       %.2f мм\n", board->thickness_mm);
    printf("   Площа одиничної плати:           %.2f мм²\n\n", board->length_mm * board->width_mm);

    printf("2. ПАРАМЕТРИ ТЕХНОЛОГІЧНОЇ ПАНЕЛІ ТА ОБМЕЖЕННЯ:\n");
    printf("   Ліміт габаритів виробника:       %.2f x %.2f мм\n", panel->max_length_mm, panel->max_width_mm);
    printf("   Ширина технологічних рейок:      %.2f мм\n", panel->rail_width_mm);
    printf("   Ширина паза кінцевої фрези:      %.2f мм\n\n", panel->route_width_mm);

    printf("3. РЕЗУЛЬТАТИ ОПТИМІЗАЦІЇ РОЗКЛАДКИ (2D ARRAY PACKING):\n");
    printf("   Орієнтація плат на панелі:       %s\n", layout->is_rotated ? "Розвернуто на 90°" : "Пряма (0°)");
    printf("   Кількість плат у сітці (Nx x Ny):%d x %d шт.\n", layout->count_x, layout->count_y);
    printf("   Сумарний вихід плат з панелі:    %d шт.\n", layout->total_boards);
    printf("   Фактичні розміри панелі:         %.2f x %.2f мм\n", layout->actual_length_mm, layout->actual_width_mm);
    printf("   Корисне використання міді/FR4:   %.2f %%\n\n", layout->utilization_pct);

    printf("4. МЕХАНІЧНІ ХАРАКТЕРИСТИКИ ПЕРЕМИЧКИ (BREAKAWAY TAB / MOUSE BITES):\n");
    printf("   Повна ширина перемички (W_tab):  %.2f мм\n", tab->tab_width_mm);
    printf("   Конфігурація перфорації:         %d отворів Ø%.2f мм (крок %.2f мм)\n",
           tab->hole_count, tab->hole_diameter_mm, tab->hole_pitch_mm);
    printf("   Чиста залишкова ширина (W_net):  %.2f мм\n", mech->solid_width_net_mm);
    printf("   Осьовий момент опору (Z_net):    %.4f мм³\n", mech->section_modulus_mm3);
    printf("   Коефіцієнт концентрації (Kt):    %.2f (за критерієм Петерсона)\n", mech->stress_concentration_kt);
    printf("   Граничний згинальний момент (M): %.2f Н·мм\n", mech->breaking_moment_n_mm);
    printf("   Зусилля руйнування при вигині:   %.2f Н (%.2f кгс) при плечі %.1f мм\n",
           mech->breaking_force_n, mech->breaking_force_n / 9.80665, tab->lever_arm_mm);
    printf("   Граничне зсувне зусилля (Shear): %.2f Н (%.2f кгс)\n\n",
           mech->shear_force_n, mech->shear_force_n / 9.80665);

    printf("5. ЗОНИ ВІДЧУЖЕННЯ ДЛЯ КОМПОНЕНТІВ ЗА IPC-9704 (STRAIN KEEPOUT):\n");
    printf("   MLCC 0402 (ліміт 1000 µε):        d_keepout >= %.2f мм від лінії злому\n", mech->safe_distance_mlcc0402_mm);
    printf("   MLCC 0805 (ліміт 500 µε):         d_keepout >= %.2f мм від лінії злому\n", mech->safe_distance_mlcc0805_mm);
    printf("   MLCC 1206 / BGA (ліміт 350 µε):   d_keepout >= %.2f мм від лінії злому\n", mech->safe_distance_mlcc1206_mm);
    printf("   Рекомендований заглиб отворів:   %.2f мм всередину контуру плати\n", tab->inset_mm);
    printf("================================================================================\n");
}

int main(int argc, char** argv) {
    PcbDimensions board = {
        .length_mm = 65.0,
        .width_mm = 42.0,
        .thickness_mm = 1.60
    };

    PanelConstraints panel = {
        .max_length_mm = 300.0,
        .max_width_mm = 200.0,
        .rail_width_mm = 7.0,
        .route_width_mm = 2.0
    };

    BreakawayTabConfig tab = {
        .tab_width_mm = 4.0,
        .hole_diameter_mm = 0.60,
        .hole_pitch_mm = 1.00,
        .hole_count = 4,
        .inset_mm = 0.15,
        .lever_arm_mm = 15.0
    };

    if (argc >= 3) {
        board.length_mm = atof(argv[1]);
        board.width_mm = atof(argv[2]);
    }
    if (argc >= 4) {
        board.thickness_mm = atof(argv[3]);
    }

    PanelLayoutResult layout = optimize_panel_layout(&board, &panel);
    TabMechanicalResult mech = analyze_breakaway_tab(&tab, board.thickness_mm);

    print_engineering_report(&board, &panel, &tab, &layout, &mech);

    return 0;
}
```
```cpp
#include <iostream>
#include <iomanip>
#include <string_view>
#include <vector>
#include <cmath>
#include <span>
#include <expected>
#include <optional>
#include <numbers>

namespace pcb::panel {

constexpr double DefaultFr4FlexuralStrengthMpa = 380.0;
constexpr double DefaultFr4YoungModulusMpa      = 22000.0;
constexpr double DefaultFr4ShearStrengthMpa     = 75.0;

enum class ComponentClass : uint8_t {
    Mlcc0402,
    Mlcc0603,
    Mlcc0805,
    Mlcc1206,
    BgaFinePitch
};

struct BoardGeometry {
    double length_mm{65.0};
    double width_mm{42.0};
    double thickness_mm{1.60};

    [[nodiscard]] constexpr double area() const noexcept {
        return length_mm * width_mm;
    }
};

struct PanelLimits {
    double max_length_mm{300.0};
    double max_width_mm{200.0};
    double rail_width_mm{7.0};
    double route_slot_width_mm{2.0};
};

struct TabSpecification {
    double tab_width_mm{4.0};
    double hole_diameter_mm{0.60};
    double hole_pitch_mm{1.00};
    int hole_count{4};
    double inset_offset_mm{0.15};
    double lever_arm_mm{15.0};
};

struct LayoutEvaluation {
    int count_x{0};
    int count_y{0};
    int total_boards{0};
    double actual_length_mm{0.0};
    double actual_width_mm{0.0};
    double utilization_percentage{0.0};
    bool is_rotated_90deg{false};
};

struct TabAnalysisResult {
    double net_solid_width_mm{0.0};
    double net_shear_area_mm2{0.0};
    double section_modulus_mm3{0.0};
    double breaking_moment_n_mm{0.0};
    double breaking_force_n{0.0};
    double shear_capacity_n{0.0};
    double stress_concentration_kt{0.0};
    double keepout_mlcc0402_mm{0.0};
    double keepout_mlcc0805_mm{0.0};
    double keepout_mlcc1206_mm{0.0};
};

class PanelizationOptimizer {
public:
    [[nodiscard]] static constexpr double GetStrainLimit(ComponentClass comp) noexcept {
        switch (comp) {
            case ComponentClass::Mlcc0402:      return 1000.0e-6;
            case ComponentClass::Mlcc0603:      return 750.0e-6;
            case ComponentClass::Mlcc0805:      return 500.0e-6;
            case ComponentClass::Mlcc1206:      return 350.0e-6;
            case ComponentClass::BgaFinePitch: return 300.0e-6;
        }
        return 500.0e-6;
    }

    [[nodiscard]] static double CalculatePetersonKt(double d_hole, double pitch) noexcept {
        if (pitch <= 0.0 || d_hole <= 0.0) return 3.0;
        double r = std::min(d_hole / pitch, 0.90);
        return 3.0 - 3.13 * r + 3.66 * (r * r) - 1.53 * (r * r * r);
    }

    [[nodiscard]] static std::expected<LayoutEvaluation, std::string_view> OptimizeLayout(
        const BoardGeometry& board,
        const PanelLimits& panel) noexcept
    {
        if (board.length_mm <= 0.0 || board.width_mm <= 0.0 || board.thickness_mm <= 0.0) {
            return std::unexpected("Некоректні габарити друкованої плати");
        }
        if (panel.max_length_mm <= 2.0 * panel.rail_width_mm || panel.max_width_mm <= 2.0 * panel.rail_width_mm) {
            return std::unexpected("Габарити панелі менші за технологічні рейки");
        }

        double avail_x = panel.max_length_mm - 2.0 * panel.rail_width_mm + panel.route_slot_width_mm;
        double avail_y = panel.max_width_mm  - 2.0 * panel.rail_width_mm + panel.route_slot_width_mm;

        // Пряма конфігурація (0°)
        int nx1 = static_cast<int>(std::floor(avail_x / (board.length_mm + panel.route_slot_width_mm)));
        int ny1 = static_cast<int>(std::floor(avail_y / (board.width_mm  + panel.route_slot_width_mm)));
        int tot1 = (nx1 > 0 && ny1 > 0) ? (nx1 * ny1) : 0;
        double len1 = (nx1 > 0) ? (nx1 * board.length_mm + (nx1 - 1) * panel.route_slot_width_mm + 2.0 * panel.rail_width_mm) : 0.0;
        double wid1 = (ny1 > 0) ? (ny1 * board.width_mm  + (ny1 - 1) * panel.route_slot_width_mm + 2.0 * panel.rail_width_mm) : 0.0;
        double util1 = (len1 > 0.0 && wid1 > 0.0) ? ((tot1 * board.area()) / (len1 * wid1) * 100.0) : 0.0;

        // Розвернута конфігурація (90°)
        int nx2 = static_cast<int>(std::floor(avail_x / (board.width_mm  + panel.route_slot_width_mm)));
        int ny2 = static_cast<int>(std::floor(avail_y / (board.length_mm + panel.route_slot_width_mm)));
        int tot2 = (nx2 > 0 && ny2 > 0) ? (nx2 * ny2) : 0;
        double len2 = (nx2 > 0) ? (nx2 * board.width_mm  + (nx2 - 1) * panel.route_slot_width_mm + 2.0 * panel.rail_width_mm) : 0.0;
        double wid2 = (ny2 > 0) ? (ny2 * board.length_mm + (ny2 - 1) * panel.route_slot_width_mm + 2.0 * panel.rail_width_mm) : 0.0;
        double util2 = (len2 > 0.0 && wid2 > 0.0) ? ((tot2 * board.area()) / (len2 * wid2) * 100.0) : 0.0;

        LayoutEvaluation result;
        if (tot2 > tot1 || (tot2 == tot1 && util2 > util1)) {
            result.count_x = nx2;
            result.count_y = ny2;
            result.total_boards = tot2;
            result.actual_length_mm = len2;
            result.actual_width_mm = wid2;
            result.utilization_percentage = util2;
            result.is_rotated_90deg = true;
        } else {
            result.count_x = nx1;
            result.count_y = ny1;
            result.total_boards = tot1;
            result.actual_length_mm = len1;
            result.actual_width_mm = wid1;
            result.utilization_percentage = util1;
            result.is_rotated_90deg = false;
        }

        if (result.total_boards == 0) {
            return std::unexpected("Плата не вміщується на панель із заданими рейками та пазами");
        }

        return result;
    }

    [[nodiscard]] static TabAnalysisResult AnalyzeTab(
        const TabSpecification& tab,
        double pcb_thickness_mm) noexcept
    {
        TabAnalysisResult res;
        double holes_total_width = tab.hole_count * tab.hole_diameter_mm;
        res.net_solid_width_mm = std::max(0.20, tab.tab_width_mm - holes_total_width);
        res.net_shear_area_mm2 = res.net_solid_width_mm * pcb_thickness_mm;
        res.section_modulus_mm3 = (res.net_solid_width_mm * pcb_thickness_mm * pcb_thickness_mm) / 6.0;

        res.breaking_moment_n_mm = DefaultFr4FlexuralStrengthMpa * res.section_modulus_mm3;
        double lever = std::max(1.0, tab.lever_arm_mm);
        res.breaking_force_n = res.breaking_moment_n_mm / lever;
        res.shear_capacity_n = DefaultFr4ShearStrengthMpa * res.net_shear_area_mm2;

        res.stress_concentration_kt = CalculatePetersonKt(tab.hole_diameter_mm, tab.hole_pitch_mm);

        res.keepout_mlcc0402_mm = ComputeKeepoutDistance(res.breaking_force_n, lever, tab.tab_width_mm, pcb_thickness_mm, GetStrainLimit(ComponentClass::Mlcc0402));
        res.keepout_mlcc0805_mm = ComputeKeepoutDistance(res.breaking_force_n, lever, tab.tab_width_mm, pcb_thickness_mm, GetStrainLimit(ComponentClass::Mlcc0805));
        res.keepout_mlcc1206_mm = ComputeKeepoutDistance(res.breaking_force_n, lever, tab.tab_width_mm, pcb_thickness_mm, GetStrainLimit(ComponentClass::Mlcc1206));

        return res;
    }

private:
    [[nodiscard]] static double ComputeKeepoutDistance(
        double force_n, double lever_arm_mm, double tab_w_mm, double thickness_mm, double limit_strain) noexcept
    {
        if (limit_strain <= 0.0 || thickness_mm <= 0.0 || tab_w_mm <= 0.0) return 0.50;
        double num = 6.0 * force_n * lever_arm_mm;
        double den = tab_w_mm * thickness_mm * thickness_mm * DefaultFr4YoungModulusMpa * limit_strain;
        if (num <= den) return 0.50;
        double d = 2.0 * thickness_mm * std::log(num / den);
        return std::max(0.50, d);
    }
};

void PrintReport(const BoardGeometry& board, const PanelLimits& panel,
                 const TabSpecification& tab, const LayoutEvaluation& layout,
                 const TabAnalysisResult& mech)
{
    std::cout << "================================================================================\n"
              << "  C++20 ІНЖЕНЕРНИЙ ЗВІТ РОЗРАХУНКУ ПАНЕЛІ ТА ПЕРЕМИЧОК SMT\n"
              << "================================================================================\n\n"
              << "1. ПАРАМЕТРИ ПЛАТИ ТА ПАНЕЛІ:\n"
              << "   Плата (L x W x T):               " << board.length_mm << " x " << board.width_mm << " x " << board.thickness_mm << " мм\n"
              << "   Ліміт панелі (L_max x W_max):    " << panel.max_length_mm << " x " << panel.max_width_mm << " мм\n"
              << "   Технологічні поля (Rails):       " << panel.rail_width_mm << " мм | Паз фрези: " << panel.route_slot_width_mm << " мм\n\n"
              << "2. ОПТИМАЛЬНА РОЗКЛАДКА (2D ARRAY PACKING):\n"
              << "   Орієнтація:                      " << (layout.is_rotated_90deg ? "Поворот 90°" : "Пряма (0°)") << "\n"
              << "   Матриця компонування (Nx x Ny):  " << layout.count_x << " x " << layout.count_y << " шт.\n"
              << "   Вихід плат з однієї панелі:      " << layout.total_boards << " шт.\n"
              << "   Розміри сформованої панелі:      " << layout.actual_length_mm << " x " << layout.actual_width_mm << " мм\n"
              << "   Коефіцієнт використання матеріалу: " << std::fixed << std::setprecision(2) << layout.utilization_percentage << " %\n\n"
              << "3. МІЦНІСНИЙ АНАЛІЗ ПЕРЕМИЧОК (MOUSE BITES BREAKAWAY TAB):\n"
              << "   Ширина перемички (W_tab):        " << tab.tab_width_mm << " мм\n"
              << "   Перфорація:                      " << tab.hole_count << " отворів Ø" << tab.hole_diameter_mm
              << " мм з кроком " << tab.hole_pitch_mm << " мм\n"
              << "   Залишкова ширина суцільної міді: " << mech.net_solid_width_mm << " мм\n"
              << "   Коефіцієнт концентрації (Kt):    " << mech.stress_concentration_kt << "\n"
              << "   Згинальний момент руйнування:    " << mech.breaking_moment_n_mm << " Н·мм\n"
              << "   Зусилля виламування (Force):     " << mech.breaking_force_n << " Н ("
              << (mech.breaking_force_n / 9.80665) << " кгс) при плечі " << tab.lever_arm_mm << " мм\n"
              << "   Зусилля зсуву (Shear):           " << mech.shear_capacity_n << " Н\n\n"
              << "4. ЗОНИ ЗАБОРОНИ КОМПОНЕНТІВ ЗА IPC-9704:\n"
              << "   Keepout для MLCC 0402 (1000 µε):  d >= " << mech.keepout_mlcc0402_mm << " мм\n"
              << "   Keepout для MLCC 0805 (500 µε):   d >= " << mech.keepout_mlcc0805_mm << " мм\n"
              << "   Keepout для MLCC 1206 (350 µε):   d >= " << mech.keepout_mlcc1206_mm << " мм\n"
              << "   Рекомендований відступ отворів:  " << tab.inset_offset_mm << " мм (Inset всередину контуру)\n"
              << "================================================================================\n";
}

} // namespace pcb::panel

int main(int argc, char** argv) {
    using namespace pcb::panel;

    BoardGeometry board{.length_mm = 65.0, .width_mm = 42.0, .thickness_mm = 1.60};
    PanelLimits panel{.max_length_mm = 300.0, .max_width_mm = 200.0, .rail_width_mm = 7.0, .route_slot_width_mm = 2.0};
    TabSpecification tab{.tab_width_mm = 4.0, .hole_diameter_mm = 0.60, .hole_pitch_mm = 1.00, .hole_count = 4, .inset_offset_mm = 0.15, .lever_arm_mm = 15.0};

    if (argc >= 3) {
        board.length_mm = std::stod(argv[1]);
        board.width_mm = std::stod(argv[2]);
    }
    if (argc >= 4) {
        board.thickness_mm = std::stod(argv[3]);
    }

    auto layout_res = PanelizationOptimizer::OptimizeLayout(board, panel);
    if (!layout_res) {
        std::cerr << "Помилка панелізації: " << layout_res.error() << "\n";
        return 1;
    }

    TabAnalysisResult mech_res = PanelizationOptimizer::AnalyzeTab(tab, board.thickness_mm);

    PrintReport(board, panel, tab, *layout_res, mech_res);

    return 0;
}
```
:::
## Інженерний аналіз технологічних пасток та крайових випадків

Практичний досвід серійного виробництва електронних модулів свідчить, що більшість дефектів, пов'язаних із панелізацією, виникають не через помилки схемотехніки, а через неврахування механіки та термодинаміки на стику технологічних операцій. Нижче детально розібрано п'ять головних технологічних пасток та методи їх запобігання.

### 1. Критичне співвідношення кроку та діаметра отворів перфорації

Геометрія перфорації визначає траєкторію зародження та поширення тріщини:
- **Надто великий крок (`p > 2.0 · d_hole`):** Якщо для отворів діаметром `d_hole = 0.6 мм` розробник встановлює крок `p = 1.5 мм`, ширина суцільного містка між отворами становить `0.9 мм`. При виламуванні напруження розриву між отворами виявляється вищим за міжшарову міцність зв'язку епоксидної смоли зі скловолокном. Злам відхиляється від лінії перфорацій і йде по діагоналі в глибину плати, викликаючи виривання мідних провідників і діелектрика (англ. *tear-out / substrate cratering*).
- **Надто малий крок (`p < 1.3 · d_hole`):** При кроці `0.75 мм` залишок матеріалу становить лише `0.15 мм`. Така перемичка ламається ще під час транспортування на конвеєрі або під дією термічних напружень у печі reflow.
- **Оптимальний діапазон:** `p = (1.4...1.7) · d_hole`. Для стандартного свердла `0.60 мм` крок повинен складати `0.90–1.00 мм`, що залишає суцільний місток `0.30–0.40 мм`.

### 2. Заглиблення отворів перфорації (Hole Inset)

Коли отвори перфорації свердляться точно по теоретичній лінії контуру плати, після руйнування перемички на грані залишаються виступаючі шорсткі фрагменти склотекстоліту («вусики» або задирки, англ. *mouse bite nubs*) заввишки `0.2–0.4 мм`.

Якщо пристрій монтується в щільний металевий корпус або вставляється у пластикові напрямні пази шасі, ці виступи не дозволяють платі сісти на посадкове місце. Монтажники змушені вручну спилювати кожен виступ напилком, що генерує електропровідний пил склотекстоліту та різко підвищує трудомісткість.

Зсув лінії центрів перфорацій на `0.15–0.20 мм` всередину контуру робочої плати формує невелику напівкруглу заглибину (англ. *recess*). Усі залишки зламаного матеріалу лишаються всередині цієї заглибини, а зовнішній габарит плати залишається ідеально гладким без додаткової механічної обробки.

### 3. Термічний прогин панелі (Panel Sag) у печі оплавлення

Під час безсвинцевого паяння панель перебуває в зоні пікового нагріву за температури 245–260 °C протягом 40–90 секунд. Оскільки температура істотно перевищує температуру склування смоли `T_g` (130–150 °C), модуль Юнга FR-4 падає майже на порядок.

Якщо ширина панелі між підтримувальними конвеєрними ланцюгами перевищує 180–200 мм, центральна зона прогинається вниз під дією сили тяжіння на 2.0–6.0 мм. Наслідки прогину:
1. **Зміщення фокусної площини:** Конвекційне прогрівання стає нерівномірним, виникає градієнт температур між краєм та центром панелі до 15–20 °C.
2. **Стікання розплавленого припою:** На кутових та центральних виводах мікросхем QFP і рознімів припій стікає в бік нахилу, викликаючи короткі замикання (паяльні містки) з одного боку та сухі ненадійні пайки з іншого.
3. **Захисні заходи:** Додавання центральних поздовжніх технологічних рейок жорсткості, використання технологічних супутників (палет із композиту Durostone/RocTool) або підтримувальних струн і титанових пальців у конвеєрі печі.

### 4. Орієнтація та розташування керамічних конденсаторів (MLCC)

Керамічний діелектрик на основі титанату барію BaTiO₃ (класи X7R, X5R, Y5V) має виражені п'єзоелектричні властивості та надзвичайно крихку структуру. Його межа міцності на стиск становить понад 800 МПа, проте межа міцності на розтяг не перевищує 50–80 МПа.

Під час згинання плати поблизу лінії депанелізації:
- **Перпендикулярна орієнтація:** Поздовжня вісь конденсатора перпендикулярна до лінії злому. Механічний вигин передається крізь паяльні галтелі безпосередньо на керамічне тіло. Нижня грань компонента зазнає максимальних розтягувальних напружень. Мікротріщина зароджується під кутом 45° від внутрішнього краю металізованого виводу вглиб діелектрика. Цей дефект має прихований характер: на вихідному контролі плата повністю працездатна, проте через 2–6 тижнів експлуатації під впливом вологи та прикладеної напруги відбувається металізація тріщини і глухе коротке замикання шини живлення з тепловим руйнуванням приладу.
- **Паралельна орієнтація:** Поздовжня вісь конденсатора розташована паралельно лінії злому. Обидва виводи перебувають на одній ізолінії деформаційного поля, тому згинальний момент уздовж корпусу відсутній. Напруження в кераміці зменшуються в 3–5 разів.
- **Використання конденсаторів із м'якими виводами (Soft Termination / Flexiterm):** Конденсатори з проміжним шаром струмопровідної епоксидної смоли з наповнювачем зі срібла між керамікою та нікель-олов'яним покриттям витримують вигин плати до 5.0 мм (проти 1.0–2.0 мм для стандартних MLCC).

### 5. Заборона міді (Copper Keepout) у зоні перемички

Під час механічного злому перфорації шари скловолокна зазнають значних локальних зсувних деформацій. Якщо сигнальні доріжки або внутрішні мідні полігони живлення підходять до отворів перфорації ближче ніж на `0.50 мм`:
1. Мідна фольга відшаровується від епоксидної смоли (англ. *delamination*), створюючи капілярну мікропорожнину, крізь яку вглиб плати проникає атмосферна волога та флюс.
2. Фрагменти міді зрізаються по лінії зламу, утворюючи тонкі металеві задирки (англ. *copper burrs*), які викликають міжшарові короткі замикання між зовнішнім сигнальним шаром та внутрішнім шаром землі GND.
3. Правило проектування: повне очищення від міді всіх шарів на відстані не менше `0.50 мм` (а для високовольтних кіл — не менше `1.50 мм`) від краю отворів перфорації.

### 6. Порівняння методів депанелізації та інструментальні деформації

Вибір інструменту для розділення панелі безпосередньо визначає фактичний рівень деформацій плати:
- **Ручне виламування руками (Manual snapping):** Найбільш небезпечний метод. Залежно від зусилля оператора, пікова деформація сягає `1500–3000 µε`, що гарантовано пошкоджує MLCC конденсатори типорозмірів 0805 та 1206, розташовані ближче ніж 5 мм до краю.
- **Ручні кусачки для перемичок (Nibbler / Tab cutters):** Спеціальний інструмент із тонким лезом, що зрізає перемичку за два зустрічні рухи. Деформація знижується до `400–600 µε`.
- **Дискові ножі для V-cut (Pizza-cutter depaneler):** Пара дискових ножів, що котяться по V-подібному пазу. Забезпечують плавне розділення з піковою деформацією `300–500 µε`.
- **Автоматичний фрезерний депанелізатор (Router depaneler):** Високошвидкісний шпиндель (40 000–60 000 об/хв) із твердосплавною фрезою діаметром 1.5–2.0 мм та нижнім вакуумним відсмоктуванням пилу. Перемички перерізаються без створення згинального моменту на платі. Рівень деформації не перевищує `50–120 µε`, що робить цей метод еталоном для відповідальних аерокосмічних та автомобільних виробів (Class 3 за IPC-A-610).
### 7. Тензометричне калібрування за стандартом IPC-JEDEC-9704

Для валідації міцності панелі та підтвердження безпечності розрахованих перемичок на серійних лініях застосовують тензометричні випробування (Strain Gage Testing). На зразок панелі в зонах найвищого механічного ризику (біля перемичок, кутових виводів BGA-процесорів та масивних керамічних конденсаторів) наклеюють триелементні тензометричні розетки (0°/45°/90° Rectangular Rosettes).

Під час депанелізації вимірювальна система фіксує динамічну зміну опору трьох каналів із частотою дискретизації `≥ 10–50 кГц`. Головні деформації розтягу `epsilon_1` та стиску `epsilon_2` обчислюються за співвідношеннями кола Мора:

```
epsilon_1,2 = (epsilon_0 + epsilon_90) / 2 ± (1 / sqrt(2)) · sqrt((epsilon_0 - epsilon_45)^2 + (epsilon_45 - epsilon_90)^2)
```

Максимальна швидкість наростання деформації (Strain Rate `d(epsilon)/dt`) критично впливає на межу руйнування кераміки:
- При повільному вигині (`d(epsilon)/dt < 1000 µε/с`) допустима деформація для MLCC 0805 становить до `700 µε`.
- При ударному динамічному зламі (`d(epsilon)/dt > 100 000 µε/с`, типовому для ручного обламування руками) межа допустимої деформації падає до `250–300 µε`.

За результатами тензометричного аудиту будується карта деформацій технологічного процесу (Strain Map), на якій позначаються критичні зони, де вимагається зміна геометрії перемичок або перехід на автоматичне фрезерування.

### 8. Розрахунок кількості перемичок та стійкості до вібрацій установника SMD

Сучасні автоматичні установники компонентів (Pick & Place) переміщують портали з монтажними головками з лінійним прискоренням до `3G–5G` та швидкістю до 50 000–100 000 компонентів на годину. Динамічні удари під час позиціонування та встановлення масивних компонентів викликають високочастотні вібрації незакріплених країв друкованої плати.

Якщо відстань між сусідніми перемичками вздовж краю плати перевищує `100 мм` для склотекстоліту завтовшки 1.6 мм (або понад `60 мм` для тонких плат завтовшки 0.8–1.0 мм), власна резонансна частота плати потрапляє в діапазон робочих частот приводів установника (50–200 Гц). Плата починає вібрувати з амплітудою до 0.5–1.0 мм. Це призводить до скидання та зміщення дрібних компонентів типорозмірів 0201/0402, щойно встановлених на паяльну пасту, ще до їх потрапляння в піч.

Інженерне правило розстановки перемичок:
1. Відстань між сусідніми перемичками вздовж прямого контуру плати не повинна перевищувати `60–80 мм`.
2. Обов'язкове встановлення перемичок на відстані `10–15 мм` від кожного кута плати для фіксації кутових ступенів вільності.
3. Додаткова перемичка встановлюється безпосередньо навпроти важких компонентів масою понад 5 грамів (дроселів живлення, великих електролітів, важких екрануючих кришок).
### 9. Інтеграція результатів розрахунку у виробничу документацію (CAM EQ)

Отримані значення оптимальної сітки, зусилля виламування та зон відчуження рекомендується включати безпосередньо у складальне креслення друкованої плати (Assembly Drawing) та супровідну записку Fab/Assembly Notes. Зокрема, у примітках зазначають:
- Вимогу збереження заглиблення отворів `Inset ≥ 0.15 мм` при підготовці CAM-даних фабрикою;
- Заборону автоматичного збільшення діаметра свердел перфорацій понад `0.80 мм`;
- Вказівку щодо використання механізованих кусачок або фрезерного депанелізатора для виробів із компонентами типорозмірів 0402 та BGA;
- Гранично допустимий прогин зібраної панелі під час вихідного контролю за стандартом IPC-A-610 (`Bow and Twist ≤ 0.75%` для SMD-монтажу).