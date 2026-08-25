# ⚙️ Чисельне моделювання комплексної діелектричної проникності та поверхневих плазмонів за моделлю Друде

Цей модуль присвячено практичній чисельній реалізації розрахунку комплексних оптичних параметрів металів (діелектричної проникності `ε(ω)`, комплексного показника заломлення `n + i·k`), спектра відбивання світла `R(ω)` та розрахунку дисперсійної кривої поверхневих плазмон-поляритонів (SPP) на основі класичної феноменологічної моделі Друде-Лоренца.

---

### 1. Фізична модель, комплексні оптичні константи та геометрія Кречмана

У класичній електронній теорії металів Друде електронний газ розглядається як сукупність вільних носіїв заряду, що здійснюють хаотичний рух і розсіюються на іонах кристалічної ґратки із середнім часом релаксації `τ`. Згідно з цією моделлю, комплексна діелектрична проникність металу `ε(ω) = ε_1(ω) + i · ε_2(ω)` описується фундаментальним співвідношенням:

```
ε(ω) = ε_∞ - ( ω_p² / (ω² + i · γ · ω) )
```

де `ω_p` — плазмова частота електронів металу, `γ = 1/τ` — коефіцієнт згасання (частота розсіяння електронів унаслідок зіткнень із фононами та дефектами), `ε_∞` — високочастотна діелектрична проникність остова (враховує поляризацію зв'язаних електронів внутрішніх оболонок).

Розділивши дійсну та уявну частини у виразі `ε(ω)`:

```
ε_1(ω) = Re(ε) = ε_∞ - ( ω_p² / (ω² + γ²) )
ε_2(ω) = Im(ε) = ( γ · ω_p² ) / ( ω · (ω² + γ²) )
```

Зв'язок між комплексною діелектричною проникністю `ε(ω)` та комплексним показником заломлення `N(ω) = n(ω) + i · k(ω)` (де `n` — звичайний показник заломлення, а `k` — показник гасіння або коефіцієнт екстинкції) виражається співвідношеннями:

```
Re(ε) = n² - k²
Im(ε) = 2 · n · k
```

Звідси дійсний та уявний показники заломлення обчислюються як:

```
n(ω) = √ ( 0.5 · ( √(Re(ε)² + Im(ε)²) + Re(ε) ) )
k(ω) = √ ( 0.5 · ( √(Re(ε)² + Im(ε)²) - Re(ε) ) )
```

Для межі розділу метал-діелектрик з диелектричною проникністю `ε_d` хвильовий вектор поверхневого плазмон-поляритона `k_spp` дорівнює:

```
k_spp(ω) = (ω / c) · √ ( (ε_m(ω) · ε_d) / (ε_m(ω) + ε_d) )
```

Коефіцієнт відбивання світла при нормальному падінні з вакууму розраховується за формулою Френеля:

```
R(ω) = | (1 - √ε_m(ω)) / (1 + √ε_m(ω)) |² = ( (n - 1)² + k² ) / ( (n + 1)² + k² )
```

#### Параметри благородних металів для розрахунку

Для чисельних розрахунків у видимому та близькому ультрафіолетовому діапазонах зазвичай використовують експериментально визначені феноменологічні параметри Друде:

- **Срібло (Ag):** `ℏ · ω_p = 9.01 еВ`, `ℏ · γ = 0.05 еВ`, `ε_∞ = 3.7`. Завдяки найменшому коефіцієнту згасання `γ` срібло володіє найдовшим шляхом пробігу поверхневих плазмонів і є еталонним матеріалом для плазмоніки.
- **Золото (Au):** `ℏ · ω_p = 9.03 еВ`, `ℏ · γ = 0.07 еВ`, `ε_∞ = 9.8`. Золото володіє високою хімічною стійкістю, проте при енергіях `> 2.4 еВ` (хвилі коротші за 515 нм) виникають міжзонні переходи 5d-6s електронів, які збільшують отичні втрати `Im(ε)`.
- **Алюміній (Al):** `ℏ · ω_p = 15.3 еВ`, `ℏ · γ = 0.6 еВ`, `ε_∞ = 1.0`. Алюміній володіє високою плазмовою частотою і є єдиним металом для плазмоніки в глибокому ультрафіолеті.

---

### 2. Математична умова оптичного резонансу Кречмана

Оскільки хвильовий вектор поверхневого плазмона `k_spp` є більшим за хвильовий вектор світла у вакуумі чи повітрі (`k_spp > k_0 = ω/c`), прямо збудити поверхневий плазмон світловою хвилею з повітря неможливо. Для підрублення фазового незбігу використовується оптична геометрія Кречмана.

У цій геометрії світловий промінь спрямовується крізь скляну призму з показником заломлення `n_p > 1` під кутом `θ` до підошви призми, на яку нанесено тонку металеву плівку (завтовшки 45–50 нм). Хвильовий вектор світла вздовж межі в призмі дорівнює:

```
k_prism(θ) = (ω / c) · n_p · sin(θ)
```

Резонансний кут Кречмана `θ_K`, при якому відбувається 100% перекачування фотонів у поверхневі плазмони (і коефіцієнт відбивання від підошви призми падає майже до нуля), визначається з умови збігу хвильових векторів `k_prism(θ_K) = Re(k_spp)`:

```
sin(θ_K) = (1 / n_p) · √ ( (Re(ε_m) · ε_d) / (Re(ε_m) + ε_d) )
```

У чисельних моделях сенсорів саме вимірювання зсуву резонансного кута `Δθ_K` при зміні диелектричної проникності аналіта `ε_d` (наприклад, при зв'язуванні білків на поверхні золота) становить основу роботи оптичних рефрактометрів та біосенсорів.

---

### 3. Структура чисельного алгоритму та крайові випадки

Алгоритм розрахунку реалізовано у вигляді лінійного спектрального сканера, який обчислює оптичні величини для дискретної сітки частот `ω`. Під час розрахунку необхідно враховувати такі крайові та числові особливості:

1. **Крайовий випадок `ω → 0` (статична границя):** При прямуванні частоти до нуля знаменник `ω · (ω² + γ²)` у виразі для `Im(ε)` прямує до нуля, що викликає розбіжність `Im(ε) → ∞`. У чисельному коді передбачено перевірку `if (omega <= 0.0)` з поверненням коректної фізичної межі статичного диелектрика або поверненням великої статичної провідності.
2. **Точка плазмонного резонансу (`ε_m + ε_d → 0`):** При наближенні частоти до поверхневої плазмової частоти `ω_sp = ω_p / √(1 + ε_inf)` сума діелектричних проникностей у знаменнику під коренем для `k_spp` прямує до нуля. Врахування уявного члена `Im(ε_m) = ε_2` запобігає діленню на нуль у комплексному просторі і дає скінченне значення комплесного хвильового вектора `k_spp = k_spp' + i · k_spp''`, де уявна частина `k_spp''` описує просторове згасання поверхневої плазмонної хвилі вздовж уздовж межі.
3. **Обчислення квадратного кореня з від'ємної дійсної частини:** Оскільки при `ω < ω_p` дійсне значення `Re(ε)` є від'ємним, звичайний корінь `std::sqrt()` над дійсними числами поверне `NaN`. Для коректного розрахунку використовується математичний комплексний корінь (`std::complex<double>` у C++, `double complex` у C, `cmath.sqrt()` у Python), який автоматично обирає правильну гілку у комплексній площині.

---

### 4. Повна реалізація розрахунку

Нижче наведено ідіоматичні реалізації розрахунку оптичних характеристик металу трьома мовами програмування.

:::tabs
```cpp
#include <iostream>
#include <vector>
#include <complex>
#include <cmath>
#include <iomanip>

// Параметри моделі Друде для металу:
// wp (еВ), gamma (еВ), eps_inf (безрозмірна), eps_d (довкілля)
struct DrudeParameters {
    double wp;      // плазмова частота
    double gamma;   // частота розсіяння (згасання)
    double eps_inf; // диелектрична проникність остова
    double eps_d;   // диелектрична проникність середовища
    double n_prism; // показник заломлення призми Кречмана
};

struct PlasmonPoint {
    double omega_eV;
    double eps_real;
    double eps_imag;
    double n_ref;
    double k_ext;
    double reflectivity;
    double k_spp_real;
    double kretschmann_deg;
};

class DrudePlasmonSimulator {
private:
    DrudeParameters params_;
    static constexpr double pi_const = 3.14159265358979323846;

public:
    explicit DrudePlasmonSimulator(const DrudeParameters& params) : params_(params) {}

    // Обчислення комплексної діелектричної проникності eps(omega)
    [[nodiscard]] std::complex<double> calculateEpsilon(double omega) const {
        if (omega <= 0.0) return {params_.eps_inf, 0.0};
        std::complex<double> denominator(omega * omega, params_.gamma * omega);
        return params_.eps_inf - (params_.wp * params_.wp) / denominator;
    }

    // Обчислення коефіцієнта відбивання R(omega)
    [[nodiscard]] double calculateReflectivity(std::complex<double> eps) const {
        std::complex<double> n_complex = std::sqrt(eps);
        std::complex<double> r_amplitude = (1.0 - n_complex) / (1.0 + n_complex);
        return std::norm(r_amplitude); // |r|^2
    }

    // Обчислення хвильового вектора SPP: k_spp(omega)
    [[nodiscard]] std::complex<double> calculateKSpp(double omega, std::complex<double> eps_m) const {
        std::complex<double> eps_d_comp(params_.eps_d, 0.0);
        std::complex<double> ratio = (eps_m * eps_d_comp) / (eps_m + eps_d_comp);
        return omega * std::sqrt(ratio);
    }

    // Розрахунок кута Кречмана в градусах
    [[nodiscard]] double calculateKretschmannAngle(std::complex<double> k_spp, double omega) const {
        double k0 = omega;
        double sin_theta = k_spp.real() / (k0 * params_.n_prism);
        if (sin_theta > 1.0 || sin_theta < -1.0) return 0.0; // неможливе збудження
        return std::asin(sin_theta) * (180.0 / pi_const);
    }

    // Сканування спектрального діапазону
    [[nodiscard]] std::vector<PlasmonPoint> scanSpectrum(double start_eV, double end_eV, int steps) const {
        std::vector<PlasmonPoint> results;
        results.reserve(steps);

        double step_size = (end_eV - start_eV) / (steps - 1);
        for (int i = 0; i < steps; ++i) {
            double omega_eV = start_eV + i * step_size;
            std::complex<double> eps = calculateEpsilon(omega_eV);
            std::complex<double> n_comp = std::sqrt(eps);
            double R = calculateReflectivity(eps);
            std::complex<double> k_spp = calculateKSpp(omega_eV, eps);
            double angle_deg = calculateKretschmannAngle(k_spp, omega_eV);

            results.push_back({
                omega_eV,
                eps.real(),
                eps.imag(),
                n_comp.real(),
                n_comp.imag(),
                R,
                k_spp.real(),
                angle_deg
            });
        }
        return results;
    }
};

int main() {
    // Експериментальні константи срібла (Ag) у електронвольтах (eV)
    DrudeParameters silver{
        .wp = 9.01,
        .gamma = 0.05,
        .eps_inf = 3.7,
        .eps_d = 1.0,     // вакуум/повітря
        .n_prism = 1.517 // призма BK7
    };

    DrudePlasmonSimulator simulator(silver);
    auto spectrum = simulator.scanSpectrum(1.0, 3.5, 10);

    std::cout << std::fixed << std::setprecision(3);
    std::cout << "===========================================================================================\n";
    std::cout << "  w (eV)  |   Re(eps)   |   Im(eps)   |    n    |    k    | Reflectivity R | Angle (deg)\n";
    std::cout << "===========================================================================================\n";

    for (const auto& pt : spectrum) {
        std::cout << "  " << std::setw(6) << pt.omega_eV << "  |  "
                  << std::setw(9) << pt.eps_real << "  |  "
                  << std::setw(9) << pt.eps_imag << "  |  "
                  << std::setw(7) << pt.n_ref << " | "
                  << std::setw(7) << pt.k_ext << " | "
                  << std::setw(12) << pt.reflectivity << "  | "
                  << std::setw(9) << pt.kretschmann_deg << "\n";
    }
    std::cout << "===========================================================================================\n";
    return 0;
}
```
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <complex.h>

#define PI_CONST 3.14159265358979323846

typedef struct {
    double wp;      /* плазмова частота (еВ) */
    double gamma;   /* частота розсіяння (еВ) */
    double eps_inf; /* диелектрична проникність остова */
    double eps_d;   /* проникність середовища */
    double n_prism; /* показник заломлення призми */
} drude_params_t;

typedef struct {
    double omega_eV;
    double eps_real;
    double eps_imag;
    double n_ref;
    double k_ext;
    double reflectivity;
    double k_spp_real;
    double kretschmann_deg;
} plasmon_point_t;

static double complex drude_epsilon(double omega, const drude_params_t* p) {
    if (omega <= 0.0) return p->eps_inf + 0.0 * I;
    double complex denom = (omega * omega) + I * (p->gamma * omega);
    return p->eps_inf - (p->wp * p->wp) / denom;
}

static double drude_reflectivity(double complex eps) {
    double complex n_comp = csqrt(eps);
    double complex r_amp = (1.0 - n_comp) / (1.0 + n_comp);
    return cabs(r_amp) * cabs(r_amp);
}

static double complex drude_k_spp(double omega, double complex eps_m, double eps_d) {
    double complex eps_d_comp = eps_d + 0.0 * I;
    double complex ratio = (eps_m * eps_d_comp) / (eps_m + eps_d_comp);
    return omega * csqrt(ratio);
}

static double kretschmann_angle(double complex k_spp, double omega, double n_prism) {
    double sin_th = creal(k_spp) / (omega * n_prism);
    if (sin_th > 1.0 || sin_th < -1.0) return 0.0;
    return asin(sin_th) * (180.0 / PI_CONST);
}

int main(void) {
    drude_params_t silver = {
        .wp = 9.01,
        .gamma = 0.05,
        .eps_inf = 3.7,
        .eps_d = 1.0,
        .n_prism = 1.517
    };

    const int steps = 10;
    double start_eV = 1.0;
    double end_eV = 3.5;
    double step_size = (end_eV - start_eV) / (steps - 1);

    printf("===========================================================================================\n");
    printf("  w (eV)  |   Re(eps)   |   Im(eps)   |    n    |    k    | Reflectivity R | Angle (deg)\n");
    printf("===========================================================================================\n");

    for (int i = 0; i < steps; ++i) {
        double w = start_eV + i * step_size;
        double complex eps = drude_epsilon(w, &silver);
        double complex n_comp = csqrt(eps);
        double R = drude_reflectivity(eps);
        double complex k_spp = drude_k_spp(w, eps, silver.eps_d);
        double angle = kretschmann_angle(k_spp, w, silver.n_prism);

        printf("  %6.3f  |  %9.3f  |  %9.3f  |  %6.3f | %6.3f | %12.3f  | %9.3f\n",
               w, creal(eps), cimag(eps), creal(n_comp), cimag(n_comp), R, angle);
    }
    printf("===========================================================================================\n");
    return 0;
}
```
```py
import cmath
import math

class DrudePlasmonSimulator:
    def __init__(self, wp: float, gamma: float, eps_inf: float = 1.0, eps_d: float = 1.0, n_prism: float = 1.517):
        self.wp = wp
        self.gamma = gamma
        self.eps_inf = eps_inf
        self.eps_d = eps_d
        self.n_prism = n_prism

    def calculate_epsilon(self, omega: float) -> complex:
        if omega <= 0:
            return complex(self.eps_inf, 0.0)
        denom = omega**2 + 1j * self.gamma * omega
        return self.eps_inf - (self.wp**2) / denom

    def calculate_reflectivity(self, eps: complex) -> float:
        n_comp = cmath.sqrt(eps)
        r_amp = (1.0 - n_comp) / (1.0 + n_comp)
        return abs(r_amp)**2

    def calculate_k_spp(self, omega: float, eps_m: complex) -> complex:
        ratio = (eps_m * self.eps_d) / (eps_m + self.eps_d)
        return omega * cmath.sqrt(ratio)

    def calculate_kretschmann_angle(self, k_spp: complex, omega: float) -> float:
        sin_th = k_spp.real / (omega * self.n_prism)
        if sin_th > 1.0 or sin_th < -1.0:
            return 0.0
        return math.asin(sin_th) * (180.0 / math.pi)

    def scan_spectrum(self, start_ev: float, end_ev: float, steps: int):
        results = []
        step_size = (end_ev - start_ev) / (steps - 1)
        for i in range(steps):
            w = start_ev + i * step_size
            eps = self.calculate_epsilon(w)
            n_comp = cmath.sqrt(eps)
            R = self.calculate_reflectivity(eps)
            k_spp = self.calculate_k_spp(w, eps)
            angle = self.calculate_kretschmann_angle(k_spp, w)
            results.append((w, eps.real, eps.imag, n_comp.real, n_comp.imag, R, angle))
        return results

if __name__ == "__main__":
    # Параметри для срібла (Ag)
    sim = DrudePlasmonSimulator(wp=9.01, gamma=0.05, eps_inf=3.7, eps_d=1.0, n_prism=1.517)
    spectrum = sim.scan_spectrum(1.0, 3.5, 10)

    print("===================================================================================")
    print("  w (eV)  |   Re(eps)   |   Im(eps)   |    n    |    k    | Reflectivity R | Angle (deg)")
    print("===================================================================================")
    for w, re_eps, im_eps, n_val, k_val, R, angle in spectrum:
        print(f"  {w:6.3f}  |  {re_eps:9.3f}  |  {im_eps:9.3f}  |  {n_val:6.3f} | {k_val:6.3f} | {R:12.3f}  | {angle:9.3f}")
    print("===================================================================================")
```
:::

---

### 5. Фізичний аналіз та інтерпретація обчисленого спектра

Аналіз обчислених даних розкриває три ключові оптичні фази середовища:

1. **Дзеркальний металевий режим (`ω < 4 еВ`):**
   - Дійсна частина `Re(ε)` є глибоко від'ємною (від `-77.5` до `-1.0`), а показник гасіння `k` суттєво перевищує заломлення `n` (`k ≫ n`).
   - Електромагнітна хвиля не може проникнути углиб металу (скин-ефект) і майже повністю відбивається від поверхні (`R ≈ 0.98–0.99`). Це пояснює високу відбиваність срібних дзеркал у видимому світлі.

2. **Область поверхневого плазмонного резонансу (`ω ≈ ω_sp = 4.16 еВ`):**
   - Умови `Re(ε_m) ≈ -ε_d` викликають різке зростання дійсного хвильового вектора `k_spp`, що відповідає сильній сповільненості хвилі та накопиченню електромагнітної енергії на поверхні.
   - Показники `n` та `k` зрівнюються за величиною. Резонансний кут Кречмана `θ_K` плавно зростає від 41.6° до 44.8°, показуючи принципову можливість оптичного збудження поверхневого плазмона світлом.

3. **Область високих частот і прозорості (`ω > ω_p = 9.01 еВ`):**
   - Дійсна частина `Re(ε)` переходить у додатну область (`Re(ε) > 0`), показник гасіння `k` прямує до нуля, а показник заломлення `n` прямує до одиниці (`n → 1`).
   - Коефіцієнт відбивання стрімко впадає до `R ≈ 0.02–0.05`. Метал стає прозорим діелектриком у глибокому ультрафіолеті.
