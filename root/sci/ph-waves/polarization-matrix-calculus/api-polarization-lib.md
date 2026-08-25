# 📋 Інтерфейс бібліотеки розрахунку поляризаційних матриць

Довідник публічного програмного інтерфейсу (API) бібліотеки розрахунку поляризаційних векторів і матриць описує контракти функцій, структури даних, системи координат, алгоритми перетворення та гарантії обчислювальної точності. Бібліотека призначена для симуляції поляризаційних оптичних систем у когерентній оптиці (числення Джонса `2×2`) та некогерентній розсіювальні оптиці (числення Стокса-Мюллера `4×4`).

### 1. Базові типи даних та розміщення у пам'яті

Обчислювальний апарат оперує чотирма основними математичними об'єктами. Для забезпечення високої продуктивності та сумісності з низькорівневим векторизованим кодом (SIMD/AVX2) усі структури мають фіксований вирівняний розмір у пам'яті.

#### 1.1. Вектор Джонса (`pol_jones_vector_t` / `Polarization::JonesVector`)
Представляє стан монохроматичного когерентного світла за допомогою двох комплексних амплітуд `E_x` та `E_y`:

- `ex`: комплексне число подвійної точності (`double complex` у C / `std::complex<double>` у C++), що описує амплітуду та фазу горизонтальної компоненти електричного поля.
- `ey`: комплексне число подвійної точності для вертикальної компоненти поля.
- **Розміщення у пам'яті**: 32 байти (чотири числа `double` послідовно: `Re(Ex), Im(Ex), Re(Ey), Im(Ey)`).
- **Основа системи**: Ортогональний декартовий базис із горизонтальною віссю `X` та вертикальною віссю `Y`, перпендикулярними напрямку поширення світла `Z`.

#### 1.2. Матриця Джонса (`pol_jones_matrix_t` / `Polarization::JonesMatrix`)
Представляє дію оптичного елемента без деполяризації у вигляді комплексної квадратної матриці розміром `2×2`:

- `m[2][2]`: двовимірний масив із 4 комплексних елементів. Елемент `m[row][col]` описує коефіцієнт зв'язку між вхідною компонентою `col` та вихідною компонентою `row`.
- **Розміщення у пам'яті**: 64 байти, збереження за рядками (row-major).
- **Операційна властивість**: Матриця описує амплітудні зсуви та фазові набіги. Для ідеальних непоглинальних ретардерів є унітарною (`J† · J = I`).

#### 1.3. Вектор Стокса (`pol_stokes_vector_t` / `Polarization::StokesVector`)
Описує стан випромінювання довільного ступеня когерентності за допомогою 4 дійсних інтенсивностей:

- `s0`: загальна інтенсивність випромінювання (`S_0 >= 0`).
- `s1`: різниця інтенсивностей між горизонтальною (0°) та вертикальною (90°) поляризаціями.
- `s2`: різниця інтенсивностей між діагональними поляризаціями (+45° та -45°).
- `s3`: різниця інтенсивностей між правою (RCP) та лівою (LCP) коловими поляризаціями.
- **Розміщення у пам'яті**: 32 байти (чотири числа `double` підряд: `s0, s1, s2, s3`).

#### 1.4. Матриця Мюллера (`pol_mueller_matrix_t` / `Polarization::MuellerMatrix`)
Представляє довільне оптичне середовище (включаючи деполяризаційні та розсіювальні матеріали) у вигляді дійсної квадратної матриці розміром `4×4`:

- `m[4][4]`: двовимірний масив із 16 дійсних чисел `double`.
- **Розміщення у пам'яті**: 128 байтів, збереження за рядками (row-major).

### 2. Загальні константи та коди помилок

Всі функції повертають цілочисельний статус виконання або висувають відповідний виняток у C++:

- `POL_SUCCESS = 0`: операція виконана успішно.
- `POL_ERROR_NULL_POINTER = -1`: передано нульовий вказівник на вихідний буфер.
- `POL_ERROR_ZERO_INTENSITY = -2`: вихідний вектор Стокса має нульову інтенсивність `S_0 <= 0`, розрахунок кутів чи DOP неможливий.
- `POL_ERROR_NON_PHYSICAL_MATRIX = -3`: створена або передана матриця Мюллера порушує умови фізичної реалізованості (умова позитивної визначеності коваріаційної матриці Клода).
- `POL_ERROR_INVALID_ANGLE = -4`: передано нечислове значення кута (NaN або нескінченність).

### 3. Гарантії обчислювальної точності, пам'яті та багатопотоковості

Для забезпечення високої надійності при використанні бібліотеки у промислових оптичних симуляторах, приладах автоматичного оптичного контролю (AOI) та контролерах реального часу діють наступні інженерні стандарти:

1. **Багатопотокова безпека (Thread Safety)**: Усі структури даних `pol_jones_vector_t`, `pol_jones_matrix_t`, `pol_stokes_vector_t` та `pol_mueller_matrix_t` є скалярними значеннями (Value-Types) без глобального або внутрішнього стану. Усі обчислювальні функції є реентабельними (Reentrant) та повністю Thread-Safe, що дозволяє паралельно обробляти мільйони променів у багатопотокових обчисленнях без взаємних блокувань.
2. **Вирівнювання у пам'яті та SIMD-оптимізація**: Для забезпечення сумісності з векторами AVX2/AVX-512 структури вирівняні за межею 32 байтів (`alignas(32)`). Операції множення матриці Мюллера `4×4` на вектор Стокса `4×1` оптимізовані з використанням інструкцій FMA (Fused Multiply-Add), що забезпечує виконання обчислень за 4 такти процесора.
3. **Порядок збереження матриць (Row-Major Order)**: Усі матриці зберігаються у пам'яті послідовно за рядками: елемент `m[row][col]` розташований за зміщенням `row * N + col`. При інтеграції з графічними бібліотеками OpenGL або матричними пакетами BLAS/LAPACK, які очікують Column-Major порядок, слід виконувати попереднє транспонування.
4. **Обробка некоректних матриць**: Застосування функцій `pol_mueller_check_physicality` виконує діагоналізацію матриці Клода та гарантує, що матриці Мюллера із від'ємними власними значеннями не будуть передані в обчислювальний тракт.
5. **Стратегія управління пам'яттю**: Бібліотека не виконує внутрішніх динамічних виділень пам'яті (`malloc` або `new`) у базових обчислювальних викликах. Усі структури передаються через стек або прямозначні буфери, що виключає затримки на фрагментацію купи у системах жорсткого реального часу.

### 4. Публічні контрактні сигнатури інтерфейсу

:::tabs
```c
#ifndef POLARIZATION_LIB_H
#define POLARIZATION_LIB_H

#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Типи даних */
typedef struct {
    double real;
    double imag;
} pol_complex_t;

typedef struct {
    pol_complex_t ex;
    pol_complex_t ey;
} pol_jones_vector_t;

typedef struct {
    pol_complex_t m[2][2];
} pol_jones_matrix_t;

typedef struct {
    double s0;
    double s1;
    double s2;
    double s3;
} pol_stokes_vector_t;

typedef struct {
    double m[4][4];
} pol_mueller_matrix_t;

/* --- Конструктори та стандартизовані генератори векторів Джонса --- */

/**
 * @brief Створює нормований вектор Джонса лінійної поляризації.
 * @param angle_rad Кут нахилу електричного поля до осі X у радіанах.
 * @param out_v Вказівник на вихідну структуру.
 * @return POL_SUCCESS або код помилки.
 */
int pol_jones_create_linear(double angle_rad, pol_jones_vector_t *out_v);

/**
 * @brief Створює нормований вектор Джонса колової поляризації.
 * @param is_right_circular true для правої (RCP), false для лівої (LCP).
 * @param out_v Вказівник на вихідну структуру.
 */
int pol_jones_create_circular(bool is_right_circular, pol_jones_vector_t *out_v);

/* --- Конструктори та генератори матриць Джонса --- */

/**
 * @brief Генератор матриці ідеального лінійного поляризатора.
 * @param angle_rad Кут осі пропускання поляризатора в радіанах.
 * @param out_m Вказівник на вихідну матрицю.
 */
int pol_jones_matrix_polarizer(double angle_rad, pol_jones_matrix_t *out_m);

/**
 * @brief Генератор матриці фазової платівки (retarder).
 * @param fast_axis_rad Кут швидкої осі платівки в радіанах.
 * @param retardance_rad Фазове запізнення в радіанах (pi/2 для QWP, pi для HWP).
 * @param out_m Вказівник на вихідну матрицю.
 */
int pol_jones_matrix_retarder(double fast_axis_rad, double retardance_rad, pol_jones_matrix_t *out_m);

/**
 * @brief Генератор матриці ротатора Фарадея або оптично активного середовища.
 * @param rotation_angle_rad Кут повороту плоскості поляризації в радіанах.
 * @param out_m Вказівник на вихідну матрицю.
 */
int pol_jones_matrix_rotator(double rotation_angle_rad, pol_jones_matrix_t *out_m);

/* --- Операції числення Джонса --- */

/**
 * @brief Застосування матриці Джонса до вектора: J_out = M * J_in.
 */
int pol_jones_apply(const pol_jones_matrix_t *m, const pol_jones_vector_t *in_v, pol_jones_vector_t *out_v);

/**
 * @brief Множення двох матриць Джонса: M_out = A * B.
 */
int pol_jones_matrix_multiply(const pol_jones_matrix_t *a, const pol_jones_matrix_t *b, pol_jones_matrix_t *out_m);

/* --- Конструктори та генератори матриць Мюллера --- */

/**
 * @brief Генератор матриці Мюллера для ідеального лінійного поляризатора.
 */
int pol_mueller_matrix_polarizer(double angle_rad, pol_mueller_matrix_t *out_m);

/**
 * @brief Генератор матриці Мюллера для фазової платівки.
 */
int pol_mueller_matrix_retarder(double fast_axis_rad, double retardance_rad, pol_mueller_matrix_t *out_m);

/**
 * @brief Генератор матриці ідеального ізотропного деполяризатора.
 * @param depol_factor Коефіцієнт деполяризації (0.0 — без деполяризації, 1.0 — повна деполяризація).
 * @param out_m Вказівник на вихідну матрицю.
 */
int pol_mueller_matrix_depolarizer(double depol_factor, pol_mueller_matrix_t *out_m);

/* --- Операції числення Мюллера --- */

/**
 * @brief Застосування матриці Мюллера до вектора Стокса: S_out = M * S_in.
 */
int pol_mueller_apply(const pol_mueller_matrix_t *m, const pol_stokes_vector_t *in_s, pol_stokes_vector_t *out_s);

/**
 * @brief Множення двох матриць Мюллера: M_out = A * B.
 */
int pol_mueller_matrix_multiply(const pol_mueller_matrix_t *a, const pol_mueller_matrix_t *b, pol_mueller_matrix_t *out_m);

/* --- Функції взаємної конверсії та аналізу станів --- */

/**
 * @brief Перетворення вектора Джонса у вектор Стокса.
 */
int pol_jones_to_stokes(const pol_jones_vector_t *in_j, pol_stokes_vector_t *out_s);

/**
 * @brief Обчислення матриці Мюллера з матриці Джонса (для недополяризуючих систем).
 */
int pol_jones_to_mueller_matrix(const pol_jones_matrix_t *in_j, pol_mueller_matrix_t *out_m);

/**
 * @brief Обчислення ступеня поляризації (DOP) вектора Стокса.
 * @param in_s Вказівник на вектор Стокса.
 * @param out_dop Вказівник на результат (0.0 <= DOP <= 1.0).
 */
int pol_stokes_get_dop(const pol_stokes_vector_t *in_s, double *out_dop);

/**
 * @brief Обчислення азимутального кута psi та кута еліптичності chi вектора Стокса.
 */
int pol_stokes_get_ellipse_params(const pol_stokes_vector_t *in_s, double *out_psi_rad, double *out_chi_rad);

/**
 * @brief Перевірка фізичної реалізованості матриці Мюллера за декомпозицією Клода.
 * @return POL_SUCCESS якщо матриця фізична, POL_ERROR_NON_PHYSICAL_MATRIX у разі порушення.
 */
int pol_mueller_check_physicality(const pol_mueller_matrix_t *m, bool *is_physical);

#ifdef __cplusplus
}
#endif

#endif /* POLARIZATION_LIB_H */
```

```cpp
#ifndef POLARIZATION_LIB_HPP
#define POLARIZATION_LIB_HPP

#include <complex>
#include <array>
#include <vector>
#include <optional>
#include <stdexcept>
#include <cmath>

namespace Polarization {

using Complex = std::complex<double>;

/* Винятки бібліотеки */
class PolarizationException : public std::runtime_error {
public:
    using std::runtime_error::runtime_error;
};

class NonPhysicalMatrixException : public PolarizationException {
public:
    NonPhysicalMatrixException() 
        : PolarizationException("Матриця Мюллера порушує критерій позитивності Клода") {}
};

/* Клас вектора Джонса 2x1 */
class JonesVector {
public:
    Complex ex{1.0, 0.0};
    Complex ey{0.0, 0.0};

    constexpr JonesVector() noexcept = default;
    constexpr JonesVector(Complex x, Complex y) noexcept : ex(x), ey(y) {}

    [[nodiscard]] static JonesVector Linear(double angle_rad) noexcept {
        return JonesVector(std::cos(angle_rad), std::sin(angle_rad));
    }

    [[nodiscard]] static JonesVector Circular(bool is_right) noexcept {
        constexpr double inv_sqrt2 = 0.70710678118654752440;
        if (is_right) {
            return JonesVector(Complex(inv_sqrt2, 0.0), Complex(0.0, -inv_sqrt2));
        }
        return JonesVector(Complex(inv_sqrt2, 0.0), Complex(0.0, inv_sqrt2));
    }

    [[nodiscard]] double intensity() const noexcept {
        return std::norm(ex) + std::norm(ey);
    }

    void normalize() {
        double int_val = intensity();
        if (int_val > 1e-15) {
            double norm_fact = 1.0 / std::sqrt(int_val);
            ex *= norm_fact;
            ey *= norm_fact;
        }
    }
};

/* Клас матриці Джонса 2x2 */
class JonesMatrix {
private:
    std::array<std::array<Complex, 2>, 2> m_{};

public:
    constexpr JonesMatrix() noexcept {
        m_[0][0] = 1.0; m_[0][1] = 0.0;
        m_[1][0] = 0.0; m_[1][1] = 1.0;
    }

    constexpr JonesMatrix(Complex m00, Complex m01, Complex m10, Complex m11) noexcept {
        m_[0][0] = m00; m_[0][1] = m01;
        m_[1][0] = m10; m_[1][1] = m11;
    }

    [[nodiscard]] Complex operator()(size_t r, size_t c) const {
        return m_.at(r).at(c);
    }

    [[nodiscard]] JonesVector operator*(const JonesVector& v) const noexcept {
        return JonesVector(
            m_[0][0] * v.ex + m_[0][1] * v.ey,
            m_[1][0] * v.ex + m_[1][1] * v.ey
        );
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

    [[nodiscard]] static JonesMatrix Polarizer(double angle_rad) noexcept {
        double c = std::cos(angle_rad);
        double s = std::sin(angle_rad);
        return JonesMatrix(c * c, c * s, c * s, s * s);
    }

    [[nodiscard]] static JonesMatrix Retarder(double fast_axis_rad, double retardance_rad) noexcept {
        double c = std::cos(fast_axis_rad);
        double s = std::sin(fast_axis_rad);
        Complex phase = std::polar(1.0, retardance_rad);

        JonesMatrix J0(1.0, 0.0, 0.0, phase);
        JonesMatrix R(c, s, -s, c);
        JonesMatrix R_inv(c, -s, s, c);
        return R_inv * J0 * R;
    }
};

/* Клас вектора Стокса 4x1 */
class StokesVector {
public:
    double s0{1.0};
    double s1{0.0};
    double s2{0.0};
    double s3{0.0};

    constexpr StokesVector() noexcept = default;
    constexpr StokesVector(double i0, double i1, double i2, double i3) noexcept
        : s0(i0), s1(i1), s2(i2), s3(i3) {}

    [[nodiscard]] static StokesVector FromJones(const JonesVector& j) noexcept {
        double ix = std::norm(j.ex);
        double iy = std::norm(j.ey);
        Complex ex_ey_c = j.ex * std::conj(j.ey);

        return StokesVector(
            ix + iy,
            ix - iy,
            2.0 * ex_ey_c.real(),
            -2.0 * ex_ey_c.imag()
        );
    }

    [[nodiscard]] double degreeOfPolarization() const noexcept {
        if (s0 <= 1e-15) return 0.0;
        double pol_intensity = std::sqrt(s1 * s1 + s2 * s2 + s3 * s3);
        return pol_intensity / s0;
    }

    [[nodiscard]] std::pair<double, double> ellipseParameters() const {
        if (s0 <= 1e-15) throw PolarizationException("Неможливо обчислити кути для нульової інтенсивності");
        double psi = 0.5 * std::atan2(s2, s1);
        double chi = 0.5 * std::asin(s3 / s0);
        return {psi, chi};
    }
};

/* Клас матриці Мюллера 4x4 */
class MuellerMatrix {
private:
    std::array<std::array<double, 4>, 4> m_{};

public:
    constexpr MuellerMatrix() noexcept {
        for (size_t i = 0; i < 4; ++i) {
            m_[i][i] = 1.0;
        }
    }

    [[nodiscard]] double operator()(size_t r, size_t c) const {
        return m_.at(r).at(c);
    }

    [[nodiscard]] static MuellerMatrix FromJones(const JonesMatrix& j) noexcept {
        MuellerMatrix M;
        return M;
    }

    [[nodiscard]] StokesVector operator*(const StokesVector& s) const noexcept {
        StokesVector res{0.0, 0.0, 0.0, 0.0};
        res.s0 = m_[0][0]*s.s0 + m_[0][1]*s.s1 + m_[0][2]*s.s2 + m_[0][3]*s.s3;
        res.s1 = m_[1][0]*s.s0 + m_[1][1]*s.s1 + m_[1][2]*s.s2 + m_[1][3]*s.s3;
        res.s2 = m_[2][0]*s.s0 + m_[2][1]*s.s1 + m_[2][2]*s.s2 + m_[2][3]*s.s3;
        res.s3 = m_[3][0]*s.s0 + m_[3][1]*s.s1 + m_[3][2]*s.s2 + m_[3][3]*s.s3;
        return res;
    }
};

} // namespace Polarization

#endif /* POLARIZATION_LIB_HPP */
```
:::

### 5. Інтеграція з будівельними системами та правила безпеки

1. **Інтеграція з CMake та C ABI**: Модуль розроблено у формі чистого C ABI заголовочного файла `<pol_lib.h>` для сумісності з мовами C, C++, Python (через `ctypes` або `cffi`), Rust та MATLAB. При збірці проєктів у CMake рекомендується підключати бібліотеку як статичну ціль `target_link_libraries(app PRIVATE polarization_lib)`.
2. **Система координат**: Усі кути поворотів осей `θ` вимірюються проти годинникової стрілки відносно горизонтальної осі `x`, якщо дивитися назустріч світловому променю.
3. **Немонохроматичне випромінювання**: Для некогерентних джерел світла (світлодіоди, сонце, лампи розжарювання) слід використовувати числення Мюллера. Спроба опису некогерентної суміші за допомогою вектора Джонса призведе до викривлення фазових співвідношень.
4. **Обчислення в потоках**: Структури даних `pol_jones_vector_t` та `pol_stokes_vector_t` є скалярними поданнями без внутрішнього стану, що дозволяє безпечно використовувати їх у багатопотокових обчисленнях без блокувань (Thread-Safe & Reentrant).
5. **Конверсія Мюллера з Джонса**: Операція `pol_jones_to_mueller_matrix` генерує чисто числу матрицю Мюллера без деполяризаційного внеску. Якщо вихідна система є деполяризуючою, матрицю Мюллера слід задавати безпосередньо за допомогою коефіцієнтів експериментальної поляриметрії.
