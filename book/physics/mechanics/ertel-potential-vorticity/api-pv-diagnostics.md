# 📋 Інтерфейс модуля геофізичної вихореносної діагностики

Цей інтерфейс визначає публічний контракт C/C++ бібліотеки `gfd_pv_diag`, яка призначена для виконання тривимірної вихореносної діагностики, обчислення потенціальної вихореності Ертеля, оцінки бароклінної стійкості та підготовки полів для інверсійних моделей у геофізичній гідродинаміці.

Модуль проектовано для використання у високопродуктивних обчислювальних комплексах прогнозування погоди, океанографічних діагностичних системах та моделях аналізу кліматичних даних.

## Філософія проекту та архітектура пам'яті

Обчислення потенціальної вихореності на тривимірних сітках реального атмосферного або океанічного стану вимагає обробки масивів обсягом у сотні мільйонів вузлів. Для забезпечення максимальної обчислювальної ефективності та мінімізації накладних витрат на виділення пам'яті, бібліотека `gfd_pv_diag` дотримується наступних проектуальних принципів:

1. **Відсутність прихованого виділення купи (Zero-allocation path)**. Основні розрахункові функції приймають попередньо виділені буфери для вихідних полів. Це дозволяє уникнути системних викликів `malloc` або `new` усередині часових циклів обчислювального ядра моделі.
2. **Уніфікована підтримка довільних кроків індексування (Strided access)**. Структури полів не вимагають строго неперервного розташування даних у пам'яті. Параметри `stride_x`, `stride_y`, `stride_z` дозволяють обробляти зрізи 4D масивів (наприклад, часових серій або ансамблів) без копіювання даних.
3. **Потокова безпека та відсутність глобального стану (Reentrancy)**. Усі функції бібліотеки є чистими (reentrant) і не використовують статичних або глобальних змінних. Модуль можна безпечно викликати з паралельних потоків OpenMP, POSIX threads або в середовищі MPI.
4. **Уніфікований контроль фізичних одиниць**. Модуль підтримує як стандартні одиниці SI (`м²·с⁻¹·К·кг⁻¹`), так і метеорологічні одиниці потенціальної вихореності (PVU). Конвертація здійснюється масштабувальними множниками без втрати точності плаваючої крапки.

## Константи та фізичні параметри

У таблиці нижче наведено базові фізичні константи, що використовуються за замовчуванням у розрахунках:

| Назва константи | Фізичне значення | Одиниця вимірювання | Фізичний зміст та призначення |
| :--- | :--- | :--- | :--- |
| `GFD_PVU_FACTOR` | `1.0e-6` | `м²·с⁻¹·К·кг⁻¹` | Стандартна метеорологічна одиниця PVU (Pot. Vorticity Unit) |
| `GFD_OMEGA_EARTH` | `7.292115e-5` | `рад/с` | Кутова швидкість обертання Землі навколо власної осі |
| `GFD_DEFAULT_DENSITY` | `1.225` | `кг/м³` | Референсна густина сухого повітря при стандартному тиску |
| `GFD_R_DRY` | `287.058` | `Дж/(кг·К)` | Питома газова стала сухого повітря у стандартній атмосфері |
| `GFD_CP_DRY` | `1004.67` | `Дж/(кг·К)` | Ізобарна теплоємність сухого повітря |
| `GFD_P0_STANDARD` | `100000.0` | `Па` | Стандартний reference-тиск для обчислення потенціальної температури |

## Коди помилок та статус виконання

Усі функції публічного API повертають цілочисельний статус `gfd_status_t`. Значення `0` позначає успішне завершення операції. Від'ємні значення вказують на конкретні помилки ініціалізації, параметрів або обчислень.

| Код помилки | Числове значення | Детальний опис причини виникнення |
| :--- | :--- | :--- |
| `GFD_SUCCESS` | `0` | Операцію виконано успішно без зауважень |
| `GFD_ERR_NULL_POINTER` | `-1` | Один із обов'язкових вказівників на структуру або масив є `NULL` |
| `GFD_ERR_INVALID_DIM` | `-2` | Розміри сітки `nx`, `ny` або `nz` менші за мінімальний поріг (`< 3`) |
| `GFD_ERR_SPAN_MISMATCH` | `-3` | Переданий розрахунковий буфер має розмір, що не відповідає конфігурації сітки |
| `GFD_ERR_ZERO_DENSITY` | `-4` | У вузлі сітки виявлено від'ємну або близьку до нуля густину (`ρ <= 0`) |
| `GFD_ERR_BAD_SPACING` | `-5` | Кроки сітки `dx`, `dy`, `dz` є від'ємними або дорівнюють нулю |
| `GFD_ERR_BOUNDARY_OUT` | `-6` | Запит за межі географічної або просторової області сітки |
| `GFD_ERR_UNSUPPORTED_BC` | `-7` | Задано комбінацію граничних умов, яка не підтримується цим ядром |

## Опис структур даних API

### 1. Геометрія сітки `gfd_grid_t`

Структура `gfd_grid_t` описує геометричні розміри, просторові кроки дискретизації та географічну орієнтацію обчислювальної області.

:::tabs
```c
typedef enum {
    GFD_GRID_CARTESIAN = 0, /* Декартова прямокутна сітка в метричних координатах */
    GFD_GRID_F_PLANE   = 1, /* Наближення f-площини (f = f0 = const) */
    GFD_GRID_BETA_PLANE= 2, /* Наближення beta-площини (f = f0 + beta * y) */
    GFD_GRID_SPHERICAL = 3  /* Сферичні географічні координати (довгота λ, широта φ) */
} gfd_grid_type_t;

typedef struct {
    int nx;                 /* Кількість вузлів уздовж вісі X (довгота / східний напрямок) */
    int ny;                 /* Кількість вузлів уздовж вісі Y (широта / північний напрямок) */
    int nz;                 /* Кількість вузлів уздовж вісі Z (висота / вертикаль) */
    double dx;              /* Просторовий крок сітки за X (метри або градуси довготи) */
    double dy;              /* Просторовий крок сітки за Y (метри або градуси широти) */
    double dz;              /* Просторовий крок сітки за Z (метри або паскалі) */
    double f0;              /* Базовий параметр Коріоліса для f-площини (1/с) */
    double beta;            /* Меридіональний градієнт параметра Коріоліса df/dy (1/(м·с)) */
    double ref_lat;         /* Опорна широта для центра області (градуси) */
    gfd_grid_type_t type;   /* Режим координатної системи сітки */
} gfd_grid_t;
```
```cpp
enum class GridType {
    Cartesian = 0,
    FPlane    = 1,
    BetaPlane = 2,
    Spherical = 3
};

struct Grid {
    int nx{0};
    int ny{0};
    int nz{0};
    double dx{1000.0};
    double dy{1000.0};
    double dz{100.0};
    double f0{1e-4};
    double beta{1.6e-11};
    double ref_lat{45.0};
    GridType type{GridType::FPlane};
};
```
:::

Детальний опис полів `gfd_grid_t`:
- `nx`, `ny`, `nz`: Кількість вузлів дискретизації. Мінімально припустиме значення для кожного виміру дорівнює `3`, оскільки внутрішні різниці вимагають щонайменше одного центрального вузла та двох сусідніх.
- `dx`, `dy`, `dz`: Просторові кроки сітки. Для декартової сітки `dx` та `dy` задаються у метрах. Для сферичної сітки `dx` та `dy` задаються у кутових градусах, а вказівник на географічні широти використовується для обчислення локального метричного кроку `dx_m = dx_deg * (π/180) * R_earth * cos(φ)`.
- `f0`: Значення параметра Коріоліса `2·Ω·sin(φ₀)` на опорній широті.
- `beta`: Градієнт параметра Коріоліса `2·Ω·cos(φ₀) / R_earth`, що використовується при розрахунках хвильових рухів на бета-площині.

### 2. Буфер тривимірного поля `gfd_field3d_t`

Структура `gfd_field3d_t` представляє неперервне або структуроване скалярне поле у пам'яті.

:::tabs
```c
typedef struct {
    double *data;           /* Вказівник на лінійний масив значень типу double */
    size_t stride_x;        /* Крок індексування при зміні індексу i на +1 */
    size_t stride_y;        /* Крок індексування при зміні індексу j на +1 */
    size_t stride_z;        /* Крок індексування при зміні індексу k на +1 */
    int is_owner;           /* 1 якщо структура є власником пам'яті, 0 якщо це зовнішній слайс */
} gfd_field3d_t;
```
```cpp
struct Field3DView {
    std::span<const double> data;
    size_t stride_x{0};
    size_t stride_y{0};
    size_t stride_z{0};

    [[nodiscard]] constexpr size_t index(size_t i, size_t j, size_t k) const noexcept {
        return i * stride_x + j * stride_y + k * stride_z;
    }

    [[nodiscard]] constexpr double operator()(size_t i, size_t j, size_t k) const noexcept {
        return data[index(i, j, k)];
    }
};
```
:::

Поведінка strides та порядок розташування у пам'яті:
- Для стандартного масиву C у порядку Row-Major (де найшвидше змінюється останній індекс `k`):
  `stride_z = 1`, `stride_y = nz`, `stride_x = ny * nz`.
- Для масивів у порядку Fortran (де найшвидше змінюється перший індекс `i`):
  `stride_x = 1`, `stride_y = nx`, `stride_z = nx * ny`.
- Завдяки явним параметрам strides одна й та сама обчислювальна функція `gfd_pv_compute_ertel` працездатна як із масивами мови C, так і з масивами Fortran (наприклад, із моделей WRF або NEMO) без попереднього перевпорядкування елементів у пам'яті.

### 3. Налаштування розрахунку `gfd_pv_options_t`

:::tabs
```c
typedef enum {
    GFD_BC_PERIODIC = 0,    /* Періодичні граничні умови (для замкнених паралелей) */
    GFD_BC_CLAMPED  = 1,    /* Задані фіксовані значення на границях */
    GFD_BC_NEUMANN  = 2     /* Нульовий градієнт (∂q/∂n = 0) на границях */
} gfd_bc_type_t;

typedef struct {
    int use_pvu_units;      /* 1 — виводити в PVU (10^-6 м²·с⁻¹·К·кг⁻¹), 0 — у SI */
    int diff_order;         /* Порядок точності різницевої схеми: 2 або 4 */
    gfd_bc_type_t bc_x;     /* Тип граничних умов за віссю X */
    gfd_bc_type_t bc_y;     /* Тип граничних умов за віссю Y */
    gfd_bc_type_t bc_z;     /* Тип граничних умов за віссю Z */
} gfd_pv_options_t;
```
```cpp
enum class BCType {
    Periodic = 0,
    Clamped  = 1,
    Neumann  = 2
};

struct PVOptions {
    bool use_pvu_units{true};
    int diff_order{2};
    BCType bc_x{BCType::Periodic};
    BCType bc_y{BCType::Neumann};
    BCType bc_z{BCType::Neumann};
};
```
:::

Опис опцій:
- `use_pvu_units`: При значення `1` результати автоматично множаться на `1.0e6`. Це зручно для діагностики метеорологічних карт на ізоентропійних поверхнях.
- `diff_order`: Порядок точності скінченно-різницевої схеми. При `diff_order == 2` використовується 3-точковий шаблон. При `diff_order == 4` використовується 5-точковий шаблон центральних різниць, що зменшує амплітудну помилку дисперсії сітки.

## Опис публічних функцій C API

### `gfd_field3d_create` та `gfd_field3d_destroy`

Виділення та звільнення пам'яті під тривимірне поле.

:::tabs
```c
gfd_status_t gfd_field3d_create(
    int nx, int ny, int nz, 
    gfd_field3d_t **out_field
);

void gfd_field3d_destroy(gfd_field3d_t *field);
```
```cpp
class Field3DOwner {
public:
    Field3DOwner(int nx, int ny, int nz)
        : nx_(nx), ny_(ny), nz_(nz), buffer_(static_cast<size_t>(nx) * ny * nz, 0.0) {}

    [[nodiscard]] std::span<double> span() noexcept { return buffer_; }
    [[nodiscard]] std::span<const double> span() const noexcept { return buffer_; }

private:
    int nx_, ny_, nz_;
    std::vector<double> buffer_;
};
```
:::

Функція `gfd_field3d_create` виділяє суцільний блок пам'яті розміром `nx * ny * nz * sizeof(double)` та ініціалізує відповідні `stride_x`, `stride_y`, `stride_z` у порядку Row-Major. Поле `is_owner` встановлюється в `1`.

Функція `gfd_field3d_destroy` перевіряє `is_owner`: якщо прапорець істинний, викликом `free()` звільняється внутрішній масив `data`, після чого звільняється сама структура `gfd_field3d_t`.

### `gfd_pv_compute_ertel`

Основна діагностична функція для розрахунку потенціальної вихореності Ертеля.

:::tabs
```c
gfd_status_t gfd_pv_compute_ertel(
    const gfd_grid_t *grid,
    const gfd_field3d_t *u,
    const gfd_field3d_t *v,
    const gfd_field3d_t *w,
    const gfd_field3d_t *theta,
    const gfd_field3d_t *rho,
    const gfd_pv_options_t *opts,
    gfd_field3d_t *pv_out
);
```
```cpp
[[nodiscard]] std::expected<std::vector<double>, gfd_status_t> computeErtelPV(
    const Grid& grid,
    Field3DView u, Field3DView v, Field3DView w,
    Field3DView theta, Field3DView rho,
    const PVOptions& opts = {}
);
```
:::

Алгоритм виконання функції:
1. Перевірка вхідних вказівників на `NULL`. Якщо бодай один є нульовим — повернення `GFD_ERR_NULL_POINTER`.
2. Перевірка розмірностей: масиви `u`, `v`, `w`, `theta`, `rho` та `pv_out` мусять мати сумісні розміри згідно зі структурою `grid`.
3. Ітерація по вузлах сітки. Для внутрішніх вузлів обчислюються складові ротора `ω_x, ω_y, ω_z`, градієнта `∂θ/∂x, ∂θ/∂y, ∂θ/∂z`, їхній скалярний добуток із додаванням планетарного вихору `2·Ω·sin(φ)`, нормування на `ρ` та масштабування одиниць.
4. Обробка граничних вузлів згідно з обраним `opts->bc_x`, `opts->bc_y`, `opts->bc_z`.
5. Повернення `GFD_SUCCESS`.

### `gfd_pv_compute_relative_vorticity`

Обчислює окремо три компоненти вектора відносної вихореності `ω = ∇ × u`.

:::tabs
```c
gfd_status_t gfd_pv_compute_relative_vorticity(
    const gfd_grid_t *grid,
    const gfd_field3d_t *u,
    const gfd_field3d_t *v,
    const gfd_field3d_t *w,
    gfd_field3d_t *wx_out,
    gfd_field3d_t *wy_out,
    gfd_field3d_t *wz_out
);
```
```cpp
struct VorticityVectorResult {
    std::vector<double> wx;
    std::vector<double> wy;
    std::vector<double> wz;
};

[[nodiscard]] std::expected<VorticityVectorResult, gfd_status_t> computeRelativeVorticity(
    const Grid& grid,
    Field3DView u, Field3DView v, Field3DView w
);
```
:::

Ця функція корисна при діагностиці зсувної та криволінійної вихореності в струминних течіях незалежно від стратифікації.

### `gfd_pv_compute_gradient`

Обчислює 3D градієнт `∇λ` довільного скалярного поля.

:::tabs
```c
gfd_status_t gfd_pv_compute_gradient(
    const gfd_grid_t *grid,
    const gfd_field3d_t *scalar,
    gfd_field3d_t *d_dx,
    gfd_field3d_t *d_dy,
    gfd_field3d_t *d_dz
);
```
```cpp
struct GradientVectorResult {
    std::vector<double> dx;
    std::vector<double> dy;
    std::vector<double> dz;
};

[[nodiscard]] std::expected<GradientVectorResult, gfd_status_t> computeGradient(
    const Grid& grid,
    Field3DView scalar
);
```
:::

## Високорівневий обгортковий клас для C++

Для розробників на C++20/C++23 бібліотека надає заголовочний клас `gfd::PVDiagnosticEngine`, який загортає низькорівневі C-функції в RAII-контейнери із використанням `std::span` та `std::expected`.

```cpp
namespace gfd {

class PVDiagnosticEngine {
public:
    explicit PVDiagnosticEngine(gfd_grid_t grid, gfd_pv_options_t options = {})
        : grid_(grid), opts_(options) {}

    ~PVDiagnosticEngine() = default;

    PVDiagnosticEngine(const PVDiagnosticEngine&) = delete;
    PVDiagnosticEngine& operator=(const PVDiagnosticEngine&) = delete;
    PVDiagnosticEngine(PVDiagnosticEngine&&) noexcept = default;
    PVDiagnosticEngine& operator=(PVDiagnosticEngine&&) noexcept = default;

    [[nodiscard]] std::expected<std::vector<double>, gfd_status_t> execute(
        std::span<const double> u,
        std::span<const double> v,
        std::span<const double> w,
        std::span<const double> theta,
        std::span<const double> rho
    ) const {
        const size_t total_size = static_cast<size_t>(grid_.nx) * grid_.ny * grid_.nz;
        if (u.size() != total_size || v.size() != total_size ||
            w.size() != total_size || theta.size() != total_size ||
            rho.size() != total_size) 
        {
            return std::unexpected(GFD_ERR_SPAN_MISMATCH);
        }

        std::vector<double> pv_result(total_size, 0.0);

        gfd_field3d_t f_u{const_cast<double*>(u.data()), static_cast<size_t>(grid_.ny * grid_.nz), static_cast<size_t>(grid_.nz), 1, 0};
        gfd_field3d_t f_v{const_cast<double*>(v.data()), static_cast<size_t>(grid_.ny * grid_.nz), static_cast<size_t>(grid_.nz), 1, 0};
        gfd_field3d_t f_w{const_cast<double*>(w.data()), static_cast<size_t>(grid_.ny * grid_.nz), static_cast<size_t>(grid_.nz), 1, 0};
        gfd_field3d_t f_th{const_cast<double*>(theta.data()), static_cast<size_t>(grid_.ny * grid_.nz), static_cast<size_t>(grid_.nz), 1, 0};
        gfd_field3d_t f_rho{const_cast<double*>(rho.data()), static_cast<size_t>(grid_.ny * grid_.nz), static_cast<size_t>(grid_.nz), 1, 0};
        gfd_field3d_t f_pv{pv_result.data(), static_cast<size_t>(grid_.ny * grid_.nz), static_cast<size_t>(grid_.nz), 1, 0};

        gfd_status_t st = gfd_pv_compute_ertel(&grid_, &f_u, &f_v, &f_w, &f_th, &f_rho, &opts_, &f_pv);
        if (st != GFD_SUCCESS) {
            return std::unexpected(st);
        }

        return pv_result;
    }

private:
    gfd_grid_t grid_;
    gfd_pv_options_t opts_;
};

} // namespace gfd
```

## Гарантії граничних умов та потокобезпечності

1. **Потокобезпечність (Thread-safety)**. Клас `PVDiagnosticEngine` є незмінним (immutable) після створення. Метод `execute()` є константним (`const`), не використовує внутрішній глобальний стан і може безпечно викликатися паралельно з кількох потоків над різними підзонами сітки.
2. **Виключні ситуації**. Жодна функція C API не генерує винятків C++ (exception-free API). Усі помилки передаються через повернення дискретних кодів статусів `gfd_status_t`.
3. **Обробка вироджень та ділення на нуль**. При наявності нефізичних значень густини (`ρ <= 0.0`), обчислювач захищає від ділення на нуль, встановлюючи значення потенціальної вихореності у даному вузлі рівним `0.0` та повертаючи статус `GFD_ERR_ZERO_DENSITY`.
