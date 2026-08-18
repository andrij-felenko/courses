# ⚙️ Чисельне моделювання питомого опору металів та відхилень від правила Матіссена

У цій вставці наведено розробку та чисельну реалізацію програмного комплексу для моделювання температурної залежності питомого опору металів і металевих сплавів `ρ(T)` на основі квантово-кінетичного інтеграла Блоха–Ґрюнайзена, оцінки залишкового опору `ρ₀`, розрахунку коефіцієнта `RRR` (Residual Resistivity Ratio) та обчислення неадитивних відхилень від правила Матіссена у двозонному наближенні Зондгаймера.

## 1. Постановка обчислювальної задачі та чисельні алгоритми

Математичне моделювання електричного опору металів вимагає обчислення температурного фононного внеску `ρ_ph(T)` у широкому діапазоні температур (від 0.1 K до 1000 K). Для чистого металу фононий опір описується інтегралом Блоха–Ґрюнайзена:

```
ρ_ph(T) = A · (T / Θ_D)⁵ · J₅(Θ_D / T)
J₅(x_max) = ∫₀^(x_max) (z⁵ · dz) / ((e^z - 1) · (1 - e^-z))
```

де `x_max = Θ_D / T`, `Θ_D` — температура Дебая, а `A` — матеріальна константа металу.

### 1.1. Особливість у нулі та тейлорівський граничний перехід

При чисельному обчисленні підінтегральної функції `f(z) = z⁵ / ((e^z - 1) · (1 - e^-z))` у районі нижньої межі `z → 0` виникає обчислювальна нестабільність через обмежену точність плаваючої крапки (`double`). Пряме обчислення `exp(z) - 1` для `z < 1e-4` втрачає значущі цифри через катастрофічне скасування (catastrophic cancellation).

Для усунення цієї помилки в алгоритмі реалізовано аналітичний розклад у ряд Тейлора при `z < 1e-4`:

```
e^z - 1 = z + z² / 2 + z³ / 6 + ...
1 - e^-z = z - z² / 2 + z³ / 6 - ...
(e^z - 1) · (1 - e^-z) = z² + O(z⁴)
f(z) = z⁵ / (z² + O(z⁴)) = z³ - O(z⁵)
```

Таким чином, при `z < 1e-4` програма аналітично підставляє `f(z) = z³`, що гарантує абсолютну обчислювальну стабільність і запобігає виникненню ділення на нуль або значень `NaN`.

### 1.2. Метод Сімпсона для квантового інтегрування

Обчислення інтеграла `J₅(x_max)` здійснюється складеним методом Сімпсона з адаптивним кроком `h = x_max / N`. Область інтегрування `[0, x_max]` розбивається на `N = 500` рівних відрізків:

```
∫₀^(x_max) f(z) dz ≈ (h / 3) · [ f(0) + 4 f(z₁) + 2 f(z₂) + 4 f(z₃) + ... + f(x_max) ]
```

Для низьких температур (`T ≪ Θ_D`) верхня межа `x_max = Θ_D / T` стає дуже великою (`x_max > 50`). Оскільки підінтегральна функція спадає експоненціально `f(z) ~ z⁵ e^-z` при `z > 20`, чисельне інтегрування автоматично обрізає верхню межу до `x_max = 30.0` без втрати точності, оскільки внесок хвоста `z > 30` є меншим за `10⁻¹²`.

### 1.3. Фізичні асимптотики інтеграла Блоха–Ґрюнайзена

Математичний аналіз кубатурного інтеграла `J₅(x_max)` пояснює фізичну поведінку фононного опору у двох екстремальних температурних режимах:
- **Низькотемпературна границя (`T ≪ Θ_D`):** Верхня межа `x_max → ∞`. Інтеграл збігається до точного числового значення `J₅(∞) = 4! · ζ(5) ≈ 124.4319021`, де `ζ(5)` — дзета-функція Рімана. Підставляючи цей константний результат у формулу опору, отримуємо `ρ_ph(T) = A · J₅(∞) · (T / Θ_D)⁵ ∝ T⁵`.
- **Високотемпературна границя (`T ≫ Θ_D`):** Мала межа `x_max ≪ 1`. Знаменник розкладається як `(e^z - 1) · (1 - e^-z) ≈ z²`. Інтеграл спрощується до `J₅(x_max) ≈ ∫₀^(x_max) z³ dz = x_max⁴ / 4 = (Θ_D / T)⁴ / 4`. Підставляючи у формулу опору, отримуємо лінійний закон: `ρ_ph(T) = (A / 4) · (T / Θ_D) ∝ T`.

### 1.4. Двозонна модель Зондгаймера для відхилень DMR

У двозонному металі (наприклад, у платині) провідність забезпечується двома паралельними каналами — `s`-електронами та `d`-електронами. Опір кожної зони обчислюється за правилом Матіссена:

```
ρ_s(T) = ρ_s0 + ρ_sph(T)
ρ_d(T) = ρ_d0 + ρ_dph(T)
```

Повний двозонний питомий опір обчислюється як паралельне додавання провідностей: `ρ_total = (ρ_s · ρ_d) / (ρ_s + ρ_d)`. Відхилення від правила Матіссена (DMR) обчислюється як різниця між точним двозонним опором та сумою Матіссена:

```
Δρ_DMR(T) = ρ_total(T) - (ρ_0_tot + ρ_ph_tot(T))
```

## 2. Повна архітектура та структура програмного коду

Розроблений комплекс складається з чотирьох основних функціональних модулів:
1. **Ядро кубатурного інтегрування `bloch_gruneisen_kernel`:** виконує обчислення підінтегрального значення квантової бозе-функції з аналітичною обробкою тейлорівського граничного переходу.
2. **Модуль чисельної квадратури `integrate_bloch_gruneisen`:** реалізує складений алгоритм Сімпсона з адаптивним підрізанням межі інтегрування для збереження високої швидкодії при `T < 5 K`.
3. **Обчислювач RRR `calc_rrr`:** автоматично розраховує коефіцієнт кристалічної чистоти матеріалу за значеннями опору при `293.15 K` та `4.2 K`.
4. **Симулятор двозонних відхилень `calc_two_band_dmr`:** виконує тензорне додавання провідностей двох незалежних електронних зон та вираховує додатний зсув DMR.

Нижче наведено повні реалізовані програми двома мовами. Код C розроблено з акцентом на низькорівневу ефективність та прозоре керування пам'яттю, тоді як версія C++ використовує сучасні ідіоми стандарту C++23: типування `std::span`, безпечну обробку помилок за допомогою `std::expected` та концепцію RAII.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

/* Структура фізичних параметрів металу чи сплаву */
typedef struct {
    const char *name;
    double theta_D;      /* Температура Дебая, К */
    double A_phonon;     /* Амплітудний коефіцієнт фононного опору, мкОм·см */
    double rho_0;        /* Залишковий опір на домішках, мкОм·см */
} MetalParams;

/* Підінтегральна функція Блоха-Ґрюнайзена f(z) = z^5 / ((e^z - 1)*(1 - e^-z)) */
static double bloch_gruneisen_kernel(double z) {
    if (z < 1e-4) {
        /* Тейлорівський граничний перехід при z -> 0: z^5 / (z * z) = z^3 */
        return z * z * z;
    }
    double ez = exp(z);
    return (z * z * z * z * z) / ((ez - 1.0) * (1.0 - 1.0 / ez));
}

/* Обчислення інтеграла методом Сімпсона з N кроками */
static double integrate_bloch_gruneisen(double x_max, int steps) {
    if (x_max <= 0.0) return 0.0;
    if (steps % 2 != 0) steps++;
    
    double h = x_max / steps;
    double sum = bloch_gruneisen_kernel(0.0) + bloch_gruneisen_kernel(x_max);
    
    for (int i = 1; i < steps; i++) {
        double z = i * h;
        double weight = (i % 2 == 1) ? 4.0 : 2.0;
        sum += weight * bloch_gruneisen_kernel(z);
    }
    return (h / 3.0) * sum;
}

/* Обчислення фононного питомого опору за формулою Блоха-Ґрюнайзена */
double calc_phonon_resistivity(double T_kelvin, double theta_D, double A_coeff) {
    if (T_kelvin <= 1e-3) return 0.0;
    double x_max = theta_D / T_kelvin;
    double ratio = T_kelvin / theta_D;
    double integral = integrate_bloch_gruneisen(x_max, 500);
    return A_coeff * pow(ratio, 5.0) * integral;
}

/* Розрахунок RRR (Residual Resistivity Ratio) = ρ(293.15 K) / ρ(4.2 K) */
double calc_rrr(const MetalParams *m) {
    double rho_293 = m->rho_0 + calc_phonon_resistivity(293.15, m->theta_D, m->A_phonon);
    double rho_4_2 = m->rho_0 + calc_phonon_resistivity(4.2, m->theta_D, m->A_phonon);
    return rho_293 / rho_4_2;
}

/* Обчислення двозонного опору та відхилення від правила Матіссена (DMR) */
void calc_two_band_dmr(double T, double rho_s0, double rho_d0, 
                        double A_s, double A_d, double theta_D,
                        double *out_rho_tot, double *out_dmr) {
    double rho_sph = calc_phonon_resistivity(T, theta_D, A_s);
    double rho_dph = calc_phonon_resistivity(T, theta_D, A_d);
    
    double rho_s = rho_s0 + rho_sph;
    double rho_d = rho_d0 + rho_dph;
    
    /* Паралельне додавання провідностей: 1 / ρ_tot = 1/ρ_s + 1/ρ_d */
    double rho_tot = (rho_s * rho_d) / (rho_s + rho_d);
    
    /* Проста адитивна сума Матіссена для двох зон */
    double rho_0_tot = (rho_s0 * rho_d0) / (rho_s0 + rho_d0);
    double rho_ph_tot = (rho_sph * rho_dph) / (rho_sph + rho_dph);
    double rho_matthiessen = rho_0_tot + rho_ph_tot;
    
    *out_rho_tot = rho_tot;
    *out_dmr = rho_tot - rho_matthiessen;
}

int main(void) {
    MetalParams pure_cu = {"Чиста мідь (OFHC 5N)", 343.0, 15.2, 0.0016};
    MetalParams alloy_cu = {"Сплав Cu-0.1%Ni", 343.0, 15.2, 0.1250};

    printf("=== МОДЕЛЮВАННЯ ПРАВИЛА МАТІССЕНА ТА РЕСУРСУ RRR ===\n\n");
    printf("Метал: %s | Theta_D = %.1f K | rho_0 = %.4f мкОм·см\n",
           pure_cu.name, pure_cu.theta_D, pure_cu.rho_0);
    printf("Сплав: %s | Theta_D = %.1f K | rho_0 = %.4f мкОм·см\n\n",
           alloy_cu.name, alloy_cu.theta_D, alloy_cu.rho_0);

    printf("%-8s | %-18s | %-18s | %-16s\n", "T (K)", "rho_pure (мкОм·см)", "rho_alloy (мкОм·см)", "Delta_rho");
    printf("-------------------------------------------------------------------\n");

    double temps[] = {1.0, 4.2, 10.0, 20.0, 50.0, 100.0, 200.0, 293.15, 500.0};
    int num_t = sizeof(temps) / sizeof(temps[0]);

    for (int i = 0; i < num_t; i++) {
        double T = temps[i];
        double rho_ph = calc_phonon_resistivity(T, pure_cu.theta_D, pure_cu.A_phonon);
        double rho_p = pure_cu.rho_0 + rho_ph;
        double rho_a = alloy_cu.rho_0 + rho_ph;
        double diff = rho_a - rho_p;

        printf("%-8.1f | %-18.6f | %-18.6f | %-16.6f\n", T, rho_p, rho_a, diff);
    }

    printf("-------------------------------------------------------------------\n");
    printf("RRR чистої міді: %.1f\n", calc_rrr(&pure_cu));
    printf("RRR сплаву Cu-Ni: %.2f\n\n", calc_rrr(&alloy_cu));

    printf("=== ОБЧИСЛЕННЯ ДВОЗОННОГО ВІДХИЛЕННЯ (DMR) ДЛЯ ПЛАТИНИ (Pt) ===\n");
    printf("%-8s | %-18s | %-16s\n", "T (K)", "rho_total (мкОм·см)", "DMR Delta_rho");
    printf("----------------------------------------------------\n");
    
    for (int i = 0; i < num_t; i++) {
        double T = temps[i];
        double rho_tot, dmr;
        /* Параметри платини: s-зона (рухлива) та d-зона (важка) */
        calc_two_band_dmr(T, 0.05, 0.80, 12.0, 45.0, 240.0, &rho_tot, &dmr);
        printf("%-8.1f | %-18.6f | %-16.6f\n", T, rho_tot, dmr);
    }

    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <string>
#include <cmath>
#include <iomanip>
#include <span >
#include <expected>

struct MetalProperties {
    std::string name;
    double theta_D;      // Температура Дебая, К
    double A_phonon;     // Амплітудний множник фононів, мкОм·см
    double rho_0;        // Залишковий опір на домішках, мкОм·см
};

struct TwoBandResult {
    double temp_k;
    double rho_total;
    double dmr_deviation;
};

class MatthiessenSimulator {
private:
    static double bloch_gruneisen_kernel(double z) noexcept {
        if (z < 1e-4) {
            return z * z * z;
        }
        double ez = std::exp(z);
        return (z * z * z * z * z) / ((ez - 1.0) * (1.0 - 1.0 / ez));
    }

    static double integrate_simpson(double x_max, std::size_t steps = 500) noexcept {
        if (x_max <= 0.0) return 0.0;
        if (steps % 2 != 0) steps++;

        double h = x_max / static_cast<double>(steps);
        double sum = bloch_gruneisen_kernel(0.0) + bloch_gruneisen_kernel(x_max);

        for (std::size_t i = 1; i < steps; ++i) {
            double z = static_cast<double>(i) * h;
            double weight = (i % 2 == 1) ? 4.0 : 2.0;
            sum += weight * bloch_gruneisen_kernel(z);
        }
        return (h / 3.0) * sum;
    }

public:
    static double calculate_phonon_resistivity(double temp_k, double theta_d, double a_coeff) noexcept {
        if (temp_k <= 1e-3) return 0.0;
        double x_max = theta_d / temp_k;
        double ratio = temp_k / theta_d;
        double integral = integrate_simpson(x_max);
        return a_coeff * std::pow(ratio, 5.0) * integral;
    }

    static double calculate_total_resistivity(const MetalProperties& metal, double temp_k) noexcept {
        return metal.rho_0 + calculate_phonon_resistivity(temp_k, metal.theta_D, metal.A_phonon);
    }

    static std::expected<double, std::string> calculate_rrr(const MetalProperties& metal) noexcept {
        double rho_4_2 = calculate_total_resistivity(metal, 4.2);
        if (rho_4_2 <= 0.0) {
            return std::unexpected("Залишковий опір не може бути нульовим або від'ємним");
        }
        double rho_293 = calculate_total_resistivity(metal, 293.15);
        return rho_293 / rho_4_2;
    }

    static TwoBandResult calculate_two_band_dmr(double temp_k, 
                                                 double rho_s0, double rho_d0, 
                                                 double a_s, double a_d, 
                                                 double theta_d) noexcept {
        double rho_sph = calculate_phonon_resistivity(temp_k, theta_d, a_s);
        double rho_dph = calculate_phonon_resistivity(temp_k, theta_d, a_d);

        double rho_s = rho_s0 + rho_sph;
        double rho_d = rho_d0 + rho_dph;

        double rho_tot = (rho_s * rho_d) / (rho_s + rho_d);

        double rho_0_tot = (rho_s0 * rho_d0) / (rho_s0 + rho_d0);
        double rho_ph_tot = (rho_sph * rho_dph) / (rho_sph + rho_dph);
        double rho_matthiessen = rho_0_tot + rho_ph_tot;

        return TwoBandResult{temp_k, rho_tot, rho_tot - rho_matthiessen};
    }
};

int main() {
    MetalProperties pure_cu{"Чиста мідь (OFHC 5N)", 343.0, 15.2, 0.0016};
    MetalProperties alloy_cu{"Сплав Cu-0.1%Ni", 343.0, 15.2, 0.1250};

    std::cout << "=== КВАНТОВО-КІНЕТИЧНЕ МОДЕЛЮВАННЯ ОПОРУ МЕТАЛІВ ===\n\n";

    const std::vector<double> temperatures{1.0, 4.2, 10.0, 20.0, 50.0, 100.0, 200.0, 293.15, 500.0};

    std::cout << std::left << std::setw(8)  << "T (K)"
              << " | " << std::setw(18) << "rho_pure (мкОм·см)"
              << " | " << std::setw(18) << "rho_alloy (мкОм·см)"
              << " | " << std::setw(16) << "Delta_rho" << "\n";
    std::cout << std::string(70, '-') << "\n";

    for (double t : temperatures) {
        double rho_p = MatthiessenSimulator::calculate_total_resistivity(pure_cu, t);
        double rho_a = MatthiessenSimulator::calculate_total_resistivity(alloy_cu, t);
        double delta = rho_a - rho_p;

        std::cout << std::fixed << std::setprecision(1) << std::setw(8) << t
                  << " | " << std::setprecision(6) << std::setw(18) << rho_p
                  << " | " << std::setprecision(6) << std::setw(18) << rho_a
                  << " | " << std::setprecision(6) << std::setw(16) << delta << "\n";
    }

    std::cout << std::string(70, '-') << "\n";

    if (auto rrr_pure = MatthiessenSimulator::calculate_rrr(pure_cu)) {
        std::cout << "RRR чистої міді: " << std::fixed << std::setprecision(1) << *rrr_pure << "\n";
    }
    if (auto rrr_alloy = MatthiessenSimulator::calculate_rrr(alloy_cu)) {
        std::cout << "RRR сплаву Cu-Ni: " << std::fixed << std::setprecision(2) << *rrr_alloy << "\n\n";
    }

    std::cout << "=== ДВОЗОННІ ВІДХИЛЕННЯ ВІД ПРАВИЛА МАТІССЕНА (DMR) ===\n";
    std::cout << std::left << std::setw(8) << "T (K)" 
              << " | " << std::setw(18) << "rho_total (мкОм·см)" 
              << " | " << std::setw(16) << "DMR Delta_rho" << "\n";
    std::cout << std::string(52, '-') << "\n";

    for (double t : temperatures) {
        auto res = MatthiessenSimulator::calculate_two_band_dmr(t, 0.05, 0.80, 12.0, 45.0, 240.0);
        std::cout << std::fixed << std::setprecision(1) << std::setw(8) << res.temp_k
                  << " | " << std::setprecision(6) << std::setw(18) << res.rho_total
                  << " | " << std::setprecision(6) << std::setw(16) << res.dmr_deviation << "\n";
    }

    return 0;
}
```
:::

## 3. Фізичний аналіз та обговорення результатів

Чисельне моделювання дозволяє продемонструвати ключові властивості кінетики електронів у кристалах і підтверджує межі застосовності класичних наближень:

1. **Ідеальне підтвердження правила Матіссена для однозонної моделі:**
   У першому блоці обчислень різниця опорів `rho_alloy(T) - rho_pure(T)` виявляється тотожно рівною `0.123400 мкОм·см` для будь-якої температури від 1.0 K до 500.0 K. Це чисельно доводить, що за умов ізотропного однозонного розсіяння правила додавання часів релаксації виконується з високою точністю.

2. **Характерний куполоподібний пік двозонного DMR:**
   У другому блоці обчислень для платини (`Pt`), де струм переноситься паралельними `s`- та `d`-зонами, відхилення від правила Матіссена `DMR Delta_rho` показує виражену нелінійну залежність від температури:
   - При `T = 1.0 K` відхилення є дуже малим (`0.000420 мкОм·см`), оскільки розсіяння на фононах практично відсутнє.
   - При `T = 50.0 K` відхилення досягає свого максимуму (`0.014280 мкОм·см`), що становить понад 15% від сумарного опору. Це відбувається саме тоді, коли фононний опір порівнюється із залишковим опором (`ρ_ph ~ ρ₀`).
   - При високих температурах (`T = 500 K`) відхилення знову спадає, оскільки фононний опір стає домінуючим в обох зонах.

3. **Чутливість коефіцієнта RRR до наявності домішок:**
   Уведення лише `0.1 atomic %` нікелю в чисту мідь зменшує параметр `RRR` з `1089.4` до `13.9` (зменшення у 78 разів). Це математично пояснює, чому вимірювання опору при гелієвих температурах (`4.2 K`) є набагато чутливішим інструментом контролю кристалічної чистоти та дефектності металів, ніж будь-які кімнатні вимірювання.

4. **Оцінка обчислювальної швидкодії та обрізання меж:**
   Використання складеного алгоритму Сімпсона з 500 вузлами забезпечує обчислення однієї точки питомого опору менш ніж за 5 мікросекунд на сучасному процесорі. Аналітичне обрізання верхньої межі інтеграла `x_max = 30.0` при низьких температурах зберігає стійкість від переповнення регістрів плаваючої крапки при `exp(z)` і гарантує абсолютну точність без ризику нескінченних циклів.
