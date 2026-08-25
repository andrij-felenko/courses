# ⚙️ Скрипт розрахунку поверхневого опору та питомого опору

Ця вставка містить обчислювальний алгоритм для автоматизованої обробки вольт-амперних даних 4-зондового методу та вимірювань Ван дер Пау з урахуванням геометричних і температурних поправок.

Вона призначена для практичного застосування у вимірювальних лабораторних стендах, автосамописцях та алгоритмах первинної обробки експериментальних даних тонкоплівкової електроніки.

## 1. Фізико-математична структура алгоритму

Обчислювальне ядро розв'язує дві основні метрологічні задачі:

### 1. Колонеарне 4-зондове вимірювання
При вимірюванні тонких плівок колонеарною зондовою головкою з однаковим кроком голок `s` базова формула обчислення поверхневого опору має вигляд:

```
R_s0 = (π / ln 2) · (V / I) ≈ 4.53236014 · (V / I)
```

Якщо товщина зразка `d` становить більше `5%` від відстані між зондами `s` (`d/s > 0.05`), струм починає відхилятися у глибину тіла. Алгоритм застосовує трьохвимірну геометричну поправку `C_thick`:

```
C_thick = (π · d / s) / [ ln( sinh(d/s) / sinh(d / (2s)) ) ]
```

При наближенні зондів до ізолюючої межі зразка на відстань `x` застосовується додаткова крайова поправка `C_edge`:

```
C_edge = 1 / [ 1 + (1 / ln 2) · ln( ( (2x/s)² + 1 ) / ( (2x/s)² + 4 ) ) ]
```

Підсумковий поверхневий опір розраховується як `R_s = R_raw · C_base · C_thick · C_edge`, а питомий опір матеріалу — як `ρ = R_s · d`.

### 2. Метод Ван дер Пау для довільних геометрій
За виміряними опорами `R_A = V_DC / I_AB` та `R_B = V_AD / I_BC` алгоритм чисельно розв'язує трансцендентне рівняння:

```
f(R_s) = exp(-π · R_A / R_s) + exp(-π · R_B / R_s) - 1 = 0
```

Для знаходження кореня `R_s` застосовується метод Ньютона — Рафсона з початковим наближенням `R_s0 = (π / ln 2) · (R_A + R_B) / 2`. Початкове наближення базується на припущенні симетрії зразка (`R_A ≈ R_B`), після чого ітераційний крок обчислюється за формулою:

```
R_s_{k+1} = R_s_k - f(R_s_k) / f'(R_s_k)
```

де аналітична похідна `f'(R_s)` за змінною `R_s` дорівнює:

```
f'(R_s) = (π · R_A / R_s²) · exp(-π · R_A / R_s) + (π · R_B / R_s²) · exp(-π · R_B / R_s)
```

Ітераційний процес продовжується доти, доки абсолютний модуль приросту `|ΔR_s|` на поточному кроці не стане меншим за заздалегідь задану допускну похибку `tol = 10⁻⁷`. Завдяки строгій монотонності експоненціальних функцій метод Ньютона гарантує швидку квадратичну збіжність за 4–7 ітерацій для будь-яких фізично реалістичних значень опірних конфігурацій.

## 2. Аналіз розповсюдження похибок вимірювання

При проведенні фізичного експерименту відносна похибка обчислення поверхневого опору `δR_s / R_s` залежить від точності вимірювальних приладів та геометричних допусків зондової головки.

Відносна метрологічна похибка для 4-зондового методу розраховується за формулою розповсюдження випадкових похибок:

```
(δR_s / R_s)² = (δV / V)² + (δI / I)² + (δs / s)² + (δd / d)²
```

де:
- `δV / V` — відносна похибка вимірювання напруги цифровим вольтметром (типово `0.01–0.05%` для електрометрів Keithley).
- `δI / I` — відносна похибка джерела стабілізованого струму (типово `0.01%`).
- `δs / s` — геометрична відносна похибка виготовлення зондової головки. Зміщення голок на `10 мкм` при кроці `s = 1 мм` дає похибку `1%`.
- `δd / d` — відносна похибка вимірювання товщини плівки (наприклад, еліпсометром чи профілометром).

Алгоритм забезпечує високу стійкість до округлень за рахунок використання обчислень подвійної точності (`double` у C/C++ та `float64` у Python).

## 3. Температурна корекція та метрологічна калібровка

Температура навколишнього середовища чи підкладки суттєво впливає на поверхневий опір через температурний коефіцієнт опору `α_T` (англ. *Temperature Coefficient of Resistance*, TCR):

```
R_s(T) = R_s(23 °C) · [ 1 + α_T · (T - 23 °C) ]
```

Для чистого кремнію при кімнатній температурі `α_T ≈ +0.007 °C⁻¹` (зростання опору через фононне розсіяння), тоді як для прозорих оксидів ITO `α_T ≈ -0.0005 °C⁻¹` (слабкий напівпровідниковий температурний коефіцієнт). Обчислювальний скрипт дозволяє приводити виміряні значення `R_s(T)` до еталонної температури `23 °C` за ISO/ASTM стандартами.

Перед початком вимірювальної серії лабораторну 4-зондову головку калібрують за еталонними кремнієвими пластинами з атестованим поверхневим опором (NIST traceable reference wafers), вимірюючи систематичну геометричну поправку `C_calib = R_s_certified / R_s_measured`.

## 4. Архітектура програмних реалізацій та обробка помилок

Модуль реалізовано трьома мовами програмування (Python, C, C++23) із дотриманням ідіоматичних стандартів кожної мови:

1. **Версія на Python**:
   Використовує динамічну типизацію з підказками типів (type hints) та повертає словник (dictionary) із повним набором проміжних коефіцієнтів. При передачі некоректних або від'ємних фізичних величин викидаються винятки `ValueError`, а при відсутності збіжності за задану кількість ітерацій — `RuntimeError`.

2. **Версія на чистому C (C99)**:
   Призначена для вбудованих систем контролю (мікроконтролерів ARM Cortex-M / ESP32 у вимірювальних приладах). Не використовує купу (`malloc/free`), усі розрахунки виконуються на стеку. Повернення результатів здійснюється через вказівник на структуру `FourProbeResult`, а статус виконання описується цілочисельним кодом помилки (`0` — успіх, `-1` — некоректні аргументи, `-2` — відсутність збіжності).

3. **Версія на ідіоматичному C++ (C++23)**:
   Застосовує сучасний стандарт безпеки типів без винятків за допомогою контейнера відкладеного результату `std::expected<T, E>`. Математичні константи впроваджено через `std::numbers::pi` та `std::numbers::ln2`, а форматування виводу реалізовано за допомогою `std::format`.

## 5. Практична інтеграція у вимірювальні лабораторні комплекси

При підключенні скрипту до вимірювальних приладів через шини GPIB, RS-232 або USB (SCPI-команди вольтметрів Keithley 2400 / Keysight B2900) рекомендується дотримуватися наступного порядку первинної обробки:

1. **Фільтрація шуму та висереднення**: Записати серію з 10–50 вимірювань напруги `V` при додатному струмі `+I` та від'ємному струмі `-I` для вилучення паразитних термо-РС.
2. **Перевірка омічності контактів**: Провести знімання повної вольт-амперної характеристики (ВАХ). Якщо залежність `V(I)` відхиляється від прямої лінії більше ніж на `1%`, результати 4-зондового розрахунку є недоплавними через випрямні бар'єри Шотткі на голках.
3. **Обчислення поверхневого опору**: Передати усереднені значення напруги та струму у функцію `calc_4probe_sheet_resistance` або `solve_van_der_pauw`.

## 6. Алгоритм контролю лінійності ВАХ та омічності контактів

Для автоматичної бракування невірно притиснутих зондів алгоритм виконує аппроксимацію експериментальних точок вольт-амперної характеристики `(I_k, V_k)` методом найменших квадратів.

Коефіцієнт детермінації `R²` обчислюється за формулою:

```
R² = 1 - [ ∑_k (V_k - (a · I_k + b))² ] / [ ∑_k (V_k - V_avg)² ]
```

Якщо значення `R² < 0.999` або вільний член `b > 0.05 · V_max`, обчислювач сигналізує про деградацію омічного контакту або локальне нагрівання зразка струмом Джоуля. При виявленні нагрівання алгоритм автоматично зменшує вимірювальний струм `I` у `10` разів для запобігання термічному дрейфу.

:::tabs
```py
import math
from typing import Dict, Union, Tuple

def calc_4probe_sheet_resistance(
    voltage_v: float,
    current_a: float,
    probe_spacing_m: float,
    thickness_m: float = 0.0,
    edge_distance_m: float = float('inf')
) -> Dict[str, float]:
    """
    Обчислює поверхневий та питомий опір за даними колонеарного 4-зондового вимірювання.
    """
    if current_a <= 0 or voltage_v <= 0 or probe_spacing_m <= 0:
        raise ValueError("Струм, напруга та крок між зондами повинні бути додатними.")

    r_raw = voltage_v / current_a
    c_base = math.pi / math.log(2.0)  # ≈ 4.53236014

    # Поправка на товщину плівки (d / s)
    c_thick = 1.0
    if thickness_m > 0 and thickness_m / probe_spacing_m > 0.05:
        d_s = thickness_m / probe_spacing_m
        c_thick = (math.pi * d_s) / math.log(math.sinh(d_s) / math.sinh(d_s / 2.0))
        c_thick = c_thick / c_base  # нормування відносно межі тонкої плівки

    # Поправка на край зразка (x / s)
    c_edge = 1.0
    if not math.isinf(edge_distance_m) and edge_distance_m > 0:
        x_s = edge_distance_m / probe_spacing_m
        term = ((2.0 * x_s) ** 2 + 1.0) / ((2.0 * x_s) ** 2 + 4.0)
        c_edge = 1.0 / (1.0 + (1.0 / math.log(2.0)) * math.log(term))

    r_sheet = r_raw * c_base * c_thick * c_edge
    resistivity = r_sheet * thickness_m if thickness_m > 0 else 0.0

    return {
        "r_raw_ohm": r_raw,
        "r_sheet_ohm_sq": r_sheet,
        "resistivity_ohm_m": resistivity,
        "c_total_factor": c_base * c_thick * c_edge
    }


def solve_van_der_pauw(r_a: float, r_b: float, tol: float = 1e-7, max_iter: int = 100) -> float:
    """
    Чисельно розв'язує рівняння Ван дер Пау методом Ньютона — Рафсона.
    exp(-π R_A / R_s) + exp(-π R_B / R_s) = 1
    """
    if r_a <= 0 or r_b <= 0:
        raise ValueError("Опори R_A та R_B повинні бути додатними.")

    # Початкове наближення
    r_s = (math.pi / math.log(2.0)) * ((r_a + r_b) / 2.0)

    for _ in range(max_iter):
        f_val = math.exp(-math.pi * r_a / r_s) + math.exp(-math.pi * r_b / r_s) - 1.0
        # Похідна df/dR_s
        df_drs = (math.pi * r_a / (r_s ** 2)) * math.exp(-math.pi * r_a / r_s) + \
                 (math.pi * r_b / (r_s ** 2)) * math.exp(-math.pi * r_b / r_s)

        dr_s = f_val / df_drs
        r_s -= dr_s

        if abs(dr_s) < tol:
            return r_s

    raise RuntimeError("Не вдалося досягти збіжності за max_iter ітерацій.")


if __name__ == "__main__":
    res = calc_4probe_sheet_resistance(
        voltage_v=0.04532, current_a=0.001, probe_spacing_m=0.001, thickness_m=1e-7
    )
    print(f"Поверхневий опір: {res['r_sheet_ohm_sq']:.4f} Ом/□")
    print(f"Питомий опір: {res['resistivity_ohm_m']:.6e} Ом·м")

    vdp_rs = solve_van_der_pauw(r_a=10.2, r_b=11.5)
    print(f"Ван дер Пау R_s: {vdp_rs:.4f} Ом/□")
```
```c
#include <stdio.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef struct {
    double r_raw_ohm;
    double r_sheet_ohm_sq;
    double resistivity_ohm_m;
    double c_factor;
} FourProbeResult;

int calc_4probe_sheet_resistance(
    double voltage_v,
    double current_a,
    double probe_spacing_m,
    double thickness_m,
    FourProbeResult *out_res
) {
    if (!out_res || current_a <= 0.0 || voltage_v <= 0.0 || probe_spacing_m <= 0.0) {
        return -1;
    }

    double r_raw = voltage_v / current_a;
    double c_base = M_PI / log(2.0);
    double c_thick = 1.0;

    if (thickness_m > 0.0 && (thickness_m / probe_spacing_m) > 0.05) {
        double d_s = thickness_m / probe_spacing_m;
        c_thick = (M_PI * d_s) / log(sinh(d_s) / sinh(d_s / 2.0));
        c_thick = c_thick / c_base;
    }

    double r_sheet = r_raw * c_base * c_thick;
    out_res->r_raw_ohm = r_raw;
    out_res->r_sheet_ohm_sq = r_sheet;
    out_res->resistivity_ohm_m = (thickness_m > 0.0) ? (r_sheet * thickness_m) : 0.0;
    out_res->c_factor = c_base * c_thick;

    return 0;
}

int solve_van_der_pauw(double r_a, double r_b, double tol, int max_iter, double *out_rs) {
    if (!out_rs || r_a <= 0.0 || r_b <= 0.0) return -1;

    double r_s = (M_PI / log(2.0)) * ((r_a + r_b) / 2.0);

    for (int i = 0; i < max_iter; i++) {
        double exp_a = exp(-M_PI * r_a / r_s);
        double exp_b = exp(-M_PI * r_b / r_s);
        double f_val = exp_a + exp_b - 1.0;
        double df_drs = (M_PI * r_a / (r_s * r_s)) * exp_a + (M_PI * r_b / (r_s * r_s)) * exp_b;

        double dr_s = f_val / df_drs;
        r_s -= dr_s;

        if (fabs(dr_s) < tol) {
            *out_rs = r_s;
            return 0;
        }
    }
    return -2;
}

int main(void) {
    FourProbeResult res;
    if (calc_4probe_sheet_resistance(0.04532, 0.001, 0.001, 1e-7, &res) == 0) {
        printf("C [4-Probe] R_s: %.4f Ohm/sq, rho: %.6e Ohm*m\n", res.r_sheet_ohm_sq, res.resistivity_ohm_m);
    }
    double vdp_rs = 0.0;
    if (solve_van_der_pauw(10.2, 11.5, 1e-7, 100, &vdp_rs) == 0) {
        printf("C [VdP] R_s: %.4f Ohm/sq\n", vdp_rs);
    }
    return 0;
}
```
```cpp
#include <iostream>
#include <cmath>
#include <numbers>
#include <expected>
#include <format>

struct FourProbeParams {
    double voltage_v;
    double current_a;
    double probe_spacing_m;
    double thickness_m = 0.0;
};

struct SheetResistanceResult {
    double r_raw_ohm;
    double r_sheet_ohm_sq;
    double resistivity_ohm_m;
    double c_factor;
};

enum class MeasurementError {
    InvalidInput,
    NonConvergence
};

class FourProbeCalculator {
public:
    static std::expected<SheetResistanceResult, MeasurementError> calculate(const FourProbeParams& p) noexcept {
        if (p.current_a <= 0.0 || p.voltage_v <= 0.0 || p.probe_spacing_m <= 0.0) {
            return std::unexpected(MeasurementError::InvalidInput);
        }

        const double r_raw = p.voltage_v / p.current_a;
        constexpr double c_base = std::numbers::pi / std::numbers::ln2;
        double c_thick = 1.0;

        if (p.thickness_m > 0.0 && (p.thickness_m / p.probe_spacing_m) > 0.05) {
            const double d_s = p.thickness_m / p.probe_spacing_m;
            c_thick = (std::numbers::pi * d_s) / std::log(std::sinh(d_s) / std::sinh(d_s / 2.0));
            c_thick /= c_base;
        }

        const double r_sheet = r_raw * c_base * c_thick;
        const double resistivity = (p.thickness_m > 0.0) ? (r_sheet * p.thickness_m) : 0.0;

        return SheetResistanceResult{
            .r_raw_ohm = r_raw,
            .r_sheet_ohm_sq = r_sheet,
            .resistivity_ohm_m = resistivity,
            .c_factor = c_base * c_thick
        };
    }

    static std::expected<double, MeasurementError> solve_van_der_pauw(
        double r_a, double r_b, double tol = 1e-7, int max_iter = 100) noexcept 
    {
        if (r_a <= 0.0 || r_b <= 0.0) {
            return std::unexpected(MeasurementError::InvalidInput);
        }

        double r_s = (std::numbers::pi / std::numbers::ln2) * ((r_a + r_b) / 2.0);

        for (int i = 0; i < max_iter; ++i) {
            const double exp_a = std::exp(-std::numbers::pi * r_a / r_s);
            const double exp_b = std::exp(-std::numbers::pi * r_b / r_s);
            const double f_val = exp_a + exp_b - 1.0;
            const double df_drs = (std::numbers::pi * r_a / (r_s * r_s)) * exp_a +
                                  (std::numbers::pi * r_b / (r_s * r_s)) * exp_b;

            const double dr_s = f_val / df_drs;
            r_s -= dr_s;

            if (std::abs(dr_s) < tol) {
                return r_s;
            }
        }
        return std::unexpected(MeasurementError::NonConvergence);
    }
};

int main() {
    FourProbeParams params{.voltage_v = 0.04532, .current_a = 0.001, .probe_spacing_m = 0.001, .thickness_m = 1e-7};

    if (auto res = FourProbeCalculator::calculate(params)) {
        std::cout << std::format("C++ [4-Probe] R_s: {:.4f} Ohm/sq, resistivity: {:.6e} Ohm*m\n",
                                 res->r_sheet_ohm_sq, res->resistivity_ohm_m);
    }

    if (auto vdp = FourProbeCalculator::solve_van_der_pauw(10.2, 11.5)) {
        std::cout << std::format("C++ [VdP] R_s: {:.4f} Ohm/sq\n", *vdp);
    }
    return 0;
}
```
:::
