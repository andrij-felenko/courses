# ⚙️ Інтегратор 3D-діаграми спрямованості та розрахунок підсилення

Обчислення повної випромінюваної потужності `P_rad`, максимального коефіцієнта спрямованої дії `D_max` та тілесного кута `Ω_A` за даними вимірювання чи моделювання 3D-діаграми спрямованості вимагає дискретного чисельного інтегрування двовимірного масиву на сфері.

У цій вставці подано детальний аналіз алгоритму чисельного інтегрування сферичних діаграм спрямованості, методологію обробки граничних умов на полюсах сфери, аналіз оптимізації пам'яті та дві повноцінні ідіоматичні реалізації програми мовами C та C++.

---

### Фізичний контекст та алгоритм обчислень

У реальних вимірювальних комплексах безвідлунних камер поворотний пристрій (*positioner*) сканує антену по двох кутових координатах: зенітному куту `θ` (від `0°` до `180°`) та азимутальному куту `ϕ` (від `0°` до `360°`). Сканер видає двовимірну матрицю виміряних значень інтенсивності випромінювання `U(i, j)` або амплітуди електричного поля `E(i, j)`.

Для розрахунку точного підсилення антени алгоритм виконує наступні математичні та обчислювальні кроки:

1. **Ініціалізація сферичної сітки.** Визначаються кроки дискретизації за кутами: `Δθ = π / (N_θ - 1)` та `Δϕ = 2·π / (N_ϕ - 1)`.
2. **Наповнення матриці полів.** Масив `U[i][j]` заповнюється виміряними значеннями інтенсивності хвилі у ватах на стерадіан (або пропорційними значеннями `|E|²`).
3. **Пошук максимуму `U_max`.** У циклі сканування знаходиться абсолютний максимум інтенсивності випромінювання `U_max = max(U[i][j])` та кутові координати `(θ_max, ϕ_max)` головного променя.
4. **Обчислення повної потужності `P_rad`.** Застосовується формула чисельного інтегрування за методом трапецій з урахуванням вагового множника `sin(θ_i)`:
   ```
   P_rad ≈ Δθ · Δϕ · ∑ᵢ₌₀ᴺᵗʰᵉᵗᵃ⁻¹ ∑ⱼ₌₀ᴺᵖʰⁱ⁻¹ w_θ(i) · w_ϕ(j) · U(i, j) · sin(θ_i)
   ```
   де `w_θ(i)` та `w_ϕ(j)` — вагові коефіцієнти методу трапецій (`0.5` для крайніх точок сітки та `1.0` для внутрішніх точок).
5. **Обчислення 3D-спрямованості.** Спрямованість у лінійній шкалі розраховується як `D_max = (4 · π · U_max) / P_rad`.
6. **Конвертація у децибели.** Підсилення у дБі обчислюється як `D_dBi = 10 · log10(D_max)`.
7. **Розрахунок тілесного кута.** Еквівалентний тілесний кут променя обчислюється за формулою `Ω_A = (4 · π) / D_max`.

---

### Обробка крайових випадків та перевірка еталонних моделей

При створенні інженерного програмного забезпечення для розрахунку 3D-діаграм важливо передбачити та правильно обробити наступні крайові випадки:

- **Нульова або вкрай мала потужність (`P_rad → 0`).** Якщо антена випромінює потужність, близьку до машинного нуля (наприклад, при збої зчитування з вимірювального приладу), ділення на `P_rad` викличе помилку ділення на нуль або поверне нескінченність (`NaN` / `Inf`). У коді реалізовано захисну перевірку `if (p_sum > 1e-12)`, яка у випадку нульового сигналу встановлює дефолтні безпечні значення (`D_max = 1.0`, `D_dBi = 0.0 дБі`).
- **Тестування на еталонному диполі `sin³(θ)`.** Для верифікації правильності чисельного інтегрування у функцію `main()` закладено тестування на аналітичній моделі напівхвильового диполя з інтенсивністю `U(θ) = sin³(θ)`. Математична теорія дає точне значення спрямованості `D_max = 1.643` (`2.15 дБі`). Якщо чисельний інтегратор повертає `1.643` з точністю до третього знака після коми, це доводить відсутність похибок вагових коефіцієнтів та правильності множника `sin(θ)`.
- **Обробка витоків пам'яті.** У C-версії створення об'єкта `pattern_create()` виконує динамічне виділення пам'яті через `malloc` та `calloc`. У випадку невдалого виділення пам'яті під масив даних функція акуратно звільняє виділену під структуру пам'ять і повертає `NULL`, запобігаючи витокам пам'яті та крахам програми.

---

### Оцінка складності та розпаралелювання обчислень

Обчислювальна складність алгоритму чисельного інтегрування становить `O(N_theta × N_phi)`. Для стандартної вимірювальної сітки з кроком 1 градус (`181 × 361 = 65 341` точка) обчислення виконуються миттєво (менше 1 мілісекунди на сучасних процесорах).

Проте для сіток високої роздільності, що використовуються при моделюванні великих дзеркальних антен або фазованих решіток з кількома тисячами елементів (крок `0.1°`, `1801 × 3601 = 6.48 × 10⁶` точок), час обчислення зростає. 

Оскільки ітерації зовнішнього циклу по куту `θ_i` є повністю незалежними одна від одної (не мають залежностей за даними), алгоритм є ідеально паралельним (*embarrassingly parallel*). У виробничих реалізаціях зовнішній цикл по `i` паралелять директивою OpenMP:

```cpp
#pragma omp parallel for reduction(+:p_sum) reduction(max:max_u)
```

Це дозволяє прискорити розрахунок повної випромінюваної потужності `P_rad` у 8–16 разів на багатоядерних процесорах або обчислювальних кластерах.

---

### Залежність точності інтегрування від роздільної здатності сітки

При виборі кутового кроку дискретизації `Δθ` та `Δϕ` у вимірювальних комплексах існує компроміс між часом вимірювання та точністю обчислення підсилення:

- **Крок 1° (сітка 181 × 361 точок).** Забезпечує найвищу точність (похибка обчислення `P_rad` менше 0.05 дБ) навіть для вузьких променів шириною 5–10 градусів.
- **Крок 5° (сітка 37 × 73 точки).** Дає високу точність (похибка до 0.2 дБ) для всебічних та помірно спрямованих антен (диполі, патчі), але для гострих тарілок починає згладжувати бокові пелюстки.
- **Крок 10° і більше.** Припускає значну похибку чисельного інтегрування (понад 1 дБ) через неврахування швидких коливань поля у діагональних напрямках.

Для забезпечення високої точності крок сітки обирають за правилом: `Δθ ≤ HPBW / 5`.

---

### Особливості реалізації мовами C та C++



При проектуванні розрахункового ядра використано ідіоматичні підходи обох мов:

- **У версії на C:** застосовано динамічне виділення пам'яті через `malloc`/`calloc`, строго визначену структуру `pattern_3d_t` для збереження одновимірного розгорнутого масиву `U[i * num_phi + j]`, явне звільнення ресурсів функцією `pattern_free()` та перевірки на нульові вказівники та ділення на нуль.
- **У версії на C++:** використано концепцію RAII (*Resource Acquisition Is Initialization*), стандартні контейнери `std::vector<std::vector<double>>`, математичні константи із сучасного стандарту C++20 (`std::numbers::pi`), метод `std::max` для пошуку піку та безпечне управління пам'яттю без сирих вказівників.

---

### Код програми

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

/* Структура для збереження дискретної 3D-діаграми спрямованості */
typedef struct {
    int num_theta;       /* Кількість точок по куту theta (0..180 deg) */
    int num_phi;         /* Кількість точок по куту phi (0..360 deg) */
    double delta_theta;  /* Крок по theta в радіанах */
    double delta_phi;    /* Крок по phi в радіанах */
    double *pattern_u;   /* Одномерний розгорнутий масив U(theta, phi) */
} pattern_3d_t;

/* Структура підсумкових результатів 3D-інтегрування */
typedef struct {
    double p_rad;           /* Повна випромінювана потужність (Вт) */
    double u_max;           /* Максимальна інтенсивність (Вт/ср) */
    double directivity;     /* Коефіцієнт спрямованості (лінійний) */
    double directivity_dbi; /* Підсилення у дБі (dBi) */
    double beam_solid_angle;/* Тілесний кут променя (стерадіани) */
} pattern_results_t;

/* Створення та ініціалізація пам'яті під 3D-діаграму */
pattern_3d_t* pattern_create(int num_theta, int num_phi) {
    if (num_theta < 2 || num_phi < 2) return NULL;
    
    pattern_3d_t *p = (pattern_3d_t*)malloc(sizeof(pattern_3d_t));
    if (!p) return NULL;
    
    p->num_theta = num_theta;
    p->num_phi = num_phi;
    p->delta_theta = M_PI / (num_theta - 1);
    p->delta_phi = (2.0 * M_PI) / (num_phi - 1);
    p->pattern_u = (double*)calloc((size_t)num_theta * (size_t)num_phi, sizeof(double));
    
    if (!p->pattern_u) {
        free(p);
        return NULL;
    }
    return p;
}

/* Звільнення пам'яті */
void pattern_free(pattern_3d_t *p) {
    if (p) {
        if (p->pattern_u) free(p->pattern_u);
        free(p);
    }
}

/* Запис значення U(i, j) у масив */
void pattern_set(pattern_3d_t *p, int i, int j, double val) {
    if (p && p->pattern_u && i >= 0 && i < p->num_theta && j >= 0 && j < p->num_phi) {
        p->pattern_u[i * p->num_phi + j] = val;
    }
}

/* Зчитування значення U(i, j) */
double pattern_get(const pattern_3d_t *p, int i, int j) {
    if (!p || !p->pattern_u) return 0.0;
    return p->pattern_u[i * p->num_phi + j];
}

/* Чисельне сферичне інтегрування методом трапецій з вагою sin(theta) */
int pattern_integrate(const pattern_3d_t *p, pattern_results_t *res) {
    if (!p || !p->pattern_u || !res) return -1;
    
    double p_sum = 0.0;
    double max_u = 0.0;
    
    for (int i = 0; i < p->num_theta; ++i) {
        double theta = i * p->delta_theta;
        double sin_th = sin(theta);
        
        /* Вага за методом трапецій по куту theta */
        double w_theta = (i == 0 || i == p->num_theta - 1) ? 0.5 : 1.0;
        
        for (int j = 0; j < p->num_phi; ++j) {
            double u_val = pattern_get(p, i, j);
            if (u_val > max_u) {
                max_u = u_val;
            }
            
            /* Вага по куту phi */
            double w_phi = (j == 0 || j == p->num_phi - 1) ? 0.5 : 1.0;
            
            /* Елемент інтегрування: U(th, ph) * sin(th) * d_th * d_ph */
            double cell_power = u_val * sin_th * (w_theta * p->delta_theta) * (w_phi * p->delta_phi);
            p_sum += cell_power;
        }
    }
    
    res->p_rad = p_sum;
    res->u_max = max_u;
    if (p_sum > 1e-12 && max_u > 0.0) {
        res->directivity = (4.0 * M_PI * max_u) / p_sum;
        res->directivity_dbi = 10.0 * log10(res->directivity);
        res->beam_solid_angle = (4.0 * M_PI) / res->directivity;
    } else {
        res->directivity = 1.0;
        res->directivity_dbi = 0.0;
        res->beam_solid_angle = 4.0 * M_PI;
    }
    return 0;
}

int main(void) {
    int n_th = 181; /* Роздільна здатність 1 градус */
    int n_ph = 361;
    
    pattern_3d_t *pat = pattern_create(n_th, n_ph);
    if (!pat) {
        fprintf(stderr, "Помилка виділення пам'яті!\n");
        return 1;
    }
    
    /* Заповнення масиву тестовою 3D-діаграмою напівхвильового диполя: U(th) = sin^3(th) */
    for (int i = 0; i < n_th; ++i) {
        double theta = i * pat->delta_theta;
        double sin_th = sin(theta);
        double u_val = sin_th * sin_th * sin_th; /* sin^3(theta) */
        for (int j = 0; j < n_ph; ++j) {
            pattern_set(pat, i, j, u_val);
        }
    }
    
    pattern_results_t res;
    if (pattern_integrate(pat, &res) == 0) {
        printf("--- Результати 3D-інтегрування диполя (C) ---\n");
        printf("Повна потужність P_rad: %.4f Вт\n", res.p_rad);
        printf("Макс. інтенсивність U_max: %.4f Вт/ср\n", res.u_max);
        printf("КСД (Directivity):        %.3f (теорія: 1.643)\n", res.directivity);
        printf("Підсилення (dBi):         %.2f дБі (теорія: 2.15 дБі)\n", res.directivity_dbi);
        printf("Тілесний кут Omega_A:     %.3f ср\n", res.beam_solid_angle);
    }
    
    pattern_free(pat);
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <cmath>
#include <numbers>
#include <iomanip>

struct PatternResults {
    double p_rad{0.0};
    double u_max{0.0};
    double directivity{1.0};
    double directivity_dbi{0.0};
    double beam_solid_angle{4.0 * std::numbers::pi};
};

class RadiationPattern3D {
public:
    RadiationPattern3D(std::size_t num_theta, std::size_t num_phi)
        : num_theta_(num_theta), num_phi_(num_phi),
          delta_theta_(std::numbers::pi / static_cast<double>(num_theta - 1)),
          delta_phi_((2.0 * std::numbers::pi) / static_cast<double>(num_phi - 1)),
          grid_(num_theta, std::vector<double>(num_phi, 0.0)) {}

    void set_intensity(std::size_t i, std::size_t j, double value) {
        grid_.at(i).at(j) = value;
    }

    [[nodiscard]] double get_intensity(std::size_t i, std::size_t j) const {
        return grid_.at(i).at(j);
    }

    [[nodiscard]] PatternResults compute_directivity() const {
        PatternResults res;
        double p_sum = 0.0;
        double max_u = 0.0;

        for (std::size_t i = 0; i < num_theta_; ++i) {
            const double theta = static_cast<double>(i) * delta_theta_;
            const double sin_th = std::sin(theta);
            const double w_theta = (i == 0 || i == num_theta_ - 1) ? 0.5 : 1.0;

            for (std::size_t j = 0; j < num_phi_; ++j) {
                const double u_val = grid_[i][j];
                max_u = std::max(max_u, u_val);

                const double w_phi = (j == 0 || j == num_phi_ - 1) ? 0.5 : 1.0;
                const double d_omega = sin_th * (w_theta * delta_theta_) * (w_phi * delta_phi_);
                p_sum += u_val * d_omega;
            }
        }

        res.p_rad = p_sum;
        res.u_max = max_u;
        if (p_sum > 1e-12 && max_u > 0.0) {
            res.directivity = (4.0 * std::numbers::pi * max_u) / p_sum;
            res.directivity_dbi = 10.0 * std::log10(res.directivity);
            res.beam_solid_angle = (4.0 * std::numbers::pi) / res.directivity;
        }
        return res;
    }

private:
    std::size_t num_theta_;
    std::size_t num_phi_;
    double delta_theta_;
    double delta_phi_;
    std::vector<std::vector<double>> grid_;
};

int main() {
    constexpr std::size_t n_th = 181;
    constexpr std::size_t n_ph = 361;

    RadiationPattern3D pattern(n_th, n_ph);

    // Симуляція 3D-діаграми напівхвильового диполя
    for (std::size_t i = 0; i < n_th; ++i) {
        const double theta = static_cast<double>(i) * (std::numbers::pi / static_cast<double>(n_th - 1));
        const double sin_th = std::sin(theta);
        const double u_val = sin_th * sin_th * sin_th;
        for (std::size_t j = 0; j < n_ph; ++j) {
            pattern.set_intensity(i, j, u_val);
        }
    }

    const auto res = pattern.compute_directivity();

    std::cout << std::fixed << std::setprecision(3);
    std::cout << "--- Результати 3D-інтегрування диполя (C++) ---\n";
    std::cout << "Повна потужність P_rad: " << res.p_rad << " Вт\n";
    std::cout << "Макс. інтенсивність U_max: " << res.u_max << " Вт/ср\n";
    std::cout << "КСД (Directivity):        " << res.directivity << " (теорія: 1.643)\n";
    std::cout << "Підсилення (dBi):         " << res.directivity_dbi << " дБі (теорія: 2.15 дБі)\n";
    std::cout << "Тілесний кут Omega_A:     " << res.beam_solid_angle << " ср\n";

    return 0;
}
```
:::
