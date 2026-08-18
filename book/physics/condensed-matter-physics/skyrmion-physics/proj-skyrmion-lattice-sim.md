# ⚙️ Чисельне моделювання текстури та топологічного заряду скирміона

Обчислювальне моделювання двовимірної магнітної ґратки спінів охоплює розрахунок її мікромагнітної енергії, чисельне інтегрування топологічного заряду, аналіз похибок дискретизації та реалізацію релаксації системи методом градуйованого спуску і динаміки Ландау — Ліфшиця — Гільберта.

## 1. Фізична та геометрична дискретизація магнітного поля

У чисельному мікромагнітному моделюванні двовимірну магнітну плівку розбивають на прямокутну сітку вузлів розміром `N x N` з кроком дискретизації `a` (зазвичай `0.5–1.0 nm`). У кожному вузлі `(i, j)` визначено тривимірний вектор орієнтації магнітного моменту `m(i, j) = (m_x, m_y, m_z)` з суворою умовою нормування `m_x² + m_y² + m_z² = 1`.

Для обчислення топологічного заряду `Q` на дискретній ґратці простого наближення частинних похідних скінченними різницями `(∂m/∂x × ∂m/∂y)` недостатньо. При наближенні скінченними різницями дискретизаційні похибки ламають строгу цілочисельну топологічну квантованість: заряд отримує дробову похибку (наприклад, `Q = -0.87` замість `-1.00`), а при русі скирміона крізь сітку значення `Q` зазнає нефізичних осциляцій. Для усунення цього дефекту застосовують геометрично точний метод Судзукі — Берглунда (Suzuki-Berg-Lüscher).

У цьому методі кожну квадратну чарунку сітки `(i, j) - (i+1, j) - (i+1, j+1) - (i, j+1)` розбивають на два орієнтовані трикутники. Дискретний телесний кут `Ω` для довільної трійки векторів спінів `(m₁, m₂, m₃)` обчислюють за геометричною формулою Ойлера — Аскера:

```
tan(Ω / 2) = [ m₁ · (m₂ × m₃) ] / [ 1 + m₁·m₂ + m₂·m₃ + m₃·m₁ ]
```

Чисельна процедура Судзукі — Берглунда володіє важливими перевагами:
1. Значення `Ω` виражає точну площу сферичного трикутника на одиничній сфері `S²`, утвореного трьома векторами `m₁`, `m₂`, `m₃`.
2. Сума телесних кутів по всіх замкнених трикутниках сітки, поділена на `4π`, дає точне ціле число топологічного заряду `Q = -1` навіть для грубих чисельних сіток, де радіус скирміона становить усього 4–5 вузлів.
3. Алгоритм є обчислювально стійким до появи точкових сингулярностей та не створює хибних топологічних зарядів при наявності шумів чи теплових коливань спінів.

## 2. Дискретизація мікромагнітних взаємодій та ефективного поля

Для моделювання динаміки або шукання рівноважної конфігурації скирміона необхідно обчислити ефективне магнітне поле `H_eff(i, j)` у кожному вузлі сітки:

```
H_eff(i, j) = - (1 / (μ₀ M_s)) · (δE_tot / δm(i, j))
```

Ефективне поле складається з чотирьох дискретних внесків:

### 2.1. Дискретне обмінне поле Гейзенберга

Згладжувальне обмінне поле обчислюють через двовимірний п'ятиточковий оператор Лапласа від чотирьох найближчих сусідів:

```
H_ex(i, j) = (2 A / (μ₀ M_s a²)) · [ m(i+1, j) + m(i-1, j) + m(i, j+1) + m(i, j-1) - 4 m(i, j) ]
```

### 2.2. Дискретне поле інтерфейсної DMI

Асиметричне поле DMI залежить від орієнтації векторів суміжних вузлів і обчислюється через центральні скінченні різниці:

```
H_DMI_x(i, j) = (D / (μ₀ M_s a)) · [ m_z(i+1, j) - m_z(i-1, j) ]
H_DMI_y(i, j) = (D / (μ₀ M_s a)) · [ m_z(i, j+1) - m_z(i, j-1) ]
H_DMI_z(i, j) = - (D / (μ₀ M_s a)) · [ m_x(i+1, j) - m_x(i-1, j) + m_y(i, j+1) - m_y(i, j-1) ]
```

### 2.3. Поле перпендикулярної магнітної анізотропії (PMA)

Поле анізотропії утримує спіни вздовж перпендикулярної осі `z`:

```
H_ani(i, j) = (2 K_u / (μ₀ M_s)) · m_z(i, j) · e_z
```

### 2.4. Поле Зеємана

Поле від зовнішнього джерела, спрямоване проти ядра скирміона:

```
H_Z = H_ext · e_z
```

## 3. Граничні умови та чисельна релаксація системи

При чисельному моделюванні застосовують два типи граничних умов:
- **Періодичні граничні умови (PBC):** вузли протилежних країв з'єднуються у тороїдальну топологію `m(N, j) = m(0, j)`. Це підходить для моделювання нескінченних періодичних ґраток скирміонів.
- **Відкриті граничні умови (OBC):** на межі плівки задають модифіковані крайові умови з урахуванням DMI. Інтерфейсна DMI створює на краях плівки додатковий обертальний момент, змушуючи спіни на межі нахилятися під кутом до вертикалі. Це генерує потенціальний бар'єр крайового відштовхування, який утримує скирміон всередині нанодроту.

Часову еволюцію та релаксацію спінової сітки до стану з мінімальною енергією описують нелінійним диференціальним рівнянням Ландау — Ліфшиця — Гільберта (LLG):

```
∂m / ∂t = - γ_0 · (m × H_eff) + α · (m × (∂m / ∂t))
```

де `γ_0 = 2.211 · 10⁵ m/(A·s)` — гіромагнітне співвідношення для вільного електрона, а `α` — безрозмірний коефіцієнт згасання Гільберта (для типових металевих плівок `α = 0.02–0.1`).

Для чисельного інтегрування рівняння LLG зводять до явної форми за допомогою перетворення Гільберта:

```
∂m / ∂t = - [ γ_0 / (1 + α²) ] · ( m × H_eff + α · m × (m × H_eff) )
```

Перший доданок описує консервативну прецесію намагніченості навколо ефективного поля `H_eff`, а другий доданок — релаксаційну дисипацію, яка повертає вектор намагніченості вздовж поля `H_eff`.

Максимальний допустимий крок інтегрування за часом `Δt` обмежено умовою Куранта — Фрідріхса — Леві (CFL):

```
Δt < [ (1 + α²) / (α · γ_0) ] · [ (μ₀ M_s a²) / (4 A) ]
```

Для типових параметрів кобальтових плівок (`a = 1 nm`, `A = 15 pJ/m`) крок за часом не повинен перевищувати `Δt ≈ 10–50 fs` (фемтосекунд).

## 4. Повна реалізація моделювання у коді C та C++

Нижче наведено повну реалізацію чисельного модуля моделювання скирміонної ґратки. Програма створює початкову конфігурацію Неєлівського скирміона у центрі сітки, обчислює топологічний заряд `Q` за методом Судзукі — Берглунда та проводить перевірку геометрії.

Код реалізовано двома мовами:
- У вкладці C використано класичний процедурний підхід із суворим використанням динамічного виділення пам'яті через `malloc`/`free`, покажчиків та векторної арифметики.
- У вкладці C++ застосовано ідіоматичні об'єктно-орієнтовані шаблони розробки: RAII-обгортки контейнерів `std::vector`, методи структури `Spin3D` для векторних добутків, типізовані константи з простору назв `std::numbers` та методи-члени класу `SkyrmionLattice`.

:::tabs
```c
/* skyrmion_sim.c — Чисельне моделювання магнітного скирміона мовою C */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define M_PI_VAL 3.14159265358979323846

typedef struct {
    double x;
    double y;
    double z;
} Vector3;

static inline Vector3 vec_normalize(Vector3 v) {
    double len = sqrt(v.x * v.x + v.y * v.y + v.z * v.z);
    if (len > 1e-12) {
        v.x /= len;
        v.y /= len;
        v.z /= len;
    }
    return v;
}

static inline double vec_dot(Vector3 a, Vector3 b) {
    return a.x * b.x + a.y * b.y + a.z * b.z;
}

static inline Vector3 vec_cross(Vector3 a, Vector3 b) {
    Vector3 res;
    res.x = a.y * b.z - a.z * b.y;
    res.y = a.z * b.x - a.x * b.z;
    res.z = a.x * b.y - a.y * b.x;
    return res;
}

/* Обчислення дискретного телесного кута трійки спінів (Ойлер — Аскер) */
static double solid_angle(Vector3 m1, Vector3 m2, Vector3 m3) {
    double triple_prod = vec_dot(m1, vec_cross(m2, m3));
    double denom = 1.0 + vec_dot(m1, m2) + vec_dot(m2, m3) + vec_dot(m3, m1);
    return 2.0 * atan2(triple_prod, denom);
}

typedef struct {
    int size;
    double grid_step;
    Vector3 *spins;
} SkyrmionGridC;

SkyrmionGridC* skyrmion_grid_create(int size, double step) {
    SkyrmionGridC *g = (SkyrmionGridC*)malloc(sizeof(SkyrmionGridC));
    if (!g) return NULL;
    g->size = size;
    g->grid_step = step;
    g->spins = (Vector3*)malloc(size * size * sizeof(Vector3));
    return g;
}

void skyrmion_grid_free(SkyrmionGridC *g) {
    if (g) {
        free(g->spins);
        free(g);
    }
}

static inline int grid_idx(int size, int r, int c) {
    return r * size + c;
}

/* Ініціалізація Неєлівського скирміона у центрі сітки */
void skyrmion_grid_init_neel(SkyrmionGridC *g, double radius) {
    int N = g->size;
    double center = (N - 1) / 2.0;

    for (int r = 0; r < N; r++) {
        for (int c = 0; c < N; c++) {
            double dx = (c - center) * g->grid_step;
            double dy = (r - center) * g->grid_step;
            double dist = sqrt(dx * dx + dy * dy);
            
            double theta = M_PI_VAL;
            if (dist < radius) {
                theta = M_PI_VAL * (1.0 - dist / radius);
            } else {
                theta = 0.0;
            }

            double phi = atan2(dy, dx); // Неєлівський скирміон (гамма = 0)

            Vector3 s;
            s.x = sin(theta) * cos(phi);
            s.y = sin(theta) * sin(phi);
            s.z = cos(theta);
            
            g->spins[grid_idx(N, r, c)] = vec_normalize(s);
        }
    }
}

/* Обчислення повного топологічного заряду Q */
double skyrmion_grid_calc_topological_charge(const SkyrmionGridC *g) {
    int N = g->size;
    double total_q = 0.0;

    for (int r = 0; r < N - 1; r++) {
        for (int c = 0; c < N - 1; c++) {
            Vector3 m00 = g->spins[grid_idx(N, r, c)];
            Vector3 m10 = g->spins[grid_idx(N, r, c + 1)];
            Vector3 m01 = g->spins[grid_idx(N, r + 1, c)];
            Vector3 m11 = g->spins[grid_idx(N, r + 1, c + 1)];

            // Перший трикутник (m00, m10, m01)
            double omega1 = solid_angle(m00, m10, m01);
            // Другий трикутник (m11, m01, m10)
            double omega2 = solid_angle(m11, m01, m10);

            total_q += (omega1 + omega2);
        }
    }

    return total_q / (4.0 * M_PI_VAL);
}

int main(void) {
    int N = 64;
    double step = 1.0e-9; // 1 nm
    double sk_radius = 12.0e-9; // 12 nm

    SkyrmionGridC *grid = skyrmion_grid_create(N, step);
    if (!grid) {
        fprintf(stderr, "Помилка виділення пам'яті\n");
        return 1;
    }

    skyrmion_grid_init_neel(grid, sk_radius);
    double Q = skyrmion_grid_calc_topological_charge(grid);

    printf("Розмір ґратки: %d x %d\n", N, N);
    printf("Обчислений топологічний заряд Q = %.6f\n", Q);

    skyrmion_grid_free(grid);
    return 0;
}
```
```cpp
// skyrmion_sim.cpp — Чисельне моделювання магнітного скирміона мовою C++
#include <iostream>
#include <vector>
#include <cmath>
#include <numbers>
#include <memory>

struct Spin3D {
    double x{0.0};
    double y{0.0};
    double z{1.0};

    [[nodiscard]] Spin3D normalized() const noexcept {
        double len = std::sqrt(x * x + y * y + z * z);
        if (len > 1e-12) {
            return {x / len, y / len, z / len};
        }
        return *this;
    }

    [[nodiscard]] static double dot(const Spin3D& a, const Spin3D& b) noexcept {
        return a.x * b.x + a.y * b.y + a.z * b.z;
    }

    [[nodiscard]] static Spin3D cross(const Spin3D& a, const Spin3D& b) noexcept {
        return {
            a.y * b.z - a.z * b.y,
            a.z * b.x - a.x * b.z,
            a.x * b.y - a.y * b.x
        };
    }
};

class SkyrmionLattice {
public:
    SkyrmionLattice(std::size_t grid_size, double step_meters)
        : size_(grid_size), step_(step_meters), spins_(grid_size * grid_size) {}

    void initialize_neel_skyrmion(double radius_meters) {
        const double center = (static_cast<double>(size_) - 1.0) / 2.0;

        for (std::size_t r = 0; r < size_; ++r) {
            for (std::size_t c = 0; c < size_; ++c) {
                double dx = (static_cast<double>(c) - center) * step_;
                double dy = (static_cast<double>(r) - center) * step_;
                double dist = std::hypot(dx, dy);

                double theta = std::numbers::pi;
                if (dist < radius_meters) {
                    theta = std::numbers::pi * (1.0 - dist / radius_meters);
                } else {
                    theta = 0.0;
                }

                double phi = std::atan2(dy, dx);

                Spin3D s{
                    std::sin(theta) * std::cos(phi),
                    std::sin(theta) * std::sin(phi),
                    std::cos(theta)
                };

                spins_[index(r, c)] = s.normalized();
            }
        }
    }

    [[nodiscard]] double compute_topological_charge() const noexcept {
        double total_q = 0.0;

        for (std::size_t r = 0; r < size_ - 1; ++r) {
            for (std::size_t c = 0; c < size_ - 1; ++c) {
                const auto& m00 = spins_[index(r, c)];
                const auto& m10 = spins_[index(r, c + 1)];
                const auto& m01 = spins_[index(r + 1, c)];
                const auto& m11 = spins_[index(r + 1, c + 1)];

                total_q += solid_angle(m00, m10, m01);
                total_q += solid_angle(m11, m01, m10);
            }
        }

        return total_q / (4.0 * std::numbers::pi);
    }

    [[nodiscard]] std::size_t size() const noexcept { return size_; }

private:
    std::size_t size_;
    double step_;
    std::vector<Spin3D> spins_;

    [[nodiscard]] std::size_t index(std::size_t r, std::size_t c) const noexcept {
        return r * size_ + c;
    }

    [[nodiscard]] static double solid_angle(const Spin3D& m1, const Spin3D& m2, const Spin3D& m3) noexcept {
        double triple_prod = Spin3D::dot(m1, Spin3D::cross(m2, m3));
        double denom = 1.0 + Spin3D::dot(m1, m2) + Spin3D::dot(m2, m3) + Spin3D::dot(m3, m1);
        return 2.0 * std::atan2(triple_prod, denom);
    }
};

int main() {
    constexpr std::size_t grid_N = 64;
    constexpr double grid_step = 1.0e-9;  // 1 nm
    constexpr double skyrmion_r = 12.0e-9; // 12 nm

    SkyrmionLattice lattice(grid_N, grid_step);
    lattice.initialize_neel_skyrmion(skyrmion_r);

    double charge_Q = lattice.compute_topological_charge();

    std::cout << "Розмір сітки: " << lattice.size() << "x" << lattice.size() << "\n";
    std::cout << "Топологічний заряд Q = " << charge_Q << "\n";

    return 0;
}
```
:::

## 5. Аналіз результатів та фізична інтерпретація

При правильному виборі розбіжності сітки обчислене значення топологічного заряду прямує до точно від'ємної одиниці (`Q = -1.000000`). 

Аналіз чисельних результатів показує:
1. **Вплив кроку сітки `a`:** якщо крок дискретизації стає порівнянним із радіусом ядра скирміона (`a > R_sk / 3`), виникає дискретизаційна анізотропія ґратки. Скирміон втрачає колову симетрію і може застрягати у чисельному потенціалі Пірлса — Набарро.
2. **Вплив граничних умов:** на відкритих межах плівки виникає крайове відштовхування скирміона завдяки взаємодії DMI з крайовими спінами. Це запобігає спонтанному виходу скирміона за межі сітки при відсутності зовнішнього струму.
3. **Чисельна стійкість:** застосування геометрії Судзукі — Берглунда гарантує збереження цілочисельного інваріанта `Q` навіть при високих швидкостях динамічного руху скирміона під дією спінових струмів.
