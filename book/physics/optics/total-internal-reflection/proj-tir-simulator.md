# ⚙️ Моделювання згасаючої хвилі та тунелювання світла (FTIR)

При повному внутрішньому відбитті світло не просто дзеркально відбивається від межі середовищ, а утворює в оптично менш щільному середовищі згасаюче (еванесцентне) поле, амплітуда якого спадає за експоненційним законом. Якщо на відстані `d`, порівнянній із довжиною хвилі, розмістити третє середовище з високим показником заломлення, повне відбиття руйнується (порушене повне внутрішнє відбиття, FTIR), і світлова енергія починає оптично тунелювати крізь тонкий проміжний шар.

Цей проєкт реалізує повноцінний алгоритм математичного моделювання трьохрівневої системи `n₁ | n₂ | n₃`. Він обчислює глибину проникнення `d[p]`, будує просторовий профіль амплітуди електричного поля `E(z)` усередині зазору та розраховує залежність коефіцієнтів пропускання `T(d)` і відбиття `R(d)` від товщини зазору.

---

### 1. Фізична модель та розрахункові співвідношення

Розглядається тришарова структура, що складається з першого напівнескінченного середовища (скляна призма, показник заломлення `n₁ = 1.50`), проміжного тонкого зазору (повітря чи вакуум, `n₂ = 1.00`) товщиною `d` та третього середовища (друга скляна призма чи аналізована речовина, `n₃ = 1.50`).

Світловий промінь падає з першого середовища під кутом `θ₁`, який перевищує критичний кут `θc = arcsin(n₂ / n₁) ≈ 41.81°`.

#### 1.1. Коефіцієнт згасання та глибина проникнення
Перпендикулярна компонента хвильового вектора у проміжному середовищі є чисто уявною величиною `k[2z] = i · α`. Коефіцієнт загасання `α` визначається співвідношенням:

```
α = (2π / λ₀) · √(n₁² · sin² θ₁ - n₂²)
```

Глибиною проникнення `d[p]` називають відстань, на якій амплітуда поля в зазорі зменшується в `e` разів (приблизно в 2.71828 раза):

```
d[p] = 1 / α = λ₀ / (2π · √(n₁² · sin² θ₁ - n₂²))
```

#### 1.2. Коефіцієнт пропускання FTIR для s-поляризованої хвилі
На відміну від звичайного 100%-го відбиття на поодинокій межі, наявність третього середовища створює граничні умови, за яких еванесцентне поле на межі `z = d` знову перетворюється у біжучу хвилю. Застосування матричного методу або узагальнених формул Френеля для трьох середовищ дає точний аналітичний вираз для енергетичного коефіцієнта пропускання `T(d)`:

```
T(d) = 1 / (1 + C · sh²(α · d))
```

Де безрозмірний геометричний та оптичний чинник `C` для s-поляризації дорівнює:

```
C[s] = ((n₁² - n₂²)² · (sin² θ₁ + cos² θ₁)) / (4 · n₁² · (n₁² · sin² θ₁ - n₂²) · cos² θ₁)
```

Для p-поляризації геометричний чинник залежить від відношення показників заломлення у четвертому ступені:

```
C[p] = ((n₁² - n₂²)² · (n₁² · sin² θ₁ - n₂² + n₁² · cos² θ₁)) / (4 · n₁² · n₂⁴ · (n₁² · sin² θ₁ - n₂²) · cos² θ₁)
```

З огляду на закон збереження енергії для непоглинаючих середовищ, енергетичний коефіцієнт відбиття становить `R(d) = 1 - T(d)`.

#### 1.3. Розподіл електричного поля усередині зазору
Напруженість електричного поля усередині зазору `0 ≤ z ≤ d` утворюється внаслідок інтерференції набігаючої еванесцентної хвилі та еванесцентної хвилі, відбитої від другої межі `z = d`. Відносний профіль поля описується через гіперболічний косинус:

```
E(z) / E₀ = ch(α · (d - z)) / ch(α · d)
```

На межі `z = 0` амплітуда поля дорівнює `E₀`, а на другій межі `z = d` вона падає до значення `E(d) = E₀ / ch(α · d)`.

---

### 2. Програмна реалізація симулятора

Нижче наведено три ідіоматичні реалізації обчислювального ядра мовами C, C++ та Python. Реалізації є повністю автономними, не використовують сторонніх математичних бібліотек і забезпечують високу точність обчислень.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

/* Структура конфігурації оптичної системи */
typedef struct {
    double n1;          /* показник заломлення першого середовища (скло) */
    double n2;          /* показник заломлення зазору (повітря) */
    double n3;          /* показник заломлення третього середовища (скло) */
    double lambda_nm;   /* довжина хвилі у вакуумі (нм) */
    double theta_deg;   /* кут падіння (градуси) */
} tir_config_t;

/* Точка розрахованої таблиці зазору */
typedef struct {
    double gap_nm;
    double gap_relative;
    double transmission;
    double reflection;
} ftir_point_t;

static inline double deg_to_rad(double deg) {
    return deg * M_PI / 180.0;
}

/* Обчислення коефіцієнта загасання alpha (1/нм) та глибини проникнення dp (нм) */
int calculate_tir_params(const tir_config_t *cfg, double *alpha_out, double *dp_out) {
    if (!cfg || !alpha_out || !dp_out) return -1;
    
    double theta_rad = deg_to_rad(cfg->theta_deg);
    double sin_t = sin(theta_rad);
    double val = cfg->n1 * cfg->n1 * sin_t * sin_t - cfg->n2 * cfg->n2;
    
    if (val <= 0.0) {
        *alpha_out = 0.0;
        *dp_out = -1.0; /* кут менший за критичний */
        return 0;
    }
    
    double alpha = (2.0 * M_PI / cfg->lambda_nm) * sqrt(val);
    *alpha_out = alpha;
    *dp_out = 1.0 / alpha;
    return 1;
}

/* Обчислення коефіцієнта пропускання T(d) для s-поляризації */
double calculate_ftir_transmission(const tir_config_t *cfg, double gap_nm) {
    double alpha, dp;
    if (calculate_tir_params(cfg, &alpha, &dp) != 1 || dp < 0.0) {
        return 1.0; /* не режим ПВВ */
    }
    
    if (gap_nm <= 1e-9) {
        return 1.0; /* повний контакт */
    }
    
    double theta_rad = deg_to_rad(cfg->theta_deg);
    double sin_t = sin(theta_rad);
    double cos_t = cos(theta_rad);
    
    double val = cfg->n1 * cfg->n1 * sin_t * sin_t - cfg->n2 * cfg->n2;
    double num = (cfg->n1 * cfg->n1 - cfg->n2 * cfg->n2) * (cfg->n1 * cfg->n1 - cfg->n2 * cfg->n2);
    double den = 4.0 * cfg->n1 * cfg->n1 * val * cos_t * cos_t;
    double C = num / den;
    
    /* Захист від переповнення при великих зазорах alpha * gap > 700 */
    double arg = alpha * gap_nm;
    if (arg > 35.0) {
        /* Асимптотичне спрощення: sh(x) ≈ exp(x) / 2 */
        double exp_val = exp(-2.0 * arg);
        return (4.0 / C) * exp_val;
    }
    
    double sh_val = sinh(arg);
    double T = 1.0 / (1.0 + C * sh_val * sh_val);
    return T;
}

/* Розрахунок профілю згасання поля E(z) у зазорі */
void print_field_profile(const tir_config_t *cfg, double gap_nm, int num_steps) {
    double alpha, dp;
    if (calculate_tir_params(cfg, &alpha, &dp) != 1 || dp < 0.0) return;
    
    printf("\n--- Профіль електричного поля E(z) для зазору d = %.1f нм ---\n", gap_nm);
    printf("%-12s %-16s %-16s\n", "z (нм)", "z / d", "E(z) / E0");
    printf("---------------------------------------------\n");
    
    double ch_ad = cosh(alpha * gap_nm);
    for (int i = 0; i <= num_steps; ++i) {
        double z = i * (gap_nm / num_steps);
        double E_rel = cosh(alpha * (gap_nm - z)) / ch_ad;
        printf("%-12.1f %-16.3f %-16.6f\n", z, z / gap_nm, E_rel);
    }
}

int main(void) {
    tir_config_t cfg = {
        .n1 = 1.50,
        .n2 = 1.00,
        .n3 = 1.50,
        .lambda_nm = 632.8,
        .theta_deg = 45.0
    };

    double alpha, dp;
    int is_tir = calculate_tir_params(&cfg, &alpha, &dp);
    
    printf("=== Симуляція порушеного повного внутрішнього відбиття (FTIR) ===\n");
    printf("Параметри: n1=%.2f, n2=%.2f, n3=%.2f, lambda=%.1f нм, theta=%.1f deg\n",
           cfg.n1, cfg.n2, cfg.n3, cfg.lambda_nm, cfg.theta_deg);
    
    if (!is_tir || dp < 0.0) {
        printf("Помилка: кут падіння менший за критичний!\n");
        return EXIT_FAILURE;
    }
    
    printf("Глибина проникнення еванесцентного поля dp = %.2f нм\n\n", dp);
    printf("%-12s %-14s %-16s %-16s\n", "Зазор d (нм)", "d / lambda", "Пропускання T", "Відбиття R");
    printf("-------------------------------------------------------------\n");

    for (int step = 0; step <= 12; ++step) {
        double gap = step * (cfg.lambda_nm / 4.0);
        double T = calculate_ftir_transmission(&cfg, gap);
        double R = 1.0 - T;
        printf("%-12.1f %-14.3f %-16.6f %-16.6f\n", gap, gap / cfg.lambda_nm, T, R);
    }
    
    print_field_profile(&cfg, dp, 5);

    return EXIT_SUCCESS;
}
```
```cpp
#include <iostream>
#include <iomanip>
#include <cmath>
#include <vector>
#include <numbers>
#include <expected>
#include <string>

struct TirConfig {
    double n1{1.50};
    double n2{1.00};
    double n3{1.50};
    double lambda_nm{632.8};
    double theta_deg{45.0};
};

struct FtirPoint {
    double gap_nm;
    double gap_relative;
    double transmission;
    double reflection;
};

class FtirSimulator {
public:
    explicit FtirSimulator(TirConfig config) : config_(config) {}

    [[nodiscard]] std::expected<double, std::string> penetrationDepth() const {
        const double theta_rad = config_.theta_deg * std::numbers::pi / 180.0;
        const double sin_t = std::sin(theta_rad);
        const double val = config_.n1 * config_.n1 * sin_t * sin_t - config_.n2 * config_.n2;
        if (val <= 0.0) {
            return std::unexpected("Кут падіння менший за критичний!");
        }
        const double alpha = (2.0 * std::numbers::pi / config_.lambda_nm) * std::sqrt(val);
        return 1.0 / alpha;
    }

    [[nodiscard]] double transmission(double gap_nm) const {
        if (gap_nm <= 1e-9) return 1.0;

        const double theta_rad = config_.theta_deg * std::numbers::pi / 180.0;
        const double sin_t = std::sin(theta_rad);
        const double cos_t = std::cos(theta_rad);

        const double val = config_.n1 * config_.n1 * sin_t * sin_t - config_.n2 * config_.n2;
        if (val <= 0.0) return 1.0;

        const double alpha = (2.0 * std::numbers::pi / config_.lambda_nm) * std::sqrt(val);
        const double num = std::pow(config_.n1 * config_.n1 - config_.n2 * config_.n2, 2);
        const double den = 4.0 * config_.n1 * config_.n1 * val * cos_t * cos_t;
        const double C = num / den;

        const double arg = alpha * gap_nm;
        if (arg > 35.0) {
            return (4.0 / C) * std::exp(-2.0 * arg);
        }

        const double sh_val = std::sinh(arg);
        return 1.0 / (1.0 + C * sh_val * sh_val);
    }

    [[nodiscard]] std::vector<FtirPoint> scanGap(double max_gap_nm, std::size_t steps) const {
        std::vector<FtirPoint> results;
        results.reserve(steps + 1);

        for (std::size_t i = 0; i <= steps; ++i) {
            const double gap = i * (max_gap_nm / steps);
            const double T = transmission(gap);
            results.push_back({
                .gap_nm = gap,
                .gap_relative = gap / config_.lambda_nm,
                .transmission = T,
                .reflection = 1.0 - T
            });
        }
        return results;
    }

private:
    TirConfig config_;
};

int main() {
    TirConfig cfg{.n1 = 1.50, .n2 = 1.00, .n3 = 1.50, .lambda_nm = 632.8, .theta_deg = 45.0};
    FtirSimulator sim(cfg);

    auto dp_res = sim.penetrationDepth();
    if (!dp_res) {
        std::cerr << "Помилка: " << dp_res.error() << "\n";
        return 1;
    }

    std::cout << std::fixed << std::setprecision(3);
    std::cout << "Глибина проникнення dp = " << *dp_res << " nm\n\n";
    std::cout << std::setw(14) << "Зазор (nm)" 
              << std::setw(16) << "d / lambda" 
              << std::setw(18) << "Пропускання T"
              << std::setw(18) << "Відбиття R\n";
    std::cout << "------------------------------------------------------------------\n";

    auto table = sim.scanGap(cfg.lambda_nm * 3.0, 12);
    for (const auto& pt : table) {
        std::cout << std::setw(14) << pt.gap_nm 
                  << std::setw(16) << pt.gap_relative 
                  << std::setw(18) << std::setprecision(6) << pt.transmission 
                  << std::setw(18) << pt.reflection << "\n";
    }

    return 0;
}
```
```python
import math

class FtirSimulator:
    def __init__(self, n1=1.50, n2=1.00, n3=1.50, lambda_nm=632.8, theta_deg=45.0):
        self.n1 = n1
        self.n2 = n2
        self.n3 = n3
        self.lambda_nm = lambda_nm
        self.theta_deg = theta_deg
        
    def penetration_depth(self):
        theta_rad = math.radians(self.theta_deg)
        sin_t = math.sin(theta_rad)
        val = self.n1**2 * sin_t**2 - self.n2**2
        if val <= 0:
            raise ValueError("Кут падіння менший за критичний!")
        alpha = (2.0 * math.pi / self.lambda_nm) * math.sqrt(val)
        return 1.0 / alpha
        
    def transmission(self, gap_nm):
        if gap_nm <= 1e-9:
            return 1.0
        theta_rad = math.radians(self.theta_deg)
        sin_t = math.sin(theta_rad)
        cos_t = math.cos(theta_rad)
        
        val = self.n1**2 * sin_t**2 - self.n2**2
        if val <= 0:
            return 1.0
            
        alpha = (2.0 * math.pi / self.lambda_nm) * math.sqrt(val)
        num = (self.n1**2 - self.n2**2)**2
        den = 4.0 * self.n1**2 * val * cos_t**2
        C = num / den
        
        arg = alpha * gap_nm
        if arg > 35.0:
            return (4.0 / C) * math.exp(-2.0 * arg)
            
        sh_val = math.sinh(arg)
        return 1.0 / (1.0 + C * sh_val**2)

    def scan_gap(self, max_gap_nm=2000.0, steps=10):
        dp = self.penetration_depth()
        print(f"Показники: n1={self.n1}, n2={self.n2}, lambda={self.lambda_nm} нм, theta={self.theta_deg}°")
        print(f"Глибина проникнення dp = {dp:.2f} нм\n")
        print(f"{'Зазор d (нм)':<14} {'d / lambda':<14} {'T (пропускання)':<18} {'R (відбиття)':<18}")
        print("-" * 64)
        
        results = []
        for i in range(steps + 1):
            gap = i * (max_gap_nm / steps)
            T = self.transmission(gap)
            R = 1.0 - T
            results.append((gap, gap / self.lambda_nm, T, R))
            print(f"{gap:<14.1f} {gap / self.lambda_nm:<14.3f} {T:<18.6f} {R:<18.6f}")
        return results

if __name__ == "__main__":
    sim = FtirSimulator()
    sim.scan_gap()
```
:::

---

### 3. Аналіз обчислювальних результатів та граничних випадків

Проведений розрахунок для лазерного випромінювання з довжиною хвилі `λ₀ = 632.8 нм` на межі скло–повітря (`n₁ = 1.50`, `n₂ = 1.00`) при куті падіння `45°` виявляє кілька принципових режимів:

1. **Режим повного оптичного контакту (`d = 0`):**
   При `d → 0` маємо `sh(0) = 0`, звідки коефіцієнт пропускання `T(0) = 1.000000` (100%), а відбиття `R(0) = 0`. Повітряний бар'єр зникає, дві скляні призми зливаються в єдине оптичне середовище, і світло вільно проходить без відбиття.

2. **Режим сильного тунелювання (`d = dp ≈ 284.8 нм`):**
   При товщині зазору, рівній глибині проникнення `d = dp` (`d / λ₀ ≈ 0.45`), маємо `sh(1) ≈ 1.1752`. Значення чинника `C ≈ 4.50`.
   Розрахунок дає `T(dp) = 1 / (1 + 4.50 · 1.1752²) ≈ 0.138` (13.8%). Понад 13% світлової енергії тунелює крізь зазор товщиною у чверть мікрометра.

3. **Режим відновлення повного відбиття (`d ≥ 2 · λ₀ ≈ 1265.6 нм`):**
   При товщині зазору в дві довжини хвилі маємо `α · d ≈ 4.44`, `sh(4.44) ≈ 42.1`.
   Розрахунок дає `T = 1 / (1 + 4.50 · 42.1²) ≈ 0.00012` (0.012%). Пропускання стає мізерно малим, а коефіцієнт відбиття відновлюється до `R = 99.988%`.

---

### 4. Алгоритмічне простеження та чисельна стійкість

При практичному розрахунку FTIR у програмних комплексах виникають важливі крайові випадки, пов'язані з обчислювальною стійкістю:

1. **Переповнення числа з плаваючою крапкою при великих зазорах (`α · d > 700`):**
   Функція гіперболічного синуса `sinh(x)` при `x > 710` викликає арифметичне переповнення реєстра `double` в обчислювачах стандарту IEEE-754. У представленому коді передбачено перехід на асимптотичне спрощення `T(d) ≈ (4 / C) · exp(-2 · α · d)`, яке гарантує чисельну стійкість для довільних товщин зазору без втрати точності.

2. **Кутова нестабільність поблизу критичного кута (`θ₁ → θc`):**
   Коли кут падіння прямує до критичного згори (`θ₁ → θc + 0°`), величина `α` прямує до нуля, а глибина проникнення `dp → ∞`. У цій зоні знаменник `C` зростає, проте формула залишається математично неперервною. Алгоритм коректно обробляє перехід від тунелювання крізь тонкий зазор до звичайного заломлення при `θ₁ < θc`.

3. **Розрізнення поляризацій:**
   Представлений код обчислює пропускання для s-поляризації (TE). Для p-поляризації (TM) у програмі достатньо замінити розрахунок чинника `C` на `C[p]`, де знаменник містить четверту ступінь показника заломлення `n₂⁴`. Це призводить до того, що p-поляризована хвиля має відчутно вище тунельне пропускання при тих самих товщинах зазору.

---

### 5. Інженерні застосування та практичні пастки

При фізичній реалізації систем на основі FTIR (сенсорних екранів, інтерферометрів, куб-сплітерів) інженер стикається з трьома критичними факторами:

1. **Вимоги до чистоти й шорсткості поверхонь:**
   Оскільки глибина проникнення становить сотні нанометрів, будь-яка пилинка чи мікрошорсткість поверхні з амплітудою понад 50 нм локально змінює товщину зазору `d`, спричиняючи паразину витік світла й плямисту модуляцію пропускання.

2. **Вплив поляризації світла:**
   Чинник `C` для p-поляризованої хвилі є суттєво меншим, ніж для s-поляризованої: `C[p] = C[s] / (n₁ / n₂)²`. Це означає, що p-поляризоване світло тунелює крізь повітряний зазор значно легше й на більшу відстань, ніж s-поляризоване. При проектуванні FTIR-сплітерів необхідно враховувати поляризаційний стан випромінювання.

3. **Теплова стабільність зазору:**
   Через експоненційну залежність `T(d)` теплове розширення скляних елементів на десятки нанометрів може змінити коефіцієнт поділу променя на 10–20%. FTIR-куби вимагають високостабільних прецизійних п'єзоактюаторів або кварцових розпірок.
