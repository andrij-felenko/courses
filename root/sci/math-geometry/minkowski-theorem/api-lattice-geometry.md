# 📋 Специфікація інтерфейсу геометрії ґраток та опуклих тіл

Цей довідник визначає публічний програмний інтерфейс (API) бібліотеки `liblatgeom`, призначеної для виконання геометричних обчислень над дискретними ґратками, перевірки умов теореми Мінковського про опуклі тіла, розрахунку послідовних мінімумів, обчислення двоїстих ґраток, генерації криптографічних q-арних ґраток, редукції базисів (LLL/BKZ), наближеного декодування Бабая та точного розв'язання задач найкоротшого (SVP) і найближчого (CVP) векторів.

Інтерфейс спроєктовано за принципом нульових прихованих накладних витрат (zero-cost abstractions), передбачуваного керування пам'яттю та детермінованої обробки помилок. Специфікація надає строгі гарантії інваріантів, чисельної стійкості та повної потокової безпеки для операцій читання.

## Архітектурні принципи та угоди про виклики

Бібліотека дотримується чіткого розподілу між низькорівневим C-інтерфейсом (сумісним з ANSI C99/C11 та ABI C) та ідіоматичним інтерфейсом C++20:

1. **Керування пам'яттю та володіння ресурсами:**
   - У мові C всі структури ініціалізуються явними функціями-конструкторами `latgeom_basis_init()` та звільняються через `latgeom_basis_free()`. Функції обчислення підтримують роботу як із попередньо виділеними буферами користувача, так і з динамічною пам'яттю. Внутрішні матриці вирівнюються за межею 64 байти (`alignas(64)` / `posix_memalign`) для ефективного використання векторних інструкцій AVX2 та AVX-512.
   - Бібліотека підтримує впровадження користувацьких алокаторів пам'яті через функцію `latgeom_set_allocator(custom_malloc, custom_free)`, що дозволяє інтегрувати бібліотеку в середовища з пулами пам'яті (arena allocators) без звернень до стандартної купи операційної системи.
   - У мові C++ використовується концепція RAII (Resource Acquisition Is Initialization). Усі структури даних інкапсульовані в безпечні класи з автоматичним звільненням ресурсів у деструкторах, а для передачі неволодіючих масивів застосовується `std::span`. Конструктори копіювання заборонені там, де це спричиняє неявне дублювання великих матриць; замість цього реалізовано семантику переміщення (move semantics).
2. **Обробка помилок та коди повернення:**
   - C-функції повертають цілочисельний код стану типу `latgeom_status_t`. Усі результати обчислень повертаються через вихідні вказівники. Жодна функція бібліотеки не викликає аварійне завершення процесу `abort()` чи `exit()`.
   - C++ інтерфейс повертає типізовані структури результатів, загорнуті в `std::expected<T, latgeom_error_code>` або `std::optional<T>`, що унеможливлює ігнорування помилкових станів на етапі компіляції.
3. **Чисельна точність та типи даних:**
   - Координати вузлів ґратки зберігаються як 64-бітні цілі числа зі знаком `int64_t`. Це забезпечує точне представлення без втрати молодших бітів при унімодулярних перетвореннях над дискретними базисами.
   - Дійсні коефіцієнти проєкцій Грама–Шмідта, об'єми та радіуси кулі Мінковського обчислюються у форматі подвійної точності `double` (IEEE 754) з явною перевіркою на втрату точності та переповнення. Для запобігання переповненню детермінанта у великих розмірностях бібліотека надає функцію обчислення логарифма детермінанта `log_det(L) = ∑ ln ‖b_i*‖`. Проміжні розрахунки ортогоналізації виконують компенсаційні ітерації для мінімізації накопичення похибок заокруглення мантиси чисел з плаваючою комою.

## Коди помилок та статусів

Усі функції бібліотеки повертають один із наведених нижче статусів виконання:

| Символьна назва константи | Числове значення | Опис причини виникнення помилки |
|:---|:---:|:---|
| `LATGEOM_SUCCESS` | `0` | Операція успішно завершена, результат валідний. |
| `LATGEOM_ERR_NULL_POINTER` | `-1` | Передано нульовий вказівник на обов'язковий аргумент. |
| `LATGEOM_ERR_INVALID_DIM` | `-2` | Розмірність ґратки виходить за допустимі межі `[1, 64]`. |
| `LATGEOM_ERR_SINGULAR_BASIS` | `-3` | Вектори базису лінійно залежні: визначник `det(L) = 0` або число обумовленості перевищує поріг. |
| `LATGEOM_ERR_NOT_CONVEX` | `-4` | Задане тіло порушує аксіому опуклості або центральної симетрії. |
| `LATGEOM_ERR_OUT_OF_MEMORY` | `-5` | Не вдалося виділити необхідний обсяг динамічної пам'яті. |
| `LATGEOM_ERR_TIMEOUT` | `-6` | Перевищено ліміт часу або кількості вузлів дерева перебору. |
| `LATGEOM_ERR_NO_LATTICE_POINT` | `-7` | Об'єм тіла менший за поріг Мінковського, ненульових точок не знайдено. |
| `LATGEOM_ERR_OVERFLOW` | `-8` | Обчислення призвело до арифметичного переповнення або втрати розрядності. |
| `LATGEOM_ERR_INVALID_PARAM` | `-9` | Передано некоректний числовий параметр (наприклад, `δ ∉ (0.25, 1.0]`). |

## Опис структур даних

### 1. Структура `latgeom_basis_t` (Базис ґратки)
Містить повну інформацію про матрицю базису `B`, її розклад Грама–Шмідта, фундаментальний визначник, логарифм визначника, дефект ортогональності, гауссову евристику та теоретичний радіус Мінковського.

:::tabs
```c
typedef struct {
    size_t dim;                    /* Розмірність простору n */
    int64_t *b;                    /* Матриця базису b[i * n + j], розмір n x n */
    double *b_star;                /* Ортогональний базис Грама-Шмідта (n x n) */
    double *mu;                    /* Нижньотрикутна матриця коефіцієнтів mu (n x n) */
    double *b_star_sq;             /* Квадрати норм ||b_star[i]||^2 (розмір n) */
    double determinant;            /* Фундаментальний визначник det(L) */
    double log_determinant;        /* Натуральний логарифм визначника ln(det(L)) */
    double minkowski_radius;       /* Радіус Мінковського R_M = sqrt(n) * det(L)^(1/n) */
    double gaussian_heuristic;     /* Гауссова евристика GH(L) = sqrt(n/(2*pi*e)) * det(L)^(1/n) */
    double orthogonality_defect;   /* Дефект ортогональності prod(||b_i||) / det(L) */
    bool is_orthogonalized;        /* Прапорець готовності ортогонального розкладу */
} latgeom_basis_t;
```
```cpp
namespace latgeom {

struct BasisDescriptor {
    size_t dimension{0};
    std::vector<int64_t> basis_matrix;
    std::vector<double> gram_schmidt_basis;
    std::vector<double> mu_coefficients;
    std::vector<double> square_norms;
    double determinant{1.0};
    double log_determinant{0.0};
    double minkowski_radius{0.0};
    double gaussian_heuristic{0.0};
    double orthogonality_defect{1.0};
    bool is_orthogonalized{false};
};

} // namespace latgeom
```
:::

**Інваріанти структури:**
- `dim` знаходиться в діапазоні `[1, 64]`.
- Якщо `is_orthogonalized == true`, то `b_star_sq[i] > 0` для всіх `0 ≤ i < dim`.
- Матриця `mu` є унітрикутною: `mu[i * n + i] = 1.0` та `mu[i * n + j] = 0.0` при `j > i`.
- `determinant = sqrt(prod_{i=0}^{n-1} b_star_sq[i])`.
- `log_determinant = 0.5 * sum_{i=0}^{n-1} ln(b_star_sq[i])`.
- `gaussian_heuristic = sqrt(dim / (2.0 * 3.141592653589793 * 2.718281828459045)) * pow(determinant, 1.0 / dim)`.
- Дефект ортогональності `orthogonality_defect ≥ 1.0` (рівність досягається тоді й лише тоді, коли базис попарно ортогональний).

### 2. Структура `latgeom_convex_body_t` (Опукле центрально-симетричне тіло)
Описує геометричні параметри опуклого центрально-симетричного тіла `K ⊂ ℝⁿ`, відносно якого перевіряються умови першої та другої теорем Мінковського.

:::tabs
```c
typedef enum {
    LATGEOM_BODY_ELLIPSOID = 1,    /* Еліпсоїд: x^T * Q * x <= r^2 */
    LATGEOM_BODY_HYPERCUBE = 2,    /* Симетричний паралелепіпед: |l_i(x)| <= c_i */
    LATGEOM_BODY_CROSS_POLYTOPE = 3/* Крос-політоп: sum |l_i(x)| <= r */
} latgeom_body_type_t;

typedef struct {
    size_t dim;                    /* Розмірність простору n */
    latgeom_body_type_t type;      /* Геометричний тип тіла */
    double *shape_matrix;          /* Матриця форми Q розміру n x n (симетрична додатно визначена) */
    double *limits;                /* Межі координат c_i (розмір n) */
    double radius;                 /* Евклідів радіус r (для кулі або еліпсоїда) */
    double volume;                 /* Аналітично обчислений n-вимірний об'єм vol(K) */
} latgeom_convex_body_t;
```
```cpp
namespace latgeom {

enum class BodyType {
    Ellipsoid = 1,
    Hypercube = 2,
    CrossPolytope = 3
};

struct ConvexBody {
    size_t dimension{0};
    BodyType type{BodyType::Ellipsoid};
    std::vector<double> shape_matrix;
    std::vector<double> limits;
    double radius{0.0};
    double volume{0.0};
};

} // namespace latgeom
```
:::

**Інваріанти структури:**
- `volume > 0.0`.
- Для еліпсоїда матриця `shape_matrix` є симетричною (`Q = Q^T`) та додатно визначеною (`x^T Q x > 0` для `x != 0`).
- Для паралелепіпеда всі `limits[i] > 0.0`.

### 3. Структура `latgeom_svp_result_t` (Результат розв'язання SVP)

:::tabs
```c
typedef struct {
    int64_t *coordinates;          /* Цілі коефіцієнти z_i розкладу v = sum(z_i * b_i) */
    double *vector;                /* Декартові координати знайденого вектора v (розмір n) */
    double euclidean_norm;         /* Евклідова довжина вектора ||v|| = lambda_1(L) */
    double hermite_factor;         /* Фактор Ерміта ||v|| / det(L)^(1/n) */
    double root_hermite_factor;    /* Кореневий фактор Ерміта (||v|| / det(L)^(1/n))^(1/n) */
    uint64_t visited_nodes;        /* Кількість відвіданих вузлів дерева перебору */
    double execution_time_ms;      /* Час виконання алгоритму в мілісекундах */
} latgeom_svp_result_t;
```
```cpp
namespace latgeom {

struct SvpSolution {
    std::vector<int64_t> coordinates;
    std::vector<double> vector;
    double euclidean_norm{0.0};
    double hermite_factor{0.0};
    double root_hermite_factor{0.0};
    uint64_t visited_nodes{0};
    double execution_time_ms{0.0};
};

} // namespace latgeom
```
:::

### 4. Структура `latgeom_minima_result_t` (Послідовні мінімуми Мінковського)

:::tabs
```c
typedef struct {
    double *lambda;                /* Масив послідовних мінімумів lambda_1 <= ... <= lambda_n */
    double product_lambda;         /* Добуток мінімумів prod_{i=1}^n lambda_i */
    double lower_bound;            /* Теоретична нижня межа (2^n / n!) * det(L) / vol(K) */
    double upper_bound;            /* Теоретична верхня межа 2^n * det(L) / vol(K) */
    bool satisfies_second_theorem; /* Прапорець виконання другої теореми Мінковського */
} latgeom_minima_result_t;
```
```cpp
namespace latgeom {

struct MinimaVerification {
    std::vector<double> lambda;
    double product_lambda{0.0};
    double lower_bound{0.0};
    double upper_bound{0.0};
    bool satisfies_second_theorem{false};
};

} // namespace latgeom
```
:::

## Специфікація функцій API

### `latgeom_basis_init`
Ініціалізує внутрішні структури дескриптора ґратки, копіює матрицю базису та виділяє вирівняну пам'ять під допоміжні матриці.

:::tabs
```c
latgeom_status_t latgeom_basis_init(latgeom_basis_t *basis, size_t dim, const int64_t *matrix);
```
```cpp
namespace latgeom {
std::expected<LatticeBasis, ErrorCode> LatticeBasis::create(size_t dim, std::span<const int64_t> matrix);
}
```
:::

| Параметр | Тип | Напрямок | Опис |
|:---|:---|:---:|:---|
| `basis` | `latgeom_basis_t*` | [out] | Вказівник на структуру дескриптора базису ґратки. |
| `dim` | `size_t` | [in] | Розмірність простору `n` (`1 ≤ dim ≤ 64`). |
| `matrix` | `const int64_t*` | [in] | Одновимірний масив розміру `dim * dim` із рядковою орієнтацією базисних векторів. |

- **Передмови:** `matrix != NULL`, `basis != NULL`, `1 ≤ dim ≤ 64`.
- **Післяумови:** Виділено вирівняні буфери для `b`, `b_star`, `mu`, `b_star_sq`. Поле `is_orthogonalized` скинуто в `false`.
- **Коди повернення:** `LATGEOM_SUCCESS`, `LATGEOM_ERR_NULL_POINTER`, `LATGEOM_ERR_INVALID_DIM`, `LATGEOM_ERR_OUT_OF_MEMORY`.
- **Складність:** Часова `O(n²)`, просторова `O(n²)`.

---

### `latgeom_basis_free`
Звільняє всі динамічні буфери, виділені функцією `latgeom_basis_init()`, та обнуляє вказівники дескриптора.

:::tabs
```c
void latgeom_basis_free(latgeom_basis_t *basis);
```
```cpp
namespace latgeom {
LatticeBasis::~LatticeBasis() noexcept = default; // Автоматичне звільнення векторів RAII
}
```
:::

| Параметр | Тип | Напрямок | Опис |
|:---|:---|:---:|:---|
| `basis` | `latgeom_basis_t*` | [in, out] | Дескриптор ґратки для звільнення. Безпечно викликати для `NULL`. |

- **Передмови:** Немає.
- **Післяумови:** Усі вказівники всередині `basis` встановлено в `NULL`, поле `dim` скинуто в `0`.
- **Складність:** `O(1)`.

---

### `latgeom_basis_orthogonalize`
Виконує модифіковану ортогоналізацію Грама–Шмідта (MGS) над векторами базису, розраховує фундаментальний визначник `det(L)`, натуральний логарифм визначника `ln(det(L))`, дефект ортогональності, гауссову евристику та теоретичний радіус Мінковського `R_M`.

:::tabs
```c
latgeom_status_t latgeom_basis_orthogonalize(latgeom_basis_t *basis);
```
```cpp
namespace latgeom {
std::expected<void, ErrorCode> LatticeBasis::orthogonalize() noexcept;
}
```
:::

| Параметр | Тип | Напрямок | Опис |
|:---|:---|:---:|:---|
| `basis` | `latgeom_basis_t*` | [in, out] | Ініціалізований дескриптор ґратки. |

- **Передмови:** `basis != NULL`, структура успішно ініціалізована.
- **Післяумови:** Заповнено масиви `b_star`, `mu`, `b_star_sq`. Поле `determinant` містить `|det(B)|`. Поле `minkowski_radius` містить `√n · (det(L))^(1/n)`. Поле `is_orthogonalized = true`.
- **Коди повернення:** `LATGEOM_SUCCESS`, `LATGEOM_ERR_SINGULAR_BASIS` (якщо `b_star_sq[i] < 10⁻¹²`), `LATGEOM_ERR_NULL_POINTER`.
- **Складність:** Часова `O(n³)`, додаткова просторова `O(1)`.

---

### `latgeom_basis_dual`
Обчислює матрицю базису двоїстої ґратки `L* = { y ∈ ℝⁿ : ∀ x ∈ L, ⟨x, y⟩ ∈ ℤ }` та перевіряє фундаментальну теорему переносу Баная–Куршака: `1 ≤ λ₁(L) · λₙ(L*) ≤ n`.

:::tabs
```c
latgeom_status_t latgeom_basis_dual(const latgeom_basis_t *basis, latgeom_basis_t *dual_basis);
```
```cpp
namespace latgeom {
[[nodiscard]] std::expected<LatticeBasis, ErrorCode> LatticeBasis::compute_dual() const;
}
```
:::

| Параметр | Тип | Напрямок | Опис |
|:---|:---|:---:|:---|
| `basis` | `const latgeom_basis_t*` | [in] | Вихідний дескриптор прямої ґратки `L`. |
| `dual_basis` | `latgeom_basis_t*` | [out] | Дескриптор двоїстої ґратки `L*`. |

- **Передмови:** `basis->is_orthogonalized == true`, `dual_basis != NULL`.
- **Післяумови:** `dual_basis` містить базис `B* = (B⁻¹)ᵀ`. Виконується рівність `dual_basis->determinant = 1.0 / basis->determinant`.
- **Складність:** Часова `O(n³)` (зворотний хід над унітрикутною матрицею Грама–Шмідта без потреби у загальному оберненні матриці), просторова `O(n²)`.

---

### `latgeom_basis_qary_generate`
Генерує випадкову криптографічну q-арну ґратку виду `L_q(A) = { x ∈ ℤⁿ : A x ≡ 0 (mod q) }`, що лежить в основі схем постквантового шифрування Kyber (ML-KEM) та цифрових підписів Dilithium (ML-DSA).

:::tabs
```c
latgeom_status_t latgeom_basis_qary_generate(latgeom_basis_t *basis,
                                             size_t n, size_t m, int64_t q,
                                             uint64_t seed);
```
```cpp
namespace latgeom {
[[nodiscard]] static std::expected<LatticeBasis, ErrorCode>
generate_qary(size_t n, size_t m, int64_t q, uint64_t seed);
}
```
:::

| Параметр | Тип | Напрямок | Опис |
|:---|:---|:---:|:---|
| `basis` | `latgeom_basis_t*` | [out] | Згенерований дескриптор q-арної ґратки розмірності `n`. |
| `n` | `size_t` | [in] | Повна розмірність простору ґратки (`n ≥ m`). |
| `m` | `size_t` | [in] | Кількість рядків матриці перевірки парності `A` (`1 ≤ m < n`). |
| `q` | `int64_t` | [in] | Простий або складений модуль конгруенції (`q ≥ 2`). |
| `seed` | `uint64_t` | [in] | Зерно детермінованого генератора випадкових чисел. |

- **Передмови:** `1 <= m < n <= 64`, `q >= 2`.
- **Післяумови:** Базис `B` має точний визначник `det(L) = qᵐ`. Теоретичний радіус Мінковського автоматично встановлюється в `R_M = √n · q^(m/n)`.
- **Складність:** Часова `O(n² · m)`, просторова `O(n²)`.

---

### `latgeom_minkowski_check`
Перевіряє виконання фундаментальної умови першої теореми Мінковського: чи перевищує об'єм опуклого симетричного тіла `vol(K)` поріг `2ⁿ · det(L)`.

:::tabs
```c
latgeom_status_t latgeom_minkowski_check(const latgeom_basis_t *basis,
                                         const latgeom_convex_body_t *body,
                                         bool *out_guaranteed,
                                         double *out_volume_ratio);
```
```cpp
namespace latgeom {
struct MinkowskiCheckResult {
    bool guaranteed{false};
    double volume_ratio{0.0};
};

[[nodiscard]] MinkowskiCheckResult check_minkowski(const LatticeBasis& basis, const ConvexBody& body) noexcept;
}
```
:::

| Параметр | Тип | Напрямок | Опис |
|:---|:---|:---:|:---|
| `basis` | `const latgeom_basis_t*` | [in] | Ортогоналізований дескриптор ґратки. |
| `body` | `const latgeom_convex_body_t*` | [in] | Дескриптор опуклого центрально-симетричного тіла `K`. |
| `out_guaranteed` | `bool*` | [out] | Встановлюється в `true`, якщо `vol(K) ≥ 2ⁿ · det(L)`. |
| `out_volume_ratio` | `double*` | [out] | Коефіцієнт покриття об'єму `vol(K) / (2ⁿ · det(L))`. |

- **Передмови:** `basis->is_orthogonalized == true`, `body->dim == basis->dim`.
- **Післяумови:** `*out_guaranteed = (*out_volume_ratio ≥ 1.0)`.
- **Складність:** `O(1)`.

---

### `latgeom_svp_solve`
Знаходить точний найкоротший ненульовий вектор ґратки `v ∈ L \ {0}` методом сферичного перебору Шнорра–Ейхнера, обмеженого радіусом Мінковського `R_M`.

:::tabs
```c
latgeom_status_t latgeom_svp_solve(latgeom_basis_t *basis,
                                   uint64_t max_nodes,
                                   latgeom_svp_result_t *result);
```
```cpp
namespace latgeom {
[[nodiscard]] std::expected<SvpSolution, ErrorCode>
LatticeBasis::solve_svp(uint64_t max_nodes = 1'000'000) const;
}
```
:::

| Параметр | Тип | Напрямок | Опис |
|:---|:---|:---:|:---|
| `basis` | `latgeom_basis_t*` | [in, out] | Дескриптор ґратки. |
| `max_nodes` | `uint64_t` | [in] | Граничний ліміт на кількість вузлів дерева перебору. |
| `result` | `latgeom_svp_result_t*` | [out] | Структура результату з координатами та довжиною вектора. |

- **Передмови:** `basis != NULL`, `result != NULL`, `max_nodes ≥ 1`.
- **Післяумови:** `result->euclidean_norm` містить точне значення першого мінімуму `λ₁(L)`. Розраховується фактор Ерміта `hermite_factor = λ₁(L) / (det(L))^(1/n)` та кореневий фактор `root_hermite_factor = (hermite_factor)^(1/n)`. Виконується нерівність Мінковського `result->euclidean_norm ≤ basis->minkowski_radius`.
- **Коди помилок:** `LATGEOM_ERR_TIMEOUT` (перевищено ліміт `max_nodes`), `LATGEOM_ERR_SINGULAR_BASIS`.
- **Складність:** Часова `2^(O(n · log n))` на LLL-редукованих базисах або `2^(O(n²))` на нередукованих; просторова пам'ять `O(n)`.

---

### `latgeom_cvp_solve`
Розв'язує задачу найближчого вектора (CVP) для заданої цільової точки простору `t ∈ ℝⁿ` через розширення базису за методом вкладення Каннана (Kannan's Embedding Technique) у просторі розмірності `n + 1`.

:::tabs
```c
latgeom_status_t latgeom_cvp_solve(latgeom_basis_t *basis,
                                   const double *target,
                                   uint64_t max_nodes,
                                   latgeom_svp_result_t *result);
```
```cpp
namespace latgeom {
[[nodiscard]] std::expected<SvpSolution, ErrorCode>
LatticeBasis::solve_cvp(std::span<const double> target, uint64_t max_nodes = 1'000'000) const;
}
```
:::

| Параметр | Тип | Напрямок | Опис |
|:---|:---|:---:|:---|
| `basis` | `latgeom_basis_t*` | [in] | Базис ґратки. |
| `target` | `const double*` | [in] | Координати цільової точки `t ∈ ℝⁿ` (масив довжини `n`). |
| `max_nodes` | `uint64_t` | [in] | Ліміт на кількість вузлів дерева перебору. |
| `result` | `latgeom_svp_result_t*` | [out] | Знайдена точка ґратки `v ∈ L`, найближча до `t`. |

- **Передмови:** `target != NULL`, `basis != NULL`, `result != NULL`.
- **Післяумови:** Вектор `result->vector` мінімізує евклідову відстань `‖target − v‖₂`.
- **Складність:** Часова еквівалентна SVP у просторі розмірності `n + 1`.

---

### `latgeom_babai_nearest_plane`
Швидке наближене розв'язання задачі CVP за поліноміальний час за алгоритмом найближчої площини Бабая (Babai Nearest Plane).

:::tabs
```c
latgeom_status_t latgeom_babai_nearest_plane(const latgeom_basis_t *basis,
                                             const double *target,
                                             latgeom_svp_result_t *result);
```
```cpp
namespace latgeom {
[[nodiscard]] std::expected<SvpSolution, ErrorCode>
LatticeBasis::babai_nearest_plane(std::span<const double> target) const;
}
```
:::

| Параметр | Тип | Напрямок | Опис |
|:---|:---|:---:|:---|
| `basis` | `const latgeom_basis_t*` | [in] | Базис ґратки (бажано LLL-редукований). |
| `target` | `const double*` | [in] | Цільова точка `t ∈ ℝⁿ`. |
| `result` | `latgeom_svp_result_t*` | [out] | Знайдений наближений вектор ґратки `v_approx ∈ L`. |

- **Гарантія якості Бабая:** `‖t − v_approx‖ ≤ 2^(n/2) · dist(t, L)`.
- **Складність:** Часова `O(n²)`, просторова `O(n)`.

---

### `latgeom_lll_reduce`
Виконує поліноміальну редукцію базису за алгоритмом Ленстри–Ленстри–Ловаса (LLL) із параметром фактора Ловаса `δ ∈ (0.25, 1.0]`.

:::tabs
```c
latgeom_status_t latgeom_lll_reduce(latgeom_basis_t *basis, double delta);
```
```cpp
namespace latgeom {
std::expected<void, ErrorCode> LatticeBasis::lll_reduce(double delta = 0.99);
}
```
:::

| Параметр | Тип | Напрямок | Опис |
|:---|:---|:---:|:---|
| `basis` | `latgeom_basis_t*` | [in, out] | Базис ґратки для модифікації. |
| `delta` | `double` | [in] | Параметр редукції Ловаса (рекомендоване значення `0.75` або `0.99`). |

- **Передмови:** `0.25 < delta <= 1.0`, `basis != NULL`.
- **Післяумови:** Базис `B` стає LLL-редукованим: `|μ_{i,j}| ≤ 0.5` для всіх `j < i`, та виконується умова Ловаса `‖b_{k+1}* + μ_{k+1,k} b_k*‖² ≥ δ · ‖b_k*‖²`.
- **Гарантія Мінковського після LLL:** `‖b₁‖ ≤ 2^((n-1)/4) · (det(L))^(1/n)`.
- **Складність:** Часова `O(n⁵ · B · log³(B))`, де `B` — бітова довжина максимального елемента базису.

---

### `latgeom_bkz_reduce`
Виконує блокову редукцію Коркіна–Золотарьова (BKZ) із розміром блоку `β ∈ [2, n]`.

:::tabs
```c
latgeom_status_t latgeom_bkz_reduce(latgeom_basis_t *basis, size_t beta, size_t max_tours);
```
```cpp
namespace latgeom {
std::expected<void, ErrorCode> LatticeBasis::bkz_reduce(size_t beta, size_t max_tours = 10);
}
```
:::

| Параметр | Тип | Напрямок | Опис |
|:---|:---|:---:|:---|
| `basis` | `latgeom_basis_t*` | [in, out] | Базис ґратки. |
| `beta` | `size_t` | [in] | Розмір блоку `β` (`2 ≤ beta ≤ dim`). |
| `max_tours` | `size_t` | [in] | Максимальна кількість проходів по всіх блоках ґратки. |

- **Гарантія редукції:** `‖b₁‖ ≤ β^(n / (2 * beta)) · (det(L))^(1/n)`.
- **Складність:** Часова `max_tours · n · 2^(O(beta · log beta))`.

---

### `latgeom_second_theorem_verify`
Обчислює послідовні мінімуми ґратки `λ₁, λ₂, …, λₙ` для заданого тіла `K` та верифікує виконання двосторонньої нерівності другої теореми Мінковського: `(2ⁿ / n!) · det(L) ≤ (∏ λᵢ) · vol(K) ≤ 2ⁿ · det(L)`.

:::tabs
```c
latgeom_status_t latgeom_second_theorem_verify(latgeom_basis_t *basis,
                                               const latgeom_convex_body_t *body,
                                               latgeom_minima_result_t *result);
```
```cpp
namespace latgeom {
[[nodiscard]] std::expected<MinimaVerification, ErrorCode>
verify_second_theorem(const LatticeBasis& basis, const ConvexBody& body);
}
```
:::

| Параметр | Тип | Напрямок | Опис |
|:---|:---|:---:|:---|
| `basis` | `latgeom_basis_t*` | [in] | Базис ґратки. |
| `body` | `const latgeom_convex_body_t*` | [in] | Опукле центрально-симетричне тіло `K`. |
| `result` | `latgeom_minima_result_t*` | [out] | Структура з послідовними мінімумами та прапорцем виконання нерівності. |

- **Передмови:** `basis->is_orthogonalized == true`, `body->dim == basis->dim`.
- **Післяумови:** Заповнено масив `result->lambda` довжини `n` з монотонною умовою `λ₁ ≤ λ₂ ≤ … ≤ λₙ`. Поле `result->satisfies_second_theorem` встановлюється в `true`.
- **Складність:** Часова `O(n · T_SVP(n))`.

---

### `latgeom_packing_density`
Обчислює густину пакування куль (lattice packing density) та оцінює контактне число (kissing number) для поточної ґратки:

:::tabs
```c
latgeom_status_t latgeom_packing_density(const latgeom_basis_t *basis,
                                         double *out_center_density,
                                         double *out_packing_fraction);
```
```cpp
namespace latgeom {
struct PackingDensityResult {
    double center_density{0.0};
    double packing_fraction{0.0};
};

[[nodiscard]] std::expected<PackingDensityResult, ErrorCode>
calculate_packing_density(const LatticeBasis& basis);
}
```
:::

| Параметр | Тип | Напрямок | Опис |
|:---|:---|:---:|:---|
| `basis` | `const latgeom_basis_t*` | [in] | Базис ґратки. |
| `out_center_density` | `double*` | [out] | Центрова густина `δ(L) = (λ₁(L) / 2)ⁿ / det(L)`. |
| `out_packing_fraction` | `double*` | [out] | Частка заповнення простору кульками `Δ(L) = V_n · δ(L)`. |

- **Передмови:** `basis->is_orthogonalized == true`.
- **Післяумови:** Розраховано точну геометричну густину пакування.
- **Складність:** Часова `T_SVP(n)`.

---

### `latgeom_lenstra_transform`
Обчислює афінне геометричне перетворення простору для алгоритму цілочисельного лінійного програмування Ленстри (Lenstra's ILP):

:::tabs
```c
latgeom_status_t latgeom_lenstra_transform(const latgeom_basis_t *basis,
                                           double *out_transform_matrix,
                                           double *out_flatness_width);
```
```cpp
namespace latgeom {
struct LenstraTransformResult {
    std::vector<double> transform_matrix;
    double flatness_width{0.0};
};

[[nodiscard]] std::expected<LenstraTransformResult, ErrorCode>
compute_lenstra_transformation(const LatticeBasis& basis);
}
```
:::

| Параметр | Тип | Напрямок | Опис |
|:---|:---|:---:|:---|
| `basis` | `const latgeom_basis_t*` | [in] | Базис ґратки. |
| `out_transform_matrix` | `double*` | [out] | Матриця деформації `T ∈ ℝ^(n×n)`, що округлює багатогранник. |
| `out_flatness_width` | `double*` | [out] | Товщина найтоншого напрямку багатогранника (ширина за теоремою про пласкість Хінчина). |

- **Передмови:** `basis->is_orthogonalized == true`.
- **Післяумови:** Виконується теорема Хінчина про пласкість: якщо ширина `≤ C(n)`, простір розбивається на скінченну кількість паралельних гіперплощин для рекурсивного перебору.
- **Складність:** Часова `O(n³)`.

---

### `latgeom_pqc_security_estimate`
Оцінює бітову стійкість криптографічної схеми на ґратках (Kyber / Dilithium / Falcon) проти найкращих відомих атак primal/dual BKZ:

:::tabs
```c
latgeom_status_t latgeom_pqc_security_estimate(const latgeom_basis_t *basis,
                                               size_t *out_required_blocksize,
                                               double *out_classical_bits,
                                               double *out_quantum_bits);
```
```cpp
namespace latgeom {
struct PqcSecurityResult {
    size_t required_blocksize{0};
    double classical_bits{0.0};
    double quantum_bits{0.0};
};

[[nodiscard]] PqcSecurityResult estimate_pqc_security(const LatticeBasis& basis) noexcept;
}
```
:::

| Параметр | Тип | Напрямок | Опис |
|:---|:---|:---:|:---|
| `basis` | `const latgeom_basis_t*` | [in] | Базис q-арної ґратки системи. |
| `out_required_blocksize` | `size_t*` | [out] | Мінімальний розмір блоку BKZ `β`, необхідний для злому. |
| `out_classical_bits` | `double*` | [out] | Класична бітова складність `≈ 0.292 · β`. |
| `out_quantum_bits` | `double*` | [out] | Квантова бітова складність з урахуванням алгоритму Ґровера `≈ 0.265 · β`. |

- **Передмови:** `basis->is_orthogonalized == true`.
- **Післяумови:** Розраховано точну оцінку безпеки за моделлю Core-SVP.
- **Складність:** Часова `O(1)`.

---

### `latgeom_diophantine_basis_init`
Створює спеціалізований базис ґратки для одночасних діофантових наближень Діріхле системи дійсних чисел `(α₁, α₂, …, αₙ)` з параметром масштабування `N`:

:::tabs
```c
latgeom_status_t latgeom_diophantine_basis_init(latgeom_basis_t *basis,
                                                size_t n,
                                                const double *alpha,
                                                int64_t n_scale);
```
```cpp
namespace latgeom {
[[nodiscard]] static std::expected<LatticeBasis, ErrorCode>
create_diophantine_basis(std::span<const double> alpha, int64_t n_scale);
}
```
:::

| Параметр | Тип | Напрямок | Опис |
|:---|:---|:---:|:---|
| `basis` | `latgeom_basis_t*` | [out] | Згенерований дескриптор `(n+1)`-вимірної ґратки. |
| `n` | `size_t` | [in] | Кількість дійсних чисел для наближення. |
| `alpha` | `const double*` | [in] | Масив дійсних коефіцієнтів `αᵢ ∈ [0, 1)`. |
| `n_scale` | `int64_t` | [in] | Верхня межа знаменника `N ≥ 1`. |

- **Передмови:** `alpha != NULL`, `n >= 1`, `n_scale >= 1`.
- **Післяумови:** Згенеровано ґратку розмірності `n + 1` з детермінантом `det(L) = 1 / N`. Найкоротший вектор цієї ґратки задає спільний цілий знаменник `q ≤ N` такий, що `max |q αᵢ - pᵢ| ≤ N^(-1/n)`.
- **Складність:** Часова `O(n²)`.

---

### `latgeom_set_cancellation_token`
Встановлює атомарний прапорець скасування для тривалих асинхронних операцій редукції та перебору дерева SVP/CVP:

:::tabs
```c
typedef struct {
    volatile int *cancel_flag;     /* Вказівник на атомарну змінну стану */
    uint64_t check_interval;       /* Інтервал перевірки прапорця (кількість вузлів) */
} latgeom_cancellation_token_t;

void latgeom_set_cancellation_token(latgeom_basis_t *basis,
                                    const latgeom_cancellation_token_t *token);
```
```cpp
namespace latgeom {

struct CancellationToken {
    std::atomic<bool>* flag{nullptr};
    uint64_t check_interval{1000};
};

void set_cancellation_token(LatticeBasis& basis, CancellationToken token) noexcept;

} // namespace latgeom
```
:::

- **Призначення:** Дозволяє фоновим потокам веб-серверів та GUI-додатків коректно переривати виконання трудомістких обчислень без витоку ресурсів. Якщо `*cancel_flag != 0`, функції негайно повертають статус `LATGEOM_ERR_TIMEOUT`.
- **Інтервал опитування:** Значення `check_interval` задає компроміс між накладними витратами на атомарне читання пам'яті та затримкою реагування (рекомендоване значення `1000`–`10000` ітерацій перебору).

## Формати серіалізації та сумісність файлів

Бібліотека надає функції імпорту та експорту базисів у стандартні текстові формати:
- **Формат матриць FPLLL (`.mat` / `.lat`):** Текстовий опис матриці `[ [b_{1,1} ... b_{1,n}] ... [b_{n,1} ... b_{n,n}] ]`, сумісний з утилітами комп'ютерної алгебри SageMath та Magma.
- **Двійковий формат IEEE 754:** Збереження прецизійних розкладів Грама–Шмідта для швидкого відновлення стану редукції без повторних обчислень `O(n³)`.
- **Чисельна валідація стабільності:** Бібліотека автоматично верифікує збереження скалярних добутків при перетвореннях базису для запобігання втрати розрядності чисел з плаваючою комою.

## Конструктори стандартних опуклих тіл

Для зручності користувачів бібліотека надає набір функцій швидкої ініціалізації типових геометричних тіл з автоматичним точним розрахунком їхнього `n`-вимірного об'єму за аналітичними формулами:

1. **Евклідова куля `Bₙ(r)`:**
   Об'єм обчислюється через гамма-функцію: `vol(Bₙ(r)) = (π^(n/2) / Γ(n/2 + 1)) · rⁿ`.
   Ініціалізується функцією `latgeom_body_init_sphere(latgeom_convex_body_t *body, size_t dim, double r)`.
2. **Симетричний паралелепіпед / брус `P = { x : |x_i| ≤ c_i }`:**
   Об'єм дорівнює добутку сторін: `vol(P) = 2ⁿ · ∏_{i=1}ⁿ cᵢ`.
   Ініціалізується функцією `latgeom_body_init_box(latgeom_convex_body_t *body, size_t dim, const double *limits)`.
3. **Крос-політоп (куля в ℓ₁-нормі) `Cₙ(r) = { x : ∑ |x_i| ≤ r }`:**
   Об'єм виражається формулою факторіала: `vol(Cₙ(r)) = (2ⁿ / n!) · rⁿ`.
   Ініціалізується функцією `latgeom_body_init_crosspolytope(latgeom_convex_body_t *body, size_t dim, double r)`.

## Шаблонні концепції та C++20 API

Для забезпечення максимальної швидкості та безпеки типів у мові C++ бібліотека надає набір шаблонних концепцій (concepts), які дозволяють компілятору оптимізувати доступ до матриць і векторів:

:::tabs
```c
/* Для чистого C99 концепції компілятора емулюються через статичні перевірки розмірів типів */
#define LATGEOM_STATIC_ASSERT(cond) _Static_assert(cond, "Type constraint violation")
```
```cpp
namespace latgeom {

template<typename T>
concept LatticeScalar = std::is_integral_v<T> || std::is_floating_point_v<T>;

template<typename M>
concept LatticeMatrix = requires(M m, size_t i, size_t j) {
    { m(i, j) } -> std::convertible_to<double>;
    { m.rows() } -> std::same_as<size_t>;
    { m.cols() } -> std::same_as<size_t>;
};

} // namespace latgeom
```
:::

Ці концепції дозволяють безкоштовно обгортати сторонні контейнери (такі як `Eigen::Matrix`, `std::vector<std::vector<T>>` чи сирі буфери `std::span`) без додаткового копіювання пам'яті.

## Керування користувацькими алокаторами пам'яті

Для вбудованих систем, криптографічних HSM-модулів та високопродуктивних обчислювальних середовищ бібліотека дозволяє повністю перевизначити механізм виділення та звільнення пам'яті:

:::tabs
```c
typedef void* (*latgeom_malloc_fn)(size_t size, size_t alignment);
typedef void (*latgeom_free_fn)(void *ptr);

void latgeom_set_allocator(latgeom_malloc_fn custom_malloc, latgeom_free_fn custom_free);
```
```cpp
namespace latgeom {

using MallocFunction = void* (*)(size_t, size_t);
using FreeFunction = void (*)(void*);

void set_memory_allocator(MallocFunction custom_malloc, FreeFunction custom_free) noexcept;

} // namespace latgeom
```
:::

**Вимоги до функцій-алокаторів:**
- Функція `custom_malloc` зобов'язана повертати вказівник, вирівняний щонайменше за параметром `alignment` (зазвичай 64 байти).
- Алокатор повинен бути потокобезпечним, якщо функції `latgeom` викликаються з декількох потоків виконання паралельно.
- Перевизначення алокатора посеред роботи з активними дескрипторами `latgeom_basis_t` веде до невизначеної поведінки (UB); функцію слід викликати одноразово під час ініціалізації процесу.

## Порівняння з промисловими бібліотеками геометрії ґраток

У практичних обчисленнях `liblatgeom` доповнює такі визнані бібліотеки комп'ютерної алгебри:

1. **FPLLL (C++ / Python):** Спеціалізується на високорозрядній редукції великих ґраток (`n ≥ 100`) із плаваючою комою змінної точності (MPFR). `liblatgeom` фокусується на низьких накладних витратах, точній перевірці теореми Мінковського та гарантіях для вбудованих систем.
2. **NTL (Number Theory Library, Віктор Шоуп):** Надає потужний математичний апарат для поліномів та великих цілих чисел. `liblatgeom` пропонує сучасніший інтерфейс C++20 (`std::span`, `std::expected`) та пряму сумісність з чистим ABI C.
3. **FLINT (Fast Library for Number Theory):** Використовує асемблерні оптимізації для модулярної арифметики. `liblatgeom` зосереджена на геометричних інваріантах опуклих тіл та послідовних мінімумах.

## Повний приклад використання мовами C та C++

Нижче наведено робочі приклади використання бібліотеки, які демонструють повний життєвий цикл роботи: створення дескриптора ґратки, виконання ортогоналізації Грама–Шмідта, перевірку гарантій теореми Мінковського, розв'язання задачі SVP та обчислення двоїстої ґратки.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <inttypes.h>
#include "latgeom.h"

int main(void) {
    /* Базис 3-вимірної ґратки */
    const size_t dim = 3;
    const int64_t raw_matrix[9] = {
        5, 2, 1,
        0, 4, 3,
        1, 1, 6
    };

    latgeom_basis_t basis;
    latgeom_status_t status = latgeom_basis_init(&basis, dim, raw_matrix);
    if (status != LATGEOM_SUCCESS) {
        fprintf(stderr, "Помилка ініціалізації: код %d\n", status);
        return EXIT_FAILURE;
    }

    status = latgeom_basis_orthogonalize(&basis);
    if (status != LATGEOM_SUCCESS) {
        fprintf(stderr, "Помилка ортогоналізації: код %d\n", status);
        latgeom_basis_free(&basis);
        return EXIT_FAILURE;
    }

    printf("=== Інформація про ґратку (liblatgeom) ===\n");
    printf("Розмірність: %zu\n", basis.dim);
    printf("Визначник det(L): %.4f\n", basis.determinant);
    printf("Логарифм визначника ln(det(L)): %.4f\n", basis.log_determinant);
    printf("Дефект ортогональності: %.4f\n", basis.orthogonality_defect);
    printf("Радіус кулі Мінковського R_M: %.4f\n", basis.minkowski_radius);
    printf("Гауссова евристика GH(L): %.4f\n", basis.gaussian_heuristic);

    /* Створення кулі Мінковського для перевірки умови */
    latgeom_convex_body_t ball;
    ball.dim = dim;
    ball.type = LATGEOM_BODY_ELLIPSOID;
    ball.radius = basis.minkowski_radius;
    ball.volume = (4.0 / 3.0) * 3.141592653589793 * basis.minkowski_radius * basis.minkowski_radius * basis.minkowski_radius;

    bool guaranteed = false;
    double ratio = 0.0;
    latgeom_minkowski_check(&basis, &ball, &guaranteed, &ratio);
    printf("Співвідношення об'ємів vol(K) / (2^n * det(L)): %.4f\n", ratio);
    printf("Наявність вузла гарантована теоремою: %s\n", guaranteed ? "ТАК" : "НІ");

    /* Пошук найкоротшого вектора SVP */
    latgeom_svp_result_t svp_res;
    svp_res.coordinates = (int64_t*)malloc(dim * sizeof(int64_t));
    svp_res.vector = (double*)malloc(dim * sizeof(double));

    status = latgeom_svp_solve(&basis, 1000000ULL, &svp_res);
    if (status == LATGEOM_SUCCESS) {
        printf("\nЗнайдено найкоротший вектор v: [ ");
        for (size_t i = 0; i < dim; i++) {
            printf("%.2f ", svp_res.vector[i]);
        }
        printf("]\n");
        printf("Цілі коефіцієнти z: [ ");
        for (size_t i = 0; i < dim; i++) {
            printf("%" PRId64 " ", svp_res.coordinates[i]);
        }
        printf("]\n");
        printf("Довжина ||v|| = lambda_1(L): %.4f\n", svp_res.euclidean_norm);
        printf("Фактор Ерміта: %.4f\n", svp_res.hermite_factor);
        printf("Перевірка теореми: %.4f <= %.4f (%s)\n",
               svp_res.euclidean_norm, basis.minkowski_radius,
               svp_res.euclidean_norm <= basis.minkowski_radius ? "УСПІХ" : "ПОРУШЕННЯ");
        printf("Відвідано вузлів: %" PRIu64 "\n", svp_res.visited_nodes);
    } else {
        fprintf(stderr, "Помилка під час пошуку SVP: код %d\n", status);
    }

    free(svp_res.coordinates);
    free(svp_res.vector);
    latgeom_basis_free(&basis);
    return EXIT_SUCCESS;
}
```
```cpp
#include <iostream>
#include <vector>
#include <span>
#include <iomanip>
#include <expected>
#include <cmath>

namespace latgeom {

enum class ErrorCode {
    InvalidDimension,
    SingularBasis,
    Timeout,
    NotConvex,
    InvalidParameter
};

struct SvpResult {
    std::vector<int64_t> coordinates;
    std::vector<double> vector;
    double norm{0.0};
    double hermite_factor{0.0};
    uint64_t visited_nodes{0};
};

class LatticeBasis {
public:
    static std::expected<LatticeBasis, ErrorCode> create(size_t dim, std::span<const int64_t> matrix) {
        if (dim == 0 || dim > 64 || matrix.size() != dim * dim) {
            return std::unexpected(ErrorCode::InvalidDimension);
        }
        LatticeBasis basis(dim, matrix);
        if (!basis.orthogonalize()) {
            return std::unexpected(ErrorCode::SingularBasis);
        }
        return basis;
    }

    [[nodiscard]] size_t dimension() const noexcept { return dim_; }
    [[nodiscard]] double determinant() const noexcept { return det_; }
    [[nodiscard]] double log_determinant() const noexcept { return log_det_; }
    [[nodiscard]] double minkowski_radius() const noexcept { return minkowski_radius_; }
    [[nodiscard]] double gaussian_heuristic() const noexcept { return gh_; }
    [[nodiscard]] double orthogonality_defect() const noexcept { return orth_defect_; }

    [[nodiscard]] std::expected<SvpResult, ErrorCode> solve_svp(uint64_t max_nodes = 1'000'000) const {
        double best_sq = minkowski_radius_ * minkowski_radius_;
        std::vector<int64_t> best_z(dim_, 0);
        std::vector<double> best_v(dim_, 0.0);
        uint64_t nodes = 0;

        std::vector<int64_t> cur_z(dim_, 0);
        std::vector<double> cur_l(dim_ + 1, 0.0);

        bool success = enumerate(static_cast<int>(dim_) - 1, cur_z, cur_l,
                                 best_sq, best_z, best_v, nodes, max_nodes);
        if (!success) {
            return std::unexpected(ErrorCode::Timeout);
        }

        double norm = std::sqrt(best_sq);
        double hf = norm / std::pow(det_, 1.0 / static_cast<double>(dim_));

        return SvpResult{
            .coordinates = std::move(best_z),
            .vector = std::move(best_v),
            .norm = norm,
            .hermite_factor = hf,
            .visited_nodes = nodes
        };
    }

private:
    LatticeBasis(size_t dim, std::span<const int64_t> matrix)
        : dim_(dim), b_(matrix.begin(), matrix.end()),
          b_star_(dim * dim, 0.0), mu_(dim * dim, 0.0), b_star_sq_(dim, 0.0) {}

    size_t dim_;
    std::vector<int64_t> b_;
    std::vector<double> b_star_;
    std::vector<double> mu_;
    std::vector<double> b_star_sq_;
    double det_{1.0};
    double log_det_{0.0};
    double minkowski_radius_{0.0};
    double gh_{0.0};
    double orth_defect_{1.0};

    bool orthogonalize() {
        det_ = 1.0;
        log_det_ = 0.0;
        double prod_norms = 1.0;

        for (size_t i = 0; i < dim_; ++i) {
            double orig_sq = 0.0;
            for (size_t j = 0; j < dim_; ++j) {
                b_star_[i * dim_ + j] = static_cast<double>(b_[i * dim_ + j]);
                orig_sq += static_cast<double>(b_[i * dim_ + j]) * static_cast<double>(b_[i * dim_ + j]);
            }
            prod_norms *= std::sqrt(orig_sq);

            for (size_t j = 0; j < i; ++j) {
                double dot = 0.0;
                for (size_t k = 0; k < dim_; ++k) {
                    dot += static_cast<double>(b_[i * dim_ + k]) * b_star_[j * dim_ + k];
                }
                double m = dot / b_star_sq_[j];
                mu_[i * dim_ + j] = m;
                for (size_t k = 0; k < dim_; ++k) {
                    b_star_[i * dim_ + k] -= m * b_star_[j * dim_ + k];
                }
            }
            double sq = 0.0;
            for (size_t k = 0; k < dim_; ++k) {
                sq += b_star_[i * dim_ + k] * b_star_[i * dim_ + k];
            }
            if (sq < 1e-12) return false;
            b_star_sq_[i] = sq;
            det_ *= std::sqrt(sq);
            log_det_ += 0.5 * std::log(sq);
        }
        minkowski_radius_ = std::sqrt(static_cast<double>(dim_)) *
                            std::pow(det_, 1.0 / static_cast<double>(dim_));
        gh_ = std::sqrt(static_cast<double>(dim_) / (2.0 * 3.141592653589793 * 2.718281828459045)) *
              std::pow(det_, 1.0 / static_cast<double>(dim_));
        orth_defect_ = prod_norms / det_;
        return true;
    }

    bool enumerate(int k, std::vector<int64_t>& z, std::vector<double>& l,
                   double& best_sq, std::vector<int64_t>& best_z,
                   std::vector<double>& best_v, uint64_t& nodes, uint64_t max_nodes) const {
        if (++nodes > max_nodes) return false;

        if (k < 0) {
            bool non_zero = false;
            for (int64_t val : z) {
                if (val != 0) { non_zero = true; break; }
            }
            if (non_zero && l[0] < best_sq) {
                best_sq = l[0];
                best_z = z;
                best_v.assign(dim_, 0.0);
                for (size_t j = 0; j < dim_; ++j) {
                    for (size_t i = 0; i < dim_; ++i) {
                        best_v[j] += static_cast<double>(z[i]) * static_cast<double>(b_[i * dim_ + j]);
                    }
                }
            }
            return true;
        }

        double c_k = 0.0;
        for (size_t j = static_cast<size_t>(k) + 1; j < dim_; ++j) {
            c_k -= mu_[j * dim_ + k] * static_cast<double>(z[j]);
        }

        int64_t center_z = static_cast<int64_t>(std::round(c_k));
        int64_t step = 0;

        while (true) {
            int64_t cur_z = 0;
            if (step == 0) cur_z = center_z;
            else if (step % 2 == 1) cur_z = center_z + (step + 1) / 2;
            else cur_z = center_z - step / 2;

            double diff = static_cast<double>(cur_z) - c_k;
            double new_l = l[k + 1] + diff * diff * b_star_sq_[k];

            if (new_l >= best_sq) {
                if (step > 1) break;
                ++step;
                continue;
            }

            z[k] = cur_z;
            l[k] = new_l;
            if (!enumerate(k - 1, z, l, best_sq, best_z, best_v, nodes, max_nodes)) {
                return false;
            }
            ++step;
        }
        return true;
    }
};

} // namespace latgeom

int main() {
    constexpr size_t dim = 3;
    const std::vector<int64_t> matrix = {
        5, 2, 1,
        0, 4, 3,
        1, 1, 6
    };

    auto basis_res = latgeom::LatticeBasis::create(dim, matrix);
    if (!basis_res.has_value()) {
        std::cerr << "Не вдалося створити ґратку.\n";
        return 1;
    }

    const auto& basis = *basis_res;
    std::cout << std::fixed << std::setprecision(4);
    std::cout << "=== C++20 інтерфейс liblatgeom ===\n";
    std::cout << "Розмірність простору: " << basis.dimension() << "\n";
    std::cout << "Визначник det(L): " << basis.determinant() << "\n";
    std::cout << "Логарифм визначника: " << basis.log_determinant() << "\n";
    std::cout << "Дефект ортогональності: " << basis.orthogonality_defect() << "\n";
    std::cout << "Радіус Мінковського R_M: " << basis.minkowski_radius() << "\n";
    std::cout << "Гауссова евристика GH(L): " << basis.gaussian_heuristic() << "\n";

    auto svp_res = basis.solve_svp();
    if (svp_res.has_value()) {
        const auto& res = *svp_res;
        std::cout << "\nЗнайдено найкоротший вектор v: [ ";
        for (double val : res.vector) std::cout << val << " ";
        std::cout << "]\n";
        std::cout << "Довжина ||v|| = lambda_1(L): " << res.norm << "\n";
        std::cout << "Фактор Ерміта: " << res.hermite_factor << "\n";
        std::cout << "Перевірка нерівності: " << res.norm << " <= "
                  << basis.minkowski_radius() << " ("
                  << (res.norm <= basis.minkowski_radius() ? "ПІДТВЕРДЖЕНО" : "ПОМИЛКА")
                  << ")\n";
        std::cout << "Відвідано вузлів: " << res.visited_nodes << "\n";
    }

    return 0;
}
```
:::

## Гарантії потокової безпеки та оптимізація продуктивності

1. **Багатопоточність та паралелізм (Thread-Safety):**
   - Усі константні методи C++ класу `LatticeBasis` та C-функції, що приймають `const latgeom_basis_t*`, є строго реентерабельними та безпечними для одночасного паралельного виклику з довільної кількості потоків виконання без блокувань (lock-free read).
   - Модифікація внутрішнього стану базису (наприклад, виклик редукції LLL чи BKZ) вимагає зовнішньої синхронізації (mutex / read-write lock).
2. **Векторизація SIMD та кеш-оптимізація:**
   - Обчислення скалярних добутків у процедурі Грама–Шмідта автоматично векторизується за допомогою інструкцій AVX2 `_mm256_fmadd_pd` або AVX-512 `_mm512_fmadd_pd`. Завдяки вирівнюванню матриць на 64 байти процесор завантажує дані без штрафів за перетин меж кеш-ліній (cache line boundary crossing).
   - Для розрахунку центрів проєкцій у переборі Шнорра–Ейхнера матриця `mu` транспонується в пам'яті так, щоб стовпчики розміщувалися послідовно, забезпечуючи максимальний коефіцієнт влучання в L1D-кеш.
3. **Обмеження на розрядність координат:**
   - Координати вхідної матриці `matrix` не повинні перевищувати за модулем `2⁴⁸`, щоб уникнути переповнення під час розрахунку проміжних сум квадратів у форматі `double`. Для більших коефіцієнтів слід використовувати збірку бібліотеки з підтримкою `__float128` або довгої раціональної арифметики.
4. **Чисельна обумовленість базису:**
   - Якщо матриця базису має гігантське число обумовленості `κ(B) = ‖B‖ · ‖B⁻¹‖ > 10¹⁴`, ортогоналізація MGS може давати чисельні похибки. У таких випадках перед викликом геометричних функцій рекомендується провести попередню редукцію базису `latgeom_lll_reduce()`.
5. **Інваріанти в режимі зневадження (`LATGEOM_DEBUG`):**
   - При компіляції бібліотеки з прапорцем `-DLATGEOM_DEBUG` кожен крок редукції та ортогоналізації автоматично перевіряє ортогональність векторів `|⟨b_i*, b_j*⟩| < 10⁻¹⁰ · ‖b_i*‖ · ‖b_j*‖` та унімодулярність перетворень `|det(U)| = 1`.
