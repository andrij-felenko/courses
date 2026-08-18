# ⚙️ Чисельне обчислення циркуляції магнітного поля вздовж довільного контуру

У цьому практичному проекті ми створимо повноцінну програму для чисельного розрахунку циркуляції магнітного поля `∮ B · dl` вздовж довільного двовимірного замкненого контуру у просторі, де розташована довільна система паралельних провідників зі струмом. 

Моделювання дозволяє чисельно перевірити виконання закону Ампера для складних геометрій контурів та струмів, що виходить за межі простих аналітичних симетрій. Ми детально проаналізуємо математичну модель, методи обчислювальної інтеграції, алгоритми обробки крайових випадків, оцінку обчислювальної складності та реалізуємо програму мовами C та C++.

---

## 1. Фізико-математична модель та чисельний метод

Розглянемо двовимірну плоско-паралельну задачу в декартовій системі координат `XY`. Нехай у просторі розташовано `N` нескінченно довгих паралельних металевих провідників, що орієнтовані перпендикулярно до площини `XY` (паралельно осі `Z`). Провідники перетинають площину у точках з координатами `(x_k, y_k)` та несуть постійні електричні струми `I_k`, де `k = 1, 2, ..., N`. Алгебраїчний знак струму `I_k` визначає його напрямок: додатне значення відповідає струму, спрямованому уздовж осі `Z` на спостерігача (значок `⊙`), а від'ємне — від спостерігача (значок `⊗`).

Згідно із диференціальним законом Біо — Савара, один точковий провідник з номером `k`, розташований у точці `(x_k, y_k)`, створює в довільній точці спостереження `P(x, y)` магнітне поле, вектор індукції якого `B_k` є ортогональним до радіус-вектора `r_k = (x − x_k, y − y_k)`. Компоненти вектора індукції `B_k = (B_x,k, B_y,k)` визначаються співвідношеннями:

```
r_k² = (x − x_k)² + (y − y_k)²

B_x,k(x, y) = − (μ₀ · I_k / (2·π)) · (y − y_k) / r_k²
B_y,k(x, y) =   (μ₀ · I_k / (2·π)) · (x − x_k) / r_k²
```

За принципом суперпозиції векторних полів, сумарний вектор магнітної індукції `B(x, y)` у довільній точці обчислюється як векторна сума внесків від усіх `N` провідників:

```
B_x(x, y) = ∑_{k=1}^{N} B_x,k(x, y)
B_y(x, y) = ∑_{k=1}^{N} B_y,k(x, y)
```

### Дискретизація криволінійного інтеграла

Нехай контур обходу `L` задано у вигляді замкненої параметричної кривої `(x(t), y(t))`, де параметр `t` змінюється від `0` до `1`. Криволінійний інтеграл другого роду, що визначає циркуляцію магнітного поля, за визначенням дорівнює:

```
∮_L B · dl = ∫₀¹ ( B_x(x(t), y(t)) · (dx/dt) + B_y(x(t), y(t)) · (dy/dt) ) dt
```

Для обчислення цього інтеграла на ЕОМ ми розбиваємо контур `L` на `M` малих орієнтованих прямолінійних сегментів з вершинами `P_0, P_1, P_2, ..., P_M`, де `P_M = P_0` (умова замкненості). 

Для кожного `j`-го сегмента між вершинами `P_j(X_j, Y_j)` та `P_{j+1}(X_{j+1}, Y_{j+1})`:
1. Вектор приросту довжини `dl_j` має компоненти:

```
Δx_j = X_{j+1} − X_j
Δy_j = Y_{j+1} − Y_j
```

2. Точка обчислення поля обирається як середина сегмента (метод середніх прямокутників / трапецій другої точності):

```
x_mid,j = (X_j + X_{j+1}) / 2
y_mid,j = (Y_j + Y_{j+1}) / 2
```

3. Скалярний добуток `B · dl` на сегменті `j` дорівнює:

```
ΔC_j = B_x(x_mid,j, y_mid,j) · Δx_j + B_y(x_mid,j, y_mid,j) · Δy_j
```

Підсумкова чисельна циркуляція є сумою по всіх `M` сегментах:

```
C_числ = ∑_{j=0}^{M-1} ΔC_j
```

Згідно з теоретичним законом Ампера, при прямуванні кількості сегментів `M → ∞` чисельна величина `C_числ` повинна строго прямувати до теоретичної величини `C_теор = μ₀ · ∑_{k ∈ охоплені} I_k`.

---

## 2. Алгоритмічний аналіз, складність та пастки обчислень

Для забезпечення високої точності та стабільності чисельних обчислень необхідно врахувати декілька фундаментальних алгоритмічних особливостей:

### 2.1. Алгоритмічна складність

Для обчислення циркуляції по `M` сегментах контуру у системі з `N` провідниками алгоритм виконує обчислення поля у кожній середній точці. Оскільки внесок кожного з `N` провідників додається незалежно, обчислювальна складність алгоритму становить `O(N · M)`. 

Для типових практичних розрахунків (`N ≈ 10` провідників, `M ≈ 2000` сегментів) алгоритм виконує близько `2 × 10⁴` операцій, що займає менше однієї мілісекунди на сучасному процесорі.

### 2.2. Сингулярність точки джерела (`1 / r` сингулярність)

Якщо контур інтегрування проходить надзвичайно близько від одного з провідників, відстань `r_k` прямує до нуля, а модуль індукції `B` та його просторові похідні прямують до нескінченності (`B ∝ 1/r`). Це призводить до різкої втрати точності чисельного інтегрування методом трапецій. 

Для уникнення ділення на нуль та обчислювального переповнення у програмі вводиться регуляризаційний параметр `ε² ≈ 10⁻¹⁴` у знаменнику (`r_k² + ε²`). Якщо контур проходить безпосередньо через самий провідник, інтеграл стає невизначеним з точки зору класичної теорії (потрібно враховувати кінцевий радіус провідника та розподіл струму у ньому).

### 2.3. Орієнтація контуру та правило правого гвинта

Напрямок нумерації вершин контуру `P_0 → P_1 → ... → P_M` визначає векторний напрямок `dl`. Якщо вершини перелічено за годинниковою стрілкою, отриманий інтеграл змінить знак на протилежний (`−μ₀ · I_охоп`). 

У програмі реалізовано автоматичне генерування замкнених контурів у додатному напрямку (проти годинникової стрілки).

### 2.4. Аналіз похибки та збіжності

Похибка квадратурної формули середніх прямокутників має порядок `O(h²)`, де `h = L_контуру / M` — крок дискретизації контуру. Збільшення кількості точок `M` з 100 до 2000 зменшує числову похибку розрахунку циркуляції приблизно у 400 разів, що дозволяє досягати відносної точності вище `99.999%`.

---

## 3. Вихідний код програми (C та C++)

Нижче наведено повні робочі реалізації алгоритму чисельного обчислення циркуляції магнітного поля.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

// Магнітна стала μ₀ (Гн/м)
#define MU_0 (4.0 * M_PI * 1e-7)

// Структура для опису прямолінійного провідника зі струмом
typedef struct {
    double x;       // X-координата провідника у метрах
    double y;       // Y-координата провідника у метрах
    double current; // Величина струму в Амперах (знак вказує напрямок)
} Wire;

// Структура для опису 2D точки / вектора
typedef struct {
    double x;
    double y;
} Point2D;

/**
 * Обчислює сумарний вектор магнітної індукції B = (Bx, By) у точці спостереження (x, y)
 * від усієї сукупності провідників за принципом суперпозиції.
 */
void compute_magnetic_field(double x, double y, const Wire* wires, size_t num_wires, double* bx, double* by) {
    *bx = 0.0;
    *by = 0.0;
    const double eps_sq = 1e-14; // Регуляризація для уникнення ділення на 0

    for (size_t i = 0; i < num_wires; ++i) {
        double dx = x - wires[i].x;
        double dy = y - wires[i].y;
        double r2 = dx * dx + dy * dy;

        // Якщо точка збігається з центром провідника, пропускаємо для уникнення сингулярності
        if (r2 < eps_sq) {
            continue;
        }

        // Закон Біо — Савара для прямого струму: B = (μ₀ · I) / (2·π·r)
        double coeff = (MU_0 * wires[i].current) / (2.0 * M_PI * r2);
        *bx += -coeff * dy;
        *by +=  coeff * dx;
    }
}

/**
 * Обчислює криволінійний інтеграл (циркуляцію) ∮ B · dl вздовж замкненого полігонального контуру.
 */
double calculate_circulation(const Point2D* contour, size_t num_points, const Wire* wires, size_t num_wires) {
    double circulation = 0.0;

    for (size_t i = 0; i < num_points; ++i) {
        size_t next_i = (i + 1) % num_points;

        // Початок та кінець поточного сегмента контуру
        double x1 = contour[i].x;
        double y1 = contour[i].y;
        double x2 = contour[next_i].x;
        double y2 = contour[next_i].y;

        // Обчислення середини сегмента (для підвищення точності квадратури)
        double x_mid = (x1 + x2) * 0.5;
        double y_mid = (y1 + y2) * 0.5;

        // Вектор елемента довжини dl = (dx, dy)
        double dl_x = x2 - x1;
        double dl_y = y2 - y1;

        // Обчислення вектора індукції B у середній точці
        double bx, by;
        compute_magnetic_field(x_mid, y_mid, wires, num_wires, &bx, &by);

        // Скалярний добуток B · dl
        circulation += (bx * dl_x + by * dl_y);
    }

    return circulation;
}

int main(void) {
    printf("=====================================================\n");
    printf("   Чисельне моделювання теореми Ампера про циркуляцію  \n");
    printf("=====================================================\n\n");

    // 1. Конфігурація джерел струму у просторі
    Wire wires[] = {
        { .x =  0.02, .y =  0.01, .current =  12.5 }, // Всередині контуру (+12.5 А)
        { .x = -0.04, .y = -0.03, .current =  -5.0 }, // Всередині контуру (-5.0 А)
        { .x =  0.35, .y =  0.40, .current =  50.0 }  // Зовні контуру (+50.0 А)
    };
    size_t num_wires = sizeof(wires) / sizeof(wires[0]);

    // 2. Створення замкненого еліптичного контуру (піввісі a=0.20м, b=0.10м)
    size_t contour_steps = 2000;
    Point2D* contour = (Point2D*)malloc(contour_steps * sizeof(Point2D));
    if (!contour) {
        fprintf(stderr, "Помилка виділення пам'яті під контур!\n");
        return 1;
    }

    double a = 0.20; // Велика піввісь (м)
    double b = 0.10; // Мала піввісь (м)
    for (size_t i = 0; i < contour_steps; ++i) {
        double angle = 2.0 * M_PI * (double)i / (double)contour_steps;
        contour[i].x = a * cos(angle);
        contour[i].y = b * sin(angle);
    }

    // 3. Обчислення чисельної циркуляції
    double calc_circ = calculate_circulation(contour, contour_steps, wires, num_wires);

    // 4. Теоретичне значення за законом Ампера: μ₀ · (I₁ + I₂)
    double enclosed_current = wires[0].current + wires[1].current; // 12.5 - 5.0 = 7.5 A
    double theory_circ = MU_0 * enclosed_current;
    double rel_error = fabs(calc_circ - theory_circ) / theory_circ * 100.0;

    printf("Розташування провідників:\n");
    for (size_t i = 0; i < num_wires; ++i) {
        printf("  Провідник №%zu: pos=(%.2f, %.2f) м, струм = %+.1f A\n", 
               i + 1, wires[i].x, wires[i].y, wires[i].current);
    }

    printf("\nПараметри контуру інтегрування:\n");
    printf("  Тип: Еліпс (a=%.2f м, b=%.2f м), кількість сегментів = %zu\n\n", a, b, contour_steps);

    printf("РЕЗУЛЬТАТИ ОБЧИСЛЕННЯ:\n");
    printf("  Сумарний охоплений струм (I_охоп): %+.3f A\n", enclosed_current);
    printf("  Чисельна циркуляція ∮ B·dl:        %.9e Тл·м\n", calc_circ);
    printf("  Теоретична циркуляція (μ₀·I_охоп):  %.9e Тл·м\n", theory_circ);
    printf("  Відносна обчислювальна похибка:    %.6f %%\n", rel_error);

    free(contour);
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <cmath>
#include <numbers>
#include <iomanip>
#include <numeric>

// Двовимірний вектор та операції над ним
struct Vector2D {
    double x{0.0};
    double y{0.0};

    [[nodiscard]] constexpr Vector2D operator+(const Vector2D& other) const noexcept {
        return {x + other.x, y + other.y};
    }

    [[nodiscard]] constexpr Vector2D operator-(const Vector2D& other) const noexcept {
        return {x - other.x, y - other.y};
    }

    [[nodiscard]] constexpr Vector2D operator*(double scalar) const noexcept {
        return {x * scalar, y * scalar};
    }

    [[nodiscard]] constexpr double dot(const Vector2D& other) const noexcept {
        return x * other.x + y * other.y;
    }

    [[nodiscard]] double lengthSquared() const noexcept {
        return x * x + y * y;
    }
};

// Провідник зі струмом
struct Wire {
    Vector2D position;
    double current{0.0}; // Струм у Амперах
};

class AmpereSimulator {
public:
    static constexpr double mu_0 = 4.0 * std::numbers::pi * 1e-7;

    /**
     * Обчислює вектор магнітної індукції B у точці point від усіх провідників.
     */
    [[nodiscard]] static Vector2D computeField(Vector2D point, const std::vector<Wire>& wires) noexcept {
        Vector2D b_total{0.0, 0.0};
        constexpr double eps_sq = 1e-14;

        for (const auto& wire : wires) {
            Vector2D r = point - wire.position;
            double r2 = r.lengthSquared();

            if (r2 < eps_sq) {
                continue; // Ігноруємо точку джерела
            }

            double coeff = (mu_0 * wire.current) / (2.0 * std::numbers::pi * r2);
            b_total.x += -coeff * r.y;
            b_total.y +=  coeff * r.x;
        }

        return b_total;
    }

    /**
     * Обчислює циркуляцію поля B вздовж замкненого контуру.
     */
    [[nodiscard]] static double calculateCirculation(const std::vector<Vector2D>& contour, 
                                                      const std::vector<Wire>& wires) noexcept {
        if (contour.size() < 3) return 0.0;

        double circulation = 0.0;
        const size_t n = contour.size();

        for (size_t i = 0; i < n; ++i) {
            const Vector2D& p1 = contour[i];
            const Vector2D& p2 = contour[(i + 1) % n];

            Vector2D mid = (p1 + p2) * 0.5;
            Vector2D dl = p2 - p1;

            Vector2D b = computeField(mid, wires);
            circulation += b.dot(dl);
        }

        return circulation;
    }
};

int main() {
    std::cout << "=====================================================\n";
    std::cout << "   C++ Обчислювальний модуль закону Ампера           \n";
    std::cout << "=====================================================\n\n";

    // 1. Ініціалізація джерел струму
    const std::vector<Wire> wires = {
        { .position = { 0.02,  0.01}, .current =  12.5 }, // Всередині
        { .position = {-0.04, -0.03}, .current =  -5.0 }, // Всередині
        { .position = { 0.35,  0.40}, .current =  50.0 }  // Зовні
    };

    // 2. Генерація замкненого контуру у формі прямокутника зі зрізаними кутами
    constexpr size_t segments_per_side = 500;
    std::vector<Vector2D> contour;
    contour.reserve(segments_per_side * 4);

    constexpr double x_min = -0.15, x_max = 0.15;
    constexpr double y_min = -0.10, y_max = 0.10;

    // Нижня сторона (зліва направо)
    for (size_t i = 0; i < segments_per_side; ++i) {
        double t = static_cast<double>(i) / segments_per_side;
        contour.push_back({ x_min + t * (x_max - x_min), y_min });
    }
    // Права сторона (знизу вгору)
    for (size_t i = 0; i < segments_per_side; ++i) {
        double t = static_cast<double>(i) / segments_per_side;
        contour.push_back({ x_max, y_min + t * (y_max - y_min) });
    }
    // Верхня сторона (справа наліво)
    for (size_t i = 0; i < segments_per_side; ++i) {
        double t = static_cast<double>(i) / segments_per_side;
        contour.push_back({ x_max - t * (x_max - x_min), y_max });
    }
    // Ліва сторона (згори вниз)
    for (size_t i = 0; i < segments_per_side; ++i) {
        double t = static_cast<double>(i) / segments_per_side;
        contour.push_back({ x_min, y_max - t * (y_max - y_min) });
    }

    // 3. Розрахунок чисельної циркуляції
    const double calc_circ = AmpereSimulator::calculateCirculation(contour, wires);

    // 4. Порівняння з теорією
    const double enclosed_current = wires[0].current + wires[1].current;
    const double theory_circ = AmpereSimulator::mu_0 * enclosed_current;
    const double rel_error = std::abs(calc_circ - theory_circ) / theory_circ * 100.0;

    std::cout << std::fixed << std::setprecision(6);
    std::cout << "Параметри моделювання:\n";
    std::cout << "  Кількість точок контуру: " << contour.size() << "\n";
    std::cout << "  Сумарний охоплений струм: " << enclosed_current << " A\n\n";

    std::cout << std::scientific << std::setprecision(9);
    std::cout << "  Чисельна циркуляція ∮ B·dl:  " << calc_circ << " Тл·м\n";
    std::cout << "  Теоретична циркуляція μ₀·I:  " << theory_circ << " Тл·м\n";
    std::cout << std::fixed << std::setprecision(6);
    std::cout << "  Відносна похибка розрахунку: " << rel_error << " %\n";

    return 0;
}
```
:::

---

## 4. Фізичний аналіз результатів та висновки

1. **Компенсація зовнішніх струмів:** Результати чисельного моделювання переконливо доводять фундаментальне положення теорії: провідник №3 зі струмом `+50.0 A`, що лежить поза контуром, створює у точках контуру магнітне поле індукцією до `2.5 × 10⁻⁵ Тл`. Проте його інтегральний внесок у циркуляцію вздовж замкненого контуру строго обнуляється (допоки похибка чисельного інтегрування становить менше `0.0001%`).
2. **Незалежність від форми контуру:** Заміна кругового контуру на еліптичний або прямокутний не змінює величини підсумкової циркуляції: вона визначається виключно сумою охопленого струму `I_охоп = 12.5 − 5.0 = 7.5 A`.
3. **Практичне застосування:** Описаний алгоритм є базовим ядром для розробки спеціалізованого програмного забезпечення розрахунку паразитних магнітних наведень у силових кабелях, проектування систем магнітного захисту та обчислення взаємної індуктивності складних шинопроводів.
