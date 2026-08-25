# ⚙️ Чисельне інтегрування задачі трьох тіл

Чисельне інтегрування диференціальних рівнянь руху — єдиний метод обчислення траєкторій у загальній задачі трьох тіл через відсутність аналітичного розв'язку у закритій формі. Побудова стійкого солвера вимагає порівняння класичного алгоритму Рунге–Кутти 4-го порядку та сімплектичного інтегратора Йошиди 4-го порядку з урахуванням пом'якшення гравітаційного потенціалу та збереження інваріантів енергії.

### Вибір чисельного алгоритму: RK4 проти сімплектичних методів

Динаміка трьох гравітуючих мас описується Гамільтоновою системою, у якій зберігаються повна енергія `E`, момент імпульсу `L` та фазовий об'єм (теорема Ліувілля). При виборі чисельного інтегратора виникає фундаментальний компроміс між локальною точністю та довгостроковою збереженістю фазової структури.

Гамільтоніан гравітаційної системи трьох тіл має роздільний вигляд `H(q, p) = K(p) + U(q)`, де кинетична енергія `K(p)` залежить лише від імпульсів `p_i = m_i · v_i`, а потенціальна енергія `U(q)` залежить лише від координат `q_i = r_i`.

#### 1. Метод Рунге–Кутти 4-го порядку (RK4)
Класичний метод RK4 дає високу локальну точність з похибкою на кроці `O(dt⁵)`. Він ідеально підходить для короткострокового моделювання та розрахунку складних перехідних траєкторій. Проте RK4 **не є сімплектичним**: на великих часових інтервалах він дисипує або накопичує енергію, через що орбіти повільно спірально розкручуються або згортаються, навіть якщо реальна фізична система не має тертя. Негативна енергетична похибка в RK4 накопичується монотонно зі швидкістю `ΔE ~ O(dt⁴ · t)`.

#### 2. Сімплектичні інтегратори (Leapfrog та метод Йошиди 4-го порядку)
Сімплектичні інтегратори зберігають диференціальну двоформу `dp ∧ dq` фазового простору. Вони точно інтегрують тіньовий Гамільтоніан `H_shadow = H + dt²·H₂ + dt⁴·H₄ + ...`, розташований нескінченно близько до справжнього Гамільтоніана системи `H`. Завдяки цьому похибка по енергії **не зростає лінійно з часом**, а здійснює обмежені коливання навколо точного значення на нескінченних проміжках часу. У працях хаотичної небесної механіки саме сімплектичні схеми забезпечують відсутність штучного згасання чи саморозгону систем.

Математична розкладка вищого порядку Йошиди 4-го порядку будується шляхом композиції симетричних кроків другого порядку `S_2(dt)` з виваженими коефіцієнтами `w₀ = −2^(1/3) / (2 − 2^(1/3))` та `w₁ = 1 / (2 − 2^(1/3))`:
```
S_4(dt) = S_2(w₁·dt) · S_2(w₀·dt) · S_2(w₁·dt)
```
Це скасовує непарні похибки низьких порядків і забезпечує суворий 4-й порядок сімплектичної точності при трьох викликах обчислення прискорень на крок.

Нижче наведено порівняльну таблицю властивостей чисельних методів:

| Метод інтегрування | Порядок точності | Сімплектичний | Збереження енергії `E` | Складність обчислень | Основне призначення |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Ейлер (Euler)** | 1-й порядок | Ні | Катастрофічний дрейф | 1 обчислення сил | Непридатний для орбіт |
| **Семі-імпліцитний Ейлер** | 1-й порядок | Так | Обмежена похибка | 1 обчислення сил | Прості ігри / навчальні демо |
| **Leapfrog / Верле** | 2-й порядок | Так | Відмінне на віках | 1 обчислення сил | Тривале моделювання N тіл |
| **Рунге–Кутта 4 (RK4)** | 4-й порядок | Ні | Повільний дрейф `O(dt⁴·t)` | 4 обчислення сил | Короткі точні розрахунки |
| **Сімплектична Йошида 4** | 4-й порядок | Так | Сувора обмеженість | 3 обчислення сил | Довгострокова небесна механіка |

### Потенціал із пом'якшенням (Gravitational Softening)

При чисельному моделюванні можливе випадкове надзвичайно близьке проходження двох тіл, коли відстань `r_ij → 0`. У фізичному законі `F = G·m₁·m₂ / r²` сила та прискорення прямують до нескінченності, що викликає чисельний вибух (переповнення `double` та катастрофічну втрату точності кроку інтегрування).

Щоб запобігти чисельним збоям, застосовують **параметр пом'якшення** `ε` (softening factor). Модифікована відстань обчислюється як:

```
r_ij = √[(x_j − x_i)² + (y_j − y_i)² + (z_j − z_i)² + ε²]
```

Модифікований пом'якшений потенціал `U_soft` зберігає гладкість та диференційованість при `r_ij → 0`:
```
U_soft = − ∑ G·m_i·m_j / √[r_ij² + ε²]
```

Для точних астрономічних задач без зіткнень задають `ε = 0`, виконуючи адаптивний вибір кроку по часу `dt`. Для демонстраційних та загальних чисельних експериментів обирають `ε ~ 10⁻⁴ ... 10⁻⁸`.

### Опис початкових умов та періодичної хореографії

У наведених далі програмах як тест застосовуються початкові умови для класичної періодичної орбіти-вісімки (Figure-Eight choreography), виявленої Аленом Шенсіне та Річардом Монтгомері у 2000 році. У цій конфігурації три однакові маси `m₁ = m₂ = m₃ = 1.0` рухаються одна за одною по плоскій замкненій траєкторії із рівними фазовими зсувами `T/3`. 

Якщо чисельний інтегратор збереже правильну симетрію та енергію, система з трьох мас виконуватиме стійкий та гарний танок протягом багатьох тисяч періодів. Будь-яка накопичена чисельна похибка швидко деформує вісімку і призводить до розпаду потрійної конфігурації.

Початкові значення вектора стану орбіти-вісімки у канонічній системі одиниць:
- Тіло 1: `pos = (−0.97000436,  0.24308753, 0.0)`, `vel = ( 0.46620531,  0.43236573, 0.0)`
- Тіло 2: `pos = ( 0.97000436, −0.24308753, 0.0)`, `vel = ( 0.46620531,  0.43236573, 0.0)`
- Тіло 3: `pos = ( 0.0,         0.0,        0.0)`, `vel = (−0.93241062, −0.86473146, 0.0)`

### Повна реалізація мовами C та C++

Наведені нижче приклади реалізують векторне чисельне інтегрування гравітаційної задачі трьох тіл у 3D-просторі з використанням сімплектичного алгоритму 4-го порядку (метод Йошиди), а також обчислюють поточну повну енергію системи для контролю збереження величин.

:::tabs
```c
/*
 * three_body.c — Чисельне інтегрування задачі трьох тіл мовою C
 * Сімплектичний інтегратор Йошиди 4-го порядку (Yoshida 4th order integrator)
 */

#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define NUM_BODIES 3
#define G_CONST 1.0
#define SOFTENING_SQ 1e-12

typedef struct {
    double x, y, z;
} Vec3;

typedef struct {
    double mass;
    Vec3 pos;
    Vec3 vel;
    Vec3 acc;
} Body;

/* Обчислення прискорень усіх тіл за законом всесвітнього тяжіння */
static void compute_accelerations(Body bodies[NUM_BODIES]) {
    for (int i = 0; i < NUM_BODIES; i++) {
        bodies[i].acc.x = 0.0;
        bodies[i].acc.y = 0.0;
        bodies[i].acc.z = 0.0;
    }

    for (int i = 0; i < NUM_BODIES; i++) {
        for (int j = i + 1; j < NUM_BODIES; j++) {
            double dx = bodies[j].pos.x - bodies[i].pos.x;
            double dy = bodies[j].pos.y - bodies[i].pos.y;
            double dz = bodies[j].pos.z - bodies[i].pos.z;

            double dist_sq = dx * dx + dy * dy + dz * dz + SOFTENING_SQ;
            double dist = sqrt(dist_sq);
            double inv_dist3 = 1.0 / (dist_sq * dist);

            double f_i = G_CONST * bodies[j].mass * inv_dist3;
            double f_j = G_CONST * bodies[i].mass * inv_dist3;

            bodies[i].acc.x += dx * f_i;
            bodies[i].acc.y += dy * f_i;
            bodies[i].acc.z += dz * f_i;

            bodies[j].acc.x -= dx * f_j;
            bodies[j].acc.y -= dy * f_j;
            bodies[j].acc.z -= dz * f_j;
        }
    }
}

/* Обчислення повної механічної енергії E = K + U */
static double compute_total_energy(const Body bodies[NUM_BODIES]) {
    double kinetic = 0.0;
    double potential = 0.0;

    for (int i = 0; i < NUM_BODIES; i++) {
        double v_sq = bodies[i].vel.x * bodies[i].vel.x +
                      bodies[i].vel.y * bodies[i].vel.y +
                      bodies[i].vel.z * bodies[i].vel.z;
        kinetic += 0.5 * bodies[i].mass * v_sq;

        for (int j = i + 1; j < NUM_BODIES; j++) {
            double dx = bodies[j].pos.x - bodies[i].pos.x;
            double dy = bodies[j].pos.y - bodies[i].pos.y;
            double dz = bodies[j].pos.z - bodies[i].pos.z;
            double dist = sqrt(dx * dx + dy * dy + dz * dz + SOFTENING_SQ);
            potential -= (G_CONST * bodies[i].mass * bodies[j].mass) / dist;
        }
    }
    return kinetic + potential;
}

/* Один крок сімплектичного інтегратора Йошиди 4-го порядку */
static void step_yoshida4(Body bodies[NUM_BODIES], double dt) {
    /* Коефіцієнти Йошиди */
    static const double w0 = -1.7024143839193153;
    static const double w1 =  1.3512071919596578;
    
    static const double c[4] = {
        0.5 * 1.3512071919596578,
        0.5 * (1.3512071919596578 - 1.7024143839193153),
        0.5 * (1.3512071919596578 - 1.7024143839193153),
        0.5 * 1.3512071919596578
    };
    static const double d[3] = {
        1.3512071919596578,
        -1.7024143839193153,
        1.3512071919596578
    };

    for (int step = 0; step < 4; step++) {
        /* Оновлення координат */
        for (int i = 0; i < NUM_BODIES; i++) {
            bodies[i].pos.x += c[step] * bodies[i].vel.x * dt;
            bodies[i].pos.y += c[step] * bodies[i].vel.y * dt;
            bodies[i].pos.z += c[step] * bodies[i].vel.z * dt;
        }

        if (step < 3) {
            compute_accelerations(bodies);
            /* Оновлення швидкостей */
            for (int i = 0; i < NUM_BODIES; i++) {
                bodies[i].vel.x += d[step] * bodies[i].acc.x * dt;
                bodies[i].vel.y += d[step] * bodies[i].acc.y * dt;
                bodies[i].vel.z += d[step] * bodies[i].acc.z * dt;
            }
        }
    }
}

int main(void) {
    /* Початкові умови для класичної орбіти-вісімки (Figure-Eight choreography) */
    Body bodies[NUM_BODIES] = {
        {1.0, {-0.97000436,  0.24308753, 0.0}, { 0.46620531,  0.43236573, 0.0}, {0}},
        {1.0, { 0.97000436, -0.24308753, 0.0}, { 0.46620531,  0.43236573, 0.0}, {0}},
        {1.0, { 0.0,         0.0,        0.0}, {-0.93241062, -0.86473146, 0.0}, {0}}
    };

    double dt = 0.001;
    int steps = 10000;
    double initial_energy = compute_total_energy(bodies);

    printf("=== Симуляція задачі трьох тіл (C / Yoshida 4) ===\n");
    printf("Початкова енергія E0 = %.10f\n", initial_energy);

    for (int k = 1; k <= steps; k++) {
        step_yoshida4(bodies, dt);

        if (k % 2000 == 0) {
            double current_energy = compute_total_energy(bodies);
            double rel_err = fabs((current_energy - initial_energy) / initial_energy);
            printf("Крок %5d | E = %.10f | Відносна похибка E: %.2e\n",
                   k, current_energy, rel_err);
        }
    }

    return 0;
}
```
```cpp
//
// three_body.cpp — Чисельне інтегрування задачі трьох тіл мовою C++20
// Ідіоматична реалізація з RAII, std::array, векторною алгеброю та шаблонами
//

#include <iostream>
#include <array>
#include <cmath>
#include <iomanip>
#include <concepts>

namespace celestial {

// Шаблонна структура 3D-вектора
template <typename T = double>
struct Vector3 {
    T x{0.0}, y{0.0}, z{0.0};

    constexpr Vector3 operator+(const Vector3& rhs) const noexcept {
        return {x + rhs.x, y + rhs.y, z + rhs.z};
    }
    constexpr Vector3 operator-(const Vector3& rhs) const noexcept {
        return {x - rhs.x, y - rhs.y, z - rhs.z};
    }
    constexpr Vector3 operator*(T scalar) const noexcept {
        return {x * scalar, y * scalar, z * scalar};
    }
    constexpr Vector3& operator+=(const Vector3& rhs) noexcept {
        x += rhs.x; y += rhs.y; z += rhs.z;
        return *this;
    }
    [[nodiscard]] double norm_sq() const noexcept {
        return x * x + y * y + z * z;
    }
    [[nodiscard]] double norm() const noexcept {
        return std::sqrt(norm_sq());
    }
};

// Тіло в гравітаційній системі
struct CelestialBody {
    double mass{1.0};
    Vector3<double> pos{};
    Vector3<double> vel{};
    Vector3<double> acc{};
};

template <std::size_t N = 3>
class ThreeBodySystem {
public:
    static constexpr double G = 1.0;
    static constexpr double softening_sq = 1e-12;

    explicit ThreeBodySystem(const std::array<CelestialBody, N>& initial_bodies)
        : bodies_(initial_bodies) {}

    // Обчислення прискорень для всіх тіл (закони Ньютона)
    void update_accelerations() noexcept {
        for (auto& body : bodies_) {
            body.acc = {0.0, 0.0, 0.0};
        }

        for (std::size_t i = 0; i < N; ++i) {
            for (std::size_t j = i + 1; j < N; ++j) {
                Vector3<double> dr = bodies_[j].pos - bodies_[i].pos;
                double dist_sq = dr.norm_sq() + softening_sq;
                double dist = std::sqrt(dist_sq);
                double inv_dist3 = 1.0 / (dist_sq * dist);

                bodies_[i].acc += dr * (G * bodies_[j].mass * inv_dist3);
                bodies_[j].acc += dr * (-G * bodies_[i].mass * inv_dist3);
            }
        }
    }

    // Сімплектичний крок інтегратора Йошиди 4-го порядку
    void step_yoshida4(double dt) noexcept {
        static constexpr std::array<double, 4> c{
            0.5 * 1.3512071919596578,
            0.5 * (1.3512071919596578 - 1.7024143839193153),
            0.5 * (1.3512071919596578 - 1.7024143839193153),
            0.5 * 1.3512071919596578
        };
        static constexpr std::array<double, 3> d{
            1.3512071919596578,
            -1.7024143839193153,
            1.3512071919596578
        };

        for (std::size_t step = 0; step < 4; ++step) {
            for (auto& body : bodies_) {
                body.pos += body.vel * (c[step] * dt);
            }
            if (step < 3) {
                update_accelerations();
                for (auto& body : bodies_) {
                    body.vel += body.acc * (d[step] * dt);
                }
            }
        }
    }

    // Розрахунок повної механічної енергії E
    [[nodiscard]] double total_energy() const noexcept {
        double kinetic = 0.0;
        double potential = 0.0;

        for (std::size_t i = 0; i < N; ++i) {
            kinetic += 0.5 * bodies_[i].mass * bodies_[i].vel.norm_sq();
            for (std::size_t j = i + 1; j < N; ++j) {
                double dist = (bodies_[j].pos - bodies_[i].pos).norm();
                potential -= (G * bodies_[i].mass * bodies_[j].mass) / dist;
            }
        }
        return kinetic + potential;
    }

    [[nodiscard]] const std::array<CelestialBody, N>& bodies() const noexcept {
        return bodies_;
    }

private:
    std::array<CelestialBody, N> bodies_;
};

} // namespace celestial

int main() {
    using namespace celestial;

    // Початкові умови: орбіта-вісімка (Figure-Eight choreography)
    const std::array<CelestialBody, 3> figure_eight_setup{{
        {1.0, {-0.97000436,  0.24308753, 0.0}, { 0.46620531,  0.43236573, 0.0}, {}},
        {1.0, { 0.97000436, -0.24308753, 0.0}, { 0.46620531,  0.43236573, 0.0}, {}},
        {1.0, { 0.0,         0.0,        0.0}, {-0.93241062, -0.86473146, 0.0}, {}}
    }};

    ThreeBodySystem<3> system(figure_eight_setup);
    const double initial_energy = system.total_energy();
    const double dt = 0.001;
    const int total_steps = 10000;

    std::cout << std::fixed << std::setprecision(10);
    std::cout << "=== Симуляція задачі трьох тіл (C++20 / Yoshida 4) ===\n";
    std::cout << "Початкова енергія E0 = " << initial_energy << "\n";

    for (int k = 1; k <= total_steps; ++k) {
        system.step_yoshida4(dt);

        if (k % 2000 == 0) {
            double current_energy = system.total_energy();
            double rel_err = std::abs((current_energy - initial_energy) / initial_energy);
            std::cout << "Крок " << std::setw(5) << k
                      << " | E = " << current_energy
                      << " | Відносна похибка E: " << std::scientific << rel_err << std::defaultfloat << "\n";
        }
    }

    return 0;
}
```
:::

### Детальний порівняльний аналіз кодів C та C++

Аналіз структури обох програм показує важливі архітектурні відмінності між підходами мов C та C++ у сфері обчислювальної механіки:
1. **Керування даними та стек**: У версії C застосовується плоский масив структур `Body bodies[3]`. Обчислення прискорень відбувається у процедурному стилі через передачу вказівників. У версії C++20 використовується шаблонний клас `ThreeBodySystem<N>` із `std::array<CelestialBody, N>`, що гарантує відсутність динамічного виділення пам'яті у купі (heap allocation) та повну розгортку циклів на етапі компіляції.
2. **Векторна алгебра**: Мова C++ дозволяє перевантажити оператори `+`, `-`, `*`, `+=` для шаблону `Vector3<T>`, що робить математичні вирази оновлення прискорень та координат ітотожними до шкільних векторних формул. Мова C вимагає явного оновлення кожної скалярної компоненти `x`, `y`, `z` вручну.
3. **Оптимізація та нульовий оверхед (Zero-Overhead Abstraction)**: Завдяки специфікаторам `constexpr`, `noexcept` та `[[nodiscard]]` сучасні компілятори (GCC, Clang, MSVC) ґенерують для C++ однаково ефективний машинний код, як і для чистого C, повністю інлайнячи методи класу `Vector3`.

### Практичні поради з оптимізації та аналізу симуляцій

1. **Адаптивний крок по часу (Adaptive Timestepping)**: У відкритих хаотичних системах, де можливі дуже близькі прольоти тіл, крок `dt` рекомендується обирати динамічно: `dt = η · min(r_ij / |v_ij|)`, де `η ~ 10⁻³ ... 10⁻²`.
2. **Контроль інваріантів**: Регулярно перевіряйте відносну похибку збереження енергії `|ΔE / E0|` та моменту імпульсу `|ΔL / L0|`. Якщо похибка перевищує `10⁻⁶`, зменшуйте крок або переходьте на вищий порядок сімплектичного інтегратора.
3. **Обчислення експоненти Ляпунова**: Для визначення межі передбачуваності конкретної траєкторії паралельно інтегрують основне тіло та його тіньового дублера з початковим зсувом `Δr₀ = 10⁻⁸`. Оцінка максимального показника Ляпунова `λ ≈ (1/t) · ln(|Δr(t)| / |Δr₀|)` дає зворотну величину часу хаотичного розходження (час Ляпунова `t_Lyapunov = 1/λ`).
4. **Використання симетрії та SIMD-векторизації**: При чисельному моделюванні багатьох варіантів орбіт обчислення парних відстаней `1 / r_ij³` оптимізують через векторизовані інструкції AVX-512 чи ARM Neon, паралельно обчислюючи 4 або 8 взаємодій одночасно.
