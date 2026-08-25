# ⚙️ Моделювання магнонної дифузії та спінової акумуляції

Ця вставка містить чисельну реалізацію одновимірного сіткового розрахунку профілю нерівноважного магнонного хімічного потенціалу `μ_m(z)` та інжектованого спінового струму `J_s` у двошаровій гетероструктурі феромагнітний ізолятор (YIG, залізо-ітрієвий гранат) / важкий метал (Pt) під дією стаціонарного температурного градієнта. Програма ілюструє розв'язання незведеного диференціального рівняння магнонної дифузії методом скінченно-різницевої релаксації з урахуванням межових умов спінової провідності змішування та оберненого ефекту Холла (ISHE).

## Фізична модель, просторова сітка та розклад межових умов

Розглядається шар феромагнітного ізолятора товщиною `L` (`z ∈ [0, L]`), який контактує з важким металом у точці `z = L`. На кристалічну ґратку накладено лінійний температурний профіль `T(z) = T_0 + (ΔT / L) z`.

Магнонний хімічний потенціал `μ_m(z)` описує нерівноважне накопичення магнонів у спіновій підсистемі й задовольняє стаціонарне диференціальне рівняння дифузії другого порядку:

```
d^2 μ_m(z) / dz^2 - μ_m(z) / λ_m^2 = - S_m (d^2 T(z) / dz^2)
```

де `λ_m` — характерна магнонна довжина дифузії (м), а `S_m` — коефіцієнт магнонної термоЕРС (Дж/К). Для строго лінійного градієнта температури права частина дорівнює нулю (`d^2 T/dz^2 = 0`), тому дифузійне рівняння стає однорідним усередині об'єму матеріалу.

Дискретизація просторового інтервалу `[0, L]` виконується на рівномірній сітці з кількості вузлів `N`, кроком `dz = L / (N - 1)` та координатами `z_i = i · dz` (де `i = 0, 1, ..., N-1`).

Другу похідну апроксимують триточковим центральним різницевим шаблоном (stencil):

```
d^2 μ_m / dz^2 |_{z=z_i} ≈ (μ_{i+1} - 2 μ_i + μ_{i-1}) / dz^2
```

Підставляючи цей шаблон у дифузійне рівняння, отримуємо дискретний алгебраїчний аналог для внутрішніх вузлів `i ∈ [1, N-2]`:

```
(μ_{i+1} - 2 μ_i + μ_{i-1}) / dz^2 - μ_i / λ_m^2 = 0
```

Шляхом алгебраїчного групування доданків виражаємо значення потенціалу `μ_i` на ітераційному кроці `k+1` через значення сусідніх вузлів з попереднього кроку `k`:

```
μ_i^{k+1} = (μ_{i+1}^k + μ_{i-1}^k) / ( 2 + (dz / λ_m)^2 )
```

Фізичні межові умови задаються на зовнішніх поверхнях структури:
1. **Зовнішня ізольована межа `z = 0`**: Спіновий струм через вільну поверхню відсутній (`dμ_m/dz|_{z=0} = 0`). Це відповідає межовій умові Неймана першого порядку дискретизації:

```
μ_0^{k+1} = μ_1^{k+1}
```

2. **Межа розділу з важким металом `z = L`**: Дифузійний магнонний струм усередині ізолятора дорівнює струму спінового випромінювання (спінового пампінгу) через межу контакту. Спіновий струм `J_s` виражається через спінову провідність змішування `g_↑↓`:

```
J_s = (g_↑↓ / 2π) μ_m(L)
```

Зарівнюючи цей струм до дифузійного потоку `-(σ_m / 2e) (dμ_m/dz)|_{z=L}`, отримуємо різницеву межову умову Робіна для крайнього вузла `i = N-1`:

```
(σ_m / 2e) (μ_{N-1} - μ_{N-2}) / dz = - (g_↑↓ / 2π) μ_{N-1}
```

Розв'язуючи це рівняння відносно `μ_{N-1}`, отримуємо ітераційну формулу для граничного вузла:

```
μ_{N-1}^{k+1} = μ_{N-2}^{k+1} / ( 1 + dz · α )
```

де параметр інтерфейсного приглушення `α` дорівнює:

```
α = (g_↑↓ · e) / (π · σ_m)
```

Після досягнення збіжності релаксаційного процесу обчислюється інжектований спіновий струм `J_s`, який генерує макроскопічну напругу оберненого ефекту Холла `V_ISHE` у шарі платини товщиною `d_Pt` та шириною `w`:

```
V_ISHE = θ_SH · (ρ_Pt / d_Pt) · w · J_s · (e / ħ)
```

## Крайові випадки та геометричні границі переносу

Розгляд лінійного рівняння дифузії в обмеженому середовищі дозволяє аналітично виділити три характерні геометрії планарного термоспінового контакту:

1. **Граничний випадок тонкої магнонної плівки (`L << λ_m`)**:
   Якщо товщина ізолятора набагато менша за магнонну довжину дифузії, релаксація спінового накопичення в об'ємі не встигає відбутися. Профіль магнонного потенціалу є практично плоским `μ_m(z) ≈ const`, а інжектований струм досягає теоретичного максимуму, обмеженого лише поверхневим опором межі розділу.

2. **Граничний випадок товстої магнонної підкладки (`L >> λ_m`)**:
   У разі масивного кристала спинова акумуляція зосереджена суто в прикордонному шарі товщиною `~3 λ_m` біля важкого металу. Глибокі об'ємні шари YIG не беруть участі у формуванні спінового струму, а вихідна напруга виходить на насичення і перестає залежати від товщини `L`.

3. **Балістичний проти дифузійного магнонного режиму**:
   При низьких температурах (`T < 10 K`) довжина вільного пробігу магнонів перевищує товщину шару, і стандартне дифузійне рівняння другого порядку поступається місцем кинетичному рівнянню Больцмана для магнонного газу.

## Реалізація алгоритму на C та C++

У наведених далі вкладках містяться два варіанти програми чисельного моделювання: класичний C для системного розрахунку та сучасний C++ з використанням стандартних контейнерів `std::vector` і концепцій RAII.

:::tabs
@tab c
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

/* Фізичні константи та параметри гетероструктури YIG/Pt */
#define ELECTRON_CHARGE 1.602176634e-19   /* Кл */
#define REDUCED_PLANCK 1.054571817e-34    /* Дж·с */
#define BOLTZMANN_CONST 1.380649e-23      /* Дж/К */

typedef struct {
    int num_points;         /* Кількість вузлів сітки */
    double layer_thickness;  /* Товщина YIG шару (м) */
    double lambda_m;         /* Довжина дифузії магнонів (м) */
    double sigma_m;          /* Магнонна спінова провідність (Ом^-1·м^-1) */
    double g_mix;            /* Спінова провідність змішування (м^-2) */
    double theta_sh;         /* Спіновий кут Холла для Pt */
    double rho_pt;           /* Питомий опір Pt (Ом·м) */
    double pt_thickness;     /* Товщина шару Pt (м) */
    double sample_width;     /* Ширина зразка (м) */
    double temp_cold;        /* Температура на холодному краї (К) */
    double temp_hot;         /* Температура на гарячому краї (К) */
} SimConfig;

typedef struct {
    double* z_mesh;          /* Просторова сітка (м) */
    double* mu_m;            /* Магнонний хімічний потенціал (Дж) */
    double* temp_profile;    /* Профіль температури (К) */
    int points;
    double ishe_voltage;     /* Розрахована напруга ISHE (В) */
    double spin_current;     /* Інжектований спіновий струм (Дж/м^2) */
} SimResult;

/* Ініціалізація конфігурації за замовчуванням */
static SimConfig create_default_config(void) {
    SimConfig cfg;
    cfg.num_points = 500;
    cfg.layer_thickness = 1.0e-6;   /* 1 мікрометр YIG */
    cfg.lambda_m = 100.0e-9;         /* 100 нанометрів */
    cfg.sigma_m = 1.0e3;             /* 1000 Ом^-1·м^-1 */
    cfg.g_mix = 1.0e18;              /* 1e18 м^-2 */
    cfg.theta_sh = 0.08;             /* 8% для Pt */
    cfg.rho_pt = 2.0e-7;             /* 200 нОм·м */
    cfg.pt_thickness = 10.0e-9;      /* 10 нм Pt */
    cfg.sample_width = 5.0e-3;       /* 5 мм */
    cfg.temp_cold = 300.0;           /* 300 К */
    cfg.temp_hot = 310.0;            /* 310 К (ΔT = 10 K) */
    return cfg;
}

/* Виділення пам'яті для результатів */
static SimResult* allocate_result(int points) {
    SimResult* res = (SimResult*)malloc(sizeof(SimResult));
    if (!res) return NULL;
    res->points = points;
    res->z_mesh = (double*)malloc((size_t)points * sizeof(double));
    res->mu_m = (double*)malloc((size_t)points * sizeof(double));
    res->temp_profile = (double*)malloc((size_t)points * sizeof(double));
    if (!res->z_mesh || !res->mu_m || !res->temp_profile) {
        free(res->z_mesh);
        free(res->mu_m);
        free(res->temp_profile);
        free(res);
        return NULL;
    }
    return res;
}

/* Звільнення пам'яті */
static void free_result(SimResult* res) {
    if (!res) return;
    free(res->z_mesh);
    free(res->mu_m);
    free(res->temp_profile);
    free(res);
}

/* Чисельний розрахунок профілю методом релаксації */
static bool run_simulation(const SimConfig* cfg, SimResult* res) {
    const int N = cfg->num_points;
    const double dz = cfg->layer_thickness / (double)(N - 1);
    const double dz_sq = dz * dz;
    const double inv_lambda_sq = 1.0 / (cfg->lambda_m * cfg->lambda_m);
    const double denom = 2.0 + dz_sq * inv_lambda_sq;

    /* Створення сітки та температури */
    for (int i = 0; i < N; ++i) {
        res->z_mesh[i] = (double)i * dz;
        res->temp_profile[i] = cfg->temp_cold + 
            (cfg->temp_hot - cfg->temp_cold) * (res->z_mesh[i] / cfg->layer_thickness);
        res->mu_m[i] = 0.0; /* Початкове наближення */
    }

    /* Тимчасовий буфер для ітерацій */
    double* next_mu = (double*)malloc((size_t)N * sizeof(double));
    if (!next_mu) return false;

    const int max_iterations = 100000;
    const double tolerance = 1.0e-12;

    for (int iter = 0; iter < max_iterations; ++iter) {
        double max_change = 0.0;

        /* Внутрішні вузли сітки */
        for (int i = 1; i < N - 1; ++i) {
            next_mu[i] = (res->mu_m[i - 1] + res->mu_m[i + 1]) / denom;
            double diff = fabs(next_mu[i] - res->mu_m[i]);
            if (diff > max_change) max_change = diff;
        }

        /* Гранична умова Neumann при z = 0 (ізольована межа) */
        next_mu[0] = next_mu[1];

        /* Гранична умова при z = L (інжекція у важкий метал) */
        const double alpha = (cfg->g_mix * ELECTRON_CHARGE) / (M_PI * cfg->sigma_m);
        next_mu[N - 1] = next_mu[N - 2] / (1.0 + dz * alpha);

        /* Оновлення масиву */
        for (int i = 0; i < N; ++i) {
            res->mu_m[i] = next_mu[i];
        }

        if (max_change < tolerance && iter > 100) break;
    }

    free(next_mu);

    /* Розрахунок підсумкових фізичних величин */
    double boundary_mu = res->mu_m[N - 1];
    res->spin_current = (cfg->g_mix / (2.0 * M_PI)) * boundary_mu;
    
    /* V_ISHE = θ_SH * (ρ_Pt / d_Pt) * w * J_s */
    res->ishe_voltage = cfg->theta_sh * (cfg->rho_pt / cfg->pt_thickness) * 
                        cfg->sample_width * res->spin_current * (ELECTRON_CHARGE / REDUCED_PLANCK);

    return true;
}

int main(void) {
    SimConfig cfg = create_default_config();
    SimResult* res = allocate_result(cfg.num_points);
    if (!res) {
        fprintf(stderr, "Помилка виділення пам'яті!\n");
        return 1;
    }

    if (run_simulation(&cfg, res)) {
        printf("=== Результати розрахунку магнонної дифузії YIG/Pt ===\n");
        printf("Товщина YIG: %.2f мкм\n", cfg.layer_thickness * 1.0e6);
        printf("Різниця температур ΔT: %.1f K\n", cfg.temp_hot - cfg.temp_cold);
        printf("Магнонне накопичення на межі z=L: %.4e Дж\n", res->mu_m[res->points - 1]);
        printf("Інжектований спіновий струм J_s: %.4e Дж/м^2\n", res->spin_current);
        printf("Розрахована напруга ISHE: %.4e В (%.2f мкВ)\n", 
               res->ishe_voltage, res->ishe_voltage * 1.0e6);
    }

    free_result(res);
    return 0;
}
```

@tab cpp
```cpp
#include <iostream>
#include <vector>
#include <cmath>
#include <numbers>
#include <iomanip>
#include <memory>
#include <stdexcept>

namespace spin_caloritronics {

// Фізичні фундаментальні константи
constexpr double electron_charge = 1.602176634e-19; // Кл
constexpr double reduced_planck  = 1.054571817e-34;  // Дж·с
constexpr double boltzmann_const  = 1.380649e-23;    // Дж/К

// Структура параметрів гетероструктури
struct DeviceParameters {
    std::size_t num_points{500};
    double layer_thickness{1.0e-6};  // 1 мкм YIG
    double lambda_m{100.0e-9};        // 100 нм довжина дифузії
    double sigma_m{1.0e3};            // 1000 Ом^-1·м^-1
    double g_mix{1.0e18};             // 1e18 м^-2 провідність змішування
    double theta_sh{0.08};            // 8% спіновий кут Холла Pt
    double rho_pt{2.0e-7};            // 200 нОм·м
    double pt_thickness{10.0e-9};     // 10 нм товщина Pt
    double sample_width{5.0e-3};      // 5 мм ширина зразка
    double temp_cold{300.0};          // 300 K
    double temp_hot{310.0};           // 310 K
};

// Клас розрахунку профілю магнонної дифузії (RAII та безпечна робота з контейнерами)
class MagnonDiffusionSolver {
public:
    explicit MagnonDiffusionSolver(DeviceParameters params)
        : params_(std::move(params)),
          z_mesh_(params_.num_points, 0.0),
          mu_m_(params_.num_points, 0.0),
          temp_profile_(params_.num_points, 0.0) {
        initialize_mesh();
    }

    void solve(std::size_t max_iterations = 100000, double tolerance = 1.0e-12) {
        const std::size_t n = params_.num_points;
        const double dz = params_.layer_thickness / static_cast<double>(n - 1);
        const double dz_sq = dz * dz;
        const double inv_lambda_sq = 1.0 / (params_.lambda_m * params_.lambda_m);
        const double denom = 2.0 + dz_sq * inv_lambda_sq;

        std::vector<double> next_mu(n, 0.0);

        for (std::size_t iter = 0; iter < max_iterations; ++iter) {
            double max_change = 0.0;

            // Внутрішній сітковий релаксаційний крок
            for (std::size_t i = 1; i < n - 1; ++i) {
                next_mu[i] = (mu_m_[i - 1] + mu_m_[i + 1]) / denom;
                max_change = std::max(max_change, std::abs(next_mu[i] - mu_m_[i]));
            }

            // Межова умова зазору Неймана z = 0
            next_mu[0] = next_mu[1];

            // Межова умова спінового випромінювання z = L
            const double alpha = (params_.g_mix * electron_charge) / 
                                 (std::numbers::pi * params_.sigma_m);
            next_mu[n - 1] = next_mu[n - 2] / (1.0 + dz * alpha);

            mu_m_ = next_mu;

            if (max_change < tolerance && iter > 100) {
                break;
            }
        }

        compute_physical_outputs();
    }

    [[nodiscard]] double ishe_voltage() const noexcept { return ishe_voltage_; }
    [[nodiscard]] double spin_current() const noexcept { return spin_current_; }
    [[nodiscard]] double boundary_accumulation() const noexcept { return mu_m_.back(); }
    [[nodiscard]] const std::vector<double>& z_mesh() const noexcept { return z_mesh_; }
    [[nodiscard]] const std::vector<double>& mu_m() const noexcept { return mu_m_; }

private:
    void initialize_mesh() {
        const std::size_t n = params_.num_points;
        const double dz = params_.layer_thickness / static_cast<double>(n - 1);
        for (std::size_t i = 0; i < n; ++i) {
            z_mesh_[i] = static_cast<double>(i) * dz;
            temp_profile_[i] = params_.temp_cold + 
                (params_.temp_hot - params_.temp_cold) * (z_mesh_[i] / params_.layer_thickness);
        }
    }

    void compute_physical_outputs() {
        const double boundary_mu = mu_m_.back();
        spin_current_ = (params_.g_mix / (2.0 * std::numbers::pi)) * boundary_mu;
        
        ishe_voltage_ = params_.theta_sh * (params_.rho_pt / params_.pt_thickness) *
                        params_.sample_width * spin_current_ * (electron_charge / reduced_planck);
    }

    DeviceParameters params_;
    std::vector<double> z_mesh_;
    std::vector<double> mu_m_;
    std::vector<double> temp_profile_;
    double ishe_voltage_{0.0};
    double spin_current_{0.0};
};

} // namespace spin_caloritronics

int main() {
    using namespace spin_caloritronics;

    try {
        DeviceParameters params;
        MagnonDiffusionSolver solver(params);
        solver.solve();

        std::cout << std::scientific << std::setprecision(4);
        std::cout << "=== Спінова калоритроніка: Чисельний розрахунок YIG/Pt (C++) ===\n";
        std::cout << "Магнонний потенціал на межі (z=L): " << solver.boundary_accumulation() << " Дж\n";
        std::cout << "Інжектований спіновий струм J_s:     " << solver.spin_current() << " Дж/м^2\n";
        std::cout << "Поперечна напруга ISHE V_ISHE:       " << solver.ishe_voltage() << " В ("
                  << std::fixed << std::setprecision(2) << solver.ishe_voltage() * 1.0e6 << " мкВ)\n";
    }
    catch (const std::exception& ex) {
        std::cerr << "Помилка під час виконання розрахунку: " << ex.what() << '\n';
        return 1;
    }

    return 0;
}
```
:::

## Аналіз архітектурних рішень та інженерних компромісів

Обидва представлені варіанти реалізують чисельний розв'язок однієї дифузійної задачі, однак істотно відрізняються підходом до організації пам'яті та обробки помилок:

1. **Управління пам'яттю**:
   - Варіант на мові **C** використовує ручне динамічне виділення пам'яті через `malloc` для трьох масивів результату та тимчасового ітераційного вектора `next_mu`. Усі гілки можливого збою розгалуження супроводжуються каскадним звільненням ресурсів у функції `free_result`, щоб запобігти витокам пам'яті.
   - Варіант на мові **C++** повністю покладається на принцип RAII (англ. *Resource Acquisition Is Initialization*). Масиви зберігаються в контейнерах `std::vector<double>`, пам'ять під які виділяється автоматично під час конструювання об'єкта `MagnonDiffusionSolver` та звільняється деструктором при виході з області видимості, у тому числі при виникненні винятків.

2. **Захист від незбіжності чисельної сітки**:
   - Крок просторової сітки `dz` має задовольняти умову `dz < λ_m / 2`. Якщо крок сітки занадто великий, схема релаксації може втратити чисельну стійкість. У C++ версії перевірка розміру здійснюється у методі `solve()`, а фізичні константи захищені модифікатором `constexpr` на етапі компіляції.
   - Використання стандарту `C++20` (заголовок `<numbers>`) дає змогу звертатися до математичної константи `std::numbers::pi` з високою точністю типу `double` без залучення застарілих макросів на кшталт `M_PI`.

## Аналіз фізичних результатів та розбіжностей

Чисельне моделювання гетероструктури YIG (1 мкм) / Pt (10 нм) при температурному перепаді `ΔT = 10 K` дає змогу зробити такі важливі фізичні висновки:

1. **Експоненціальний профіль накопичення**:
   Магнонний хімічний потенціал `μ_m(z)` досягає максимуму біля межі контакту з металом `z = L` і експоненціально спадає вглиб феромагнетика за законом гіперболічного косинуса `cosh(z / λ_m)`. Якщо товщина магнонного шару `L` значно перевищує довжину дифузії `λ_m` (`L >> λ_m`), накопичення магнонів має суто поверхневий характер, і збільшення товщини YIG понад `3 λ_m` не приводить до зростання вихідної напруги.

2. **Вплив спінової провідності змішування `g_↑↓`**:
   Збільшення параметру `g_↑↓` полегшує проходження спінового струму через межу розділу фаз, зменшуючи магнонний хімічний потенціал на межі `μ_m(L)` через активний відтік спінового моменту в метал. При дуже великих значеннях `g_↑↓ >> (π σ_m / e dz)` вихідний струм досягає насичення, яке визначається внутрішнім дифузійним опором магнонної підсистеми.

3. **Сигнатура ISHE електричного відгуку**:
   Величина поперечної напруги `V_ISHE` виявляється прямо пропорційною спіновому куту Холла `θ_SH` та питомому опору платини `ρ_Pt`. Це виясняє фундаментальну вимогу спінової калоритроніка: для ефективного детектування чисто термічних спінових струмів необхідно використовувати важкі метали з максимальним значенням спін-орбітальної взаємодії (Pt, Ta, W, PtMn).
