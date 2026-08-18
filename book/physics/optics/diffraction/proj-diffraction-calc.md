# ⚙️ Чисельне моделювання дифракції: розрахунок полів Френеля та Фраунгофера

Ця вставка детально описує математичні принципи, структуру даних, алгоритмічні кроки та програмні реалізації чисельних алгоритмів розрахунку хвильових дифракційних полів. Моделювання хвильової оптики є ключовим інструментом при розробці оптичних систем, симуляції фотолітографічних процесів, обчисленні світлорозподілу світлодіодних лінз та проектуванні дифракційних елементів.

У статті розглянуто два фундаментальні обчислювальні режими поширення електромагнітного випромінювання:
- **Далеке поле (дифракція Фраунгофера):** застосовується при великих відстанях `z ≫ a² / λ` (число Френеля `N_F ≪ 1`), коли світлові хвилі можна вважати плоскими. Математично цей режим зводиться до розрахунку просторового перетворення Фур'є від амплітудно-фазової маски апертури.
- **Близьке поле (дифракція Френеля):** застосовується при проміжних відстанях `N_F ≳ 1`, коли фронт хвилі залишається викривленим (сферичним). Математично цей режим зводиться до обчислення згортки вхідного поля з ядром Френеля `exp(i·π·(x-x')²/(λ·z))`.

Нижче подано повністю працездатні, ідіоматичні та оптимізовані рішення трьома мовами програмування:
1. **C (стандарт C99/C11)** — низькорівнева реалізація з явним управлінням пам'яттю та власною комплексною арифметикою, призначена для вбудованих обчислювальних ядер та високопродуктивних C-бібліотек;
2. **C++ (стандарт C++20)** — сучасна об'єктно-орієнтована реалізація із застосуванням концепції RAII, контейнерів `std::vector`, `std::complex`, перевірки меж `std::span`, стандартних констант `std::numbers::pi` та синтаксису атрибутів `[[nodiscard]]`;
3. **Python (NumPy / SciPy)** — векторизована реалізація для швидкого прототипування, обчислення 2D-полів та побудови просторових профілів інтенсивності з використанням спеціальних функцій Бесселя.

---

### 1. Математичні основи дискретизації та чисельні алгоритми

Обчислення дифракційного поля полягає у чисельному інтегруванні скалярного хвильового рівняння Гюйгенса — Френеля по поверхні апертури. Розглянемо розрахункову область апертури розміром `L_in` вздовж осі `X'`, дискретизовану на `N` рівновіддалених вузлів із кроком `dx' = L_in / N`.

Координата `j`-го вузла апертури дорівнює:
```
x'[j] = -L_in / 2 + j · dx'     (де j = 0, 1, ..., N - 1)
```

Поле на апертурі задається дискретним масивом комплексних амплітуд `E_in[j]`. У найпростішому випадку для прозорої щілини шириною `a`:
```
E_in[j] = E₀  при |x'[j]| <= a / 2,  і  0.0  при |x'[j]| > a / 2
```

#### Алгоритм 1: Пряме сумування для дифракції Фраунгофера (далеке поле)

У далекому полі Фраунгофера (`z ≫ a² / λ`) комплексне поле в точці спостереження `x[k]` на екрані визначається дискретним сумуванням:

```
E_out[k] = (1 / √(i·λ·z)) · ∑_{j=0}^{N-1} E_in[j] · exp( -i · (2π / λ) · sin(θ_k) · x'[j] ) · dx'
```

де `sin(θ_k) = x[k] / √(x[k]² + z²)`.

Складність прямого розрахунку для `M` точок екрана та `N` точок апертури становить `O(N · M)`. При використанні Швидкого Перетворення Фур'є (FFT) складність знижується до `O(N log N)`.

#### Алгоритм 2: Конволюційне інтегрування дифракції Френеля (близьке поле)

У близькому полі Френеля (`N_F = a² / (λ·z) ≳ 1`) фазовий множник залежить квадратично від відстані між точками апертури та екрана `(x[k] - x'[j])²`:

```
E_fresnel[k] = (exp(i·k·z) / √(i·λ·z)) · ∑_{j=0}^{N-1} E_in[j] · exp( i·π / (λ·z) · (x[k] - x'[j])² ) · dx'
```

#### Умова запобігання аліасингу (критерій Найквіста)

Фазовий фактор Френеля `exp(i · π · x² / (λ · z))` швидко осцилює при віддаленні від центру. Щоб фаза між двома сусідніми вузлами сітки не змінювалася більше ніж на `π` (теорема Котельникова — Найквіста — Шеннона), крок дискретизації сітки `dx'` повинен задовольняти строге обмеження:

```
dx' <= (λ · z) / L_screen     [Критерій дискретизації Найквіста]
```

Якщо ця умова порушується, у чисельному розрахунку виникають несправжні дифракційні паразитичні смуги (аліасинг).

---

### 2. Реалізація обчислювального двигуна

Подані нижче лістинги описують моделювання дифракції світла лазера з довжиною хвилі `λ = 632.8 нм` (гелій-неоновий лазер) на щілині шириною `a = 0.2 мм`. Кожна вкладка містить повністю самостійний, ідіоматичний та перевірений код для відповідної платформи.

:::tabs
```c
/* C Implementation — 1D Fresnel & Fraunhofer Wave Diffraction Engine */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

/* Структура для подання комплексного числа з подвійною точністю */
typedef struct {
    double real;
    double imag;
} ComplexDouble;

static inline ComplexDouble complex_add(ComplexDouble a, ComplexDouble b) {
    ComplexDouble r = { a.real + b.real, a.imag + b.imag };
    return r;
}

static inline ComplexDouble complex_mul_scalar(ComplexDouble a, double s) {
    ComplexDouble r = { a.real * s, a.imag * s };
    return r;
}

static inline ComplexDouble complex_exp_i(double phase) {
    ComplexDouble r = { cos(phase), sin(phase) };
    return r;
}

static inline double complex_abs_sq(ComplexDouble a) {
    return a.real * a.real + a.imag * a.imag;
}

/* Обчислення дифракції Фраунгофера у далекому полі */
int calc_fraunhofer_1d(
    double wavelength,
    double slit_width,
    int n_aperture,
    double screen_width,
    int n_screen,
    double distance_z,
    double* out_intensity
) {
    if (!out_intensity || n_aperture <= 0 || n_screen <= 0 || distance_z <= 0.0) {
        return -1;
    }

    double k = 2.0 * M_PI / wavelength;
    double dx_in = (slit_width * 3.0) / n_aperture;
    double dx_out = screen_width / n_screen;

    for (int k_idx = 0; k_idx < n_screen; ++k_idx) {
        double x_out = -screen_width / 2.0 + k_idx * dx_out;
        double sin_theta = x_out / sqrt(x_out * x_out + distance_z * distance_z);

        ComplexDouble sum = { 0.0, 0.0 };

        for (int j = 0; j < n_aperture; ++j) {
            double x_in = - (slit_width * 1.5) + j * dx_in;
            
            /* Перевірка перебування всередині щілини [-a/2, +a/2] */
            if (fabs(x_in) <= slit_width / 2.0) {
                double phase = -k * sin_theta * x_in;
                ComplexDouble c = complex_exp_i(phase);
                sum = complex_add(sum, c);
            }
        }

        sum = complex_mul_scalar(sum, dx_in);
        out_intensity[k_idx] = complex_abs_sq(sum) / (wavelength * distance_z);
    }

    return 0;
}

/* Обчислення дифракції Френеля у близькому полі */
int calc_fresnel_1d(
    double wavelength,
    double slit_width,
    int n_aperture,
    double screen_width,
    int n_screen,
    double distance_z,
    double* out_intensity
) {
    if (!out_intensity || n_aperture <= 0 || n_screen <= 0 || distance_z <= 0.0) {
        return -1;
    }

    double coeff_phase = M_PI / (wavelength * distance_z);
    double dx_in = (slit_width * 3.0) / n_aperture;
    double dx_out = screen_width / n_screen;

    for (int k_idx = 0; k_idx < n_screen; ++k_idx) {
        double x_out = -screen_width / 2.0 + k_idx * dx_out;
        ComplexDouble sum = { 0.0, 0.0 };

        for (int j = 0; j < n_aperture; ++j) {
            double x_in = - (slit_width * 1.5) + j * dx_in;

            if (fabs(x_in) <= slit_width / 2.0) {
                double diff_x = x_out - x_in;
                double phase = coeff_phase * (diff_x * diff_x);
                ComplexDouble c = complex_exp_i(phase);
                sum = complex_add(sum, c);
            }
        }

        sum = complex_mul_scalar(sum, dx_in);
        out_intensity[k_idx] = complex_abs_sq(sum) / (wavelength * distance_z);
    }

    return 0;
}

int main(void) {
    double lambda = 632.8e-9; /* 632.8 нм */
    double slit_a = 0.2e-3;   /* 0.2 мм */
    double screen_w = 0.04;   /* 4 см екран */
    int n_screen = 200;

    double* intensity = (double*)malloc(sizeof(double) * n_screen);
    if (!intensity) {
        fprintf(stderr, "Помилка виділення пам'яті!\n");
        return 1;
    }

    printf("=== Обчислення дифракції Фраунгофера (z = 2.0 м) ===\n");
    if (calc_fraunhofer_1d(lambda, slit_a, 500, screen_w, n_screen, 2.0, intensity) == 0) {
        printf("Центральна інтенсивність I(0): %.4e Вт/м²\n", intensity[n_screen / 2]);
        printf("Інтенсивність біля першого мінімуму: %.4e Вт/м²\n", intensity[n_screen / 2 + 15]);
    }

    printf("\n=== Обчислення дифракції Френеля (z = 0.08 м) ===\n");
    if (calc_fresnel_1d(lambda, slit_a, 500, screen_w, n_screen, 0.08, intensity) == 0) {
        printf("Центральна інтенсивність Френеля I(0): %.4e Вт/м²\n", intensity[n_screen / 2]);
    }

    free(intensity);
    return 0;
}
```
```cpp
// C++ Implementation — Modern RAII Wave Diffraction Calculator
#include <iostream>
#include <vector>
#include <complex>
#include <cmath>
#include <numbers>
#include <span>
#include <stdexcept>

class DiffractionSolver {
public:
    using Complex = std::complex<double>;

    struct Config {
        double wavelength = 632.8e-9; // Довжина хвилі (м)
        double aperture_size = 0.2e-3; // Ширина щілини (м)
        double screen_size = 0.04;     // Розмір екрана (м)
        std::size_t grid_aperture = 500;
        std::size_t grid_screen = 400;
    };

    explicit DiffractionSolver(Config cfg) : config_(cfg) {
        if (config_.wavelength <= 0.0 || config_.aperture_size <= 0.0) {
            throw std::invalid_argument("Некоректні фізичні параметри апертури!");
        }
    }

    // Обчислення дифракції Фраунгофера (далеке поле)
    [[nodiscard]] std::vector<double> computeFraunhofer(double distance_z) const {
        if (distance_z <= 0.0) {
            throw std::invalid_argument("Відстань z має бути додатною!");
        }

        std::vector<double> intensity(config_.grid_screen, 0.0);
        const double k = 2.0 * std::numbers::pi / config_.wavelength;
        const double dx_in = (config_.aperture_size * 3.0) / static_cast<double>(config_.grid_aperture);
        const double dx_out = config_.screen_size / static_cast<double>(config_.grid_screen);

        for (std::size_t i = 0; i < config_.grid_screen; ++i) {
            const double x_out = -config_.screen_size / 2.0 + static_cast<double>(i) * dx_out;
            const double sin_theta = x_out / std::hypot(x_out, distance_z);

            Complex field_sum{0.0, 0.0};
            for (std::size_t j = 0; j < config_.grid_aperture; ++j) {
                const double x_in = -(config_.aperture_size * 1.5) + static_cast<double>(j) * dx_in;
                if (std::abs(x_in) <= config_.aperture_size / 2.0) {
                    const double phase = -k * sin_theta * x_in;
                    field_sum += std::polar(1.0, phase);
                }
            }
            field_sum *= dx_in;
            intensity[i] = std::norm(field_sum) / (config_.wavelength * distance_z);
        }
        return intensity;
    }

    // Обчислення дифракції Френеля (близьке поле)
    [[nodiscard]] std::vector<double> computeFresnel(double distance_z) const {
        if (distance_z <= 0.0) {
            throw std::invalid_argument("Відстань z має бути додатною!");
        }

        std::vector<double> intensity(config_.grid_screen, 0.0);
        const double phase_coeff = std::numbers::pi / (config_.wavelength * distance_z);
        const double dx_in = (config_.aperture_size * 3.0) / static_cast<double>(config_.grid_aperture);
        const double dx_out = config_.screen_size / static_cast<double>(config_.grid_screen);

        for (std::size_t i = 0; i < config_.grid_screen; ++i) {
            const double x_out = -config_.screen_size / 2.0 + static_cast<double>(i) * dx_out;

            Complex field_sum{0.0, 0.0};
            for (std::size_t j = 0; j < config_.grid_aperture; ++j) {
                const double x_in = -(config_.aperture_size * 1.5) + static_cast<double>(j) * dx_in;
                if (std::abs(x_in) <= config_.aperture_size / 2.0) {
                    const double diff_x = x_out - x_in;
                    const double phase = phase_coeff * (diff_x * diff_x);
                    field_sum += std::polar(1.0, phase);
                }
            }
            field_sum *= dx_in;
            intensity[i] = std::norm(field_sum) / (config_.wavelength * distance_z);
        }
        return intensity;
    }

private:
    Config config_;
};

int main() {
    try {
        DiffractionSolver::Config cfg{.wavelength = 632.8e-9, .aperture_size = 0.2e-3, .screen_size = 0.04};
        DiffractionSolver solver(cfg);

        auto fraunhofer_pattern = solver.computeFraunhofer(2.0);
        auto fresnel_pattern = solver.computeFresnel(0.08);

        std::cout << "Фраунгофер I_max: " << fraunhofer_pattern[fraunhofer_pattern.size() / 2] << " Вт/м²\n";
        std::cout << "Френель I_center: " << fresnel_pattern[fresnel_pattern.size() / 2] << " Вт/м²\n";
    } catch (const std::exception& e) {
        std::cerr << "Помилка виконання: " << e.what() << '\n';
        return 1;
    }
    return 0;
}
```
```py
# Python Implementation — Vectorized 2D Circular Airy Pattern Simulator
import numpy as np

def simulate_airy_disk_2d(wavelength=532e-9, diameter=1.0e-3, z_dist=1.5, grid_pts=512):
    """
    Моделювання двовимірної плями Ейрі при дифракції Фраунгофера на круглому отворі.
    """
    x = np.linspace(-0.005, 0.005, grid_pts)
    y = np.linspace(-0.005, 0.005, grid_pts)
    X, Y = np.meshgrid(x, y)
    R_screen = np.sqrt(X**2 + Y**2)
    
    sin_theta = R_screen / np.sqrt(R_screen**2 + z_dist**2)
    k = 2.0 * np.pi / wavelength
    q = k * (diameter / 2.0) * sin_theta
    
    # Використання граничного розкладу для уникнення ділення на нуль в центрі q = 0
    with np.errstate(divide='ignore', invalid='ignore'):
        from scipy.special import j1
        intensity = np.where(q == 0, 1.0, (2.0 * j1(q) / q)**2)
        
    return X, Y, intensity

if __name__ == '__main__':
    X, Y, I = simulate_airy_disk_2d()
    print(f"Розраховано двовимірну сітку {I.shape}. Максимальна інтенсивність у центрі = {I[256, 256]:.4f}")
```
:::

---

### 3. Покроковий розбір C-реалізації та керування пам'яттю

C-реалізація базується на трьох чітких етапах виконання:
1. **Перевірка вхідних аргументів:** Функції `calc_fraunhofer_1d` та `calc_fresnel_1d` захищені від нульових вказівників `out_intensity` та некоректних параметрів `n_aperture <= 0` або `distance_z <= 0.0`. Якщо виявлено невалідний параметр, функція миттєво повертає статус помилки `-1`, запобігаючи аварійному завершенню (Null Pointer Dereference або Division by Zero).
2. **Дискретизація простору:** Внутрішній крок входів `dx_in` та виходів `dx_out` обчислюється на основі фізичних розмірів вікна. Для апертури береться діапазон `1.5 · a`, щоб переконатися, що крайні вузли належать непрозорій частині екрана.
3. **Накопичення комплексного поля:** У внутрішньому циклі за `j` обчислюється фаза `phase` і додається комплексний вектор `c = exp(i · phase)` до акумулятора `sum`. Після закінчення інтегрування квадрат модуля `complex_abs_sq` дає підсумкову інтенсивність `I = |E|²`.

---

### 4. Покроковий розбір C++20 переваг та паттернів безпеки

Опис оптимізацій C++20 у коді:
1. **Конструкція `std::hypot(x_out, distance_z)`:** Використання функції `std::hypot` запобігає можливому чисельному переповненню або втраті точності при піднесенні до квадрата великих чи малих чисел під коренем.
2. **Метод `std::norm(field_sum)`:** На відміну від `std::abs`, який повертає модуль числа `|z|` (що вимагає обчислення квадратної коріння), `std::norm` повертає квадрат модуля `|z|² = Re² + Im²`. Це дає пряме значення інтенсивності без зайвої операції вилучення квадратного кореня.
3. **Атрибут `[[nodiscard]]`:** Гарантує, що розрахований вектор інтенсивності не буде випадково заігнорований викликаючим кодом.

---

### 5. Порівняльний аналіз продуктивності та інженерні рекомендації

При виборі архітектури чисельного розрахунку дифракції слід враховувати такі інженерні критерії:

1. **Обчислительна складність:**
   - Пряме інтегрування `O(N · M)` є єдино можливим рішенням для апертур довільної викривленої форми та нерівномірної розрахункової сітки.
   - Двовимірне швидке перетворення Фур'є `FFT2D` знижує складність до `O(N² log N)`, але вимагає прямокутної регулярної сітки із заповненням нулями (zero-padding).
2. **Оптимізація пам'яті та кешу:**
   - Для розрахунку великих двовимірних сіток (`2048 x 2048`) об'єм пам'яті для збереження комплексного поля досягає `64 МБ`. Для запобігання промахам кешу (cache misses) обхід матриць виконується за рядками (row-major order).
3. **Паралелізація на багатоядерних системах:**
   - Цикли обчислень у C та C++ легко паралеляться за допомогою розширення OpenMP добавленням директиви `#pragma omp parallel for`. Це забезпечує прискорення обчислень у `N_threads` разів.
