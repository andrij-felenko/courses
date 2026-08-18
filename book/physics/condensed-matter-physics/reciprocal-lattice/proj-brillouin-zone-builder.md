# ⚙️ Алгоритм обчислення векторів оберненої ґратки та меж зони Бріллюена

Обчислення кристалографічних характеристик оберненої ґратки та геометрії зон Бріллюена є базовим модулем сучасних пакетів квантовомеханічних та солітонних розрахунків матеріалів (таких як Quantum ESPRESSO, VASP, WIEN2k, ABINIT або ASE). Автоматизація цих розрахунків вимагає поєднання векторної алгебри 3D-простору, алгоритмів обчислення випуклих оболонок та ефективної перевірки геометричних обмежень у хвильовому `k`-просторі.

## Математичні основи алгоритму розрахунку

Програмний модуль розрахунку оберненої ґратки вирішує три головні обчислювальні задачі:

1. **Ініціалізація оберненого базису**: за трьома векторами прямої ґратки `a₁`, `a₂`, `a₃` обчислюється орієнтований об'єм примітивної комірки `V_cell = a₁ · (a₂ × a₃)`. Якщо модуль об'єму менший за задану числову точність `ε = 10⁻¹²`, вектори вважаються компланарними, і створення ґратки переривається помилкою. Далі обчислюються вектори оберненого базису `b₁`, `b₂`, `b₃` за формулами Пауля Евальда.

2. **Обчислення міжплощинної відстані `d[hkl]`**: для заданої трійки цілих індексів Міллера `(h, k, l)` формується вектор оберненої ґратки `G[hkl] = h·b₁ + k·b₂ + l·b₃`. Довжина цього вектора `|G[hkl]| = √(G · G)` обчислюється скалярним квадратом, після чого міжплощинна відстань знаходить як `d[hkl] = 2π / |G[hkl]|`.

3. **Локалізація хвильового вектора відносно першої зони Бріллюена**: для довільного вектора хвилі `k` здійснюється перевірка системи нерівностей для всіх сусідніх векторів оберненої ґратки `G ≠ 0`:

```
k · G ≤ (1/2) · |G|²
```

Якщо для усіх найближчих векторів `G` скалярний добуток `k · G` не перевищує `0.5 · |G|²`, точка `k` лежить всередині першої зони Бріллюена. Якщо для хоча б одного вектора `G` виконується строга рівність `k · G = 0.5 · |G|²`, точка `k` знаходиться безпосередньо на межі ЗБ (на бреґґівській площині відбиття). Якщо ж скалярний добуток перевищує `0.5 · |G|²`, вектор `k` виходить за межі першої зони Бріллюена.

## Алгоритм побудови випуклої оболонки першої зони Бріллюена

Для візуалізації або обчислення об'єму першої зони Бріллюена застосовується алгоритм перетину півпросторів (*half-space intersection*):

1. **Генерація найближчих вузлів**: генерується сітка векторів оберненої ґратки `G[hkl]` у діапазоні індексів `-N ≤ h, k, l ≤ N` (зазвичай `N = 2` або `N = 3` достатньо для замикання першої ЗБ).
2. **Формування півпросторів**: кожен вектор `G` задає обмежувальний півпростір `k · (G / |G|) ≤ 0.5 · |G|`.
3. **Пошук вершин багатогранника**: обчислюються точки потрійного перетину трійок бреґґівських площин. Точка перетину є дійсною вершиною першої зони Бріллюена тоді і тільки тоді, коли вона задовольняє нерівності усіх інших півпросторів.
4. **Триангуляція граней**: знайдені вершини групуються по гранях для отримання випуклої оболонки (за допомогою алгоритму Quickhull або триангуляції Делоне в оберненому просторі).

## Детальний математичний аналіз тестування FCC-ґратки кремнію

У наведеній програмі розглянуто розрахунок гранецентрованої кубічної ґратки (FCC) монокристалічного кремнію `Si` з кубічним параметром `a = 0.543` нм. Примітивні вектори трансляції прямого базису дорівнюють:

```
a₁ = (a / 2) · (0, 1, 1)
a₂ = (a / 2) · (1, 0, 1)
a₃ = (a / 2) · (1, 1, 0)
```

Об'єм примітивної комірки прямого простору `V_cell = a₁ · (a₂ × a₃) = a³ / 4 = 0.04002` нм³. За формулами Евальда вектори оберненого базису мають вигляд:

```
b₁ = (2π / a) · (−1, 1, 1)
b₂ = (2π / a) · (1, −1, 1)
b₃ = (2π / a) · (1, 1, −1)
```

Ці вектори утворюють об'ємноцентровану кубічну ґратку (BCC) в оберненому `k`-просторі з об'ємом примітивної комірки `V_BZ = (2π)³ / V_cell = 4 (2π / a)³`.

Проаналізуємо результати роботи функції `is_inside_first_brillouin_zone` для трьох контрольних точок `k`:

1. **Точка `Γ` (центр ЗБ, `k = (0, 0, 0)`)**: скалярний добуток `k · G = 0` для будь-якого `G`. Нерівність `0 ≤ 0.5 · |G|²` виконується строго для всіх векторів `G ≠ 0`. Функція повертає `True`.
2. **Точка `k_boundary = 0.5 · b₁` (центр шестикутної грані ЗБ, точка `L`)**: скалярний добуток `k_boundary · b₁ = 0.5 · b₁ · b₁ = 0.5 · |b₁|²`. Для даного вектора `G = b₁` нерівність перетворюється на точне рівняння бреґґівської площини `0.5 · |b₁|² ≤ 0.5 · |b₁|² + 1e-9`. Для усіх інших векторів `G ≠ b₁` скалярний добуток є меншим за `0.5 |G|²`. Функція повертає `True` (точка належить межі ЗБ).
3. **Точка `k_outside = 0.8 · b₁`**: скалярний добуток `k_outside · b₁ = 0.8 · |b₁|²`. Оскільки `0.8 · |b₁|² > 0.5 · |b₁|² + 1e-9`, виникає порушення нерівності Бреґґа для вектора `G = b₁`. Функція негайно перериває цикл перевірки і повертає `False` (точка лежить за межами першої ЗБ).

## Практична реалізація

:::tabs
```py
import math
import numpy as np

class ReciprocalLattice:
    """Клас для обчислення векторів оберненої ґратки та зон Бріллюена."""
    
    def __init__(self, a1, a2, a3):
        self.a1 = np.array(a1, dtype=float)
        self.a2 = np.array(a2, dtype=float)
        self.a3 = np.array(a3, dtype=float)
        
        # Об'єм примітивної елементарної комірки прямого простору
        self.v_cell = float(np.dot(self.a1, np.cross(self.a2, self.a3)))
        if abs(self.v_cell) < 1e-12:
            raise ValueError("Базисні вектори прямої ґратки є компланарними!")
            
        # Формули Пауля Евальда для векторів оберненого базису
        self.b1 = (2.0 * math.pi / self.v_cell) * np.cross(self.a2, self.a3)
        self.b2 = (2.0 * math.pi / self.v_cell) * np.cross(self.a3, self.a1)
        self.b3 = (2.0 * math.pi / self.v_cell) * np.cross(self.a1, self.a2)

    def get_reciprocal_vector(self, h, k, l):
        """Обчислює вектор оберненої ґратки G[hkl] = h*b1 + k*b2 + l*b3."""
        return h * self.b1 + k * self.b2 + l * self.b3

    def interplanar_spacing(self, h, k, l):
        """Обчислює міжплощинну відстань d[hkl] = 2pi / |G[hkl]|."""
        g = self.get_reciprocal_vector(h, k, l)
        g_len = np.linalg.norm(g)
        if g_len < 1e-12:
            raise ValueError("Індекси Міллера не можуть бути одночасно нульовими!")
        return 2.0 * math.pi / g_len

    def is_inside_first_brillouin_zone(self, k_vec, max_index=2):
        """Перевіряє чи належить хвильовий вектор k першій зоні Бріллюена."""
        k_arr = np.array(k_vec, dtype=float)
        for h in range(-max_index, max_index + 1):
            for k in range(-max_index, max_index + 1):
                for l in range(-max_index, max_index + 1):
                    if h == 0 and k == 0 and l == 0:
                        continue
                    g = self.get_reciprocal_vector(h, k, l)
                    g_sq = np.dot(g, g)
                    # Перевірка умови Бреґґа: k . G <= 0.5 * |G|^2
                    if np.dot(k_arr, g) > 0.5 * g_sq + 1e-9:
                        return False
        return True

# Демонстраційний розрахунок для гранецентрованої кубічної ґратки (FCC Кремнію)
if __name__ == "__main__":
    a = 0.543  # параметр ґратки Si в нанометрах
    # Примітивні вектори трансляції FCC
    a1 = [0.0, a / 2.0, a / 2.0]
    a2 = [a / 2.0, 0.0, a / 2.0]
    a3 = [a / 2.0, a / 2.0, 0.0]

    lat = ReciprocalLattice(a1, a2, a3)
    print(f"Об'єм прямої примітивної комірки V_cell: {lat.v_cell:.5f} нм³")
    print(f"Міжплощинна відстань d(111): {lat.interplanar_spacing(1, 1, 1):.5f} нм")
    print(f"Міжплощинна відстань d(220): {lat.interplanar_spacing(2, 2, 0):.5f} нм")

    # Перевірка кристалографічних точок у k-просторі
    k_gamma = [0.0, 0.0, 0.0]
    k_boundary = lat.b1 * 0.5
    k_outside = lat.b1 * 0.8

    print(f"Точка Gamma (0,0,0) всередині ЗБ: {lat.is_inside_first_brillouin_zone(k_gamma)}")
    print(f"Точка на межі b1/2 всередині ЗБ: {lat.is_inside_first_brillouin_zone(k_boundary)}")
    print(f"Точка за межею 0.8*b1 всередині ЗБ: {lat.is_inside_first_brillouin_zone(k_outside)}")
```
```c
#include <stdio.h>
#include <math.h>
#include <stdbool.h>

#define M_PI_VAL 3.14159265358979323846

typedef struct {
    double x, y, z;
} Vector3;

static inline Vector3 vec_add(Vector3 a, Vector3 b) {
    return (Vector3){a.x + b.x, a.y + b.y, a.z + b.z};
}

static inline Vector3 vec_scale(Vector3 a, double s) {
    return (Vector3){a.x * s, a.y * s, a.z * s};
}

static inline double vec_dot(Vector3 a, Vector3 b) {
    return a.x * b.x + a.y * b.y + a.z * b.z;
}

static inline Vector3 vec_cross(Vector3 a, Vector3 b) {
    return (Vector3){
        a.y * b.z - a.z * b.y,
        a.z * b.x - a.x * b.z,
        a.x * b.y - a.y * b.x
    };
}

static inline double vec_norm(Vector3 a) {
    return sqrt(vec_dot(a, a));
}

typedef struct {
    Vector3 b1, b2, b3;
    double v_cell;
} ReciprocalLatticeC;

bool reciprocal_lattice_init(ReciprocalLatticeC *lat, Vector3 a1, Vector3 a2, Vector3 a3) {
    Vector3 cross23 = vec_cross(a2, a3);
    lat->v_cell = vec_dot(a1, cross23);
    if (fabs(lat->v_cell) < 1e-12) {
        return false; // Помилка: компланарні вектори
    }
    double factor = 2.0 * M_PI_VAL / lat->v_cell;
    lat->b1 = vec_scale(cross23, factor);
    lat->b2 = vec_scale(vec_cross(a3, a1), factor);
    lat->b3 = vec_scale(vec_cross(a1, a2), factor);
    return true;
}

Vector3 reciprocal_get_g(const ReciprocalLatticeC *lat, int h, int k, int l) {
    Vector3 gh = vec_scale(lat->b1, (double)h);
    Vector3 gk = vec_scale(lat->b2, (double)k);
    Vector3 gl = vec_scale(lat->b3, (double)l);
    return vec_add(vec_add(gh, gk), gl);
}

double reciprocal_interplanar_spacing(const ReciprocalLatticeC *lat, int h, int k, int l) {
    Vector3 g = reciprocal_get_g(lat, h, k, l);
    double g_len = vec_norm(g);
    if (g_len < 1e-12) return -1.0;
    return 2.0 * M_PI_VAL / g_len;
}

bool reciprocal_is_inside_bz(const ReciprocalLatticeC *lat, Vector3 k_vec, int max_index) {
    for (int h = -max_index; h <= max_index; ++h) {
        for (int k = -max_index; k <= max_index; ++k) {
            for (int l = -max_index; l <= max_index; ++l) {
                if (h == 0 && k == 0 && l == 0) continue;
                Vector3 g = reciprocal_get_g(lat, h, k, l);
                double g_sq = vec_dot(g, g);
                if (vec_dot(k_vec, g) > 0.5 * g_sq + 1e-9) {
                    return false;
                }
            }
        }
    }
    return true;
}

int main(void) {
    double a = 0.543; // Parameter in nm
    Vector3 a1 = {0.0, a / 2.0, a / 2.0};
    Vector3 a2 = {a / 2.0, 0.0, a / 2.0};
    Vector3 a3 = {a / 2.0, a / 2.0, 0.0};

    ReciprocalLatticeC lat;
    if (!reciprocal_lattice_init(&lat, a1, a2, a3)) {
        printf("Помилка ініціалізації базису!\n");
        return 1;
    }

    printf("Об'єм V_cell (C): %.5f nm^3\n", lat.v_cell);
    printf("Міжплощинна відстань d(111): %.5f nm\n", reciprocal_interplanar_spacing(&lat, 1, 1, 1));
    printf("Міжплощинна відстань d(220): %.5f nm\n", reciprocal_interplanar_spacing(&lat, 2, 2, 0));

    Vector3 k_gamma = {0.0, 0.0, 0.0};
    Vector3 k_outside = vec_scale(lat.b1, 0.8);

    printf("Gamma у ЗБ: %s\n", reciprocal_is_inside_bz(&lat, k_gamma, 2) ? "так" : "ні");
    printf("k_outside у ЗБ: %s\n", reciprocal_is_inside_bz(&lat, k_outside, 2) ? "так" : "ні");
    return 0;
}
```
```cpp
#include <iostream>
#include <cmath>
#include <array>
#include <numbers>
#include <stdexcept>
#include <format>

struct Vector3D {
    double x{0.0}, y{0.0}, z{0.0};

    constexpr Vector3D operator+(const Vector3D& rhs) const noexcept {
        return {x + rhs.x, y + rhs.y, z + rhs.z};
    }

    constexpr Vector3D operator*(double scalar) const noexcept {
        return {x * scalar, y * scalar, z * scalar};
    }

    constexpr double dot(const Vector3D& rhs) const noexcept {
        return x * rhs.x + y * rhs.y + z * rhs.z;
    }

    constexpr Vector3D cross(const Vector3D& rhs) const noexcept {
        return {
            y * rhs.z - z * rhs.y,
            z * rhs.x - x * rhs.z,
            x * rhs.y - y * rhs.x
        };
    }

    double norm() const noexcept {
        return std::sqrt(dot(*this));
    }
};

class ReciprocalLatticeCPP {
public:
    ReciprocalLatticeCPP(const Vector3D& a1, const Vector3D& a2, const Vector3D& a3)
        : m_a1(a1), m_a2(a2), m_a3(a3) {
        
        Vector3D cross23 = m_a2.cross(m_a3);
        m_v_cell = m_a1.dot(cross23);
        if (std::abs(m_v_cell) < 1e-12) {
            throw std::invalid_argument("Прямі базисні вектори компланарні (V_cell = 0)!");
        }

        const double factor = 2.0 * std::numbers::pi / m_v_cell;
        m_b1 = cross23 * factor;
        m_b2 = m_a3.cross(m_a1) * factor;
        m_b3 = m_a1.cross(m_a2) * factor;
    }

    [[nodiscard]] double unit_cell_volume() const noexcept {
        return m_v_cell;
    }

    [[nodiscard]] Vector3D get_g(int h, int k, int l) const noexcept {
        return m_b1 * h + m_b2 * k + m_b3 * l;
    }

    [[nodiscard]] double interplanar_spacing(int h, int k, int l) const {
        if (h == 0 && k == 0 && l == 0) {
            throw std::invalid_argument("Індекси Міллера не можуть бути одночасно нульовими!");
        }
        const Vector3D g = get_g(h, k, l);
        return 2.0 * std::numbers::pi / g.norm();
    }

    [[nodiscard]] bool is_inside_first_brillouin_zone(const Vector3D& k_vec, int max_index = 2) const noexcept {
        for (int h = -max_index; h <= max_index; ++h) {
            for (int k = -max_index; k <= max_index; ++k) {
                for (int l = -max_index; l <= max_index; ++l) {
                    if (h == 0 && k == 0 && l == 0) continue;
                    const Vector3D g = get_g(h, k, l);
                    const double g_sq = g.dot(g);
                    if (k_vec.dot(g) > 0.5 * g_sq + 1e-9) {
                        return false;
                    }
                }
            }
        }
        return true;
    }

    [[nodiscard]] const Vector3D& b1() const noexcept { return m_b1; }
    [[nodiscard]] const Vector3D& b2() const noexcept { return m_b2; }
    [[nodiscard]] const Vector3D& b3() const noexcept { return m_b3; }

private:
    Vector3D m_a1, m_a2, m_a3;
    Vector3D m_b1, m_b2, m_b3;
    double m_v_cell{0.0};
};

int main() {
    constexpr double a = 0.543; // нм
    const Vector3D a1{0.0, a / 2.0, a / 2.0};
    const Vector3D a2{a / 2.0, 0.0, a / 2.0};
    const Vector3D a3{a / 2.0, a / 2.0, 0.0};

    try {
        ReciprocalLatticeCPP lat(a1, a2, a3);
        std::cout << std::format("Об'єм V_cell (C++20): {:.5f} nm^3\n", lat.unit_cell_volume());
        std::cout << std::format("Міжплощинна відстань d(111): {:.5f} nm\n", lat.interplanar_spacing(1, 1, 1));
        std::cout << std::format("Міжплощинна відстань d(220): {:.5f} nm\n", lat.interplanar_spacing(2, 2, 0));

        const Vector3D k_gamma{0.0, 0.0, 0.0};
        const Vector3D k_outside = lat.b1() * 0.8;

        std::cout << std::format("Gamma у ЗБ: {}\n", lat.is_inside_first_brillouin_zone(k_gamma));
        std::cout << std::format("k_outside у ЗБ: {}\n", lat.is_inside_first_brillouin_zone(k_outside));
    } catch (const std::exception& ex) {
        std::cerr << "Помилка розрахунку: " << ex.what() << '\n';
        return 1;
    }
    return 0;
}
```
:::

## Аналіз відмінностей реалізацій та крайових випадків

Кожна з трьох мовних реалізацій вирішує поставлену задачу з урахуванням специфіки свого середовища виконання:

1. **Python-версія (`numpy`)**: орієнтована на наукові дослідження, інтерактивний аналіз у Jupyter Notebook та швидке прототипування. Застосування векторних операцій `numpy` забезпечує високу наочність коду та лаконічність запису мішаних і векторних добутків.
2. **C-версія**: реалізована за стандартом C99 з використанням простих структур `Vector3` та закритих `static inline` помічників без динамічного виділення пам'яті у купі (`heap allocation`). Цей підхід є ідеальним для інтеграції у високопродуктивні обчислювальні ядра фізичних симуляторів на суперкомп'ютерних кластерах (OpenMP/MPI) або вбудовані системи розрахунку дифракційних сканерів.
3. **C++20-версія**: демонструє суперефективний та типізований підхід з використанням новітніх можливостей стандарту C++20: константні вирази `constexpr`, типізовані константи з модуля `<numbers>`, концепція RAII для безпечної інкапсуляції стану ґратки, тип `std::invalid_argument` для обробки виняткових ситуацій та `std::format` для безпечного форматованого виводу.

### Крайові випадки та числова стійкість
При практичному використанні даного алгоритму слід враховувати такі числові нюанси:
- **Машинна точність та виродження базису**: обчислення об'єму комірки `V_cell = a₁ · (a₂ × a₃)` схильне до накопичення помилок заокруглення плаваючої крапки. Порогова перевірка `abs(V_cell) < 1e-12` запобігає діленню на нуль при виродженні ґратки у площину.
- **Епсилон-похибка бреґґівського відбиття**: у функції `is_inside_first_brillouin_zone` умова `np.dot(k_arr, g) > 0.5 * g_sq + 1e-9` містить невелику числову добавку `1e-9`. Це необхідне для того, щоб точки, які лежать **строго на межі** першої зони Бріллюена (`k · G = 0.5 |G|²`), через округлення чисел з плаваючою комою не були випадково збрикнуті за межі 1-ї ЗБ.
- **Вибір межі пошуку `max_index`**: для більшості симетричних кубічних ґраток (SC, BCC, FCC) перша зона Бріллюена повністю формується векторними `G` з індексами `h, k, l ∈ {-1, 0, 1, 2}`. Збільшення `max_index` до 3 або 4 гарантує точність для видовжених триклінних або моноклінних ґраток, хоч і збільшує обчислювальну складність алгоритму як `O(N³)`.

## Оптимізація обчислень для масивів k-точок (k-point grids)

У реальних фізичних симуляторах зонної структури (наприклад, при генерації сіток Монкхорста — Пака для інтегрування по зоні Бріллюена) функція перевірки належності виконується мільйони разів для різних векторів `k`.

Для прискорення обчислень застосовують такі оптимізаційні прийоми:

1. **Попереднє відсікання за радіусом (Bounding Sphere Filtering)**: перша зона Бріллюена вписана у сферу радіуса `R_max = max(|k_vertex|)`. Якщо модуль випробовуваного вектора `|k| > R_max`, вектор гарантовано знаходиться за межами першої ЗБ, і перевірку скалярних добутків можна пропустити.
2. **Використання точкової симетрії (Irreducible Wedge Mapping)**: завдяки кристалографічній точковій групі (наприклад, `O_h` для кубічних кристалів) розрахунок проводиться лише у 1/48 частині зони Бріллюена (незвідний клин).
3. **Векторизація SIMD (AVX-512 / NEON)**: скалярні добутки `k · G` для масиву точок `k` обчислюються паралельно за допомогою векторних інструкцій процесора, що прискорює розрахунок у 4–8 разів у C/C++ реалізаціях.
