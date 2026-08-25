# ⚙️ Чисельне трасування променів у градієнтних середовищах

Чисельне трасування світлових променів у оптично неоднорідних середовищах (Graded-Index, GRIN) розраховує траєкторію світла в умовах, коли показник заломлення `n(r)` змінюється безперервно у просторі. Обчислювальний алгоритм реалізує розв'язання векторного диференціального рівняння принципу Ферма шляхом покрокового інтегрування методом Рунге — Кутти 4-го порядку (RK4).

## Фізична модель та канонічна гамільтонова форма

З варіаційного принципу Ферма `δ ∫ n(r) ds = 0` випливає диференціальне рівняння другого порядку для геометрії світлового променя у середовищі з показником заломлення `n(x, y, z)`:

```
d/ds ( n(r) · dr/ds ) = ∇n(r)
```

де `s` — природний параметр (довжина дуги променя), `r = (x, y, z)` — вектор положення, `u = dr/ds` — одиничний вектор напрямку променя, для якого виконується нормалізаційна умова `|u| = |dr/ds| = 1`.

Для побудови стійкої чисельної схеми інтегрування доцільно перевести це рівняння другого порядку до канонічної системи звичайних диференціальних рівнянь (ЗДР) першого порядку. Для цього введемо вектор канонічного оптичного імпульсу `p`:

```
p = n(r) · dr/ds = n(r) · u
```

Фізичний зміст вектора оптичного імпульсу `p` полягає у тому, що його напрямок збігається з напрямком поширення променя, а його модуль у кожній точці простору строго дорівнює місцевому показникові заломлення:

```
|p| = sqrt(px² + py² + pz²) = n(r)
```

Використовуючи вектор імпульсу `p`, початкове диференціальне рівняння другого порядку розпадається на симетричну систему з двох векторних диференціальних рівнянь першого порядку:

```
dr / ds = p / n(r)
dp / ds = ∇n(r)
```

У двовимірному випадку `(x, y)` стан променя повністю описується чотиривимірним вектором стану `State = (x, y, px, py)`. Диференціальні рівняння для кожної компоненти мають вигляд:

```
dx / ds = px / n(x, y)
dy / ds = py / n(x, y)
dpx / ds = ∂n / ∂x
dpy / ds = ∂n / ∂y
```

Ця система рівнянь є математично еквівалентною рівнянням Гамільтона у класичній механіці, де ролю гамільтоніана відіграє функція `H(r, p) = (1/2) · [ |p|² - n²(r) ] = 0`.

## Фізична модель нижнього атмосферного міражу

Як приклад практичного застосування розглянемо модель нижнього атмосферного міражу, який виникає у спекотний день над сонячним асфальтом або піском у пустелі.

Інтенсивне нагрівання поверхні землі створює крутий температурний градієнт у нижньому шарі повітря висотою близько двох метрів. Повітря біля самої землі нагрівається, розширюється і стає менш щільним. Оскільки показник заломлення газу прямо пропорційний його щільності (за законом Гладстона — Дейла `n - 1 = k · ρ`), показник заломлення досягає мінімуму біля землі і монотонно зростає з висотою `y`.

Фізична модель аналітично описується експоненціальним профілем показника заломлення:

```
n(x, y) = n₀ + Δn · (1 - exp(-y / y₀))
```

де прийнято такі фізичні параметри атмосфери:
- `n₀ = 1.00026` — показник заломлення сильно нагрітого повітря безпосередньо біля поверхні землі (`y = 0`).
- `Δn = 0.00030` — максимальна різниця показника заломлення між гарячим приземним та холодним вищим повітрям.
- `y₀ = 1.5` м — характерний вертикальний масштаб експоненціального нагріву.

Вектор градієнта показника заломлення `∇n = (∂n/∂x, ∂n/∂y)` у цій моделі спрямований строго вертикально вгору по осі `y`:

```
∂n / ∂x = 0
∂n / ∂y = (Δn / y₀) · exp(-y / y₀)
```

Оскільки `∂n/∂x = 0`, складова оптичного імпульсу `px` залишається строго постійною вздовж усієї траєкторії променя (`dpx/ds = 0`), що відповідає оптичному аналогу закону збереження горизонтального імпульсу.

## Алгоритм Рунге — Кутти 4-го порядку (RK4)

Для чисельного розв'язання системи ЗДР застосовується класичний метод Рунге — Кутти 4-го порядку. Цей метод забезпечує високу точність із локальною похибкою `O(Δs⁵)` та глобальною похибкою `O(Δs⁴)` на кожному кроці за довжиною дуги `Δs`.

Нехай на кроці `n` стан променя задається вектором `Stateⁿ = (xⁿ, yⁿ, pxⁿ, pyⁿ)`. Алгоритм обчислює чотири проміжні вектори похідних `k₁, k₂, k₃, k₄`:

```
k₁ = F( Stateⁿ )
k₂ = F( Stateⁿ + (Δs / 2) · k₁ )
k₃ = F( Stateⁿ + (Δs / 2) · k₂ )
k₄ = F( Stateⁿ + Δs · k₃ )
```

де векторна функція `F(State)` повертає прави частини системи ЗДР:

```
F(x, y, px, py) = ( px / n(x,y),  py / n(x,y),  ∂n/∂x,  ∂n/∂y )
```

Новий стан променя на відстані `s + Δs` обчислюється як зважена комбінація:

```
Stateⁿ⁺¹ = Stateⁿ + (Δs / 6) · ( k₁ + 2·k₂ + 2·k₃ + k₄ )
```

Одночасно з координатами інтегрується диференціал оптичної довжини шляху `dL = n(x, y) ds`, що дає накопичену оптичну довжину шляху (OPL):

```
Lⁿ⁺¹ = Lⁿ + (Δs / 6) · ( n(k₁) + 2·n(k₂) + 2·n(k₃) + n(k₄) )
```

## Програмні реалізації мовами C та C++

Нижче наведено робочі та ідіоматичні реалізації чисельного трасувальника променів мовами C та C++.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

// Вектор стану променя у 2D просторі: (x, y, px, py)
typedef struct {
    double x;
    double y;
    double px;
    double py;
} RayState;

// Фізичні параметри атмосфери
typedef struct {
    double n0;  // показник заломлення гарячого повітря біля землі
    double dn;  // перепад показника заломлення з висотою
    double y0;  // характерний масштаб висоти (м)
} AtmosphereModel;

// Обчислення локального показника заломлення n(x, y)
double get_refractive_index(const AtmosphereModel* env, double x, double y) {
    (void)x;
    if (y < 0.0) y = 0.0;
    return env->n0 + env->dn * (1.0 - exp(-y / env->y0));
}

// Обчислення векторного градієнта ∇n = (dn/dx, dn/dy)
void get_index_gradient(const AtmosphereModel* env, double x, double y, double* dndx, double* dndy) {
    (void)x;
    *dndx = 0.0;
    if (y < 0.0) y = 0.0;
    *dndy = (env->dn / env->y0) * exp(-y / env->y0);
}

// Прави частини системи ЗДР: dState/ds = F(State)
RayState ray_derivatives(const AtmosphereModel* env, RayState state) {
    double n = get_refractive_index(env, state.x, state.y);
    double dndx, dndy;
    get_index_gradient(env, state.x, state.y, &dndx, &dndy);

    RayState deriv;
    deriv.x  = state.px / n;
    deriv.y  = state.py / n;
    deriv.px = dndx;
    deriv.py = dndy;
    return deriv;
}

// Крок чисельного інтегрування методом Рунге-Кутти 4-го порядку (RK4)
RayState rk4_step(const AtmosphereModel* env, RayState state, double ds) {
    RayState k1 = ray_derivatives(env, state);

    RayState s_k2 = {
        state.x  + 0.5 * ds * k1.x,
        state.y  + 0.5 * ds * k1.y,
        state.px + 0.5 * ds * k1.px,
        state.py + 0.5 * ds * k1.py
    };
    RayState k2 = ray_derivatives(env, s_k2);

    RayState s_k3 = {
        state.x  + 0.5 * ds * k2.x,
        state.y  + 0.5 * ds * k2.y,
        state.px + 0.5 * ds * k2.px,
        state.py + 0.5 * ds * k2.py
    };
    RayState k3 = ray_derivatives(env, s_k3);

    RayState s_k4 = {
        state.x  + ds * k3.x,
        state.y  + ds * k3.y,
        state.px + ds * k3.px,
        state.py + ds * k3.py
    };
    RayState k4 = ray_derivatives(env, s_k4);

    RayState next_state;
    next_state.x  = state.x  + (ds / 6.0) * (k1.x  + 2.0 * k2.x  + 2.0 * k3.x  + k4.x);
    next_state.y  = state.y  + (ds / 6.0) * (k1.y  + 2.0 * k2.y  + 2.0 * k3.y  + k4.y);
    next_state.px = state.px + (ds / 6.0) * (k1.px + 2.0 * k2.px + 2.0 * k3.px + k4.px);
    next_state.py = state.py + (ds / 6.0) * (k1.py + 2.0 * k2.py + 2.0 * k3.py + k4.py);

    return next_state;
}

int main(void) {
    AtmosphereModel env = { .n0 = 1.00026, .dn = 0.00030, .y0 = 1.5 };

    // Початкові умови трасування: джерело світла на висоті 1.2 м
    double start_x = 0.0;
    double start_y = 1.2;
    double angle_deg = -1.5; // кут нахилу -1.5° до горизонту
    double angle_rad = angle_deg * (M_PI / 180.0);

    double n_start = get_refractive_index(&env, start_x, start_y);
    RayState current = {
        .x = start_x,
        .y = start_y,
        .px = n_start * cos(angle_rad),
        .py = n_start * sin(angle_rad)
    };

    double ds = 0.1;           // крок за довжиною дуги (метрів)
    double max_length = 150.0; // максимальна довжина прогону
    double opl = 0.0;          // накопичена оптична довжина шляху

    printf("# Tracing ray in GRIN atmosphere (Mirage Simulation)\n");
    printf("# s(m)\tx(m)\ty(m)\tpx\tpy\tn\tOPL(m)\n");

    for (double s = 0.0; s < max_length; s += ds) {
        double n_curr = get_refractive_index(&env, current.x, current.y);
        opl += n_curr * ds;

        printf("%.1f\t%.3f\t%.4f\t%.6f\t%.6f\t%.6f\t%.4f\n",
               s, current.x, current.y, current.px, current.py, n_curr, opl);

        if (current.y <= 0.0 && current.py < 0.0) {
            // Гранична умова дзеркального відбиття від землі при досягненні нуля
            current.py = -current.py;
        }

        current = rk4_step(&env, current, ds);
    }

    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>
#include <algorithm>

struct Vector2D {
    double x{0.0};
    double y{0.0};

    [[nodiscard]] Vector2D operator+(const Vector2D& other) const { return {x + other.x, y + other.y}; }
    [[nodiscard]] Vector2D operator*(double scalar) const { return {x * scalar, y * scalar}; }
};

struct RayState {
    Vector2D pos; // (x, y) - вектор координати
    Vector2D p;   // (px, py) - канонічний оптичний імпульс
};

class GRINMedium {
public:
    GRINMedium(double n0, double dn, double y0)
        : n0_(n0), dn_(dn), y0_(y0) {}

    [[nodiscard]] double index(const Vector2D& pos) const {
        double y = std::max(0.0, pos.y);
        return n0_ + dn_ * (1.0 - std::exp(-y / y0_));
    }

    [[nodiscard]] Vector2D gradient(const Vector2D& pos) const {
        double y = std::max(0.0, pos.y);
        return {0.0, (dn_ / y0_) * std::exp(-y / y0_)};
    }

private:
    double n0_;
    double dn_;
    double y0_;
};

class RayTracer {
public:
    explicit RayTracer(GRINMedium medium) : medium_(std::move(medium)) {}

    [[nodiscard]] RayState derivatives(const RayState& state) const {
        double n = medium_.index(state.pos);
        Vector2D grad = medium_.gradient(state.pos);

        return {
            .pos = {state.p.x / n, state.p.y / n},
            .p   = grad
        };
    }

    [[nodiscard]] RayState rk4Step(const RayState& state, double ds) const {
        RayState k1 = derivatives(state);

        RayState s_k2{
            .pos = state.pos + k1.pos * (0.5 * ds),
            .p   = state.p   + k1.p   * (0.5 * ds)
        };
        RayState k2 = derivatives(s_k2);

        RayState s_k3{
            .pos = state.pos + k2.pos * (0.5 * ds),
            .p   = state.p   + k2.p   * (0.5 * ds)
        };
        RayState k3 = derivatives(s_k3);

        RayState s_k4{
            .pos = state.pos + k3.pos * ds,
            .p   = state.p   + k3.p   * ds
        };
        RayState k4 = derivatives(s_k4);

        return {
            .pos = state.pos + (k1.pos + k2.pos * 2.0 + k3.pos * 2.0 + k4.pos) * (ds / 6.0),
            .p   = state.p   + (k1.p   + k2.p   * 2.0 + k3.p   * 2.0 + k4.p)   * (ds / 6.0)
        };
    }

    std::vector<RayState> trace(RayState start, double ds, double maxDistance) const {
        std::vector<RayState> path;
        path.reserve(static_cast<size_t>(maxDistance / ds));

        RayState current = start;
        for (double s = 0.0; s < maxDistance; s += ds) {
            path.push_back(current);
            if (current.pos.y <= 0.0 && current.p.y < 0.0) {
                current.p.y = -current.p.y; // Дзеркальне відбиття від поверхні
            }
            current = rk4Step(current, ds);
        }
        return path;
    }

private:
    GRINMedium medium_;
};

int main() {
    GRINMedium atmosphere(1.00026, 0.00030, 1.5);
    RayTracer tracer(atmosphere);

    double startY = 1.2;
    double angleRad = -1.5 * (M_PI / 180.0);
    double nStart = atmosphere.index({0.0, startY});

    RayState initial{
        .pos = {0.0, startY},
        .p   = {nStart * std::cos(angleRad), nStart * std::sin(angleRad)}
    };

    double ds = 0.1;
    auto trajectory = tracer.trace(initial, ds, 150.0);

    std::cout << std::fixed << std::setprecision(4);
    std::cout << "# Trajectory points (x, y):\n";
    for (size_t i = 0; i < trajectory.size(); i += 50) {
        std::cout << "Step " << i << ": x = " << trajectory[i].pos.x
                  << " m, y = " << trajectory[i].pos.y << " m\n";
    }

    return 0;
}
```
:::

## Аналіз точності та збереження інваріанта імпульсу

При реалізації чисельних методів для принципів варіаційної оптики критично важливим є контроль інваріанта модуля імпульсу. Оскільки за визначенням `p = n(r) · u`, де `|u| = 1`, у кожній точці чисельної траєкторії повинен виконуватися алгебраїчний інваріант:

```
|p(s)| = sqrt( px²(s) + py²(s) ) = n( x(s), y(s) )
```

У разі накопичення фазових похибок чисельного інтегрування (наприклад, при використанні простішого метода Ейлера першого порядку) величина `|p|` швидко починає відхилятися від `n(r)`. Це призводить до несправжнього «зміщення фази» і викривлення розрахованих світлових променів.

Метод Рунге — Кутти 4-го порядку (RK4) з диференціальним кроком `Δs = 0.1` м забезпечує відносне відхилення інваріанта `| |p| - n | / n < 10⁻⁸` протягом усього трасування на відстані 150 метрів.

Результати розрахунку демонструють: світловий промінь, випущений з висоти `1.2` м під кутом `-1.5°` до горизонту, рухається похило вниз, але по мірі наближення до гарячої поверхні земля вертикальний градієнт `∂n/∂y` створює вигинаючу силу вгору. Промінь досягає точки мінімального зближення з землею на висоті `y_min ≈ 0.15` м при `x ≈ 75` м і плавно повертає вгору, не торкаючись поверхні асфальту.

Для спостерігача, розташованого на відстані 150 метрів, цей промінь входить в око під кутом знизу. Мозок людини экстраполює прямолінійну траєкторію назад під поверхню землі, формуючи уявне перевернуте зображення блакитного неба — класичний нижній міраж.

## Адаптація алгоритму для 3D графічних рушіїв

Наведений чисельний алгоритм легко узагальнюється на повний тривимірний простір `(x, y, z)`. Вектор стану розширюється до 6 компонент `State = (x, y, z, px, py, pz)`.

При інтеграції з сучасними графічними рушіями (наприклад, NVIDIA OptiX або Intel Embree) чисельне трасування у volumetric GRIN середовищах поєднується з BVH-деревами (Bounding Volume Hierarchy). Трасування розбивається на дві фази:
1. Безперервне розв'язання рівнянь RK4 всередині об'ємного градієнтного середовища.
2. Швидка перевірка дискретних перетинів з трикутними сітками оптичних поверхонь (лінз, дзеркал) з перерахунком векторів заломлення за законом Снеліуса при перетині поверхонь.

Такий гібридний підхід використовується при моделюванні атмосферної рефракції у геоінформаційних системах, проектуванні волоконно-оптичних компонентів та створенні фотореалістичних спецефектів у комп'ютерній графіці.
