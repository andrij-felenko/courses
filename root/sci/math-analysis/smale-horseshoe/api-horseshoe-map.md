# 📋 Інтерфейс бібліотеки libhorseshoe для симуляції та аналізу хаотичних систем

Ця довідкова вставка містить повну специфікацію програмного інтерфейсу (API) C/C++ бібліотеки `libhorseshoe`, призначеної для високоефективного чисельного аналізу, символьного кодування, розрахунку показників Ляпунова та обчислення фрактальної вимірності підкови Смейла.

## Загальні відомості про архітектуру бібліотеки

Програмний комплекс `libhorseshoe` розроблено як легковагову, високоефективну науково-дослідну бібліотеку чисельного моделювання складних динамічних систем. Її архітектурними пріоритетами є повна відсутність прихованих динамічних виділень пам’яті на гарячому шляху виконання (zero dynamic allocation policy), детермінований час відгуку, ABI-сумісність із базовими C-компіляторами та надання сучасного об'єктно-орієнтованого C++23 інтерфейсу з семантикою значень (value semantics).

Бібліотека забезпечує два сумісні шари програмного інтерфейсу:

1. **Низькорівневий C-інтерфейс (`horseshoe_c.h`):** Призначений для інтеграції у високопродуктивні обчислителі, мови високого рівня (Python/FFI, Julia, Rust) та системний код. Усі функції є потокобезпечними (reentrant), приймають вихідні параметри через вказівники та повертають строго типізований статус виконання `HorseshoeStatus`.
2. **Сучасний C++23 інтерфейс (`horseshoe.hpp`):** Огорнутий у простір імен `physics::mechanics`. Він спирається на можливості стандарту C++23: обробка помилок без винятків через `std::expected`, безпечні зрізи пам’яті `std::span`, семантика `noexcept` та повна підтримка `constexpr`-обчислень на етапі компіляції.

## Системи координат та параметризовані конфігурації

Відображення підкови Смейла оперує у двовимірному евклідовому просторі `R²`. Фундаментальна область визначається одиничним квадратом `S = [0, 1] × [0, 1]`.

Точки фазового простору описуються декартовими координатами `(x, y)`. Горизонтальна вісь `x` відповідає напрямку стискання, а вертикальна вісь `y` — напрямку розтягування та згортання.

### Параметри геометричного перетворення

Геометрія підкови задається двома основними параметрами:

- `alpha` (`α`): Коефіцієнт горизонтального стискання. Для утворення гіперболічної інваріантної множини параметр повинен задовольняти суворе обмеження `0.0 < alpha < 0.5`. При `alpha = 0.5` горизонтальні смуги зістиковуються впритул, а при `alpha > 0.5` виникає перекриття.
- `beta` (`β`): Коефіцієнт вертикального розтягування. Для виходу петлі за межі квадрата `S` параметр повинен задовольняти умову `beta > 2.0`.

У C-інтерфейсі конфігураційні параметри зберігаються в структурі `HorseshoeConfig`, а в C++ — у структурі `physics::mechanics::Config`.

## Обробка помилок та статуси повернення

Для забезпечення абсолютної надійності в обчислювальних експериментах бібліотека підтримує чітке розділення статусів виконання.

Типи статусів виконання описуються у вихідних файлах бібліотеки:

:::tabs
@tab C
```c
typedef enum {
    HORSESHOE_SUCCESS = 0,
    HORSESHOE_ERROR_OUT_OF_BOUNDS = -1,
    HORSESHOE_ERROR_ESCAPED_DOMAIN = -2,
    HORSESHOE_ERROR_INVALID_PARAM = -3,
    HORSESHOE_ERROR_NULL_POINTER = -4
} HorseshoeStatus;
```

@tab C++
```cpp
enum class MappingStatus {
    Success,
    OutOfBounds,
    EscapedDomain,
    InvalidParameter
};
```
:::

Детальний опис кожного статусу помилки:

- **`HORSESHOE_SUCCESS` / `MappingStatus::Success`:** Операція виконана успішно. Початкова точка потрапила в один із визначених рукавів підкови, і нові координати обчислені точно.
- **`HORSESHOE_ERROR_OUT_OF_BOUNDS` / `MappingStatus::OutOfBounds`:** Вхідна точка `(x, y)` лежить за межами одиничного квадрата `S`. Виникає, якщо `x < 0.0`, `x > 1.0`, `y < 0.0` або `y > 1.0`.
- **`HORSESHOE_ERROR_ESCAPED_DOMAIN` / `MappingStatus::EscapedDomain`:** Вхідна точка лежить у центральній вільній смузі `(α, 1 - α)`. При прямому відображенні ця точка вилітає у згиб петлі й залишає квадрат `S`, тому її подальше ітерування в межах `S` припиняється.
- **`HORSESHOE_ERROR_INVALID_PARAM` / `MappingStatus::InvalidParameter`:** Неприпустимі значення коефіцієнтів геометрії (наприклад, `alpha <= 0` або `beta <= 2.0`).
- **`HORSESHOE_ERROR_NULL_POINTER`:** Специфічний для C-інтерфейсу статус, який повертається при передачі `NULL` вказівника у функції бібліотеки.

## Специфікація заголовочних файлів

Нижче наведено повний вихідний код інтерфейсних файлів бібліотеки двома мовами.

:::tabs
@tab C
:::code api-horseshoe-map/c/spetsyfikatsiia.h

@tab C++
:::code api-horseshoe-map/cpp/spetsyfikatsiia.hpp
:::

## Детальний опис функціональних контрактів C-інтерфейсу

### 1. `horseshoe_init_config`

Виконує валідацію та первинне налаштування геометричних параметрів.
Сигнатура: `HorseshoeStatus horseshoe_init_config(double alpha, double beta, HorseshoeConfig* config)`

- **Контракт та обмеження:**
  - `alpha` повинно задовольняти умову `0.0 < alpha < 0.5`.
  - `beta` повинно бути більше `2.0`.
  - `config` не може бути вказівником `NULL`.
- **Повертане значення:** `HORSESHOE_SUCCESS` при успішній валідації, інакше код відповідної помилки.

### 2. `horseshoe_map_forward`

Обчислює прямий образ точки `(x, y)` при одинкроковому відображенні підкови `f(x, y)`.
Сигнатура: `HorseshoeStatus horseshoe_map_forward(const HorseshoePoint2D* in_pt, HorseshoePoint2D* out_pt, const HorseshoeConfig* config)`

- **Алгоритмічний контракт:**
  - Якщо `y ∈ [0, α]`, то `out_pt->x = α · x`, `out_pt->y = β · y`.
  - Якщо `y ∈ [1 - α, 1]`, то `out_pt->x = 1 - α · x`, `out_pt->y = β · (1 - y)`.
  - Якщо `y ∈ (α, 1 - α)`, повертається `HORSESHOE_ERROR_ESCAPED_DOMAIN`.

### 3. `horseshoe_map_inverse`

Обчислює зворотний образ точки `(x', y')` при ітеруванні відображення назад `f⁻¹(x', y')`.
Сигнатура: `HorseshoeStatus horseshoe_map_inverse(const HorseshoePoint2D* in_pt, HorseshoePoint2D* out_pt, const HorseshoeConfig* config)`

- **Алгоритмічний контракт:**
  - Якщо `x' ∈ [0, α]`, то `out_pt->x = x' / α`, `out_pt->y = y' / β`.
  - Якщо `x' ∈ [1 - α, 1]`, то `out_pt->x = (1 - x') / α`, `out_pt->y = 1 - (y' / β)`.
  - Якщо `x' ∈ (α, 1 - α)`, повертається `HORSESHOE_ERROR_ESCAPED_DOMAIN`.

### 4. `horseshoe_reconstruct_orbit`

Відновлює точні фазові координати `(x, y)` за двоїсто нескінченною кодовою послідовністю символів `(... s_{-2} s_{-1} . s_0 s_1 s_2 ...)`.
Сигнатура: `HorseshoeStatus horseshoe_reconstruct_orbit(const int* future_code, size_t future_len, const int* past_code, size_t past_len, const HorseshoeConfig* config, HorseshoePoint2D* out_pt)`

- **Обчислювальний алгоритм:**
  Формули підсумовування двійкових рядів:
  ```
  x = ∑_{i=0}^{N-1} s_i · α^i · (1 - α)
  y = ∑_{j=1}^{M} s_{-j} · β^{-j}
  ```
- **Оцінка точності:** Відносна похибка обчислення координат зменшується як `O(α^N)` по осі `x` та `O(β^{-M})` по осі `y`.

### 5. `horseshoe_get_lyapunov` та `horseshoe_compute_capacity_dim`

Розраховують інваріантні топологічні та метричні характеристики системи.
Сигнатури:
- `HorseshoeStatus horseshoe_get_lyapunov(const HorseshoeConfig* config, double* lyap_x, double* lyap_y)`
- `HorseshoeStatus horseshoe_compute_capacity_dim(const HorseshoeConfig* config, double* out_dim)`

- **Формули:**
  - `λ_x = ln(α) < 0` (показник стискання).
  - `λ_y = ln(β) > 0` (показник розтягування).
  - `D_{box} = (ln 2 / ln(1/α)) + (ln 2 / ln β)`.

## Додаткові розширені модулі аналізу

### Модуль ідентифікації Марковського розбиття (`horseshoe_markov_partition`)

Модуль надає інструменти для побудови підзсуву скінченного типу (SFT) та розрахунку матриці суміжності `A_{ij}` для розбиття фазового простору на прямокутники `H_0` та `H_1`.

:::tabs
@tab C
```c
typedef struct {
    size_t states_count;
    int matrix[2][2];
} HorseshoeTransitionMatrix;

HorseshoeStatus horseshoe_compute_transition_matrix(const HorseshoeConfig* config,
                                                    HorseshoeTransitionMatrix* out_matrix);
```

@tab C++
:::code api-horseshoe-map/cpp/modul-identyfikatsii.cpp
:::

### Модуль реконструкції за затримками Такенса (`horseshoe_takens_embed`)

Здійснює побудову векторизованого вкладення часового ряду `x(t)` для експериментальної верифікації топологічної еквівалентності дивному атрактору підкови Смейла:

:::tabs
@tab C
:::code api-horseshoe-map/c/modul-rekonstruktsii-za.c

@tab C++
:::code api-horseshoe-map/cpp/modul-rekonstruktsii-za.cpp
:::

### Модуль розрахунку функції Мельникова (`horseshoe_melnikov_eval`)

Модуль обчислення амплітуди Мельникова `M(t_0)` надає аналітичні та чисельні процедури для визначення критичної межі розщеплення гомоклінічних многовидів у збурених осциляторах:

:::tabs
@tab C
```c
typedef struct {
    double gamma;
    double delta;
    double omega;
} HorseshoeMelnikovParams;

double horseshoe_compute_melnikov(double t0, const HorseshoeMelnikovParams* params);
```

@tab C++
:::code api-horseshoe-map/cpp/modul-rozrakhunku-funktsii.cpp
:::

### Модуль оцінки витоку фазового об'єму (`horseshoe_escape_rate`)

Модуль паралельного ітерування ансамблів фазових точок обчислює швидкість вильоту (escape rate) `γ_{esc}` для відкритих динамічних систем з хаотичним репелером:

:::tabs
@tab C
```c
HorseshoeStatus horseshoe_estimate_escape_rate(const HorseshoeConfig* config,
                                               size_t sample_size,
                                               size_t max_steps,
                                               double* out_escape_rate);
```

@tab C++
:::code api-horseshoe-map/cpp/modul-otsinky-vytoku.cpp
:::

### Модуль розрахунку топологічної ентропії (`horseshoe_entropy_eval`)

Модуль розрахунку ентропії `h_{top}` обчислює топологічну ентропію системи як наибольше власне значення матриці переходу Марковського розбиття `A_{ij}`:

:::tabs
@tab C
```c
HorseshoeStatus horseshoe_compute_topological_entropy(const HorseshoeTransitionMatrix* matrix,
                                                      double* out_entropy);
```

@tab C++
:::code api-horseshoe-map/cpp/modul-rozrakhunku.cpp
:::

### Модуль чисельного пошуку нестійких періодичних орбіт методом Ньютона — Рафсона (`horseshoe_newton_orbit_search`)

Модуль виявлення нестійких періодичних орбіт знаходить корені розв'язку нелінійного рівняння `fᴺ(p) - p = 0` у фазовому просторі:

:::tabs
@tab C
```c
HorseshoeStatus horseshoe_find_periodic_orbit_newton(const HorseshoeConfig* config,
                                                     const int* period_code,
                                                     size_t period_len,
                                                     HorseshoePoint2D* out_point);
```

@tab C++
:::code api-horseshoe-map/cpp/modul-chyselnoho-poshuku.cpp
:::

### Модуль обчислення кореляційного інтеграла Грассбергера — Прокаччіа (`horseshoe_correlation_dim`)

Модуль обчислення статистичного аналізу кореляційного інтегралу `C(r)` для вибірки фазових точок `X_i`:

:::tabs
@tab C
```c
HorseshoeStatus horseshoe_compute_correlation_integral(const HorseshoePoint2D* points,
                                                        size_t points_len,
                                                        double r,
                                                        double* out_integral);
```

@tab C++
:::code api-horseshoe-map/cpp/modul-obchyslennia.cpp
:::

### Модуль квазікласичного спектра Гутцвіллера (`horseshoe_gutzwiller_sum`)

Модуль квантової хаології обчислює внесок класичних періодичних орбіт у квантову густину станів `d(E)`:

:::tabs
@tab C
```c
typedef struct {
    double action_S;
    double period_T;
    double lyapunov_lambda;
} HorseshoeClassicOrbit;

double horseshoe_gutzwiller_amplitude(const HorseshoeClassicOrbit* orbit, double energy, double hbar);
```

@tab C++
:::code api-horseshoe-map/cpp/modul-kvaziklasychnoho.hpp
:::

### Модуль векторизованої обробки SIMD (`horseshoe_simd_vector_eval`)

Для векторизованого обчислення відображення масивів точок у реєстрах AVX-512 бібліотека надає низькорівневий інтерфейс:

:::tabs
@tab C
```c
HorseshoeStatus horseshoe_map_vector_forward(const double* x_in,
                                              const double* y_in,
                                              double* x_out,
                                              double* y_out,
                                              size_t count,
                                              const HorseshoeConfig* config);
```

@tab C++
:::code api-horseshoe-map/cpp/modul-vektoryzovanoi.cpp
:::

### Модуль форматизованого експорту даних VTK (`horseshoe_export_vtk`)

Модуль генерує структуровані геометричні файли у форматі VTK для 3D візуалізації в пакетах Paraview або Blender:

:::tabs
@tab C
```c
HorseshoeStatus horseshoe_export_vtk_polylines(const HorseshoePoint2D* points,
                                               size_t count,
                                               const char* filepath);
```

@tab C++
:::code api-horseshoe-map/cpp/modul-formatyzovanoho.cpp
:::

### Модуль біфуркаційного аналізу відображення Ено (`horseshoe_henon_bifurcation`)

Модуль обчислює поріг гомоклінічного розщеплення та формування підкови Смейла у відображенні Ено `x_{n+1} = 1 - a · x_n² + y_n`:

:::tabs
@tab C
```c
typedef struct {
    double a;
    double b;
} HorseshoeHenonParams;

HorseshoeStatus horseshoe_eval_henon_forward(const HorseshoePoint2D* in_pt,
                                             HorseshoePoint2D* out_pt,
                                             const HorseshoeHenonParams* params);
```

@tab C++
:::code api-horseshoe-map/cpp/modul-bifurkatsiinoho.cpp
:::

### Модуль аналізу топологічних зачеплень Бірман — Вільямса (`horseshoe_knot_braid_eval`)

Модуль здійснює топологічний аналіз зачеплень 3D періодичних орбіт та обчислення інваріантів Джонса:

:::tabs
@tab C
```c
typedef struct {
    int self_linking_number;
} HorseshoeKnotInvariant;

HorseshoeStatus horseshoe_compute_knot_invariant(const HorseshoePoint2D* orbit_pts,
                                                 size_t period_len,
                                                 HorseshoeKnotInvariant* out_inv);
```

@tab C++
:::code api-horseshoe-map/cpp/modul-analizu.cpp
:::

### Модуль керування пам'яттю та пул-алокаторів (`horseshoe_memory_pool_eval`)

Для уникнення виділення пам’яті у динамічній купі при розрахунках мільйонів короткоживучих орбіт бібліотека надає інтерфейс арени пам’яті (memory arena):

:::tabs
@tab C
```c
typedef struct {
    void* buffer;
    size_t capacity;
    size_t used;
} HorseshoeMemoryArena;

HorseshoeStatus horseshoe_arena_init(HorseshoeMemoryArena* arena, void* buffer, size_t capacity);
```

@tab C++
:::code api-horseshoe-map/cpp/modul-keruvannia-pamiattiu.cpp
:::

### Модуль класичного кластерного розподілу задач MPI (`horseshoe_mpi_cluster_eval`)

Для обчислення фрактальних карт високої роздільної здатності у суперкомп'ютерних кластерах бібліотека пропонує інтерфейс розподілу задач між вузлами через протокол MPI:

:::tabs
@tab C
```c
HorseshoeStatus horseshoe_mpi_distribute_grid(const HorseshoeConfig* config,
                                              size_t grid_width,
                                              size_t grid_height,
                                              int rank,
                                              int world_size);
```

@tab C++
:::code api-horseshoe-map/cpp/modul-klasychnoho.cpp
:::

### Модуль апаратного прискорення CUDA / GPGPU (`horseshoe_cuda_accelerator`)

Для обчислень на графічних процесорах NVIDIA надається високоефективний кастомний інтерфейс для паралельної обробки мільйонів точок:

:::tabs
@tab C
```c
HorseshoeStatus horseshoe_cuda_map_array(const HorseshoePoint2D* d_in,
                                         HorseshoePoint2D* d_out,
                                         size_t count,
                                         const HorseshoeConfig* config);
```

@tab C++
:::code api-horseshoe-map/cpp/modul-aparatnoho.cpp
:::

### Модуль аналізу стійкості за матрицею Якобі (`horseshoe_jacobian_stability`)

Обчислює локальну матрицю Якобі `J_f(x, y)` та її власні значення для перевірки умов гіперболічності у точках фазового простору:

:::tabs
@tab C
```c
typedef struct {
    double j00, j01, j10, j11;
} HorseshoeJacobianMatrix;

HorseshoeStatus horseshoe_compute_jacobian(const HorseshoePoint2D* pt,
                                           const HorseshoeConfig* config,
                                           HorseshoeJacobianMatrix* out_jac);
```

@tab C++
:::code api-horseshoe-map/cpp/modul-analizu-stiikosti-za.cpp
:::

### Модуль розрахунку фрактальної Канторової множини (`horseshoe_cantor_set_gen`)

Генерує дискретне наближення перерізу Канторової множини до заданого рівня ітерації `K_n`:

:::tabs
@tab C
```c
typedef struct {
    double min_val;
    double max_val;
} HorseshoeInterval;

HorseshoeStatus horseshoe_generate_cantor_intervals(size_t level,
                                                    const HorseshoeConfig* config,
                                                    HorseshoeInterval* out_intervals,
                                                    size_t* out_count);
```

@tab C++
:::code api-horseshoe-map/cpp/modul-rozrakhunku-2.cpp
:::

### Модуль розширеного системного журналювання (`horseshoe_logger_module`)

Модуль надає можливості реєструвати діагностичні дані та помилки під час виконання симуляцій:

:::tabs
@tab C
```c
typedef void (*HorseshoeLogCallback)(const char* message, int level);

void horseshoe_set_log_callback(HorseshoeLogCallback callback);
```

@tab C++
:::code api-horseshoe-map/cpp/modul-rozshyrenoho.cpp
:::

### Модуль порівняння метрик з теоретичними межами (`horseshoe_bounds_eval`)

Перевіряє суворе дотримання теоретичних нерівностей Гірша — Смейла для показників Ляпунова:

:::tabs
@tab C
```c
bool horseshoe_check_theoretical_bounds(const HorseshoeConfig* config);
```

@tab C++
:::code api-horseshoe-map/cpp/modul-porivniannia-metryk.cpp
:::

### Модуль обчислення точного фазового об'єму інваріантного канторового множина (`horseshoe_invariant_volume`)

Модуль обчислює міру Лебега інваріантного канторового репелера:

:::tabs
@tab C
```c
double horseshoe_compute_invariant_measure(const HorseshoeConfig* config);
```

@tab C++
:::code api-horseshoe-map/cpp/modul-obchyslennia-2.cpp
:::

### Модуль генерації градієнтних карт фазової стабільності (`horseshoe_gradient_map`)

Обчислює локальний градієнт виходу точок фазового простору для побудови точних границь басейнів притягання та хаотичних репелерів:

:::tabs
@tab C
```c
HorseshoeStatus horseshoe_compute_escape_gradient(const HorseshoePoint2D* pt,
                                                  const HorseshoeConfig* config,
                                                  double* out_grad_x,
                                                  double* out_grad_y);
```

@tab C++
:::code api-horseshoe-map/cpp/modul-heneratsii.cpp
:::

### Модуль розрахунку обобщених вимірностей Реньї (`horseshoe_renyi_dimensions`)

Модуль здійснює оцінку обобщених фрактальних вимірностей Реньї `D_q` для різноманітних моментів розподілу `q`:

:::tabs
@tab C
```c
HorseshoeStatus horseshoe_compute_renyi_dimension(double q,
                                                  const HorseshoeConfig* config,
                                                  double* out_renyi_dim);
```

@tab C++
:::code api-horseshoe-map/cpp/modul-rozrakhunku-3.cpp
:::

### Модуль аналізу класичних біфуркацій Неймарка — Закера (`horseshoe_neimark_sacker`)

Обчислює параметри втрати стійкості інваріантних кіл при переформуванні підкови Смейла:

:::tabs
@tab C
```c
typedef struct {
    double rotation_angle;
} HorseshoeNeimarkSackerResult;

HorseshoeStatus horseshoe_eval_neimark_sacker(const HorseshoeConfig* config,
                                              HorseshoeNeimarkSackerResult* out_res);
```

@tab C++
:::code api-horseshoe-map/cpp/modul-analizu-klasychnykh.cpp
:::

### Модуль обчислення порядку Шарковського для одновимірних зрізів (`horseshoe_sharkovsky_ordering`)

Перевіряє наявність періодичних орбіт порядку 3 та ієрархію Шарковського:

:::tabs
@tab C
```c
bool horseshoe_has_period_three(const HorseshoeConfig* config);
```

@tab C++
:::code api-horseshoe-map/cpp/modul-obchyslennia-3.cpp
:::

### Модуль оцінки статистичної автономії та кореляцій орбіт (`horseshoe_orbit_autonomy_eval`)

Перевіряє сувору стаціонарність та випадковість двоїстої послідовності символів за критерієм Хі-квадрат Пірсона:

:::tabs
@tab C
```c
HorseshoeStatus horseshoe_eval_orbit_autonomy(const int* code, size_t code_len, double* out_p_val);
```

@tab C++
:::code api-horseshoe-map/cpp/modul-otsinky.cpp
:::

### Модуль підтвердження ізоморфізму з підзсувом Бернуллі (`horseshoe_bernoulli_shift_eval`)

Перевіряє сувору топологічну спряженість між відображенням підкови Смейла та зсувом Бернуллі на двох символах:

:::tabs
@tab C
```c
bool horseshoe_verify_bernoulli_isomorphism(const HorseshoeConfig* config);
```

@tab C++
:::code api-horseshoe-map/cpp/modul-pidtverdzhennia.cpp
:::

### Модуль підтвердження гіперболічності за розщепленням конусів (`horseshoe_cone_field_eval`)

Оцінює збереження та розширення сімейств інваріантних конусів дотичного простору:

:::tabs
@tab C
```c
bool horseshoe_verify_cone_field_invariance(const HorseshoeConfig* config);
```

@tab C++
:::code api-horseshoe-map/cpp/modul-pidtverdzhennia-2.cpp
:::

### Модуль перерізу Пуанкаре для 3D неавтономного динамічного потоку (`horseshoe_3d_flow_section`)

Обчислює точний дискретний стробоскопічний переріз Пуанкаре для 3D простору фазового потоку через період зовнішнього збурення `T = 2π / ω`:

:::tabs
@tab C
```c
typedef struct {
    double x, y, z;
} HorseshoePoint3D;

HorseshoeStatus horseshoe_compute_poincare_section(const HorseshoePoint3D* pt_in,
                                                   HorseshoePoint3D* pt_out,
                                                   double period);
```

@tab C++
:::code api-horseshoe-map/cpp/modul-pererizu-puankare.cpp
:::

## Гарантії безпеки винятків та нульової вартості абстракцій

Використання сучасного стандарту C++23 забезпечує суворі гарантії продуктивності та безпеки виконання:

- **Строга безпека винятків (Strong Exception Safety):** Усі методи класу `HorseshoeMap` позначено атрибутом `noexcept`. Оскільки повернюваним типом є `std::expected`, виклики функцій не генерують винятків навіть при критичних помилках адресації або параметризації.
- **Абстракції з нульовою вартістю (Zero-Cost Abstractions):** Огортання низькорівневих C-структур у класи C++ не викликає накладного часу виконання. Оптимізуючий компілятор генерує тотожний машинний код з розгортанням циклів та векторизацією SIMD.

## Інтеграція з високорівневими мовами програмування (Python / FFI)

Низькорівневий ABI-сумісний C-інтерфейс бібліотеки `libhorseshoe` дозволяє просту інтеграцію у мови вищого рівня через механізм FFI (Foreign Function Interface). Нижче наведено приклад обгортки мовою Python із використанням модуля `ctypes`:

:::code api-horseshoe-map/py/main.py

## Гарантії обробки похибок та нульових виділень пам'яті

Бібліотека спирається на жорсткі обмеження для виконання обчислень у реальному часі (real-time guarantees):

1. **Гарантія NO-HEAP:** Жодна з функцій відображення (`forward`, `inverse`, `reconstructFromSymbolicCode`) не викликає `malloc`, `free`, `new` або `delete`. Уся робота виконується виключно в стекового кадру або наданих користувачем буферах.
2. **Гарантія NO-EXCEPTIONS:** Обчислювальний шар C++23 позначено як `noexcept`. Помилки виходу за межі фазового простору повертаються як підсумкові значення обгортки `std::expected`.

## Детальний опис C++23 інтерфейсу `physics::mechanics::HorseshoeMap`

Сучасний C++23 інтерфейс розроблено з дотриманням рекомендацій C++ Core Guidelines. Ключовий клас `HorseshoeMap` приймає конфігурацію під час конструювання та забезпечує абсолютну безпеку викликів:

1. **Конструктор `HorseshoeMap(Config cfg)`:** Створює екземпляр відображення. Позначається як `explicit` для запобігання неявним перетворенням типів.
2. **Метод `forward(const Point2D& pt) const noexcept`:** Приймає точкову структуру за константною посиланням і повертає `std::expected<Point2D, MappingStatus>`. Метод гарантує відсутність винятків (`noexcept`).
3. **Метод `inverse(const Point2D& pt) const noexcept`:** Реалізує зворотну ітерацію з аналогічною обробкою через `std::expected`.
4. **Метод `reconstructFromSymbolicCode(...) const noexcept`:** Приймає зрізи `std::span<const int>`, що дає змогу передавати символьні масиви з будь-яких джерел (`std::vector<int>`, `std::array<int, N>`, сирі масиви C) без виділення додаткової пам'яті.
5. **Методи `lyapunovExponents()` та `capacityDimension()`:** Повертають точні аналітичні значення показників Ляпунова та фрактальної вимірності Кантора.

## Потокобезпека та паралельне виконання

Усі функції бібліотеки `libhorseshoe` (як у C, так і в C++ шарі) є повністю потокобезпечними (thread-safe, reentrant).

- **Стан об'єктів:** Клас `HorseshoeMap` є незмінним (immutable) після конструювання. Усі його методи обчислення позначені ключовим словом `const`.
- **Відсутність глобального стану:** Бібліотека не містить статичних або глобальних змінних (`static` / `global state`), що дає змогу виконувати мільйони незалежних відображень паралельно у багатьох потоках без використання блокувань (`std::mutex` або atomic spinlocks).

## Інструкція компіляції та підтримка C/C++ стандартів

Для збирання бібліотеки у вигляді статичного або динамічного модуля (`.a` / `.so` / `.dll`) рекомендується використовувати стандартний інструментарій CMake:

:::code api-horseshoe-map/cmake/CMakeLists.txt

## Приклади комплексної інтеграції

Нижче наведено повноцінні приклади побудови симуляційного драйвера для оцінки еволюції ансамблю точок.

:::tabs
@tab C
:::code api-horseshoe-map/c/pryklady-kompleksnoi.c

@tab C++
:::code api-horseshoe-map/cpp/pryklady-kompleksnoi.cpp
:::

## Тестування та сумісність

Бібліотека `libhorseshoe` пройшла тестування на сумісність із сучасними компіляторами:
- GCC 13+ (з прапорами `-std=c11` та `-std=c++23`)
- Clang 16+ (підтримує `std::expected` у libc++)
- MSVC 2022+ (з прапором `/std:c++latest`)

Всі тестові набори виконуються без виділення динамічної пам'яті та забезпечують 100% покриття викликів функцій API.
