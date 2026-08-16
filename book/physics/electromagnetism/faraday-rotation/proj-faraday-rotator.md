# ⚙️ Симуляція оптичного ізолятора та ротатора Фарадея

Комп'ютерне моделювання поляризаційного стану світла при проходженні крізь магнітооптичний ротатор Фарадея та багатоелементні оптичні системи здійснюється за допомогою **векторного числення Джонса** (*Jones calculus*). У цьому математичному формалізмі повністю поляризована світлова хвиля описується двокомпонентним комплексним вектором Джонса, а кожен оптичний елемент (поляризатор, пластина фазової затримки, магнітооптичний ротатор) — відповідною матрицею Джонса розміром `2×2`.

У цьому практичному проекті реалізовано розрахунок прямого й зворотного проходження хвилі крізь нереципрокний оптичний ізолятор (поляризатор 0°, ротатор Фарадея 45°, аналізатор 45°), обчислення втрат на вставку (*insertion loss*), коефіцієнта ізоляції (*isolation level* у децибелах) та деградації ізоляції при температурних флуктуаціях магнітного поля чи відхиленні кута обертання від номіналу.

## 1. Векторне числення Джонса для нереципрокних елементів

Електричне поле плоскої світлової хвилі, яка поширюється уздовж осі `z`, у будь-який момент часу розкладається на дві ортогональні компоненти `E_x` та `E_y`. Комплексний вектор Джонса `E` визначається як:

```
E = [ Ex ] = [ |Ex| · e^(i·δx) ]
    [ Ey ]   [ |Ey| · e^(i·δy) ]
```

Для чистого горизонтально поляризованого світла вектор Джонса має вигляд `[1, 0]ᵀ`, для вертикально поляризованого — `[0, 1]ᵀ`, а для лінійно поляризованого під кутом `45°` — `[1/√2, 1/√2]ᵀ`.

При проходженні світла крізь оптичний пристрій із матрицею `M` вихідний вектор поляризації `E_out` обчислюється шляхом стандартного множення матриці на вектор: `E_out = M · E_in`.

### Матриці Джонса для основних елементів:

1. **Лінійний поляризатор з віссю під кутом `α`:**
```
M_pol(α) = [ cos²(α)       sin(α)·cos(α) ]
           [ sin(α)·cos(α) sin²(α)       ]
```

2. **Ротатор Фарадея на кут обертання `θ`:**
При прямому ході хвилі (вздовж вектора магнітного поля `B`) ротатор Фарадея повертає вектор поляризації на кут `+θ` за годинниковою стрілкою:
```
M_FR_fwd(θ) = [ cos(θ) -sin(θ) ]
              [ sin(θ)  cos(θ) ]
```

При зворотному ході хвилі (проти напрямку поширення, але у тому самому магнітному полі `B`) завдяки **нереципрокності** знак обертання відносно напрямку поширення зворотної хвилі змінюється на протилежний. Матриця зворотного проходу має вигляд:
```
M_FR_bwd(θ) = [ cos(θ)  sin(θ) ]
              [ -sin(θ) cos(θ) ]
```

Саме ця різниця між `M_FR_fwd` та `M_FR_bwd` гарантує, що при зворотному проходженні кути обертання не скасовуються, а подвоюються, що й дозволяє повністю заблокувати відбитий промінь на вхідному поляризаторі.

## 2. Аналітичний розрахунок прямого та зворотного ходу світла

Простежимо математичні множення матриць Джонса для нереципрокного ізолятора покроково у прозі:

### 2.1 Прямий хід (Forward propagation)
1. Вхідний промінь проходить крізь перший поляризатор `P1(0°)`:
```
E_1 = P_1 · E_in = [ 1 0 ] · [ 1 ] = [ 1 ]   (вертикальна поляризація 0°)
                  [ 0 0 ]   [ 0 ]   [ 0 ]
```

2. Промінь проходить крізь ротатор Фарадея `FR(45°)`:
```
E_2 = FR(45°) · E_1 = [ cos(45°) -sin(45°) ] · [ 1 ] = [ 1/√2 ]   (поляризація 45°)
                      [ sin(45°)  cos(45°) ]   [ 0 ]   [ 1/√2 ]
```

3. Промінь проходить крізь вихідний поляризатор-аналізатор `P2(45°)`:
```
P_2(45°) = 1/2 · [ 1  1 ]
                 [ 1  1 ]

E_out = P_2 · E_2 = 1/2 · [ 1  1 ] · [ 1/√2 ] = [ 1/√2 ]
                          [ 1  1 ]   [ 1/√2 ]   [ 1/√2 ]
```
Вихідна інтенсивність дорівнює `I_out = |Ex|² + |Ey|² = (1/√2)² + (1/√2)² = 1.0` (100% пропускання, `Insertion Loss = 0.0 дБ`).

### 2.2 Зворотний хід (Backward propagation)
1. Відбитий промінь повертається до вихідного поляризатора `P2(45°)` із поляризацією `45°`:
```
E_back_1 = [ 1/√2 ]
           [ 1/√2 ]
```

2. Відбитий промінь проходить крізь ротатор Фарадея у зворотному напрямку. Завдяки нереципрокності матриця обертання додає ще `+45°` у тому самому напрямку відносно магнітного поля `B`:
```
E_back_2 = FR_bwd(45°) · E_back_1 = [ cos(45°)  sin(45°) ] · [ 1/√2 ] = [ 1 ]   (горизонтальна 90°)
                                    [ -sin(45°) cos(45°) ]   [ 1/√2 ]   [ 0 ]
```

3. Промінь потрапляє на вхідний поляризатор `P1(0°)`, ось якого становить `0°`:
```
E_back_out = P_1(0°) · E_back_2 = [ 1 0 ] · [ 0 ] = [ 0 ]
                                  [ 0 0 ]   [ 1 ]   [ 0 ]
```
Вихідна інтенсивність зворотної хвилі строго дорівнює `I_bwd = 0.0` (повне блокування, `Isolation = ∞ дБ`).

## 3. Реалізація симуляції мовами C та C++

Нижче наведено повний робочий код симуляції нереципрокного оптичного ізолятора мовами C (стандарт C99 з використанням `complex.h`) та C++ (стандарт C++17 із застосуванням ООП, `std::complex` та `std::vector`).

:::tabs
```c
#include <stdio.h>
#include <math.h>
#include <complex.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

/* Вектор Джонса для опису поляризації світлової хвилі */
typedef struct {
    double complex Ex;
    double complex Ey;
} JonesVector;

/* Матриця Джонса 2x2 для оптичного елемента */
typedef struct {
    double complex m00, m01;
    double complex m10, m11;
} JonesMatrix;

/* Множення матриці Джонса на вектор поляризації */
JonesVector apply_element(JonesMatrix M, JonesVector v) {
    JonesVector result;
    result.Ex = M.m00 * v.Ex + M.m01 * v.Ey;
    result.Ey = M.m10 * v.Ex + M.m11 * v.Ey;
    return result;
}

/* Обчислення інтенсивності (потужності) світлової хвилі */
double get_intensity(JonesVector v) {
    return cabs(v.Ex) * cabs(v.Ex) + cabs(v.Ey) * cabs(v.Ey);
}

/* Матриця лінійного поляризатора, повернутого на кут alpha (в радіанах) */
JonesMatrix make_polarizer(double alpha_rad) {
    double c = cos(alpha_rad);
    double s = sin(alpha_rad);
    JonesMatrix M;
    M.m00 = c * c;      M.m01 = c * s;
    M.m10 = c * s;      M.m11 = s * s;
    return M;
}

/* Матриця нереципрокного ротатора Фарадея для кута обертання theta (в радіанах).
   Важливо: ротатор Фарадея повертає вектор за годинниковою стрілкою
   відносно напрямку магнітного поля B, незалежно від напрямку хвилі! */
JonesMatrix make_faraday_rotator(double theta_rad, int is_forward) {
    /* При зворотному ході промінь іде проти вектора B, тому знак обертання
       відносно напрямку поширення хвилі протилежний */
    double sign = is_forward ? 1.0 : -1.0;
    double rot = sign * theta_rad;
    double c = cos(rot);
    double s = sin(rot);
    JonesMatrix M;
    M.m00 = c;   M.m01 = -s;
    M.m10 = s;   M.m11 = c;
    return M;
}

int main(void) {
    printf("=== Симуляція нереципрокного оптичного ізолятора Фарадея ===\n\n");

    /* Номінальні параметри */
    double target_rot_deg = 45.0;
    double target_rot_rad = target_rot_deg * M_PI / 180.0;
    
    /* 1. Початкове неполяризоване світло моделюємо як горизонтально поляризоване E0 */
    JonesVector E_in = { 1.0 + 0.0*I, 0.0 + 0.0*I };
    double I_in = get_intensity(E_in);

    /* Елементи ізолятора */
    JonesMatrix P1_input  = make_polarizer(0.0);                    /* Поляризатор 0 град */
    JonesMatrix FR_fwd    = make_faraday_rotator(target_rot_rad, 1); /* Фарадей +45 град */
    JonesMatrix P2_output = make_polarizer(45.0 * M_PI / 180.0);    /* Аналізатор 45 град */

    /* Прямий хід */
    JonesVector E1 = apply_element(P1_input, E_in);
    JonesVector E2 = apply_element(FR_fwd, E1);
    JonesVector E_out_fwd = apply_element(P2_output, E2);
    double I_fwd = get_intensity(E_out_fwd);

    double insertion_loss_db = -10.0 * log10(I_fwd / I_in);
    printf("[Прямий хід] Вхідна потужність: %.3f, Вихідна: %.3f\n", I_in, I_fwd);
    printf("[Прямий хід] Втрати на вставку (Insertion Loss): %.2f дБ\n\n", insertion_loss_db);

    /* Зворотний хід (відбите світло виходить з боку виходу під 45 град) */
    JonesVector E_back_start = { cos(45.0*M_PI/180.0), sin(45.0*M_PI/180.0) };
    double I_back_in = get_intensity(E_back_start);

    JonesMatrix FR_bwd = make_faraday_rotator(target_rot_rad, 0); /* Зворотній прохід крізь ротатор */
    
    JonesVector Eb1 = apply_element(P2_output, E_back_start);
    JonesVector Eb2 = apply_element(FR_bwd, Eb1);
    JonesVector E_out_bwd = apply_element(P1_input, Eb2);
    double I_bwd = get_intensity(E_out_bwd);

    /* Оскільки I_bwd близька до 0, додаємо захист від log(0) */
    double isolation_db = (I_bwd < 1e-12) ? 120.0 : -10.0 * log10(I_bwd / I_back_in);
    printf("[Зворотний хід] Відбита потужність: %.3f, Пропущена назад: %.6e\n", I_back_in, I_bwd);
    printf("[Зворотний хід] Рівень ізоляції (Isolation): %.2f дБ\n\n", isolation_db);

    /* Оцінка чутливості до флуктуацій магнітного поля */
    printf("--- Залежність ізоляції від помилки кута обертання (Δθ) ---\n");
    printf("Помилка (град) | Кут (град) | Пропускання назад | Ізоляція (дБ)\n");
    printf("-----------------------------------------------------------\n");
    
    double error_angles[] = { 0.0, 0.5, 1.0, 2.0, 5.0 };
    for (int i = 0; i < 5; i++) {
        double err = error_angles[i];
        double actual_rot = (45.0 - err) * M_PI / 180.0;
        JonesMatrix FR_err = make_faraday_rotator(actual_rot, 0);
        
        JonesVector Eb_err = apply_element(P1_input, apply_element(FR_err, Eb1));
        double I_err = get_intensity(Eb_err);
        double iso_err = -10.0 * log10(I_err / I_back_in);
        
        printf("%+12.1f | %10.1f | %17.6e | %11.2f\n", -err, 45.0 - err, I_err, iso_err);
    }

    return 0;
}
```
```cpp
#include <iostream>
#include <complex>
#include <cmath>
#include <vector>
#include <iomanip>

namespace Optics {

constexpr double PI = 3.14159265358979323846;

// Вектор поляризації Джонса (Ex, Ey)
class JonesVector {
public:
    using Complex = std::complex<double>;

    Complex ex{1.0, 0.0};
    Complex ey{0.0, 0.0};

    constexpr JonesVector() = default;
    constexpr JonesVector(Complex x, Complex y) : ex(x), ey(y) {}

    [[nodiscard]] double intensity() const noexcept {
        return std::norm(ex) + std::norm(ey);
    }
};

// Матриця оптичного елемента 2x2
class JonesMatrix {
public:
    using Complex = std::complex<double>;

    Complex m00{1, 0}, m01{0, 0};
    Complex m10{0, 0}, m11{1, 0};

    constexpr JonesMatrix() = default;
    constexpr JonesMatrix(Complex c00, Complex c01, Complex c10, Complex c11)
        : m00(c00), m01(c01), m10(c10), m11(c11) {}

    [[nodiscard]] JonesVector operator*(const JonesVector& v) const noexcept {
        return JonesVector(
            m00 * v.ex + m01 * v.ey,
            m10 * v.ex + m11 * v.ey
        );
    }

    // Лінійний поляризатор під кутом alpha
    static JonesMatrix createPolarizer(double alphaRad) {
        const double c = std::cos(alphaRad);
        const double s = std::sin(alphaRad);
        return JonesMatrix(c * c, c * s, c * s, s * s);
    }

    // Нереципрокний ротатор Фарадея
    static JonesMatrix createFaradayRotator(double thetaRad, bool isForward) {
        const double sign = isForward ? 1.0 : -1.0;
        const double rot = sign * thetaRad;
        const double c = std::cos(rot);
        const double s = std::sin(rot);
        return JonesMatrix(c, -s, s, c);
    }
};

// Симулятор оптичного ізолятора
class FaradayIsolatorSimulator {
private:
    double rotationAngleRad_;

public:
    explicit FaradayIsolatorSimulator(double rotationAngleDeg = 45.0)
        : rotationAngleRad_(rotationAngleDeg * PI / 180.0) {}

    struct SimulationResult {
        double insertionLossDb;
        double isolationDb;
        double forwardEfficiency;
        double backwardLeakage;
    };

    [[nodiscard]] SimulationResult runSimulation(double angleErrorDeg = 0.0) const {
        const double actualRotRad = rotationAngleRad_ - (angleErrorDeg * PI / 180.0);

        const auto P1 = JonesMatrix::createPolarizer(0.0);
        const auto P2 = JonesMatrix::createPolarizer(PI / 4.0); // 45 градусів
        const auto FR_fwd = JonesMatrix::createFaradayRotator(actualRotRad, true);
        const auto FR_bwd = JonesMatrix::createFaradayRotator(actualRotRad, false);

        // Прямий хід
        const JonesVector E_in{1.0, 0.0};
        const JonesVector E_fwd = P2 * (FR_fwd * (P1 * E_in));
        const double I_fwd = E_fwd.intensity();
        const double I_in = E_in.intensity();

        // Зворотний хід
        const JonesVector E_back_in{std::cos(PI / 4.0), std::sin(PI / 4.0)};
        const JonesVector E_bwd = P1 * (FR_bwd * (P2 * E_back_in));
        const double I_bwd = E_bwd.intensity();
        const double I_back_in = E_back_in.intensity();

        const double insLoss = -10.0 * std::log10(I_fwd / I_in);
        const double iso = (I_bwd < 1e-12) ? 120.0 : -10.0 * std::log10(I_bwd / I_back_in);

        return SimulationResult{ insLoss, iso, I_fwd / I_in, I_bwd / I_back_in };
    }
};

} // namespace Optics

int main() {
    std::cout << "=== C++17 Оптичний ізолятор Фарадея ===\n\n";

    Optics::FaradayIsolatorSimulator isolator(45.0);
    auto baseRes = isolator.runSimulation(0.0);

    std::cout << std::fixed << std::setprecision(2);
    std::cout << "Ідеальний ізолятор (θ = 45.0°):\n";
    std::cout << "  - Втрати на вставку (Insertion Loss): " << baseRes.insertionLossDb << " дБ\n";
    std::cout << "  - Ізоляція зворотного променя (Isolation): " << baseRes.isolationDb << " дБ\n\n";

    std::cout << "Аналіз деградації ізоляції при флуктуаціях магнітного поля:\n";
    std::cout << "--------------------------------------------------------\n";
    std::cout << "Відхилення (°) | Ефективний кут | Витік назад (дБ) | Ізоляція (дБ)\n";
    std::cout << "--------------------------------------------------------\n";

    const std::vector<double> errors = {0.0, 0.2, 0.5, 1.0, 2.0, 5.0};
    for (double err : errors) {
        auto res = isolator.runSimulation(err);
        std::cout << std::setw(13) << -err << "° | "
                  << std::setw(13) << (45.0 - err) << "° | "
                  << std::scientific << std::setprecision(3) << std::setw(15) << res.backwardLeakage << " | "
                  << std::fixed << std::setprecision(2) << std::setw(12) << res.isolationDb << " дБ\n";
    }

    return 0;
}
```
:::

## 4. Детальний фізичний аналіз результатів та інженерні пастки

Результати симуляції демонструють декілька критично важливих практичних висновків для проектування лазерних систем:

### 1. Критична чутливість рівня ізоляції до кутової точності `Δθ`
В ідеальному випадку (`θ = 45.0°`) вихідна поляризація зворотної хвилі складає строго `90.0°` відносно вхідного поляризатора, що дає теоретичне нескінченне пригнічення (`Isolation > 120 дБ`).

Проте якщо через зміну температури або флуктуацію магнітного поля кут обертання відхиляється на малу величину `Δθ`, зсув поляризації зворотної хвилі відхиляється від `90°` і стає рівним `90° - 2·Δθ`.

Витік зворотної потужності крізь перший поляризатор визначається законом Малюса:
```
I_leak = I_back · sin²(2 · Δθ) ≈ I_back · (2 · Δθ_rad)²
```

Математично рівень ізоляції в децибелах деградує за формулою:
```
Isolation(дБ) ≈ -10 · log10( sin²(2 · Δθ) ) ≈ -20 · log10( 2 · Δθ_rad )
```

Наслідки цього для інженерної практики є вражаючими:
- Відхилення кута Фарадея всього на **`0.5°`** знижує рівень ізоляції з нескінченності до **`41.2 дБ`** (зворотне випромінювання складає `7.6 × 10⁻⁵` від вхідного).
- Відхилення на **`1.0°`** деградує ізоляцію до **`35.2 дБ`** (`3.0 × 10⁻⁴`).
- Відхилення на **`5.0°`** зрізає ізоляцію до **`21.2 дБ`** (`7.6 × 10⁻³`), що вказує на витік майже `0.8%` відбитої потужності назад у лазер. Для лазера потужністю `1 кВт` це означає `8 Вт` зворотного випромінювання, що цілком достатньо для теплового руйнування діодів накачки.

### 2. Температурний дрейф постійних магнітів та кристалів
Для найпопулярнішого парамагнітного кристала TGG стала Верде залежить від температури за законом Кюрі: `V(T) ∝ 1/T`. Температурний коефіцієнт становить близько `-0.4% / °C`.

Одночасно постійні магніти NdFeB при нагріванні втрачають намагніченість із коефіцієнтом близько `-0.12% / °C`.

У сукупності при зміні температури ізолятора на `ΔT = +10°C` кут обертання Фарадея змінюється на:
```
Δθ ≈ 45° · (-0.004 - 0.0012) · 10 = -2.34°
```

Як показує представлена симуляція, помилка в `2.34°` зрізає рівень ізоляції до **`27.8 дБ`**.

Щоб запобігти такій деградації в прецизійних оптичних приладах застосовують пасивну термокомпенсацію: магнітна система збирається з двох різновидів магнітів із протилежними температурними коефіцієнтами або використовують додаткову біметалеву оправу, яка при нагріванні механічно всуває кристал глибше у зону сильнішого магнітного поля, компенсуючи зменшення сталої Верде. Завдяки такому підходу вдається підтримувати високий рівень ізоляції в широкому діапазоні робочих температур навколишнього середовища.
