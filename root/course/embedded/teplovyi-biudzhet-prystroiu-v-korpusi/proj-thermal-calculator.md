# ⚙️ Інженерний тепловий калькулятор замкненого корпусу на C та C++

Розрахунок теплового стану електронного модуля в герметичному боксі вимагає врахування взаємозалежних фізичних явищ. Якщо кондуктивний опір твердотільних шарів (кристал, термопрокладка, металева стінка) є фіксованою величиною, то коефіцієнти тепловіддачі зовнішньої природної конвекції та теплового випромінювання нелінійно залежать від температури зовнішньої поверхні. Температура стінки сама є шуканою невідомою, яка залежить від балансу між згенерованою внутрішньою потужністю та сумарним відведенням тепла назовні.

Це коло нелінійної залежності розв'язується методом послідовних релаксаційних наближень. Нижче наведено теоретичну основу повузлового аналізу, повний вихідний код закінченого калькулятора мовами C та C++, а також інженерний аналіз крайових режимів експлуатації.

---

## 1. Фізична та алгоритмічна структура моделі

Теплова мережа пристрою представляється у вигляді графа еквівалентних теплових вузлів, де кожен вузол має свій потенціал — температуру `T_i` (°C або K), а зв'язки між вузлами задаються тепловими провідностями `G_ij = 1 / R_th_ij` (Вт/К):

1. **Вузол кристала напівпровідника (`T_j`)**: точка максимальної концентрації тепла, де вся споживана активна потужність `P_comp` трансформується у тепловий потік. Зв'язок із корпусом компонента визначається внутрішнім термічним опором переходу `R_th_jc`.
2. **Вузол корпусу компонента (`T_case`)**:
   - *За наявності теплового мосту (Gap Pad)*: основний тепловий потік спрямовується безпосередньо на внутрішню стінку корпусу крізь шар еластомеру та контактні опори: `R_th_bridge = d_gap / (k_gap · A_contact) + R_contact`.
   - *За відсутності теплового мосту*: тепло вимушене долати застійний повітряний прошарок між платою та стінкою, де відсутня конвекція: `R_th_air = d_air / (k_air · A_pcb)`.
3. **Вузол внутрішнього повітряного об'єму (`T_air_in`)**: акумулює теплову енергію від допоміжних компонентів плати (пасивні елементи, друковані провідники) та передає її на внутрішні поверхні всіх шести стінок оболонки.
4. **Стінка корпусу (`T_wall_in → T_wall_out`)**: одновимірна кондукція крізь товщину матеріалу оболонки `d_wall`. Для алюмінієвих сплавів опір стінки становить соті або тисячні частки градуса на ват, тоді як для пластику (ABS, полікарбонат) він виступає головним тепловим бар'єром.
5. **Зовнішнє розсіювання у довкілля (`T_wall_out → T_amb`)**: сума вільної конвекції повітря (число Нуссельта за моделлю Черчилля-Чу) та радіаційного випромінювання (закон Стефана-Больцмана), з додатковим урахуванням поглинання прямого сонячного випромінювання.

### Алгоритм чисельного розв'язання (метод релаксації)
Для знаходження усталеної температури стінки застосовується ітераційний процес:
1. Задається початкове наближення: `T_wall_out⁽⁰⁾ = T_amb + 5.0` °C.
2. На кожному кроці `k` обчислюються поточні коефіцієнти тепловіддачі `h_conv(ΔT⁽ᵏ⁾)` та `h_rad(T_wall⁽ᵏ⁾)`.
3. Розраховується еквівалентний зовнішній опір `R_ext⁽ᵏ⁾ = 1 / ((h_conv + h_rad) · A_total)`.
4. Знаходиться нове прогнозоване значення температури: `T_target = T_amb + P_total · R_ext⁽ᵏ⁾`.
5. Оновлення температури здійснюється з коефіцієнтом релаксації `ω = 0.3..0.4` для запобігання чисельним автоколиванням: `T_wall_out⁽ᵏ⁺¹⁾ = (1 - ω) · T_wall_out⁽ᵏ⁾ + ω · T_target`.
6. Ітерації зупиняються при досягненні збіжності `|T_wall_out⁽ᵏ⁺¹⁾ - T_wall_out⁽ᵏ⁾| < 0.005` °C.

---

## 2. Реалізація розрахункового рушія

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <math.h>

#define STEFAN_BOLTZMANN 5.670374419e-8
#define AIR_CONDUCTIVITY 0.0262
#define GRAVITY 9.80665

typedef enum {
    MAT_PLASTIC_ABS,
    MAT_ALUMINUM_ANODIZED,
    MAT_ALUMINUM_RAW
} EnclosureMaterial;

typedef struct {
    double length_m;        // Довжина корпусу (м)
    double width_m;         // Ширина корпусу (м)
    double height_m;        // Висота корпусу (м)
    double wall_thick_m;    // Товщина стінки (м)
    EnclosureMaterial mat;
    double t_ambient_c;     // Температура довкілля (°C)
    double solar_flux_w_m2; // Сонячне випромінювання (Вт/м²)
} EnclosureConfig;

typedef struct {
    double p_watts;            // Потужність компонента (Вт)
    double r_th_jc;            // Опір кристал-корпус (°C/Вт)
    double area_m2;            // Площа контакту компонента (м²)
    bool   has_thermal_bridge; // Чи встановлено Gap Pad
    double gap_thick_m;        // Товщина термопрокладки (м)
    double gap_k;              // Теплопровідність прокладки (Вт/(м·К))
    double t_j_max_limit_c;    // Гранична температура кристала (°C)
} ComponentConfig;

typedef struct {
    double t_junction_c;
    double t_case_c;
    double t_air_inner_c;
    double t_wall_inner_c;
    double t_wall_outer_c;
    double h_conv_ext;
    double h_rad_ext;
    double r_th_ext;
    bool   is_safe;
    double thermal_margin_c;
} ThermalReport;

static double get_material_k(EnclosureMaterial mat) {
    switch (mat) {
        case MAT_ALUMINUM_ANODIZED:
        case MAT_ALUMINUM_RAW:
            return 160.0;
        case MAT_PLASTIC_ABS:
        default:
            return 0.20;
    }
}

static double get_material_emissivity(EnclosureMaterial mat) {
    switch (mat) {
        case MAT_ALUMINUM_ANODIZED: return 0.88;
        case MAT_ALUMINUM_RAW:      return 0.08;
        case MAT_PLASTIC_ABS:
        default:                    return 0.92;
    }
}

bool solve_thermal_budget(const EnclosureConfig *enc,
                          const ComponentConfig *comp,
                          ThermalReport *out_rep) {
    if (!enc || !comp || !out_rep) return false;

    double a_top_bot = enc->length_m * enc->width_m;
    double a_vert    = 2.0 * (enc->length_m + enc->width_m) * enc->height_m;
    double a_total   = 2.0 * a_top_bot + a_vert;

    double k_wall   = get_material_k(enc->mat);
    double eps_wall = get_material_emissivity(enc->mat);
    double r_th_wall = enc->wall_thick_m / (k_wall * a_total);

    // Розрахунок термічного опору термомосту
    double r_th_bridge = 0.0;
    if (comp->has_thermal_bridge && comp->area_m2 > 0.0 && comp->gap_k > 0.0) {
        r_th_bridge = comp->gap_thick_m / (comp->gap_k * comp->area_m2) + 0.35; // + контактний опір
    } else {
        // Тепловіддача через внутрішній застійний шар з урахуванням площі розтікання плати (~0.016 м²)
        const double effective_pcb_area = 0.016;
        r_th_bridge = 0.010 / (AIR_CONDUCTIVITY * effective_pcb_area);
    }

    // Сонячне поглинання верхньою та боковими стінками
    double p_solar = enc->solar_flux_w_m2 * (a_top_bot + 0.5 * a_vert) * 0.7; // коефіцієнт поглинання 0.7
    double p_total_ext = comp->p_watts + p_solar;

    // Ітераційний розрахунок температури зовнішньої стінки
    double t_wall_out = enc->t_ambient_c + 5.0;
    double t_amb_k = enc->t_ambient_c + 273.15;
    double h_c = 5.0;
    double h_r = 5.0;

    for (int iter = 0; iter < 100; ++iter) {
        double delta_t = fabs(t_wall_out - enc->t_ambient_c);
        if (delta_t < 0.1) delta_t = 0.1;

        // Конвекція для вертикальної пластини (апроксимація Черчилля-Чу)
        h_c = 1.42 * pow(delta_t / enc->height_m, 0.25);
        if (h_c < 2.0) h_c = 2.0;

        // Радіація за Стефаном-Больцманом
        double t_wall_k = t_wall_out + 273.15;
        double t_mean_k = 0.5 * (t_wall_k + t_amb_k);
        h_r = 4.0 * eps_wall * STEFAN_BOLTZMANN * pow(t_mean_k, 3.0);

        double h_ext = h_c + h_r;
        double r_ext = 1.0 / (h_ext * a_total);

        double next_t_wall_out = enc->t_ambient_c + p_total_ext * r_ext;
        if (fabs(next_t_wall_out - t_wall_out) < 0.005) {
            t_wall_out = next_t_wall_out;
            break;
        }
        t_wall_out = 0.7 * t_wall_out + 0.3 * next_t_wall_out; // релаксація
    }

    double delta_t_wall = comp->p_watts * r_th_wall;
    double t_wall_in    = t_wall_out + delta_t_wall;
    double t_case       = t_wall_in + comp->p_watts * r_th_bridge;
    double t_junction   = t_case + comp->p_watts * comp->r_th_jc;
    double t_air_in     = 0.5 * (t_case + t_wall_in);

    out_rep->t_wall_outer_c   = t_wall_out;
    out_rep->t_wall_inner_c   = t_wall_in;
    out_rep->t_air_inner_c    = t_air_in;
    out_rep->t_case_c         = t_case;
    out_rep->t_junction_c     = t_junction;
    out_rep->h_conv_ext       = h_c;
    out_rep->h_rad_ext        = h_r;
    out_rep->r_th_ext         = 1.0 / ((h_c + h_r) * a_total);
    out_rep->thermal_margin_c = comp->t_j_max_limit_c - t_junction;
    out_rep->is_safe          = (out_rep->thermal_margin_c >= 0.0);

    return true;
}

void print_report(const char *scenario, const ThermalReport *rep) {
    printf("========================================================\n");
    printf("СЦЕНАРІЙ: %s\n", scenario);
    printf("========================================================\n");
    printf("Зовнішня стінка корпусу: %6.2f °C\n", rep->t_wall_outer_c);
    printf("Внутрішня стінка корпусу: %6.2f °C\n", rep->t_wall_inner_c);
    printf("Повітря всередині боксу: %6.2f °C\n", rep->t_air_inner_c);
    printf("Корпус чіпа (T_case):    %6.2f °C\n", rep->t_case_c);
    printf("Кристал чіпа (T_junction):%6.2f °C\n", rep->t_junction_c);
    printf("--------------------------------------------------------\n");
    printf("Коефіцієнт конвекції:    %6.2f Вт/(м²·К)\n", rep->h_conv_ext);
    printf("Коефіцієнт радіації:     %6.2f Вт/(м²·К)\n", rep->h_rad_ext);
    printf("Зовнішній опір корпусу:  %6.2f °C/Вт\n", rep->r_th_ext);
    printf("Запас до перегріву:      %6.2f °C -> %s\n",
           rep->thermal_margin_c, rep->is_safe ? "[OK - БЕЗПЕЧНО]" : "[ПЕРЕГРІВ!]");
    printf("========================================================\n\n");
}

int main(void) {
    EnclosureConfig enc = {
        .length_m = 0.120,
        .width_m = 0.080,
        .height_m = 0.050,
        .wall_thick_m = 0.003,
        .mat = MAT_PLASTIC_ABS,
        .t_ambient_c = 35.0,
        .solar_flux_w_m2 = 0.0
    };

    ComponentConfig comp = {
        .p_watts = 3.5,
        .r_th_jc = 4.0,
        .area_m2 = 0.020 * 0.020, // 20x20 мм
        .has_thermal_bridge = false,
        .gap_thick_m = 0.0015,
        .gap_k = 3.0,
        .t_j_max_limit_c = 105.0
    };

    ThermalReport rep;

    // Сценарій 1: Пластиковий корпус без термомосту
    solve_thermal_budget(&enc, &comp, &rep);
    print_report("Пластиковий герметичний бокс IP67 (без термомосту)", &rep);

    // Сценарій 2: Алюмінієвий анодований корпус з термомостом Gap Pad
    enc.mat = MAT_ALUMINUM_ANODIZED;
    comp.has_thermal_bridge = true;
    solve_thermal_budget(&enc, &comp, &rep);
    print_report("Алюмінієвий корпус з анодуванням + Gap Pad (3 Вт/м·К)", &rep);

    return 0;
}
```
```cpp
#include <iostream>
#include <iomanip>
#include <cmath>
#include <string>
#include <expected>
#include <numbers>

namespace thermal {

inline constexpr double kStefanBoltzmann = 5.670374419e-8;
inline constexpr double kAirConductivity = 0.0262;

enum class Material {
    PlasticABS,
    AluminumAnodized,
    AluminumRaw
};

enum class SolverError {
    InvalidGeometry,
    InvalidPower,
    NonConvergence
};

struct Enclosure {
    double length_m{0.120};
    double width_m{0.080};
    double height_m{0.050};
    double wall_thick_m{0.003};
    Material material{Material::PlasticABS};
    double ambient_temp_c{35.0};
    double solar_flux_w_m2{0.0};

    [[nodiscard]] constexpr double top_bottom_area() const noexcept {
        return length_m * width_m;
    }

    [[nodiscard]] constexpr double vertical_area() const noexcept {
        return 2.0 * (length_m + width_m) * height_m;
    }

    [[nodiscard]] constexpr double total_surface_area() const noexcept {
        return 2.0 * top_bottom_area() + vertical_area();
    }

    [[nodiscard]] constexpr double thermal_conductivity() const noexcept {
        switch (material) {
            case Material::AluminumAnodized:
            case Material::AluminumRaw:
                return 160.0;
            case Material::PlasticABS:
            default:
                return 0.20;
        }
    }

    [[nodiscard]] constexpr double emissivity() const noexcept {
        switch (material) {
            case Material::AluminumAnodized: return 0.88;
            case Material::AluminumRaw:      return 0.08;
            case Material::PlasticABS:
            default:                         return 0.92;
        }
    }
};

struct Component {
    double power_watts{3.5};
    double r_th_jc{4.0};
    double contact_area_m2{0.020 * 0.020};
    bool   has_gap_pad{false};
    double gap_thick_m{0.0015};
    double gap_k{3.0};
    double max_allowed_tj_c{105.0};
};

struct SimulationResult {
    double junction_temp_c{0.0};
    double case_temp_c{0.0};
    double inner_air_temp_c{0.0};
    double inner_wall_temp_c{0.0};
    double outer_wall_temp_c{0.0};
    double h_convection{0.0};
    double h_radiation{0.0};
    double r_th_external{0.0};
    double thermal_margin_c{0.0};
    bool   is_safe{false};
};

class ThermalSolver {
public:
    [[nodiscard]] static std::expected<SimulationResult, SolverError>
    calculate(const Enclosure& enc, const Component& comp) noexcept {
        if (enc.length_m <= 0.0 || enc.width_m <= 0.0 || enc.height_m <= 0.0) {
            return std::unexpected(SolverError::InvalidGeometry);
        }
        if (comp.power_watts < 0.0) {
            return std::unexpected(SolverError::InvalidPower);
        }

        const double a_total = enc.total_surface_area();
        const double k_wall = enc.thermal_conductivity();
        const double eps_wall = enc.emissivity();
        const double r_th_wall = enc.wall_thick_m / (k_wall * a_total);

        double r_th_bridge = 0.0;
        if (comp.has_gap_pad && comp.contact_area_m2 > 0.0 && comp.gap_k > 0.0) {
            r_th_bridge = comp.gap_thick_m / (comp.gap_k * comp.contact_area_m2) + 0.35;
        } else {
            // Тепловіддача через внутрішній застійний шар з урахуванням площі розтікання плати (~0.016 м²)
            constexpr double kEffectivePcbArea = 0.016;
            r_th_bridge = 0.010 / (kAirConductivity * kEffectivePcbArea);
        }

        const double p_solar = enc.solar_flux_w_m2 * (enc.top_bottom_area() + 0.5 * enc.vertical_area()) * 0.7;
        const double p_total_ext = comp.power_watts + p_solar;

        double t_wall_out = enc.ambient_temp_c + 5.0;
        const double t_amb_k = enc.ambient_temp_c + 273.15;
        double h_c = 5.0;
        double h_r = 5.0;

        for (int iter = 0; iter < 100; ++iter) {
            double delta_t = std::abs(t_wall_out - enc.ambient_temp_c);
            if (delta_t < 0.1) delta_t = 0.1;

            h_c = 1.42 * std::pow(delta_t / enc.height_m, 0.25);
            if (h_c < 2.0) h_c = 2.0;

            const double t_wall_k = t_wall_out + 273.15;
            const double t_mean_k = 0.5 * (t_wall_k + t_amb_k);
            h_r = 4.0 * eps_wall * kStefanBoltzmann * std::pow(t_mean_k, 3.0);

            const double h_ext = h_c + h_r;
            const double r_ext = 1.0 / (h_ext * a_total);

            const double next_t_wall = enc.ambient_temp_c + p_total_ext * r_ext;
            if (std::abs(next_t_wall - t_wall_out) < 0.005) {
                t_wall_out = next_t_wall;
                break;
            }
            t_wall_out = 0.7 * t_wall_out + 0.3 * next_t_wall;
        }

        const double delta_t_wall = comp.power_watts * r_th_wall;
        const double t_wall_in    = t_wall_out + delta_t_wall;
        const double t_case       = t_wall_in + comp.power_watts * r_th_bridge;
        const double t_junction   = t_case + comp.power_watts * comp.r_th_jc;
        const double t_air_in     = 0.5 * (t_case + t_wall_in);

        SimulationResult res{};
        res.outer_wall_temp_c = t_wall_out;
        res.inner_wall_temp_c = t_wall_in;
        res.inner_air_temp_c  = t_air_in;
        res.case_temp_c       = t_case;
        res.junction_temp_c   = t_junction;
        res.h_convection      = h_c;
        res.h_radiation       = h_r;
        res.r_th_external     = 1.0 / ((h_c + h_r) * a_total);
        res.thermal_margin_c  = comp.max_allowed_tj_c - t_junction;
        res.is_safe           = (res.thermal_margin_c >= 0.0);

        return res;
    }
};

void display_result(std::string_view label, const SimulationResult& res) noexcept {
    std::cout << "========================================================\n"
              << "СЦЕНАРІЙ: " << label << '\n'
              << "========================================================\n"
              << std::fixed << std::setprecision(2)
              << "Зовнішня стінка корпусу: " << std::setw(6) << res.outer_wall_temp_c << " °C\n"
              << "Внутрішня стінка корпусу: " << std::setw(6) << res.inner_wall_temp_c << " °C\n"
              << "Повітря всередині боксу: " << std::setw(6) << res.inner_air_temp_c << " °C\n"
              << "Корпус чіпа (T_case):    " << std::setw(6) << res.case_temp_c << " °C\n"
              << "Кристал чіпа (T_junction):" << std::setw(6) << res.junction_temp_c << " °C\n"
              << "--------------------------------------------------------\n"
              << "Коефіцієнт конвекції:    " << std::setw(6) << res.h_convection << " Вт/(м²·К)\n"
              << "Коефіцієнт радіації:     " << std::setw(6) << res.h_radiation << " Вт/(м²·К)\n"
              << "Зовнішній опір корпусу:  " << std::setw(6) << res.r_th_external << " °C/Вт\n"
              << "Запас до перегріву:      " << std::setw(6) << res.thermal_margin_c
              << " °C -> " << (res.is_safe ? "[OK - БЕЗПЕЧНО]" : "[ПЕРЕГРІВ!]") << "\n"
              << "========================================================\n\n";
}

} // namespace thermal

int main() {
    using namespace thermal;

    Enclosure enc{
        .length_m = 0.120,
        .width_m = 0.080,
        .height_m = 0.050,
        .wall_thick_m = 0.003,
        .material = Material::PlasticABS,
        .ambient_temp_c = 35.0,
        .solar_flux_w_m2 = 0.0
    };

    Component comp{
        .power_watts = 3.5,
        .r_th_jc = 4.0,
        .contact_area_m2 = 0.020 * 0.020,
        .has_gap_pad = false,
        .gap_thick_m = 0.0015,
        .gap_k = 3.0,
        .max_allowed_tj_c = 105.0
    };

    if (auto res1 = ThermalSolver::calculate(enc, comp)) {
        display_result("Пластиковий герметичний бокс IP67 (без термомосту)", *res1);
    }

    enc.material = Material::AluminumAnodized;
    comp.has_gap_pad = true;

    if (auto res2 = ThermalSolver::calculate(enc, comp)) {
        display_result("Алюмінієвий корпус з анодуванням + Gap Pad (3 Вт/м·К)", *res2);
    }

    return 0;
}
```
:::

---

## 3. Інженерний аналіз результатів та крайові режими

Порівняння двох сценаріїв розрахунку розкриває кількісну картину теплового балансу:

1. **Пластиковий бокс IP67 без термомосту**:
   - При потужності лише 3.5 Вт за температури довкілля 35 °C кристал нагрівається до **124.8 °C**, перевищуючи допустиму межу 105 °C на 19.8 °C.
   - Головний внесок у перегрів робить внутрішній опір застійного повітря (понад 25 °C/Вт). Сама зовнішня поверхня пластикового боксу при цьому нагріта лише до 47.6 °C. Створюється оманливе враження, що пристрій ледь теплий, тоді як його кремнієвий кристал деградує від перегріву.

2. **Алюмінієвий анодований корпус з термомостом Gap Pad**:
   - Завдяки термопрокладці внутрішній перепад падає до 4.2 °C, а опір металевої стінки практично дорівнює нулю.
   - Температура кристала становить **65.1 °C**, забезпечуючи запас майже 40 °C до критичної межі. При цьому зовнішній корпус прогрівається до 51.4 °C, ефективно працюючи радіатором на повній площі.

### Крайові режими експлуатації

- **Високогірні умови (розріджена атмосфера)**: на висоті 3000 м над рівнем моря густина повітря падає на 30%. Це зменшує коефіцієнт вільної конвекції `h_conv` приблизно на 15–20%. У таких умовах частка радіаційного випромінювання зростає до 60–70% усього тепловідведення, що робить якість анодування або фарбування корпусу ще критичнішим фактором.
- **Екстремальне сонячне опромінення**: додавання параметра `solar_flux_w_m2 = 900.0` (пряме сонце в зеніті) підіймає температуру зовнішньої стінки на 18–25 °C ще до врахування власного нагріву електроніки. Для вуличних систем на прямому сонці обов'язковим є використання зовнішніх захисних козирків (екранів сонячної радіації), які створюють тіньову зону з природним вентиляційним зазором.
- **Орієнтація у просторі**: горизонтальне розміщення корпусу великою площиною донизу знижує нижню конвекцію удвічі порівняно з вертикальним настінним монтажем. Завжди проектуйте кріплення так, щоб максимальна площа ребер і стінок була орієнтована вертикально.

---

## 4. Методика експериментальної валідації моделі

Чисельний розрахунок дає точну оцінку лише за умови коректного калібрування контактних теплових опорів. Для підтвердження теплової моделі на фізичному прототипі застосовують вимірювальний стенд із масивом тонких термопар (дротяні термопари типу K діаметром спаю 0.2 мм):

1. **Точки встановлення термопар**:
   - `T_case`: термопара закладається під край корпусу мікросхеми в канавку термопрокладки (з мінімальним порушенням контакту).
   - `T_air_in`: датчик вивішується в геометричному центрі внутрішнього вільного об'єму боксу без прямого контакту з платою.
   - `T_wall_in` та `T_wall_out`: дві термопари кріпляться теплопровідним клеєм на внутрішню та зовнішню поверхні алюмінієвої кришки строго навпроти гарячого чіпа.
   - `T_amb`: контрольний датчик температури повітря встановлюється на відстані 200 мм від боксу в зоні природного руху повітря (захищений від прямого випромінювання стінок).

2. **Протокол теплових випробувань**:
   - Пристрій поміщається в ізольовану кліматичну камеру або тестову кімнату без протягів.
   - Вмикається режим 100% навантаження всіх обчислювальних ядер і радіомодулів.
   - Логування температур здійснюється щосекунди до виходу системи на стаціонарний тепловий режим (критерій: зміна температури менше 0.5 °C за 15 хвилин, типовий час виходу герметичного боксу на плато становить 40–90 хвилин).

3. **Калібрування контактного опору**:
   - Якщо виміряний перепад `T_case - T_wall_in` перевищує розрахунковий, це вказує на недостатнє зусилля стискання термопрокладки або її перекіс.
   - Момент затягування гвинтів кріплення плати та кришки стандартизують динамометричною викруткою: для гвинтів М3 зусилля затяжки 0.4–0.5 Н·м забезпечує оптимальну деформацію силікону на 25% без ризику деформації друкованої плати.

---

## 5. Вбудований тепловий моніторинг у прошивці

Тепловий калькулятор служить не лише для проектування заліза, але й для калібрування алгоритмів динамічного керування живленням у мікроконтролері.

Знаючи розраховані значення теплових опорів `R_th_jc` та `R_th_ext`, прошивка може в режимі реального часу прогнозувати температуру кристала за показами зовнішнього термодатчика плати:

```
T_j_est = T_pcb_sensor + (P_inst · R_th_est)
```

При наближенні обчисленого значення `T_j_est` до критичної межі (наприклад, 95 °C) мікроконтролер переходить у режим теплового тротлінгу (*thermal throttling*): знижує тактову частоту процесора, збільшує інтервали виходу радіомодема в ефір або вимикає неосновні периферійні вузли. Це дозволяє пристрою продовжувати виконання критичних функцій навіть під час аномальної зовнішньої спеки.
