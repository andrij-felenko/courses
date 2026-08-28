# ⚙️ Панельний метод розрахунку обтікання профілю

Панельні методи (англ. *Panel Methods*) — це класичний апарат чисельної гідроаеродинаміки для розрахунку безв'язкісного потенціального обтікання тіл довільної геометричної форми. Замість тривимірної або двовимірної дискретизації всього об'єму рідини сіткою (як у методах скінченних різниць, скінченних елементів або скінченних об'ємів рівнянь Нав'є-Стокса) панельний метод спирається на інтегральні граничні рівняння. Оскільки для потенціального плину нестисливої рідини поле швидкостей задовольняє лінійне рівняння Лапласа для потенціалу швидкості (`∇²φ = 0`), розв'язок задачі в усьому просторі однозначно визначається розподілом сингулярностей (джерел, стоків, диполів або вихорів) виключно на границі обтічного тіла.

Це кардинально зменшує розмірність задачі: двовимірне обтікання профілю зводиться до одновимірної замкненої лінії контуру. Контур крила розбивається на скінченну кількість плоских панелей, а диференціальна крайова задача перетворюється на систему лінійних алгебраїчних рівнянь, що розв'язується за мілісекунди.

Нижче наведено повну самодостатню реалізацію методу дискретних вихрових панелей з кусково-постійним розподілом циркуляції для довільного профілю серії NACA 4-digit на мовах C та C++.

## Математична постановка методу вихрового шару

Нехай плоский профіль обтікається потоком нестисливої нев'язкої рідини з густиною `ρ` та швидкістю на нескінченності `v_∞` під кутом атаки `α`. За межами тонкого шару примежового тертя потік є безвихровим (`rot v = 0`), тому поле швидкостей описується потенціалом `φ(x, y)`:

```
v(x, y) = ∇φ = (∂φ/∂x, ∂φ/∂y)
∇²φ = 0
```

У методі вихрових панелей тверда поверхня профілю замінюється неперервним вихровим шаром (вихровим простирадлом) із поверхневою густиною циркуляції `γ(s)`, де `s` — дугова координата вздовж контуру. Вихровий шар забезпечує розрив тангенціальної складової швидкості при переході через поверхню: якщо швидкість рідини всередині тіла вважати рівною нулю, то зовнішня дотична швидкість на поверхні крила точно дорівнює локальній густині вихорів: `v_t(s) = γ(s)`.

Контур профілю розбивається на `N` плоских відрізків-панелей. Нумерація вузлів і панелей починається від гострої задньої кромки (TE), іде вздовж нижньої поверхні (черева) до передньої кромки (LE), обгинає носок і повертається по верхній поверхні (спинці) назад до задньої кромки.

Кожна панель з індексом `i` (`i = 1, 2, ..., N`) описується такими геометричними елементами:
- Координатами початкового та кінцевого вузлів: `P1_i = (x_i, y_i)` та `P2_i = (x_{i+1}, y_{i+1})`.
- Довжиною відрізка: `S_i = √((x_{i+1} - x_i)² + (y_{i+1} - y_i)²)`.
- Кутом нахилу панелі до осі X: `θ_i = atan2(y_{i+1} - y_i, x_{i+1} - x_i)`.
- Контрольною точкою колокації (геометричним центром панелі): `x_{c,i} = ½·(x_i + x_{i+1})`, `y_{c,i} = ½·(y_i + y_{i+1})`.
- Одиничним вектором дотичної: `t_i = (cos θ_i, sin θ_i) = ((x_{i+1} - x_i)/S_i, (y_{i+1} - y_i)/S_i)`.
- Одиничним вектором зовнішньої нормалі: `n_i = (-sin θ_i, cos θ_i) = (-t_{i,y}, t_{i,x})`.

## Аналітичне інтегрування індукованих швидкостей

Кожна панель несе на собі рівномірно розподілений вихровий шар постійної невідомої інтенсивності `γ_j`. Швидкість, яку індукує панель `j` одиничної інтенсивності (`γ_j = 1`) у довільній точці простору `(x, y)`, обчислюється інтегруванням елементарних вихорів Біо-Савара вздовж відрізка панелі.

Для спрощення інтегрування перейдемо у власну локальну систему координат `j`-ї панелі `(x*, y*)`, де початок координат розташований у першому вузлі `P1_j`, вісь `x*` спрямована вздовж панелі до `P2_j`, а вісь `y*` — по зовнішній нормалі:

```
x* = (x - x_j) · cos θ_j + (y - y_j) · sin θ_j
y* = -(x - x_j) · sin θ_j + (y - y_j) · cos θ_j
```

У локальній системі координат швидкість від рівномірного вихрового шару одиничної густини на відрізку `0 ≤ ξ ≤ S_j` знаходиться аналітично:

```
u_{loc} = -(1 / (2·π)) · ∫₀^{S_j} [ y* / ((x* - ξ)² + (y* )²) ] dξ
= -(1 / (2·π)) · [ atan2(y*, x* - S_j) - atan2(y*, x*) ]

v_{loc} = (1 / (2·π)) · ∫₀^{S_j} [ (x* - ξ) / ((x* - ξ)² + (y* )²) ] dξ
= (1 / (4·π)) · ln [ ((x* - S_j)² + (y* )²) / ((x* )² + (y* )²) ]
```

Повернення знайдених швидкостей у глобальну декартову систему здійснюється зворотним перетворенням:

```
u_{ij} = u_{loc} · cos θ_j - v_{loc} · sin θ_j
v_{ij} = u_{loc} · sin θ_j + v_{loc} · cos θ_j
```

Особливий випадок (самоіндукція, коли точка колокації належить самій панелі, `i = j`):
У центрі панелі `x* = S_i / 2`, `y* = 0`. Границя логарифма при `y* → 0` дорівнює нулю (`v_{loc} = 0`), а різниця арктангенсів дає `u_{loc} = 0` (вплив симетричних частин ліворуч і праворуч взаємно компенсується). Проте безпосередньо на вихровому шарі існує стрибок тангенціальної швидкості `± ½ · γ_i`.

## Формування матриці та умова Кутти

Гранична умова непротікання (крайова умова Неймана) вимагає, щоб у контрольній точці кожної панелі сумарна швидкість (набігаючий потік плюс індукція всіх вихрових панелей) була строго дотичною до поверхні:

```
v_{total,i} · n_i = 0
(v_∞ + ∑_{j=1}^N γ_j · v_{ij}) · n_i = 0
```

Розкриваючи скалярний добуток, отримуємо лінійне рівняння для кожної контрольної точки `i`:

```
∑_{j=1}^N A_{ij} · γ_j = -(v_{∞,x} · n_{i,x} + v_{∞,y} · n_{i,y})
```

де `A_{ij} = u_{ij} · n_{i,x} + v_{ij} · n_{i,y}` — коефіцієнт геометричного впливу `j`-ї панелі на нормальну швидкість `i`-ї панелі. Для самоіндукції `A_{ii} = 0`.

Система з `N` рівнянь для `N` панелей є виродженою (лінійно залежною), оскільки в ідеальній рідині циркуляція може бути довільною. Для однозначного фізичного замикання задачі останнє `N`-е рівняння замінюється дискретною **умовою Кутти** на задній кромці: потік повинен гладко сходити з гострого хвоста крила без нескінченних швидкостей. У методі вихрових панелей це відповідає зануленню суми циркуляцій на першій (нижній TE) та останній (верхній TE) панелях:

```
γ_1 + γ_N = 0
```

Отримана система `A · γ = b` розмірності `N × N` розв'язується прямим методом Гаусса з вибором головного елемента по стовпцю (partial pivoting) для забезпечення високої чисельної стійкості.

## Обчислення коефіцієнтів тиску та інтегрування сил

Після знаходження вектора циркуляцій `γ` тангенціальна швидкість у контрольній точці кожної панелі обчислюється підсумовуванням проекцій на одиничний вектор дотичної `t_i`:

```
v_{t,i} = (v_{∞,x} · t_{i,x} + v_{∞,y} · t_{i,y}) + ∑_{j=1, j≠i}^N (u_{ij} · t_{i,x} + v_{ij} · t_{i,y}) · γ_j + ½ · γ_i
```

Коефіцієнт статичного тиску за законом Бернуллі:

```
C_{p,i} = 1 - (v_{t,i} / v_∞)²
```

Коефіцієнт підіймальної сили `C_l` та поздовжнього моменту відносно чверті хорди `C_{m,c/4}` отримуються чисельним інтегруванням розподілу сили тиску `dF_i = -C_{p,i} · S_i · n_i`:

```
C_l = ∑_{i=1}^N (-C_{p,i} · S_i · n_{i,y})
C_{m,c/4} = ∑_{i=1}^N (-C_{p,i} · S_i) · [ n_{i,y} · (x_{c,i} - 0.25) - n_{i,x} · y_{c,i} ]
```

## Чисельні особливості та крайові випадки

1. **Косинусоподібне згущення вузлів (Cosine Spacing)**:
   Рівномірний розподіл точок вздовж хорди непридатний через високі градієнти кривини та піки швидкості на носку крила. Вузли генеруються за параметричним законом `x_k = ½ · (1 - cos β_k)`, що згущує панелі біля передньої та задньої кромок, забезпечуючи високу точність інтегрування піка розрідження навіть при помірній кількості панелей (`N = 40–80`).
2. **Парадокс Д'Аламбера та обмеження безв'язкісного методу**:
   Оскільки метод розв'язує рівняння нев'язкої потенціальної рідини, інтегрування нормального тиску по замкненому контуру дає строго нульовий лобовий опір тиску (`C_{d,press} = 0`). Для розрахунку повного опору профілю `C_d` та урахування відривних зон сучасні аеродинамічні комплекси (наприклад, XFOIL Марка Дрели) доповнюють панельний метод розв'язанням інтегральних рівнянь примежового шару методом товщини витіснення `δ*(x)` у двозв'язній ітераційній постановці.

## Програмна реалізація

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

#define MAX_PANELS 120

typedef struct {
    double x, y;
} Point;

typedef struct {
    Point p1, p2;     /* Вузли панелі */
    Point cp;         /* Контрольна точка колокації */
    double length;    /* Довжина панелі S_i */
    double theta;     /* Кут нахилу */
    Point normal;     /* Одинична нормаль n_i (назовні) */
    Point tangent;    /* Одинична дотична t_i */
    double gamma;     /* Розрахована інтенсивність вихорів */
    double cp_val;    /* Коефіцієнт тиску C_p */
} Panel;

/* Генерація контуру NACA 4-значного профілю за годинниковою стрілкою від TE */
int generate_naca4(int m_digit, int p_digit, int t_digit, int num_panels, Panel *panels) {
    if (num_panels % 2 != 0 || num_panels > MAX_PANELS) return 0;
    int half_pts = num_panels / 2;
    double m = m_digit / 100.0;
    double p = p_digit / 10.0;
    double t = t_digit / 100.0;

    Point nodes[MAX_PANELS + 1];
    int n_nodes = 0;

    /* Нижній контур від TE (x=1.0) до LE (x=0.0) */
    for (int i = 0; i <= half_pts; i++) {
        double beta = (M_PI * i) / half_pts;
        double x = 0.5 * (1.0 + cos(beta)); /* 1.0 -> 0.0 */
        double yt = 5.0 * t * (0.2969 * sqrt(x) - 0.1260 * x - 0.3516 * x * x + 0.2843 * x * x * x - 0.1015 * x * x * x * x);
        double yc = 0.0, dy_dx = 0.0;
        if (p > 0.0 && m > 0.0) {
            if (x <= p) {
                yc = (m / (p * p)) * (2.0 * p * x - x * x);
                dy_dx = (2.0 * m / (p * p)) * (p - x);
            } else {
                yc = (m / ((1.0 - p) * (1.0 - p))) * ((1.0 - 2.0 * p) + 2.0 * p * x - x * x);
                dy_dx = (2.0 * m / ((1.0 - p) * (1.0 - p))) * (p - x);
            }
        }
        double th = atan(dy_dx);
        nodes[n_nodes].x = x + yt * sin(th);
        nodes[n_nodes].y = yc - yt * cos(th);
        n_nodes++;
    }

    /* Верхній контур від LE (x=0.0) до TE (x=1.0) */
    for (int i = 1; i <= half_pts; i++) {
        double beta = (M_PI * i) / half_pts;
        double x = 0.5 * (1.0 - cos(beta)); /* 0.0 -> 1.0 */
        double yt = 5.0 * t * (0.2969 * sqrt(x) - 0.1260 * x - 0.3516 * x * x + 0.2843 * x * x * x - 0.1015 * x * x * x * x);
        double yc = 0.0, dy_dx = 0.0;
        if (p > 0.0 && m > 0.0) {
            if (x <= p) {
                yc = (m / (p * p)) * (2.0 * p * x - x * x);
                dy_dx = (2.0 * m / (p * p)) * (p - x);
            } else {
                yc = (m / ((1.0 - p) * (1.0 - p))) * ((1.0 - 2.0 * p) + 2.0 * p * x - x * x);
                dy_dx = (2.0 * m / ((1.0 - p) * (1.0 - p))) * (p - x);
            }
        }
        double th = atan(dy_dx);
        nodes[n_nodes].x = x - yt * sin(th);
        nodes[n_nodes].y = yc + yt * cos(th);
        n_nodes++;
    }

    /* Побудова панелей за списком вузлів */
    for (int i = 0; i < num_panels; i++) {
        panels[i].p1 = nodes[i];
        panels[i].p2 = nodes[i + 1];
        panels[i].cp.x = 0.5 * (panels[i].p1.x + panels[i].p2.x);
        panels[i].cp.y = 0.5 * (panels[i].p1.y + panels[i].p2.y);
        double dx = panels[i].p2.x - panels[i].p1.x;
        double dy = panels[i].p2.y - panels[i].p1.y;
        panels[i].length = sqrt(dx * dx + dy * dy);
        panels[i].theta = atan2(dy, dx);
        panels[i].tangent.x = dx / panels[i].length;
        panels[i].tangent.y = dy / panels[i].length;
        panels[i].normal.x = -panels[i].tangent.y;
        panels[i].normal.y = panels[i].tangent.x;
    }
    return 1;
}

/* Обчислення швидкості, індукованої панеллю j у точці (x, y) */
void panel_velocity(const Panel *p, double x, double y, double *u, double *v) {
    double dx1 = x - p->p1.x;
    double dy1 = y - p->p1.y;
    double ct = cos(p->theta);
    double st = sin(p->theta);

    /* Координати у системі панелі */
    double x_loc = dx1 * ct + dy1 * st;
    double y_loc = -dx1 * st + dy1 * ct;

    if (fabs(y_loc) < 1e-10 && x_loc >= 0.0 && x_loc <= p->length) {
        *u = 0.0;
        *v = 0.0;
        return;
    }

    double r1_sq = x_loc * x_loc + y_loc * y_loc;
    double r2_sq = (x_loc - p->length) * (x_loc - p->length) + y_loc * y_loc;

    double theta1 = atan2(y_loc, x_loc);
    double theta2 = atan2(y_loc, x_loc - p->length);

    double u_loc = -(1.0 / (2.0 * M_PI)) * (theta2 - theta1);
    double v_loc = (1.0 / (4.0 * M_PI)) * log(r2_sq / (r1_sq + 1e-15));

    /* Трансформація у глобальні координати */
    *u = u_loc * ct - v_loc * st;
    *v = u_loc * st + v_loc * ct;
}

/* Розв'язувач лінійної системи A*x = b методом Гаусса з вибором головного елемента */
int solve_gauss(int n, double A[MAX_PANELS][MAX_PANELS], double b[MAX_PANELS], double x[MAX_PANELS]) {
    for (int i = 0; i < n; i++) {
        int max_row = i;
        double max_val = fabs(A[i][i]);
        for (int k = i + 1; k < n; k++) {
            if (fabs(A[k][i]) > max_val) {
                max_val = fabs(A[k][i]);
                max_row = k;
            }
        }
        if (max_val < 1e-12) return 0; /* Вироджена матриця */

        for (int k = i; k < n; k++) {
            double tmp = A[i][k];
            A[i][k] = A[max_row][k];
            A[max_row][k] = tmp;
        }
        double tmp_b = b[i];
        b[i] = b[max_row];
        b[max_row] = tmp_b;

        for (int k = i + 1; k < n; k++) {
            double factor = A[k][i] / A[i][i];
            b[k] -= factor * b[i];
            for (int j = i; j < n; j++) {
                A[k][j] -= factor * A[i][j];
            }
        }
    }

    for (int i = n - 1; i >= 0; i--) {
        double sum = 0.0;
        for (int j = i + 1; j < n; j++) {
            sum += A[i][j] * x[j];
        }
        x[i] = (b[i] - sum) / A[i][i];
    }
    return 1;
}

int main(void) {
    int num_panels = 40;
    Panel panels[MAX_PANELS];
    generate_naca4(2, 4, 12, num_panels, panels); /* NACA 2412 */

    double alpha_deg = 5.0;
    double alpha = alpha_deg * M_PI / 180.0;
    double v_inf_x = cos(alpha);
    double v_inf_y = sin(alpha);

    double A[MAX_PANELS][MAX_PANELS];
    double b[MAX_PANELS];
    double gamma[MAX_PANELS];

    /* Формування матриці впливу */
    for (int i = 0; i < num_panels - 1; i++) {
        b[i] = -(v_inf_x * panels[i].normal.x + v_inf_y * panels[i].normal.y);
        for (int j = 0; j < num_panels; j++) {
            if (i == j) {
                A[i][j] = 0.0;
            } else {
                double u, v;
                panel_velocity(&panels[j], panels[i].cp.x, panels[i].cp.y, &u, &v);
                A[i][j] = u * panels[i].normal.x + v * panels[i].normal.y;
            }
        }
    }

    /* Умова Кутти на останньому рядку: gamma_0 + gamma_{N-1} = 0 */
    for (int j = 0; j < num_panels; j++) {
        A[num_panels - 1][j] = 0.0;
    }
    A[num_panels - 1][0] = 1.0;
    A[num_panels - 1][num_panels - 1] = 1.0;
    b[num_panels - 1] = 0.0;

    solve_gauss(num_panels, A, b, gamma);

    /* Обчислення тангенціальних швидкостей та інтегрування сил */
    double cl = 0.0;
    double cm_c4 = 0.0;

    for (int i = 0; i < num_panels; i++) {
        panels[i].gamma = gamma[i];
        double vt = v_inf_x * panels[i].tangent.x + v_inf_y * panels[i].tangent.y + 0.5 * gamma[i];
        for (int j = 0; j < num_panels; j++) {
            if (i != j) {
                double u, v;
                panel_velocity(&panels[j], panels[i].cp.x, panels[i].cp.y, &u, &v);
                vt += (u * panels[i].tangent.x + v * panels[i].tangent.y) * gamma[j];
            }
        }
        panels[i].cp_val = 1.0 - vt * vt;

        /* Внесок у підіймальну силу (нормаль Y) та поздовжній момент відносно (0.25, 0.0) */
        double cp_ds = -panels[i].cp_val * panels[i].length;
        cl += cp_ds * panels[i].normal.y;
        cm_c4 += cp_ds * (panels[i].normal.y * (panels[i].cp.x - 0.25) - panels[i].normal.x * panels[i].cp.y);
    }

    printf("NACA 2412 | Alpha: %.1f deg | Panels: %d\n", alpha_deg, num_panels);
    printf("Cl: %.4f | Cm(c/4): %.4f\n", cl, cm_c4);
    printf("-----------------------------------------\n");
    printf("Panel   x/c        Cp (Нижня / Верхня)\n");
    for (int i = 0; i < num_panels; i += 4) {
        printf("%3d    %6.3f    %+7.3f\n", i, panels[i].cp.x, panels[i].cp_val);
    }
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <cmath>
#include <numbers>
#include <iomanip>
#include <algorithm>
#include <span>

struct Point {
    double x{0.0};
    double y{0.0};
};

struct Panel {
    Point p1;
    Point p2;
    Point cp;
    double length{0.0};
    double theta{0.0};
    Point normal;
    Point tangent;
    double gamma{0.0};
    double cp_val{0.0};
};

class PanelSolver {
public:
    PanelSolver(int m_digit, int p_digit, int t_digit, int num_panels)
        : m_{m_digit / 100.0}, p_{p_digit / 10.0}, t_{t_digit / 100.0}, num_panels_{num_panels} {
        generate_geometry();
    }

    void solve(double alpha_deg) {
        const double alpha = alpha_deg * std::numbers::pi / 180.0;
        const double v_inf_x = std::cos(alpha);
        const double v_inf_y = std::sin(alpha);

        std::vector<std::vector<double>> A(num_panels_, std::vector<double>(num_panels_, 0.0));
        std::vector<double> b(num_panels_, 0.0);

        for (int i = 0; i < num_panels_ - 1; ++i) {
            b[i] = -(v_inf_x * panels_[i].normal.x + v_inf_y * panels_[i].normal.y);
            for (int j = 0; j < num_panels_; ++j) {
                if (i != j) {
                    auto [u, v] = panel_velocity(panels_[j], panels_[i].cp.x, panels_[i].cp.y);
                    A[i][j] = u * panels_[i].normal.x + v * panels_[i].normal.y;
                }
            }
        }

        // Дискретна умова Кутти: сума циркуляцій на задній кромці дорівнює нулю
        A[num_panels_ - 1][0] = 1.0;
        A[num_panels_ - 1][num_panels_ - 1] = 1.0;
        b[num_panels_ - 1] = 0.0;

        std::vector<double> gamma(num_panels_, 0.0);
        solve_linear_system(A, b, gamma);

        cl_ = 0.0;
        cm_c4_ = 0.0;

        for (int i = 0; i < num_panels_; ++i) {
            panels_[i].gamma = gamma[i];
            double vt = v_inf_x * panels_[i].tangent.x + v_inf_y * panels_[i].tangent.y + 0.5 * gamma[i];
            for (int j = 0; j < num_panels_; ++j) {
                if (i != j) {
                    auto [u, v] = panel_velocity(panels_[j], panels_[i].cp.x, panels_[i].cp.y);
                    vt += (u * panels_[i].tangent.x + v * panels_[i].tangent.y) * gamma[j];
                }
            }
            panels_[i].cp_val = 1.0 - vt * vt;

            const double cp_ds = -panels_[i].cp_val * panels_[i].length;
            cl_ += cp_ds * panels_[i].normal.y;
            cm_c4_ += cp_ds * (panels_[i].normal.y * (panels_[i].cp.x - 0.25) - panels_[i].normal.x * panels_[i].cp.y);
        }
    }

    [[nodiscard]] double lift_coefficient() const noexcept { return cl_; }
    [[nodiscard]] double moment_coefficient() const noexcept { return cm_c4_; }
    [[nodiscard]] std::span<const Panel> panels() const noexcept { return panels_; }

private:
    double m_{0.0};
    double p_{0.0};
    double t_{0.0};
    int num_panels_{0};
    std::vector<Panel> panels_;
    double cl_{0.0};
    double cm_c4_{0.0};

    void generate_geometry() {
        const int half = num_panels_ / 2;
        std::vector<Point> nodes;
        nodes.reserve(num_panels_ + 1);

        auto compute_surface = [this](double x) {
            const double yt = 5.0 * t_ * (0.2969 * std::sqrt(x) - 0.1260 * x - 0.3516 * x * x + 0.2843 * x * x * x - 0.1015 * x * x * x * x);
            double yc = 0.0;
            double dy_dx = 0.0;
            if (p_ > 0.0 && m_ > 0.0) {
                if (x <= p_) {
                    yc = (m_ / (p_ * p_)) * (2.0 * p_ * x - x * x);
                    dy_dx = (2.0 * m_ / (p_ * p_)) * (p_ - x);
                } else {
                    yc = (m_ / ((1.0 - p_) * (1.0 - p_))) * ((1.0 - 2.0 * p_) + 2.0 * p_ * x - x * x);
                    dy_dx = (2.0 * m_ / ((1.0 - p_) * (1.0 - p_))) * (p_ - x);
                }
            }
            return std::make_tuple(yc, yt, std::atan(dy_dx));
        };

        // Нижня поверхня від TE до LE
        for (int i = 0; i <= half; ++i) {
            const double beta = (std::numbers::pi * i) / half;
            const double x = 0.5 * (1.0 + std::cos(beta));
            auto [yc, yt, th] = compute_surface(x);
            nodes.push_back({x + yt * std::sin(th), yc - yt * std::cos(th)});
        }

        // Верхня поверхня від LE до TE
        for (int i = 1; i <= half; ++i) {
            const double beta = (std::numbers::pi * i) / half;
            const double x = 0.5 * (1.0 - std::cos(beta));
            auto [yc, yt, th] = compute_surface(x);
            nodes.push_back({x - yt * std::sin(th), yc + yt * std::cos(th)});
        }

        panels_.resize(num_panels_);
        for (int i = 0; i < num_panels_; ++i) {
            panels_[i].p1 = nodes[i];
            panels_[i].p2 = nodes[i + 1];
            panels_[i].cp = {0.5 * (nodes[i].x + nodes[i + 1].x), 0.5 * (nodes[i].y + nodes[i + 1].y)};
            const double dx = nodes[i + 1].x - nodes[i].x;
            const double dy = nodes[i + 1].y - nodes[i].y;
            panels_[i].length = std::hypot(dx, dy);
            panels_[i].theta = std::atan2(dy, dx);
            panels_[i].tangent = {dx / panels_[i].length, dy / panels_[i].length};
            panels_[i].normal = {-panels_[i].tangent.y, panels_[i].tangent.x};
        }
    }

    static std::pair<double, double> panel_velocity(const Panel& p, double x, double y) noexcept {
        const double dx = x - p.p1.x;
        const double dy = y - p.p1.y;
        const double ct = std::cos(p.theta);
        const double st = std::sin(p.theta);

        const double x_loc = dx * ct + dy * st;
        const double y_loc = -dx * st + dy * ct;

        if (std::abs(y_loc) < 1e-10 && x_loc >= 0.0 && x_loc <= p.length) {
            return {0.0, 0.0};
        }

        const double r1_sq = x_loc * x_loc + y_loc * y_loc;
        const double r2_sq = (x_loc - p.length) * (x_loc - p.length) + y_loc * y_loc;

        const double theta1 = std::atan2(y_loc, x_loc);
        const double theta2 = std::atan2(y_loc, x_loc - p.length);

        const double u_loc = -(1.0 / (2.0 * std::numbers::pi)) * (theta2 - theta1);
        const double v_loc = (1.0 / (4.0 * std::numbers::pi)) * std::log(r2_sq / (r1_sq + 1e-15));

        return {u_loc * ct - v_loc * st, u_loc * st + v_loc * ct};
    }

    static bool solve_linear_system(std::vector<std::vector<double>>& A, std::vector<double>& b, std::vector<double>& x) {
        const int n = static_cast<int>(b.size());
        for (int i = 0; i < n; ++i) {
            int max_row = i;
            double max_val = std::abs(A[i][i]);
            for (int k = i + 1; k < n; ++k) {
                if (std::abs(A[k][i]) > max_val) {
                    max_val = std::abs(A[k][i]);
                    max_row = k;
                }
            }
            if (max_val < 1e-12) return false;

            std::swap(A[i], A[max_row]);
            std::swap(b[i], b[max_row]);

            for (int k = i + 1; k < n; ++k) {
                const double factor = A[k][i] / A[i][i];
                b[k] -= factor * b[i];
                for (int j = i; j < n; ++j) {
                    A[k][j] -= factor * A[i][j];
                }
            }
        }

        for (int i = n - 1; i >= 0; --i) {
            double sum = 0.0;
            for (int j = i + 1; j < n; ++j) {
                sum += A[i][j] * x[j];
            }
            x[i] = (b[i] - sum) / A[i][i];
        }
        return true;
    }
};

int main() {
    PanelSolver solver(2, 4, 12, 40); // NACA 2412, 40 панелей
    solver.solve(5.0);

    std::cout << std::fixed << std::setprecision(4);
    std::cout << "NACA 2412 | Alpha: 5.0 deg | Panels: 40\n";
    std::cout << "Cl: " << solver.lift_coefficient() << " | Cm(c/4): " << solver.moment_coefficient() << "\n";
    std::cout << "-----------------------------------------\n";
    std::cout << "Panel   x/c        Cp (Нижня / Верхня)\n";

    const auto panels = solver.panels();
    for (size_t i = 0; i < panels.size(); i += 4) {
        std::cout << std::setw(3) << i << "    "
                  << std::setw(6) << std::setprecision(3) << panels[i].cp.x << "    "
                  << std::showpos << std::setw(7) << panels[i].cp_val << std::noshowpos << "\n";
    }
    return 0;
}
```
:::
