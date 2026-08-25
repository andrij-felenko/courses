# ⚙️ Симуляція когерентності та розрахунок видності інтерференційних смуг

Чисельне моделювання часової та просторової когерентності є важливим інструментом сучасної обчислювальної оптики. Воно дає змогу проектувати інтерферометричні системи, розраховувати роздільну здатність оптичних томографів і передбачати видність інтерференційної картини без побудови дорогих експериментальних установок.

У цьому матеріалі детально розглядаються алгоритми чисельного моделювання частково когерентного світла, наводяться робочі програми мовами Python, C та C++, а також аналізуються найтиповіші чисельні пастки й граничні умови розрахунків.

### Фізико-математичні алгоритми моделювання

Моделювання хвильових полів із скінченною когерентністю в обчислювальній оптиці виконується за двома основними методологічними підходами:

#### 1. Часовий підхід (Time-domain Monte-Carlo simulation)

Хвильовий процес моделюється безпосередньо у часовій області як послідовність багатьох випадкових хвильових цугів. Для кожного цуга тривалістю `τ_c` випадковим чином обирається початкова фаза `φ₀ ∈ [0, 2π)`. 

Далі обчислюється миттєве значення поля для двох плечей інтерферометра зі запізненням `τ = Δx / c`:

```
V₁(t) = A₀ · exp(i · (ω₀·t + φ₁(t)))
V₂(t) = A₀ · exp(i · (ω₀·(t − τ) + φ₂(t − τ)))
```

Для врахування реального детектора виконується чисельне інтегрування квадратного модуля суми полів `|V₁(t) + V₂(t)|²` на довгому часовому інтервалі `T_det >> τ_c`. Цей метод є фізично найбільш наочним, оскільки буквально відтворює роботу оптичного фотодетектора.

#### 2. Спектральний підхід через фур'є-перетворення (Frequency-domain approach)

За теоремою Вінера — Хінчина, взаємна когерентність `Γ₁₁(τ)` обчислюється як пряме фур'є-перетворення від спектральної густини потужності джерела `S(ν)`. 

Цей підхід є обчислювально набагато ефективнішим за монте-карловську часову симуляцію, оскільки спирається на алгоритм Швидкого Перетворення Фур'є (FFT) зі складністю `O(N · log N)` замість прямого часового інтегрування.

#### 3. Просторова когерентність (Двовимірне інтегрування за поверхнею)

За теоремою Ван Ціттерта — Церніке, ступінь просторової когерентності `γ₁₂(0)` обчислюється шляхом двовимірного чисельного інтегрування по поверхні некогерентного джерела. Для кожної пари точок на екрані спостереження додаються внески від усіх випромінювальних елементів поверхні джерела з урахуванням фазових затримок, пропорційних геометричній відстані.

### Детальний розбір реалізації на Python

Нижче наведено повнофункціональний модуль на Python, який обчислює функцію часової когерентності `γ(τ)`, будує інтерферограму Майкельсона для довільного спектрального профілю (гаусового чи лоренцового) та вираховує видність смуг.

```python
import numpy as np

def generate_spectrum(wavelength_center_nm, fwhm_nm, num_points=2048, profile='gaussian'):
    """
    Генерує масив спектральної густини потужності S(nu) для заданої довжини хвилі та ширини лінії.
    """
    c = 299792458.0  # швидкість світла в м/с
    lambda0 = wavelength_center_nm * 1e-9
    delta_lambda = fwhm_nm * 1e-9
    
    nu0 = c / lambda0
    delta_nu = (c / (lambda0 ** 2)) * delta_lambda
    
    # Частотний інтервал навколо центральної частоти nu0
    nu_vector = np.linspace(nu0 - 5 * delta_nu, nu0 + 5 * delta_nu, num_points)
    
    if profile == 'gaussian':
        sigma_nu = delta_nu / (2 * np.sqrt(2 * np.log(2)))
        spectrum = np.exp(-0.5 * ((nu_vector - nu0) / sigma_nu) ** 2)
    elif profile == 'lorentzian':
        spectrum = 1.0 / (1.0 + 4.0 * ((nu_vector - nu0) / delta_nu) ** 2)
    else:
        raise ValueError("Невідомий тип профілю. Обирайте 'gaussian' або 'lorentzian'")
        
    # Нормування спектра
    spectrum /= np.trapz(spectrum, nu_vector)
    return nu_vector, spectrum

def compute_interferogram(nu_vector, spectrum, max_delay_fs=500, steps=1000):
    """
    Обчислює інтерферограму Майкельсона та комплексний ступень когерентності gamma(tau).
    """
    c = 299792458.0
    tau_vector = np.linspace(-max_delay_fs * 1e-15, max_delay_fs * 1e-15, steps)
    dnu = nu_vector[1] - nu_vector[0]
    
    gamma_complex = np.zeros(len(tau_vector), dtype=complex)
    
    # Дискретне інтегрування: gamma(tau) = int S(nu) * exp(i * 2*pi * nu * tau) dnu
    for i, tau in enumerate(tau_vector):
        integrand = spectrum * np.exp(1j * 2 * np.pi * nu_vector * tau)
        gamma_complex[i] = np.trapz(integrand, nu_vector)
        
    # Нормування на нульове значення
    gamma_complex /= np.abs(gamma_complex[len(tau_vector)//2])
    
    visibility = np.abs(gamma_complex)
    path_difference_um = tau_vector * c * 1e6
    intensity_signal = 1.0 + np.real(gamma_complex)
    
    return path_difference_um, visibility, intensity_signal

# Демонстрація розрахунку для світлодіода LED (630 нм, FWHM = 30 нм)
nu, spec = generate_spectrum(wavelength_center_nm=630, fwhm_nm=30, profile='gaussian')
path_um, vis, I_sig = compute_interferogram(nu, spec, max_delay_fs=200, steps=500)

lc_theory_um = (630e-9)**2 / (30e-9) * 1e6
print(f"Теоретична довжина когерентності L_c: {lc_theory_um:.2f} мкм")
print(f"Максимальна видність при zero delay: V_max = {np.max(vis):.4f}")
```

Скрипт демонструє, як спектральне розширення безпосередньо визначає форму огинаючої інтерференційних смуг. Зі зростанням різниці ходу `Δx` видність монотонно падає за профілем, що є двовимірним фур'є-образом від спектра.

### Обчислення просторової когерентності на C та C++

Для обчислення просторової когерентності протяжного джерела методом чисельного інтегрування 2D-поверхні потрібна висока продуктивність виконання. Нижче наведено ідіоматичні реалізації цього алгоритму мовами C та C++.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

// Структура конфігурації протяжного некогерентного джерела
typedef struct {
    double width_mm;
    double height_mm;
    double distance_R_mm;
    double wavelength_mm;
} SourceConfig;

// Обчислення ступеня просторової когерентності методом двовимірної сітки
double compute_spatial_coherence_2d(const SourceConfig* cfg, double dx_mm, double dy_mm, int grid_nodes) {
    double re_sum = 0.0;
    double im_sum = 0.0;
    double total_intensity = 0.0;
    
    double step_x = cfg->width_mm / grid_nodes;
    double step_y = cfg->height_mm / grid_nodes;
    double k = 2.0 * M_PI / cfg->wavelength_mm;
    
    for (int i = 0; i < grid_nodes; ++i) {
        double xi = -cfg->width_mm / 2.0 + (i + 0.5) * step_x;
        for (int j = 0; j < grid_nodes; ++j) {
            double eta = -cfg->height_mm / 2.0 + (j + 0.5) * step_y;
            
            // Рівномірний розподіл інтенсивності джерела
            double intensity = 1.0;
            double phase = k * (dx_mm * xi + dy_mm * eta) / cfg->distance_R_mm;
            
            re_sum += intensity * cos(phase) * step_x * step_y;
            im_sum += intensity * sin(phase) * step_x * step_y;
            total_intensity += intensity * step_x * step_y;
        }
    }
    
    double modulus = sqrt(re_sum * re_sum + im_sum * im_sum);
    return modulus / total_intensity;
}

int main(void) {
    SourceConfig cfg = {
        .width_mm = 2.0,
        .height_mm = 2.0,
        .distance_R_mm = 1000.0,  // 1000 мм (1 метр)
        .wavelength_mm = 0.0005    // 500 нм
    };
    
    printf("--- Просторова когерентність (Обчислення мовою C) ---\n");
    printf("Відстань d (мм) | |gamma_12| | Видність смуг V\n");
    printf("--------------------------------------------\n");
    
    for (double d = 0.0; d <= 0.4; d += 0.05) {
        double g = compute_spatial_coherence_2d(&cfg, d, 0.0, 100);
        printf("   %6.2f       | %6.4f   | %6.4f\n", d, g, g);
    }
    
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <cmath>
#include <numbers>
#include <iomanip>
#include <complex>

struct SourceParameters {
    double width_mm{2.0};
    double height_mm{2.0};
    double distance_R_mm{1000.0};
    double wavelength_nm{500.0};
};

struct CoherenceDataPoint {
    double slit_separation_mm;
    double degree_of_coherence;
    double fringe_visibility;
};

// Сучасний клас C++20 для розрахунку просторової когерентності за теоремою Ван Ціттерта — Церніке
class SpatialCoherenceSimulator {
private:
    SourceParameters params_;
    double wavelength_mm_;

public:
    explicit SpatialCoherenceSimulator(const SourceParameters& params)
        : params_(params), wavelength_mm_(params.wavelength_nm * 1e-6) {}

    // Обчислення просторової когерентності методом 2D чисельного інтегрування
    [[nodiscard]] double evaluate_coherence(double dx_mm, double dy_mm, std::size_t integration_steps = 120) const {
        std::complex<double> integral_sum{0.0, 0.0};
        double total_power{0.0};

        const double step_x = params_.width_mm / static_cast<double>(integration_steps);
        const double step_y = params_.height_mm / static_cast<double>(integration_steps);
        const double k = 2.0 * std::numbers::pi / wavelength_mm_;

        for (std::size_t ix = 0; ix < integration_steps; ++ix) {
            const double xi = -params_.width_mm / 2.0 + (static_cast<double>(ix) + 0.5) * step_x;
            for (std::size_t iy = 0; iy < integration_steps; ++iy) {
                const double eta = -params_.height_mm / 2.0 + (static_cast<double>(iy) + 0.5) * step_y;

                const double phase = k * (dx_mm * xi + dy_mm * eta) / params_.distance_R_mm;
                const double cell_area = step_x * step_y;
                
                // Рівномірний розподіл інтенсивності джерела I(xi, eta) = 1.0
                constexpr double intensity = 1.0;
                integral_sum += intensity * std::exp(std::complex<double>{0.0, -phase}) * cell_area;
                total_power += intensity * cell_area;
            }
        }

        return std::abs(integral_sum) / total_power;
    }

    // Генерація повного профілю просторової когерентності
    [[nodiscard]] std::vector<CoherenceDataPoint> generate_profile(double max_d_mm, std::size_t points_count) const {
        std::vector<CoherenceDataPoint> profile;
        profile.reserve(points_count);

        const double step = max_d_mm / static_cast<double>(points_count - 1);
        for (std::size_t i = 0; i < points_count; ++i) {
            const double d = static_cast<double>(i) * step;
            const double gamma_val = evaluate_coherence(d, 0.0);
            profile.push_back({
                .slit_separation_mm = d,
                .degree_of_coherence = gamma_val,
                .fringe_visibility = gamma_val
            });
        }
        return profile;
    }
};

int main() {
    const SourceParameters config{.width_mm = 1.5, .height_mm = 1.5, .distance_R_mm = 1200.0, .wavelength_nm = 632.8};
    const SpatialCoherenceSimulator simulator(config);
    
    const auto coherence_results = simulator.generate_profile(0.6, 13);

    std::cout << "--- Просторова когерентність (Обчислення на C++20) ---\n";
    std::cout << std::fixed << std::setprecision(4);
    std::cout << "Відстань d (мм) | |gamma_12| | Видність V\n";
    std::cout << "--------------------------------------\n";

    for (const auto& entry : coherence_results) {
        std::cout << "   " << std::setw(6) << entry.slit_separation_mm 
                  << "       | " << entry.degree_of_coherence 
                  << " | " << entry.fringe_visibility << "\n";
    }

    return 0;
}
```
:::

### Подібність розрахунків та відмінності між C і C++

При порівнянні двох реалізацій важливо звернути увагу на архітектурні відмінності:

1. **Типобезпека та математичні константи:** У версії C++20 використовується стандартне константне значення `std::numbers::pi` з бібліотеки `<numbers>`, яке гарантує максимальну точність для типу `double`. У версії C використовується традиційний макрос `#ifndef M_PI`.
2. **Комплексні числа:** У C++ застосовується стандартний шаблонний клас `std::complex<double>`, який підтримує виразну алгебру та автоматичні функції на зразок `std::abs()` та `std::exp()`. У C реалізовано окремі масиви для дісної `re_sum` та уявної `im_sum` частин.
3. **Керування пам'яттю та RAII:** У версії C++ контейнер `std::vector<CoherenceDataPoint>` самостійно виділяє й звільняє пам'ять у купі (RAII — Resource Acquisition Is Initialization), у той час як C-програма використовує стек або прямий виклик `malloc()` / `free()`.
4. **Конструювання об'єктів:** У C++20 застосовано позначення агрегатної ініціалізації з названими полями (designated initializers) `.slit_separation_mm = d`, що робить код легшим для читання та запобігає помилкам перестановки аргументів.

### Особливості чисельної реалізації та оптимізація

При програмуванні чисельних алгоритмів оптичної когерентності необхідно враховувати кілька важливих інженерних моментів:

#### 1. Крок сітки та теорема Котельникова — Шеннона

При обчисленні спектрального інтеграла часової когерентності крок за частотою `dν` у дискретному масиві має задовольняти умову `dν << Δν`. 

Якщо обрати `dν` занадто великим, виникає ефект **чисельного аліасингу (aliasing)** у часовій області: розрахований ступінь когерентності `γ(τ)` починає періодично повторюватися через фальшивий період `τ_alias = 1 / dν`. Для запобігання цьому явищу число точок у масиві частот `num_points` зазвичай обирають не менше 2048–4096.

#### 2. Двовимірне інтегрування та векторні інструкції

Обчислення просторової когерентності некогерентного джерела за допомогою двох вкладених циклів має обчислювальну складність `O(N²)`, де `N` — кількість вузлів сітки по кожній осі. Для сітки 1000×1000 точок це вимагає 1,000,000 обчислень тригонометричних функцій `cos()` та `sin()` на кожний крок за відстанню `d`.

У C++ версії для прискорення розрахунків використовується компіляторна автовекторизація (AVX2/AVX-512) та заміна комплексних експонент на паралельне обчислення масивів.

#### 3. Крайові ефекти та нульове доповнення (Zero-Padding)

При використанні Швидкого Перетворення Фур'є (FFT) для отримання функції когерентності зі спектра `S(ν)` необхідно виконувати нульове доповнення вхідного масиву щонайменше у 4–8 разів (zero-padding factor = 4..8). Це забезпечує плавність обчисленої огинаючої та точне визначення видності смуг `V` без чисельного спотворення фази.

#### 4. Наближення Фраунгофера vs наближення Френеля

Спрощені формули Ван Ціттерта — Церніке на основі функції `sinc` чи функцій Бесселя `J₁(x)/x` справедливі лише за умови виконання критерію далекої зони (Фраунгофера):

```
R >> (d_src · d_obs) ÷ λ₀      [критерій далекої зони]
```

Якщо відстань до екрана `R` не задовольняє цю нерівність (наприклад, у мікроскопії ближнього поля або у коротких оптичних плечах), у чисельний інтеграл необхідно включати квадратичний фазовий множник Френеля `exp(i · k · (ξ² + η²) / (2R))`.
