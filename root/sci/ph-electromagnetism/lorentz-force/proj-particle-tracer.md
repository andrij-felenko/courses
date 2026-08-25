# ⚙️ Числовий інтегратор Бориса для траєкторій зарядів у полях E та B

При числовому моделюванні руху зарядженої частинки у магнітному полі стандартні класичні методи чисельного інтегрування звичайних диференціальних рівнянь (такі як простий метод Ейлера чи навіть класичний метод Рунге-Кутти 4-го порядку) показують систематичну незадовільну похибку. Звичайні алгоритми не зберігають фазовий об'єм у просторі й чисельно розганяють або гальмують частинку, змушуючи її циклотронну орбіту по спіралі розкручуватися або згортатися з кожним новим кроком за часом.

Основна фізична причина цього дефекту полягає у тому, що магнітна сила Лоренца `F = q · (v × B)` є строго перпендикулярною до вектора швидкості й не повинна змінювати модуль швидкості та кінетичну енергію. Двоступеневі чисельні апроксимації розносних схем порушують цю перпендикулярність на кожному дискретному кроці. Для збереження постійного орбітального радіуса, кінетичної енергії та збереження симплектичної структури фазового простору у фізиці плазми, астрофізиці та фізиці прискорювачів застосовують **симплектичний алгоритм Бориса** (*Boris algorithm / Boris pusher*, винайдений Дональдом Борисом у 1970 році).

### Ідея та етапи алгоритму Бориса

Алгоритм Бориса елегантно розділяє дію електричного та магнітного полів протягом одного часового кроку `dt`, ізолюючи чисте векторне обертання від прискорення:

1. **Перша половина прискорення електричним полем E:**
   На першому піветапі швидкість змінюється під дією електричної сили на половину кроку за часом `dt / 2`:
   ```
   v_мінус = v^n + (q · E / m) · (dt / 2)
   ```
2. **Чисте векторне обертання магнітним полем B без зміни модуля швидкості:**
   Обчислюється проміжний вектор обертання `t = (q · B / m) · (dt / 2)` та модифікований вектор `s = 2 · t / (1 + |t|²)`.
   Потім виконується двокроковий розворот вектора швидкості `v_мінус` у просторі:
   ```
   v' = v_мінус + v_мінус × t
   v_плюс = v_мінус + v' × s
   ```
   Завдяки такій векторній алгебрі модуль вектора швидкості зберігається з машинною точністю: `|v_плюс| = |v_мінус|`.
3. **Друга половина прискорення електричним полем E:**
   На завершальному піветапі додається друга половина електричного прискорення:
   ```
   v^(n+1) = v_плюс + (q · E / m) · (dt / 2)
   ```
4. **Оновлення просторових координат:**
   Нове положення частинки обчислюється за оновленим вектором швидкості:
   ```
   x^(n+1) = x^n + v^(n+1) · dt
   ```

Завдяки розділенню кроку алгоритм Бориса гарантує відсутність чисельного дрейфу кінетичної енергії на необмежених часових інтервалах моделювання, що робить його незамінним для розрахунку плазмових пасток, токамаків та циклотронів.

### Математичне порівняння з методом Рунге-Кутти (RK4)

Порівняльний аналіз з класичним методом Рунге-Кутти 4-го порядку (RK4) показує фундаментальну перевагу метода Бориса при симуляціях у магнітних полях. Метод RK4 є високоефективним для звичайних диференціальних рівнянь, але він є несимплектичним: при обчисленні комбінації чотирьох проміжних векторів швидкості на кожному кроці модуль підсумкового вектора розраховується з незначною похибкою `O(dt⁵)`. Оскільки похибка одного знака накопичується на кожному з мільйонів циклотронних обертів, у симуляції RK4 радіус Лармора електрона чи протона систематично розкручується по спіралі назовні, створюючи ілюзію неіснуючого фізичного нагріву плазми.

Алгоритм Бориса повністю позбавлений цього недоліку: магнітний розворот `v_плюс` виконується через точну геометричну формулу повороту вектора у 3D-просторі, для якої `|v_плюс|² = |v_мінус|²` зберігається до останнього біта плаваючої коми. Тому інтегратор Бориса демонструє строге збереження кінетичної енергії навіть при інтегруванні на мільярди кроків.

### Вплив точності плаваючої коми (Float32 vs Float64)

При реалізації алгоритму Бориса у реальних обчислювальних комплексах важливим інженерним вибором є точність розрядності чисел з плаваючою комою:
- **Single Precision (float32):** забезпечує вдвічі вищу швидкість обчислень на графічних процесорах (GPU CUDA/OpenCL) та удвічі менший об'єм пам'яті. Проте через малу кількість біт мантиси (23 біти) при накопиченні мільйонів кроків координатичастинки `x = x + v * dt` зазнають накопичення похибок округлення (Loss of Precision), коли `x` стає значно більшим за `v * dt`.
- **Double Precision (float64):** має 52 біти мантиси, що повністю усуває похибки округлення при тривалих симуляціях плазмодинаміки. Використання double є обов'язковим для розрахунку мас-спектрометрів та циклотронів.

### Паралелізація симулятора на графічних прискорювачах (GPU)

Оскільки в алгоритмі Бориса кожна частинка рухається незалежно від інших частинок у зовнішніх полях (без урахування власного кулонівського відштовхування), ця задача є ідеально паралельною (*embarrassingly parallel*). При моделюванні пучків з мільйонів частинок функцію `boris_step` оформлюють у вигляді ядра CUDA (CUDA Kernel), де кожен обчислювальний потік GPU моделює траєкторію однієї частинки. Це дозволяє прискорити симуляцію у 100–500 разів порівняно з послідовним виконання на ЦП (CPU).

### Практична реалізація симулятора Бориса

Нижче наведено робочу реалізацію алгоритму Бориса мовами C++, C та Python для моделювання руху електрона в однорідних та схрещених полях.

:::tabs
```cpp
#include <iostream>
#include <vector>
#include <cmath>
#include <fstream>
#include <iomanip>

struct Vector3 {
    double x{0.0}, y{0.0}, z{0.0};

    Vector3 operator+(const Vector3& o) const { return {x + o.x, y + o.y, z + o.z}; }
    Vector3 operator-(const Vector3& o) const { return {x - o.x, y - o.y, z - o.z}; }
    Vector3 operator*(double s) const { return {x * s, y * s, z * s}; }

    static Vector3 cross(const Vector3& a, const Vector3& b) {
        return {
            a.y * b.z - a.z * b.y,
            a.z * b.x - a.x * b.z,
            a.x * b.y - a.y * b.x
        };
    }

    double norm_sq() const { return x * x + y * y + z * z; }
    double norm() const { return std::sqrt(norm_sq()); }
};

struct Particle {
    Vector3 pos;
    Vector3 vel;
    double charge; // Кл
    double mass;   // кг
};

class BorisIntegrator {
public:
    BorisIntegrator(Particle p, Vector3 E, Vector3 B)
        : particle_(std::move(p)), E_(E), B_(B) {}

    void step(double dt) {
        const double q_over_m = particle_.charge / particle_.mass;
        const Vector3 half_E_step = E_ * (q_over_m * dt * 0.5);

        // 1. Половина прискорення від електричного поля
        Vector3 v_minus = particle_.vel + half_E_step;

        // 2. Обертання в магнітному полі (збереження енергії)
        Vector3 t = B_ * (q_over_m * dt * 0.5);
        double t_sq = t.norm_sq();
        Vector3 s = t * (2.0 / (1.0 + t_sq));

        Vector3 v_prime = v_minus + Vector3::cross(v_minus, t);
        Vector3 v_plus = v_minus + Vector3::cross(v_prime, s);

        // 3. Друга половина прискорення від E-поля
        particle_.vel = v_plus + half_E_step;

        // 4. Зсув координат
        particle_.pos = particle_.pos + particle_.vel * dt;
    }

    const Particle& particle() const { return particle_; }

private:
    Particle particle_;
    Vector3 E_;
    Vector3 B_;
};

int main() {
    // Електрон у магнітному полі B_z = 0.01 Тл
    Particle electron{
        .pos = {0.0, 0.0, 0.0},
        .vel = {1e6, 0.0, 2e5}, // v_x = 10^6 м/с, v_z = 2*10^5 м/с
        .charge = -1.60217663e-19,
        .mass = 9.1093837e-31
    };

    Vector3 E{0.0, 0.0, 0.0};
    Vector3 B{0.0, 0.0, 0.01}; // 100 Гаусів

    BorisIntegrator sim(electron, E, B);

    const double dt = 1e-11; // 10 пікосекунд
    const int steps = 1000;

    std::cout << std::fixed << std::setprecision(4);
    std::cout << "t[ns]\tx[mm]\ty[mm]\tz[mm]\tE_k[eV]\n";

    for (int i = 0; i <= steps; ++i) {
        if (i % 100 == 0) {
            const auto& p = sim.particle();
            double v_sq = p.vel.norm_sq();
            double e_k_ev = (0.5 * p.mass * v_sq) / 1.60217663e-19;
            std::cout << (i * dt * 1e9) << "\t"
                      << (p.pos.x * 1000.0) << "\t"
                      << (p.pos.y * 1000.0) << "\t"
                      << (p.pos.z * 1000.0) << "\t"
                      << e_k_ev << "\n";
        }
        sim.step(dt);
    }
    return 0;
}
```
```c
#include <stdio.h>
#include <math.h>

typedef struct {
    double x, y, z;
} Vector3;

static inline Vector3 vec_add(Vector3 a, Vector3 b) {
    return (Vector3){a.x + b.x, a.y + b.y, a.z + b.z};
}

static inline Vector3 vec_sub(Vector3 a, Vector3 b) {
    return (Vector3){a.x - b.x, a.y - b.y, a.z - b.z};
}

static inline Vector3 vec_scale(Vector3 a, double s) {
    return (Vector3){a.x * s, a.y * s, a.z * s};
}

static inline Vector3 vec_cross(Vector3 a, Vector3 b) {
    return (Vector3){
        a.y * b.z - a.z * b.y,
        a.z * b.x - a.x * b.z,
        a.x * b.y - a.y * b.x
    };
}

static inline double vec_norm_sq(Vector3 a) {
    return a.x * a.x + a.y * a.y + a.z * a.z;
}

typedef struct {
    Vector3 pos;
    Vector3 vel;
    double charge;
    double mass;
} Particle;

void boris_step(Particle *p, Vector3 E, Vector3 B, double dt) {
    double q_over_m = p->charge / p->mass;
    Vector3 half_E = vec_scale(E, q_over_m * dt * 0.5);

    // 1. Половина E-прискорення
    Vector3 v_minus = vec_add(p->vel, half_E);

    // 2. Векторне обертання у полем B
    Vector3 t = vec_scale(B, q_over_m * dt * 0.5);
    double t_sq = vec_norm_sq(t);
    Vector3 s = vec_scale(t, 2.0 / (1.0 + t_sq));

    Vector3 v_prime = vec_add(v_minus, vec_cross(v_minus, t));
    Vector3 v_plus = vec_add(v_minus, vec_cross(v_prime, s));

    // 3. Друга половина E-прискорення
    p->vel = vec_add(v_plus, half_E);

    // 4. Оновлення координат
    p->pos = vec_add(p->pos, vec_scale(p->vel, dt));
}

int main(void) {
    Particle electron = {
        .pos = {0.0, 0.0, 0.0},
        .vel = {1e6, 0.0, 2e5},
        .charge = -1.60217663e-19,
        .mass = 9.1093837e-31
    };

    Vector3 E = {0.0, 0.0, 0.0};
    Vector3 B = {0.0, 0.0, 0.01};
    double dt = 1e-11;

    printf("Step\tX_mm\t\tY_mm\t\tZ_mm\n");
    for (int step = 0; step <= 1000; step++) {
        if (step % 100 == 0) {
            printf("%d\t%.4f\t%.4f\t%.4f\n",
                   step, electron.pos.x * 1e3, electron.pos.y * 1e3, electron.pos.z * 1e3);
        }
        boris_step(&electron, E, B, dt);
    }
    return 0;
}
```
```py
import math

class Particle:
    def __init__(self, x, y, z, vx, vy, vz, charge, mass):
        self.x, self.y, self.z = x, y, z
        self.vx, self.vy, self.vz = vx, vy, vz
        self.charge = charge
        self.mass = mass

def boris_step(p: Particle, Ex: float, Ey: float, Ez: float,
               Bx: float, By: float, Bz: float, dt: float):
    q_m = p.charge / p.mass
    hdt = 0.5 * dt

    # 1. Половина прискорення E
    v_minus_x = p.vx + q_m * Ex * hdt
    v_minus_y = p.vy + q_m * Ey * hdt
    v_minus_z = p.vz + q_m * Ez * hdt

    # 2. Обертання у магнітному полі B
    tx = q_m * Bx * hdt
    ty = q_m * By * hdt
    tz = q_m * Bz * hdt
    t_sq = tx*tx + ty*ty + tz*tz

    sx = 2.0 * tx / (1.0 + t_sq)
    sy = 2.0 * ty / (1.0 + t_sq)
    sz = 2.0 * tz / (1.0 + t_sq)

    # v' = v_minus + v_minus x t
    v_prime_x = v_minus_x + (v_minus_y * tz - v_minus_z * ty)
    v_prime_y = v_minus_y + (v_minus_z * tx - v_minus_x * tz)
    v_prime_z = v_minus_z + (v_minus_x * ty - v_minus_y * tx)

    # v_plus = v_minus + v' x s
    v_plus_x = v_minus_x + (v_prime_y * sz - v_prime_z * sy)
    v_plus_y = v_minus_y + (v_prime_z * sx - v_prime_x * sz)
    v_plus_z = v_minus_z + (v_prime_x * sy - v_prime_y * sx)

    # 3. Друга половина E
    p.vx = v_plus_x + q_m * Ex * hdt
    p.vy = v_plus_y + q_m * Ey * hdt
    p.vz = v_plus_z + q_m * Ez * hdt

    # 4. Координати
    p.x += p.vx * dt
    p.y += p.vy * dt
    p.z += p.vz * dt

# Тестовий запуск
if __name__ == "__main__":
    e = Particle(0, 0, 0, 1e6, 0, 2e5, -1.602e-19, 9.109e-31)
    dt = 1e-11
    print("Step | X (mm) | Y (mm) | Z (mm)")
    for step in range(1001):
        if step % 200 == 0:
            print(f"{step:4d} | {e.x*1e3:7.3f} | {e.y*1e3:7.3f} | {e.z*1e3:7.3f}")
        boris_step(e, 0, 0, 0, 0, 0, 0.01, dt)
```
:::

### Інженерні застереження та критерій стабільності

Головний критерій стійкості чисельного інтегратора Бориса при програмуванні фізичних симуляцій — правильний вибір часового кроку `dt`. Для забезпечення високої точності обертання та відсутності зсуву фази крок часу зобов'язаний задовольняти умові:

```
dt < 0.1 · T_c = 0.1 · (2π · m / (|q| · B))
```

Якщо обрати `dt > T_c / π`, математична апроксимація вектора `s` втрачає стійкість і циклотронна частота чисельно спотворюється. Для електрона у магнітному полі з індукцією 1 Тесла циклотронна частота становить `f_c ≈ 28` ГГц, а період обертання `T_c ≈ 35.7` пікосекунд. Відповідно, крок інтегрування має вибиратися не більшим за 1–3 пікосекунди. При моделюванні у неоднорідних полях крок часу вибирають динамічно за локальним значенням `B(x, y, z)`.
