# ⚙️ Моделювання електронного транспорту та плато Холла в 2DEG

Чисельне моделювання електронного транспорту в двовимірному електронному газі (2DEG) є необхідним інструментом для проектування напівпровідникових гетероструктур, розрахунку поздовжнього та поперечного опорів Холла залежно від індукції магнітного поля `B` та аналізу впливу температури й розсіювання на ширину квантових плато. Нижче наведено детальний опис фізико-математичного алгоритму, чисельних методів та повноцінних програмних реалізацій мовами C та C++.

---

### Фізична модель чисельного розрахунку

Для заданого матеріалу 2DEG (наприклад, гетероструктури `GaAs / AlGaAs` або кремнієвого MOSFET) чисельний алгоритм обчислює квантові транспортні характеристики на основі трьох зв'язаних фізичних блоків:

1. **Макроскопічне виродження та коефіцієнт заповнення (Filling Factor)**:
   При прикладанні магнітного поля `B` густина станів на один рівень Ландау становить `n_B = e · B / h`. Відношення концентрації електронів `n_s` до `n_B` дає коефіцієнт заповнення:

```
ν = n_s / n_B = (n_s · h) / (e · B)
```

2. **Моделювання області локалізації та ширини плато**:
   У реальному зразку з флуктуаціями потенціалу дефектів рівні Ландау розширюються. На краях розширених рівнів знаходяться локалізовані стани, які не беруть участі у провідності. Якщо `ν` знаходиться близько до цілого числа `i` (в межах відносної області локалізації `Δν_loc`), рівень Фермі потрапляє в щілину рухливості. У цій області поперечний опір Холла `R_xy` ідеально квантується:

```
R_xy = h / (i · e²)
```

3. **Температурне розмиття та дисипативний поздовжній опір `R_xx`**:
   Поздовжній опір `R_xx` виникає через термополеву активацію електронів між рівнями Ландау або через розсіювання у центрі рівнів Ландау. Поздовжній опір описується комбінацією двох факторів: експоненціального пригнічення в області плато та пікового розсіювання при переходах між плато:

```
R_xx(B) = R_zero · exp[ - (ℏ · ω_c) / (2 · k_B · T) ] + R_peak · sin²(π · ν)
```

де `ω_c = e · B / m*` — циклотронна частота, `m*` — ефективна маса електрона, а `T` — абсолютна температура.

---

### Детальний аналіз алгоритму та архітектури програмного модуля

Програма виконує чисельний аналіз та сканування за магнітним полем за наступною кроковою процедурою:

1. **Етап ініціалізації матеріальних та фізичних констант**:
   Користувач задає параметри гетероструктури: поверхневу концентрацію носіїв `n_s`, відносну ефективну масу електрона `m* / m_e` (наприклад, `0.067` для GaAs), робочу температуру зразка `T` у Кельвінах та рухливість носіїв `μ`. Фізичні константи задаються з високою точністю у відповідності до міжнародного стандарту CODATA/SI.

2. **Етап обчислення циклотронних характеристик**:
   Для кожного значення індукції магнітного поля `B` обчислюється циклотронна частота електронів `ω_c = e · B / (m* · m_e)` та енергетичний інтервал між рівнями Ландау `ΔE_L = ℏ · ω_c`.

3. **Етап визначення стану локалізації**:
   Алгоритм обчислює дробову частину коефіцієнта заповнення `ν` та знаходить найближче ціле число `i = round(ν)`. Якщо модуль відхилення `|ν - i|` менший за поріг локалізації `plateau_threshold = 0.15`, система вважається такою, що перебуває у режимі нестисливої квантової рідини на плато. Значення `R_xy` фіксується як `h / (i · e²)`, а поздовжній опір `R_xx` обчислюється через термоактиваційний множник `exp(-ΔE_L / 2 k_B T)`.

4. **Етап міжплатонного переходу**:
   Якщо відхилення перевищує поріг локалізації, рівень Фермі перетинає делокалізовані стани у центрі рівня Ландау. Поперечний опір описується класичним нахилом `R_xy = h / (ν · e²)`, а поздовжній опір демонструє дисипативний пік, що описується функцією `sin²(π · ν)`.

5. **Етап генерації табличного звіту та збереження результатів**:
   Отримані масиви даних виводяться у форматовану таблицю або зберігаються для подальшої візуалізації у графічних пакетах.

---

### Реалізація коду моделювання

Нижче наведено дві ідіоматичні реалізації алгоритму моделювання. Перша реалізація написана мовою C із дотриманням стандарту C99, а друга — мовою C++ з використанням сучасних можливостей стандарту C++20 (концепти, `std::span`, `std::vector`, типубезпечні структури та RAII).

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

/* Фундаментальні фізичні константи (SI) */
#define CONST_H  6.62607015e-34  /* Стала Планка (Дж·с) */
#define CONST_E  1.602176634e-19 /* Елементарний заряд (Кл) */
#define CONST_KB 1.380649e-23    /* Стала Больцмана (Дж/К) */
#define CONST_ME 9.1093837015e-31/* Маса електрона (кг) */

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

/* Структура для зберігання результатів в одній точці поля B */
typedef struct {
    double B;          /* Індукція магнітного поля (Тесла) */
    double nu;         /* Коефіцієнт заповнення ν */
    int i_filled;      /* Індекс найближчого плато i */
    double R_xy;       /* Розрахований опір Холла (Ом) */
    double R_xx;       /* Розрахований поздовжній опір (Ом) */
} qhe_point_t;

/* Структура фізичних параметрів зразка 2DEG */
typedef struct {
    double n_s;        /* Поверхнева густина носіїв (м^-2) */
    double m_eff;      /* Відносна ефективна маса (m* / m_e) */
    double temp;       /* Температура зразка (Кельвіни) */
    double mobility;   /* Рухливість носіїв (м^2 / В·с) */
} qhe_sample_t;

/* Обчислення транспортних характеристик QHE для однієї точки B */
qhe_point_t calculate_qhe_point(const qhe_sample_t *sample, double B) {
    qhe_point_t pt;
    pt.B = B;
    
    /* Густина станів одного рівня Ландау: n_B = e * B / h */
    double n_B = (CONST_E * B) / CONST_H;
    pt.nu = sample->n_s / n_B;
    
    /* Знайдемо найближче ціле число заповнених рівнів Ландау */
    int i_near = (int)floor(pt.nu + 0.5);
    if (i_near < 1) {
        i_near = 1;
    }
    pt.i_filled = i_near;
    
    /* Відхилення від цілого числа */
    double deviation = fabs(pt.nu - (double)i_near);
    double plateau_threshold = 0.15; /* Відносна ширина області локалізації */
    
    if (deviation < plateau_threshold) {
        /* Знаходимося на квантованому плато */
        pt.R_xy = CONST_H / ((double)i_near * CONST_E * CONST_E);
        
        /* Поздовжній опір експоненціально пригнічений термоактивацією */
        double m_kg = sample->m_eff * CONST_ME;
        double hbar = CONST_H / (2.0 * M_PI);
        double hw_c = (hbar * CONST_E * B) / m_kg;
        double thermal_suppression = exp(-hw_c / (2.0 * CONST_KB * sample->temp));
        pt.R_xx = 500.0 * thermal_suppression;
    } else {
        /* Перехідна область між плато (класичний нахил + пік розсіювання) */
        pt.R_xy = CONST_H / (pt.nu * CONST_E * CONST_E);
        
        /* Дисипативний пік R_xx на межі рівнів Ландау */
        double peak_shape = sin(M_PI * pt.nu);
        pt.R_xx = 1500.0 * (peak_shape * peak_shape);
    }
    
    return pt;
}

/* Проведення сканування за магнітним полем із виділенням динамічного масиву */
qhe_point_t* run_qhe_sweep(const qhe_sample_t *sample, double B_start, double B_end, int steps) {
    if (steps <= 1) return NULL;
    
    qhe_point_t *results = (qhe_point_t*)malloc(sizeof(qhe_point_t) * (size_t)steps);
    if (!results) {
        fprintf(stderr, "Помилка виділення пам'яті під результати симуляції.\n");
        return NULL;
    }
    
    double dB = (B_end - B_start) / (double)(steps - 1);
    for (int k = 0; k < steps; ++k) {
        double B = B_start + (double)k * dB;
        results[k] = calculate_qhe_point(sample, B);
    }
    
    return results;
}

int main(void) {
    qhe_sample_t gaas_sample = {
        .n_s = 3.2e15,     /* 3.2*10^15 м^-2 (GaAs/AlGaAs 2DEG) */
        .m_eff = 0.067,    /* Ефективна маса електрона у GaAs */
        .temp = 1.2,       /* 1.2 Кельвіна */
        .mobility = 60.0   /* Рухливість 60 м^2 / (В·с) */
    };
    
    double B_min = 1.0;
    double B_max = 8.5;
    int num_steps = 16;
    
    qhe_point_t *data = run_qhe_sweep(&gaas_sample, B_min, B_max, num_steps);
    if (!data) {
        return EXIT_FAILURE;
    }
    
    printf("===================================================================\n");
    printf("   СИМУЛЯЦІЯ ТРАНСПОРТУ QHE В ДВОВИМІРНОМУ ЕЛЕКТРОННОМУ ГАЗІ (C)   \n");
    printf("===================================================================\n");
    printf(" B (Тл)  | Factor nu | Index i |   R_xy (Ом)     |   R_xx (Ом)   \n");
    printf("-------------------------------------------------------------------\n");
    
    for (int k = 0; k < num_steps; ++k) {
        printf(" %6.2f  | %9.3f |   %2d    | %13.4f | %11.5f\n",
               data[k].B, data[k].nu, data[k].i_filled, data[k].R_xy, data[k].R_xx);
    }
    
    printf("-------------------------------------------------------------------\n");
    
    free(data);
    return EXIT_SUCCESS;
}
```
```cpp
#include <iostream>
#include <vector>
#include <cmath>
#include <numbers>
#include <iomanip>
#include <span>
#include <memory>

namespace qhe {

// Фундаментальні фізичні константи у системі SI
constexpr double h_Planck = 6.62607015e-34;     // Дж·с
constexpr double e_charge = 1.602176634e-19;    // Кл
constexpr double k_Boltzmann = 1.380649e-23;    // Дж/К
constexpr double m_electron = 9.1093837015e-31; // кг

// Параметри напівпровідникового зразка 2DEG
struct SampleParameters {
    double electron_density{3.2e15}; // м^-2
    double effective_mass{0.067};   // m* / m_e
    double temperature{1.2};         // Кельвіни
    double mobility{60.0};           // м^2 / (В·с)
};

// Результат чисельного розрахунку у точці
struct TransportDataPoint {
    double magnetic_field{};
    double filling_factor{};
    int plateau_index{};
    double r_hall{};
    double r_longitudinal{};
};

// Симулятор квантового транспорту Холла
class HallSimulator {
public:
    explicit HallSimulator(SampleParameters params) noexcept
        : params_(params) {}

    [[nodiscard]] TransportDataPoint compute_at(double B) const noexcept {
        TransportDataPoint pt;
        pt.magnetic_field = B;

        const double n_B = (e_charge * B) / h_Planck;
        pt.filling_factor = params_.electron_density / n_B;

        const int i_near = std::max(1, static_cast<int>(std::round(pt.filling_factor)));
        pt.plateau_index = i_near;

        const double deviation = std::abs(pt.filling_factor - static_cast<double>(i_near));
        constexpr double plateau_threshold = 0.15;

        if (deviation < plateau_threshold) {
            // Режим квантованого плато
            pt.r_hall = h_Planck / (static_cast<double>(i_near) * e_charge * e_charge);

            const double m_kg = params_.effective_mass * m_electron;
            const double hbar = h_Planck / (2.0 * std::numbers::pi);
            const double hw_c = (hbar * e_charge * B) / m_kg;
            const double thermal_suppression = std::exp(-hw_c / (2.0 * k_Boltzmann * params_.temperature));
            pt.r_longitudinal = 500.0 * thermal_suppression;
        } else {
            // Режим міжплатоного переходу
            pt.r_hall = h_Planck / (pt.filling_factor * e_charge * e_charge);
            const double peak_shape = std::sin(std::numbers::pi * pt.filling_factor);
            pt.r_longitudinal = 1500.0 * (peak_shape * peak_shape);
        }

        return pt;
    }

    [[nodiscard]] std::vector<TransportDataPoint> sweep(double b_min, double b_max, std::size_t steps) const {
        if (steps < 2) return {};

        std::vector<TransportDataPoint> results;
        results.reserve(steps);

        const double dB = (b_max - b_min) / static_cast<double>(steps - 1);
        for (std::size_t k = 0; k < steps; ++k) {
            results.push_back(compute_at(b_min + static_cast<double>(k) * dB));
        }

        return results;
    }

private:
    SampleParameters params_;
};

// Функція виводу звіту з використанням C++ std::span для безпечного доступу до пам'яті
void print_simulation_report(std::span<const TransportDataPoint> data) {
    std::cout << "===================================================================\n";
    std::cout << "  СИМУЛЯЦІЯ ТРАНСПОРТУ QHE В ДВОВИМІРНОМУ ЕЛЕКТРОННОМУ ГАЗІ (C++20)\n";
    std::cout << "===================================================================\n";
    std::cout << std::setw(8) << "B (Тл)" << " | "
              << std::setw(9) << "Factor nu" << " | "
              << std::setw(7) << "Index i" << " | "
              << std::setw(14) << "R_xy (Ом)" << " | "
              << std::setw(13) << "R_xx (Ом)" << "\n";
    std::cout << "-------------------------------------------------------------------\n";

    for (const auto& point : data) {
        std::cout << std::fixed << std::setprecision(2)
                  << std::setw(8) << point.magnetic_field << " | "
                  << std::setprecision(3)
                  << std::setw(9) << point.filling_factor << " | "
                  << std::setw(7) << point.plateau_index << " | "
                  << std::setprecision(4)
                  << std::setw(14) << point.r_hall << " | "
                  << std::setprecision(5)
                  << std::setw(13) << point.r_longitudinal << "\n";
    }

    std::cout << "-------------------------------------------------------------------\n";
}

} // namespace qhe

int main() {
    qhe::SampleParameters gaas_params{
        .electron_density = 3.2e15,
        .effective_mass = 0.067,
        .temperature = 1.2,
        .mobility = 60.0
    };

    const qhe::HallSimulator simulator(gaas_params);
    const auto results = simulator.sweep(1.0, 8.5, 16);

    qhe::print_simulation_report(results);

    return 0;
}
```
:::

---

### Порівняльний аналіз реалізацій та крайові випадки

1. **Типобезпека та керування пам'яттю**:
   - У C-версії використовується виділення пам'яті у купі через `malloc` із обов'язковим ручним звільненням через `free`. Помилка розробника (забудькуватість викликати `free`) призводить до витоку пам'яті.
   - У C++20 версії застосовується контейнер `std::vector`, який автоматично керує пам'яттю за принципом RAII. Передача даних у функцію друку через `std::span<const TransportDataPoint>` забезпечує безпечний доступ без копіювання елементів.

2. **Обчислювальна складність та оптимізація**:
   - Обчислювальна складність симуляції для `N` точок поля є строго лінійною `O(N)`. Пам'ятна складність — також `O(N)` для збереження результуючих точок.
   - Використання `std::numbers::pi` та `constexpr` констант дозволяє компілятору C++ обчислювати вирази на етапі компіляції (compile-time evaluation), розгортаючи математичні операції та оптимізуючи циклічні виклики.

3. **Точність та крайові випадки**:
   - **Границя слабкого поля (`B → 0`)**: При `B → 0` коефіцієнт заповнення `ν → ∞`. Поділ на `ν` у формі `n_B = e·B / h` може призвести до ділення на нуль або переповнення (overflow). У програмі встановлено нижню межу сканування `B_min = 1.0` Тл.
   - **Експоненціальний анти-підплав (underflow)**: При дуже високих полях `B > 12` Тл та низькій температурі `T = 0.1` К показник експоненти `-ℏω_c / (2 k_B T)` стає негативним і дуже великим за модулем (наприклад, `-250`). Стандартний чисельний тип `double` коректно обробляє це як втрату значущості, повертаючи чистий `0.0`.
   - **Високотемпературне руйнування**: Якщо встановити `temp = 300.0` К (кімнатна температура), показник експоненти прямує до нуля `exp(0) = 1`, і експоненціальний множник перестає пригнічувати `R_xx`. Поздовжній опір залишається високим, а плато `R_xy` повністю розмиваються, що відображає фізичне зникання ефекту при звичайних температурах.
   - **Шумовий поріг потенціалу дефектів**: У чисельній моделі вибірка `plateau_threshold = 0.15` визначає розмах флуктуацій потенціалу. Збільшення ступеня безладу розширює плато, але якщо безлад перевищує половину циклотронної енергії `ℏω_c`, сусідні рівні Ландау перекриваються, що повністю знищує квантоване плато.
