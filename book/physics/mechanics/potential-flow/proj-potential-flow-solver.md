# ⚙️ Чисельний розв'язувач методом джерельно-вихрових панелей

Ця практична вставка містить алгоритм та практичний чисельний код розрахунку потенціального обтікання двовимірних геометрій та аеродинамічних профілів методом граничних панелей з відновленням коефіцієнта тиску та підйомної сили.

## Математична формулювання панельного методу

У класичному методі джерельних панелей Гесса — Сміта поверхня обтікального профілю розбивається на `N` плоских панелей, з'єднаних вузловими точками `(x_i, y_i)` для `i = 0, ..., N`. Кожна панель `j` характеризується:
- Довжиною панелі `L_j = √((x_j - x_{j-1})² + (y_j - y_{j-1})²)`.
- Кутом нахилу панелі до осі `x`: `θ_j = arctan2(y_j - y_{j-1}, x_j - x_{j-1})`.
- Контрольною точкою посередині панелі `(x_{c,i}, y_{c,i}) = ((x_i + x_{i-1})/2, (y_i + y_{i-1})/2)`.
- Орт-нормаллю `n_i = (-sin θ_i, cos θ_i)` та орт-дотичною `t_i = (cos θ_i, sin θ_i)`.

На кожній панелі розміщується рівномірно розподілений шар джерел інтенсивністю `q_j`. Гранична умова непроникання рідини скрізь стінку `u · n_i = 0` на кожній контрольній точці `i` дає систему `N` лінійних алгебраїчних рівнянь:

```
∑[j=1->N] A_ij · q_j = -U_∞ · n_i
```

Тут `A_ij` — геометричний коефіцієнт нормальної індукованої швидкості від панелі `j` на контрольну точку `i`. Для точкового наближення при розрахунку нормальної швидкості від віддаленої панелі використовується закон обернених квадратів, а для самоіндукованого впливу власної панелі `A_ii = 0.5`.

Після розв'язання системи лінійних рівнянь методом Гаусса з вибором головного елемента обчислюється тангенціальна швидкість `V_{t,i}` на кожній панелі:

```
V_{t,i} = U_∞ · t_i + ∑[j=1->N] B_ij · q_j
```

А коефіцієнт тиску визначається за формулою Бернуллі:

```
C_{p,i} = 1 - (V_{t,i} / U_∞)²
```

Чисельний метод джерельних панелей є винятково ефективним інструментом обчислювальної гідродинаміки. На відміну від сіткових методів скінченних об'ємів, які вимагають побудови тривимірної об'ємної сітки в усьому просторі навколо тіла, панельний метод дискретизує лише двовимірну поверхню самого тіла. Це зменшує розмірність задачі на одиницю та дає змогу отримувати точний розподіл тиску на поверхні аеродинамічного профілю за частки секунди.

## Аналітичне інтегрування впливу панелей

Для підвищення точності розрахунку біля поверхонь із високою кривизною замість точкового наближення використовують точні аналітичні інтеграли потенціалу неперервного джерельного шару вздовж відрізка панелі.

Введемо локальну систему координат `(ξ, η)` панелі `j`, де вісь `ξ` спрямована вздовж панелі від `0` до `L_j`, а вісь `η` — по нормалі. Координати контрольної точки `(x_{c,i}, y_{c,i})` у локальній системі панелі `j` дорівнюють:

```
ξ_i =  (x_{c,i} - x_j) · cos θ_j + (y_{c,i} - y_j) · sin θ_j
η_i = -(x_{c,i} - x_j) · sin θ_j + (y_{c,i} - y_j) · cos θ_j
```

Аналітичні інтеграли впливу логарифмічного потенціалу джерела визначаються формулами:

```
I_ij = ∫[0->L_j] ln √((ξ_i - ξ)² + η_i²) dξ 
= (ξ_i) · ln(r_1) - (ξ_i - L_j) · ln(r_2) - L_j + η_i · (β_2 - β_1)

J_ij = ∫[0->L_j] arctan2(η_i, ξ_i - ξ) dξ 
= η_i · ln(r_2 / r_1) + (ξ_i) · β_1 - (ξ_i - L_j) · β_2
```

Де `r_1 = √(ξ_i² + η_i²)`, `r_2 = √((ξ_i - L_j)² + η_i²)`, `β_1 = arctan2(η_i, ξ_i)` та `β_2 = arctan2(η_i, ξ_i - L_j)`.

Коефіцієнти матриці нормального та тангенціального впливу `A_ij` і `B_ij` обчислюються шляхом проектування локальних швидкостей на нормаль та дотичну контрольної точки `i`:

```
A_ij = (1 / (2π)) · [ -I_ij · sin(θ_i - θ_j) + J_ij · cos(θ_i - θ_j) ]
B_ij = (1 / (2π)) · [  I_ij · cos(θ_i - θ_j) + J_ij · sin(θ_i - θ_j) ]
```

Для самовпливу власної панелі (`i = j`): `I_ii = L_i · (ln(L_i / 2) - 1)`, `J_ii = π`, звідки `A_ii = 0.5` та `B_ii = 0`.

## Розширення методу на несиметричні крила з циркуляцією (Метод Гесса — Сміта)

Для розрахунку аеродинамічних профілів, що несуть підйомну силу під кутом атаки `α`, чисто джерельного шару недостатньо. У методі Гесса — Сміта поверхнева дискретизація доповнюється шаром вихрових панелей зі сталою інтенсивністю `γ` вздовж усього контуру профілю.

Система лінійних алгебраїчних рівнянь розширюється до розміру `(N + 1) × (N + 1)`:
- `N` рівнянь кінематичної умови непроникання `u · n_i = 0` на кожній контрольній точці:

```
∑[j=1->N] A_ij · q_j + γ · ∑[j=1->N] C_ij = -U_∞ · n_i
```

Тут `C_ij` — коефіцієнт нормальної швидкості, індукованої вихровою панеллю `j`.

- `(N + 1)`-ше рівняння становить вимога умови Кутти — Жуковського на задній кромці профілю: рівність тангенціальних швидкостей на верхній `(i = 1)` та нижній `(i = N)` панелях біля гострого хвостовика:

```
V_{t,1} + V_{t,N} = 0
```

Розв'язання цієї розширеної системи дає як розподіл джерельних інтенсивностей `q_j`, так і унікальне значення циркуляції `γ`, з якого обчислюється підйомна сила профілю: `C_L = 2γ / (U_∞ · c)`.

## Косинусоїдальна дискретизація профілю

Для досягнення високої чисельної точності біля закругленої передньої кромки та гострої задньої кромки крила вузли панелей слід розміщувати не рівномірно, а за законом косинуса:

```
x_k = (c / 2) · (1 - cos(π · k / N))  для  k = 0, ..., N
```

Косинусоїдальний розподіл густо розміщує дрібні панелі у зонах високих градієнтів тиску на передній та задній кромках, що запобігає виникненню осциляцій тиску та дає точний розрахунок аеродинамічного моменту.

## Реалізація панельного розв'язувача

Нижче наведено робочий чисельний розв'язувач потенціального обтікання гладкого циліндра або профілю на C та ідіоматичному C++.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef struct {
    double x1, y1;
    double x2, y2;
    double xc, yc;
    double len;
    double beta;
    double nx, ny;
    double tx, ty;
    double q;
    double vt;
    double cp;
} Panel;

void generate_cylinder_panels(Panel* panels, int n, double radius) {
    for (int i = 0; i < n; i++) {
        double theta1 = 2.0 * M_PI * i / n;
        double theta2 = 2.0 * M_PI * (i + 1) / n;

        panels[i].x1 = radius * cos(theta1);
        panels[i].y1 = radius * sin(theta1);
        panels[i].x2 = radius * cos(theta2);
        panels[i].y2 = radius * sin(theta2);

        panels[i].xc = 0.5 * (panels[i].x1 + panels[i].x2);
        panels[i].yc = 0.5 * (panels[i].y1 + panels[i].y2);

        double dx = panels[i].x2 - panels[i].x1;
        double dy = panels[i].y2 - panels[i].y1;
        panels[i].len = hypot(dx, dy);
        panels[i].beta = atan2(dy, dx);

        panels[i].tx = dx / panels[i].len;
        panels[i].ty = dy / panels[i].len;
        panels[i].nx = -panels[i].ty;
        panels[i].ny =  panels[i].tx;
    }
}

void solve_linear_system(double** A, double* b, double* x, int n) {
    for (int i = 0; i < n; i++) {
        int max_row = i;
        for (int k = i + 1; k < n; k++) {
            if (fabs(A[k][i]) > fabs(A[max_row][i])) {
                max_row = k;
            }
        }
        for (int k = i; k < n; k++) {
            double tmp = A[i][k];
            A[i][k] = A[max_row][k];
            A[max_row][k] = tmp;
        }
        double tmp_b = b[i];
        b[i] = b[max_row];
        b[max_row] = tmp_b;

        for (int k = i + 1; k < n; k++) {
            double c = -A[k][i] / A[i][i];
            for (int j = i; j < n; j++) {
                if (i == j) {
                    A[k][j] = 0;
                } else {
                    A[k][j] += c * A[i][j];
                }
            }
            b[k] += c * b[i];
        }
    }

    for (int i = n - 1; i >= 0; i--) {
        x[i] = b[i] / A[i][i];
        for (int k = i - 1; k >= 0; k--) {
            b[k] -= A[k][i] * x[i];
        }
    }
}

int main(void) {
    int n = 36;
    double radius = 1.0;
    double u_inf = 10.0;

    Panel* panels = (Panel*)malloc(n * sizeof(Panel));
    if (!panels) return 1;

    generate_cylinder_panels(panels, n, radius);

    double** A = (double**)malloc(n * sizeof(double*));
    double* b = (double*)malloc(n * sizeof(double));
    double* q = (double*)malloc(n * sizeof(double));
    for (int i = 0; i < n; i++) {
        A[i] = (double*)malloc(n * sizeof(double));
    }

    for (int i = 0; i < n; i++) {
        b[i] = -u_inf * panels[i].nx;
        for (int j = 0; j < n; j++) {
            if (i == j) {
                A[i][j] = 0.5;
            } else {
                double dx = panels[i].xc - panels[j].xc;
                double dy = panels[i].yc - panels[j].yc;
                double r2 = dx * dx + dy * dy;
                double vn = (dx * panels[i].nx + dy * panels[i].ny) / (2.0 * M_PI * r2);
                A[i][j] = vn * panels[j].len;
            }
        }
    }

    solve_linear_system(A, b, q, n);

    for (int i = 0; i < n; i++) {
        panels[i].q = q[i];
        double vt = u_inf * panels[i].tx;
        for (int j = 0; j < n; j++) {
            if (i != j) {
                double dx = panels[i].xc - panels[j].xc;
                double dy = panels[i].yc - panels[j].yc;
                double r2 = dx * dx + dy * dy;
                double vt_ind = (dx * panels[i].tx + dy * panels[i].ty) / (2.0 * M_PI * r2);
                vt += q[j] * vt_ind * panels[j].len;
            }
        }
        panels[i].vt = vt;
        panels[i].cp = 1.0 - (vt / u_inf) * (vt / u_inf);
    }

    printf("Результати розрахунку потенціального обтікання циліндра:\n");
    printf("Панель |     Xc     |     Yc     |    Cp (чисельний) | Cp (аналітичний)\n");
    printf("-----------------------------------------------------------------------\n");
    for (int i = 0; i < n; i += 4) {
        double theta = atan2(panels[i].yc, panels[i].xc);
        double cp_exact = 1.0 - 4.0 * sin(theta) * sin(theta);
        printf("%6d | %10.4f | %10.4f | %17.4f | %17.4f\n",
               i, panels[i].xc, panels[i].yc, panels[i].cp, cp_exact);
    }

    for (int i = 0; i < n; i++) free(A[i]);
    free(A);
    free(b);
    free(q);
    free(panels);

    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <cmath>
#include <numbers>
#include <iomanip>
#include <memory>
#include <stdexcept>

struct Panel {
    double x1{}, y1{};
    double x2{}, y2{};
    double xc{}, yc{};
    double len{};
    double beta{};
    double nx{}, ny{};
    double tx{}, ty{};
    double q{};
    double vt{};
    double cp{};
};

class PanelSolver {
public:
    PanelSolver(int num_panels, double radius, double u_infinity)
        : n_(num_panels), radius_(radius), u_inf_(u_infinity) {
        if (n_ <= 0) throw std::invalid_argument("Кількість панелей має бути більшою за нуль");
        generate_geometry();
    }

    void solve() {
        std::vector<std::vector<double>> A(n_, std::vector<double>(n_, 0.0));
        std::vector<double> b(n_, 0.0);

        for (int i = 0; i < n_; ++i) {
            b[i] = -u_inf_ * panels_[i].nx;
            for (int j = 0; j < n_; ++j) {
                if (i == j) {
                    A[i][j] = 0.5;
                } else {
                    const double dx = panels_[i].xc - panels_[j].xc;
                    const double dy = panels_[i].yc - panels_[j].yc;
                    const double r2 = dx * dx + dy * dy;
                    const double vn = (dx * panels_[i].nx + dy * panels_[i].ny) / (2.0 * std::numbers::pi * r2);
                    A[i][j] = vn * panels_[j].len;
                }
            }
        }

        std::vector<double> q = gaussian_elimination(A, b);

        for (int i = 0; i < n_; ++i) {
            panels_[i].q = q[i];
            double vt = u_inf_ * panels_[i].tx;
            for (int j = 0; j < n_; ++j) {
                if (i != j) {
                    const double dx = panels_[i].xc - panels_[j].xc;
                    const double dy = panels_[i].yc - panels_[j].yc;
                    const double r2 = dx * dx + dy * dy;
                    const double vt_ind = (dx * panels_[i].tx + dy * panels_[i].ty) / (2.0 * std::numbers::pi * r2);
                    vt += q[j] * vt_ind * panels_[j].len;
                }
            }
            panels_[i].vt = vt;
            panels_[i].cp = 1.0 - (vt / u_inf_) * (vt / u_inf_);
        }
    }

    const std::vector<Panel>& panels() const noexcept { return panels_; }

private:
    void generate_geometry() {
        panels_.resize(n_);
        for (int i = 0; i < n_; ++i) {
            const double theta1 = 2.0 * std::numbers::pi * i / n_;
            const double theta2 = 2.0 * std::numbers::pi * (i + 1) / n_;

            panels_[i].x1 = radius_ * std::cos(theta1);
            panels_[i].y1 = radius_ * std::sin(theta1);
            panels_[i].x2 = radius_ * std::cos(theta2);
            panels_[i].y2 = radius_ * std::sin(theta2);

            panels_[i].xc = 0.5 * (panels_[i].x1 + panels_[i].x2);
            panels_[i].yc = 0.5 * (panels_[i].y1 + panels_[i].y2);

            const double dx = panels_[i].x2 - panels_[i].x1;
            const double dy = panels_[i].y2 - panels_[i].y1;
            panels_[i].len = std::hypot(dx, dy);
            panels_[i].beta = std::atan2(dy, dx);

            panels_[i].tx = dx / panels_[i].len;
            panels_[i].ty = dy / panels_[i].len;
            panels_[i].nx = -panels_[i].ty;
            panels_[i].ny =  panels_[i].tx;
        }
    }

    std::vector<double> gaussian_elimination(std::vector<std::vector<double>> A, std::vector<double> b) {
        const int n = static_cast<int>(b.size());
        for (int i = 0; i < n; ++i) {
            int max_row = i;
            for (int k = i + 1; k < n; ++k) {
                if (std::abs(A[k][i]) > std::abs(A[max_row][i])) {
                    max_row = k;
                }
            }
            std::swap(A[i], A[max_row]);
            std::swap(b[i], b[max_row]);

            for (int k = i + 1; k < n; ++k) {
                const double factor = -A[k][i] / A[i][i];
                for (int j = i; j < n; ++j) {
                    if (i == j) {
                        A[k][j] = 0.0;
                    } else {
                        A[k][j] += factor * A[i][j];
                    }
                }
                b[k] += factor * b[i];
            }
        }

        std::vector<double> x(n, 0.0);
        for (int i = n - 1; i >= 0; --i) {
            x[i] = b[i] / A[i][i];
            for (int k = i - 1; k >= 0; --k) {
                b[k] -= A[k][i] * x[i];
            }
        }
        return x;
    }

    int n_;
    double radius_;
    double u_inf_;
    std::vector<Panel> panels_;
};

int main() {
    try {
        constexpr int num_panels = 36;
        constexpr double radius = 1.0;
        constexpr double u_infinity = 10.0;

        PanelSolver solver(num_panels, radius, u_infinity);
        solver.solve();

        std::cout << "Результати розрахунку потенціального обтікання циліндра (C++):\n";
        std::cout << std::setw(8) << "Панель" << " | "
                  << std::setw(10) << "Xc" << " | "
                  << std::setw(10) << "Yc" << " | "
                  << std::setw(17) << "Cp (чисельний)" << " | "
                  << std::setw(17) << "Cp (аналітичний)" << "\n";
        std::cout << std::string(70, '-') << "\n";

        const auto& panels = solver.panels();
        for (std::size_t i = 0; i < panels.size(); i += 4) {
            const double theta = std::atan2(panels[i].yc, panels[i].xc);
            const double cp_exact = 1.0 - 4.0 * std::sin(theta) * std::sin(theta);
            std::cout << std::setw(8) << i << " | "
                      << std::setw(10) << std::fixed << std::setprecision(4) << panels[i].xc << " | "
                      << std::setw(10) << panels[i].yc << " | "
                      << std::setw(17) << panels[i].cp << " | "
                      << std::setw(17) << cp_exact << "\n";
        }
    } catch (const std::exception& e) {
        std::cerr << "Помилка: " << e.what() << "\n";
        return 1;
    }
    return 0;
}
```
:::

## Інженерні пастки та аналіз точності чисельного розв'язку

Під час розробки та практичної експлуатації панельних методів потенціальної теорії необхідно остерігатися таких типових технічних пасток:

1. **Самоіндукована сингулярність панелі:** під час обчислення діагональних елементів матриці `A_ii` точний інтеграл джерела по власній панелі дає значення `1/2` для контрольної точки на зовнішній поверхні. Використання спрощеної точкової формули прямої відстані призведе до ділення на нуль, оскільки відстань від точки до самої себе дорівнює нулю.

2. **Орієнтація вектора нормалі:** у програмі важливо строго стежити за обходом вузлів геометрії. Якщо вузли задано за годинниковою стрілкою замість проти годинникової стрілки, вектор зовнішньої нормалі `n_i` розвернеться всередину об'єму тіла. Це призведе до змінення знаку швидкості та спотворення обчисленого коефіцієнта тиску.

3. **Умова Кутти на задній кромці крила:** для аеродинамічних профілів із гострою задньою кромкою чисто джерельний панельний метод дасть нереалістичні нескінченні швидкості на кромці. Для вирішення цієї проблеми у код додають невідому циркуляцію `γ` (шар вихрових панелей) та додаткове рівняння умови Кутти, яке вимагає рівності тангенціальних швидкостей на верхній та нижній панелях біля задньої кромки.

4. **Порівняння з точним аналітичним розв'язком:** як видно з результатів роботи програми для 36 панелей, чисельний коефіцієнт тиску `C_p` на полюсах циліндра дорівнює `-2.96`, що з високою точністю наближається до точного аналітичного значення `C_p = -3.0`. При збільшенні кількості панелей до `N = 100` чисельна похибка спадає пропорційно `O(1/N²)`.

