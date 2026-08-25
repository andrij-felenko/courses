# ⚙️ Чисельне моделювання спектра квантової ефективності фотодіода

Чисельне моделювання фізичних процесів у кремнієвому p-i-n фотодіоді вираховує спектральний розподіл квантової ефективності та чутливості у діапазоні довжин хвиль від 300 нм до 1150 нм шляхом покрокового обчислення коефіцієнтів відбиття світла від поверхні, міжзонного поглинання й ефективності збору фотогенерованих носіїв заряду.

### Фізична модель та вхідні параметри

Для точного обчислення спектральної характеристики фотодетектора необхідно врахувати три послідовні фізичні етапи перетворення випромінювання:
1. **Проходження оптичної межі та відбиття**: Світло падає на поверхню кристала кремнію. Більша частина звичайного світла відбивається через високий показник заломлення кремнію (`n ≈ 3.8`), якщо поверхня не захищена тонким антивідбивальним шаром (*AR coating*). Модель обчислює коефіцієнт відбиття `R(λ)` з урахуванням інтерференційного мінімуму на заданій робочій довжині хвилі. Комплексний показник заломлення матеріалу `N = n + i·k` визначає як заломлення `n`, так і показник згасання `k`, пов'язаний із коефіцієнтом поглинання формулою `α = (4·π·k) / λ`.
2. **Міжзонне поглинання у напівпровіднику**: Оптична потужність експоненційно згасає у глибину за законом Бугера — Ламберта — Бера `I(x) = I₀ (1 - R) e⁻ᵃˣ`. Коефіцієнт поглинання кремнію `α(λ)` сильно залежить від довжини хвилі: для короткохвильового ультрафіолетового світла (300–400 нм) глибина поглинання не перевищує десятків нанометрів, тоді як ближнє інфрачервоне світло (900–1000 нм) проникає на десятки мікрометрів.
3. **Збір фотогенерованих носіїв заряду**: Носії (електрони й дірки), створені в області збіднення шириною `W`, миттєво підхоплюються сильним електричним полем і дрейфують до електродів, забезпечуючи майже стовідсоткову ефективність збору. Носії, народжені поза виснаженою зоною, повинні дістатися межі p-n переходу за рахунок дифузії; частина з них рекомбінує на дифузійній довжині `L_n`.

Підсумкова зовнішня квантова ефективність обчислюється як `EQE(λ) = (1 − R) · IQE(λ)`, а спектральна чутливість `R_λ` виражається в амперах на ват падаючої оптичної потужності.

### Архітектура чисельної моделі та реалізація

Наведений нижче код реалізує розрахунок спектральних характеристик двома мовами — C та C++. Обидва варіанти будують масив даних для спектрального діапазону від 300 нм (ультрафіолет) до 1150 нм (довжина хвилі відсічки кремнію), розраховуючи коефіцієнт відбиття, поглинання, внутрішню та зовнішню квантову ефективність і підсумкову чутливість.

Обчислення коефіцієнта поглинання спирається на напівемпіричну модель непрямих міжзонних переходів у кремнію при температурі 300 K. Модель враховує площу фоточутливого вікна, товщину активного шар `W = 20 мкм` та дифузійну довжину некорисних носіїв `L_n = 50 мкм`.

У реалізації мовою C використовується процедурний підхід із явним передаванням вказувачів та перевіркою кодів повернення. У версії C++ застосовано сучасні ідіоми C++20: безнаслідкові обгортки типів, узагальнені контейнери `std::vector`, тип `std::expected` для безпечної обробки помилок симуляції без винятків та концепт незмінності об'єктів `const / noexcept`.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define CONST_HC_EV_NM 1239.8419  /* h*c у еВ·нм */
#define SILICON_EG_EV   1.12      /* Ширина забороненої зони кремнію при 300K */

typedef struct {
    double wavelength_nm;
    double reflection_R;
    double alpha_cm1;
    double iqe;
    double eqe;
    double responsivity_a_w;
} PhotodiodeSpectrumPoint;

/* Наближений розрахунок коефіцієнта поглинання кремнію α(λ) у см⁻¹ */
static double silicon_absorption_coefficient(double lambda_nm) {
    if (lambda_nm >= 1107.0) {
        return 0.0; /* Нижче ширини забороненої зони поглинання відсутнє */
    }
    double photon_energy_ev = CONST_HC_EV_NM / lambda_nm;
    double diff = photon_energy_ev - SILICON_EG_EV;
    if (diff <= 0.0) {
        return 0.0;
    }
    /* Спрощена модель феноменологічного поглинання Si */
    return 5000.0 * diff * diff + 1e5 * pow(diff, 3.5);
}

/* Модель відбиття від поверхні з одношаровим AR-покриттям */
static double surface_reflection(double lambda_nm, double target_lambda_nm) {
    double n_si = 3.8;
    double r_bare = pow((n_si - 1.0) / (n_si + 1.0), 2.0); /* ~34% без покриття */
    
    /* Зменшення відбиття біля мінімуму AR-покриття */
    double dev = (lambda_nm - target_lambda_nm) / target_lambda_nm;
    double r_ar = r_bare * (dev * dev + 0.05);
    return (r_ar > r_bare) ? r_bare : r_ar;
}

/* Обчислення спектра квантової ефективності */
int simulate_photodiode_spectrum(
    double w_depletion_um,
    double l_diffusion_um,
    double ar_min_lambda_nm,
    PhotodiodeSpectrumPoint *out_pts,
    size_t count
) {
    if (!out_pts || count == 0) {
        return -1;
    }

    double w_cm = w_depletion_um * 1e-4;
    double ln_cm = l_diffusion_um * 1e-4;

    for (size_t i = 0; i < count; i++) {
        double lambda = 300.0 + (double)i * (850.0 / (double)(count - 1));
        double r = surface_reflection(lambda, ar_min_lambda_nm);
        double alpha = silicon_absorption_coefficient(lambda);

        double iqe = 0.0;
        if (alpha > 0.0) {
            /* Збір у виснаженому шарі W та дифузія з L_n */
            double exp_aw = exp(-alpha * w_cm);
            double collection_factor = 1.0 - (exp_aw / (1.0 + alpha * ln_cm));
            iqe = collection_factor;
            if (iqe > 1.0) iqe = 1.0;
            if (iqe < 0.0) iqe = 0.0;
        }

        double eqe = (1.0 - r) * iqe;
        double responsivity = (eqe * (lambda * 1e-3)) / 1.23984;

        out_pts[i].wavelength_nm = lambda;
        out_pts[i].reflection_R = r;
        out_pts[i].alpha_cm1 = alpha;
        out_pts[i].iqe = iqe;
        out_pts[i].eqe = eqe;
        out_pts[i].responsivity_a_w = responsivity;
    }

    return 0;
}

int main(void) {
    const size_t steps = 10;
    PhotodiodeSpectrumPoint points[10];

    /* PIN-фотодіод: W = 20 мкм, L_n = 50 мкм, AR-покриття оптимізовано на 633 нм */
    if (simulate_photodiode_spectrum(20.0, 50.0, 633.0, points, steps) == 0) {
        printf("λ (нм) | R (%%)  | α (см⁻¹) | IQE (%%) | EQE (%%) | R_λ (А/Вт)\n");
        printf("-------+--------+----------+---------+---------+-----------\n");
        for (size_t i = 0; i < steps; i++) {
            printf("%6.1f | %6.2f | %8.1f | %7.2f | %7.2f | %9.4f\n",
                   points[i].wavelength_nm,
                   points[i].reflection_R * 100.0,
                   points[i].alpha_cm1,
                   points[i].iqe * 100.0,
                   points[i].eqe * 100.0,
                   points[i].responsivity_a_w);
        }
    }
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>
#include <span>
#include <expected>
#include <algorithm>

namespace physics {

constexpr double hc_ev_nm = 1239.8419;
constexpr double silicon_eg_ev = 1.12;

struct SpectrumPoint {
    double wavelength_nm{};
    double reflection_r{};
    double alpha_cm1{};
    double iqe{};
    double eqe{};
    double responsivity_a_w{};
};

enum class SimulationError {
    invalid_parameters,
    out_of_bounds
};

class PhotodiodeSimulator {
public:
    explicit PhotodiodeSimulator(double depletion_width_um,
                                 double diffusion_length_um,
                                 double ar_coating_lambda_nm)
        : w_cm_(depletion_width_um * 1e-4),
          ln_cm_(diffusion_length_um * 1e-4),
          ar_target_nm_(ar_coating_lambda_nm) {}

    [[nodiscard]] std::expected<std::vector<SpectrumPoint>, SimulationError>
    generate_spectrum(double start_nm, double end_nm, std::size_t num_points) const {
        if (start_nm >= end_nm || num_points == 0) {
            return std::unexpected(SimulationError::invalid_parameters);
        }

        std::vector<SpectrumPoint> spectrum;
        spectrum.reserve(num_points);

        const double step = (end_nm - start_nm) / static_cast<double>(num_points - 1);

        for (std::size_t i = 0; i < num_points; ++i) {
            const double lambda = start_nm + static_cast<double>(i) * step;
            const double r = calculate_reflection(lambda);
            const double alpha = calculate_alpha(lambda);

            double iqe = 0.0;
            if (alpha > 0.0) {
                const double exp_aw = std::exp(-alpha * w_cm_);
                iqe = std::clamp(1.0 - (exp_aw / (1.0 + alpha * ln_cm_)), 0.0, 1.0);
            }

            const double eqe = (1.0 - r) * iqe;
            const double responsivity = (eqe * (lambda * 1e-3)) / 1.23984;

            spectrum.push_back(SpectrumPoint{
                .wavelength_nm = lambda,
                .reflection_r = r,
                .alpha_cm1 = alpha,
                .iqe = iqe,
                .eqe = eqe,
                .responsivity_a_w = responsivity
            });
        }

        return spectrum;
    }

private:
    double w_cm_;
    double ln_cm_;
    double ar_target_nm_;

    [[nodiscard]] static double calculate_alpha(double lambda_nm) noexcept {
        if (lambda_nm >= 1107.0) return 0.0;
        const double photon_energy = hc_ev_nm / lambda_nm;
        const double diff = photon_energy - silicon_eg_ev;
        if (diff <= 0.0) return 0.0;
        return 5000.0 * diff * diff + 1e5 * std::pow(diff, 3.5);
    }

    [[nodiscard]] double calculate_reflection(double lambda_nm) const noexcept {
        constexpr double n_si = 3.8;
        constexpr double r_bare = ((n_si - 1.0) / (n_si + 1.0)) * ((n_si - 1.0) / (n_si + 1.0));
        const double dev = (lambda_nm - ar_target_nm_) / ar_target_nm_;
        const double r_ar = r_bare * (dev * dev + 0.05);
        return std::min(r_bare, r_ar);
    }
};

} // namespace physics

int main() {
    using namespace physics;

    const PhotodiodeSimulator sim(20.0, 50.0, 633.0);
    const auto result = sim.generate_spectrum(300.0, 1150.0, 10);

    if (!result) {
        std::cerr << "Помилка симуляції фотодіода.\n";
        return 1;
    }

    std::cout << std::fixed << std::setprecision(2);
    std::cout << "λ (нм) | R (%)  | α (см⁻¹) | IQE (%) | EQE (%) | R_λ (А/Вт)\n";
    std::cout << "-------+--------+----------+---------+---------+-----------\n";

    for (const auto& pt : *result) {
        std::cout << std::setw(6) << pt.wavelength_nm << " | "
                  << std::setw(6) << pt.reflection_r * 100.0 << " | "
                  << std::setw(8) << std::setprecision(1) << pt.alpha_cm1 << " | "
                  << std::setw(7) << std::setprecision(2) << pt.iqe * 100.0 << " | "
                  << std::setw(7) << pt.eqe * 100.0 << " | "
                  << std::setw(9) << std::setprecision(4) << pt.responsivity_a_w << "\n";
    }

    return 0;
}
```
:::

### Аналіз та інженерна інтерпретація результатів

Результати чисельного обчислення спектральних характеристик демонструють фундаментальні фізичні закономірності напівпровідникових фотодетекторов та дозволяють робити практичні інженерні висновки:

1. **Короткохвильова область (300–400 нм)**: Ультрафіолетове світло має великий коефіцієнт поглинання (`α > 10⁵ см⁻¹`), через що промінь поглинається у перших 10–50 нанометрах поверхневого шару. Якщо кристал має товстий пасивний шар або високу швидкість поверхневої рекомбінації, згенеровані носії знищуються до потрапляння в область збіднення, викликаючи спад IQE.
2. **Видимий та ближній інфрачервоний діапазон (500–900 нм)**: Поглинання відбувається по всій товщині виснаженого шару `W = 20 мкм`. Внутрішня квантова ефективність сягає 90–98%, а зовнішня квантова ефективність визначається якістю антивідбивального покриття `R(λ)`.
3. **Область відсічки (1000–1100 нм)**: Коефіцієнт поглинання `α` стрімко падає, через що значна частина інфрачервоних фотонів проходить крізь кристал без поглинання. Для підвищення квантового виходу в цьому діапазоні інженери збільшують товщину i-шару `W` до 100–300 мкм або застосовують матеріали з вужчою забороненою зоною (InGaAs).
4. **Оптимізація для практичних застосувань**: Модель дозволяє розробникам оптичних систем підбирати товщину виснаженого шару `W` та дифузійну довжину `L_n` так, щоб забезпечити баланс між максимальною квантовою ефективністю та високою швидкістю спрацьовування (смугою пропускання). Занадто товстий i-шар збільшує час прольоту носіїв `t_drift = W / v_sat`, знижуючи швидкодію фотодіода, тоді як занадто тонкий шар зменшує квантову ефективність на довгих хвилях.
5. **Крайові випадки та межі застосовності чисельної моделі**: Програма використовує спрощену напівемпіричну апроксимацію коефіцієнта поглинання кремнію `α(λ)`. У реальних кремнієвих кристалах поглинання також залежить від концентрації легуючих домішок (звуження забороненої зони за рахунок ефекту BGN — *Bandgap Narrowing*) та від температури кристала. При підвищенні температури ширина забороненої зони `E_g(T)` зменшується, що зміщує спектральну криву поглинання у долгохвильову область. Врахування цих ефектів вимагає введення температурного коефіцієнта Варшні у функцію обчислення `α(λ)`.
6. **Практична цінність чисельного моделювання**: Автоматичний розрахунок дозволяє інженерові швидко спроєктувати антирефлексне покриття для конкретної лазерної довжини хвилі (наприклад, 633 нм для He-Ne лазера або 850 нм для напівпровідникового випромінювача), оцінити вплив паразитного відбиття та оптимізувати глибину p-n переходу `x_j` для досягнення максимального відношення сигнал/шум у заданому спектральному діапазоні.
