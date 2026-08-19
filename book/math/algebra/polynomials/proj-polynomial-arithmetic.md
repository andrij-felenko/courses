# ⚙️ Реалізація поліноміальної арифметики: схема Горнера, множення та криві Безьє

Цей інженерний практикум містить завершені, виробничі реалізації ключових поліноміальних алгоритмів двома мовами — чистим C та сучасним C++: ефективне представлення многочленів у пам'яті, швидке та чисельно стійке обчислення значення за схемою Горнера, поліноміальне додавання й множення через згортку Коші, алгоритм ділення у стовпчик з остачею та обчислення параметричних точок на кривій Безьє за алгоритмом де Кастельжо. Кожен розділ супроводжується детальним аналізом часової та просторової складності, аналізом похибок обчислень із рухомою комою та розбором крайових випадків.

---

### 1. Архітектура представлення многочленів у пам'яті

Для обчислювальної роботи з многочленом `P(x) = aₙ·xⁿ + aₙ₋₁·xⁿ⁻¹ + … + a₁·x + a₀` у пам'яті комп'ютера необхідно обрати структуру даних, яка забезпечує мінімальні накладні витрати на доступ до елементів та максимальну локальність кешу процесора.

Існують два класичних підходи до представлення многочленів:
1. **Щільне представлення (англ. *dense representation*):** коефіцієнти зберігаються у неперервному динамічному масиві, де індекс елемента `i` строго відповідає показнику степеня `xⁱ`. Якщо певний проміжний степінь відсутній (наприклад, у многочлені `x¹⁰⁰ + 1`), у масиві зберігаються нулі. Цей підхід є оптимальним для многочленів помірного степеня (до сотень або тисяч), оскільки операції читання та запису коефіцієнта виконуються за `O(1)`, а послідовний обхід масиву ідеально лягає на векторні інструкції процесора (SIMD) та апаратний передзавантажувач пам'яті (hardware prefetcher).
2. **Розріджене представлення (англ. *sparse representation*):** зберігається список пар `(степінь, коефіцієнт)` лише для ненульових членів. Цей формат виправданий для гігантських розріджених поліномів у символьних системах комп'ютерної алгебри, але програє за швидкістю на щільних задачах через непряму адресацію та промахи кешу.

У наших реалізаціях використовується щільне представлення з так званим «прямим порядком» (англ. *little-endian indexing*):

```
Індекс комірки масиву [i]:    0     1     2     3    ...    n
Відповідний моном:          a₀·x⁰ a₁·x¹ a₂·x² a₃·x³ ...   aₙ·xⁿ
```

За такої угоди розмір масиву дорівнює `n + 1` (кількості коефіцієнтів), вільний член `a₀` завжди розташований за індексом `0`, а старший коефіцієнт `aₙ` — за індексом `n`.

**Інваріант нормалізації:**
Будь-який коректний ненульовий многочлен повинен задовольняти умову `aₙ ≠ 0`. Якщо в результаті операцій віднімання старші коефіцієнти обнулилися, розмір масиву необхідно зменшити (видалити фіктивні нулі), щоб степінь многочлена `deg P` визначався строго однозначно.

---

### 2. Схема Горнера та чисельна стійкість обчислення P(x)

Наївне обчислення значення многочлена полягає в піднесенні числа `x` до степеня `i` за допомогою викликів функції `pow(x, i)` або послідовного накопичення добутку з подальшим множенням на коефіцієнт `aᵢ` та додаванням.

Такий наївний підхід має два суттєві недоліки:
1. **Часова неефективність:** вимагає `O(n²)` операцій множення за наївного підходу або `2n` операцій за збереження проміжних степенів.
2. **Катастрофічна чисельна похибка:** пряме обчислення степенів великого показника `xⁱ` при `|x| > 1` швидко призводить до переповнення розрядної сітки (`overflow`), а при `|x| < 1` — до втрати точності через машинне занулення (`underflow`).

Схема Горнера (англ. *Horner's method*, описана англійським математиком Вільямом Джорджем Горнером у 1819 році та задовго до нього китайськими вченими епохи Сун) перетворює многочлен на вкладену форму з дужками:

```
P(x) = a₀ + x · (a₁ + x · (a₂ + … + x · (aₙ₋₁ + x · aₙ)…))
```

Алгоритм обчислює значення за один зворотний прохід масиву, починаючи зі старшого коефіцієнта `aₙ`. На кожному кроці поточний акумулятор множиться на `x` і до нього додається черговий коефіцієнт:

```
sₙ   = aₙ
sₙ₋₁ = sₙ · x + aₙ₋₁
sₙ₋₂ = sₙ₋₁ · x + aₙ₋₂
…
s₀   = s₁ · x + a₀ = P(x)
```

Схема Горнера вимагає рівно `n` операцій множення та `n` операцій додавання — це математично мінімально можлива кількість операцій для довільного полінома загального вигляду (теорема Островського).

**Аналіз чисельної похибки Вілкінсона:**
Джеймс Вілкінсон довів, що обчислене у машинній арифметиці значення `P̂(x)` за схемою Горнера задовольняє оцінку зворотної похибки:

```
|P̂(x) - P(x)| ≤ 2n · u · ∑ |aᵢ| · |x|ⁱ + O(u²)
```

де `u` — машинне епсилон (для типу `double` стандарту IEEE 754 величина `u ≈ 1.11 × 10⁻¹⁶`). Це свідчить про високу чисельну стійкість схеми Горнера для більшості аргументів.

Нижче наведено виробничі реалізації схеми Горнера мовами C та C++:

:::tabs
```c
#include <stdio.h>
#include <stddef.h>

/* Обчислення значення многочлена P(x) за схемою Горнера.
   coeffs: вказівник на масив коефіцієнтів [a0, a1, ..., an].
   deg: степінь многочлена n (розмір масиву становить deg + 1).
   x: аргумент, у якому обчислюється значення.
   Часова складність: O(n), просторова складність: O(1). */
double polynomial_eval_horner(const double *coeffs, size_t deg, double x) {
    if (coeffs == NULL) {
        return 0.0;
    }
    double result = coeffs[deg];
    for (size_t i = deg; i > 0; --i) {
        result = result * x + coeffs[i - 1];
    }
    return result;
}
```
```cpp
#include <iostream>
#include <span>
#include <vector>

// Обчислення P(x) за схемою Горнера для довільного неперервного діапазону коефіцієнтів.
// coeffs: послідовність коефіцієнтів [a0, a1, ..., an], де coeffs[i] відповідає моному a_i * x^i.
// Забезпечує noexcept таconstexpr сумісність.
[[nodiscard]] constexpr double evaluate_horner(std::span<const double> coeffs, double x) noexcept {
    if (coeffs.empty()) {
        return 0.0;
    }
    double result = coeffs.back();
    for (auto it = coeffs.rbegin() + 1; it != coeffs.rend(); ++it) {
        result = result * x + *it;
    }
    return result;
}
```
:::

---

### 3. Додавання та множення многочленів (дискретна згортка)

**Додавання:**
Додавання двох многочленів `A(x)` степеня `n` та `B(x)` степеня `m` здійснюється поелементним додаванням коефіцієнтів за однаковими індексами: `cᵢ = aᵢ + bᵢ`. Результуючий степінь не перевищує `max(n, m)`. Після додавання обов'язково виконується процедура нормалізації для видалення можливих нульових старших коефіцієнтів.

**Множення (згортка Коші):**
Добуток `C(x) = A(x) · B(x)` має степінь `n + m`. Кожен коефіцієнт `cₖ` (де `k` змінюється від `0` до `n + m`) обчислюється як сума всіх можливих попарних добутків `aᵢ · bⱼ`, для яких сума індексів дорівнює `k`:

```
cₖ = ∑ aᵢ · bⱼ    (для всіх i ∈ [0, n], j ∈ [0, m] таких, що i + j = k)
```

Цей класичний алгоритм має часову складність `O(n · m)` (або `O(n²)` для многочленів однакового степеня) та потребує `O(n + m)` додаткової пам'яті для збереження результату. Для астрономічно великих степенів (тисячі й мільйони членів у комп'ютерній алгебрі) застосовують швидке перетворення Фур'є (FFT), яке знижує складність до `O(n · log n)`, проте для інженерних задач базового та середнього масштабу пряма дискретна згортка є найшвидшою завдяки відсутності накладних витрат на комплексні експоненти та перестановки бітів.

:::tabs
```c
#include <stdlib.h>
#include <string.h>
#include <math.h>

typedef struct {
    double *coeffs;
    size_t degree;
} Polynomial;

/* Створення многочлена заданого степеня з ініціалізацією нулями */
Polynomial poly_create(size_t degree) {
    Polynomial p;
    p.degree = degree;
    p.coeffs = (double *)calloc(degree + 1, sizeof(double));
    return p;
}

/* Звільнення динамічної пам'яті */
void poly_free(Polynomial *p) {
    if (p && p->coeffs) {
        free(p->coeffs);
        p->coeffs = NULL;
        p->degree = 0;
    }
}

/* Нормалізація: видалення нульових коефіцієнтів на старших позиціях */
void poly_normalize(Polynomial *p) {
    if (!p || !p->coeffs) return;
    while (p->degree > 0 && fabs(p->coeffs[p->degree]) < 1e-12) {
        p->degree--;
    }
}

/* Додавання двох многочленів: C(x) = A(x) + B(x) */
Polynomial poly_add(const Polynomial *a, const Polynomial *b) {
    if (!a || !b) return poly_create(0);
    size_t max_deg = (a->degree > b->degree) ? a->degree : b->degree;
    Polynomial c = poly_create(max_deg);
    
    for (size_t i = 0; i <= max_deg; ++i) {
        double val_a = (i <= a->degree) ? a->coeffs[i] : 0.0;
        double val_b = (i <= b->degree) ? b->coeffs[i] : 0.0;
        c.coeffs[i] = val_a + val_b;
    }
    poly_normalize(&c);
    return c;
}

/* Множення двох многочленів: C(x) = A(x) * B(x) через дискретну згортку */
Polynomial poly_multiply(const Polynomial *a, const Polynomial *b) {
    if (!a || !b || !a->coeffs || !b->coeffs) {
        return poly_create(0);
    }
    size_t res_deg = a->degree + b->degree;
    Polynomial c = poly_create(res_deg);
    
    for (size_t i = 0; i <= a->degree; ++i) {
        for (size_t j = 0; j <= b->degree; ++j) {
            c.coeffs[i + j] += a->coeffs[i] * b->coeffs[j];
        }
    }
    poly_normalize(&c);
    return c;
}
```
```cpp
#include <vector>
#include <span>
#include <algorithm>
#include <cmath>
#include <iostream>

class Polynomial {
public:
    std::vector<double> coeffs;

    explicit Polynomial(size_t degree = 0) : coeffs(degree + 1, 0.0) {}
    explicit Polynomial(std::vector<double> c) : coeffs(std::move(c)) {
        normalize();
    }

    [[nodiscard]] size_t degree() const noexcept {
        return coeffs.empty() ? 0 : coeffs.size() - 1;
    }

    // Інваріант нормалізації: видалення фіктивних нульових старших коефіцієнтів
    void normalize() noexcept {
        while (coeffs.size() > 1 && std::abs(coeffs.back()) < 1e-12) {
            coeffs.pop_back();
        }
        if (coeffs.empty()) {
            coeffs.push_back(0.0);
        }
    }

    [[nodiscard]] friend Polynomial operator+(const Polynomial& a, const Polynomial& b) {
        const size_t max_deg = std::max(a.degree(), b.degree());
        Polynomial res(max_deg);
        for (size_t i = 0; i <= max_deg; ++i) {
            const double val_a = (i <= a.degree()) ? a.coeffs[i] : 0.0;
            const double val_b = (i <= b.degree()) ? b.coeffs[i] : 0.0;
            res.coeffs[i] = val_a + val_b;
        }
        res.normalize();
        return res;
    }

    [[nodiscard]] friend Polynomial operator*(const Polynomial& a, const Polynomial& b) {
        if (a.coeffs.empty() || b.coeffs.empty()) {
            return Polynomial(0);
        }
        Polynomial res(a.degree() + b.degree());
        for (size_t i = 0; i <= a.degree(); ++i) {
            for (size_t j = 0; j <= b.degree(); ++j) {
                res.coeffs[i + j] += a.coeffs[i] * b.coeffs[j];
            }
        }
        res.normalize();
        return res;
    }
};
```
:::

---

### 4. Алгоритм ділення многочленів у стовпчик з остачею

Алгоритм ділення многочлена `A(x)` на ненульовий многочлен `B(x)` обчислює частку `Q(x)` та остачу `R(x)` таку, що `A(x) = Q(x) · B(x) + R(x)`, де `deg R < deg B`.

**Покроковий механізм:**
1. Ініціалізуємо змінну поточної остачі `R(x) = A(x)`.
2. Якщо `deg R < deg B`, ділення завершено: частка `Q(x) = 0`, остача `R(x) = A(x)`.
3. Поки `deg R ≥ deg B`, знаходимо відношення старших членів:
   `factor = (старший коефіцієнт R) / (старший коефіцієнт B)`.
   Показник степеня цього монома дорівнює `k = deg R - deg B`.
4. Записуємо `factor` у коефіцієнт частки `Q[k]`.
5. Віднімаємо з поточної остачі добуток `factor · xᵏ · B(x)`. Ця операція гарантовано занулює старший коефіцієнт `R`, знижуючи його степінь як мінімум на 1.
6. Повторюємо цикл доти, доки степінь остачі не стане строго меншим за `deg B`.

**Обробка крайових випадків:**
- **Ділення на нульовий поліном:** є неприпустимою операцією (аналог ділення на нуль у числах). У C повертається нульовий результат із повідомленням про помилку, у C++ генерується виняток `std::invalid_argument`.
- **Малі старші коефіцієнти:** при роботі з числами з рухомою комою порівняння з нулем виконується через граничне значення `|bₘ| < 10⁻¹²`, щоб запобігти діленню на денормалізовані числа.

:::tabs
```c
#include <math.h>

/* Структура для повернення частки та остачі */
typedef struct {
    Polynomial quotient;
    Polynomial remainder;
} DivisionResult;

/* Поліноміальне ділення у стовпчик: A(x) = Q(x)*B(x) + R(x) */
DivisionResult poly_divide(const Polynomial *a, const Polynomial *b) {
    DivisionResult res;
    memset(&res, 0, sizeof(res));
    
    if (!a || !b || !b->coeffs || fabs(b->coeffs[b->degree]) < 1e-12) {
        return res; // Помилка: дільник є нульовим многочленом
    }
    
    // Якщо степінь діленого менший за степінь дільника
    if (a->degree < b->degree) {
        res.quotient = poly_create(0);
        res.remainder = poly_create(a->degree);
        memcpy(res.remainder.coeffs, a->coeffs, (a->degree + 1) * sizeof(double));
        return res;
    }
    
    size_t q_deg = a->degree - b->degree;
    res.quotient = poly_create(q_deg);
    
    // Копіюємо ділене в робочий буфер остачі
    Polynomial rem = poly_create(a->degree);
    memcpy(rem.coeffs, a->coeffs, (a->degree + 1) * sizeof(double));
    
    double lead_b = b->coeffs[b->degree];
    
    for (size_t i = a->degree; i >= b->degree; --i) {
        size_t q_idx = i - b->degree;
        double factor = rem.coeffs[i] / lead_b;
        res.quotient.coeffs[q_idx] = factor;
        
        for (size_t j = 0; j <= b->degree; ++j) {
            rem.coeffs[q_idx + j] -= factor * b->coeffs[j];
        }
        if (i == 0) break; // Захист від зациклення беззнакового size_t
    }
    
    poly_normalize(&res.quotient);
    poly_normalize(&rem);
    res.remainder = rem;
    return res;
}
```
```cpp
#include <utility>
#include <stdexcept>
#include <cmath>

struct PolyDivisionResult {
    Polynomial quotient;
    Polynomial remainder;
};

// Безпечне ділення з остачею з перевіркою інваріантів
[[nodiscard]] PolyDivisionResult divide(const Polynomial& a, const Polynomial& b) {
    if (b.coeffs.empty() || std::abs(b.coeffs.back()) < 1e-12) {
        throw std::invalid_argument("Помилка: ділення на нульовий многочлен");
    }

    if (a.degree() < b.degree()) {
        return { Polynomial(0), a };
    }

    const size_t q_deg = a.degree() - b.degree();
    Polynomial q(q_deg);
    Polynomial rem = a;

    const double lead_b = b.coeffs.back();

    for (size_t i = a.degree(); i >= b.degree(); --i) {
        const size_t q_idx = i - b.degree();
        const double factor = rem.coeffs[i] / lead_b;
        q.coeffs[q_idx] = factor;

        for (size_t j = 0; j <= b.degree(); ++j) {
            rem.coeffs[q_idx + j] -= factor * b.coeffs[j];
        }
        if (i == 0) break;
    }

    q.normalize();
    rem.normalize();
    return { std::move(q), std::move(rem) };
}
```
:::

---

### 5. Обчислення кривих Безьє за алгоритмом де Кастельжо

У комп'ютерній графіці та CAD-системах векторні криві описуються як параметричні поліноми `P(t) = (x(t), y(t))` для параметра часу або довжини `t ∈ [0, 1]`.

Класична кубічна крива Безьє визначається чотирма опорними точками `P₀, P₁, P₂, P₃` за формулою:

```
B(t) = (1 - t)³ · P₀ + 3(1 - t)²·t · P₁ + 3(1 - t)·t² · P₂ + t³ · P₃
```

Пряме розкриття цієї формули в коді з піднесенням до степеня страждає на похибки округлення. Французький математик та інженер компанії Citroën Поль де Кастельжо у 1959 році відкрив чисельно бездоганний рекурентний геометричний алгоритм: точка на кривій обчислюється через послідовні кроки лінійної інтерполяції (англ. *linear interpolation, lerp*) між контрольними вершинами.

**Геометричні властивості алгоритму де Кастельжо:**
1. **Опукла оболонка:** уся крива гарантовано лежить усередині опуклого многокутника контрольних точок (властивість опуклої оболонки), що критично важливо для швидкого визначення зіткнень у графічних рушіях.
2. **Афінна інваріантність:** поворот, масштабування чи перенесення контрольних точок еквівалентні перетворенню самої кривої.
3. **Чисельна стійкість:** оскільки `t ∈ [0, 1]` та `(1 - t) ∈ [0, 1]`, операція `lerp(A, B, t) = (1 - t)·A + t·B` є опуклою комбінацією, яка ніколи не спричиняє зростання похибки чи переповнення розрядної сітки.

:::tabs
```c
typedef struct {
    double x;
    double y;
} Point2D;

/* Лінійна інтерполяція між двома точками */
static inline Point2D lerp_point(Point2D p0, Point2D p1, double t) {
    Point2D p;
    p.x = (1.0 - t) * p0.x + t * p1.x;
    p.y = (1.0 - t) * p0.y + t * p1.y;
    return p;
}

/* Обчислення точки на кубічній кривій Безьє за алгоритмом де Кастельжо.
   points: масив із 4 контрольних вершин [P0, P1, P2, P3].
   t: параметр нормованого діапазону [0.0, 1.0].
   Складність: 6 операцій lerp, час O(1), пам'ять O(1). */
Point2D bezier_cubic_eval(const Point2D points[4], double t) {
    // Рівень 1: обчислення 3 проміжних точок на відрізках P0-P1, P1-P2, P2-P3
    Point2D q0 = lerp_point(points[0], points[1], t);
    Point2D q1 = lerp_point(points[1], points[2], t);
    Point2D q2 = lerp_point(points[2], points[3], t);

    // Рівень 2: обчислення 2 проміжних точок на відрізках q0-q1, q1-q2
    Point2D r0 = lerp_point(q0, q1, t);
    Point2D r1 = lerp_point(q1, q2, t);

    // Рівень 3: фінальна точка на кривій Безьє B(t)
    return lerp_point(r0, r1, t);
}
```
```cpp
#include <vector>
#include <span>
#include <concepts>

struct Point2D {
    double x{0.0};
    double y{0.0};

    [[nodiscard]] constexpr friend Point2D lerp(Point2D p0, Point2D p1, double t) noexcept {
        return {
            (1.0 - t) * p0.x + t * p1.x,
            (1.0 - t) * p0.y + t * p1.y
        };
    }
};

// Узагальнений алгоритм де Кастельжо для кривих Безьє довільного порядку n
// control_points: довільна кількість опорних точок (2 для відрізка, 3 для квадратичної, 4 для кубічної)
[[nodiscard]] Point2D evaluate_bezier_de_casteljau(std::span<const Point2D> control_points, double t) {
    if (control_points.empty()) {
        return {0.0, 0.0};
    }
    std::vector<Point2D> pts(control_points.begin(), control_points.end());
    for (size_t step = 1; step < control_points.size(); ++step) {
        for (size_t i = 0; i < control_points.size() - step; ++i) {
            pts[i] = lerp(pts[i], pts[i + 1], t);
        }
    }
    return pts.front();
}
```
:::

---

### 6. Комплексний тест та перевірка інваріантів

Наведений нижче тестовий стенд перевіряє коректність усіх реалізованих компонентів: множення двох поліномів, обчислення значення за схемою Горнера, ділення з остачею та обчислення координат кривої Безьє.

:::tabs
```c
int main(void) {
    // 1. Тест множення: A(x) = 2x + 3, B(x) = x^2 - 4x + 5
    // Очікуваний добуток: C(x) = 2x^3 - 5x^2 - 2x + 15
    Polynomial a = poly_create(1);
    a.coeffs[0] = 3.0;
    a.coeffs[1] = 2.0;

    Polynomial b = poly_create(2);
    b.coeffs[0] = 5.0;
    b.coeffs[1] = -4.0;
    b.coeffs[2] = 1.0;

    Polynomial c = poly_multiply(&a, &b);
    printf("Тест множення C(x): ");
    for (size_t i = 0; i <= c.degree; ++i) {
        printf("%+.1f*x^%zu ", c.coeffs[i], i);
    }
    printf("\n");

    // 2. Тест Горнера: C(2.0) = 2*(8) - 5*(4) - 2*(2) + 15 = 16 - 20 - 4 + 15 = 7.0
    double val = polynomial_eval_horner(c.coeffs, c.degree, 2.0);
    printf("Схема Горнера C(2.0) = %.2f (очікується 7.00)\n", val);

    // 3. Тест ділення: C(x) / A(x) має дати частку B(x) та остачу 0
    DivisionResult div = poly_divide(&c, &a);
    printf("Тест ділення C(x) / A(x) -> частка Q: ");
    for (size_t i = 0; i <= div.quotient.degree; ++i) {
        printf("%+.1f*x^%zu ", div.quotient.coeffs[i], i);
    }
    printf(", остача R: %.2f\n", div.remainder.coeffs[0]);

    // 4. Тест кривої Безьє
    Point2D ctrl[4] = {{0.0, 0.0}, {0.0, 1.0}, {1.0, 1.0}, {1.0, 0.0}};
    Point2D pt = bezier_cubic_eval(ctrl, 0.5);
    printf("Крива Безьє при t=0.5: (x=%.3f, y=%.3f) [очікується (0.500, 0.750)]\n", pt.x, pt.y);

    poly_free(&a);
    poly_free(&b);
    poly_free(&c);
    poly_free(&div.quotient);
    poly_free(&div.remainder);
    return 0;
}
```
```cpp
int main() {
    // 1. Тест множення: A(x) = 2x + 3, B(x) = x^2 - 4x + 5
    Polynomial a({3.0, 2.0});
    Polynomial b({5.0, -4.0, 1.0});
    Polynomial c = a * b;

    std::cout << "Тест множення C(x): ";
    for (size_t i = 0; i <= c.degree(); ++i) {
        std::cout << (c.coeffs[i] >= 0 ? "+" : "") << c.coeffs[i] << "*x^" << i << " ";
    }
    std::cout << "\n";

    // 2. Тест Горнера: C(2.0)
    double val = evaluate_horner(c.coeffs, 2.0);
    std::cout << "Схема Горнера C(2.0) = " << val << " (очікується 7.0)\n";

    // 3. Тест ділення
    auto [quotient, remainder] = divide(c, a);
    std::cout << "Тест ділення -> частка Q: ";
    for (size_t i = 0; i <= quotient.degree(); ++i) {
        std::cout << (quotient.coeffs[i] >= 0 ? "+" : "") << quotient.coeffs[i] << "*x^" << i << " ";
    }
    std::cout << ", остача R: " << remainder.coeffs.front() << "\n";

    // 4. Тест Безьє
    std::vector<Point2D> ctrl{{0.0, 0.0}, {0.0, 1.0}, {1.0, 1.0}, {1.0, 0.0}};
    Point2D pt = evaluate_bezier_de_casteljau(ctrl, 0.5);
    std::cout << "Крива Безьє при t=0.5: (x=" << pt.x << ", y=" << pt.y << ") [очікується (0.5, 0.75)]\n";

    return 0;
}
```
:::

Усі наведені алгоритми мають суворі гарантії ресурсної коректності (відсутність витоків пам'яті завдяки RAII у C++ та симетричним функціям створення/звільнення у C) і готові для використання у виробничих бібліотеках чисельного аналізу, комп'ютерного зору та графіки.
