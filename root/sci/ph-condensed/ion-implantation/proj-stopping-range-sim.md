# ⚙️ Моделювання траєкторій іонів та каскадів дефектів методом Монте-Карло

Обчислювальне моделювання процесів проникнення високоенергетичних іонів у тверді тіла методом Монте-Карло спирається на наближення парних зіткнень (BCA — *Binary Collision Approximation*). Цей метод є стандартом сучасної фізики напівпровідникового матеріалознавства і лежить в основі класичних розрахункових програм TRIM (*Transport of Ions in Matter*) та універсального комплексу SRIM (*Stopping and Range of Ions in Matter*), розробленого Джеймсом Зіглером (*James F. Ziegler*).

### Фізичні засади наближення парних зіткнень (BCA)

Наближення BCA базується на фундаментальному припущенні, що при кінетичних енергіях іона `E > 100 еВ` його взаємодія з атомною ґраткою мишені зводиться до серії послідовних незалежних двочастинкових пружних зіткнень з окремими атомами кремнію. Вплив усіх інших віддалених атомів кристала в момент удару вважається знехтувально малим і враховується лише як усереднений потенціал екранування.

Фізична модель Монте-Карло відстежує покрокову траєкторію частинки у тривимірному просторі за допомогою такої послідовності дій:

1. **Прямолінійне переміщення між вузлами**: між двома послідовними ядерними актами розсіювання іон рухається по прямій лінії на довжину вільного пробігу `λ = N⁻¹ᐟ³` (для кремнію середня міжмитальна відстань становить `λ ≈ 2.5 Å`).
2. **Безперервне електронне гальмування**: уздовж усієї довжини кроку `λ` іон зазнає неупругого в'язкого тертя з електронною хмарою середовища. Втрата енергії розраховується за формулою Ліндгарда–Шарффа (LSS): `ΔE_elec = S_e(E) · λ = k_e · √E · λ`.
3. **Випадковий прицільний параметр**: при наближенні до чергового вузла ґратки прицільний параметр `b` вибирається як випадкова величина з рівномірним розподілом площі круга `b = √(r · b_max²)`, де `r ∈ [0, 1)`.
4. **Кут розсіювання у системі центру мас**: для розрахунку кута відхилення `θ_cm` застосовують універсальний екранований потенціал Зіглера–Бірсака–Літтмарка (ZBL), який підходить для будь-якої пари іон-мишень.
5. **Пороговий критерій утворення дефектів за Френкелем**: при зіткненні частина кінетичної енергії `T` передається атому ґратки. Якщо передана енергія перевищує порогову енергію зміщення `E_d` (для кремнію `E_d ≈ 15 еВ`), атом Si вибивається зі свого вузла й перетворюється на первинний вторинний снаряд (PKA — *Primary Knock-on Atom*). На місці вибитого атома виникає **вакансія**, а вибитий атом мандрує кристалом, поки не зупиниться у міжвузлі, створюючи **міжвузловий атом** (пару Френкеля).

### Моделювання вторинних каскадів та розпилення поверхні

Коли вибитий атом кремнію (PKA) отримує кінетичну енергію `T >> E_d` (наприклад, `T = 2–5 кеВ`), він сам перетворюється на швидку частинку й починає вибивати інші атоми ґратки. Симулятор Монте-Карло рекурсивно відстежує траєкторії всіх вторинних та третинних вибитих атомів кремнію (модель MARLOWE / TRIM cascade).

При цьому виникають два важливі крайові випадки:
- **Поверхневе розпилення (Sputtering)**: якщо вибитий атом кремнію біля самої поверхні (`x < 1 нм`) отримує вектор імпульсу, спрямований у бік вакууму, і його енергія перевищує сублімаційну енергію зв'язку поверхні `E_sb ≈ 4.7 еВ`, він залишає кристал. Це явище викликає розпилення (ерозію) поверхні пластини при великих дозах.
- **Спонтанна анігіляція парів Френкеля**: якщо вибитий атом Si зупиняється від своєї вакансії на відстані, меншій за радіус спонтанного захоплення `r_rec ≈ 2–3` періоди ґратки, пара Френкеля неусталено рекомбінує без утворення стабільного дефекту.

### Математичний вивід та алгоритм розсіювання на потенціалі ZBL

Для обчислення кута відхилення `θ_cm` у системі центру мас використовується розв'язок класичного інтеграла розсіювання для екранованого потенціалу кулонівської взаємодії ZBL:

```
V(r) = (Z₁ · Z₂ · e² / (4 · π · ε₀ · r)) · Ф_ZBL(r / a_u)
```

де `a_u = 0.8854 · a₀ / (Z₁⁰.²³ + Z₂⁰.²³)` — універсальний радіус екранування Зіглера, а `Ф_ZBL(x)` — експоненціальна сума чотирьох зважених екрануючих членів:

```
Ф_ZBL(x) = 0.1818 · e^(-3.2 · x) + 0.5099 · e^(-0.9423 · x) + 0.2802 · e^(-0.4029 · x) + 0.02817 · e^(-0.2016 · x)
```

Інтеграл розсіювання для кута `θ_cm` визначається співвідношенням:

```
θ_cm = π - 2 · b · ∫_{r_min}^{∞} dr / (r² · √(1 - V(r)/E_cm - b²/r²))
```

У симуляторах швидкого розрахунку цей інтеграл заморожується у вигляді впорядкованої двомірної таблиці апроксимацій (Magic Formula Зіглера), що забезпечує високу швидкість обчислення мільйонів зіткнень на секунду.

---

### Програмування симулятора мовами C та C++

Нижче наведено повноцінний реальний код симулятора методом Монте-Карло. Він моделює інжекцію іонів у кремній, обчислює підсумковий проектований пробіг `R_p`, розраховує поздовжній страґлінг `ΔR_p` та будує гістограми розподілу імплантованої домішки та утворених радіаційних вакансій.

:::tabs
```c
/* Simulation of Ion Implantation via Monte Carlo (C99) */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define PI 3.14159265358979323846
#define SI_DENSITY 5.02e22      /* Atom density of Si (atoms/cm^3) */
#define LAMBDA_STEP 2.5e-8      /* Free path step (cm) = 2.5 Angstrom */
#define E_DISPLACEMENT 15.0     /* Displacement energy threshold for Si (eV) */
#define E_SURFACE_BIND 4.7      /* Surface binding energy for Si sputtering (eV) */
#define MAX_HISTOGRAM_BINS 100

typedef struct {
    double energy_ev;       /* Current kinetic energy (eV) */
    double x_cm;            /* Depth coordinate (cm) */
    double y_cm;            /* Lateral coordinate (cm) */
    double dir_x;           /* Direction cosine X */
    double dir_y;           /* Direction cosine Y */
    int is_recoil;          /* Flag: 0 = primary ion, 1 = recoil Si atom */
} IonParticle;

typedef struct {
    double initial_energy_ev;
    double m1_amu;
    double z1;
    double m2_amu;
    double z2;
    double ke_coeff;        /* Electronic stopping factor (eV^0.5 / cm) */
    int total_ions;
    double depth_max_cm;
} SimConfig;

/* Simple uniform random generator [0, 1) */
static double rand_uniform(void) {
    return (double)rand() / ((double)RAND_MAX + 1.0);
}

/* Recursive cascade simulation for recoil atoms */
void simulate_recoil_cascade(const SimConfig *cfg, double start_x, double start_y, double start_energy, int *vacancies_hist) {
    if (start_energy < E_DISPLACEMENT) return;

    IonParticle recoil;
    recoil.energy_ev = start_energy - E_DISPLACEMENT;
    recoil.x_cm = start_x;
    recoil.y_cm = start_y;
    recoil.dir_x = (rand_uniform() - 0.5) * 2.0;
    recoil.dir_y = (rand_uniform() - 0.5) * 2.0;
    recoil.is_recoil = 1;

    double max_b = 1.5e-8;
    while (recoil.energy_ev > E_DISPLACEMENT && recoil.x_cm >= 0.0 && recoil.x_cm < cfg->depth_max_cm) {
        double dE_elec = cfg->ke_coeff * sqrt(recoil.energy_ev) * LAMBDA_STEP;
        recoil.energy_ev -= dE_elec;
        if (recoil.energy_ev <= 0.0) break;

        double r = rand_uniform();
        double b = sqrt(r) * max_b;
        double sin_half_theta = 1.0 / sqrt(1.0 + (b * b * 1e16) * (recoil.energy_ev / 500.0));
        double T_transferred = recoil.energy_ev * (sin_half_theta * sin_half_theta);

        if (T_transferred > E_DISPLACEMENT) {
            int bin = (int)((recoil.x_cm / cfg->depth_max_cm) * MAX_HISTOGRAM_BINS);
            if (bin >= 0 && bin < MAX_HISTOGRAM_BINS) {
                vacancies_hist[bin]++;
            }
            /* Secondary recoil cascade recursive call */
            if (T_transferred > 50.0) {
                simulate_recoil_cascade(cfg, recoil.x_cm, recoil.y_cm, T_transferred, vacancies_hist);
            }
        }

        recoil.energy_ev -= T_transferred;
        recoil.x_cm += recoil.dir_x * LAMBDA_STEP;
        recoil.y_cm += recoil.dir_y * LAMBDA_STEP;
    }
}

/* Simulate trajectory of a single primary ion */
void simulate_ion(const SimConfig *cfg, IonParticle *ion, int *vacancies_hist, int *range_hist, int *sputtered_count) {
    ion->energy_ev = cfg->initial_energy_ev;
    ion->x_cm = 0.0;
    ion->y_cm = 0.0;
    ion->dir_x = 1.0; /* Injected straight inside (along X axis) */
    ion->dir_y = 0.0;
    ion->is_recoil = 0;

    double max_b = 1.5e-8; /* Max impact parameter (cm) */
    double t_max_factor = (4.0 * cfg->m1_amu * cfg->m2_amu) / 
                          ((cfg->m1_amu + cfg->m2_amu) * (cfg->m1_amu + cfg->m2_amu));

    while (ion->energy_ev > 5.0 && ion->x_cm >= 0.0 && ion->x_cm < cfg->depth_max_cm) {
        /* 1. Electronic stopping loss */
        double dE_elec = cfg->ke_coeff * sqrt(ion->energy_ev) * LAMBDA_STEP;
        ion->energy_ev -= dE_elec;
        if (ion->energy_ev <= 0.0) break;

        /* 2. Nuclear collision selection */
        double r = rand_uniform();
        double b = sqrt(r) * max_b;

        /* Reduced energy proxy for center-of-mass scattering angle */
        double sin_half_theta = 1.0 / sqrt(1.0 + (b * b * 1e16) * (ion->energy_ev / 1000.0));
        double T_transferred = t_max_factor * ion->energy_ev * (sin_half_theta * sin_half_theta);

        /* 3. Check for Frenkel vacancy creation & recoil cascade */
        if (T_transferred > E_DISPLACEMENT) {
            int bin = (int)((ion->x_cm / cfg->depth_max_cm) * MAX_HISTOGRAM_BINS);
            if (bin >= 0 && bin < MAX_HISTOGRAM_BINS) {
                vacancies_hist[bin]++;
            }
            if (ion->x_cm < 1.0e-7 && T_transferred > E_SURFACE_BIND) {
                (*sputtered_count)++;
            }
            /* Trigger secondary recoil atom tracking if transferred energy is high */
            if (T_transferred > 100.0) {
                simulate_recoil_cascade(cfg, ion->x_cm, ion->y_cm, T_transferred, vacancies_hist);
            }
        }

        ion->energy_ev -= T_transferred;

        /* 4. Angular deflection */
        double theta_lab = sin_half_theta * (cfg->m2_amu / (cfg->m1_amu + cfg->m2_amu));
        double phi = (rand_uniform() - 0.5) * 2.0 * theta_lab;

        double new_dir_x = ion->dir_x * cos(phi) - ion->dir_y * sin(phi);
        double new_dir_y = ion->dir_x * sin(phi) + ion->dir_y * cos(phi);
        double norm = sqrt(new_dir_x * new_dir_x + new_dir_y * new_dir_y);

        ion->dir_x = new_dir_x / norm;
        ion->dir_y = new_dir_y / norm;

        /* 5. Advance position */
        ion->x_cm += ion->dir_x * LAMBDA_STEP;
        ion->y_cm += ion->dir_y * LAMBDA_STEP;
    }

    /* Record final stopping range location */
    if (ion->x_cm >= 0.0 && ion->x_cm < cfg->depth_max_cm) {
        int bin = (int)((ion->x_cm / cfg->depth_max_cm) * MAX_HISTOGRAM_BINS);
        if (bin >= 0 && bin < MAX_HISTOGRAM_BINS) {
            range_hist[bin]++;
        }
    }
}

int main(void) {
    SimConfig cfg = {
        .initial_energy_ev = 50000.0, /* 50 keV Boron */
        .m1_amu = 11.0,
        .z1 = 5.0,
        .m2_amu = 28.08,
        .z2 = 14.0,
        .ke_coeff = 1.2e6,
        .total_ions = 10000,
        .depth_max_cm = 400e-7 /* 400 nm max depth */
    };

    int *vacancies_hist = (int*)calloc(MAX_HISTOGRAM_BINS, sizeof(int));
    int *range_hist = (int*)calloc(MAX_HISTOGRAM_BINS, sizeof(int));
    int sputtered_count = 0;

    if (!vacancies_hist || !range_hist) {
        free(vacancies_hist); free(range_hist);
        return 1;
    }

    srand(42);
    for (int i = 0; i < cfg.total_ions; ++i) {
        IonParticle ion;
        simulate_ion(&cfg, &ion, vacancies_hist, range_hist, &sputtered_count);
    }

    printf("=== Monte Carlo BCA Ion Implantation Simulation (C99) ===\n");
    printf("Total Ions Simulated: %d\n", cfg.total_ions);
    printf("Total Surface Sputtered Si Atoms: %d\n", sputtered_count);
    printf("Depth (nm) | Ion Stops (Count) | Vacancy Cascade (Count)\n");
    for (int i = 0; i < MAX_HISTOGRAM_BINS; i += 10) {
        double depth_nm = (i + 0.5) * (cfg.depth_max_cm * 1e7 / MAX_HISTOGRAM_BINS);
        printf("%9.1f  | %17d | %23d\n", depth_nm, range_hist[i], vacancies_hist[i]);
    }

    free(vacancies_hist);
    free(range_hist);
    return 0;
}
```
```cpp
// Simulation of Ion Implantation via Monte Carlo (Idiomatic C++20)
#include <iostream>
#include <vector>
#include <cmath>
#include <random>
#include <numbers>
#include <iomanip>
#include <memory>
#include <numeric>

namespace ion_sim {

constexpr double SI_DENSITY = 5.02e22;      // Atom density of Si (atoms/cm^3)
constexpr double LAMBDA_STEP = 2.5e-8;      // Free path step (cm)
constexpr double E_DISPLACEMENT = 15.0;     // Threshold displacement energy (eV)
constexpr double E_SURFACE_BIND = 4.7;      // Surface binding energy for Si sputtering (eV)

struct IonState {
    double energy_ev{0.0};
    double x_cm{0.0};
    double y_cm{0.0};
    double dir_x{1.0};
    double dir_y{0.0};
    bool is_recoil{false};
};

struct SimConfig {
    double initial_energy_ev{50000.0}; // 50 keV
    double m1_amu{11.0};               // Boron
    double z1{5.0};
    double m2_amu{28.08};              // Silicon
    double z2{14.0};
    double ke_coeff{1.2e6};            // Electronic drag coefficient
    std::size_t total_ions{10000};
    double depth_max_cm{400e-7};       // 400 nm depth window
    std::size_t num_bins{100};
};

class ImplantationSimulator {
public:
    explicit ImplantationSimulator(SimConfig config)
        : config_(config),
          rng_(42),
          dist_distrib_(0.0, 1.0),
          vacancies_hist_(config.num_bins, 0),
          range_hist_(config.num_bins, 0),
          sputtered_count_(0) {}

    void run() {
        for (std::size_t i = 0; i < config_.total_ions; ++i) {
            simulate_single_ion();
        }
    }

    void print_results() const {
        std::cout << "=== Monte Carlo Ion Stopping Profile (C++20) ===\n";
        std::cout << "Simulated Primary Ions: " << config_.total_ions << "\n";
        std::cout << "Sputtered Surface Silicon Atoms: " << sputtered_count_ << "\n";
        std::cout << std::setw(12) << "Depth (nm)"
                  << std::setw(18) << "Ion Concentration"
                  << std::setw(24) << "Vacancy Cascade\n";

        for (std::size_t i = 0; i < config_.num_bins; i += 10) {
            double depth_nm = (i + 0.5) * (config_.depth_max_cm * 1e7 / config_.num_bins);
            std::cout << std::setw(12) << std::fixed << std::setprecision(1) << depth_nm
                      << std::setw(18) << range_hist_[i]
                      << std::setw(24) << vacancies_hist_[i] << "\n";
        }
    }

    [[nodiscard]] double calculate_projected_range_nm() const {
        double weighted_sum = 0.0;
        std::size_t total_stops = 0;
        for (std::size_t i = 0; i < config_.num_bins; ++i) {
            double depth_nm = (i + 0.5) * (config_.depth_max_cm * 1e7 / config_.num_bins);
            weighted_sum += depth_nm * range_hist_[i];
            total_stops += range_hist_[i];
        }
        return total_stops > 0 ? weighted_sum / total_stops : 0.0;
    }

    [[nodiscard]] double calculate_straggling_nm(double r_p_nm) const {
        double weighted_sq_sum = 0.0;
        std::size_t total_stops = 0;
        for (std::size_t i = 0; i < config_.num_bins; ++i) {
            double depth_nm = (i + 0.5) * (config_.depth_max_cm * 1e7 / config_.num_bins);
            double diff = depth_nm - r_p_nm;
            weighted_sq_sum += diff * diff * range_hist_[i];
            total_stops += range_hist_[i];
        }
        return total_stops > 0 ? std::sqrt(weighted_sq_sum / total_stops) : 0.0;
    }

private:
    void simulate_recoil_cascade(double start_x, double start_y, double start_energy) {
        if (start_energy < E_DISPLACEMENT) return;

        IonState recoil{
            .energy_ev = start_energy - E_DISPLACEMENT,
            .x_cm = start_x,
            .y_cm = start_y,
            .dir_x = (dist_distrib_(rng_) - 0.5) * 2.0,
            .dir_y = (dist_distrib_(rng_) - 0.5) * 2.0,
            .is_recoil = true
        };

        const double max_b = 1.5e-8;
        while (recoil.energy_ev > E_DISPLACEMENT && recoil.x_cm >= 0.0 && recoil.x_cm < config_.depth_max_cm) {
            const double dE_elec = config_.ke_coeff * std::sqrt(recoil.energy_ev) * LAMBDA_STEP;
            recoil.energy_ev -= dE_elec;
            if (recoil.energy_ev <= 0.0) break;

            const double r = dist_distrib_(rng_);
            const double b = std::sqrt(r) * max_b;
            const double sin_half_theta = 1.0 / std::sqrt(1.0 + (b * b * 1e16) * (recoil.energy_ev / 500.0));
            const double T_transferred = recoil.energy_ev * (sin_half_theta * sin_half_theta);

            if (T_transferred > E_DISPLACEMENT) {
                const auto bin = static_cast<std::size_t>((recoil.x_cm / config_.depth_max_cm) * config_.num_bins);
                if (bin < config_.num_bins) {
                    vacancies_hist_[bin]++;
                }
                if (T_transferred > 50.0) {
                    simulate_recoil_cascade(recoil.x_cm, recoil.y_cm, T_transferred);
                }
            }

            recoil.energy_ev -= T_transferred;
            recoil.x_cm += recoil.dir_x * LAMBDA_STEP;
            recoil.y_cm += recoil.dir_y * LAMBDA_STEP;
        }
    }

    void simulate_single_ion() {
        IonState ion{.energy_ev = config_.initial_energy_ev, .x_cm = 0.0, .y_cm = 0.0, .dir_x = 1.0, .dir_y = 0.0, .is_recoil = false};

        const double max_b = 1.5e-8;
        const double t_max_factor = (4.0 * config_.m1_amu * config_.m2_amu) /
                                    ((config_.m1_amu + config_.m2_amu) * (config_.m1_amu + config_.m2_amu));

        while (ion.energy_ev > 5.0 && ion.x_cm >= 0.0 && ion.x_cm < config_.depth_max_cm) {
            // 1. Electronic drag loss
            const double dE_elec = config_.ke_coeff * std::sqrt(ion.energy_ev) * LAMBDA_STEP;
            ion.energy_ev -= dE_elec;
            if (ion.energy_ev <= 0.0) break;

            // 2. Impact parameter & nuclear collision
            const double r = dist_distrib_(rng_);
            const double b = std::sqrt(r) * max_b;

            const double sin_half_theta = 1.0 / std::sqrt(1.0 + (b * b * 1e16) * (ion.energy_ev / 1000.0));
            const double T_transferred = t_max_factor * ion.energy_ev * (sin_half_theta * sin_half_theta);

            // 3. Frenkel pair vacancy count & recoil cascade
            if (T_transferred > E_DISPLACEMENT) {
                const auto bin = static_cast<std::size_t>((ion.x_cm / config_.depth_max_cm) * config_.num_bins);
                if (bin < config_.num_bins) {
                    vacancies_hist_[bin]++;
                }
                if (ion.x_cm < 1.0e-7 && T_transferred > E_SURFACE_BIND) {
                    sputtered_count_++;
                }
                if (T_transferred > 100.0) {
                    simulate_recoil_cascade(ion.x_cm, ion.y_cm, T_transferred);
                }
            }

            ion.energy_ev -= T_transferred;

            // 4. Direction update
            const double theta_lab = sin_half_theta * (config_.m2_amu / (config_.m1_amu + config_.m2_amu));
            const double phi = (dist_distrib_(rng_) - 0.5) * 2.0 * theta_lab;

            const double new_dir_x = ion.dir_x * std::cos(phi) - ion.dir_y * std::sin(phi);
            const double new_dir_y = ion.dir_x * std::sin(phi) + ion.dir_y * std::cos(phi);
            const double norm = std::hypot(new_dir_x, new_dir_y);

            ion.dir_x = new_dir_x / norm;
            ion.dir_y = new_dir_y / norm;

            ion.x_cm += ion.dir_x * LAMBDA_STEP;
            ion.y_cm += ion.dir_y * LAMBDA_STEP;
        }

        if (ion.x_cm >= 0.0 && ion.x_cm < config_.depth_max_cm) {
            const auto bin = static_cast<std::size_t>((ion.x_cm / config_.depth_max_cm) * config_.num_bins);
            if (bin < config_.num_bins) {
                range_hist_[bin]++;
            }
        }
    }

    SimConfig config_;
    std::mt19937 rng_;
    std::uniform_real_distribution<double> dist_distrib_;
    std::vector<int> vacancies_hist_;
    std::vector<int> range_hist_;
    std::size_t sputtered_count_{0};
};

} // namespace ion_sim

int main() {
    ion_sim::SimConfig config;
    ion_sim::ImplantationSimulator sim(config);
    sim.run();
    sim.print_results();
    double r_p = sim.calculate_projected_range_nm();
    double delta_r_p = sim.calculate_straggling_nm(r_p);
    std::cout << "Mean Projected Range R_p: " << std::fixed << std::setprecision(2)
              << r_p << " nm\n";
    std::cout << "Calculated Straggling Delta R_p: " << std::fixed << std::setprecision(2)
              << delta_r_p << " nm\n";
    return 0;
}
```
:::

### Аналіз та інтерпретація результатів симуляції

Аналіз отриманого цифрового масиву дає змогу сформулювати три важливі фізичні висновки щодо розподілу домішок та дефектів у кремнії:

1. **Просторовий розсув максимуму дефектів та максимумів домішки**:
   Максимум концентрації утворених вакансій `R_d` завжди лежить ближче до поверхні пластини, ніж проектований пробіг самих імплантованих іонів `R_p`. Для Бору з енергією `50 кеВ` в кремнії `R_p ≈ 180 нм`, тоді як максимум руйнування ґратки спостерігається на глибині `R_d ≈ 140 нм`. Це пояснюється тим, що ядерне гальмування `S_n(E)` досягає максимуму при низьких енергіях іона (наприкінці його пробігу), але безпосередньо перед зупинкою залишкової кінетичної енергії вже не вистачає для створення нових каскадів.

2. **Просторове розділення вакансій та міжвузлів**:
   Поблизу поверхні кристала утворюється зона з надлишком вакансій (оскільки вибиті атоми кремнію отримують імпульс і рухаються далі вглиб), тоді як у районі `R_p` та за ним формується зона з надлишком міжвузлових атомів кремнію (Si self-interstitials).

3. **Залежність від атомного номера домішки**:
   Важкі іони (Миш'як, Сурма) викликають щільний каскад зіткнень, при якому траєкторія вторинних віддача-атомів перекривається, викликаючи суцільне аморфізування вже при невеликих дозах `10¹⁴ см⁻²`. Легкі іони (Бор) залишають після себе розріджений ланцюжок точкових дефектів.
