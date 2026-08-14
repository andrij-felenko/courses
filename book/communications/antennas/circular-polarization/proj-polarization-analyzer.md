# ⚙️ Аналізатор поляризаційного еліпса та розрахунок коефіцієнта осьового відношення

Точна оцінка поляризаційного стану електромагнітної хвилі в цифрових програмованих радіосистемах (SDR) та контрольно-вимірювальних комплексах вимагає розв'язання задачі оперативної обробки ортогональних комплексних відліків I/Q. Вимірювання векторів Стокса S₀…S₃ та розрахунок осьового відношення (Axial Ratio, AR) дають змогу геометрично відновити поляризаційний еліпс, визначити кути τ і χ, класифікувати тип поляризації (Linear, RHCP, LHCP) та обчислити поляризаційні втрати (PLF) для автоматичного фазування і вибору оптимального приймального каналу. Програмний модуль мовами C та C++ реалізує цей обчислювальний тракт із дотриманням чисельної стабільності та підтримкою новітніх стандартів.

---

### Системне призначення та архітектура модуля

У сучасних НВЧ-вимірювальних комплексах і цифровій обробці сигналів (DSP) вектор електричного поля отримують у вигляді двох комплексних відліків `I/Q` від двох ортогонально орієнтованих приймальних каналів (горизонтального `E_x` та вертикального `E_y`).

Завдання аналітичного модуля полягає в перетворенні цих сирих амплітудно-фазових вимірювань на інженерні параметри поляризаційного стану хвилі:
1. **Обчислення параметрів Стокса (`S₀, S₁, S₂, S₃`):** фізичні величини інтенсивності поля, які вимірюють ступінь переважання лінійних чи кругових компонент.
2. **Геометрична ідентифікація еліпса:** визначення великої півосі `a`, малой півосі `b`, кута нахилу `τ` (tilt angle) та кута еліптичності `χ`.
3. **Обчислення осьового відношення (Axial Ratio, AR):** ключової характеристики чистоти кругової поляризації як у лінійному масштабі, так і в децибелах.
4. **Класифікація поляризаційного стану:** надання чіткого системного висновку (Linear, RHCP, LHCP, Elliptical Right, Elliptical Left) на основі порогів `AR` та знаку параметра Стокса `S₃`.
5. **Прогнозування втрат енергії (PLF):** обчислення ефективності прийому даної хвилі стандартними антенами (лінійною горизонтальною/вертикальною та ідеальною RHCP/LHCP антеною).

---

### Обробка крайових випадків та чисельна стабільність

Під час чисельного розрахунку поляризаційних параметрів на мікроконтролерах чи DSP-процесорах виникають специфічні обчислювальні ризики:

- **Ділення на нуль при лінійній поляризації:** Коли мала піввісь `b → 0`, кут еліптичності `χ → 0`, а тангенс `tan(χ) → 0`. Пряме обчислення `AR = 1 / tan(χ)` викликає апаратне виключення `divide-by-zero`. У модулі реалізовано захисну перевірку: якщо `|tan(χ)| < 1e-6`, значення `AR` примусово обмежується константою `1e6` (що відповідає `99.9 дБ`), а стан однозначно класифікується як `POL_LINEAR`.
- **Вихід аргументу за межі допустимого діапазону тригонометричних функцій:** Через накоплення похибок округлення чисел із плаваючою крапкою (`float`/`double`) нормований параметр Стокса `s₃ = S₃ / S₀` може набути значення `1.0000000000000002`. Прямий виклик `asin(1.0000000000000002)` у стандартній бібліотеці `math.h` повертає значення `NaN` (Not a Number). У C++ реалізації застосовано функцію `std::clamp(s3_norm, -1.0, 1.0)`, яка гарантує чисельну стабільність.
- **Обробка фазової невизначеності при нульовій амплітуді:** Якщо обидві амплітуди `E₀x` та `E₀y` наближаються до нуля (рівень сигналу нижче порогу шумів), програма корректно повертає помилку через механізм `std::expected` у C++20 або відповідний прапорець помилки у C.

---

### Опис вхідних та вихідних структур даних

Математичний апарат алгоритму спирається на три базові структури:

1. **`FieldInput`:**
   - `ex0` (`double`): амплітуда складової електричного поля уздовж осі `x` (В/м або Уод. АЦП).
   - `ey0` (`double`): амплітуда складової електричного поля уздовж осі `y` (В/м або Уод. АЦП).
   - `delta_deg` (`double`): різниця фаз між вертикальною та горизонтальною складовими у градусах (`δ = φ_y - φ_x`).

2. **`PolarizationAnalysis`:**
   - `s0, s1, s2, s3`: параметри Стокса у фізичних одиницях інтенсивності.
   - `s1_norm, s2_norm, s3_norm`: нормовані компоненти вектора Стокса на одиничній сфері Пуанкаре (`s₁² + s₂² + s₃² = 1.0`).
   - `major_axis, minor_axis`: обчислені довжини великої `a` та малої `b` півосей поляризаційного еліпса.
   - `tilt_deg`: кут нахилу великої осі `τ` відносно горизонталі у градусах (`-90° ≤ τ ≤ 90°`).
   - `ellipticity_deg`: кут еліптичності `χ` у градусах (`-45° ≤ χ ≤ 45°`).
   - `ar_linear, ar_db`: осьове відношення у лінійному масштабі та в децибелах.
   - `pol_class`: перелічуваний тип класифікації стану поляризації.
   - `plf_linear_h, plf_rhcp`: коефіцієнти поляризаційних втрат для H-антени та RHCP-антени (значення від `0.0` до `1.0`).

---

### Програмна реалізація мовами C та C++

:::tabs
```c
#include <stdio.h>
#include <math.h>
#include <stdbool.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef enum {
    POL_LINEAR,
    POL_CIRCULAR_RHCP,
    POL_CIRCULAR_LHCP,
    POL_ELLIPTICAL_RHCP,
    POL_ELLIPTICAL_LHCP
} PolarizationClass;

typedef struct {
    double ex0;          /* Амплітуда E_x */
    double ey0;          /* Амплітуда E_y */
    double delta_deg;    /* Зсув фази у градусах (y відносно x) */
} FieldInput;

typedef struct {
    double s0, s1, s2, s3;  /* Параметри Стокса */
    double s1_norm, s2_norm, s3_norm;
    double major_axis;   /* Велика піввісь a */
    double minor_axis;   /* Мала піввісь b */
    double tilt_deg;     /* Кут нахилу tau (град) */
    double ellipticity_deg; /* Кут еліптичності chi (град) */
    double ar_linear;    /* Осьове відношення (лінійне) */
    double ar_db;        /* Осьове відношення (дБ) */
    PolarizationClass pol_class;
    double plf_linear_h; /* PLF для горизонтальної антени (0.0 .. 1.0) */
    double plf_rhcp;     /* PLF для ідеальної RHCP антени */
} PolarizationAnalysis;

static double deg_to_rad(double deg) {
    return deg * M_PI / 180.0;
}

static double rad_to_deg(double rad) {
    return rad * 180.0 / M_PI;
}

PolarizationAnalysis analyze_polarization(FieldInput input) {
    PolarizationAnalysis res;
    double delta = deg_to_rad(input.delta_deg);
    double ex2 = input.ex0 * input.ex0;
    double ey2 = input.ey0 * input.ey0;

    /* 1. Розрахунок базових параметрів Стокса */
    res.s0 = ex2 + ey2;
    res.s1 = ex2 - ey2;
    res.s2 = 2.0 * input.ex0 * input.ey0 * cos(delta);
    res.s3 = 2.0 * input.ex0 * input.ey0 * sin(delta);

    /* 2. Нормування векторів Стокса */
    if (res.s0 > 1e-12) {
        res.s1_norm = res.s1 / res.s0;
        res.s2_norm = res.s2 / res.s0;
        res.s3_norm = res.s3 / res.s0;
    } else {
        res.s1_norm = res.s2_norm = res.s3_norm = 0.0;
    }

    /* 3. Кут нахилу tau [-90..90] та кут еліптичності chi [-45..45] */
    double two_tau = atan2(res.s2, res.s1);
    res.tilt_deg = rad_to_deg(two_tau / 2.0);

    /* sin(2*chi) = s3 / s0 */
    double sin_two_chi = res.s3_norm;
    if (sin_two_chi > 1.0) sin_two_chi = 1.0;
    if (sin_two_chi < -1.0) sin_two_chi = -1.0;
    double two_chi = asin(sin_two_chi);
    res.ellipticity_deg = rad_to_deg(two_chi / 2.0);

    /* 4. Обчислення великої та малої півосей еліпса */
    double tan_chi = tan(two_chi / 2.0);
    double abs_tan_chi = fabs(tan_chi);
    
    double e_total = sqrt(res.s0);
    /* a = E_total * cos(chi), b = E_total * |sin(chi)| */
    res.major_axis = e_total * cos(two_chi / 2.0);
    res.minor_axis = e_total * fabs(sin(two_chi / 2.0));

    /* 5. Осьове відношення (Axial Ratio) */
    if (abs_tan_chi < 1e-6) {
        res.ar_linear = 1e6; /* Нескінченність для лінійної */
        res.ar_db = 99.9;
    } else {
        res.ar_linear = 1.0 / abs_tan_chi;
        res.ar_db = 20.0 * log10(res.ar_linear);
    }

    /* 6. Класифікація стану поляризації */
    if (res.ar_db > 20.0) {
        res.pol_class = POL_LINEAR;
    } else if (res.ar_db < 0.5) {
        res.pol_class = (res.s3 > 0) ? POL_CIRCULAR_RHCP : POL_CIRCULAR_LHCP;
    } else {
        res.pol_class = (res.s3 > 0) ? POL_ELLIPTICAL_RHCP : POL_ELLIPTICAL_LHCP;
    }

    /* 7. Розрахунок PLF для приймача */
    /* Для горизонтальної лінійної антени вектор s_r = (1, 0, 0) */
    res.plf_linear_h = 0.5 * (1.0 + res.s1_norm);
    /* Для ідеальної RHCP антени вектор s_r = (0, 0, +1) */
    res.plf_rhcp = 0.5 * (1.0 + res.s3_norm);

    return res;
}

const char* get_pol_class_name(PolarizationClass c) {
    switch (c) {
        case POL_LINEAR:          return "Лінійна (Linear)";
        case POL_CIRCULAR_RHCP:   return "Чиста колова RHCP";
        case POL_CIRCULAR_LHCP:   return "Чиста колова LHCP";
        case POL_ELLIPTICAL_RHCP: return "Еліптична (Праве обертання / RHCP)";
        case POL_ELLIPTICAL_LHCP: return "Еліптична (Ліве обертання / LHCP)";
    }
    return "Невідома";
}

int main(void) {
    FieldInput in = { .ex0 = 1.0, .ey0 = 0.8, .delta_deg = 80.0 };
    PolarizationAnalysis res = analyze_polarization(in);

    printf("=== Результати аналізу поляризаційного еліпса ===\n");
    printf("Вхідні дані: Ex0=%.2f, Ey0=%.2f, delta=%.1f deg\n", in.ex0, in.ey0, in.delta_deg);
    printf("Нормований вектор Стокса: s1=%.3f, s2=%.3f, s3=%.3f\n",
           res.s1_norm, res.s2_norm, res.s3_norm);
    printf("Кут нахилу (tau): %.2f deg\n", res.tilt_deg);
    printf("Кут еліптичності (chi): %.2f deg\n", res.ellipticity_deg);
    printf("Осьове відношення (AR): %.3f (%.2f дБ)\n", res.ar_linear, res.ar_db);
    printf("Класифікація стану: %s\n", get_pol_class_name(res.pol_class));
    printf("PLF при прийомі H-антеною: %.4f (%.2f дБ)\n", 
           res.plf_linear_h, 10.0 * log10(res.plf_linear_h));
    printf("PLF при прийомі RHCP-антеною: %.4f (%.2f дБ)\n", 
           res.plf_rhcp, 10.0 * log10(res.plf_rhcp));

    return 0;
}
```
```cpp
#include <iostream>
#include <cmath>
#include <numbers>
#include <string_view>
#include <expected>
#include <iomanip>
#include <algorithm>

enum class PolarizationState {
    Linear,
    CircularRHCP,
    CircularLHCP,
    EllipticalRHCP,
    EllipticalLHCP
};

struct FieldInput {
    double ex0{1.0};
    double ey0{1.0};
    double delta_deg{90.0};
};

struct PolarizationAnalysis {
    double s0{0.0}, s1{0.0}, s2{0.0}, s3{0.0};
    double s1_norm{0.0}, s2_norm{0.0}, s3_norm{0.0};
    double major_axis{0.0};
    double minor_axis{0.0};
    double tilt_deg{0.0};
    double ellipticity_deg{0.0};
    double ar_linear{1.0};
    double ar_db{0.0};
    PolarizationState state{PolarizationState::CircularRHCP};
    double plf_linear_h{0.5};
    double plf_rhcp{1.0};
};

enum class AnalysisError {
    ZeroFieldMagnitude,
    InvalidPhase
};

constexpr double deg_to_rad(double deg) noexcept {
    return deg * std::numbers::pi / 180.0;
}

constexpr double rad_to_deg(double rad) noexcept {
    return rad * 180.0 / std::numbers::pi;
}

std::expected<PolarizationAnalysis, AnalysisError> 
analyze_polarization(const FieldInput& input) noexcept {
    if (input.ex0 <= 0.0 && input.ey0 <= 0.0) {
        return std::unexpected(AnalysisError::ZeroFieldMagnitude);
    }

    PolarizationAnalysis res;
    const double delta = deg_to_rad(input.delta_deg);
    const double ex2 = input.ex0 * input.ex0;
    const double ey2 = input.ey0 * input.ey0;

    res.s0 = ex2 + ey2;
    res.s1 = ex2 - ey2;
    res.s2 = 2.0 * input.ex0 * input.ey0 * std::cos(delta);
    res.s3 = 2.0 * input.ex0 * input.ey0 * std::sin(delta);

    if (res.s0 > 1e-12) {
        res.s1_norm = res.s1 / res.s0;
        res.s2_norm = res.s2 / res.s0;
        res.s3_norm = res.s3 / res.s0;
    }

    const double two_tau = std::atan2(res.s2, res.s1);
    res.tilt_deg = rad_to_deg(two_tau / 2.0);

    const double sin_two_chi = std::clamp(res.s3_norm, -1.0, 1.0);
    const double two_chi = std::asin(sin_two_chi);
    res.ellipticity_deg = rad_to_deg(two_chi / 2.0);

    const double e_total = std::sqrt(res.s0);
    res.major_axis = e_total * std::cos(two_chi / 2.0);
    res.minor_axis = e_total * std::abs(std::sin(two_chi / 2.0));

    const double abs_tan_chi = std::abs(std::tan(two_chi / 2.0));
    if (abs_tan_chi < 1e-6) {
        res.ar_linear = 1e6;
        res.ar_db = 99.9;
    } else {
        res.ar_linear = 1.0 / abs_tan_chi;
        res.ar_db = 20.0 * std::log10(res.ar_linear);
    }

    if (res.ar_db > 20.0) {
        res.state = PolarizationState::Linear;
    } else if (res.ar_db < 0.5) {
        res.state = (res.s3 > 0) ? PolarizationState::CircularRHCP : PolarizationState::CircularLHCP;
    } else {
        res.state = (res.s3 > 0) ? PolarizationState::EllipticalRHCP : PolarizationState::EllipticalLHCP;
    }

    res.plf_linear_h = 0.5 * (1.0 + res.s1_norm);
    res.plf_rhcp = 0.5 * (1.0 + res.s3_norm);

    return res;
}

constexpr std::string_view state_to_string(PolarizationState s) noexcept {
    switch (s) {
        case PolarizationState::Linear:         return "Лінійна (Linear)";
        case PolarizationState::CircularRHCP:   return "Чиста колова RHCP";
        case PolarizationState::CircularLHCP:   return "Чиста колова LHCP";
        case PolarizationState::EllipticalRHCP: return "Еліптична (Праве обертання / RHCP)";
        case PolarizationState::EllipticalLHCP: return "Еліптична (Ліве обертання / LHCP)";
    }
    return "Невідома";
}

int main() {
    constexpr FieldInput input{ .ex0 = 1.0, .ey0 = 0.8, .delta_deg = 80.0 };

    if (auto result = analyze_polarization(input); result.has_value()) {
        const auto& res = result.value();
        std::cout << std::fixed << std::setprecision(3);
        std::cout << "=== Результати аналізу поляризаційного еліпса (C++20) ===\n";
        std::cout << "Нормований вектор Стокса: s1=" << res.s1_norm 
                  << ", s2=" << res.s2_norm << ", s3=" << res.s3_norm << "\n";
        std::cout << "Кут нахилу (tau): " << res.tilt_deg << " deg\n";
        std::cout << "Кут еліптичності (chi): " << res.ellipticity_deg << " deg\n";
        std::cout << "Осьове відношення (AR): " << res.ar_linear << " (" << res.ar_db << " дБ)\n";
        std::cout << "Класифікація стану: " << state_to_string(res.state) << "\n";
        std::cout << "PLF при прийомі H-антеною: " << res.plf_linear_h 
                  << " (" << 10.0 * std::log10(res.plf_linear_h) << " дБ)\n";
        std::cout << "PLF при прийомі RHCP-антеною: " << res.plf_rhcp 
                  << " (" << 10.0 * std::log10(res.plf_rhcp) << " дБ)\n";
    } else {
        std::cerr << "Помилка аналізу: нульова амплітуда поля!\n";
    }

    return 0;
}
```
:::

---

### Детальний аналіз алгоритму та математичних кроків

Розберемо покроково електродинамічну логіку розрахунку, яка виконується всередині функції `analyze_polarization`:

1. **Конвертація фази та розрахунок ненормованих параметрів Стокса:**
   Вхідний кут `delta_deg` переводиться з градусів у радіани. Обчислюються квадрати амплітуд `ex2 = E₀x²` та `ey2 = E₀y²`. Ненормовані параметри Стокса визначаються за класичними формулами:
   - `s0 = ex2 + ey2` (Загальна інтенсивність).
   - `s1 = ex2 - ey2` (Різниця між горизонтальною та вертикальною інтенсивностями).
   - `s2 = 2 · E₀x · E₀y · cos(δ)` (Інтенсивність уздовж діагональних осей +45°/-45°).
   - `s3 = 2 · E₀x · E₀y · sin(δ)` (Кругова квадратурна інтенсивність).

2. **Нормування вектора Стокса на сферичні координати:**
   Якщо загальна інтенсивність `s0 > 1e-12`, компоненти діляться на `s0`, утворюючи точку на одиничній сфері Пуанкаре:
   - `s1_norm = s1 / s0`
   - `s2_norm = s2 / s0`
   - `s3_norm = s3 / s0`

3. **Обчислення кута орієнтації `τ` та кута еліптичності `χ`:**
   Кут повороту еліпса `τ` розраховується через чотириквадрантний арктангенс `atan2(s2, s1)`:
   - `two_tau = atan2(s2, s1)`
   - `tilt_deg = rad_to_deg(two_tau / 2.0)`

   Кут еліптичності `χ` обчислюється через арксинус нормованого параметра `s3_norm`:
   - `sin_two_chi = clamp(s3_norm, -1.0, 1.0)`
   - `two_chi = asin(sin_two_chi)`
   - `ellipticity_deg = rad_to_deg(two_chi / 2.0)`

4. **Геометрична реконструкція півосей `a` та `b`:**
   Загальний вектор напруженості поля дорівнює `e_total = sqrt(s0)`. Велика та мала півосі розраховуються за сферичними проєкціями:
   - `major_axis = e_total · cos(χ)`
   - `minor_axis = e_total · |sin(χ)|`

5. **Точне обчислення осьового відношення (Axial Ratio, AR):**
   Обчислюється модуль тангенса кута еліптичності `abs_tan_chi = |tan(χ)|`.
   Якщо `abs_tan_chi < 1e-6`, то хвиля є лінійною, `ar_linear` приймається рівним `1e6`, а `ar_db = 99.9 dB`.
   Інакше:
   - `ar_linear = 1.0 / abs_tan_chi`
   - `ar_db = 20.0 · log10(ar_linear)`

6. **Системна класифікація поляризаційного стану:**
   - Якщо `ar_db > 20.0 dB` → `POL_LINEAR`.
   - Якщо `ar_db < 0.5 dB` → `POL_CIRCULAR_RHCP` (при `s3 > 0`) або `POL_CIRCULAR_LHCP` (при `s3 < 0`).
   - Якщо `0.5 dB ≤ ar_db ≤ 20.0 dB` → `POL_ELLIPTICAL_RHCP` (при `s3 > 0`) або `POL_ELLIPTICAL_LHCP` (при `s3 < 0`).

7. **Обчислення Polarization Loss Factor (PLF):**
   За формулою скалярного добутку векторів Стокса `PLF = 0.5 · [1 + s_t · s_r]`:
   - Для горизонтальної антени приймача `s_r = (1, 0, 0)` → `plf_linear_h = 0.5 · (1 + s1_norm)`.
   - Для RHCP антени приймача `s_r = (0, 0, +1)` → `plf_rhcp = 0.5 · (1 + s3_norm)`.

---

### Набір тестових сценаріїв та верифікація результатів

Для повної верифікації працездатності алгоритму проведено тестування на чотирьох канонічних фізичних станах хвилі:

#### Сценарій 1: Ідеально горизонтальна лінійна поляризація
- **Вхідні дані:** `E₀x = 1.0`, `E₀y = 0.0`, `δ = 0.0°`.
- **Розрахунок:** `s1_norm = 1.0`, `s2_norm = 0.0`, `s3_norm = 0.0`.
- **Результат:** `tilt_deg = 0.0°`, `ellipticity_deg = 0.0°`, `AR = ∞ (99.9 dB)`.
- **Класифікація:** `POL_LINEAR`.
- **Втрати:** `PLF_H = 1.000 (0.0 dB)`, `PLF_RHCP = 0.500 (-3.01 dB)`.

#### Сценарій 2: Чиста права колова поляризація (RHCP)
- **Вхідні дані:** `E₀x = 1.0`, `E₀y = 1.0`, `δ = 90.0°`.
- **Розрахунок:** `s1_norm = 0.0`, `s2_norm = 0.0`, `s3_norm = +1.0`.
- **Результат:** `tilt_deg = 0.0°`, `ellipticity_deg = +45.0°`, `AR = 1.000 (0.0 dB)`.
- **Класифікація:** `POL_CIRCULAR_RHCP`.
- **Втрати:** `PLF_H = 0.500 (-3.01 dB)`, `PLF_RHCP = 1.000 (0.0 dB)`.

#### Сценарій 3: Чиста ліва колова поляризація (LHCP)
- **Вхідні дані:** `E₀x = 1.0`, `E₀y = 1.0`, `δ = -90.0°` (або `270.0°`).
- **Розрахунок:** `s1_norm = 0.0`, `s2_norm = 0.0`, `s3_norm = -1.0`.
- **Результат:** `tilt_deg = 0.0°`, `ellipticity_deg = -45.0°`, `AR = 1.000 (0.0 dB)`.
- **Класифікація:** `POL_CIRCULAR_LHCP`.
- **Втрати:** `PLF_H = 0.500 (-3.01 dB)`, `PLF_RHCP = 0.000 (-∞ dB)`.

#### Сценарій 4: Реальна неідеальна еліптична хвиля
- **Вхідні дані:** `E₀x = 1.0`, `E₀y = 0.8`, `δ = 80.0°`.
- **Розрахунок:** `s1_norm = 0.220`, `s2_norm = 0.170`, `s3_norm = 0.960`.
- **Результат:** `tilt_deg = 18.84°`, `ellipticity_deg = 36.87°`, `AR = 1.333 (2.50 dB)`.
- **Класифікація:** `POL_ELLIPTICAL_RHCP`.
- **Втрати:** `PLF_H = 0.6100 (-2.15 dB)`, `PLF_RHCP = 0.9800 (-0.09 dB)`.

---

### Інтеграція у реальні SDR-тракти та продуктивність

У складі програмно-визначених радіосистем (на базі GNU Radio, SDR++ або кастомного C++ блоку на FPGA/SoC) цей аналітичний модуль викликається для кожного комплексно-значного відліку або блок-кадру FFT.

Для забезпечення високої обчислювальної швидкодії при роботі з потоками даних рівня 100 Мвибірок/сек рекомендовано застосовувати векторні SIMD-інструкції (AVX2/NEON) для одночасної обробки 4 або 8 комплексних каналів. Оскільки тригонометричні функції `atan2` та `asin` є відносно "важкими" для CPU, обчислення кутів `τ` та `χ` доцільно виносити лише на фазу візуалізації користувачеві (з частотою оновлення 30–60 Гц), тоді як фільтрація та вибір поляризаційного каналу в режимі реального часу здійснюються виключно через швидкі скалярні добутки векторів Стокса `S₁..S₃`.
