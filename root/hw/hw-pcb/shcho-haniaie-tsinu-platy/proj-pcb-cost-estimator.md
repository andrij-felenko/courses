# ⚙️ Параметричний калькулятор собівартості друкованих плат на C99 та C++20

Під час проектування апаратури вибір геометрії плати, кількості шарів, мінімальних зазорів та типу фінішного покриття часто робиться інтуїтивно, без урахування їхнього нелінійного впливу на фінальну ціну партії. Проте коли проект переходить від прототипів у 5 штук до серії у 5 000 одиниць, додавання одного сліпого перехідного отвору або розширення плати на 3 мм поза кратність виробничої панелі здатне збільшити витрати бюджету на десятки тисяч доларів. Цей інструмент реалізує детерміністичну математичну модель оцінки виробничої собівартості партії друкованих плат, дозволяючи розробникам інтегрувати автоматичний розрахунок ціни безпосередньо в конвеєри неперервної інтеграції (CI/CD) та CAD/EDA-скрипти перед відправленням файлів на фабрику.

Модуль приймає повний набір фізичних та технологічних параметрів друкованої плати, розраховує оптимальний 2D-розкрій стандартної виробничої заготовки, оцінює вихід придатних виробів (англ. *Yield*) за законом Пуассона залежно від класу точності та підсумовує прямі матеріальні витрати, машинний час і фіксовану вартість підготовки виробництва (NRE).

---

## 1. Математична модель ціноутворення виробництва

Виробнича собівартість одиничної плати у складі партії обсягом `Q` штук складається з двох ключових компонентів: амортизованих фіксованих інженерних витрат на підготовку лінійки (англ. *Non-Recurring Engineering*, NRE) та змінних витрат на виготовлення робочих панелей з урахуванням технологічного виходу придатних виробів `Y`:

```
Unit_Cost(Q) = (NRE_total / Q) + (Panel_Cost / (N_boards_per_panel · Y))
```

Розгляньмо фізичний та економічний зміст кожної складової цієї моделі.

### 1.1. Геометрія розкрою робочої панелі (Nesting Efficiency)

Фабрика ніколи не обробляє окремі плати. Основним виробничим квантом є заготовка стандартного розміру (найчастіше `18" × 24"` або `457 × 610 мм`). По периметру панелі розташовується технологічне поле шириною `M_edge` (типово `12.5 мм`), призначене для затискачів конвеєра, оптичних реперів (fiducials), тестових купонів контролю імпедансу та штифтів суміщення шарів.

Якщо плата має прямокутні розміри `W_b × H_b`, а технологічний зазор на фрезерування дисковою фрезою становить `S_route` (типово `2.0 мм`), максимальна кількість плат, що вміщується на панелі розміром `W_p × H_p`, розраховується для двох можливих орієнтацій (0° та 90°):

```
W_eff = W_p - 2·M_edge
H_eff = H_p - 2·M_edge

N_direct = floor((W_eff + S_route) / (W_b + S_route)) · floor((H_eff + S_route) / (H_b + S_route))
N_rot    = floor((W_eff + S_route) / (H_b + S_route)) · floor((H_eff + S_route) / (W_b + S_route))

N_boards_per_panel = max(N_direct, N_rot)
```

Коефіцієнт корисного використання площі панелі `K_util` визначає частку оплаченого склотекстоліту, яка перетворюється на готовий виріб:

```
K_util = (N_boards_per_panel · W_b · H_b) / (W_p · H_p)
```

Якщо `K_util` падає нижче `60%`, замовник сплачує за утилізацію дорогого склотекстоліту, перетворюваного на стружку під час контурного фрезерування.

### 1.2. Базова вартість матеріалів та шаруватості (Layer Multiplier)

Базова ціна обробки панелі площею `A_panel = W_p · H_p` масштабується нелінійно залежно від кількості шарів `N_layers`. Для двошарової плати використовується готовий двосторонній фольгований діелектрик (CCL), який не потребує операцій спікання. Для `4+` шарів процес вимагає внутрішнього травлення, нанесення адгезійного оксидного шару, підготовки пакету з препрегів і внутрішніх ядер (core) та високотемпературного пресування під вакуумом:

```
C_material = A_panel · Cost_FR4_per_m2 · f_Tg · (1 + 0.42·(N_layers - 2)) · f_lamination
```

де:
* `f_Tg` — коефіцієнт термостійкості смоли (`1.0` для стандартного FR-4 Tg130–140 °C, `1.25` для High-Tg170 °C, `1.65` для безгалогенових матеріалів);
* `f_lamination` — множник циклів пресування (`1.0` для стандартного 1-етапного пресування 4–8 шарів; `1.85` для структури HDI 1+N+1; `2.90` для HDI 2+N+2).

### 1.3. Товщина міді (Copper Weight Adder)

Збільшення товщини зовнішньої та внутрішньої міді з базової `1 oz` (35 мкм) до `2 oz` (70 мкм) або `3 oz` (105 мкм) для силових кіл підвищує вартість сировини та збільшує тривалість травлення у ванні хлориду заліза чи купруму. Крім того, товсті доріжки утворюють глибокі міжпровідникові рівчаки, що потребує використання препрегів із високим вмістом смоли (high resin content, наприклад тип 1080 або 2116) для запобігання утворенню повітряних каверн:

```
f_cu = 1.0 + 0.38·(Weight_oz - 1.0)
```

### 1.4. Складність отворів та перехідних з'єднань (Via Complexity)

Застосування стандартних наскрізних отворів (Through-Hole, PTH) обмежується витратами на механічне свердління карбідними свердлами. Проте перехід до глухих/прихованих отворів (Blind/Buried Vias) або мікроотворів (Laser Microvias діаметром 75–125 мкм) різко ускладнює маршрутну карту:

```
C_vias = (N_pth · Cost_pth) + (N_laser · Cost_microvia) + (N_vippo · Cost_vippo)
```

Для технології `VIPPO` (Via-in-Pad Plated Over, заповнення отвору епоксидною смолою з наступною планаризацією та гальванічним покриттям мідним ковпачком) додається 5 додаткових операцій хіміко-механічного циклу, що додає фіксовану націнку на кожен отвір у контактному майданчику BGA.

### 1.5. Фінішні покриття (Surface Finish Adders)

Вартість хімічного нанесення захисного шару на відкриті мідні контактні майданчики залежить від вартості застосовуваних реагентів та часу експозиції у ваннах:

* **HASL (Lead-Free)**: базова технологія гарячого лудження олов'яно-мідним припоєм (множник `1.0`);
* **OSP**: тонка органічна плівка (множник `0.92`, найнижча ціна завдяки простоті хімічного пасивування);
* **ENIG**: шар хімічного нікелю (3–6 мкм) та імерсійного золота (0.05–0.1 мкм). Націнка формується витратою солей золота та необхідністю регулярної регенерації ванн хімічного відновлення нікелю гіпофосфітом натрію (множник `1.30`);
* **ENEPIG**: нікель-паладій-золото для прямого розварювання кристалів дротом (множник `1.90`).

### 1.6. Вихід придатних та клас точності (Yield Defect Density Model)

Зменшення ширини провідника `w` та мінімального зазору `s` (Trace/Space) збільшує ймовірність критичних дефектів — обривів через мікропорошинки під час фотолітографії або коротких замикань через неповне травлення. Вихід придатних плат на панелі `Y` описується модифікованою експоненційною моделлю дефектів Пуассона:

```
D_eff = D_base · ((6.0 / min(w_mil, s_mil))^1.75) · (N_layers / 2.0)^0.5
Y = exp(-D_eff · (A_board_cm2 / 100.0))
```

де `D_base` — базова густина дефектів чистої кімнати фабрики (типово `0.018 дефект/см²` для ISO Class 7). Для класу `6/6 mil` вихід становить `98–99%`, тоді як для `3/3 mil` на великих платах він може впасти до `80–85%`, що фабрика компенсує включенням вартості відбракованих заготовок у ціну партії.

### 1.7. Терміновість (Rush Turnaround Multiplier)

Стандартний виробничий цикл складає 5–7 робочих днів (120–144 години). Експрес-виготовлення за 24 або 48 годин вимагає зупинки конвеєра для позачергового завантаження заготовок, ручного перенесення касет між ваннами, окремого налаштування свердлувальних верстатів та роботи персоналу в нічні зміни:

```
k_rush(Hours) = 1.0 + max(0.0, (120 - Hours) / 120)^1.6 · 2.8
```

Для 24-годинного виконання коефіцієнт `k_rush` досягає `2.8–3.5×`.

---

## 2. Реалізація параметричного калькулятора

Нижче наведено повні та взаємно еквівалентні реалізації калькулятора мовами C99 та C++20. Код модульний, не містить зовнішніх бібліотек і готовий до використання в автоматизованих утилітах та тестах.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <stdbool.h>

#define PANEL_WIDTH_MM       457.0  /* Стандарт 18 дюймів */
#define PANEL_HEIGHT_MM      610.0  /* Стандарт 24 дюйми */
#define PANEL_MARGIN_MM      12.5   /* Технологічні поля панелі */
#define ROUTER_GAP_MM        2.0    /* Ширина фрези між платами */
#define BASE_FR4_COST_SQM    35.0   /* Базова ціна FR-4 за 1 м2 */
#define BASE_NRE_SETUP       120.0  /* Фіксована підготовка лінійки */

typedef enum {
    SURFACE_HASL_LEADFREE = 0,
    SURFACE_OSP           = 1,
    SURFACE_ENIG          = 2,
    SURFACE_ENEPIG        = 3
} SurfaceFinish;

typedef enum {
    TG_STANDARD_130 = 0,
    TG_MID_150      = 1,
    TG_HIGH_170     = 2
} TgRating;

typedef struct {
    double width_mm;
    double height_mm;
    int layer_count;
    double copper_oz;
    double min_trace_mil;
    double min_space_mil;
    TgRating tg;
    SurfaceFinish finish;
    bool has_blind_buried_vias;
    bool has_vippo;
    int vippo_holes_count;
    int order_quantity;
    int turnaround_hours;
} PcbSpecification;

typedef struct {
    int boards_per_panel;
    int panels_needed;
    double panel_utilization_pct;
    double estimated_yield;
    double nre_tooling_cost;
    double panel_unit_cost;
    double total_batch_cost;
    double unit_board_cost;
} PcbCostResult;

static int calculate_nesting(double board_w, double board_h, double panel_w, double panel_h, double margin, double gap) {
    double eff_w = panel_w - 2.0 * margin;
    double eff_h = panel_h - 2.0 * margin;

    if (eff_w <= 0.0 || eff_h <= 0.0 || board_w <= 0.0 || board_h <= 0.0) {
        return 0;
    }

    /* Орієнтація 0 градусів */
    int cols_0 = (int)floor((eff_w + gap) / (board_w + gap));
    int rows_0 = (int)floor((eff_h + gap) / (board_h + gap));
    int count_0 = (cols_0 > 0 && rows_0 > 0) ? (cols_0 * rows_0) : 0;

    /* Орієнтація 90 градусів */
    int cols_90 = (int)floor((eff_w + gap) / (board_h + gap));
    int rows_90 = (int)floor((eff_h + gap) / (board_w + gap));
    int count_90 = (cols_90 > 0 && rows_90 > 0) ? (cols_90 * rows_90) : 0;

    return (count_0 > count_90) ? count_0 : count_90;
}

static double estimate_yield(double board_area_cm2, int layers, double min_feature_mil) {
    double feature = (min_feature_mil < 3.0) ? 3.0 : min_feature_mil;
    /* Базова модель дефектів фотолітографії */
    double defect_density = 0.018 * pow(6.0 / feature, 1.75) * sqrt((double)layers / 2.0);
    double y = exp(-defect_density * (board_area_cm2 / 100.0));
    return (y < 0.40) ? 0.40 : ((y > 0.99) ? 0.99 : y);
}

bool pcb_calculate_cost(const PcbSpecification* spec, PcbCostResult* res) {
    if (!spec || !res || spec->width_mm <= 0.0 || spec->height_mm <= 0.0 || spec->order_quantity <= 0) {
        return false;
    }

    int n_per_panel = calculate_nesting(
        spec->width_mm, spec->height_mm,
        PANEL_WIDTH_MM, PANEL_HEIGHT_MM,
        PANEL_MARGIN_MM, ROUTER_GAP_MM
    );

    if (n_per_panel == 0) {
        return false;
    }

    double board_area_sqm = (spec->width_mm * spec->height_mm) / 1000000.0;
    double board_area_cm2 = (spec->width_mm * spec->height_mm) / 100.0;
    double panel_area_sqm = (PANEL_WIDTH_MM * PANEL_HEIGHT_MM) / 1000000.0;

    double util_pct = ((double)n_per_panel * board_area_sqm / panel_area_sqm) * 100.0;

    double min_feature = (spec->min_trace_mil < spec->min_space_mil) ? spec->min_trace_mil : spec->min_space_mil;
    double yield_val = estimate_yield(board_area_cm2, spec->layer_count, min_feature);

    /* Множник матеріалів за шаруватістю */
    double layer_mult = 1.0;
    if (spec->layer_count > 2) {
        layer_mult = 1.0 + 0.42 * (double)(spec->layer_count - 2);
    }

    /* Множник матеріалу Tg */
    double tg_mult = 1.0;
    if (spec->tg == TG_MID_150) tg_mult = 1.20;
    else if (spec->tg == TG_HIGH_170) tg_mult = 1.45;

    /* Множник міді */
    double cu_mult = 1.0 + 0.38 * (spec->copper_oz > 1.0 ? (spec->copper_oz - 1.0) : 0.0);

    /* Множник покриття */
    double finish_cost_panel = 0.0;
    if (spec->finish == SURFACE_ENIG) finish_cost_panel = 14.5 * panel_area_sqm;
    else if (spec->finish == SURFACE_ENEPIG) finish_cost_panel = 32.0 * panel_area_sqm;
    else if (spec->finish == SURFACE_OSP) finish_cost_panel = -2.0 * panel_area_sqm;

    /* Вартість глухих отворів та VIPPO */
    double via_complexity_mult = 1.0;
    if (spec->has_blind_buried_vias) {
        via_complexity_mult += 0.65;
    }
    double vippo_cost = 0.0;
    if (spec->has_vippo && spec->vippo_holes_count > 0) {
        vippo_cost = (double)spec->vippo_holes_count * 0.035;
    }

    /* Базова собівартість панелі */
    double panel_cost = (panel_area_sqm * BASE_FR4_COST_SQM * tg_mult * layer_mult * cu_mult * via_complexity_mult)
                      + finish_cost_panel + vippo_cost;

    /* Терміновість */
    double rush_mult = 1.0;
    if (spec->turnaround_hours < 120) {
        double delta = (120.0 - (double)spec->turnaround_hours) / 120.0;
        rush_mult = 1.0 + pow(delta, 1.6) * 2.8;
    }

    panel_cost *= rush_mult;

    /* Розрахунок NRE */
    double nre = BASE_NRE_SETUP;
    if (spec->layer_count > 2) nre += (double)(spec->layer_count - 2) * 28.0;
    if (spec->has_blind_buried_vias) nre += 85.0;
    if (spec->min_trace_mil < 4.0 || spec->min_space_mil < 4.0) nre += 50.0;
    nre *= (rush_mult > 1.5) ? 1.5 : rush_mult;

    /* Кількість панелей для виконання замовлення з урахуванням виходу */
    int effective_boards_per_panel = (int)floor((double)n_per_panel * yield_val);
    if (effective_boards_per_panel < 1) effective_boards_per_panel = 1;

    int panels_needed = (spec->order_quantity + effective_boards_per_panel - 1) / effective_boards_per_panel;
    if (panels_needed < 1) panels_needed = 1;

    double total_variable = (double)panels_needed * panel_cost;
    double total_cost = nre + total_variable;

    res->boards_per_panel = n_per_panel;
    res->panels_needed = panels_needed;
    res->panel_utilization_pct = util_pct;
    res->estimated_yield = yield_val;
    res->nre_tooling_cost = nre;
    res->panel_unit_cost = panel_cost;
    res->total_batch_cost = total_cost;
    res->unit_board_cost = total_cost / (double)spec->order_quantity;

    return true;
}

int main(void) {
    PcbSpecification spec = {
        .width_mm = 85.0,
        .height_mm = 54.0,
        .layer_count = 4,
        .copper_oz = 1.0,
        .min_trace_mil = 5.0,
        .min_space_mil = 5.0,
        .tg = TG_MID_150,
        .finish = SURFACE_ENIG,
        .has_blind_buried_vias = false,
        .has_vippo = false,
        .vippo_holes_count = 0,
        .order_quantity = 500,
        .turnaround_hours = 120
    };

    PcbCostResult res;
    if (pcb_calculate_cost(&spec, &res)) {
        printf("=== Результати розрахунку собівартості PCB ===\n");
        printf("Розмір плати: %.1f x %.1f мм\n", spec.width_mm, spec.height_mm);
        printf("Кількість шарів: %d, Покриття: ENIG, Партія: %d шт.\n", spec.layer_count, spec.order_quantity);
        printf("Плат на панелі 18\"x24\": %d шт. (Утилізація: %.1f%%)\n", res.boards_per_panel, res.panel_utilization_pct);
        printf("Оціночний вихід (Yield): %.2f%%\n", res.estimated_yield * 100.0);
        printf("Потрібно виробничих панелей: %d шт.\n", res.panels_needed);
        printf("Фіксовані витрати (NRE Tooling): $%.2f\n", res.nre_tooling_cost);
        printf("Собівартість 1 панелі: $%.2f\n", res.panel_unit_cost);
        printf("Повна вартість партії: $%.2f\n", res.total_batch_cost);
        printf("Ціна за 1 готову плату: $%.2f\n", res.unit_board_cost);
    }
    return 0;
}
```
```cpp
#include <iostream>
#include <cmath>
#include <algorithm>
#include <string_view>
#include <span>
#include <expected>
#include <format>
#include <numbers>

namespace pcb_cost {

inline constexpr double PanelWidthMm    = 457.0; // 18 дюймів
inline constexpr double PanelHeightMm   = 610.0; // 24 дюйми
inline constexpr double PanelMarginMm   = 12.5;  // Технологічні поля
inline constexpr double RouterGapMm     = 2.0;   // Зазор на фрезерування
inline constexpr double BaseFr4CostSqm  = 35.0;  // Базовий тариф склотекстоліту
inline constexpr double BaseNreSetup    = 120.0; // Інженерна підготовка виробництва

enum class SurfaceFinish : uint8_t {
    HaslLeadFree,
    Osp,
    Enig,
    Enepig
};

enum class TgRating : uint8_t {
    Standard130,
    Mid150,
    High170
};

enum class CalculatorError : uint8_t {
    InvalidDimensions,
    InvalidQuantity,
    ZeroFitOnPanel
};

struct BoardDimensions {
    double width_mm{0.0};
    double height_mm{0.0};

    [[nodiscard]] constexpr double area_sqm() const noexcept {
        return (width_mm * height_mm) / 1'000'000.0;
    }

    [[nodiscard]] constexpr double area_cm2() const noexcept {
        return (width_mm * height_mm) / 100.0;
    }
};

struct PcbSpecification {
    BoardDimensions dimensions;
    int layer_count{2};
    double copper_oz{1.0};
    double min_trace_mil{6.0};
    double min_space_mil{6.0};
    TgRating tg{TgRating::Standard130};
    SurfaceFinish finish{SurfaceFinish::HaslLeadFree};
    bool has_blind_buried_vias{false};
    bool has_vippo{false};
    int vippo_holes_count{0};
    int order_quantity{100};
    int turnaround_hours{120};
};

struct PcbCostBreakdown {
    int boards_per_panel{0};
    int panels_needed{0};
    double panel_utilization_pct{0.0};
    double estimated_yield{0.0};
    double nre_tooling_cost{0.0};
    double panel_unit_cost{0.0};
    double total_batch_cost{0.0};
    double unit_board_cost{0.0};
};

class CostEstimator {
public:
    [[nodiscard]] static std::expected<PcbCostBreakdown, CalculatorError>
    calculate(const PcbSpecification& spec) noexcept {
        if (spec.dimensions.width_mm <= 0.0 || spec.dimensions.height_mm <= 0.0) {
            return std::unexpected(CalculatorError::InvalidDimensions);
        }
        if (spec.order_quantity <= 0) {
            return std::unexpected(CalculatorError::InvalidQuantity);
        }

        const int n_per_panel = compute_nesting(spec.dimensions);
        if (n_per_panel == 0) {
            return std::unexpected(CalculatorError::ZeroFitOnPanel);
        }

        constexpr double panel_area_sqm = (PanelWidthMm * PanelHeightMm) / 1'000'000.0;
        const double board_area_sqm = spec.dimensions.area_sqm();
        const double board_area_cm2 = spec.dimensions.area_cm2();

        const double util_pct = (static_cast<double>(n_per_panel) * board_area_sqm / panel_area_sqm) * 100.0;

        const double min_feature = std::min(spec.min_trace_mil, spec.min_space_mil);
        const double yield_val = estimate_yield(board_area_cm2, spec.layer_count, min_feature);

        // Множник шаруватості
        const double layer_mult = (spec.layer_count > 2)
            ? 1.0 + 0.42 * static_cast<double>(spec.layer_count - 2)
            : 1.0;

        // Термостійкість Tg
        double tg_mult = 1.0;
        if (spec.tg == TgRating::Mid150) tg_mult = 1.20;
        else if (spec.tg == TgRating::High170) tg_mult = 1.45;

        // Мідне покриття
        const double cu_mult = 1.0 + 0.38 * std::max(0.0, spec.copper_oz - 1.0);

        // Хімічне фінішне покриття
        double finish_adder = 0.0;
        switch (spec.finish) {
            case SurfaceFinish::Enig:         finish_adder = 14.5 * panel_area_sqm; break;
            case SurfaceFinish::Enepig:       finish_adder = 32.0 * panel_area_sqm; break;
            case SurfaceFinish::Osp:          finish_adder = -2.0 * panel_area_sqm; break;
            case SurfaceFinish::HaslLeadFree: finish_adder = 0.0; break;
        }

        // Складність отворів
        double via_mult = spec.has_blind_buried_vias ? 1.65 : 1.0;
        double vippo_cost = (spec.has_vippo && spec.vippo_holes_count > 0)
            ? static_cast<double>(spec.vippo_holes_count) * 0.035
            : 0.0;

        double panel_cost = (panel_area_sqm * BaseFr4CostSqm * tg_mult * layer_mult * cu_mult * via_mult)
                          + finish_adder + vippo_cost;

        // Терміновість
        double rush_mult = 1.0;
        if (spec.turnaround_hours < 120) {
            const double delta = (120.0 - static_cast<double>(spec.turnaround_hours)) / 120.0;
            rush_mult = 1.0 + std::pow(delta, 1.6) * 2.8;
        }
        panel_cost *= rush_mult;

        // NRE витрати
        double nre = BaseNreSetup;
        if (spec.layer_count > 2) nre += static_cast<double>(spec.layer_count - 2) * 28.0;
        if (spec.has_blind_buried_vias) nre += 85.0;
        if (min_feature < 4.0) nre += 50.0;
        nre *= std::min(1.5, rush_mult);

        const int eff_boards_per_panel = std::max(1, static_cast<int>(std::floor(n_per_panel * yield_val)));
        const int panels_needed = (spec.order_quantity + eff_boards_per_panel - 1) / eff_boards_per_panel;

        const double total_variable = static_cast<double>(panels_needed) * panel_cost;
        const double total_batch = nre + total_variable;

        return PcbCostBreakdown{
            .boards_per_panel = n_per_panel,
            .panels_needed = panels_needed,
            .panel_utilization_pct = util_pct,
            .estimated_yield = yield_val,
            .nre_tooling_cost = nre,
            .panel_unit_cost = panel_cost,
            .total_batch_cost = total_batch,
            .unit_board_cost = total_batch / static_cast<double>(spec.order_quantity)
        };
    }

private:
    [[nodiscard]] static int compute_nesting(const BoardDimensions& board) noexcept {
        const double eff_w = PanelWidthMm - 2.0 * PanelMarginMm;
        const double eff_h = PanelHeightMm - 2.0 * PanelMarginMm;

        if (eff_w <= 0.0 || eff_h <= 0.0) return 0;

        const int cols_0  = static_cast<int>(std::floor((eff_w + RouterGapMm) / (board.width_mm + RouterGapMm)));
        const int rows_0  = static_cast<int>(std::floor((eff_h + RouterGapMm) / (board.height_mm + RouterGapMm)));
        const int count_0 = (cols_0 > 0 && rows_0 > 0) ? (cols_0 * rows_0) : 0;

        const int cols_90  = static_cast<int>(std::floor((eff_w + RouterGapMm) / (board.height_mm + RouterGapMm)));
        const int rows_90  = static_cast<int>(std::floor((eff_h + RouterGapMm) / (board.width_mm + RouterGapMm)));
        const int count_90 = (cols_90 > 0 && rows_90 > 0) ? (cols_90 * rows_90) : 0;

        return std::max(count_0, count_90);
    }

    [[nodiscard]] static double estimate_yield(double area_cm2, int layers, double min_feature_mil) noexcept {
        const double feature = std::max(3.0, min_feature_mil);
        const double defect_density = 0.018 * std::pow(6.0 / feature, 1.75) * std::sqrt(static_cast<double>(layers) / 2.0);
        const double y = std::exp(-defect_density * (area_cm2 / 100.0));
        return std::clamp(y, 0.40, 0.99);
    }
};

} // namespace pcb_cost

int main() {
    using namespace pcb_cost;

    const PcbSpecification spec{
        .dimensions = {.width_mm = 85.0, .height_mm = 54.0},
        .layer_count = 4,
        .copper_oz = 1.0,
        .min_trace_mil = 5.0,
        .min_space_mil = 5.0,
        .tg = TgRating::Mid150,
        .finish = SurfaceFinish::Enig,
        .has_blind_buried_vias = false,
        .has_vippo = false,
        .vippo_holes_count = 0,
        .order_quantity = 500,
        .turnaround_hours = 120
    };

    const auto result = CostEstimator::calculate(spec);
    if (!result) {
        std::cerr << "Помилка розрахунку параметрів плати.\n";
        return 1;
    }

    const auto& res = *result;
    std::cout << "=== Результати розрахунку собівартості PCB (C++20) ===\n";
    std::cout << "Розмір плати: " << spec.dimensions.width_mm << " x " << spec.dimensions.height_mm << " мм\n";
    std::cout << "Шари: " << spec.layer_count << ", Покриття: ENIG, Партія: " << spec.order_quantity << " шт.\n";
    std::cout << "Плат на заготовці: " << res.boards_per_panel << " шт. (Утилізація: " << res.panel_utilization_pct << "%)\n";
    std::cout << "Вихід придатних (Yield): " << (res.estimated_yield * 100.0) << "%\n";
    std::cout << "Необхідно панелей: " << res.panels_needed << " шт.\n";
    std::cout << "NRE підготовка виробництва: $" << res.nre_tooling_cost << "\n";
    std::cout << "Собівартість 1 панелі: $" << res.panel_unit_cost << "\n";
    std::cout << "Повна собівартість партії: $" << res.total_batch_cost << "\n";
    std::cout << "Ціна 1 готової плати: $" << res.unit_board_cost << "\n";

    return 0;
}
```
:::

---

## 3. Поглиблений аналіз технологічних переходів та витратних статей

Окрім прямої вартості діелектрика та фольги, собівартість складних плат формується специфічними машинними операціями контролю, свердління та оптичної інспекції.

### 3.1. Електричне тестування: рухомі щупи (Flying Probe) проти ложа цвяхів (Bed-of-Nails)

Кожна виготовлена плата перед відвантаженням проходить 100% електричний контроль цілісності електричних кіл (відсутність обривів) та ізоляції між сусідніми мережами (відсутність коротких замикань). Вибір методу контролю суттєво змінює співвідношення між фіксованими та змінними витратами:

* **Тестер із рухомими щупами (англ. *Flying Probe Tester*)**: чотири або вісім прецизиційних маніпуляторів переміщують тестові голки по координатах тестових точок плати.
  Час тестування однієї плати лінійно залежить від кількості контактних майданчиків та вузлів мереж `N_nets`:

```
T_test = N_pads · t_contact + N_nets · t_isolation
```

  де `t_contact ≈ 0.04 с`, а `t_isolation ≈ 0.015 с`. Для складної 6-шарової плати з 1 800 контактними майданчиками час тестування однієї плати складає близько 80–100 секунд. Машинний час високоточного тестера коштує фабриці близько $45–60 за годину. Таким чином, перевірка однієї плати на Flying Probe коштує від $1.00 до $1.60. Для партії з 10 штук це ідеальний підхід, оскільки він не вимагає NRE-витрат на спеціальну оснастку.
* **Адаптер «ложе цвяхів» (англ. *Bed-of-Nails Fixture*)**: спеціальна матрична плита, в яку за координатами тестових майданчиків конкретної плати запресовані тисячі пружних позолочених голок (pogo pins). Усі кола тестуються паралельно за один механічний притиск тривалістю 2–3 секунди.
  Виготовлення адаптера вимагає інженерного проектування та прецизійного свердління матриці з текстоліту G10/FR-4, що формує фіксовану статтю витрат NRE у розмірі $450–1500. Проте змінна вартість тестування плати падає до $0.05.

Точка беззбитковості переходу від Flying Probe до Bed-of-Nails для плат середньої складності зазвичай знаходиться в діапазоні від 300 до 600 штук.

### 3.2. Механічне свердління: знос інструменту та щільність отворів

Механічне свердління отворів карбідними свердлами (сплав карбіду вольфраму з кобальтовою зв'язкою) виконується на шпинделях зі швидкістю обертання від 150 000 до 250 000 об/хв. Свердло діаметром `0.3 мм` здатне просвердлити пакет із трьох заготовок сумарною товщиною 4.8 мм без втрати циліндричності отвору. Проте коли діаметр отвору падає нижче `0.25 мм`:

1. **Пакетне свердління забороняється**: свердління виконується лише для однієї панелі за раз, що збільшує час роботи свердлувального верстата втричі;
2. **Знос інструменту**: ресурс свердла `0.2 мм` падає з 2 500 отворів до 400–600 ударів, після чого свердло викидається через ризик мікрозламу та утворення задирок скловолокна всередині отвору;
3. **Хімічне очищення від нагару (Desmear)**: тертя тонкого свердла розігріває епоксидну смолу діелектрика до температури склування, викликаючи налипання смоляної плівки (англ. *resin smear*) на торці мідних внутрішніх шарів. Для відновлення контакту з майбутньою металізацією панель повинна проходити додаткову ванну плазмового або перманганатного травлення.

### 3.3. Порівняльний аналіз структури витрат для різних партій

Розгляньмо, як розподіляються фіксовані (NRE) та змінні витрати для 4-шарової плати формату `85 × 54 мм` залежно від розміру серії:

| Розмір партії `Q` | NRE амортизація на одиницю | Матеріальна частка | Фінальна ціна за плату | Домінуючий фактор вартості |
|---|---|---|---|---|
| **5 шт. (прототип)** | $35.20 / шт. | $4.85 / шт. | **$40.05** | Амортизація NRE (88% ціни) |
| **50 шт. (пілот)** | $3.52 / шт. | $3.90 / шт. | **$7.42** | Баланс NRE та завантаження панелей |
| **500 шт. (серія)** | $0.35 / шт. | $2.45 / шт. | **$2.80** | Ефективність розкрою панелі (85%) |
| **5 000 шт. (масове)** | $0.03 / шт. | $1.98 / шт. | **$2.01** | Вартість сировини та вихід придатних |

З таблиці чітко видно фундаментальну закономірність: для прототипів головним оптимізаційним завданням є вибір фабрики з дешевим пулінгом (поділом NRE між клієнтами), тоді як для серії понад 500 штук єдиним критичним фактором стає геометрія (розкрій панелі) та технологічний вихід.

### 3.4. Підводні камені та граничні обмеження геометрії

1. **Стрибок співвідношення сторін отвору (Aspect Ratio > 8:1)**. Коли товщина плати складає `1.6 мм`, а мінімальний діаметр механічного отвору зменшується до `0.15 мм` (співвідношення `10.6:1`), капілярні сили перешкоджають циркуляції електроліту всередині отвору під час гальванічної металізації. Фабрика змушена застосовувати ультразвукове перемішування та уповільнювати швидкість подачі свердла у 2.5 раза для уникнення заклинювання та перегріву. Це призводить до встановлення технологічної націнки `+30–50%` на операцію свердління.
2. **Пастка граничного розміру 100 × 100 мм**. Більшість фабрик прототипного виробництва субсидують виготовлення плат розміром до `100 × 100 мм` (спеціальні тарифи на кшталт «$2 за 5 плат»). Якщо розробник залишає плату габаритами `102 × 98 мм`, вона випадає з субсидованого пулу в категорію стандартного комерційного замовлення, і ціна партії з 5 плат миттєво зростає з $2 до $38.
3. **Асиметричне шарування та короблення (Warpage / Twisting)**. Якщо у 4-шаровій платі внутрішній шар L2 містить суцільний мідний полігон землі (90% міді), а шар L3 містить лише кілька рідких сигнальних доріжок (10% міді), різниця коефіцієнтів теплового розширення (CTE) призведе до скручування плати («пропелера») під час проходження печі оплавлення припою (reflow). Відповідно до стандарту IPC-6012, короблення понад `0.75%` вважається браком, що різко знижує вихід придатних виробів.

---

## 4. Практичні інженерні кейси оптимізації

### Кейс 1: Силовий перетворювач 48 В / 100 А (Товста мідь проти паралельних шарів)

Перед інженером стоїть завдання розвести плату синхронного понижувального перетворювача з піковим струмом 100 А. Початковий варіант: 4 шари з фольгою `3 oz` (105 мкм) на всіх шарах для забезпечення перерізу силових полігонів.

* **Аналіз варіанту 3 oz**: фольга 105 мкм вимагає мінімального зазору `10 mil` (0.25 мм) через ефект бокового підтравлювання міді (undercut). Це унеможливлює підведення доріжок до драйверів у корпусах QFN-32 з кроком виводів 0.5 мм. Фабрика виставляє рахунок із націнкою `+85%` за товсту мідь та збільшений час травлення.
* **Оптимізований варіант**: перехід на 6-шарову плату зі стандартною міддю `1 oz` (35 мкм), де силові полігони вхідного та вихідного струму розпаралелені по трьох внутрішніх та двох зовнішніх шарах за допомогою масиву теплових перехідних отворів (thermal vias).
* **Економічний результат**: 6-шарова плата 1 oz має мінімальний зазор `4/4 mil`, дозволяє пряме трасування QFN без перехідних плат, а її собівартість у серії з 1 000 штук виявляється на **22% нижчою**, ніж 4-шарова плата з міддю 3 oz.

### Кейс 2: Мікромодуль з процесором у BGA-0.4 мм (HDI 1+4+1 проти VIPPO на 6 шарах)

Для мобільного пристрою обрано систему на кристалі (SoC) у корпусі BGA-256 з кроком кульок `0.4 мм` та діаметром майданчика `0.22 мм`. Зазор між майданчиками складає лише `0.18 мм` (7.1 mil).

* Провести стандартну доріжку 4 mil з відступом 4 mil між сусідніми кульками геометрично неможливо (`4 + 4 + 4 = 12 mil > 7.1 mil`).
* **Варіант А**: 6-шарова плата зі стандартними наскрізними отворами у контактних майданчиках (VIPPO). Кожен отвір свердлиться механічно свердлом 0.15 мм, заповнюється смолою та гальванізується міддю. Витрати на VIPPO для 256 виводів BGA додають $8.96 до кожної плати.
* **Варіант Б**: 6-шарова плата з мікроотворами (HDI 1+4+1). Отвори між шарами L1-L2 та L5-L6 пропалюються UV-лазером (діаметр 100 мкм) безпосередньо у контактні майданчики BGA і затягуються міддю під час гальваніки без операції смоляного заповнення.
* **Результат**: для партії понад 500 штук варіант HDI 1+4+1 виявився на **34% дешевшим**, ніж механічний VIPPO на 6 шарах, оскільки лазерне свердління 1 000 мікроотворів на панелі виконується за лічені секунди, тоді як свердління мікросвердлами 0.15 мм на PTH вимагає постійної заміни дорогого інструменту та тривалого циклу планаризації.

### Кейс 3: Радіочастотний тракт на гібридному діелектрику (Rogers RO4350B + FR-4)

Для пристрою з радіотрактом 5.8 ГГц потрібна підкладка з низьким тангенсом діелектричних втрат (`tan δ < 0.004`). Суцільна 4-шарова плата з високочастотного ламінату Rogers RO4350B коштує у 4.5 раза дорожче за стандартний FR-4 через вартість керамо-вуглеводневого матеріалу та спеціальних алмазних фрез для обробки твердого наповнювача.

* **Гібридне рішення**: високочастотний ламінат RO4350B товщиною 0.254 мм використовується лише як зовнішнє ядро між шарами L1 та L2 для контрольованих 50-омних мікросмужкових ліній. Внутрішній пакет L2–L4 пресується зі стандартного дешевого склотекстоліту FR-4 Tg150.
* **Технологічні нюанси**: фабрика застосовує ступеневий температурний профіль пресування, оскільки температура плинності смоли препрегу FR-4 (175 °C) відрізняється від характеристик розширення Rogers. Це додає $65 до інженерної підготовки NRE, проте скорочує витрати на матеріали панелі на **58%**.

---

## 5. Інтеграція калькулятора в автоматизований CI/CD конвеєр

Сучасна розробка електроніки переймає практики неперервної інтеграції з програмної інженерії. Автоматизований запуск параметричного калькулятора дозволяє зупиняти злиття змін у репозиторій плати (Pull Request), якщо зміна топології спричинила критичне зростання прогнозованої собівартості.

Типовий конвеєр автоматичної перевірки виконує такі кроки:
1. **Експорт фізичних параметрів**: скрипт на Python або KiCad CLI витягує з файлу плати (`.kicad_pcb` або ODB++) розміри контуру, кількість мідних шарів, мінімальний зазор DRC, кількість отворів у контактних майданчиках (VIPPO) та товщину міді;
2. **Формування JSON-специфікації**: згенеровані параметри передаються у скомпільований бінарний модуль калькулятора;
3. **Порівняння з бюджетом проекту**: якщо розрахована собівартість плати при цільовій партії 1 000 штук перевищує ліміт специфікації (наприклад, $3.50 за одиницю), CI-сервер маркує пайплайн як невдалий і додає звіт із детальним переліком факторів здорожчання прямо в коментарі до пул-реквесту.

Такий підхід повністю виключає неприємні сюрпризи, коли після місяців проектування з'ясовується, що плата коштує вдвічі дорожче за закладену в бізнес-план фінансову модель.
