# ⚙️ Програмне моделювання поляризаційного тракту та закону Малюса

Обчислювальний аналіз оптичних систем, що містять поляризаційні фільтри, двозаломлюючі кристали та фазові пластинки, вимагає точного математичного моделювання зміни вектора поляризації світлової хвилі. Простеження хвильового процесу крізь складний каскад із десятків елементів «вручну» за допомогою тригонометричних рівнянь є громіздким та вразливим до помилок. Спроба обчислити підсумкову інтенсивність світла після проходження серії похилих поляризаторів чи фазових пластинок без матричного апарату вимагає розв'язання нескінченних систем фазових кутів.

Архітектура обчислювального движка мовами C та C++ описує поляризаційний тракт як послідовність комплексних операторів Джонса, що діють на двовимірний вектор стану світлової хвилі.

### 1. Постановка задачі та математична модель

Розглядається оптична система, яка складається з послідовності `N` оптичних елементів (поляризаторів, фазових пластинок `λ/4` та `λ/2`, оптичних обертачів). На вхід системи подається монохроматичний світловий промінь із відомим початковим станом поляризації, який описується двовимірним комплексним вектором Джонса:

```
V = [ E_x ] = [ E₀ₓ · e^(i·φₓ) ]
    [ E_y ]   [ E₀ᵣ · e^(i·φᵣ) ]
```

Кожен оптичний елемент системи описується комплексною квадратною матрицею Джонса розміром `2×2`:

```
M = [ m₀₀  m₀₁ ]
    [ m₁₀  m₁₁ ]
```

Проходження світла крізь один оптичний елемент визначається операцією множення матриці на вектор:

```
V_out = M · V_in
```

Для каскаду з `N` послідовних елементів підсумковий вектор на виході обчислюється шляхом послідовного застосування матриць у зворотному порядку їх розміщення вздовж оптичного променя:

```
V_out = M_N · ... · M₂ · M₁ · V_in
```

Підсумкова інтенсивність світла `I`, яку реєструє фотоприймач, пропорційна сумі квадратів модулів компонент напруженості електричного поля:

```
I = |E_x|² + |E_y|² = (Re(E_x)² + Im(E_x)²) + (Re(E_y)² + Im(E_y)²)
```

Завдяки цьому матричному підходу обчислення інтенсивності світла на виході з оптичного тракту зводиться до швидких матрично-векторних операцій, які ідеально підходять для програмної реалізації у високоефективному коді.

### 2. Реалізація симулятора мовами C та C++

Нижче наведено повні ідіоматичні реалізації обчислювального модулю мовами C (стандарт C99/C11) та C++ (стандарт C++20). Модуль реалізує генерацію векторів Джонса, побудову матриць для поляризаторів та фазових пластинок під довільним кутом, множення матриць на вектор і розрахунок закону Малюса.

В обидвох реалізаціях зберігається повна строгість математичних моделей: комплексна арифметика використовує двоїстий опис дійсних та уявних компонент, а розрахунок підсумкових інтенсивностей спирається на квадрат евклідової норми у комплексному просторі.

:::tabs
```c
#include <stdio.h>
#include <math.h>
#include <stdbool.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

/* Комплексне число та базові операції */
typedef struct {
    double real;
    double imag;
} Complex;

static inline Complex complex_create(double r, double i) {
    Complex c = {r, i};
    return c;
}

static inline Complex complex_add(Complex a, Complex b) {
    return complex_create(a.real + b.real, a.imag + b.imag);
}

static inline Complex complex_sub(Complex a, Complex b) {
    return complex_create(a.real - b.real, a.imag - b.imag);
}

static inline Complex complex_mul(Complex a, Complex b) {
    return complex_create(a.real * b.real - a.imag * b.imag,
                          a.real * b.imag + a.imag * b.real);
}

static inline double complex_abs_sq(Complex c) {
    return c.real * c.real + c.imag * c.imag;
}

/* Вектор Джонса (2x1) */
typedef struct {
    Complex ex;
    Complex ey;
} JonesVector;

/* Матриця Джонса (2x2) */
typedef struct {
    Complex m00, m01;
    Complex m10, m11;
} JonesMatrix;

/* Створення лінійно поляризованого вектора під кутом theta (рад) */
JonesVector jones_vector_linear(double amplitude, double theta_rad) {
    JonesVector v;
    v.ex = complex_create(amplitude * cos(theta_rad), 0.0);
    v.ey = complex_create(amplitude * sin(theta_rad), 0.0);
    return v;
}

/* Створення кругово поляризованого вектора (право- або лівообертального) */
JonesVector jones_vector_circular(double amplitude, bool right_handed) {
    JonesVector v;
    double norm_amp = amplitude / sqrt(2.0);
    v.ex = complex_create(norm_amp, 0.0);
    /* Right-handed: phase shift +pi/2 (i), Left-handed: -pi/2 (-i) */
    v.ey = complex_create(0.0, right_handed ? norm_amp : -norm_amp);
    return v;
}

/* Обчислення інтенсивності світла */
double jones_intensity(JonesVector v) {
    return complex_abs_sq(v.ex) + complex_abs_sq(v.ey);
}

/* Множення матриці Джонса 2x2 на вектор Джонса 2x1 */
JonesVector jones_apply(JonesMatrix M, JonesVector v) {
    JonesVector res;
    res.ex = complex_add(complex_mul(M.m00, v.ex), complex_mul(M.m01, v.ey));
    res.ey = complex_add(complex_mul(M.m10, v.ex), complex_mul(M.m11, v.ey));
    return res;
}

/* Матриця лінійного поляризатора під кутом theta (рад) */
JonesMatrix jones_polarizer(double theta_rad) {
    double c = cos(theta_rad);
    double s = sin(theta_rad);
    JonesMatrix M;
    M.m00 = complex_create(c * c, 0.0);
    M.m01 = complex_create(c * s, 0.0);
    M.m10 = complex_create(c * s, 0.0);
    M.m11 = complex_create(s * s, 0.0);
    return M;
}

/* Матриця фазового затримувача (пластинки) з фазою phi та орієнтацією theta */
JonesMatrix jones_retarder(double theta_rad, double phi_rad) {
    double c = cos(theta_rad);
    double s = sin(theta_rad);
    Complex e_neg = complex_create(cos(-phi_rad / 2.0), sin(-phi_rad / 2.0));
    Complex e_pos = complex_create(cos(phi_rad / 2.0), sin(phi_rad / 2.0));

    Complex c2 = complex_create(c * c, 0.0);
    Complex s2 = complex_create(s * s, 0.0);
    Complex cs = complex_create(c * s, 0.0);

    JonesMatrix M;
    M.m00 = complex_add(complex_mul(c2, e_neg), complex_mul(s2, e_pos));
    M.m01 = complex_mul(cs, complex_sub(e_neg, e_pos));
    M.m10 = M.m01;
    M.m11 = complex_add(complex_mul(s2, e_neg), complex_mul(c2, e_pos));
    return M;
}

int main(void) {
    printf("=== Симуляція оптичного тракту (C99) ===\n");
    
    /* 1. Початкове світло: лінійно поляризоване під 0 градусів (горизонтальне) */
    JonesVector in_wave = jones_vector_linear(1.0, 0.0);
    double i0 = jones_intensity(in_wave);
    printf("Початкова інтенсивність I0 = %.4f\n", i0);

    /* 2. Проходження крізь чвертьхвильову пластинку (λ/4) під кутом 45 град */
    JonesMatrix qwp = jones_retarder(45.0 * M_PI / 180.0, M_PI / 2.0);
    JonesVector after_qwp = jones_apply(qwp, in_wave);
    printf("Інтенсивність після λ/4 пластинки = %.4f\n", jones_intensity(after_qwp));

    /* 3. Проходження крізь поворотний аналізатор під кутами від 0 до 180 град */
    printf("\nПеревірка закону Малюса після поляризаційного тракту:\n");
    printf("Кут (град) | Інтенсивність I | Теорія I_exp\n");
    printf("-------------------------------------------\n");
    
    for (int deg = 0; deg <= 180; deg += 30) {
        double rad = deg * M_PI / 180.0;
        JonesMatrix analyzer = jones_polarizer(rad);
        JonesVector out_wave = jones_apply(analyzer, after_qwp);
        double i_out = jones_intensity(out_wave);
        printf("  %3d°     |     %.4f     |    0.5000\n", deg, i_out);
    }

    return 0;
}
```
```cpp
#include <iostream>
#include <complex>
#include <cmath>
#include <numbers>
#include <array>
#include <iomanip>

using Complex = std::complex<double>;

/* Вектор Джонса для опису стану поляризації */
struct JonesVector {
    Complex ex{0.0, 0.0};
    Complex ey{0.0, 0.0};

    [[nodiscard]] double intensity() const noexcept {
        return std::norm(ex) + std::norm(ey);
    }

    static JonesVector linear(double amplitude, double theta_rad) noexcept {
        return JonesVector{
            .ex = Complex{amplitude * std::cos(theta_rad), 0.0},
            .ey = Complex{amplitude * std::sin(theta_rad), 0.0}
        };
    }

    static JonesVector circular(double amplitude, bool right_handed) noexcept {
        const double norm_amp = amplitude / std::numbers::sqrt2;
        return JonesVector{
            .ex = Complex{norm_amp, 0.0},
            .ey = Complex{0.0, right_handed ? norm_amp : -norm_amp}
        };
    }
};

/* Матриця Джонса 2x2 для оптичного елемента */
struct JonesMatrix {
    std::array<std::array<Complex, 2>, 2> m{{{0, 0}, {0, 0}}};

    [[nodiscard]] JonesVector operator*(const JonesVector& v) const noexcept {
        return JonesVector{
            .ex = m[0][0] * v.ex + m[0][1] * v.ey,
            .ey = m[1][0] * v.ex + m[1][1] * v.ey
        };
    }

    [[nodiscard]] JonesMatrix operator*(const JonesMatrix& other) const noexcept {
        JonesMatrix result;
        for (size_t i = 0; i < 2; ++i) {
            for (size_t j = 0; j < 2; ++j) {
                result.m[i][j] = m[i][0] * other.m[0][j] + m[i][1] * other.m[1][j];
            }
        }
        return result;
    }
};

/* Фабричні функції для оптичних елементів */
[[nodiscard]] JonesMatrix make_polarizer(double theta_rad) noexcept {
    const double c = std::cos(theta_rad);
    const double s = std::sin(theta_rad);
    return JonesMatrix{{
        std::array<Complex, 2>{ c * c, c * s },
        std::array<Complex, 2>{ c * s, s * s }
    }};
}

[[nodiscard]] JonesMatrix make_retarder(double theta_rad, double phi_rad) noexcept {
    const double c = std::cos(theta_rad);
    const double s = std::sin(theta_rad);
    const Complex e_neg = std::polar(1.0, -phi_rad / 2.0);
    const Complex e_pos = std::polar(1.0, phi_rad / 2.0);

    const Complex m00 = c * c * e_neg + s * s * e_pos;
    const Complex m01 = c * s * (e_neg - e_pos);
    const Complex m10 = m01;
    const Complex m11 = s * s * e_neg + c * c * e_pos;

    return JonesMatrix{{
        std::array<Complex, 2>{ m00, m01 },
        std::array<Complex, 2>{ m10, m11 }
    }};
}

int main() {
    std::cout << "=== Симуляція оптичного тракту (C++20) ===\n";
    std::cout << std::fixed << std::setprecision(4);

    // 1. Початкове горизонтально поляризоване світло
    const auto in_wave = JonesVector::linear(1.0, 0.0);
    std::cout << "Початкова інтенсивність I0 = " << in_wave.intensity() << "\n";

    // 2. Чвертьхвильова пластинка (λ/4) під кутом 45 градусів
    const auto qwp = make_retarder(45.0 * std::numbers::pi / 180.0, std::numbers::pi / 2.0);
    const auto after_qwp = qwp * in_wave;
    std::cout << "Інтенсивність після λ/4 пластинки = " << after_qwp.intensity() << "\n\n";

    // 3. Аналіз інтенсивності після поворотного аналізатора (Закон Малюса)
    std::cout << "Кут (град) | Інтенсивність I | Теорія I_exp\n";
    std::cout << "-------------------------------------------\n";

    for (int deg = 0; deg <= 180; deg += 30) {
        const double rad = deg * std::numbers::pi / 180.0;
        const auto analyzer = make_polarizer(rad);
        const auto out_wave = analyzer * after_qwp;
        std::cout << "  " << std::setw(3) << deg << "°     |     " 
                  << out_wave.intensity() << "     |    0.5000\n";
    }

    return 0;
}
```
:::

### 3. Детальний аналіз алгоритму та обчислювальні особливості

Моделювання поляризаційного тракту за допомогою матричного числення Джонса висуває декілька важливих вимог до чисельної точності, обробки кутів та загальної архітектури коду.

#### 3.1. Комплексна арифметика та нормалізація інтенсивності

Вектор Джонса зберігає не лише відносні амплітуди компонент `E_x` та `E_y`, а й їхні часові та просторові фази. При проходженні крізь ідеальний поляризатор або фазову пластинку енергія світлової хвилі повинна зберігатися або зменшуватися відповідно до фундаментального закону збереження енергії.

Для обчислення фізичної інтенсивності світла використовується квадрат норми комплексної амплітуди:

```
I = |E_x|² + |E_y|² = Re(E_x)² + Im(E_x)² + Re(E_y)² + Im(E_y)²
```

У реалізації мовою C++20 стандартна функція `std::norm(z)` із розділу `<complex>` повертає саме квадрат модуля комплексно-комплексного числа (`|z|²`), що є оптимізованою операцією, оскільки вона дозволяє уникнути обчислення зайвого квадратного кореня (на відміну від `std::abs(z)`). У C99-версії коду для цієї мети створено власну вбудовану функцію `complex_abs_sq`, яка гарантує максимальну продуктивність.

#### 3.2. Обробка послідовності оптичних елементів

При каскадуванні кількох оптичних елементів у реальному оптичному приладі (наприклад, у поляризаційному мікроскопі чи еліпсометрі) існує два основних методи розрахунку:

1. **Попослідовне множення матриці на вектор:** на кожному кроці вектор стану `V` послідовно множиться на матрицю чергового оптичного елемента `M_i`. Кількість скалярних множень для `N` елементів становить `O(N)`. Це найпростіший метод при симуляції одного променя.
2. **Перемноження матриць самих елементів:** спочатку обчислюється єдина еквівалентна матриця всієї оптичної системи `M_sys = M_N · ... · M_1`, яка потім один раз застосовується до вхідного вектора `V`. Цей підхід є суттєво ефективнішим, коли необхідно прорахувати проходження мільйонів світлових променів (наприклад, при трасуванні променів у 3D-графіці чи оптичному рендерингу) крізь один і той самий фіксований оптичний тракт.

Реалізація мовою C++20 підтримує перевантажений оператор `operator*` для множення двох матриць Джонса `JonesMatrix * JonesMatrix`, що дозволяє легко обчислювати еквівалентні матриці складних комбінованих оптичних систем.

#### 3.3. Граничні випадки, фазові узгодження та пастки реалізації

При розробці програмного забезпечення для обчислення поляризації слід стерегтися кількох класичних помилок:

- **Узгодження осей координат:** усі кути повороту оптичних елементів `θ` мусять відраховуватися в єдиній правій системі координат (зазвичай від горизонтальної осі `x` проти годинникової стрілки, якщо спостерігач дивиться назустріч променю). Помилка в знаку кута повертає правильну кругову поляризацію на ліву.
- **Дзеркальне відображення при відбитті:** при відбитті світла від дзеркальних поверхонь напрямок поширення променя `z` змінюється на протилежний, що змінює орієнтацію правої системи координат. Матриці Джонса для відбиття повинні включати відповідну зміну знаку для паралельної або перпендикулярної компонент.
- **Обмеження матричного апарату Джонса:** векторний апарат Джонса застосовний **тільки для повністю поляризованого когерентного світла**. Якщо оптичний тракт містить частково поляризоване або природне (неполяризоване) світло, необхідно переходити від векторів Джонса до векторів Стокса та матриць Мюллера `4×4` (детальніше див. [🧮 Математичний апарат матричного числення Джонса та векторів Стокса](root:ph-waves/polarization-matrix-calculus)).
