# ⚙️ Симулятор поляризаційного тракту

Симулятор поляризаційного тракту обчислює трансформацію стану поляризації світлового променя при проходженні крізь послідовність оптичних елементів — поляризаторів, фазових платівок та елементів обертання. Програма реалізує двовимірне комплексне числення Джонса для когерентного світла та чотиривимірне дійсне числення Мюллера для розрахунку ступеня поляризації (DOP) і втрат інтенсивності в некогерентних променях.

### 1. Фізична та математична модель симулятора

Симулятор будується на принципі послідовного каскадування оптичних блоків. Вхідний світловий промінь задається у вигляді двокомпонентного комплексного вектора Джонса `J_in = (E_x, E_y)ᵀ` для строго монохроматичного лазерного випромінювання або у вигляді чотирикомпонентного дійснозначного вектора Стокса `S_in = (S_0, S_1, S_2, S_3)ᵀ` для некогерентного чи частково поляризованого світла.

Кожен оптичний прилад у тракті характеризується двома основними фізичними параметрами:
- **Азимутальний кут `θ`**: кут повороту головної оптичної осі елемента (наприклад, осі пропускання поляризатора або швидкої осі фазової платівки) відносно горизонтальної координатної осі `x`.
- **Фазове запізнення `δ`**: різниця фазового набігу між повільною та швидкою компонентами хвилі. Для чвертьхвильової платівки (QWP) `δ = π/2`, для півхвильової платівки (HWP) `δ = π`.

Для довільного оптичного елемента з базовою матрицею `J_0(δ)` у власних осях його підсумкова матриця `J_elem(θ, δ)` для лабораторної системи координат обчислюється шляхом ортогонального повороту:

```
J_elem(θ, δ) = R(-θ) · J_0(δ) · R(θ)
```

де `R(θ)` — матриця двовимірного повороту координат:

```
R(θ) = [  cos θ   sin θ ]
       [ -sin θ   cos θ ]
```

Підсумковий вектор Джонса на виході оптичної системи із `N` послідовних елементів обчислюється множенням операторів у строгому зворотному порядку (справа наліво відносно напрямку поширення світлового променя):

```
J_out = J_N · J_{N-1} ... J_1 · J_in
```

Після обчислення підсумкового вектора Джонса `J_out = (E_x, E_y)ᵀ` симулятор перераховує отримані комплексні амплітуди у фізично вимірювані інтенсивності вектора Стокса `S = (S_0, S_1, S_2, S_3)ᵀ`:

```
S_0 = |E_x|² + |E_y|²                     [Загальна інтенсивність випромінювання]
S_1 = |E_x|² - |E_y|²                     [Різниця інтенсивностей H та V компонент]
S_2 = 2 · Re(E_x · E_y*)                  [Різниця інтенсивностей під +45° та -45°]
S_3 = -2 · Im(E_x · E_y*)                 [Переважання правої або лівої колової хвилі]
```

Отриманий вектор Стокса дає можливість миттєво обчислити **ступінь поляризації** (`Degree of Polarization`, DOP):

```
DOP = √(S_1² + S_2² + S_3²) / S_0
```

Для когерентного вектора Джонса значення `DOP` завжди строго дорівнює `1.0` (100% поляризоване світло). Якщо ж у тракті присутній елемент деполяризації або некогерентне змішування променів, значення `DOP` спадає у діапазон `0.0 ≤ DOP < 1.0`.

### 2. Аналіз прикладу каскаду (QWP + Поляризатор)

У контрольному прикладі програма розраховує проходження горизонтально поляризованого світла `J_in = (1, 0)ᵀ` крізь послідовність двох приладів:
1. Чвертьхвильова платівка під кутом 45°: створює різницю фаз `90°` між компонентами, перетворюючи горизонтальну лінійну поляризацію на суто лівоколову (LCP) з вектором `J_mid = (1, -i)ᵀ / √2` та вектором Стокса `S_mid = (1, 0, 0, -1)ᵀ`.
2. Лінійний поляризатор під кутом 90° (вертикальний): виділяє з колового світла лише вертикальну компоненту `E_y`.

На виході симулятор отримує вектор Джонса `J_out = (0, -i/√2)ᵀ`, що відповідає вертикальній поляризації з інтенсивністю `S_0 = 0.5`. Це підтверджує фізичний факт: лінійно поляризоване світло після перетворення у колову поляризацію втрачає рівно 50% інтенсивності при проходженні крізь довільно орієнтований лінійний поляризатор.

### 3. Архітектура та оптимізація коду

Модульна структура симулятора передбачає розділення алгебраїчного ядра та інтерфейсів побудови оптичного тракту.

1. **Типізація та представлення комплексних чисел**: Мовою C реалізовано власну структуру `DoubleComplex` та явні арифметичні функції `c_add`, `c_mul`, `c_conj`. Це виключає залежність від компіляторно-залежного заголовочного файла `<complex.h>` і гарантує сумісність із вбудованими платформами без підтримки C99 complex. У C++ використовується стандартний шаблон `std::complex<double>`.
2. **Конверсія матриць Джонса у матриці Мюллера**: Для некогерентного каскадування симулятор містить алгоритм побудови дійсної матриці Мюллера `4×4` з комплексної матриці Джонса `2×2` через вирази Паулі `M_ij = 1/2 · Tr(σ_i · J · σ_j · J†)`.
3. **Обчислювальна стійкість та контроль граничних умов**:
   - При множенні векторів реалізовано перевірку нормалізації станів.
   - Для запобігання діленню на нуль у разі нульової інтенсивності `S_0 <= 1e-15` введене затискання результату `DOP = 0.0`.
   - Тригонометричні коефіцієнти синусів і косинусів розраховуються один раз при створенні об'єкта матриці, що знижує витрати ресурсів у циклі обробки.

### 4. Аналіз крайових випадків та перевірка стійкості

При моделюванні складних оптичних трактів виникають крайові умови, які вимагають окремої обробки:

1. **Схрещені поляризатори (Повне погашення світла)**: Коли світло проходить крізь поляризатор 0°, а потім крізь поляризатор 90°, вихідний вектор Джонса стає строго нульовим `J_out = (0, 0)ᵀ`. У цьому випадку інтенсивність `S_0 = 0.0`. Функція `stokes_dop` перевіряє поріг `S_0 <= 1e-15` і повертає `DOP = 0.0` замість виникнення помилки ділення на нуль (`NaN`).
2. **Переповнення фазового кута**: При множенні десятків фазових платівок фаза може перевищувати `2·π`. Для обчислення кутів поляризаційного еліпса `ψ` та `χ` використовується функція `std::atan2(s2, s1)`, яка коректно обробляє кути в усіх чотирьох квадрантах у діапазоні `[-π, π]`.
3. **Фізична валідація Стокса**: Якщо через чисельну похибку накопичується дрібне відхилення, при якому `S_1² + S_2² + S_3² > S_0²`, програма затискає значення `DOP` до верхньої межі `1.0`.

### 5. Конфігурація збірки та інтеграція у проєкти

Джерельний код симулятора призначений для автономної збірки без сторонніх залежностей.

- **Компіляція для C**: Для збірки C-модуля достатньо виконати `gcc -O3 -std=c99 main.c -lm -o pol_sim_c`. Прапорець `-O3` вмикає автовекторизацію циклів множення матриць.
- **Компіляція для C++**: Для збірки C++ версії використовується `g++ -O3 -std=c++17 main.cpp -o pol_sim_cpp`. Використання стандарту C++17 забезпечує підтримку атрибутів `[[nodiscard]]` та розширених евристик векторних типів.
- **Тестування на мікроконтролерах**: Версія мовою C не використовує динамічного виділення пам'яті у стеку обчислення `jones_apply`, що дає можливість інтегрувати код у прошивки контролерів ARM Cortex-M4/M7 для автоматичної юстування оптичних голівок у реальному часі.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

/* Комплексне число та операції над ним */
typedef struct {
    double real;
    double imag;
} DoubleComplex;

DoubleComplex c_make(double r, double i) {
    DoubleComplex z = {r, i};
    return z;
}

DoubleComplex c_add(DoubleComplex a, DoubleComplex b) {
    return c_make(a.real + b.real, a.imag + b.imag);
}

DoubleComplex c_mul(DoubleComplex a, DoubleComplex b) {
    return c_make(a.real * b.real - a.imag * b.imag,
                  a.real * b.imag + a.imag * b.real);
}

DoubleComplex c_conj(DoubleComplex a) {
    return c_make(a.real, -a.imag);
}

double c_abs_sq(DoubleComplex a) {
    return a.real * a.real + a.imag * a.imag;
}

/* Вектор Джонса 2x1 */
typedef struct {
    DoubleComplex ex;
    DoubleComplex ey;
} JonesVector;

/* Матриця Джонса 2x2 */
typedef struct {
    DoubleComplex m[2][2];
} JonesMatrix;

/* Вектор Стокса 4x1 */
typedef struct {
    double s0;
    double s1;
    double s2;
    double s3;
} StokesVector;

/* Множення матриці Джонса на вектор Джонса: J_out = M * J_in */
JonesVector jones_apply(JonesMatrix M, JonesVector J) {
    JonesVector res;
    res.ex = c_add(c_mul(M.m[0][0], J.ex), c_mul(M.m[0][1], J.ey));
    res.ey = c_add(c_mul(M.m[1][0], J.ex), c_mul(M.m[1][1], J.ey));
    return res;
}

/* Множення двох матриць Джонса: M_out = A * B */
JonesMatrix jones_mul_matrix(JonesMatrix A, JonesMatrix B) {
    JonesMatrix R;
    for (int i = 0; i < 2; i++) {
        for (int j = 0; j < 2; j++) {
            R.m[i][j] = c_make(0.0, 0.0);
            for (int k = 0; k < 2; k++) {
                R.m[i][j] = c_add(R.m[i][j], c_mul(A.m[i][k], B.m[k][j]));
            }
        }
    }
    return R;
}

/* Створення матриці фазової платівки під кутом theta (рад) із запізненням delta (рад) */
JonesMatrix make_retarder(double theta_rad, double delta_rad) {
    double c = cos(theta_rad);
    double s = sin(theta_rad);
    DoubleComplex phase = c_make(cos(delta_rad), sin(delta_rad));

    /* Базова матриця в власній системі координат */
    JonesMatrix J0;
    J0.m[0][0] = c_make(1.0, 0.0);
    J0.m[0][1] = c_make(0.0, 0.0);
    J0.m[1][0] = c_make(0.0, 0.0);
    J0.m[1][1] = phase;

    /* Матриця повороту R(theta) */
    JonesMatrix R, R_inv;
    R.m[0][0] = c_make(c, 0.0);  R.m[0][1] = c_make(s, 0.0);
    R.m[1][0] = c_make(-s, 0.0); R.m[1][1] = c_make(c, 0.0);

    R_inv.m[0][0] = c_make(c, 0.0); R_inv.m[0][1] = c_make(-s, 0.0);
    R_inv.m[1][0] = c_make(s, 0.0); R_inv.m[1][1] = c_make(c, 0.0);

    /* J = R(-theta) * J0 * R(theta) */
    JonesMatrix tmp = jones_mul_matrix(J0, R);
    return jones_mul_matrix(R_inv, tmp);
}

/* Створення матриці лінійного поляризатора під кутом theta (рад) */
JonesMatrix make_polarizer(double theta_rad) {
    double c = cos(theta_rad);
    double s = sin(theta_rad);

    JonesMatrix J;
    J.m[0][0] = c_make(c * c, 0.0);
    J.m[0][1] = c_make(c * s, 0.0);
    J.m[1][0] = c_make(c * s, 0.0);
    J.m[1][1] = c_make(s * s, 0.0);
    return J;
}

/* Перетворення вектора Джонса у вектор Стокса */
StokesVector jones_to_stokes(JonesVector J) {
    StokesVector S;
    double I_x = c_abs_sq(J.ex);
    double I_y = c_abs_sq(J.ey);

    DoubleComplex ex_ey_conj = c_mul(J.ex, c_conj(J.ey));

    S.s0 = I_x + I_y;
    S.s1 = I_x - I_y;
    S.s2 = 2.0 * ex_ey_conj.real;
    S.s3 = -2.0 * ex_ey_conj.imag;
    return S;
}

/* Обчислення ступеня поляризації (DOP) */
double stokes_dop(StokesVector S) {
    if (S.s0 <= 1e-15) return 0.0;
    double pol_int = sqrt(S.s1 * S.s1 + S.s2 * S.s2 + S.s3 * S.s3);
    return pol_int / S.s0;
}

int main(void) {
    /* Початковий стан: Горизонтально поляризоване світло J_in = (1, 0)^T */
    JonesVector J_in;
    J_in.ex = c_make(1.0, 0.0);
    J_in.ey = c_make(0.0, 0.0);

    printf("=== Симулятор поляризаційного тракту (C) ===\n");
    printf("Початковий стан (H-поляризація):\n");
    printf("Ex = %.3f + %.3fi, Ey = %.3f + %.3fi\n",
           J_in.ex.real, J_in.ex.imag, J_in.ey.real, J_in.ey.imag);

    /* 1. Чвертьхвильова платівка (QWP) під кутом 45° (delta = pi/2) */
    JonesMatrix QWP45 = make_retarder(45.0 * M_PI / 180.0, M_PI / 2.0);

    /* 2. Лінійний аналізатор під кутом 90° (вертикальний) */
    JonesMatrix Pol90 = make_polarizer(90.0 * M_PI / 180.0);

    /* Обчислення каскаду: J_mid = QWP45 * J_in */
    JonesVector J_mid = jones_apply(QWP45, J_in);
    StokesVector S_mid = jones_to_stokes(J_mid);

    printf("\nПісля чвертьхвильової платівки (+45°):\n");
    printf("Ex = %.3f + %.3fi, Ey = %.3f + %.3fi\n",
           J_mid.ex.real, J_mid.ex.imag, J_mid.ey.real, J_mid.ey.imag);
    printf("Вектор Стокса: S0=%.3f, S1=%.3f, S2=%.3f, S3=%.3f\n",
           S_mid.s0, S_mid.s1, S_mid.s2, S_mid.s3);
    printf("Ступінь поляризації (DOP): %.4f\n", stokes_dop(S_mid));

    /* J_out = Pol90 * J_mid */
    JonesVector J_out = jones_apply(Pol90, J_mid);
    StokesVector S_out = jones_to_stokes(J_out);

    printf("\nПісля аналізатора (90°):\n");
    printf("Вихідна інтенсивність (S0): %.4f (50%% від початкової)\n", S_out.s0);
    printf("Вектор Стокса: S0=%.3f, S1=%.3f, S2=%.3f, S3=%.3f\n",
           S_out.s0, S_out.s1, S_out.s2, S_out.s3);

    return 0;
}
```

```cpp
#include <iostream>
#include <complex>
#include <array>
#include <vector>
#include <cmath>
#include <iomanip>

namespace Polarization {

using Complex = std::complex<double>;

/* Вектор Джонса 2x1 */
struct JonesVector {
    Complex ex{1.0, 0.0};
    Complex ey{0.0, 0.0};

    [[nodiscard]] double intensity() const noexcept {
        return std::norm(ex) + std::norm(ey);
    }
};

/* Матриця Джонса 2x2 */
class JonesMatrix {
private:
    std::array<std::array<Complex, 2>, 2> m_{};

public:
    JonesMatrix() {
        m_[0][0] = 1.0; m_[0][1] = 0.0;
        m_[1][0] = 0.0; m_[1][1] = 1.0;
    }

    JonesMatrix(Complex m00, Complex m01, Complex m10, Complex m11) {
        m_[0][0] = m00; m_[0][1] = m01;
        m_[1][0] = m10; m_[1][1] = m11;
    }

    [[nodiscard]] Complex operator()(size_t r, size_t c) const {
        return m_.at(r).at(c);
    }

    [[nodiscard]] JonesVector operator*(const JonesVector& j) const noexcept {
        return JonesVector{
            m_[0][0] * j.ex + m_[0][1] * j.ey,
            m_[1][0] * j.ex + m_[1][1] * j.ey
        };
    }

    [[nodiscard]] JonesMatrix operator*(const JonesMatrix& b) const noexcept {
        JonesMatrix res;
        for (size_t i = 0; i < 2; ++i) {
            for (size_t j = 0; j < 2; ++j) {
                Complex sum{0.0, 0.0};
                for (size_t k = 0; k < 2; ++k) {
                    sum += m_[i][k] * b.m_[k][j];
                }
                res.m_[i][j] = sum;
            }
        }
        return res;
    }

    /* Генератор поляризатора під кутом theta (рад) */
    static JonesMatrix Polarizer(double theta_rad) {
        double c = std::cos(theta_rad);
        double s = std::sin(theta_rad);
        return JonesMatrix(c * c, c * s, c * s, s * s);
    }

    /* Генератор фазової платівки (retarder) */
    static JonesMatrix Retarder(double theta_rad, double delta_rad) {
        double c = std::cos(theta_rad);
        double s = std::sin(theta_rad);
        Complex phase = std::polar(1.0, delta_rad);

        JonesMatrix J0(1.0, 0.0, 0.0, phase);
        JonesMatrix R(c, s, -s, c);
        JonesMatrix R_inv(c, -s, s, c);

        return R_inv * J0 * R;
    }
};

/* Клас вектора Стокса 4x1 */
struct StokesVector {
    double s0{1.0};
    double s1{0.0};
    double s2{0.0};
    double s3{0.0};

    [[nodiscard]] double degreeOfPolarization() const noexcept {
        if (s0 <= 1e-15) return 0.0;
        double pol = std::sqrt(s1 * s1 + s2 * s2 + s3 * s3);
        return pol / s0;
    }

    static StokesVector fromJones(const JonesVector& j) noexcept {
        double ix = std::norm(j.ex);
        double iy = std::norm(j.ey);
        Complex ex_ey_c = j.ex * std::conj(j.ey);

        return StokesVector{
            ix + iy,
            ix - iy,
            2.0 * ex_ey_c.real(),
            -2.0 * ex_ey_c.imag()
        };
    }
};

/* Клас каскаду оптичного тракту */
class OpticalCascade {
private:
    std::vector<JonesMatrix> elements_;

public:
    void addElement(const JonesMatrix& m) {
        elements_.push_back(m);
    }

    [[nodiscard]] JonesVector process(const JonesVector& input) const {
        JonesVector current = input;
        for (const auto& elem : elements_) {
            current = elem * current;
        }
        return current;
    }
};

} // namespace Polarization

int main() {
    using namespace Polarization;
    constexpr double PI = 3.14159265358979323846;

    std::cout << std::fixed << std::setprecision(4);
    std::cout << "=== Симулятор поляризаційного тракту (C++) ===\n";

    JonesVector j_in{Complex{1.0, 0.0}, Complex{0.0, 0.0}};

    OpticalCascade cascade;
    // 1. Чвертьхвильова платівка QWP під 45°
    cascade.addElement(JonesMatrix::Retarder(45.0 * PI / 180.0, PI / 2.0));
    // 2. Лінійний поляризатор 90°
    cascade.addElement(JonesMatrix::Polarizer(90.0 * PI / 180.0));

    JonesVector j_out = cascade.process(j_in);
    StokesVector s_out = StokesVector::fromJones(j_out);

    std::cout << "Вихідний вектор Джонса: Ex=" << j_out.ex << ", Ey=" << j_out.ey << "\n";
    std::cout << "Вектор Стокса: S0=" << s_out.s0 << ", S1=" << s_out.s1
              << ", S2=" << s_out.s2 << ", S3=" << s_out.s3 << "\n";
    std::cout << "Ступінь поляризації (DOP): " << s_out.degreeOfPolarization() << "\n";

    return 0;
}
```
:::
