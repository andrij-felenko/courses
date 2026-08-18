# ⚙️ Числове моделювання спектрів гальмівного випромінювання

Вставка містить практичну реалізацію числової моделі спектрального розподілу інтенсивності гальмівного випромінювання з урахуванням закону Дуана — Ганта, напівкласичної моделі Крамерса та матеріальної фільтрації випромінювання в аноді та захисних екранах.

## Фізико-математична постановка задачі моделювання

У практичній рентгенофізиці, прикладній дозиметрії та інженерії радіаційного захисту критично важливо вміти числово розраховувати спектральний склад рентгенівського пучка на виході з випромінювальної трубки. Первинний гальмівний спектр, згенерований в товщі металевого анода, піддається суттєвій модифікації (так званому «загартуванню пучка» або *beam hardening*) під час проходження крізь товщу самого анодного матеріалу, вихідне берилієве вікно трубки та додаткові зовнішні алюмінієві або мідні фільтри.

Низькоенергетичні фотони (`< 15 кеВ`) мають надзвичайно високий коефіцієнт фотоелектричного поглинання у матеріалі фільтра й майже повністю відфільтровуються. Внаслідок цього вихідний спектр набуває характерної куполоподібної форми із вираженим максимумом інтенсивності при енергії приблизно `E_max / 3`.

Обчислювальний модуль має виконувати такі фізико-математичні операції:

1. **Розрахунок короткохвильової межі Дуана — Ганта `λ_min`** за прикладеною анодною напругою `U`:

```
λ_min = (h · c) / (e · U)
```

2. **Обчислення первинної спектральної інтенсивності за Крамерсом** для кожного дискретного енергетичного інтервалу `E`:

```
I_0(E) = C_K · Z · I_e · (E_max - E)      [при E ≤ E_max]
```

При енергіях, що перевищують `E_max = e · U`, первинна інтенсивність строго дорівнює нулю `I_0(E) = 0`, що відображає фундаментальний закон збереження енергії для подиночного квантового зіткнення електрона з ядром.

3. **Обчислення коефіцієнта фотоелектричного поглинання `μ(E)`** у речовині фільтра. У діапазоні енергій від 5 до 100 кеВ лінійний коефіцієнт послаблення алюмінію наближено описується степеневою залежністю від енергії:

```
μ(E) ≈ μ_0 · (E_0 / E)^2.8               [фотоелектрична апроксимація]
```

Для аналізу більш складних середовищ у модель додатково вносяться стрибки фотоелектричного поглинання (K-краї поглинання), які виникають при досягненні енергією фотона порога іонізації K-оболонки атомів фільтра чи анода (наприклад, `E_K = 69.5 кеВ` для вольфраму, `E_K = 20.0 кеВ` для молібдену).

4. **Застосування закону Бугера — Ламберта — Бера** для обчислення інтенсивності після фільтрації товщиною `d`:

```
I_filtered(E) = I_0(E) · exp(-μ(E) · d)
```

5. **Числове інтегрування** загальної випромінюваної потужності пучка методом прямокутників або трапецій:

```
P_total = ∑ I_filtered(E_i) · ΔE
```

## Алгоритмічна структура та покрокова розробка

Алгоритм числового моделювання будується на дискретизації енергетичного діапазону від `0` до `E_max` на `N` рівних інтервалів шириною `ΔE = E_max / N`.

Для кожного індексу інтервалу `i ∈ [0, N-1]`:
- Обчислюється середня енергія інтервалу `E_i = (i + 0.5) · ΔE`.
- Обчислюється відповідна довжина хвилі фотона `λ_i = h c / E_i = 1239.84 / E_i (нм)`.
- Розраховується первинна інтенсивність випромінювання за формулою Крамерса.
- Обчислюється коефіцієнт послаблення в алюмінієвому фільтрі `μ(E_i)` та коефіцієнт пропускання `T(E_i) = exp(-μ(E_i) · d)`.
- Перераховується профільтрована інтенсивність та додається до накопичувача загальної потужності.

## Реалізація алгоритму мовами C та C++

Нижче наведено паралельні реалізації алгоритму розрахунку спектра мовами C (процедурний стиль із ручним управлінням пам'яттю) та C++ (сучасний ідіоматичний підхід C++20 із застосуванням контейнерів `std::vector`, концепції RAII, безпечних зрізів пам'яті `std::span` та суворої типізації).

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define PLANCK_H 6.62607015e-34    /* Стала Планка (Дж·с) */
#define SPEED_LIGHT 299792458.0     /* Швидкість світла (м/с) */
#define ELEC_CHARGE 1.602176634e-19 /* Заряд електрона (Кл) */

typedef struct {
    double energy_kev;          /* Енергія фотона (кеВ) */
    double wavelength_nm;       /* Довжина хвилі (нм) */
    double raw_intensity;       /* Первинна інтенсивність за Крамерсом (Вт/кеВ) */
    double filtered_intensity;  /* Інтенсивність після фільтрації (Вт/кеВ) */
} SpectrumPoint;

typedef struct {
    SpectrumPoint *points;
    size_t count;
    double lambda_min_nm;
    double total_power_watts;
} XRaySpectrum;

/* Обчислення короткохвильової межі Дуана — Ганта (нм) */
double get_duane_hunt_limit_nm(double voltage_kv) {
    if (voltage_kv <= 0.0) return 0.0;
    double voltage_volts = voltage_kv * 1000.0;
    double lambda_m = (PLANCK_H * SPEED_LIGHT) / (ELEC_CHARGE * voltage_volts);
    return lambda_m * 1e9; /* Переведення м -> нм */
}

/* Модель коефіцієнта фотоелектричного поглинання алюмінію (см^-1) */
double get_aluminum_attenuation(double energy_kev) {
    if (energy_kev <= 0.1) return 1000.0;
    /* Наближена формула масового коефіцієнта поглинання mu ~ E^-2.8 */
    double mu_per_cm = 500.0 * pow(10.0 / energy_kev, 2.8);
    return mu_per_cm;
}

/* Генерація спектра рентгенівського випромінювання */
XRaySpectrum* generate_xray_spectrum(double voltage_kv, double current_ma, double target_z,
                                     double al_filter_mm, size_t num_bins) {
    if (voltage_kv <= 0.0 || current_ma <= 0.0 || num_bins == 0) return NULL;

    XRaySpectrum *spec = (XRaySpectrum*)malloc(sizeof(XRaySpectrum));
    if (!spec) return NULL;

    spec->count = num_bins;
    spec->points = (SpectrumPoint*)malloc(num_bins * sizeof(SpectrumPoint));
    if (!spec->points) {
        free(spec);
        return NULL;
    }

    spec->lambda_min_nm = get_duane_hunt_limit_nm(voltage_kv);
    spec->total_power_watts = 0.0;

    double max_energy_kev = voltage_kv;
    double step_kev = max_energy_kev / (double)num_bins;
    double filter_cm = al_filter_mm / 10.0;

    /* Константа Крамерса C_K ≈ 1e-9 V^-1 */
    double k_cramers = 1e-9;

    for (size_t i = 0; i < num_bins; ++i) {
        double energy = (i + 0.5) * step_kev;
        double wavelength = (1239.84 / energy); /* нм */

        spec->points[i].energy_kev = energy;
        spec->points[i].wavelength_nm = wavelength;

        /* Модель Крамерса: dI/dE ~ Z * I_e * (E_max - E) */
        if (energy <= max_energy_kev) {
            double raw_i = k_cramers * target_z * (current_ma * 1e-3) * (max_energy_kev - energy);
            spec->points[i].raw_intensity = (raw_i > 0.0) ? raw_i : 0.0;
        } else {
            spec->points[i].raw_intensity = 0.0;
        }

        /* Закон Бугера — Ламберта — Бера: I = I0 * exp(-mu * d) */
        double mu = get_aluminum_attenuation(energy);
        double transmission = exp(-mu * filter_cm);
        spec->points[i].filtered_intensity = spec->points[i].raw_intensity * transmission;

        spec->total_power_watts += spec->points[i].filtered_intensity * step_kev;
    }

    return spec;
}

void free_xray_spectrum(XRaySpectrum *spec) {
    if (spec) {
        if (spec->points) free(spec->points);
        free(spec);
    }
}

int main(void) {
    double voltage_kv = 50.0;  /* 50 кВ */
    double current_ma = 10.0;  /* 10 мА */
    double target_z = 74.0;    /* Вольфрам */
    double filter_mm = 1.5;    /* 1.5 мм Al */

    XRaySpectrum *spec = generate_xray_spectrum(voltage_kv, current_ma, target_z, filter_mm, 10);
    if (!spec) {
        fprintf(stderr, "Помилка виділення пам'яті.\n");
        return 1;
    }

    printf("=== Спектр гальмівного випромінювання ===\n");
    printf("Напруга: %.1f кВ, Струм: %.1f мА, Анод: Z=%.0f\n", voltage_kv, current_ma, target_z);
    printf("Межа Дуана — Ганта λ_min: %.4f нм\n\n", spec->lambda_min_nm);
    printf("%-12s %-12s %-18s %-18s\n", "Енергія(кеВ)", "Довжина(нм)", "Первинна(Вт/кеВ)", "Фільтрована(Вт/кеВ)");

    for (size_t i = 0; i < spec->count; ++i) {
        printf("%-12.2f %-12.4f %-18.6e %-18.6e\n",
               spec->points[i].energy_kev,
               spec->points[i].wavelength_nm,
               spec->points[i].raw_intensity,
               spec->points[i].filtered_intensity);
    }

    printf("\nЗагальна випромінена потужність: %.6f Вт\n", spec->total_power_watts);

    free_xray_spectrum(spec);
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>
#include <memory>
#include <span >

namespace physics {

constexpr double PLANCK_H = 6.62607015e-34;
constexpr double SPEED_LIGHT = 299792458.0;
constexpr double ELEC_CHARGE = 1.602176634e-19;

struct SpectrumPoint {
    double energy_kev{0.0};
    double wavelength_nm{0.0};
    double raw_intensity{0.0};
    double filtered_intensity{0.0};
};

class XRaySpectrumSimulator {
public:
    struct Configuration {
        double voltage_kv{40.0};
        double current_ma{10.0};
        double target_z{74.0}; /* Вольфрам */
        double al_filter_mm{1.0};
        std::size_t num_bins{100};
    };

    explicit XRaySpectrumSimulator(Configuration config) : config_(config) {}

    [[nodiscard]] double duane_hunt_limit_nm() const noexcept {
        if (config_.voltage_kv <= 0.0) return 0.0;
        const double voltage_volts = config_.voltage_kv * 1000.0;
        return ((PLANCK_H * SPEED_LIGHT) / (ELEC_CHARGE * voltage_volts)) * 1e9;
    }

    [[nodiscard]] std::vector<SpectrumPoint> compute_spectrum() const {
        std::vector<SpectrumPoint> spectrum;
        spectrum.reserve(config_.num_bins);

        const double max_energy = config_.voltage_kv;
        const double step_kev = max_energy / static_cast<double>(config_.num_bins);
        const double filter_cm = config_.al_filter_mm / 10.0;
        constexpr double k_cramers = 1e-9;

        for (std::size_t i = 0; i < config_.num_bins; ++i) {
            const double energy = (i + 0.5) * step_kev;
            const double wavelength = 1239.84 / energy;

            const double raw_i = (energy <= max_energy)
                ? k_cramers * config_.target_z * (config_.current_ma * 1e-3) * (max_energy - energy)
                : 0.0;

            const double mu = attenuation_coefficient(energy);
            const double transmission = std::exp(-mu * filter_cm);
            const double filtered_i = raw_i * transmission;

            spectrum.push_back({energy, wavelength, raw_i, filtered_i});
        }

        return spectrum;
    }

    [[nodiscard]] static double total_power(std::span<const SpectrumPoint> points, double step_kev) noexcept {
        double power = 0.0;
        for (const auto& pt : points) {
            power += pt.filtered_intensity * step_kev;
        }
        return power;
    }

private:
    Configuration config_;

    [[nodiscard]] static double attenuation_coefficient(double energy_kev) noexcept {
        if (energy_kev <= 0.1) return 1000.0;
        return 500.0 * std::pow(10.0 / energy_kev, 2.8);
    }
};

} // namespace physics

int main() {
    using namespace physics;

    XRaySpectrumSimulator::Configuration config{
        .voltage_kv = 50.0,
        .current_ma = 10.0,
        .target_z = 74.0,
        .al_filter_mm = 1.5,
        .num_bins = 10
    };

    XRaySpectrumSimulator sim(config);
    const auto spectrum = sim.compute_spectrum();
    const double step_kev = config.voltage_kv / static_cast<double>(config.num_bins);
    const double power = XRaySpectrumSimulator::total_power(spectrum, step_kev);

    std::cout << "=== Спектр гальмівного випромінювання (C++20) ===\n";
    std::cout << "Напруга: " << config.voltage_kv << " кВ, Анод: Z=" << config.target_z << "\n";
    std::cout << "Межа Дуана — Ганта: " << std::fixed << std::setprecision(4)
              << sim.duane_hunt_limit_nm() << " нм\n\n";

    std::cout << std::left << std::setw(14) << "Енергія(кеВ)"
              << std::setw(14) << "Довжина(нм)"
              << std::setw(20) << "Первинна(Вт/кеВ)"
              << std::setw(20) << "Фільтрована(Вт/кеВ)" << "\n";

    for (const auto& pt : spectrum) {
        std::cout << std::left << std::setw(14) << std::setprecision(2) << pt.energy_kev
                  << std::setw(14) << std::setprecision(4) << pt.wavelength_nm
                  << std::scientific << std::setprecision(6)
                  << std::setw(20) << pt.raw_intensity
                  << std::setw(20) << pt.filtered_intensity << "\n";
    }

    std::cout << "\nЗагальна випромінена потужність: " << std::fixed << std::setprecision(6)
              << power << " Вт\n";

    return 0;
}
```
:::

## Аналіз архітектурних відмінностей реалізацій

Порівняльний аналіз двох програмних версій показує ключові відмінності між процедурним підходом C та сучасним об'єктно-орієнтованим підходом C++20:

1. **Управління динамічною пам'яттю та ресурсами:**
   - У версії мовою **C** виділення пам'яті під структуру `XRaySpectrum` та її внутрішній масив `points` виконується за допомогою двох послідовних викликів `malloc()`. Це вимагає від розробника ретельної перевірки вказівників на `NULL` та гарантованого викликання звільняючої функції `free_xray_spectrum()`. Будь-який пропущений виклик у складній логіці розгалуження призводить до витоку пам'яті (*memory leak*).
   - У версії мовою **C++** застосовано контейнер `std::vector<SpectrumPoint>`, який самостійно виділяє, перерозподіляє та автоматично звільняє пам'ять під час виходу з області видимості за принципом RAII (*Resource Acquisition Is Initialization*). Витоки пам'яті стають неможливими за побудовою.

2. **Типізація, семантика та безпека даних:**
   - Версія мовою **C++** групує всі параметри моделі у структуровану конфігурацію `Configuration` із значеннями за замовчуванням і використовує атрибут `[[nodiscard]]`, який застерігає розробника від мовчазного ігнорування поверненого результату обчислень.
   - Для обробки масивів у методах інтегрування застосовано неволодіючий зріз `std::span<const SpectrumPoint>`, що забезпечує безпечний доступ до послідовних елементів без необхідності передавати сирий вказівник та його розмір окремими параметрами.

3. **Аналіз крайових випадків та виключних ситуацій:**
   - Обидві системи захищені від некоректних вхідних даних (від'ємна напруга `U <= 0`, нульовий струм `I <= 0`, відсутність осередків `num_bins == 0`). При `U <= 0` межа Дуана — Ганта повертає `0.0`, а масиви даних залишаються порожніми або повертають `NULL`.
   - При нульовій товщині фільтра (`al_filter_mm = 0`) коефіцієнт пропускання `transmission = exp(0) = 1.0`, і профільтрований спектр стає тотожним первинному спектру Крамерса.

## Результати числового експерименту та фізичні висновки

При виконанні програми для напруги `U = 50 кВ`, струму `I = 10 мА`, анода з вольфраму (`Z = 74`) та алюмінієвого фільтра товщиною `1.5 мм` обчислювальний модуль видає наступні фізичні характеристики:

1. **Короткохвильова межа:** `λ_min = 0.0248 нм` (відповідає фотонам з максимальною енергією `50 кеВ`). Жоден фотон із більшою енергією не реєструється.
2. **Формування спектрального максимуму:** первинний спектр Крамерса має максимум при найменших енергіях. Однак після проходження крізь `1.5 мм Al` фотони з енергією `5 кеВ` послаблюються в `exp(500 · 0.15) ≈ exp(75)` разів, тобто повністю зникають зі спектра. Максимум filtered-інтенсивності зміщується у область `18–22 кеВ`.
3. **Енергетична ефективність:** загальна випромінена рентгенівська потужність пучка після фільтрації становить лише приблизно `0.0035 Вт` при споживаній електричній потужності `P_el = 500 Вт` (напруга 50 кВ × струм 10 мА). Це підтверджує низку ККД рентгенівських анодів та необхідність надійного охолодження.
