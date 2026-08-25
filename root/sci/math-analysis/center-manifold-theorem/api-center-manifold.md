# 📋 Інтерфейс бібліотеки чисельної редукції на центральний многовид

Даний документ визначає повний публічний програмний контракт (API) C/C++ бібліотеки `libcenter_manifold`, призначеної для автоматизованого обчислення Тейлорівських коефіцієнтів центрального многовиду, побудови редукованого векторного поля та чисельного інтегрування динамічних систем зі спектральним розподілом мод.

Бібліотека створена для використання у високопродуктивних обчислювальних модулях аерокосмічного моделювання, аналізу стійкості конструкцій та симуляторах нелінійних коливальних систем. Основною метою бібліотеки є автоматизація процедури редукції високовимірних моделей без необхідності виконання ручних алгебраїчних перетворень.

---

### 1. Заголовний файл, концепція архітектури та залежності

Архітектура бібліотеки спирається на чітке розмежування об'єктів конфігурації, математичного опису диференціальної системи та обчисленого геометричного многовиду. 

:::tabs
```c
#include "center_manifold.h"
```
```cpp
#include <center_manifold.hpp>
```
:::

Бібліотека гарантує сумісність зі стандартами C11 та C++20/C++23, не має сторонніх зовнішніх залежностей (використовує лише функціонал стандартної бібліотеки C/C++) та забезпечує повну потокобезпечність (Thread Safety) для незалежних екземплярів даних.

Головний принцип архітектури — **відсутність прихованого глобального стану**. Усі розрахункові функції приймають явні вказівники на структури контексту, що дозволяє виконувати паралельні обчислення фазових траєкторій у багатьох потоках виконання (multithreading) без використання локальних блокувань чи м'ютексів.

Для розробників на мові C++ реалізована сучасна обгортка `center_manifold.hpp`, яка використовує концепцію RAII (Resource Acquisition Is Initialization), строго типізовані переліки `enum class`, різновиди типізованих обробників помилок `std::expected` та контейнерну семантику без прямого управління сирими вказівниками.

---

### 2. Переліки та коди повернення статусу виконання

Усі функції бібліотеки, які виконують обчислення, перевірку спектра або виділення пам'яті, повертають статус виконання у вигляді коду `cm_status_e`. Від'ємні значення відповідають помилкам ініціалізації або розбіжності чисельних алгоритмів, тоді як нуль свідчить про успішне завершення операції.

| Перелік (Enum) | Числове значення | Опис статусу виконання |
| :--- | :---: | :--- |
| `CM_SUCCESS` | `0` | Операція виконана успішно |
| `CM_ERR_NULL_POINTER` | `-1` | Передано вказівник `NULL` на обов'язковий аргумент |
| `CM_ERR_INVALID_DIM` | `-2` | Некоректна вимірність центрального або стійкого підпросторів |
| `CM_ERR_NON_STABLE_SPECTRUM` | `-3` | Спектр `B` містить власні значення з `Re(λ) ≥ 0` |
| `CM_ERR_NON_CENTER_SPECTRUM` | `-4` | Спектр `A` містить власні значення з `Re(λ) ≠ 0` |
| `CM_ERR_ALLOCATION_FAILED` | `-5` | Не вдалося виділити динамічну пам'ять для коефіцієнтів |
| `CM_ERR_DIVERGENCE_DETECTED` | `-6` | Фазова точка вийшла за межі локального радіуса Тейлора |

Кожен код помилки супроводжується детальним записом у системний журнал або текстовий буфер при ввімкненні режимів відлагодження.

---

### 3. Опис основних структур даних

#### 3.1. Структура конфігурації `cm_solver_config_t`

Управляє параметрами точності обчислення багатовиду та обмеженнями чисельного інтегрування.

:::tabs
```c
typedef struct {
    uint32_t max_taylor_order;  /* Максимальний порядок Тейлора (за замовчуванням: 3) */
    double   convergence_tol;   /* Допуск збіжності залишку N(h) <= tol */
    double   taylor_radius;     /* Максимально припустимий радіус |x| <= R */
    bool     enable_fast_decay; /* Опція автозанулення згасаючих мод після транзієнту */
} cm_solver_config_t;
```
```cpp
namespace CM {
struct SolverConfig {
    std::uint32_t max_taylor_order{3};  // Максимальний порядок Тейлора
    double        convergence_tol{1e-8}; // Допуск збіжності залишку
    double        taylor_radius{1.0};    // Радіус збіжності |x| <= R
    bool          enable_fast_decay{true};
};
} // namespace CM
```
:::

Параметр `max_taylor_order` визначає найвищий ступінь полінома Тейлора. Збільшення порядку полінома до `k = 4` чи `k = 5` підвищує точність апроксимації многовиду, але експоненційно збільшує обсяг пам'яті для збереження тензорів коефіцієнтів.

#### 3.2. Структура опису системи `cm_system_t`

Визначає лінійну та нелінійну частини вихідної диференціальної системи у канонічному відокремленому вигляді.

:::tabs
```c
typedef struct {
    uint32_t dim_center;   /* Вимірність n центрального підпростору E^c */
    uint32_t dim_stable;   /* Вимірність m стійкого підпростору E^s */
    
    double  *matrix_A;     /* Двовимірний масив (n x n) нейтральної матриці A */
    double  *matrix_B;     /* Двовимірний масив (m x m) гурвіцевої матриці B */
    
    /* Функтор нелінійностей f(x, y) розміру n */
    void (*func_f)(const double *x, const double *y, double *out_f, void *user_data);
    
    /* Функтор нелінійностей g(x, y) розміру m */
    void (*func_g)(const double *x, const double *y, double *out_g, void *user_data);
    
    void *user_data;       /* Укористувацький контекст даних для функторів */
} cm_system_t;
```
```cpp
namespace CM {
using VectorFunc = std::function<void(std::span<const double>, std::span<const double>, std::span<double>)>;

class System {
public:
    System(std::size_t dim_center, std::size_t dim_stable);
    
    void set_matrix_A(std::span<const double> A);
    void set_matrix_B(std::span<const double> B);
    void set_nonlinearity_f(VectorFunc f);
    void set_nonlinearity_g(VectorFunc g);

    [[nodiscard]] std::size_t dim_center() const noexcept;
    [[nodiscard]] std::size_t dim_stable() const noexcept;
};
} // namespace CM
```
:::

Вказувані матриці `matrix_A` та `matrix_B` зберігаються у пам'яті за правилом Row-Major order (по рядках). Функтори `func_f` та `func_g` повинні обчислювати лише суто нелінійні доданки вищого порядку (`O(|x|² + |y|²)`), не включаючи лінійні члени, що вже входять до матриць `A` та `B`.

#### 3.3. Структура обчисленого багатовиду `cm_manifold_t`

Зберігає тензори Тейлорівських коефіцієнтів многовиду `y = h(x)`.

:::tabs
```c
typedef struct {
    uint32_t dim_center;       /* Вимірність n */
    uint32_t dim_stable;       /* Вимірність m */
    uint32_t order;            /* Порядок Тейлора k */
    
    double  *coeff_tensor;     /* Масив розміру m x N_poly */
    size_t   poly_terms_count; /* Кількість поліноміальних членів */
} cm_manifold_t;
```
```cpp
namespace CM {
class Manifold {
public:
    Manifold(std::size_t dim_center, std::size_t dim_stable, std::uint32_t order);
    
    [[nodiscard]] std::vector<double> evaluate(std::span<const double> x) const;
    [[nodiscard]] std::uint32_t order() const noexcept;
};
} // namespace CM
```
:::

---

### 4. Опис сигнатур публічних функцій

#### 4.1. Створення та ініціалізація об'єктів

Для гарантії сумісності між різними версіями бібліотеки створення об'єктів системи виконується через спеціалізовані конструктори, які перевіряють спектральні вимоги.

:::tabs
```c
/* Заповнює конфігурацію за замовчуванням */
cm_status_e cm_config_init_default(cm_solver_config_t *config);

/* Створює об'єкт системи з перевіркою матричних спектрів A та B */
cm_status_e cm_system_create(cm_system_t **sys, uint32_t dim_center, uint32_t dim_stable);

/* Звільняє ресурс системи та її матричні структури */
void cm_system_destroy(cm_system_t *sys);
```
```cpp
namespace CM {
// У C++ створюється RAII об'єкт класу System, розрахунок спектра у конструкторі
[[nodiscard]] std::expected<System, Status> create_system(std::size_t dim_center, std::size_t dim_stable);
} // namespace CM
```
:::

При виклику `cm_system_create` бібліотека виконує перевірку власних значень матриць: якщо матриця `B` містить хоча б одне власне значення з `Re(λ) ≥ 0`, функція повертає помилку `CM_ERR_NON_STABLE_SPECTRUM`.

#### 4.2. Обчислення коефіцієнтів многовиду

Процедура редукції виконує автоматичне формування символьно-чисельної системи лінійних рівнянь для знаходження невизначених коефіцієнтів.

:::tabs
```c
/* Обчислює тензори коефіцієнтів h(x) до вказаного порядку order */
cm_status_e cm_compute_manifold(
    const cm_system_t       *sys,
    const cm_solver_config_t *config,
    cm_manifold_t          **manifold
);

/* Обчислює векторне значення h(x) у заданій фазовій точці x */
cm_status_e cm_eval_manifold(
    const cm_manifold_t *manifold,
    const double        *x,
    double              *out_y
);

/* Звільняє пам'ять тензора коефіцієнтів многовиду */
void cm_manifold_destroy(cm_manifold_t *manifold);
```
```cpp
namespace CM {
// C++ метод обчислення повернуто об'єкт Manifold у списку std::expected
[[nodiscard]] std::expected<Manifold, Status> compute_manifold(
    const System& sys,
    const SolverConfig& config
);
} // namespace CM
```
:::

#### 4.3. Обчислення редукованого поля та чисельне інтегрування

Обчислення правих частин та виконання кроку чисельного інтегрування реалізовано з оптимізацією векторних інструкцій (SIMD) для досягнення максимальної швидкодії.

:::tabs
```c
/* Обчислює вектор правого боку редукованої системи: dx/dt = A*x + f(x, h(x)) */
cm_status_e cm_eval_reduced_rhs(
    const cm_system_t   *sys,
    const cm_manifold_t *manifold,
    const double        *x,
    double              *out_dxdt
);

/* Виконує один крок чисельного інтегрування редукованої системи методом RK4 */
cm_status_e cm_step_reduced_rk4(
    const cm_system_t   *sys,
    const cm_manifold_t *manifold,
    double              *inout_x,
    double               dt
);
```
```cpp
namespace CM {
class Solver {
public:
    Solver(const System& sys, const Manifold& mf);
    
    void step_reduced_rk4(std::span<double> x, double dt) const;
};
} // namespace CM
```
:::

---

### 5. Контракт володіння пам'яттю, життєвий цикл та потокобезпечність

Управління ресурсами в бібліотеці спирається на чітко визначені правила володіння (Ownership Model):

1. **Модель володіння пам'яттю**:
   - Об'єкти `cm_system_t` та `cm_manifold_t`, створені викликами `cm_system_create` та `cm_compute_manifold`, виділяють пам'ять у купі (heap).
   - Користувацький код зобов'язаний викликом парних деструкторів `cm_system_destroy` та `cm_manifold_destroy` звільняти виділені ресурси після завершення розрахунків.
   - У мові C++ автоматичні деструктори класів `System` та `Manifold` здійснюють звільнення контейнерів `std::vector` автоматично (RAII), унеможливлюючи витоки пам'яті (Memory Leaks).
   - Буфери масивів `x` та `out_y` у розрахункових функціях належать викликаючій стороні (можуть бути виділені у стеку функцій для уникнення накладних витрат).
2. **Гарантії потокобезпечності**:
   - Функція обчислення многовиду `cm_eval_manifold` та крок інтегрування `cm_step_reduced_rk4` є чисто функціональними (thread-safe), оскільки вони лише читають дані зі структури `cm_manifold_t`.
   - Це дозволяє розпаралелювати обчислення тисяч фазових траєкторій (наприклад, для проведення Монте-Карло аналізу стійкості) на багатьох ядрах процесора з використанням одного спільного екземпляра `cm_manifold_t`.
3. **Обробка виняткових ситуацій у розрахунковому циклі**:
   - Якщо під час розрахунку фазова точка виходить за межі заданого радіуса Тейлора `taylor_radius`, функція `cm_eval_manifold` повертає статус `CM_ERR_DIVERGENCE_DETECTED`. Бібліотека гарантує відсутність арифметичного переповнення або неконтрольованого падіння програми (Hard Crash), надаючи викликаючій стороні можливість відновити стан або зменшити крок інтегрування.

---

### 6. Сумісність із компіляторами та варіанти компонування

Бібліотека поставляється у вигляді вихідного коду C/C++ та збирається у статичну (`libcenter_manifold.a` / `center_manifold.lib`) або динамічну (`libcenter_manifold.so` / `.dll`) бібліотеку.

Для забезпечення максимальної переносності підтримуються такі компілятори:
- **GCC** (версії 10.0 і вище) — з підтримкою прапорців `-O3 -march=native -std=c11`;
- **Clang/LLVM** (версії 12.0 і вище) — з використанням політики об оптимізації векторних обчислень `-fvectorize`;
- **MSVC** (Visual Studio 2022 / C++20) — сумісність з MSVC ABI та специфікаціями `/std:c++20`.

---

### 7. Повний приклад використання C та C++ API

Нижче наведено практичний приклад ініціалізації системи, розрахунку многовиду та виконання кроків чисельного інтегрування для нелінійного механічного осцилятора.

:::tabs
```c
#include <stdio.h>
#include "center_manifold.h"

/* Нелінійність f(x, y) = x*y */
static void my_func_f(const double *x, const double *y, double *out_f, void *user_data) {
    (void)user_data;
    out_f[0] = x[0] * y[0];
}

/* Нелінійність g(x, y) = x^2 */
static void my_func_g(const double *x, const double *y, double *out_g, void *user_data) {
    (void)user_data;
    (void)y;
    out_g[0] = x[0] * x[0];
}

int main(void) {
    cm_solver_config_t config;
    cm_config_init_default(&config);
    config.max_taylor_order = 3;
    
    cm_system_t *sys = NULL;
    if (cm_system_create(&sys, 1, 1) != CM_SUCCESS) {
        fprintf(stderr, "Помилка створення системи\n");
        return 1;
    }
    
    sys->matrix_A[0] = 0.0;    /* Нейтральний спектр */
    sys->matrix_B[0] = -5.0;   /* Стійкий спектр (gamma = 5) */
    sys->func_f = my_func_f;
    sys->func_g = my_func_g;
    
    cm_manifold_t *mf = NULL;
    cm_status_e status = cm_compute_manifold(sys, &config, &mf);
    if (status != CM_SUCCESS) {
        fprintf(stderr, "Помилка обчислення многовиду: %d\n", status);
        cm_system_destroy(sys);
        return 1;
    }
    
    printf("Многовид успішно побудовано (порядок %u)\n", mf->order);
    
    double x_state[1] = {0.3};
    double dt = 0.01;
    
    for (int step = 0; step < 50; step++) {
        cm_step_reduced_rk4(sys, mf, x_state, dt);
        if (step % 10 == 0) {
            double y_eval[1];
            cm_eval_manifold(mf, x_state, y_eval);
            printf("Крок %2d: x = %.6f, h(x) = %.6f\n", step, x_state[0], y_eval[0]);
        }
    }
    
    cm_manifold_destroy(mf);
    cm_system_destroy(sys);
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <span>
#include <format>
#include <center_manifold.hpp>

int main() {
    CM::SolverConfig config{.max_taylor_order = 3};

    auto sys_exp = CM::create_system(1, 1);
    if (!sys_exp) {
        std::cerr << "Помилка створення системи\n";
        return 1;
    }

    auto sys = std::move(*sys_exp);
    sys.set_matrix_A(std::array{0.0});
    sys.set_matrix_B(std::array{-5.0});

    sys.set_nonlinearity_f([](auto x, auto y, auto out_f) {
        out_f[0] = x[0] * y[0];
    });

    sys.set_nonlinearity_g([](auto x, auto y, auto out_g) {
        out_g[0] = x[0] * x[0];
    });

    auto mf_exp = CM::compute_manifold(sys, config);
    if (!mf_exp) {
        std::cerr << "Помилка обчислення многовиду\n";
        return 1;
    }

    const auto& mf = *mf_exp;
    std::cout << std::format("Многовид успішно побудовано (порядок {})\n", mf.order());

    CM::Solver solver(sys, mf);
    std::vector<double> x_state{0.3};
    constexpr double dt = 0.01;

    for (int step = 0; step < 50; ++step) {
        solver.step_reduced_rk4(x_state, dt);
        if (step % 10 == 0) {
            auto y_eval = mf.evaluate(x_state);
            std::cout << std::format("Крок {:2d}: x = {:.6f}, h(x) = {:.6f}\n", 
                                     step, x_state[0], y_eval[0]);
        }
    }

    return 0;
}
```
:::
