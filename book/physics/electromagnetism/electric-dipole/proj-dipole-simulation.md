# ⚙️ Чисельне моделювання полів та динаміки електричного диполя

У цій вставці наведено практичні чисельні алгоритми, математичне обґрунтування, аналіз точності та робочий програмний код для обчислення тривимірного векторного поля електричного диполя, моделювання його обертальних коливань у зовнішньому електричному полі та розрахунку траєкторії руху нейтральної полярної частинки під дією сили діелектрофорезу.

Моделювання польових взаємодій є невід'ємною частиною розробки антенних систем, молекулярної динаміки у хімії, а також проєктування мікрофлюїдних чипів (лабораторій на чипі), де клітини та молекули ДНК розділяють за допомогою неоднорідних високочастотних полів.

Код подано двома мовами у вигляді зручних вкладок — ідіоматичною C++20 (з використанням векторів, типів `std::valarray` / `std::array` та строгих математичних функцій) та Python 3 (з використанням бібліотеки векторних обчислень NumPy).

## 1. Розрахунок сітки поля та потенціалу диполя

Першим практичним завданням є створення тривимірної сітки значень електростатичного потенціалу `Φ(r)` та векторів напруженості `E(r)` для точкового диполя з довільним векторним моментом `p`.

### 1.1. Фізичний алгоритм та математична модель
Для обчислення потенціалу та вектора напруженості у кожному вузлі просторової сітки `(x, y, z)` алгоритм виконує такі послідовні математичні кроки:

1. Розрахунок радіус-вектора від центру диполя `r_0` до точки спостереження `r`:
   ```
   Δr = r − r_0 = (x − x_0, y − y_0, z − z_0)
   ```
2. Обчислення евклідової відстані `R = |Δr| = √(Δx² + Δy² + Δz²)`.
3. Перевірка критерію сингулярності `R < R_cutoff`. Якщо точка лежить занадто близько до центру диполя (у зоні `R < 10⁻¹²` м), поле вважають сингулярним, щоб уникнути помилки ділення на нуль (`division by zero`).
4. Розрахунок нормованого одиничного вектора напрямку `r̂ = Δr / R`.
5. Обчислення скалярного добутку `(p · r̂) = p_x · r̂_x + p_y · r̂_y + p_z · r̂_z`.
6. Розрахунок потенціалу `Φ = (1 / (4·π·ε₀)) · (p · r̂) / R²`.
7. Розрахунок вектора напруженості `E = (1 / (4·π·ε₀)) · (3 · (p · r̂) · r̂ − p) / R³`.

У програмі на мові C++ для збереження тривимірних координат використовують легковагову структуру `Vector3D` з константними методиками, що дозволяє компілятору виконувати інлайн-оптимізацію та векторизацію (SIMD-інструкції AVX2/AVX-512). У реалізації на Python застосовують векторні операції з тривимірними масивами NumPy (`np.meshgrid`), що дозволяє обчислити мільйони вузлів сітки за частки секунди без використання повільних циклів `for`.

:::tabs
```cpp
#include <iostream>
#include <vector>
#include <cmath>
#include <array>
#include <numbers>

// Структура для 3D вектора дійсної точності
struct Vector3D {
    double x{0.0};
    double y{0.0};
    double z{0.0};

    constexpr Vector3D operator+(const Vector3D& other) const noexcept {
        return {x + other.x, y + other.y, z + other.z};
    }

    constexpr Vector3D operator-(const Vector3D& other) const noexcept {
        return {x - other.x, y - other.y, z - other.z};
    }

    constexpr Vector3D operator*(double scalar) const noexcept {
        return {x * scalar, y * scalar, z * scalar};
    }

    [[nodiscard]] double dot(const Vector3D& other) const noexcept {
        return x * other.x + y * other.y + z * other.z;
    }

    [[nodiscard]] double norm() const noexcept {
        return std::sqrt(dot(*this));
    }
};

// Фізичні константи в системі SI
constexpr double EPSILON_0 = 8.8541878128e-12; // Ф/м
constexpr double K_COULOMB = 1.0 / (4.0 * std::numbers::pi * EPSILON_0);

// Результат обчислення поля в точці
struct FieldPoint {
    Vector3D position;
    double potential{0.0};
    Vector3D electric_field;
};

// Обчислення дипольного потенціалу та поля у точці observation_point (r > 0)
FieldPoint calculate_dipole_field(const Vector3D& dipole_center,
                                 const Vector3D& dipole_moment,
                                 const Vector3D& observation_point) {
    const Vector3D r_vec = observation_point - dipole_center;
    const double r = r_vec.norm();

    if (r < 1e-12) {
        // Уникнення сингулярності в самому центрі диполя
        return {observation_point, 0.0, {0.0, 0.0, 0.0}};
    }

    const Vector3D r_hat = r_vec * (1.0 / r);
    const double p_dot_rhat = dipole_moment.dot(r_hat);

    // Потенціал Phi = (1 / 4pi eps0) * (p . rhat) / r^2
    const double potential = K_COULOMB * p_dot_rhat / (r * r);

    // Поле E = (1 / 4pi eps0) * (3 * (p . rhat) * rhat - p) / r^3
    const Vector3D field_vec = (r_hat * (3.0 * p_dot_rhat) - dipole_moment) * (K_COULOMB / (r * r * r));

    return {observation_point, potential, field_vec};
}

int main() {
    // Диполь з моментом p = 1.85 Debye (молекула води H2O) уздовж осі Z
    const double debye_unit = 3.33564e-30; // C*m
    const Vector3D dipole_center{0.0, 0.0, 0.0};
    const Vector3D dipole_moment{0.0, 0.0, 1.85 * debye_unit};

    std::cout << "--- Розрахунок поля диполя H2O (p = 1.85 D) ---\n";

    // Скануємо точки вздовж осі Z (θ = 0) та осі X (θ = 90 deg) на відстані 1 нм
    const double dist = 1e-9; // 1 нм
    const Vector3D point_z{0.0, 0.0, dist};
    const Vector3D point_x{dist, 0.0, 0.0};

    const auto res_z = calculate_dipole_field(dipole_center, dipole_moment, point_z);
    const auto res_x = calculate_dipole_field(dipole_center, dipole_moment, point_x);

    std::cout << "Точка на осі Z (1 нм): Phi = " << res_z.potential 
              << " В, |E| = " << res_z.electric_field.norm() << " В/м\n";
    std::cout << "Точка на осі X (1 нм): Phi = " << res_x.potential 
              << " В, |E| = " << res_x.electric_field.norm() << " В/м\n";
    std::cout << "Співвідношення полів E_z / E_x: " 
              << res_z.electric_field.norm() / res_x.electric_field.norm() 
              << " (теоретично має бути 2.0)\n";

    return 0;
}
```
```py
import numpy as np

# Фізичні константи SI
EPSILON_0 = 8.8541878128e-12
K_COULOMB = 1.0 / (4.0 * np.pi * EPSILON_0)
DEBYE = 3.33564e-30

def compute_dipole_field_grid(dipole_moment, grid_size=50, box_limit=2e-9):
    """
    Обчислення 3D сітки потенціалу та поля диполя за допомогою векторного NumPy.
    dipole_moment: вектор [px, py, pz] у C*m
    """
    x = np.linspace(-box_limit, box_limit, grid_size)
    y = np.linspace(-box_limit, box_limit, grid_size)
    z = np.linspace(-box_limit, box_limit, grid_size)
    X, Y, Z = np.meshgrid(x, y, z, indexing='ij')

    # Вектор відстані R від центру (0,0,0)
    R_norm = np.sqrt(X**2 + Y**2 + Z**2)
    # Маска для уникнення ділення на нуль у центрі
    mask = R_norm > 1e-12

    Potential = np.zeros_like(R_norm)
    Ex = np.zeros_like(R_norm)
    Ey = np.zeros_like(R_norm)
    Ez = np.zeros_like(R_norm)

    px, py, pz = dipole_moment
    # Скалярний добуток p . r
    p_dot_r = px * X[mask] + py * Y[mask] + pz * Z[mask]

    # Потенціал Phi = (1 / 4pi eps0) * (p . r) / r^3
    Potential[mask] = K_COULOMB * p_dot_r / (R_norm[mask]**3)

    # Вектор поля E = (1 / 4pi eps0) * (3 * (p . r) * r / r^5 - p / r^3)
    coeff_3 = 3.0 * p_dot_r / (R_norm[mask]**5)
    r3 = R_norm[mask]**3

    Ex[mask] = K_COULOMB * (coeff_3 * X[mask] - px / r3)
    Ey[mask] = K_COULOMB * (coeff_3 * Y[mask] - py / r3)
    Ez[mask] = K_COULOMB * (coeff_3 * Z[mask] - pz / r3)

    return X, Y, Z, Potential, Ex, Ey, Ez

if __name__ == "__main__":
    p_h2o = np.array([0.0, 0.0, 1.85 * DEBYE])
    X, Y, Z, Phi, Ex, Ey, Ez = compute_dipole_field_grid(p_h2o)
    print("Сітку поля диполя H2O успішно згенеровано.")
    print(f"Максимальний потенціал на відстані 1 нм: {np.max(np.abs(Phi)):.4f} В")
```
:::

## 2. Моделювання обертальної динаміки диполя у зовнішньому полі

Розглянемо чисельне інтегрування диференціального рівняння обертання полярного диполя із моментом інерції `I` та дипольним моментом `p` у зовнішньому однорідному полі `E` з урахуванням коефіцієнта в'язкого тертя `γ`:

```
I · (d²θ / dt²) + γ · (dθ / dt) + p · E · sin θ = 0    [динамічне рівняння обертання]
```

### 2.1. Алгоритм Рунге-Кутти 4-го порядку (RK4)
Для забезпечення високої точності чисельного інтегрування нелінійного рівняння коливань зводимо диференціальне рівняння другого порядку до системи двох рівнянь першого порядку відносно кута `θ` та кутової швидкості `ω = dθ/dt`:

```
dθ / dt = ω
dω / dt = ( −p · E · sin θ − γ · ω ) / I
```

Метод Рунге-Кутти 4-го порядку має четвертий порядок точності по кроку часу `O(dt⁴)`. На кожному кроці часу `dt` обчислюють чотири проміжні прирости:
- `k1` — оцінка похідних на початку інтервалу `t`.
- `k2` — оцінка похідних у середині інтервалу `t + dt/2` за допомогою приросту `k1`.
- `k3` — повторна уточнена оцінка в середині інтервалу `t + dt/2` за допомогою `k2`.
- `k4` — оцінка в кінці інтервалу `t + dt` за допомогою `k3`.

Сумарний крок обчислюють як зважену комбінацію:
```
θ(t + dt) = θ(t) + (dt / 6) · (k1_θ + 2·k2_θ + 2·k3_θ + k4_θ)
ω(t + dt) = ω(t) + (dt / 6) · (k1_ω + 2·k2_ω + 2·k3_ω + k4_ω)
```

Для молекулярних систем із малим моментом інерції `I ≈ 10⁻⁴⁷` кг·м² та високими частотами коливань `ω₀ ≈ 10¹²` рад/с крок інтегрування `dt` слід вибирати суттєво меншим за період коливань — у діапазоні `1` – `10` фемтосекунд (`10⁻¹⁵` – `10⁻¹⁴` с).

Вибір явного схеми RK4 замість простої схеми Ейлера `θ(t + dt) = θ(t) + ω(t)·dt` є критично важливим для даної фізичної задачі. Схема Ейлера є схемою першого порядку точності `O(dt)` і вносить систематичну чисельну в'язку амплітуду (чисельне самозбудження або штучне згасання), що призводить до швидкої втрати енергії за кілька періодів коливань. Натомість схема RK4 зберігає повну фазову траєкторію та гарантує точне дотримання закону збереження механічної енергії на тривалих інтервалах симуляції.

:::tabs
```cpp
#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>
#include <numbers>

// Стан ротатора: кут theta (рад) та кутова швидкість omega (рад/с)
struct State {
    double theta;
    double omega;
};

// Права частина системи ODE: dtheta/dt = omega, domega/dt = (-p*E*sin(theta) - gamma*omega) / I
State derivatives(const State& s, double p, double E, double I, double gamma) {
    double dtheta = s.omega;
    double domega = (-p * E * std::sin(s.theta) - gamma * s.omega) / I;
    return {dtheta, domega};
}

// Крок інтегрування методом Рунге-Кутти 4-го порядку (RK4)
State rk4_step(const State& current, double dt, double p, double E, double I, double gamma) {
    const auto k1 = derivatives(current, p, E, I, gamma);

    const State s2{current.theta + 0.5 * dt * k1.theta, current.omega + 0.5 * dt * k1.omega};
    const auto k2 = derivatives(s2, p, E, I, gamma);

    const State s3{current.theta + 0.5 * dt * k2.theta, current.omega + 0.5 * dt * k2.omega};
    const auto k3 = derivatives(s3, p, E, I, gamma);

    const State s4{current.theta + dt * k3.theta, current.omega + dt * k3.omega};
    const auto k4 = derivatives(s4, p, E, I, gamma);

    const double dtheta = (k1.theta + 2.0 * k2.theta + 2.0 * k3.theta + k4.theta) / 6.0;
    const double domega = (k1.omega + 2.0 * k2.omega + 2.0 * k3.omega + k4.omega) / 6.0;

    return {current.theta + dt * dtheta, current.omega + dt * domega};
}

int main() {
    // Параметри мікромолекулярного ротатора (молекула H2O)
    const double p = 1.85 * 3.33564e-30; // p = 1.85 D
    const double E = 1e6;                // Поле E = 1 МВ/м
    const double I = 2.0e-47;            // Момент інерції кг*м^2
    const double gamma = 1.0e-36;        // Коефіцієнт в'язкого згасання

    State state{1.57079632679, 0.0};     // Стартовий кут 90 градусів (pi/2)
    const double dt = 1e-14;             // Крок часу 10 фемтосекунд
    const int steps = 500;

    std::cout << "--- Симуляція згасаючих коливань диполя (RK4) ---\n";
    std::cout << std::setw(10) << "Час (пс)" << std::setw(15) << "Кут (град)" 
              << std::setw(20) << "Швидкість (рад/с)\n";

    for (int i = 0; i <= steps; ++i) {
        if (i % 50 == 0) {
            double time_ps = i * dt * 1e12;
            double angle_deg = state.theta * 180.0 / std::numbers::pi;
            std::cout << std::setw(10) << time_ps << std::setw(15) << angle_deg 
                      << std::setw(20) << state.omega << "\n";
        }
        state = rk4_step(state, dt, p, E, I, gamma);
    }

    return 0;
}
```
```py
import numpy as np

def simulate_dipole_rotation(p_val, E_val, I_val, gamma_val, theta0_deg=90.0, t_max_ps=5.0):
    """
    Моделювання обертальної динаміки диполя в однорідному полі методом RK4.
    """
    theta0 = np.radians(theta0_deg)
    state = np.array([theta0, 0.0]) # [theta, omega]
    dt = 1e-14 # 10 фс
    steps = int(t_max_ps * 1e-12 / dt)

    times = np.linspace(0, t_max_ps, steps)
    angles = np.zeros(steps)

    def rhs(st):
        th, om = st[0], st[1]
        dth = om
        dom = (-p_val * E_val * np.sin(th) - gamma_val * om) / I_val
        return np.array([dth, dom])

    for i in range(steps):
        angles[i] = np.degrees(state[0])
        # Крок RK4
        k1 = rhs(state)
        k2 = rhs(state + 0.5 * dt * k1)
        k3 = rhs(state + 0.5 * dt * k2)
        k4 = rhs(state + dt * k3)
        state += (dt / 6.0) * (k1 + 2*k2 + 2*k3 + k4)

    return times, angles

if __name__ == "__main__":
    p_h2o = 1.85 * 3.33564e-30
    E_ext = 1e6
    I_h2o = 2.0e-47
    gamma = 1.0e-36

    t, deg = simulate_dipole_rotation(p_h2o, E_ext, I_h2o, gamma)
    print(f"Симуляцію завершено. Кінцевий кут диполя: {deg[-1]:.2f}° (орієнтація за полем).")
```
:::

## 3. Симуляція траєкторії діелектрофорезу в неоднорідному полі

У мікрофлюїдних пристроях для сортування клітин неоднорідне поле створюється квадрупольною або клиноподібною системою електродів. Поступальний рух частинки маса `m` описується другим законом Ньютона з урахуванням сили діелектрофорезу `F_dep = (1/2) · α · ∇(E²)` та сили гідродинамічного опору Стокса `F_drag = −6·π·η·a · v`:

```
m · (d²r / dt²) = (1 / 2) · α · ∇(E²) − 6 · π · η · a · (dr / dt)   [динаміка діелектрофорезу]
```

Де `η` — динамічна в'язкість рідини, `a` — радіус мікрочастинки чи клітини, `α` — її ефективна поляризовність у даному середовищі.

### 3.1. Квазістаціонарне наближення низьких чисел Рейнольдса
Завдяки мікроскопічним розмірам частинок у біофлюїдиці (`a ≈ 1` – `10` мкм) та малій масі `m ≈ 10⁻¹²` кг, характерний час релаксації швидкості Стокса `τ_v = m / (6·π·η·a)` становить менше 1 мікросекунди. Тому інерційним членом `m · (d²r/dt²)` можна нехтувати (квазістаціонарне наближення низьких чисел Рейнольдса `Re « 1`). 

Швидкість частинки у кожен момент часу виражається прямо через градієнт квадрата напруженості поля:

```
v = dr / dt = [ α / (12 · π · η · a) ] · ∇(E²)         [квазістаціонарна швидкість діелектрофорезу]
```

Цей чисельний підхід дозволяє розраховувати точно траєкторії руху клітин у лабораторних чипах без витратних повномасштабних сіткових гідродинамічних симуляцій Navier-Stokes.

Полярність частинки відносно середовища визначає знак сили:
- Якщо поляризовність частинки вища за поляризовність рідини (`α > 0`), частинка рухається у бік максимуму поля (**позитивний діелектрофорез**, pDEP).
- Якщо поляризовність частинки нижча за поляризовність рідини (`α < 0`), частинка відштовхується від сильного поля (**негативний діелектрофорез**, nDEP).

Описані чисельні моделі є основою проєктування сучасних аналітичних біочипів та медичних сортувальних систем.

## 4. Обчислювальна точність та граничні умови

При чисельному моделюванні молекулярних та мікроскопічних дипольних полів особливу увагу слід приділяти точності обчислення чисел з рухомою комою подвійної точності (`double precision`, стандарт IEEE 754). Оскільки потенціал спадає пропорційно `1 / r²`, а напруженість поля — пропорційно `1 / r³`, різка зміна масштабів величин від нанометрових відстаней біля диполя до макроскопічних відстаней може спричиняти втрату значущих розрядів при відніманні близьких чисел (`catastrophic cancellation`).

Для запобігання втратам точності рекомендується:
1. Використовувати безрозмірні (нормовані) змінні при обчисленнях у сітці, масштабуючи координати на радіус молекули `r_0`, а потенціал — на характеристичний потенціал `Φ_0 = p / (4·π·ε₀·r_0²)`.
2. Застосовувати алгоритм підсумовування Кахана (`Kahan summation`) при обчисленні сумарного поля від велетенського ансамблю з мільйонів молекулярних диполів у розчині.
3. На межах розрахункової області задавати нульові граничні умови Діріхле `Φ = 0` для потенціалу або періодичні граничні умови з використанням методу Евальда (`Ewald summation`) для нескінченних кристалічних ґраток.

