# ⚙️ Поліноміальна арифметика, алгоритм Безу та базиси Грьобнера в коді

Теоретичні конструкції кілець многочленів вимагають точної алгоритмічної реалізації: обчислення частки й остачі, пошук найбільшого спільного дільника та розв'язання нелінійних алгебраїчних систем через базиси Грьобнера. Нижче подано структури даних та алгоритми комп'ютерної алгебри над числовими полями.

---

### Структури даних для поліномів: щільне та розріджене представлення

У комп'ютерній алгебрі вибір структури даних для многочлена визначається кількістю змінних та щільністю ненульових коефіцієнтів:

1. **Щільне представлення (Dense representation):**
   Многочлен від однієї змінної `f(x) = ∑ aᵢ xⁱ` зберігається як динамічний масив (вектор) коефіцієнтів `[a₀, a₁, …, aₙ]`, де індекс елемента прямо відповідає показнику степеня.
   - *Переваги:* прямий доступ за `O(1)` до коефіцієнта будь-якого степеня, компактне розміщення в кеш-пам'яті процесора, простота покомпонентного додавання.
   - *Недоліки:* якщо многочлен є розрідженим (наприклад, `x¹⁰⁰⁰⁰⁰⁰ + 1`), вектор зберігатиме мільйон нулів, витрачаючи гігабайти пам'яті.

2. **Розріджене представлення (Sparse representation):**
   Многочлен зберігається як впорядкований список або хеш-таблиця пар `(коефіцієнт, моном)`. Це єдиний життєздатний підхід для многочленів від багатьох змінних `K[x₁, …, xₙ]`, де кількість потенційних мономів зростає комбінаторно.

Для забезпечення абсолютної точності в полі раціональних чисел `ℚ` коефіцієнти представляються структурою нескоротного дробу `Rational` (чисельник і знаменник як цілі числа довільної або фіксованої розрядності із постійним скороченням на їхній спільний дільник через `std::gcd`).

---

### Задача 1: Евклідове ділення та розширений алгоритм Евкліда для многочленів

**Постановка задачі:**
Маючи два многочлени `f(x)` та `g(x)` з раціональними коефіцієнтами (`ℚ[x]`), реалізувати:
1. Поліноміальне ділення з остачею: `f(x) = q(x) · g(x) + r(x)`, де `deg(r) < deg(g)` або `r = 0`.
2. Розширений алгоритм Евкліда для знаходження монічного `НСД(f, g) = d(x)` та співвідношення Безу: `u(x) · f(x) + v(x) · g(x) = d(x)`.

**Ідея алгоритму та інваріанти:**
Многочлен задається масивом коефіцієнтів від молодшого степеня до старшого. На кожному кроці ділення вираховуємо коефіцієнт `c = lead(f) / lead(g)` та степінь `k = deg(f) - deg(g)`, віднімаємо `c · xᵏ · g(x)` від діленого і накопичуємо мономи в частці `q(x)`. Часова складність ділення становить `O(n · m)` арифметичних операцій у полі `K`, де `n = deg(f)` та `m = deg(g)`.

Розширений алгоритм Евкліда підтримує матрицю перетворень для поліноміальних співмножників Безу. На кожній ітерації зберігається інваріант:
```
u_k(x) · f(x) + v_k(x) · g(x) = r_k(x)
```
де степінь остач строго монотонно спадає: `deg(r_k) < deg(r_{k-1})`. Після завершення алгоритму результат ділиться на старший коефіцієнт останньої ненульової остачі, що робить `НСД` унітарним (монічним).

:::tabs
```cpp
#include <iostream>
#include <vector>
#include <numeric>
#include <cmath>
#include <algorithm>
#include <stdexcept>

// Раціональне число (дріб) для точної арифметики без похибок із рухомою комою
struct Rational {
    long long num{0};
    long long den{1};

    Rational(long long n = 0, long long d = 1) : num(n), den(d) {
        if (den == 0) throw std::invalid_argument("Знаменник не може дорівнювати нулю");
        if (den < 0) { num = -num; den = -den; }
        long long g = std::gcd(std::abs(num), den);
        if (g > 0) { num /= g; den /= g; }
    }

    Rational operator+(const Rational& o) const { return {num * o.den + o.num * den, den * o.den}; }
    Rational operator-(const Rational& o) const { return {num * o.den - o.num * den, den * o.den}; }
    Rational operator*(const Rational& o) const { return {num * o.num, den * o.den}; }
    Rational operator/(const Rational& o) const { return {num * o.den, den * o.num}; }
    bool operator==(const Rational& o) const { return num == o.num && den == o.den; }
    bool operator!=(const Rational& o) const { return !(*this == o); }
    bool is_zero() const { return num == 0; }
};

class Polynomial {
public:
    std::vector<Rational> coeffs; // coeffs[i] — коефіцієнт при x^i

    Polynomial() = default;
    Polynomial(std::initializer_list<Rational> list) : coeffs(list) { normalize(); }
    explicit Polynomial(std::vector<Rational> c) : coeffs(std::move(c)) { normalize(); }

    void normalize() {
        while (coeffs.size() > 1 && coeffs.back().is_zero()) {
            coeffs.pop_back();
        }
        if (coeffs.empty()) coeffs.push_back(Rational(0));
    }

    int deg() const {
        return (coeffs.size() == 1 && coeffs[0].is_zero()) ? -1 : static_cast<int>(coeffs.size()) - 1;
    }

    bool is_zero() const { return deg() == -1; }

    Rational lead() const { return coeffs.back(); }

    Polynomial operator+(const Polynomial& o) const {
        size_t n = std::max(coeffs.size(), o.coeffs.size());
        std::vector<Rational> res(n, Rational(0));
        for (size_t i = 0; i < coeffs.size(); ++i) res[i] = res[i] + coeffs[i];
        for (size_t i = 0; i < o.coeffs.size(); ++i) res[i] = res[i] + o.coeffs[i];
        return Polynomial(res);
    }

    Polynomial operator-(const Polynomial& o) const {
        size_t n = std::max(coeffs.size(), o.coeffs.size());
        std::vector<Rational> res(n, Rational(0));
        for (size_t i = 0; i < coeffs.size(); ++i) res[i] = res[i] + coeffs[i];
        for (size_t i = 0; i < o.coeffs.size(); ++i) res[i] = res[i] - o.coeffs[i];
        return Polynomial(res);
    }

    Polynomial operator*(const Polynomial& o) const {
        if (is_zero() || o.is_zero()) return Polynomial({Rational(0)});
        std::vector<Rational> res(coeffs.size() + o.coeffs.size() - 1, Rational(0));
        for (size_t i = 0; i < coeffs.size(); ++i) {
            for (size_t j = 0; j < o.coeffs.size(); ++j) {
                res[i + j] = res[i + j] + (coeffs[i] * o.coeffs[j]);
            }
        }
        return Polynomial(res);
    }

    Polynomial operator*(const Rational& scalar) const {
        if (scalar.is_zero()) return Polynomial({Rational(0)});
        std::vector<Rational> res = coeffs;
        for (auto& c : res) c = c * scalar;
        return Polynomial(res);
    }
};

// Ділення з остачею: f = q * g + r
std::pair<Polynomial, Polynomial> div_rem(Polynomial f, const Polynomial& g) {
    if (g.is_zero()) throw std::invalid_argument("Ділення на нульовий многочлен");
    Polynomial q({Rational(0)});
    while (!f.is_zero() && f.deg() >= g.deg()) {
        int shift = f.deg() - g.deg();
        Rational factor = f.lead() / g.lead();
        std::vector<Rational> m_coeffs(shift + 1, Rational(0));
        m_coeffs[shift] = factor;
        Polynomial monom(m_coeffs);

        q = q + monom;
        f = f - (monom * g);
    }
    return {q, f};
}

// Розширений алгоритм Евкліда: знаходить gcd, u, v такі, що u*f + v*g = gcd (монічний)
struct BezoutResult {
    Polynomial gcd;
    Polynomial u;
    Polynomial v;
};

BezoutResult ext_gcd(Polynomial a, Polynomial b) {
    Polynomial u0({Rational(1)}), u1({Rational(0)});
    Polynomial v0({Rational(0)}), v1({Rational(1)});

    while (!b.is_zero()) {
        auto [q, r] = div_rem(a, b);
        a = b;
        b = r;

        Polynomial next_u = u0 - (q * u1);
        u0 = u1;
        u1 = next_u;

        Polynomial next_v = v0 - (q * v1);
        v0 = v1;
        v1 = next_v;
    }

    // Нормалізація до унітарного многочлена (старший коефіцієнт = 1)
    Rational lead_c = a.lead();
    Rational inv_c = Rational(1) / lead_c;
    return {a * inv_c, u0 * inv_c, v0 * inv_c};
}
```
```py
from fractions import Fraction

class Polynomial:
    def __init__(self, coeffs):
        # coeffs[i] відповідає степеню x^i
        self.coeffs = [Fraction(c) for c in coeffs]
        self._normalize()

    def _normalize(self):
        while len(self.coeffs) > 1 and self.coeffs[-1] == 0:
            self.coeffs.pop()
        if not self.coeffs:
            self.coeffs = [Fraction(0)]

    def deg(self):
        if len(self.coeffs) == 1 and self.coeffs[0] == 0:
            return -1
        return len(self.coeffs) - 1

    def is_zero(self):
        return self.deg() == -1

    def lead(self):
        return self.coeffs[-1]

    def __add__(self, other):
        n = max(len(self.coeffs), len(other.coeffs))
        c1 = self.coeffs + [Fraction(0)] * (n - len(self.coeffs))
        c2 = other.coeffs + [Fraction(0)] * (n - len(other.coeffs))
        return Polynomial([a + b for a, b in zip(c1, c2)])

    def __sub__(self, other):
        n = max(len(self.coeffs), len(other.coeffs))
        c1 = self.coeffs + [Fraction(0)] * (n - len(self.coeffs))
        c2 = other.coeffs + [Fraction(0)] * (n - len(other.coeffs))
        return Polynomial([a - b for a, b in zip(c1, c2)])

    def __mul__(self, other):
        if isinstance(other, (int, Fraction)):
            return Polynomial([c * Fraction(other) for c in self.coeffs])
        if self.is_zero() or other.is_zero():
            return Polynomial([0])
        res = [Fraction(0)] * (len(self.coeffs) + len(other.coeffs) - 1)
        for i, a in enumerate(self.coeffs):
            for j, b in enumerate(other.coeffs):
                res[i + j] += a * b
        return Polynomial(res)


def div_rem(f: Polynomial, g: Polynomial):
    if g.is_zero():
        raise ZeroDivisionError("Ділення на нульовий многочлен")
    q = Polynomial([0])
    cur = Polynomial(f.coeffs)
    while not cur.is_zero() and cur.deg() >= g.deg():
        shift = cur.deg() - g.deg()
        factor = cur.lead() / g.lead()
        monom_coeffs = [Fraction(0)] * (shift + 1)
        monom_coeffs[shift] = factor
        monom = Polynomial(monom_coeffs)
        q = q + monom
        cur = cur - (monom * g)
    return q, cur


def ext_gcd(a: Polynomial, b: Polynomial):
    u0, u1 = Polynomial([1]), Polynomial([0])
    v0, v1 = Polynomial([0]), Polynomial([1])
    while not b.is_zero():
        q, r = div_rem(a, b)
        a, b = b, r
        u0, u1 = u1, u0 - (q * u1)
        v0, v1 = v1, v0 - (q * v1)

    lead_c = a.lead()
    inv_c = Fraction(1, 1) / lead_c
    return a * inv_c, u0 * inv_c, v0 * inv_c
```
:::

---

### Задача 2: Побудова базису Грьобнера (Алгоритм Бухбергера) для ℚ[x, y]

**Постановка задачі:**
Для скінченного набору поліномів `{f₁, f₂, …, fₘ} ⊆ ℚ[x, y]` від двох змінних знайти базис Грьобнера `G` ідеалу `I = ⟨f₁, …, fₘ⟩` щодо градуйованого обернено-лексикографічного порядку (grevlex).

**Ідея алгоритму та структура редукції:**
1. **Мономіальний порядок:** Визначає, який член у многочлені є старшим `LT(f) = LC(f) · LM(f)`. У порядку grevlex моном `xᵃ yᵇ` переважає `xᶜ yᵈ`, якщо його повний степінь більший `a + b > c + d`, а за рівності степенів — якщо степінь `y` є меншим (`b < d`).
2. **Багатовимірна редукція:** Ділення многочлена `f` на набір `{g₁, …, gₛ}` шукає перший дільник `gᵢ`, чий старший моном `LM(gᵢ)` ділить поточний старший моном діленого `LM(f)`. Якщо такий дільник знайдено, виконується крок редукції `f ← f − (LT(f)/LT(gᵢ)) · gᵢ`. Якщо жоден `LM(gᵢ)` не ділить старший моном, він переноситься до остачі `r`, а процес продовжується для решти доданків.
3. **S-многочлени (Syzygy-polynomials):** Для усунення взаємних компенсацій старших членів для кожної пари `(gᵢ, gⱼ)` обчислюють:
```
S(gᵢ, gⱼ) = (LCM(LM(gᵢ), LM(gⱼ)) / LT(gᵢ)) · gᵢ − (LCM(LM(gᵢ), LM(gⱼ)) / LT(gⱼ)) · gⱼ
```
4. **Алгоритм Бухбергера:** Обчислює редукцію `S(gᵢ, gⱼ)` відносно поточного базису `G`. Якщо редукована остача `r ≠ 0`, вона додається до базису `G`, а нові пари многочленів ставляться в чергу перевірки.

:::tabs
```cpp
#include <iostream>
#include <vector>
#include <string>
#include <algorithm>

// Моном x^a * y^b
struct Monomial {
    int a{0}; // степінь x
    int b{0}; // степінь y

    int total_deg() const { return a + b; }

    // Graded reverse lexicographic (grevlex) order
    bool operator<(const Monomial& o) const {
        if (total_deg() != o.total_deg()) return total_deg() < o.total_deg();
        if (b != o.b) return b > o.b; // у grevlex менший степінь y виграє
        return a < o.a;
    }
    bool operator==(const Monomial& o) const { return a == o.a && b == o.b; }
};

Monomial lcm(const Monomial& m1, const Monomial& m2) {
    return {std::max(m1.a, m2.a), std::max(m1.b, m2.b)};
}

bool divides(const Monomial& div, const Monomial& target) {
    return div.a <= target.a && div.b <= target.b;
}

struct Term {
    Rational coeff;
    Monomial monom;
};

class Poly2D {
public:
    std::vector<Term> terms;

    void cleanup() {
        std::vector<Term> clean;
        for (const auto& t : terms) {
            if (!t.coeff.is_zero()) clean.push_back(t);
        }
        std::sort(clean.begin(), clean.end(), [](const Term& t1, const Term& t2) {
            return t2.monom < t1.monom; // за спаданням порядку
        });
        terms.clear();
        for (const auto& t : clean) {
            if (!terms.empty() && terms.back().monom == t.monom) {
                terms.back().coeff = terms.back().coeff + t.coeff;
                if (terms.back().coeff.is_zero()) terms.pop_back();
            } else {
                terms.push_back(t);
            }
        }
    }

    bool is_zero() const { return terms.empty(); }
    Term lt() const { return terms.empty() ? Term{Rational(0), {0, 0}} : terms[0]; }
};

// Редукція f відносно набору g_list
Poly2D reduce_poly(Poly2D f, const std::vector<Poly2D>& g_list) {
    f.cleanup();
    Poly2D rem;
    while (!f.is_zero()) {
        bool reduced = false;
        Term lt_f = f.lt();
        for (const auto& g : g_list) {
            Term lt_g = g.lt();
            if (divides(lt_g.monom, lt_f.monom)) {
                Rational factor = lt_f.coeff / lt_g.coeff;
                Monomial shift = {lt_f.monom.a - lt_g.monom.a, lt_f.monom.b - lt_g.monom.b};
                // Віднімаємо factor * shift * g
                for (const auto& gt : g.terms) {
                    f.terms.push_back({Rational(0) - (factor * gt.coeff),
                                      {gt.monom.a + shift.a, gt.monom.b + shift.b}});
                }
                f.cleanup();
                reduced = true;
                break;
            }
        }
        if (!reduced) {
            rem.terms.push_back(lt_f);
            f.terms.erase(f.terms.begin());
        }
    }
    rem.cleanup();
    return rem;
}

// Побудова S-многочлена для пари g1, g2
Poly2D s_polynomial(const Poly2D& g1, const Poly2D& g2) {
    Term lt1 = g1.lt();
    Term lt2 = g2.lt();
    Monomial L = lcm(lt1.monom, lt2.monom);

    Poly2D s;
    Monomial s1 = {L.a - lt1.monom.a, L.b - lt1.monom.b};
    Monomial s2 = {L.a - lt2.monom.a, L.b - lt2.monom.b};
    Rational c1 = Rational(1) / lt1.coeff;
    Rational c2 = Rational(1) / lt2.coeff;

    for (const auto& t : g1.terms) s.terms.push_back({t.coeff * c1, {t.monom.a + s1.a, t.monom.b + s1.b}});
    for (const auto& t : g2.terms) s.terms.push_back({Rational(0) - (t.coeff * c2), {t.monom.a + s2.a, t.monom.b + s2.b}});
    s.cleanup();
    return s;
}

// Алгоритм Бухбергера
std::vector<Poly2D> buchberger(std::vector<Poly2D> G) {
    for (auto& g : G) g.cleanup();
    std::vector<std::pair<size_t, size_t>> pairs;
    for (size_t i = 0; i < G.size(); ++i) {
        for (size_t j = i + 1; j < G.size(); ++j) pairs.emplace_back(i, j);
    }

    while (!pairs.empty()) {
        auto [i, j] = pairs.back();
        pairs.pop_back();

        Poly2D S = s_polynomial(G[i], G[j]);
        Poly2D rem = reduce_poly(S, G);

        if (!rem.is_zero()) {
            size_t new_idx = G.size();
            for (size_t k = 0; k < G.size(); ++k) pairs.emplace_back(k, new_idx);
            G.push_back(rem);
        }
    }
    return G;
}
```
```py
from fractions import Fraction

class Monomial:
    def __init__(self, a, b):
        self.a = a  # степінь x
        self.b = b  # степінь y

    def total_deg(self):
        return self.a + self.b

    def __lt__(self, other):
        if self.total_deg() != other.total_deg():
            return self.total_deg() < other.total_deg()
        if self.b != other.b:
            return self.b > other.b  # grevlex order
        return self.a < other.a

    def __eq__(self, other):
        return self.a == other.a and self.b == other.b


def lcm(m1: Monomial, m2: Monomial):
    return Monomial(max(m1.a, m2.a), max(m1.b, m2.b))


def divides(div: Monomial, target: Monomial):
    return div.a <= target.a and div.b <= target.b


class Poly2D:
    def __init__(self, terms=None):
        # terms: list of (Fraction, Monomial)
        self.terms = terms or []
        self.cleanup()

    def cleanup(self):
        d = {}
        for coeff, monom in self.terms:
            c = Fraction(coeff)
            key = (monom.a, monom.b)
            d[key] = d.get(key, Fraction(0)) + c
        clean = []
        for (a, b), c in d.items():
            if c != 0:
                clean.append((c, Monomial(a, b)))
        clean.sort(key=lambda t: t[1], reverse=True)
        self.terms = clean

    def is_zero(self):
        return len(self.terms) == 0

    def lt(self):
        return self.terms[0] if self.terms else (Fraction(0), Monomial(0, 0))


def reduce_poly(f: Poly2D, g_list: list):
    f_cur = Poly2D(list(f.terms))
    rem_terms = []
    while not f_cur.is_zero():
        c_f, m_f = f_cur.lt()
        reduced = False
        for g in g_list:
            c_g, m_g = g.lt()
            if divides(m_g, m_f):
                factor = c_f / c_g
                shift = Monomial(m_f.a - m_g.a, m_f.b - m_g.b)
                new_terms = list(f_cur.terms)
                for cg, mg in g.terms:
                    new_terms.append((-factor * cg, Monomial(mg.a + shift.a, mg.b + shift.b)))
                f_cur = Poly2D(new_terms)
                reduced = True
                break
        if not reduced:
            rem_terms.append((c_f, m_f))
            f_cur.terms.pop(0)
    return Poly2D(rem_terms)


def s_polynomial(g1: Poly2D, g2: Poly2D):
    c1, m1 = g1.lt()
    c2, m2 = g2.lt()
    L = lcm(m1, m2)
    s1 = Monomial(L.a - m1.a, L.b - m1.b)
    s2 = Monomial(L.a - m2.a, L.b - m2.b)

    terms = []
    for c, m in g1.terms:
        terms.append((c / c1, Monomial(m.a + s1.a, m.b + s1.b)))
    for c, m in g2.terms:
        terms.append((-c / c2, Monomial(m.a + s2.a, m.b + s2.b)))
    return Poly2D(terms)


def buchberger(G: list):
    G = [Poly2D(g.terms) for g in G]
    pairs = [(i, j) for i in range(len(G)) for j in range(i + 1, len(G))]
    while pairs:
        i, j = pairs.pop()
        S = s_polynomial(G[i], G[j])
        rem = reduce_poly(S, G)
        if not rem.is_zero():
            new_idx = len(G)
            for k in range(len(G)):
                pairs.append((k, new_idx))
            G.append(rem)
    return G
```
:::

---

### Покроковий числовий розбір: ручне простеження алгоритму Бухбергера

Щоб побачити роботу алгоритму Бухбергера зсередини, розберемо класичний приклад побудови базису Грьобнера в кільці `ℚ[x, y]` із градуйованим порядком `grevlex` (`x > y`).

Нехай вхідна система складається з двох многочленів:
```
f₁ = x² + y
f₂ = xy + 1
```

**Крок 1: Аналіз початкового набору G = {f₁, f₂}**
- Старші члени: `LT(f₁) = x²`, `LT(f₂) = xy`.
- Найменше спільне кратне старших мономів: `LCM(x², xy) = x²y`.

**Крок 2: Побудова першого S-многочлена**
Домножимо `f₁` на `y`, а `f₂` на `x`, щоб зрівняти їхні старші мономи:
```
S(f₁, f₂) = y · (x² + y) − x · (xy + 1) = (x²y + y²) − (x²y + x) = y² − x
```

**Крок 3: Редукція S(f₁, f₂) відносно G = {f₁, f₂}**
Старший член різниці: `LT(y² − x) = y²`.
Перевіримо дільники:
- `LT(f₁) = x²` не ділить `y²` (степінь `x` у дільника 2, у діленого 0);
- `LT(f₂) = xy` не ділить `y²` (степінь `x` у дільника 1, у діленого 0).
Оскільки жоден старший член не ділить `y²`, редукція неможлива. Остача `r = y² − x ≠ 0`.
Додаємо новий многочлен `f₃ = y² − x` до базису:
```
G = {f₁, f₂, f₃} = {x² + y, xy + 1, y² − x}
```

**Крок 4: Перевірка нових критичних пар**
Тепер необхідно перевірити дві нові пари: `(f₂, f₃)` та `(f₁, f₃)`.

*Пара (f₂, f₃):*
- `LT(f₂) = xy`, `LT(f₃) = y²`. `LCM(xy, y²) = xy²`.
- `S(f₂, f₃) = y · (xy + 1) − x · (y² − x) = (xy² + y) − (xy² − x²) = x² + y`.
- Редукція `x² + y` відносно `f₁ = x² + y`:
```
(x² + y) − 1 · (x² + y) = 0
```
Остача дорівнює нулю! Пара закрита.

*Пара (f₁, f₃):*
- `LT(f₁) = x²`, `LT(f₃) = y²`.
- Старші мономи `x²` та `y²` є **взаємно простими** (`НСД(x², y²) = 1`, спільних змінних немає). За першим критерієм Бухбергера такий S-многочлен завжди редукується в нуль безпосередньо через поліноми `f₁` та `f₃`, тому обчислювати редукцію вручну не потрібно.

Усі критичні пари перевірено, залишок скрізь нульовий. Остаточний базис Грьобнера:
```
G = {x² + y, xy + 1, y² − x}
```
Зверніть увагу: за допомогою `f₃ = y² − x` ми можемо виключити змінну `x = y²` і звести початкову нелінійну систему до одного рівняння `y³ + 1 = 0`.

---

### Практичні пастки та оптимізації

1. **Дробові коефіцієнти в цілочисловому кільці `ℤ[x]`:** Якщо алгоритм Евкліда викликати для многочленів із цілими коефіцієнтами без переходу до поля дробів `ℚ`, виникне помилка через відсутність точного ділення коефіцієнтів (наприклад, спроба відняти `(3/2) · x · g(x)`). Для кілець `ℤ[x]` застосовують псевдоділення або субрезультантний алгоритм Евкліда.
2. **Проблема вибуху проміжних коефіцієнтів (Coefficient explosion):** Під час виконання алгоритму Бухбергера чисельники й знаменники раціональних чисел можуть подвоювати кількість цифр на кожному кроці редукції. На практиці обов'язково застосовують критерій взаємної простоти старших мономів (якщо `LCM(LM(f), LM(g)) = LM(f) · LM(g)`, то S-многочлен завжди редукується в нуль і пару можна пропустити) та мінімізацію/редукцію результуючого базису Грьобнера.
3. **Редукований базис Грьобнера (Reduced Gröbner Basis):** Отриманий після алгоритму Бухбергера базис часто містить зайві або надлишкові многочлени. Щоб зробити базис канонічним і єдиним для даного ідеалу, виконують два завершальні кроки:
   - *Мінімізація:* видаляють кожен многочлен `gᵢ`, старший член якого `LT(gᵢ)` ділиться на старший член будь-якого іншого многочлена `LT(gⱼ)` з базису.
   - *Взаємна редукція:* кожен многочлен базису ділять з остачею на всі інші многочлени, замінюючи його на повну остачу, і нормалізують старший коефіцієнт до одиниці (`LC = 1`).
