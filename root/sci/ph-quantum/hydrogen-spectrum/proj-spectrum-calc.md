# ⚙️ Програмування розрахунку спектральних ліній та тонкої структури

Ця практична вставка містить алгоритмічну реалізацію розрахунку спектральних ліній водню та воднеподібних іонів, обчислення ізотопічного зсуву між протієм та дейтерієм, перерахунок довжин хвиль між вакуумом і стандартним повітрям та розрахунок релятивістського розщеплення рівнів.

У чисельному моделюванні атомної спектроскопії виникає низка специфічних обчислювальних задач. Оскільки спектральні лінії вимірюються з експериментальною точністю до дев'яти-дванадцяти значущих цифр, обчислювальні алгоритми повинні суворо дотримуватися стандартів плаваючої коми подвійної точності (`double`, IEEE 754) або підвищеної точності (`long double`). Просте обчислення за формулою Рідберга без урахування ефектів скороченої маси ядра чи показника заломлення повітря призводить до систематичних похибок, які у сотні разів перевищують роздільну здатність сучасних спектрометрів.

## 1. Алгоритмічні задачі та фізична модель

Алгоритм спектрального калькулятора розв'язує чотири послідовні задачі:

1. **Корекція скороченої маси для ізотопів**: оскільки стала Рідберга `R_M = R_∞ / (1 + m_e / M)` залежить від маси ядра `M`, програма динамічно обчислює ефективну константу Рідберга для заданого нукліда (`¹H`, `²H`, `³H`, `³He⁺`, `⁴He⁺`, `⁶Li²⁺`). Маси ядер беруться за даними CODATA у кілограмах або перераховуються з атомних одиниць маси (`а.о.м.`, `1 а.о.м. ≈ 1.66053906660 × 10⁻²⁷ кг`).
2. **Перехід між вакуумними та повітряними довжинами хвиль**: астрономічні спостереження та лабораторні вимірювання зазвичай проводяться у стандартному повітрі (температура 15 °C, тиск 101325 Па, сухе повітря з вмістом `CO₂` 0.04%). Перерахунок виконується за модифікованою формулою Едлена для показника заломлення повітря `n(λ)`:

```
n(λ) - 1 = 10⁻⁸ · [8342.54 + 2406147 / (130 - σ²) + 15998 / (38.9 - σ²)]
```

де `σ = 1000 / λ_vac` — хвильове число у мікронах⁻¹ (`мкм⁻¹`).

3. **Релятивістська тонка структура**: розрахунок зсуву енергетичних рівнів `E_{n, j}` за наближеною формулою Зоммерфельда — Дірака для оцінки розщеплення дублетів `2P_3/2 - 2S_1/2`.
4. **Валідація квантових чисел**: перевірка фізичної допустимості вхідних параметрів (головні квантові числа `n₁ ≥ 1`, `n₂ > n₁`, атомний номер `Z ≥ 1`).

## 2. Поетапний розбір архітектури коду

Програма розроблена у двох варіантах реалізації — C (ISO C99) та C++ (ISO C++23).

### Аналіз реалізації мовою C

У реалізації мовою C основою структури даних є типи `HydrogenIsotope` та `SpectralLineResult`.

- Функція `get_reduced_rydberg()` приймає масу ядра `nuclear_mass_kg` та атомний номер `Z`. Вона обчислює коефіцієнт скороченої маси `μ / m_e = 1 / (1 + m_e / M)` і множить його на базову константу Рідберга `CONST_R_INF` та квадрат атомного номера `Z²`.
- Функція `air_refractive_index()` обчислює коефіцієнт заломлення `n_air` за формулою Едлена. Якщо вхідне значення `lambda_vac_nm` дорівнює нулю або є від'ємним, функція повертає `1.0` (вакуумний режим) для запобігання діленню на нуль.
- Функція `compute_spectral_line()` є головним розрахунковим модулем. Вона виконує первинну валідацію вхідних вказівників та квантових чисел (`n1 > 0`, `n2 > n1`). Після розрахунку вакуумної довжини хвилі у метрах `lambda_vac_m = 1 / wavenumber` відбувається її переведення у нанометри (`10⁹ нм/м`), розрахунок повітряної довжини хвилі `lambda_air_nm = lambda_vac_nm / n_air` та обчислення енергії фотона в електронвольтах `E_eV = (h · c / λ) / e`.
- Функція `dirac_fine_structure_shift_ev()` обчислює релятивістський зсув енергетичного рівня `E_{n,j}` за формулою Дірака. Вона враховує сталу тонкої структури `α ≈ 1/137.036` та повний момент імпульсу `j`.

### Аналіз реалізації мовою C++

У C++23 версії алгоритм оформлено у вигляді простору імен `quantum` та класу `SpectrumCalculator`.

- Константи визначено як static constexpr double значення, що дозволяє виконувати розрахунок сталі Рідберга та квантових коефіцієнтів під час компіляції (`constexpr`).
- Замість сирих вказівників та числових кодів помилок C++ функція `compute_line()` повертає `std::expected<SpectralLine, SpectralError>`. Якщо вхідні квантові числа порушують фізичні обмеження, функція повертає об'єкт `std::unexpected(SpectralError::InvalidQuantumNumbers)` без викидання винятків (zero-overhead error handling).
- Тип `std::string_view` використовується для імен ізотопів, що виключає виділення динамічної пам'яті в купі (`heap allocation`).
- Результат обчислення повертає розкриту структуру `SpectralLine` за допомогою агрегатної ініціалізації C++20 (`designated initializers`).

## 3. Джерельний код реалізації (C та C++)

Нижче наведено вихідні тексти обох реалізацій, які можна зкомпілювати будь-яким стандартним компілятором (`gcc -std=c99 -O2` або `g++ -std=c++23 -O2`).

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

/* Фундаментальні фізичні константи (CODATA) */
#define CONST_R_INF     10973731.568160  /* Стала Рідберга для нескінченної маси (м⁻¹) */
#define CONST_MASS_E    9.1093837015e-31 /* Маса електрона (кг) */
#define CONST_MASS_P    1.67262192369e-27/* Маса протона (кг) */
#define CONST_MASS_D    3.3435837724e-27 /* Маса дейтерону (кг) */
#define CONST_ALPHA     7.2973525693e-3  /* Стала тонкої структури α ≈ 1/137 */
#define CONST_C         299792458.0      /* Швидкість світла у вакуумі (м/с) */
#define CONST_EV_JOULE  1.602176634e-19  /* Джоулів у 1 еВ */
#define CONST_PLANCK    6.62607015e-34   /* Стала Планка h (Дж·с) */

typedef struct {
    const char *name;
    double nuclear_mass_kg;
    int Z;
} HydrogenIsotope;

typedef struct {
    int n1;
    int n2;
    double wavelength_vac_nm;
    double wavelength_air_nm;
    double energy_ev;
} SpectralLineResult;

/* Обчислення ефективної сталої Рідберга з урахуванням маси ядра */
double get_reduced_rydberg(double nuclear_mass_kg, int Z) {
    double reduced_mass_ratio = 1.0 / (1.0 + CONST_MASS_E / nuclear_mass_kg);
    return CONST_R_INF * ((double)Z * (double)Z) * reduced_mass_ratio;
}

/* Формула Едлена для показника заломлення стандартного повітря */
double air_refractive_index(double lambda_vac_nm) {
    if (lambda_vac_nm <= 0.0) return 1.0;
    double sigma = 1000.0 / lambda_vac_nm; /* Хвильове число в мкм⁻¹ */
    double s2 = sigma * sigma;
    double n_minus_1 = 1.0e-8 * (8342.54 + 2406147.0 / (130.0 - s2) + 15998.0 / (38.9 - s2));
    return 1.0 + n_minus_1;
}

/* Обчислення параметрів спектральної лінії між рівнями n1 та n2 */
int compute_spectral_line(const HydrogenIsotope *iso, int n1, int n2, SpectralLineResult *out_line) {
    if (!iso || !out_line || n1 <= 0 || n2 <= n1) {
        return -1;
    }

    double R_eff = get_reduced_rydberg(iso->nuclear_mass_kg, iso->Z);
    double wavenumber = R_eff * (1.0 / ((double)n1 * n1) - 1.0 / ((double)n2 * n2));

    if (wavenumber <= 0.0) return -2;

    double lambda_vac_m = 1.0 / wavenumber;
    double lambda_vac_nm = lambda_vac_m * 1.0e9;
    double n_air = air_refractive_index(lambda_vac_nm);
    double lambda_air_nm = lambda_vac_nm / n_air;

    double energy_j = wavenumber * CONST_PLANCK * CONST_C;
    double energy_ev = energy_j / CONST_EV_JOULE;

    out_line->n1 = n1;
    out_line->n2 = n2;
    out_line->wavelength_vac_nm = lambda_vac_nm;
    out_line->wavelength_air_nm = lambda_air_nm;
    out_line->energy_ev = energy_ev;

    return 0;
}

/* Релятивістський зсув Дірака для стану (n, j) у електронвольтах */
double dirac_fine_structure_shift_ev(int Z, int n, double j) {
    if (n <= 0 || j < 0.5) return 0.0;
    
    double Z_alpha = (double)Z * CONST_ALPHA;
    double Z_alpha2 = Z_alpha * Z_alpha;
    double E_n = -13.605693 * ((double)(Z * Z) / ((double)(n * n)));
    double factor = (Z_alpha2 / ((double)n)) * ((1.0 / (j + 0.5)) - (0.75 / (double)n));
    
    return E_n * factor;
}

int main(void) {
    HydrogenIsotope protium = {"Протій (1H)", CONST_MASS_P, 1};
    HydrogenIsotope deuterium = {"Дейтерій (2H)", CONST_MASS_D, 1};

    printf("=== Спектральні лінії серії Бальмера (C) ===\n\n");
    printf("%-15s %-6s %-14s %-14s %-12s\n", "Ізотоп", "Перехід", "λ вак (нм)", "λ повітря (нм)", "ΔE (еВ)");
    printf("--------------------------------------------------------------------\n");

    for (int n2 = 3; n2 <= 6; ++n2) {
        SpectralLineResult res_h, res_d;
        if (compute_spectral_line(&protium, 2, n2, &res_h) == 0 &&
            compute_spectral_line(&deuterium, 2, n2, &res_d) == 0) {
            
            printf("%-15s %d -> %d  %-14.4f %-14.4f %-12.4f\n", 
                   protium.name, res_h.n1, res_h.n2, res_h.wavelength_vac_nm, res_h.wavelength_air_nm, res_h.energy_ev);
            printf("%-15s %d -> %d  %-14.4f %-14.4f %-12.4f\n", 
                   deuterium.name, res_d.n1, res_d.n2, res_d.wavelength_vac_nm, res_d.wavelength_air_nm, res_d.energy_ev);
            
            double shift_pm = (res_h.wavelength_vac_nm - res_d.wavelength_vac_nm) * 1000.0;
            printf("  └─ Ізотопічний зсув H-D: %.2f пм (%.4f нм)\n\n", shift_pm, shift_pm / 1000.0);
        }
    }

    printf("\n=== Тонке розщеплення рівня n = 2 в атомі водню ===\n");
    double shift_2s12 = dirac_fine_structure_shift_ev(1, 2, 0.5);
    double shift_2p32 = dirac_fine_structure_shift_ev(1, 2, 1.5);
    printf("Зсув рівня 2S_1/2 (j = 1/2): %+.6e еВ\n", shift_2s12);
    printf("Зсув рівня 2P_3/2 (j = 3/2): %+.6e еВ\n", shift_2p32);
    printf("Тонкий інтервал 2P_3/2 - 2S_1/2: %.6e еВ (%.2f МГц)\n", 
           fabs(shift_2p32 - shift_2s12), fabs(shift_2p32 - shift_2s12) * CONST_EV_JOULE / (CONST_PLANCK * 1e6));

    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <string_view>
#include <cmath>
#include <iomanip>
#include <expected>
#include <optional>

namespace quantum {

struct Isotope {
    std::string_view name;
    double nuclear_mass_kg;
    int atomic_number;
};

struct SpectralLine {
    int n1;
    int n2;
    double wavelength_vac_nm;
    double wavelength_air_nm;
    double energy_ev;
};

enum class SpectralError {
    InvalidQuantumNumbers,
    CalculationOverflow
};

class SpectrumCalculator {
public:
    static constexpr double R_INF = 10973731.568160;  // м⁻¹
    static constexpr double MASS_E = 9.1093837015e-31; // кг
    static constexpr double MASS_P = 1.67262192369e-27;// кг
    static constexpr double MASS_D = 3.3435837724e-27; // кг
    static constexpr double ALPHA = 7.2973525693e-3;   // α ≈ 1/137
    static constexpr double SPEED_OF_LIGHT = 299792458.0; // м/с
    static constexpr double EV_TO_JOULE = 1.602176634e-19;
    static constexpr double PLANCK_H = 6.62607015e-34;

    [[nodiscard]] static constexpr double get_reduced_rydberg(const Isotope& iso) noexcept {
        const double mu_ratio = 1.0 / (1.0 + MASS_E / iso.nuclear_mass_kg);
        const double z = static_cast<double>(iso.atomic_number);
        return R_INF * (z * z) * mu_ratio;
    }

    [[nodiscard]] static double calculate_air_refractive_index(double lambda_vac_nm) noexcept {
        if (lambda_vac_nm <= 0.0) return 1.0;
        const double sigma = 1000.0 / lambda_vac_nm;
        const double s2 = sigma * sigma;
        const double n_minus_1 = 1.0e-8 * (8342.54 + 2406147.0 / (130.0 - s2) + 15998.0 / (38.9 - s2));
        return 1.0 + n_minus_1;
    }

    [[nodiscard]] static std::expected<SpectralLine, SpectralError> 
    compute_line(const Isotope& iso, int n1, int n2) noexcept {
        if (n1 <= 0 || n2 <= n1) {
            return std::unexpected(SpectralError::InvalidQuantumNumbers);
        }

        const double r_eff = get_reduced_rydberg(iso);
        const double wavenumber = r_eff * (1.0 / (static_cast<double>(n1 * n1)) - 1.0 / (static_cast<double>(n2 * n2)));

        if (wavenumber <= 0.0) {
            return std::unexpected(SpectralError::CalculationOverflow);
        }

        const double lambda_vac_nm = (1.0 / wavenumber) * 1.0e9;
        const double n_air = calculate_air_refractive_index(lambda_vac_nm);
        const double lambda_air_nm = lambda_vac_nm / n_air;
        const double energy_ev = (wavenumber * PLANCK_H * SPEED_OF_LIGHT) / EV_TO_JOULE;

        return SpectralLine{
            .n1 = n1,
            .n2 = n2,
            .wavelength_vac_nm = lambda_vac_nm,
            .wavelength_air_nm = lambda_air_nm,
            .energy_ev = energy_ev
        };
    }

    [[nodiscard]] static constexpr double 
    fine_structure_shift_ev(int z, int n, double j) noexcept {
        if (n <= 0 || j < 0.5) return 0.0;
        const double z_double = static_cast<double>(z);
        const double z_alpha = z_double * ALPHA;
        const double e_n = -13.605693 * ((z_double * z_double) / static_cast<double>(n * n));
        const double factor = ((z_alpha * z_alpha) / static_cast<double>(n)) * 
                              ((1.0 / (j + 0.5)) - (0.75 / static_cast<double>(n)));
        return e_n * factor;
    }
};

} // namespace quantum

int main() {
    using namespace quantum;

    constexpr Isotope protium{"Протій (1H)", SpectrumCalculator::MASS_P, 1};
    constexpr Isotope deuterium{"Дейтерій (2H)", SpectrumCalculator::MASS_D, 1};

    std::cout << std::fixed << std::setprecision(4);
    std::cout << "=== Спектральні лінії серії Бальмера (C++23) ===\n\n";

    for (int n2 = 3; n2 <= 6; ++n2) {
        auto res_h = SpectrumCalculator::compute_line(protium, 2, n2);
        auto res_d = SpectrumCalculator::compute_line(deuterium, 2, n2);

        if (res_h && res_d) {
            std::cout << protium.name << " " << res_h->n1 << "->" << res_h->n2 
                      << " | λ_vac: " << res_h->wavelength_vac_nm << " нм"
                      << " | λ_air: " << res_h->wavelength_air_nm << " нм\n";
            std::cout << deuterium.name << " " << res_d->n1 << "->" << res_d->n2 
                      << " | λ_vac: " << res_d->wavelength_vac_nm << " нм"
                      << " | λ_air: " << res_d->wavelength_air_nm << " нм\n";
            
            const double shift_pm = (res_h->wavelength_vac_nm - res_d->wavelength_vac_nm) * 1000.0;
            std::cout << "  └─ Ізотопічний зсув H-D: " << shift_pm << " пм\n\n";
        }
    }

    return 0;
}
```
:::

## 4. Детальний аналіз крайових випадків та похибок обчислень

Під час проектування спектральних алгоритмів необхідно враховувати фізичні та числові граничні умови:

1. **Крайовий випадок високих квантових чисел (`n₂ → ∞`)**: при розрахунку границь спектральних серій (Рідбергівські стани з `n₂ > 100`) різниця енергій наближається до енергії іонізації. У програмах формулу `1/n₂²` необхідно обчислювати першою, щоб уникнути втрати значущих розрядів від віднімання близьких чисел (катастрофічна втрата точності при `1/n₁² - 1/n₂²`).
2. **Воднеподібні багатозарядні іони (`Z > 1`)**: для іонів `He⁺` (`Z = 2`), `Li²⁺` (`Z = 3`) або високозарядних важких іонів (наприклад, `U⁹¹⁺` з `Z = 92`) параметр `Z·α` досягає значень порядка `0.67`. У цьому випадку наближена формула Зоммерфельда втрачає точність, і необхідно застосовувати точний релятивістський вираз Дірака з вищими степенями `(Z·α)⁴` та квантово-електродинамічними радіаційними поправками (Self-Energy та Vacuum Polarization).
3. **Температурна та тискова залежність показника заломлення**: формула Едлена, використана у функції `air_refractive_index`, розрахована на метеорологічний стандарт (15 °C, 101325 Па). Для спостережень у гірських обсерваторіях або у вакуумних спектрографах необхідно вносити розрахунок густини повітря через рівняння стану ідеального газу з урахуванням тиску водяної пари.
4. **Обчислювальна складність та сумісність**: утиліти на C++ дозволяють обчислювати константи `constexpr` під час компіляції, що повністю виключає накладні витрати у runtime при збірці спектральних таблиць.
5. **Одиниця вимірювання та перетворення числових типів**: при проведенні спектральних обчислень для астрофізичних застосувань часто вимагається конвертація довжин хвиль з нанометрів у ангстреми (`1 нм = 10 Å`) або у частоти у гігагерцах (`Гц`). Усі математичні множення слід проводити в системі СІ з кінцевим переведенням у заданий формат виводу, що виключає накопичення похибок заокруглення при проміжних перетвореннях.
