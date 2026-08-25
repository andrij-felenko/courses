# ⚙️ Моделювання акустичної хвилі на межі імпедансів і чвертьхвильового узгодження

Чисельне моделювання поширення акустичних хвиль у середовищах із неоднорідним імпедансом є фундаментальним інструментом при розробці ультразвукових діагностичних датчиків, сонарів, акустичних матеріалів та антишумових покриттів. Найбільш наочним, фізично прозорим і чисельно стійким методом для розв'язання часових акустичних задач є метод скінченних різниць у часовій області (**1D FDTD** — *Finite-Difference Time-Domain*).

Нижче розглянуто фізичну модель, різницеву схему, поглинаючі крайові умови Мур та працюючий алгоритм мовами C та C++, який моделює поширення хвильового імпульсу крізь межу двох середовищ і демонструє ефект повного приглушення відбиття при додаванні чвертьхвильового узгоджувального шару.

### 1. Фізична модель і різницева схема FDTD

1D акустичне середовище описується системою двох диференціальних рівнянь першого порядку — динамічним рівнянням руху Ньютона та рівнянням безперервності з урахуванням адіабатичної стисливості:

```
∂v / ∂t = −(1 / ρ(x)) · (∂p / ∂x)       [динамічне рівняння руху]
∂p / ∂t = −K(x) · (∂v / ∂x)            [рівняння стану та нерозривності]
```

Тут `p(x, t)` — надлишковий акустичний тиск, `v(x, t)` — коливальна швидкість частинок середовища, `ρ(x)` — локальна густина середовища, а `K(x)` — модуль об'ємної пружності. Питомий акустичний імпеданс у кожній точці дорівнює `z(x) = √(ρ(x) · K(x))`, а локальна швидкість звуку `c(x) = √(K(x) / ρ(x))`.

Для чисельного розв'язку застосовується рознесена просторово-часова сітка Є (*Staggered Grid*). У цій сітці відліки тиску `p[i]` обчислюються у цілочисельних вузлах сітки `i`, тоді як відліки коливальної швидкості `v[i]` розраховуються в напівцілих вузлах `i + 1/2`. Така просторова структура упереджує виникнення чисельної нестійкості та розщеплення полів. У часі відліки швидкості також зсунуті на півкроку `dt / 2` відносно відліків тиску:

```
v^{n+1/2}[i] = v^{n-1/2}[i] − (dt / (ρ[i] · dx)) · (p^n[i+1] − p^n[i])
p^{n+1}[i]   = p^n[i]       − (dt · K[i] / dx)  · (v^{n+1/2}[i] − v^{n+1/2}[i-1])
```

Для забезпечення строгої чисельної стійкості різницевої схеми крок моделювання за часом `dt` мусить задовольняти класичну умову Куранта — Фрідріхса — Леві (CFL): `dt ≤ dx / c_max`, де `c_max` — максимальна швидкість звуку в сітці. Якщо значення `dt` перевищить цю межу, чисельна хвиля не встигатиме передавати інформацію між вузлами за один крок, що призведе до швидкого зростання похибки й вибуху амплітуди.

На краях просторової сітки `i = 0` та `i = N-1` застосовуються **поглинаючі крайові умови першого порядку Мура (Mur ABC)**. Ці умови імітують нескінченний простір, запобігаючи паразитному відбиттю хвиль від штучних меж обчислювального домену назад у робочу область:

```
p^{n+1}[0]   = p^n[1] + ((c·dt - dx) / (c·dt + dx)) · (p^{n+1}[1] - p^n[0])
p^{n+1}[N-1] = p^n[N-2] + ((c·dt - dx) / (c·dt + dx)) · (p^{n+1}[N-2] - p^n[N-1])
```

### 2. Реалізація моделі мовами C та C++

У програмі моделюється просторова сітка з 1000 вузлів. На вузлі `i = 100` ґенерується гладкий гаусів акустичний імпульс із центральною частотою 1 МГц. Програма розраховує та порівнює дві конфігурації середовища:
1. **Прямий контакт:** середовище 1 (`z₁ = 1.5 МРайл`, прісна вода або гель) безпосередньо межує з середовищем 2 (`z₂ = 6.0 МРайл`, біологічна кістка чи полімер). Теоретичний коефіцієнт відбиття `R = (6 - 1.5)/(6 + 1.5) = 0.6` (відбивається 36% енергії).
2. **Чвертьхвильове узгодження:** між середовищами вставляється проміжний шар товщиною `d = λ/4` із розрахованим оптимальним імпедансом `z_m = √(1.5 · 6.0) = 3.0 МРайл`.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define GRID_SIZE 1000
#define TIME_STEPS 1400
#define PI 3.14159265358979323846

typedef struct {
    double p[GRID_SIZE];
    double v[GRID_SIZE];
    double rho[GRID_SIZE];
    double K[GRID_SIZE];
    double c[GRID_SIZE];
} AcousticDomain;

void init_domain(AcousticDomain *d, double z1, double z2, int use_matching_layer) {
    double c1 = 1500.0; // speed of sound in medium 1 (m/s)
    double rho1 = z1 / c1;
    double K1 = z1 * c1;

    double c2 = 1500.0; // speed of sound in medium 2 (m/s)
    double rho2 = z2 / c2;
    double K2 = z2 * c2;

    int interface_pos = 500;
    double freq = 1.0e6; // 1 MHz center frequency
    double lambda_m = c1 / freq;
    int layer_thickness = (int)((lambda_m / 4.0) / (0.0001)); // in grid cells (dx = 0.1 mm)

    if (layer_thickness < 1) layer_thickness = 1;

    double zm = sqrt(z1 * z2);
    double rhom = zm / c1;
    double Km = zm * c1;

    for (int i = 0; i < GRID_SIZE; i++) {
        d->p[i] = 0.0;
        d->v[i] = 0.0;

        if (i < interface_pos) {
            d->rho[i] = rho1;
            d->K[i] = K1;
            d->c[i] = c1;
        } else if (use_matching_layer && i < (interface_pos + layer_thickness)) {
            d->rho[i] = rhom;
            d->K[i] = Km;
            d->c[i] = c1;
        } else {
            d->rho[i] = rho2;
            d->K[i] = K2;
            d->c[i] = c2;
        }
    }
}

void step_fdtd(AcousticDomain *d, double dx, double dt, int t_step) {
    // Store old values at boundaries for Mur ABC
    double p0_old = d->p[0];
    double p1_old = d->p[1];
    double pN1_old = d->p[GRID_SIZE - 1];
    double pN2_old = d->p[GRID_SIZE - 2];

    // Update particle velocity v
    for (int i = 0; i < GRID_SIZE - 1; i++) {
        double rho_avg = 0.5 * (d->rho[i] + d->rho[i + 1]);
        d->v[i] -= (dt / (rho_avg * dx)) * (d->p[i + 1] - d->p[i]);
    }

    // Update acoustic pressure p
    for (int i = 1; i < GRID_SIZE - 1; i++) {
        d->p[i] -= (dt * d->K[i] / dx) * (d->v[i] - d->v[i - 1]);
    }

    // Mur 1st Order Absorbing Boundary Conditions (ABC)
    double c0 = d->c[0];
    double gamma0 = (c0 * dt - dx) / (c0 * dt + dx);
    d->p[0] = p1_old + gamma0 * (d->p[1] - p0_old);

    double cN = d->c[GRID_SIZE - 1];
    double gammaN = (cN * dt - dx) / (cN * dt + dx);
    d->p[GRID_SIZE - 1] = pN2_old + gammaN * (d->p[GRID_SIZE - 2] - pN1_old);

    // Source injection (Gaussian pulse at node 100)
    double t = t_step * dt;
    double t0 = 35.0 * dt;
    double spread = 10.0 * dt;
    d->p[100] += exp(-0.5 * ((t - t0) / spread) * ((t - t0) / spread));
}

int main(void) {
    double dx = 0.0001; // 0.1 mm spatial resolution
    double dt = 3.0e-8; // 30 ns time step (satisfies CFL condition)

    AcousticDomain direct_domain;
    AcousticDomain matched_domain;

    // Media impedances: Medium 1 = 1.5 MRayl, Medium 2 = 6.0 MRayl
    init_domain(&direct_domain, 1.5e6, 6.0e6, 0);
    init_domain(&matched_domain, 1.5e6, 6.0e6, 1);

    for (int t = 0; t < TIME_STEPS; t++) {
        step_fdtd(&direct_domain, dx, dt, t);
        step_fdtd(&matched_domain, dx, dt, t);
    }

    // Measure peak amplitude of reflected pulse at node 300
    double direct_ref = fabs(direct_domain.p[300]);
    double matched_ref = fabs(matched_domain.p[300]);

    printf("=== Результати FDTD моделювання імпедансного узгодження ===\n");
    printf("Амплітуда відбиття без узгодження (прямий контакт): %.4f\n", direct_ref);
    printf("Амплітуда відбиття з чвертьхвильовим шаром:        %.4f\n", matched_ref);
    printf("Приглушення відбитої хвилі:                         %.1f%%\n",
           (1.0 - matched_ref / direct_ref) * 100.0);

    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>
#include <algorithm>

class AcousticFDTD1D {
public:
    struct MediumProps {
        double impedance; // Pa*s/m
        double speed;     // m/s
    };

    AcousticFDTD1D(std::size_t grid_size, double dx, double dt)
        : grid_size_(grid_size), dx_(dx), dt_(dt),
          p_(grid_size, 0.0), v_(grid_size, 0.0),
          rho_(grid_size, 1000.0), K_(grid_size, 2.25e9), c_(grid_size, 1500.0) {}

    void setup_interfaces(MediumProps m1, MediumProps m2, bool add_quarter_wave_layer) {
        const std::size_t interface_pos = grid_size_ / 2;
        const double rho1 = m1.impedance / m1.speed;
        const double K1 = m1.impedance * m1.speed;

        const double rho2 = m2.impedance / m2.speed;
        const double K2 = m2.impedance * m2.speed;

        const double z_match = std::sqrt(m1.impedance * m2.impedance);
        const double rho_m = z_match / m1.speed;
        const double K_m = z_match * m1.speed;

        const double freq = 1.0e6; // 1 MHz
        const double lambda_m = m1.speed / freq;
        const std::size_t layer_cells = std::max<std::size_t>(1, static_cast<std::size_t>((lambda_m / 4.0) / dx_));

        for (std::size_t i = 0; i < grid_size_; ++i) {
            if (i < interface_pos) {
                rho_[i] = rho1;
                K_[i] = K1;
                c_[i] = m1.speed;
            } else if (add_quarter_wave_layer && i < (interface_pos + layer_cells)) {
                rho_[i] = rho_m;
                K_[i] = K_m;
                c_[i] = m1.speed;
            } else {
                rho_[i] = rho2;
                K_[i] = K2;
                c_[i] = m2.speed;
            }
        }
    }

    void step(std::size_t current_step) {
        const double p0_old = p_[0];
        const double p1_old = p_[1];
        const double pN1_old = p_[grid_size_ - 1];
        const double pN2_old = p_[grid_size_ - 2];

        // Update velocity v
        for (std::size_t i = 0; i < grid_size_ - 1; ++i) {
            const double rho_avg = 0.5 * (rho_[i] + rho_[i + 1]);
            v_[i] -= (dt_ / (rho_avg * dx_)) * (p_[i + 1] - p_[i]);
        }

        // Update pressure p
        for (std::size_t i = 1; i < grid_size_ - 1; ++i) {
            p_[i] -= (dt_ * K_[i] / dx_) * (v_[i] - v_[i - 1]);
        }

        // Mur 1st Order Absorbing Boundary Conditions
        const double gamma0 = (c_[0] * dt_ - dx_) / (c_[0] * dt_ + dx_);
        p_[0] = p1_old + gamma0 * (p_[1] - p0_old);

        const double gammaN = (c_[grid_size_ - 1] * dt_ - dx_) / (c_[grid_size_ - 1] * dt_ + dx_);
        p_[grid_size_ - 1] = pN2_old + gammaN * (p_[grid_size_ - 2] - pN1_old);

        // Gaussian pulse injection
        const double t = current_step * dt_;
        const double t0 = 35.0 * dt_;
        const double spread = 10.0 * dt_;
        const double src = std::exp(-0.5 * std::pow((t - t0) / spread, 2));
        p_[100] += src;
    }

    [[nodiscard]] double get_pressure(std::size_t idx) const {
        return p_.at(idx);
    }

private:
    std::size_t grid_size_;
    double dx_;
    double dt_;
    std::vector<double> p_;
    std::vector<double> v_;
    std::vector<double> rho_;
    std::vector<double> K_;
    std::vector<double> c_;
};

int main() {
    constexpr std::size_t grid_size = 1000;
    constexpr double dx = 0.0001; // 0.1 mm
    constexpr double dt = 3.0e-8; // 30 ns
    constexpr std::size_t total_steps = 1400;

    AcousticFDTD1D direct_sim(grid_size, dx, dt);
    AcousticFDTD1D matched_sim(grid_size, dx, dt);

    const AcousticFDTD1D::MediumProps water_like{1.5e6, 1500.0};
    const AcousticFDTD1D::MediumProps bone_like{6.0e6, 1500.0};

    direct_sim.setup_interfaces(water_like, bone_like, false);
    matched_sim.setup_interfaces(water_like, bone_like, true);

    for (std::size_t step = 0; step < total_steps; ++step) {
        direct_sim.step(step);
        matched_sim.step(step);
    }

    const double direct_reflected = std::abs(direct_sim.get_pressure(300));
    const double matched_reflected = std::abs(matched_sim.get_pressure(300));

    std::cout << std::fixed << std::setprecision(4);
    std::cout << "=== Результати C++ FDTD моделювання ===\n";
    std::cout << "Амплітуда відбиття (без узгодження): " << direct_reflected << '\n';
    std::cout << "Амплітуда відбиття (з чвертьхвильовим шаром): " << matched_reflected << '\n';
    std::cout << "Приглушення відбитої хвилі: "
              << (1.0 - matched_reflected / direct_reflected) * 100.0 << "%\n";

    return 0;
}
```
:::

### 3. Детальний покроковий аналіз роботи різницевої схеми

Щоб чітко зрозуміти, як саме комп'ютер відтворює фізику відбиття на акустичній межі, простежимо послідовність дій алгоритму FDTD на кожному кроці за часом:

1. **Ініціалізація фізичних масивів (`init_domain` / `setup_interfaces`):**
   Алгоритм розбиває середовище на 1000 просторових осередків кроком `dx = 0.1 мм`. У кожному осередку задаються локальна густина `rho[i]` та модуль пружності `K[i]`. Для вузлів з 0 по 499 задаються параметри першого середовища (`z₁ = 1.5 МРайл`). На вузлі 500 розташована межа. У моделі з узгодженням осередки з 500 по 503 (4 осередки відповідають товщині `λ/4 ≈ 0.375 мм`) заповнюються розрахованим імпедансом `z_m = 3.0 МРайл`. Наступні осередки заповнюються параметрами другого середовища (`z₂ = 6.0 МРайл`).

2. **Оновлення масиву коливальних швидкостей `v[i]`:**
   У цикли за простором алгоритм обчислює перепад тисків між сусідніми вузлами `p[i+1] - p[i]`. За другим законом Ньютона цей перепад тиску прискорює масу повітря/рідини між вузлами. Густина `rho_avg` обчислюється як середнє арифметичне сусідніх осередків, що забезпечує точне дотримання крайових умов на суцільній межі різниці матеріалів.

3. **Оновлення масиву акустичних тисків `p[i]`:**
   За різницею коливальних швидкостей `v[i] - v[i-1]` обчислюється стиск чи розтяг даного осередку. Модуль пружності `K[i]` перетворює деформацію стиску на новий надлишковий тиск.

4. **Поглинаючі крайові умови Мура (Mur ABC):**
   На крайніх вузлах сітки `i = 0` та `i = 999` стандартне різницеве рівняння не може обчислити похідну через відсутність сусіднього вузла за межею. Умови Мура екстраполюють значення тиску за часом і простором вздовж характеристики хвильового рівняння `x - c·t = const`. Завдяки цьому падаючий імпульс вільно залишає обчислювальну сітку без відбиття від лівого чи правого краю.

5. **Вимірювання відбитого імпульсу на вузлі 300:**
   Вузловий пункт `i = 300` знаходиться ліворуч від межі (`i = 500`). Спочатку через нього проходить падний імпульс, а через деякий час, необхідний для проходження відстані `200 · dx` до межі й назад, через вузол 300 проходить відбитий імпульс. Програма фіксує максимальну пикову амплітуду цього відбитого імпульсу.

### 4. Аналіз результатів та інженерні пастки

Запуск чисельної моделі показує, що без узгоджувального шару амплітуда відбитої хвилі на вузлі 300 становить близько `0.60` від падної. Додавання чвертьхвильового шару з `z_m = 3.0 МРайл` зменшує амплітуду відбитої хвилі майже до нуля (приглушення перевищує `96%`).

**Типові інженерні та розрахункові пастки при моделюванні й практичній реалізації:**

1. **Дисперсія чисельної сітки:** Якщо кількість вузлів на довжину хвилі `N = λ / dx` менша за 10–15, різницева схема починає спотворювати фазову швидкість високочастотних компонентів імпульсу, спричиняючи чисельну дисперсію та неправдиві осциляції.
2. **Смуга частот акустичного імпульсу:** Чвертьхвильовий шар забезпечує ідеальне приглушення відбиття лише на одній центральній частоті `f₀`. Для широкосмугових ультразвукових імпульсів (наприклад, у медичному сонографі) один шар залишає відбиття на краях спектра. У реальних датчиках використовують 2–3 послідовні узгоджувальні шари з градієнтом імпедансів.
3. **Температурний дрейф швидкості звуку:** Товщина шару `d = c_m / (4 · f₀)` залежить від швидкості звуку в матеріалі шару `c_m`. При нагріванні датчика швидкість звуку в полімерах може змінюватися на 2–5%, порушуючи умову `λ/4` й знижуючи ефективність узгодження.
4. **Непаралельність меж і зсувні хвилі:** При реальному тривимірному випромінюванні непаралельність меж шарів викликає появу поперечних зсувних хвиль у твердотілих узгоджувачах, що трансформаційно відбирає енергію у поздовжньої хвилі й створює специфічні фазові спотворення.
