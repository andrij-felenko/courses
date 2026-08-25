# 📋 Інтерфейс калькулятора енергії електростатичного поля

Цей довідник описує специфікацію публічного інтерфейсу та контракту програмного модуля `ElectrostaticEnergyCalc`, призначеного для аналітичного й чисельного розрахунку розподілу напруженості, потенціалу та об'ємної густини енергії електростатичних полів у двовимірних і тривимірних геометріях.

### Архітектура програмного інтерфейсу та контракту

Програмний модуль розроблено як високопродуктивний обчислювальний компонент для систем автоматизованого проектування (САПР) високовольтного обладнання, мікроелектромеханічних систем (МЕМС) та інтегральних схем. Модуль забезпечує розрахунок локальної густини енергії `w_e = ½ ε E²` та інтегрування повної енергії електростатичного поля `W = ∫ w_e dV`.

Архітектура інтерфейсу базується на принципах строгої типізації, нульових динамічних накладних витрат у критичних ітераційних циклах, повної відсутності сторонніх залежностей та обробки помилок за допомогою концепцій сучасної мови C++20 (`std::expected` замість винятків) і типізованих об'єктів мови Python (`dataclasses`).

Інтерфейс надає повну потокобезпечність (*thread-safety*) при паралельному зчитуванні полів та обчисленні енергетичних інтегралів у багатопотокових обчислювальних середовищах із використанням OpenMP чи POSIX threads. Для оптимізації роботи з пам'яттю тривимірні розрахункові сітки потенціалів та напруженостей зберігаються у лінійних неперервних масивах (*1D flattened array*) з можливістю векторної SIMD-оптимізації циклів інтегрування.

### Структури даних та параметри конфігурації

Усі величини в інтерфейсі строго дотримуються міжнародної системи одиниць СІ (метри для довжини, вольти для потенціалу, фаради для ємності, джоулі для енергії, кулони для заряду та паскалі для електростатичного тиску).

#### 1. Специфікація сітки `GridConfig`
- `nx`, `ny`, `nz` (`uint32_t`): Кількість вузлів сітки вздовж осей X, Y, Z відповідно. Для двовимірних (2D) моделей параметр `nz` встановлюється рівним `1`.
- `step_size_meters` (`double`): Просторовий крок дискретизації сітки `h` у метрах (`м`). Відстань між сусідніми вузлами по всіх трьох осях вважається однаковою.
- `relative_permittivity` (`double`): Безрозмірна відносна діелектрична проникність середовища `εᵣ` (`≥ 1.0`). Для чистого вакууму або сухого повітря встановлюється значення `1.0`.

#### 2. Конфігурація електрода `ElectrodeSpec`
- `electrode_id` (`uint16_t`): Унікальний числовий ідентифікатор провідного тіла у системі.
- `potential_volts` (`double`): Електричний потенціал `V` на поверхні електрода у вольтах (`В`).
- `boundary_type` (`enum`): Тип граничної умови на поверхні провідника. `DIRICHLET` фіксує значення потенціалу `V = const`, а `NEUMANN` визначає фіксовану нормальна похідну `∂V/∂n` або поверхневу густину заряду.
- `nodes` (`std::vector<GridPoint>` / `list[tuple]`): Масив індексів вузлів розрахункової сітки `(x, y, z)`, які формують межі та об'єм даного металевого електрода.

#### 3. Результати обчислення енергії `EnergyResult`
- `total_energy_joules` (`double`): Повна обчислена енергія електричного поля `W = ∫ (½ ε E²) dV` у джоулях (`Дж`).
- `max_energy_density_j_m3` (`double`): Пикове значення об'ємної густини енергії `w_{e,max} = ½ ε E²_{max}` у `Дж/м³`. Цей показник є критичним для виявлення точок локальної концентрації поля та ризику діелектричного пробою.
- `mean_energy_density_j_m3` (`double`): Середнє значення об'ємної густини енергії по всіх внутрішніх комірках сітки.
- `iterations_count` (`uint32_t`): Кількість ітерацій чисельного сольвера (метод SOR або кон'югованих градієнтів), за яку було досягнуто критерію збіжності.
- `is_converged` (`bool`): Прапор успішного досягнення встановленої точності розв'язку рівняння Пуассона.

### Деталізований протокол конфігурування багатопровідникових систем

Перед запуском розрахунку енергії користувачеві необхідно передати повну геометричну структуру системи. Наприклад, для конфігурування трипровідної екранованої лінії передачі створюється об'єкт `GridConfig` із розміром сітки `200 × 200 × 1` та кроком `h = 0.5 мм`.

Потім за допомогою виклику `add_electrode()` додаються окремі специфікації `ElectrodeSpec`:
1. Зовнішній металевий екран із `electrode_id = 1` та потенціалом `V = 0.0 В` (земля).
2. Перша сигнальна жила з `electrode_id = 2` та потенціалом `V = +5.0 В`.
3. Друга сигнальна жила з `electrode_id = 3` та потенціалом `V = -5.0 В`.

Після додавання всіх електродів функція `solve_field()` розв'язує рівняння Пуассона для міжпровідникового середовища, а виклики `get_electric_field()` та `calculate_total_energy()` дозволяють обчислити матрицю часткових ємностей та сумарну запасану енергію електричного поля.

### Інтеграція з зовнішніми файлами конфігурації

Модуль надає вбудований метод імпорту геометричних конфігурацій та граничних умов із форматів JSON та STEP. При зчитуванні JSON-файлу масив параметрів перевіряється на відповідність типу та межам сітки, а потенціали автоматично конвертуються до базової одиниці вольт (В). У випадку виявлення помилок у координатах електродів метод повертає `ErrorCode::ElectrodeOutOfBounds` без порушення стану поточного розрахункового середовища.

Для експорту розподілу потенціалів та об'ємної густини енергії передбачено функцію `export_vtk()`, яка формує стандартні файли формату VTK (Visualization Toolkit). Це дозволяє візуалізувати тривимірний енергетичний рельєф у сторонніх пакетах аналізу (ParaView або VTK Viewer), відображаючи ізоповерхні рівної густини енергії. Експортований файл містить роздільні вектори напруженості електричного поля та скалярне поле потенціалу для кожного вузла розрахункової сітки.

### Заголовок інтерфейсу на C++

Нижче наведено повну специфікацію заголовка класу `ElectrostaticEnergyCalculator` мовою C++20.

```cpp
#ifndef ELECTROSTATIC_ENERGY_CALCULATOR_HPP
#define ELECTROSTATIC_ENERGY_CALCULATOR_HPP

#include <vector>
#include <cstdint>
#include <system_error>
#include <expected>

namespace electrostatics {

struct GridPoint {
    std::uint32_t x;
    std::uint32_t y;
    std::uint32_t z;
};

enum class BoundaryType {
    Dirichlet,
    Neumann
};

struct ElectrodeSpec {
    std::uint16_t electrode_id;
    double potential_volts;
    BoundaryType boundary_type;
    std::vector<GridPoint> nodes;
};

struct GridConfig {
    std::uint32_t nx{100};
    std::uint32_t ny{100};
    std::uint32_t nz{1};
    double step_size_meters{1e-3};
    double relative_permittivity{1.0};
};

struct EnergyResult {
    double total_energy_joules{0.0};
    double max_energy_density_j_m3{0.0};
    double mean_energy_density_j_m3{0.0};
    std::uint32_t iterations_count{0};
    bool is_converged{false};
};

enum class ErrorCode {
    InvalidGridSize,
    InvalidStepSize,
    InvalidPermittivity,
    ElectrodeOutOfBounds,
    SolverDiverged
};

class ElectrostaticEnergyCalculator {
public:
    explicit ElectrostaticEnergyCalculator(const GridConfig& config);
    ~ElectrostaticEnergyCalculator() = default;

    // Скидання або зміна конфігурації сітки
    std::expected<void, ErrorCode> set_grid_config(const GridConfig& config);

    // Додавання електрода до розрахункової області
    std::expected<void, ErrorCode> add_electrode(const ElectrodeSpec& electrode);

    // Задання об'ємного заряду у вузлі
    std::expected<void, ErrorCode> set_charge_density(std::uint32_t x, std::uint32_t y, std::uint32_t z, double rho_c_m3);

    // Виконання чисельного розв'язку рівняння Пуассона
    std::expected<void, ErrorCode> solve_field(std::uint32_t max_iterations = 10000, double tolerance = 1e-7);

    // Обчислення повної енергії поля по об'єму
    [[nodiscard]] EnergyResult calculate_total_energy() const noexcept;

    // Отримання локального значення потенціалу у точці
    [[nodiscard]] double get_potential(std::uint32_t x, std::uint32_t y, std::uint32_t z) const;

    // Отримання вектора напруженості E у точці (Ex, Ey, Ez)
    [[nodiscard]] std::vector<double> get_electric_field(std::uint32_t x, std::uint32_t y, std::uint32_t z) const;

    // Аналітичний розрахунок для ідеального плоского конденсатора
    [[nodiscard]] static double analytical_flat_capacitor_energy(
        double area_sq_m, 
        double distance_m, 
        double voltage_volts, 
        double relative_permittivity = 1.0) noexcept;
};

} // namespace electrostatics

#endif // ELECTROSTATIC_ENERGY_CALCULATOR_HPP
```

### Інтерфейс у мові Python

Нижче наведено аналогічний контракт класу для мови Python з використанням суворої аннотацій типів (`typing`).

```python
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Tuple, Optional

class BoundaryType(Enum):
    DIRICHLET = "dirichlet"
    NEUMANN = "neumann"

@dataclass
class GridConfig:
    nx: int = 100
    ny: int = 100
    nz: int = 1
    step_size_meters: float = 1e-3
    relative_permittivity: float = 1.0

@dataclass
class ElectrodeSpec:
    electrode_id: int
    potential_volts: float
    boundary_type: BoundaryType
    nodes: List[Tuple[int, int, int]] = field(default_factory=list)

@dataclass
class EnergyResult:
    total_energy_joules: float
    max_energy_density_j_m3: float
    mean_energy_density_j_m3: float
    iterations_count: int
    is_converged: bool

class ElectrostaticEnergyCalculator:
    def __init__(self, config: GridConfig) -> None:
        ...

    def add_electrode(self, electrode: ElectrodeSpec) -> None:
        """Додає поверхню або об'єм електрода з заданим потенціалом."""
        ...

    def set_charge_density(self, x: int, y: int, z: int, rho_c_m3: float) -> None:
        """Встановлює об'ємну густину заряду ρ у вказаному вузлі сітки."""
        ...

    def solve_field(self, max_iterations: int = 10000, tolerance: float = 1e-7) -> None:
        """Розв'язує рівняння Пуассона ітераційним методом."""
        ...

    def calculate_total_energy(self) -> EnergyResult:
        """Обчислює інтегральну енергію поля по всіх комірках сітки."""
        ...

    @staticmethod
    def analytical_flat_capacitor_energy(
        area_sq_m: float, 
        distance_m: float, 
        voltage_volts: float, 
        relative_permittivity: float = 1.0
    ) -> float:
        """Аналітичний розрахунок W = 0.5 * C * V^2 для плоского конденсатора."""
        eps0 = 8.854187817e-12
        capacitance = (eps0 * relative_permittivity * area_sq_m) / distance_m
        return 0.5 * capacitance * (voltage_volts ** 2)
```

### Специфікація помилок та крайових умов

Під час виклику методів конфігурації та чисельного розрахунку модуль здійснює строгу валідацію вхідних даних та повертає відповідні коди помилок:

1. `InvalidGridSize`: Розмірності сітки `nx`, `ny` або `nz` є меншими за `3` вузли або сумарна кількість вузлів перевищує доступний обсяг оперативної пам'яті системи.
2. `InvalidStepSize`: Крок сітки `step_size_meters ≤ 0`, що є фізично неможливим і заважає обчисленню скінченно-різницевих градієнтів `1 / (2 h)`.
3. `InvalidPermittivity`: Відносна діелектрична проникність середовища `relative_permittivity < 1.0`, що порушує термодинамічні обмеження стабільності середовища.
4. `ElectrodeOutOfBounds`: Координати вузлів електрода `GridPoint(x, y, z)` виходять за встановлені межі розрахункової сітки `[0, nx-1]`, `[0, ny-1]`, `[0, nz-1]`.
5. `SolverDiverged`: Ітераційний розв'язок рівняння Пуассона (метод SOR) не досяг критерію збіжності `tolerance` за вказану максимальну кількість ітерацій `max_iterations`.

### Аналітичні модулі верифікації

Для перевірки точності чисельного інтегрування енергії модуль містить вбудовані статичні методи аналітичного розрахунку енергії стандартних конфігурацій:

- **Ідеальний плоский конденсатор:** `W = ½ · (ε₀ εᵣ S / d) · V²`.
- **Сферичний конденсатор (радіуси `a`, `b`):** `W = 2π ε₀ εᵣ · (a b / (b − a)) · V²`.
- **Циліндричний коаксіальний кабель (радіуси `a`, `b`, довжина `L`):** `W = (π ε₀ εᵣ L / ln(b / a)) · V²`.

Кожен із цих аналітичних методів виконується за час `O(1)` і слугує стандартним еталоном для юніт-тестування точності чисельного сольвера.
