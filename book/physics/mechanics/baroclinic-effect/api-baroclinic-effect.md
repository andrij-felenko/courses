# 📋 Інтерфейс довідника та API модулів бароклінної діагностики

Довідник описує повну специфікацію публічного програмувального інтерфейсу (API), структур даних, конфігураційних параметрів, кодів помилок та сигнатур функцій для бібліотеки бароклінної діагностики гідродинамічних полів. Бібліотека призначена для інтеграції у чисельні моделі атмосфери й океану (включаючи регіональні метеорологічні комплекси, oceanographic solvers та астрофізичні плазмові симулятори). Документ визначає точний контракт підключення мовами C99 та C++20, а також CLI-інтерфейс та високорівневу обгортку для мови Python.

## Архітектура та принципи інтеграції

Бібліотека бароклінної діагностики надає гнучку дворівневу архітектуру обчислень, розраховану як на вбудовування у високопродуктивні обчислювальні ядра моделей прогнозу погоди, так і на використання у сценаріях постобробки та аналізу геофізичних даних.

Розділення на мовні рівні реалізовано за такими принципами:

1. **Низькорівневе обчислювальне ядро (C99 ABI)**: сумісне з будь-якими системами обчислення (включаючи FORTRAN 90/2008 гідродинамічні ядра моделей WRF, ROMS, NEMO та MPAS). Ядро працює з пласкими лінійними масивами подвійної точності в пам'яті, не здійснює прихованих динамічних виділень пам'яті під час виконання обчислень та є повністю потік-безпечним (thread-safe, reentrant). Це дозволяє викликати функції ядра з паралельних секцій OpenMP або POSIX Threads без додаткових блокувань.
2. **Високорівневий об'єктно-орієнтований інтерфейс (C++20)**: забезпечує безпеку типів за допомогою `std::span`, автоматичне керування ресурсами через RAII-контейнери, підтримку паралельних алгоритмів `std::execution::par` та обробку виняткових ситуацій. Інтерфейс виключає сирі вказівники та витоки пам'яті.
3. **Прикладний модуль діагностики (Python)**: інтерфейс для інтеграції в системи аналізу даних та постпроцесингу на основі бібліотек `NumPy`, `xarray` та файлових форматів `NetCDF4` / `HDF5`.

Усі просторові поля подаються на структурованій тривимірній сітці з порядком индексації `[k][j][i]`, де `i` відповідає східній координаті `x` (індекс `0..nx-1`), `j` відповідає північній координаті `y` (індекс `0..ny-1`), а `k` відповідає вертикальній координаті `z` (індекс `0..nz-1`, від поверхні до верхньої межі). Такий порядок розміщення елементів у пам'яті забезпечує послідовний доступ до даних уздовж зональної осі X, що оптимізує використання кєш-пам'яті процесора (L1/L2 cache prefetching).

Усі вхідні буфери повинні мати вирівнювання адреси в пам'яті на межу 64 байт (aligned memory allocation) для забезпечення підтримки векторизатора інструкцій SIMD AVX-512 та ARM NEON. Для масивів, розмір яких не ділиться на довжину векторного регістра, рекомендується додавати заповнювальні елементи (padding) в кінці кожного зонального рядка.

## Коди помилок та статус виконання

Усі функції С-інтерфейсу повертають 32-бітне ціле число зі знаком типу `baroclinic_error_t`, яке характеризує результат виконання операції. Від'ємні значення відповідають критичним помилкам виконання, додатні — попередженням, а нуль свідчить про успішне завершення.

Детальна розшифровка кодів помилок та рекомендації щодо їх усунення:

```
Код помилки                              Значення  Опис, причина та методи вирішення
-----------------------------------------------------------------------------------------------------------------------
BAROCLINIC_SUCCESS                            0    Операцію виконано успішно без зауважень.
BAROCLINIC_ERR_NULL_POINTER                  -1    Передано нульовий вказівник (NULL) для обов'язкового буфера. Перевірте виділення пам'яті перед викликом.
BAROCLINIC_ERR_INVALID_GRID                  -2    Некоректні розміри сітки (nx < 3, ny < 3 або nz < 1). Сітка повинна мати принаймні 3 вузли для центральних різниць.
BAROCLINIC_ERR_INVALID_SPACING               -3    Нефізичне значення просторового кроку (dx <= 0, dy <= 0 або dz <= 0). Вкажіть додатні кроки в метрах.
BAROCLINIC_ERR_INVALID_CORIOLIS              -4    Значення параметра Коріоліса f дорівнює нулю у геострофічному розрахунку. На екваторі геострофічний баланс не працює.
BAROCLINIC_ERR_OUT_OF_BOUNDS                 -5    Спроба доступу поза межами виділеного буфера пам'яті. Впевніться у відповідності розміру масиву nx*ny*nz.
BAROCLINIC_ERR_UNSTABLE_STRATIFICATION       -6    Виявлено конвективну нестійкість (N² < 0) при розрахунку частоти Брента. Свідчить о наявності перевороту густини.
BAROCLINIC_ERR_PGF_SIGMA_DIVERGENCE          -7    Чисельна розбіжність градієнта тиску в сігма-координатах понад поріг. Застосуйте фільтрацію рельєфу.
BAROCLINIC_WARN_BOUNDARY_STRIP               1    Попередження: крайові вузли сітки заповнено нулями через брак сусідів для центральної різниці.
BAROCLINIC_WARN_NON_HYDROSTATIC              2    Попередження: відхилення від гідростатичного балансу перевищує 5%. Результати термічного вітру є наближеними.
```

При виникненні будь-якої критичної помилки обчислення припиняється, а у вихідні масиви записуються значення `NaN` у пошкоджених вузлах для відстеження аномалій.

## Переліки та конфігураційні структури

### 1. Тип координатної системи

Перелік визначає тип вертикальної координатної системи, яка використовується в дискретній сітці. Вибір координатної системи визначає внутрішню математичну схему обчислення похідних.

:::tabs
```c
typedef enum {
    BAROCLINIC_COORD_Z_LEVELS    = 0,  /* Фіксовані горизонтальні z-рівні в метрах */
    BAROCLINIC_COORD_PRESSURE    = 1,  /* Ізобаричні поверхні (тиск у Паскалях) */
    BAROCLINIC_COORD_SIGMA       = 2,  /* Рельєфо-наступні σ-координати (0..1) */
    BAROCLINIC_COORD_ISOPYCNAL   = 3   /* Густинні ізопікнічні поверхні */
} baroclinic_coord_type_t;
```
```cpp
enum class BaroclinicCoordType : int32_t {
    ZLevels    = 0,  // Фіксовані горизонтальні z-рівні в метрах
    Pressure   = 1,  // Ізобаричні поверхні (тиск у Паскалях)
    Sigma      = 2,  // Рельєфо-наступні σ-координати (0..1)
    Isopycnal  = 3   // Густинні ізопікнічні поверхні
};
```
:::

Опис режимів:
- `BAROCLINIC_COORD_Z_LEVELS`: стандартні горизонтальні горизонти. Використовуються у більшості великомасштабних моделей океану.
- `BAROCLINIC_COORD_PRESSURE`: ізобаричні поверхні (1000, 850, 500 hPa). Стандартний формат аналізу метеорологічних даних NCEP/ECMWF.
- `BAROCLINIC_COORD_SIGMA`: поверхні, що повторюють рельєф дна або гірських масивів. Вимагають поправки PGF.
- `BAROCLINIC_COORD_ISOPYCNAL`: поверхні рівної густини, на яких діапікнічна дифузія дорівнює нулю.

### 2. Тип граничних умов

Перелік вказує спосіб апроксимації на бічних межах обчислювального домену:

:::tabs
```c
typedef enum {
    BAROCLINIC_BC_ZERO_FILL   = 0, /* Заповнення нулями крайових вузлів */
    BAROCLINIC_BC_PERIODIC    = 1, /* Замкнені періодичні граничні умови (схід-захід) */
    BAROCLINIC_BC_CLAMPED     = 2  /* Дублювання граничного значення (Neumann zero) */
} baroclinic_bc_type_t;
```
```cpp
enum class BaroclinicBcType : int32_t {
    ZeroFill  = 0,  // Заповнення нулями крайових вузлів
    Periodic  = 1,  // Замкнені періодичні граничні умови
    Clamped   = 2   // Дублювання граничного значення
};
```
:::

Використання `BAROCLINIC_BC_PERIODIC` є обов'язковим для глобальних моделей або зон із замкненою зональною геометрією.

### 3. Порядок скінченних різниць

Перелік вказує порядок точності скінченно-різницевої схеми для розрахунку градієнтів:

:::tabs
```c
typedef enum {
    BAROCLINIC_FD_ORDER_2_CENTRAL = 2, /* Центральні різниці 2-го порядку (3-точкові) */
    BAROCLINIC_FD_ORDER_4_CENTRAL = 4  /* Центральні різниці 4-го порядку (5-точкові) */
} baroclinic_fd_order_t;
```
```cpp
enum class BaroclinicFdOrder : int32_t {
    Order2Central = 2,  // Центральні різниці 2-го порядку (3-точкові)
    Order4Central = 4   // Центральні різниці 4-го порядку (5-точкові)
};
```
:::

Схема 4-го порядку точності зменшує фазову дисперсію та чисельну дисипацію коротких хвиль, проте вимагає наявності двох фиктивних вузлів (ghost cells) на кожному краї обчислювальної області.

### 4. Структура конфігурації сітки

Усі просторові та термодинамічні параметри сітки передаються у вигляді структури:

:::tabs
```c
typedef struct {
    size_t nx;                     /* Кількість вузлів по осі X (зональний напрямок) */
    size_t ny;                     /* Кількість вузлів по осі Y (меридіональний напрямок) */
    size_t nz;                     /* Кількість вузлів по осі Z (вертикальний напрямок) */
    double dx;                     /* Крок сітки по осі X (метри) */
    double dy;                     /* Крок сітки по осі Y (метри) */
    double dz;                     /* Крок сітки по осі Z (метри, для z-рівнів) */
    double latitude_deg;           /* Опорна географічна широта у градусах (-90..+90) */
    double coriolis_f0;            /* Параметр Коріоліса f0 (1/с), якщо 0 — рахується з latitude_deg */
    double gravity_g;              /* Прискорення вільного падіння (за замовчуванням 9.80665 м/с²) */
    baroclinic_coord_type_t coord; /* Тип вертикальної координати */
    baroclinic_bc_type_t bc;       /* Тип граничних умов */
    baroclinic_fd_order_t fd_order;/* Порядок скінченних різниць */
} baroclinic_grid_config_t;
```
```cpp
struct BaroclinicGridConfig {
    size_t nx{0};
    size_t ny{0};
    size_t nz{0};
    double dx{10000.0};
    double dy{10000.0};
    double dz{100.0};
    double latitude_deg{45.0};
    double coriolis_f0{0.0};
    double gravity_g{9.80665};
    BaroclinicCoordType coord{BaroclinicCoordType::ZLevels};
    BaroclinicBcType bc{BaroclinicBcType::ZeroFill};
    BaroclinicFdOrder fd_order{BaroclinicFdOrder::Order2Central};
};
```
:::

Перед використанням конфігурації у викликах обчислювальних функцій її обов'язково слід піддати валідації через виклик `baroclinic_config_init()`.

### 5. Структура входів термодинамічного стану

Вхідні поля описуються вказівниками на безперервні тривимірні буфери розміром `nx * ny * nz` елементів типу `double`:

:::tabs
```c
typedef struct {
    const double* pressure;     /* Поле гідростатичного тиску p (Паскалі) */
    const double* density;      /* Поле густини середовища ρ (кг/м³) */
    const double* temperature;  /* Поле абсолютної температури T (Кельвіни) */
    const double* salinity;     /* Поле солоності S (psu, для океану, NULL для повітря) */
    const double* u_velocity;   /* Зональна компонента швидкості u (м/с, може бути NULL) */
    const double* v_velocity;   /* Меридіональна компонента швидкості v (м/с, може бути NULL) */
} baroclinic_state_t;
```
```cpp
struct BaroclinicState {
    std::span<const double> pressure;
    std::span<const double> density;
    std::span<const double> temperature;
    std::span<const double> salinity;
    std::span<const double> u_velocity;
    std::span<const double> v_velocity;
};
```
:::

Поля `pressure` та `density` є строго обов'язковими для розрахунку бароклінного моменту `τ_z`. Поле `temperature` вимагається для розрахунку термічного вітру та частоти Брента — Вяйсяля. Поля `u_velocity` та `v_velocity` є опціональними й використовуються для обчислення числа Річардсона.

### 6. Структура вихідних діагностичних полів

Вихідні буфери повинні бути заздалегідь виділені викликаючою стороною у пам'яті (кожен масив розміром `nx * ny * nz` елементів `double`):

:::tabs
```c
typedef struct {
    double* baroclinic_torque_z; /* Z-компонента бароклінного моменту τ_z (1/с²) */
    double* thermal_wind_du_dz;  /* Вертикальний зсув зонального вітру ∂u_g/∂z (1/с) */
    double* thermal_wind_dv_dz;  /* Вертикальний зсув меридіонального вітру ∂v_g/∂z (1/с) */
    double* brunt_vaisala_n2;    /* Квадрат частоти Брента — Вяйсяля N² (rad²/s²) */
    double* eady_growth_rate;    /* Максимальний інкремент нестійкості Іді σ_max (1/с) */
    double* rossby_radius;       /* Бароклінний радіус деформації Росбі L_R (метри) */
} baroclinic_output_t;
```
```cpp
struct BaroclinicOutput {
    std::span<double> baroclinic_torque_z;
    std::span<double> thermal_wind_du_dz;
    std::span<double> thermal_wind_dv_dz;
    std::span<double> brunt_vaisala_n2;
    std::span<double> eady_growth_rate;
    std::span<double> rossby_radius;
};
```
:::

Викликаюча сторона може встановити вказівник окремого вихідного поля у `NULL`, якщо відповідний показник не потребує розрахунку. Обчислювальне ядро перевіряє вказівники й пропускає неакутальні обчислити, що заощаджує процесорний час.

## С-сигнатури функцій обчислювального ядра та C++20 клас

Усі функції С-інтерфейсу мають префікс `baroclinic_` та експортуються з C ABI сумісністю (`extern "C"`). Вони розроблені для забезпечення максимальної швидкодії та відсутності побічних ефектів.

### 1. Ініціалізація конфігурації

:::tabs
```c
int baroclinic_config_init(baroclinic_grid_config_t* config);
```
```cpp
void init_config(BaroclinicGridConfig& config);
```
:::

Валідує структуру конфігурації сітки та заповнює дефолтні значення. Якщо `coriolis_f0 == 0`, розраховує `f0 = 2 * Ω * sin(latitude_deg)`. Якщо `gravity_g == 0`, встановлює `g = 9.80665 м/с²`.

### 2. Обчислення бароклінного моменту завихреності

:::tabs
```c
int baroclinic_compute_torque(
    const baroclinic_grid_config_t* config,
    const baroclinic_state_t* state,
    baroclinic_output_t* output);
```
```cpp
int compute_torque(
    const BaroclinicGridConfig& config,
    const BaroclinicState& state,
    BaroclinicOutput& output);
```
:::

Обчислює Z-компоненту бароклінного моменту завихреності `τ_z = (1/ρ²) * (∇ρ × ∇p)_z`. Передумови: `state.pressure` та `state.density` не порожні, `output.baroclinic_torque_z` виділено у пам'яті.

### 3. Обчислення термічного зсуву геострофічного вітру

:::tabs
```c
int baroclinic_compute_thermal_wind(
    const baroclinic_grid_config_t* config,
    const baroclinic_state_t* state,
    baroclinic_output_t* output);
```
```cpp
int compute_thermal_wind(
    const BaroclinicGridConfig& config,
    const BaroclinicState& state,
    BaroclinicOutput& output);
```
:::

Обчислює компоненти термічного зсуву вітру `∂u_g/∂z` та `∂v_g/∂z`. Використовує формули: `∂u_g/∂z = - (g / (f*T)) * ∂T/∂y`, `∂v_g/∂z = (g / (f*T)) * ∂T/∂x`. Передумови: `state.temperature` не порожнє, `f0 != 0`.

### 4. Комплексна бароклінна діагностика

:::tabs
```c
int baroclinic_compute_all(
    const baroclinic_grid_config_t* config,
    const baroclinic_state_t* state,
    baroclinic_output_t* output);
```
```cpp
int compute_all(
    const BaroclinicGridConfig& config,
    const BaroclinicState& state,
    BaroclinicOutput& output);
```
:::

Розраховує повний спектр бароклінних параметрів (момент, термічний вітер, N², інкремент Іді, радіус Росбі). Автоматично виконує всі векторні операції в один прохід по пам'яті для оптимізації кєшу.

### 5. Отримання текстового опису помилки

:::tabs
```c
const char* baroclinic_get_error_string(int err_code);
```
```cpp
std::string_view get_error_string(int err_code) noexcept;
```
:::

Повертає текстовий рядок із описом коду помилки у кодуванні UTF-8. Метод не виділяє пам'ять у купі й повертає константний рядок із таблиці.

## Інтерфейс C++20 (`namespace baroclinic`)

У мові C++20 надається безпечний об'єктний обгортковий клас `baroclinic::Solver`, який керує внутрішнім станом, забезпечує перевірку меж та підтримує паралельні алгоритми виконання `std::execution::par`.

```cpp
namespace baroclinic {

class BaroclinicException : public std::runtime_error {
public:
    explicit BaroclinicException(int code)
        : std::runtime_error(std::string(get_error_string(code))), code_(code) {}
    int code() const noexcept { return code_; }
private:
    int code_;
};

class Solver {
public:
    explicit Solver(BaroclinicGridConfig config) : config_(config) {
        init_config(config_);
    }

    // Обчислення моменту завихреності через std::span (без копіювання)
    std::vector<double> compute_torque(
        std::span<const double> pressure,
        std::span<const double> density) const
    {
        const size_t total = config_.nx * config_.ny * config_.nz;
        if (pressure.size() != total || density.size() != total) {
            throw BaroclinicException(BAROCLINIC_ERR_OUT_OF_BOUNDS);
        }

        std::vector<double> torque(total, 0.0);
        BaroclinicState state{.pressure = pressure, .density = density};
        BaroclinicOutput out{.baroclinic_torque_z = torque};

        int rc = compute_torque(config_, state, out);
        if (rc < 0) throw BaroclinicException(rc);

        return torque;
    }

    const BaroclinicGridConfig& config() const noexcept { return config_; }

private:
    BaroclinicGridConfig config_;
};

} // namespace baroclinic
```

## Високорівневий Python-інтерфейс та CLI

### Клас `BaroclinicDiagnostic` (Python)

Для високорівневої роботи у науковому стеку Python надається клас `BaroclinicDiagnostic`, який підтримує масиви `numpy.ndarray` та об'єкти `xarray.DataArray`:

```py
import numpy as np

class BaroclinicDiagnostic:
    def __init__(self, dx: float, dy: float, dz: float, latitude: float = 45.0):
        self.dx = dx
        self.dy = dy
        self.dz = dz
        self.latitude = latitude
        self.f0 = 2.0 * 7.2921159e-5 * np.sin(np.radians(latitude))
        self.g = 9.80665

    def compute_torque(self, p: np.ndarray, rho: np.ndarray) -> np.ndarray:
        """Обчислює бароклінний момент τ_z на 3D масивах."""
        drho_dx = np.gradient(rho, self.dx, axis=2)
        drho_dy = np.gradient(rho, self.dy, axis=1)
        dp_dx   = np.gradient(p,   self.dx, axis=2)
        dp_dy   = np.gradient(p,   self.dy, axis=1)
        
        return (drho_dx * dp_dy - drho_dy * dp_dx) / (rho ** 2)

    def compute_thermal_wind(self, T: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Обчислює вертикальний зсув геострофічного вітру (du_g/dz, dv_g/dz)."""
        dT_dx = np.gradient(T, self.dx, axis=2)
        dT_dy = np.gradient(T, self.dy, axis=1)
        
        du_g_dz = - (self.g / (self.f0 * T)) * dT_dy
        dv_g_dz =   (self.g / (self.f0 * T)) * dT_dx
        return du_g_dz, dv_g_dz
```

### Командний рядок (CLI Tool `baroclinic-diag`)

Для автоматичної обробки файлів у системах пакетного аналізу даних чисельного прогнозу погоди надається консольна утиліта `baroclinic-diag`:

```bash
baroclinic-diag --input model_output.nc --output diag_results.nc \
                --grid-dx 10000 --grid-dy 10000 --lat 48.5 \
                --vars-pressure P --vars-density RHO --vars-temp T \
                --compute-all --fd-order 4 --threads 8
```

Повний перелік параметрів командного рядка:
- `--input, -i`: Шлях до вхідного файлу в форматі NetCDF4 або HDF5, який містить 3D початкові поля.
- `--output, -o`: Шлях до вихідного файлу, куди будуть записані розраховані діагностичні поля.
- `--grid-dx, --grid-dy`: Просторові кроки сітки в метрах вздовж вісей X та Y.
- `--lat`: Опорна географічна широта в градусах для розрахунку параметр Коріоліса.
- `--fd-order`: Порядок скінченних різниць (`2` для швидкого розрахунку або `4` для високої точності).
- `--compute-all`: Прапорець обчислення всіх бароклінних метрик (момент, термічний вітер, N², інкремент Іді, радіус Росбі).
- `--threads, -t`: Кількість паралельних потоків OpenMP / POSIX Threads.

## Таблиця фізичних параметрів та діапазонів значень

У таблиці наведено зведені фізичні характеристики, одиниці вимірювання в системі SI та діапазони допустимих значень для атмосферних та океанічних застосувань:

```
Параметр                       Символ   Одиниці SI    Типовий діапазон в атмосфері  Типовий діапазон в океані
---------------------------------------------------------------------------------------------------------------
Густина середовища             ρ        кг/м³         0.4 — 1.35                    1020 — 1030
Гідростатичний тиск            p        Па            10⁴ — 10⁵ (100–1000 hPa)     10⁵ — 10⁸ (1–1000 bar)
Температура                    T        К             210 — 310 K                   271 — 303 K (0–30 °C)
Параметр Коріоліса             f        1/с           0.7e-4 — 1.4e-4 (помірні)     0.7e-4 — 1.4e-4
Бароклінний момент             τ_z      1/с²          1e-9 — 1e-6                   1e-11 — 1e-8
Термічний зсув вітру           ∂v_g/∂z  1/с           1e-3 — 1e-2 (3–30 м/с на км)   1e-4 — 1e-3
Частота Брента — Вяйсяля       N²       rad²/s²       1e-4 — 4e-4                   1e-6 — 1e-4
Інкремент нестійкості Іді     σ_max    1/с           5e-6 — 2e-5 (t_2 ~ 1–2 доби)   1e-6 — 5e-6 (t_2 ~ 3–7 діб)
Радіус деформації Росбі        L_R      м             500,000 — 1,000,000 (500–1000 км) 10,000 — 50,000 (10–50 км)
```
