# ⚙️ Алгоритми побудови та обчислення характерів Діріхле

Обчислювальний аналіз характерів Діріхле є ключовим інструментом у сучасній алгоритмічній теорії чисел, обчислювальні криптографії та цифровій обробці сигналів на скінченних алгебраїчних структурах. На відміну від аналітичних формул на папері, програмне втілення характерів вимагає точного поєднання дискретної алгебри, модульної арифметики великих чисел, чисельних комплексних обчислень та глибокого розуміння топологеми двоїстих груп.

У цій вставці розглядаються алгоритмічні принципи побудови повних таблиць характерів Діріхле за довільним модулем `q`, методи ідентифікації первісних характерів та обчислення провідника (conductor), а також надаються повні, готові до продакшену реалізації трьома мовами: C, C++ та Python.

## 1. Алгоритмічний дизайн та математичні етапи

Обчислення всієї системи характерів Діріхле для заданого натурального модуля `q` розбивається на п'ять послідовних алгоритмічних етапів.

### Етап 1. Генерація приведеної системи залишків

Першим кроком є побудова множини цілих чисел `G = (ℤ/qℤ)*`, взаємно простих з модулем `q` у проміжку від 1 до `q - 1`.
Для цього застосовується алгоритм Евкліда обчислення найбільшого спільного дільника `gcd(n, q)`:

```
n ∈ G ⟺ gcd(n, q) = 1,   де n ∈ {1, 2, ..., q - 1}
```

Кількість таких елементів точно дорівнює значенню функції Ейлера `|G| = φ(q)`. Усі знайдені елементи зберігаються у впорядкованому масиві `coprimes` довжини `φ(q)`.

### Етап 2. Розклад групи залишків на циклічні твірні

Структура групи `G = (ℤ/qℤ)*` визначає спосіб індексації характерів. Тут можливі два класи модулів:

1. **Циклічні модулі (`q = 2, 4, pᵏ, 2pᵏ` для непарних простих `p`):**
   Існує принаймні один первісний корінь `g`, який породжує всі елементи групи як послідовні степені: `G = {g⁰, g¹, g², ..., g^{φ(q)-1}}`.
   Пошук первісного кореня здійснюється перевіркою умови: `g^{φ(q) / p_i} ≢ 1 (mod q)` для кожного простого дільника `p_i` числа `φ(q)`.
   Після знаходження `g` будується таблиця дискретного логарифма (індексу) `ind_g(n)` за допомогою хеш-таблиці або масиву:

   ```
   n ≡ g^{ind_g(n)} (mod q)
   ```

2. **Нециклічні модулі (наприклад, `q = 2ᵏ` при `k ≥ 3` або складене `q` з кількома непарними простими дільниками):**
   За основною теоремою про скінченні абелеві групи, `G` розкладається у прямий добуток кількох циклічних підгруп `C_{d₁} × C_{d₂} × ... × C_{d_r}`.
   Наприклад, для `q = 2ᵏ` група породжується двома елементами: `-1` (порядок 2) та `5` (порядок `2ᵏ⁻²`). Довільне взаємно просте число `n` подається у вигляді `n ≡ (-1)ᵃ · 5ᵇ (mod 2ᵏ)`.
   Для складеного числа `q = a · b` з `gcd(a, b) = 1` застосовується Китайська теорема про залишки (CRT), а характер обчислюється як добуток фактор-характерів `χ(n) = χ_a(n mod a) · χ_b(n mod b)`.

### Етап 3. Обчислення комплексних значень характера

Кожен з `φ(q)` характерів замощується вектором індексів `k = (k₁, k₂, ..., k_r)`. Для циклічного випадку з генератором `g` значення `k`-го характера на елементі `n` із дискретним логарифмом `idx = ind_g(n)` обчислюється як комплексна експонента:

```
χₖ(n) = exp(2 π i · k · idx / φ(q)) = cos(2 π k idx / φ(q)) + i · sin(2 π k idx / φ(q))
```

Результатом є двовимірна матриця розміром `φ(q) × φ(q)`, де рядок `k` відповідає характеру `χₖ`, а стовпчик `i` відповідає елементу `coprimes[i]`.

### Етап 4. Визначення провідника (Conductor) та перевірка на первісність

Характер `χ (mod q)` індукується характером за дільником `d | q`, якщо значення `χ(n)` залежить лише від остачі `n (mod d)`.
Алгоритм визначення провідника перебирає всі дільники `d` числа `q` у зростаючому порядку. Дільник `d` є кандидатним провідником, якщо виконується умова:

```
Для всіх n ∈ G: якщо n ≡ 1 (mod d), то χ(n) = 1 + 0i
```

Найменший дільник `d`, для якого ця умова справджується з урахуванням похибки плаваючої коми `ε = 1e-6`, є **провідником** `cond(χ) = d`.
Якщо `cond(χ) = q`, характер позначається як **первісний** (primitive); якщо `cond(χ) < q` — як **індукований** (imprimitive).

### Етап 5. Верифікація співвідношень ортогональності

Для підтвердження коректності побудованої матриці здійснюється автоматична перевірка двох критеріїв:

1. **Перша ортогональність (за рядками):**
   ```
   ⟨χ_a, χ_b⟩ = ∑_{i=0}^{φ(q)-1} χ_a(n_i) · χ̄_b(n_i) = φ(q) · δ_{a,b}
   ```
2. **Друга ортогональність (за стовпчиками):**
   ```
   ∑_{k=0}^{φ(q)-1} χ_k(m) · χ̄_k(n) = φ(q) · δ_{m ≡ n (mod q)}
   ```

## 2. Повні програмні реалізації

Нижче наведено три незалежні, повністю працездатні реалізації алгоритму для системного програмування (C), об'єктно-орієнтованого аналізу (C++) та швидкого скриптування (Python).

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

#define PI 3.14159265358979323846

/* Структура для представлення комплексного числа */
typedef struct {
    double real;
    double imag;
} Complex;

Complex complex_make(double r, double i) {
    Complex c = {r, i};
    return c;
}

Complex complex_mul(Complex a, Complex b) {
    return complex_make(a.real * b.real - a.imag * b.imag,
                        a.real * b.imag + a.imag * b.real);
}

Complex complex_conj(Complex a) {
    return complex_make(a.real, -a.imag);
}

/* Алгоритм Евкліда для НСД */
int gcd(int a, int b) {
    while (b != 0) {
        int t = b;
        b = a % b;
        a = t;
    }
    return a;
}

/* Швидке бінарне піднесення до степеня за модулем */
int power_mod(int base, int exp, int mod) {
    int res = 1;
    base %= mod;
    while (exp > 0) {
        if (exp % 2 == 1) res = (res * base) % mod;
        base = (base * base) % mod;
        exp /= 2;
    }
    return res;
}

/* Пошук найменшого первісного кореня за модулем q */
int find_primitive_root(int q, int phi_q) {
    if (q == 2) return 1;
    for (int g = 2; g < q; ++g) {
        if (gcd(g, q) != 1) continue;
        bool ok = true;
        int dummy = phi_q;
        for (int p = 2; p * p <= dummy; ++p) {
            if (dummy % p == 0) {
                if (power_mod(g, phi_q / p, q) == 1) {
                    ok = false;
                    break;
                }
                while (dummy % p == 0) dummy /= p;
            }
        }
        if (dummy > 1 && ok) {
            if (power_mod(g, phi_q / dummy, q) == 1) ok = false;
        }
        if (ok) return g;
    }
    return -1;
}

/* Обчислення провідника (conductor) для характера */
int compute_conductor(int q, const int *coprimes, int phi_q, const Complex *char_vals) {
    for (int d = 1; d <= q; ++d) {
        if (q % d != 0) continue;
        bool is_conductor = true;
        for (int i = 0; i < phi_q; ++i) {
            int n = coprimes[i];
            if (n % d == 1 % d) {
                if (fabs(char_vals[i].real - 1.0) > 1e-6 || fabs(char_vals[i].imag) > 1e-6) {
                    is_conductor = false;
                    break;
                }
            }
        }
        if (is_conductor) return d;
    }
    return q;
}

int main(void) {
    int q = 5;
    int coprimes[5];
    int phi_q = 0;

    for (int i = 1; i < q; ++i) {
        if (gcd(i, q) == 1) {
            coprimes[phi_q++] = i;
        }
    }

    int g = find_primitive_root(q, phi_q);
    if (g == -1) {
        printf("Модуль q=%d не має єдиного первісного кореня.\n", q);
        return 1;
    }

    int *discrete_log = (int *)malloc(sizeof(int) * q);
    int curr = 1;
    for (int exp = 0; exp < phi_q; ++exp) {
        discrete_log[curr] = exp;
        curr = (curr * g) % q;
    }

    Complex **char_table = (Complex **)malloc(sizeof(Complex *) * phi_q);
    for (int k = 0; k < phi_q; ++k) {
        char_table[k] = (Complex *)malloc(sizeof(Complex) * phi_q);
        for (int i = 0; i < phi_q; ++i) {
            int n = coprimes[i];
            int idx = discrete_log[n];
            double angle = 2.0 * PI * k * idx / phi_q;
            char_table[k][i] = complex_make(cos(angle), sin(angle));
        }
    }

    printf("Таблиця характерів за модулем q = %d (g = %d):\n", q, g);
    for (int k = 0; k < phi_q; ++k) {
        int conductor = compute_conductor(q, coprimes, phi_q, char_table[k]);
        printf("χ_%d [провідник d=%d, %s]: ", k, conductor,
               (conductor == q) ? "первісний" : "індукований");
        for (int i = 0; i < phi_q; ++i) {
            printf("(%.2f, %.2f) ", char_table[k][i].real, char_table[k][i].imag);
        }
        printf("\n");
    }

    /* Перевірка ортогональності chi_1 та chi_2 */
    Complex sum = complex_make(0, 0);
    for (int i = 0; i < phi_q; ++i) {
        Complex term = complex_mul(char_table[1][i], complex_conj(char_table[2][i]));
        sum.real += term.real;
        sum.imag += term.imag;
    }
    printf("\nСкалярний добуток <χ_1, χ_2> = (%.2f, %.2f) [очікується (0.00, 0.00)]\n",
           sum.real, sum.imag);

    for (int k = 0; k < phi_q; ++k) free(char_table[k]);
    free(char_table);
    free(discrete_log);
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <complex>
#include <numeric>
#include <cmath>
#include <optional>
#include <iomanip>

class DirichletCharacterTable {
public:
    using Complex = std::complex<double>;

    explicit DirichletCharacterTable(int modulus) : q_(modulus) {
        build_coprimes();
        g_ = find_primitive_root();
        if (g_) {
            build_table_cyclic();
        }
    }

    [[nodiscard]] int modulus() const { return q_; }
    [[nodiscard]] int phi() const { return static_cast<int>(coprimes_.size()); }
    [[nodiscard]] const std::vector<int>& coprimes() const { return coprimes_; }

    [[nodiscard]] Complex eval(int char_idx, int n) const {
        int rem = ((n % q_) + q_) % q_;
        if (std::gcd(rem, q_) != 1) return {0.0, 0.0};
        auto it = std::find(coprimes_.begin(), coprimes_.end(), rem);
        size_t elem_idx = std::distance(coprimes_.begin(), it);
        return table_[char_idx][elem_idx];
    }

    [[nodiscard]] int compute_conductor(int char_idx) const {
        for (int d = 1; d <= q_; ++d) {
            if (q_ % d != 0) continue;
            bool is_cond = true;
            for (size_t i = 0; i < coprimes_.size(); ++i) {
                if (coprimes_[i] % d == 1 % d) {
                    if (std::abs(table_[char_idx][i] - Complex{1.0, 0.0}) > 1e-6) {
                        is_cond = false;
                        break;
                    }
                }
            }
            if (is_cond) return d;
        }
        return q_;
    }

    [[nodiscard]] Complex scalar_product(int char_a, int char_b) const {
        Complex sum{0.0, 0.0};
        for (size_t i = 0; i < coprimes_.size(); ++i) {
            sum += table_[char_a][i] * std::conj(table_[char_b][i]);
        }
        return sum;
    }

    void print_summary() const {
        std::cout << "Таблиця характерів (mod " << q_ << "), φ(q) = " << phi() << ":\n";
        for (int k = 0; k < phi(); ++k) {
            int cond = compute_conductor(k);
            std::cout << "χ_" << k << " [провідник d=" << cond << ", "
                      << (cond == q_ ? "первісний" : "індукований") << "]: ";
            for (size_t i = 0; i < coprimes_.size(); ++i) {
                std::cout << std::setw(6) << std::fixed << std::setprecision(2)
                          << table_[k][i] << " ";
            }
            std::cout << "\n";
        }
    }

private:
    int q_;
    std::vector<int> coprimes_;
    std::optional<int> g_;
    std::vector<std::vector<Complex>> table_;

    void build_coprimes() {
        for (int i = 1; i < q_; ++i) {
            if (std::gcd(i, q_) == 1) coprimes_.push_back(i);
        }
    }

    std::optional<int> find_primitive_root() {
        if (q_ == 2) return 1;
        int phi_val = phi();
        for (int g = 2; g < q_; ++g) {
            if (std::gcd(g, q_) != 1) continue;
            bool ok = true;
            int temp = phi_val;
            for (int p = 2; p * p <= temp; ++p) {
                if (temp % p == 0) {
                    if (power_mod(g, phi_val / p, q_) == 1) { ok = false; break; }
                    while (temp % p == 0) temp /= p;
                }
            }
            if (temp > 1 && ok && power_mod(g, phi_val / temp, q_) == 1) ok = false;
            if (ok) return g;
        }
        return std::nullopt;
    }

    static int power_mod(int base, int exp, int mod) {
        int res = 1;
        base %= mod;
        while (exp > 0) {
            if (exp % 2 == 1) res = (res * base) % mod;
            base = (base * base) % mod;
            exp /= 2;
        }
        return res;
    }

    void build_table_cyclic() {
        int phi_val = phi();
        std::vector<int> discrete_log(q_, 0);
        int curr = 1;
        for (int exp = 0; exp < phi_val; ++exp) {
            discrete_log[curr] = exp;
            curr = (curr * (*g_)) % q_;
        }

        constexpr double kPi = 3.14159265358979323846;
        table_.assign(phi_val, std::vector<Complex>(phi_val));
        for (int k = 0; k < phi_val; ++k) {
            for (size_t i = 0; i < coprimes_.size(); ++i) {
                int n = coprimes_[i];
                int idx = discrete_log[n];
                double angle = 2.0 * kPi * k * idx / phi_val;
                table_[k][i] = std::polar(1.0, angle);
            }
        }
    }
};

int main() {
    DirichletCharacterTable table(5);
    table.print_summary();

    auto prod = table.scalar_product(1, 2);
    std::cout << "\nПеревірка першої ортогональності <χ_1, χ_2> = " << prod << "\n";
    return 0;
}
```
```python
import cmath
import math

class DirichletCharacterTable:
    def __init__(self, q: int):
        self.q = q
        self.coprimes = [x for x in range(1, q) if math.gcd(x, q) == 1]
        self.phi = len(self.coprimes)
        self.g = self._find_primitive_root()
        self.table = self._build_table()

    def _power_mod(self, base: int, exp: int, mod: int) -> int:
        return pow(base, exp, mod)

    def _find_primitive_root(self):
        if self.q == 2:
            return 1
        phi_val = self.phi
        for g in range(2, self.q):
            if math.gcd(g, self.q) != 1:
                continue
            ok = True
            temp = phi_val
            p = 2
            while p * p <= temp:
                if temp % p == 0:
                    if self._power_mod(g, phi_val // p, self.q) == 1:
                        ok = False
                        break
                    while temp % p == 0:
                        temp //= p
                p += 1
            if temp > 1 and ok:
                if self._power_mod(g, phi_val // temp, self.q) == 1:
                    ok = False
            if ok:
                return g
        return None

    def _build_table(self):
        if not self.g:
            raise ValueError(f"Модуль q={self.q} не має єдиного первісного кореня.")
        discrete_log = {}
        curr = 1
        for exp in range(self.phi):
            discrete_log[curr] = exp
            curr = (curr * self.g) % self.q

        table = []
        for k in range(self.phi):
            row = []
            for n in self.coprimes:
                idx = discrete_log[n]
                angle = 2 * math.pi * k * idx / self.phi
                val = cmath.rect(1.0, angle)
                row.append(val)
            table.append(row)
        return table

    def compute_conductor(self, char_idx: int) -> int:
        row = self.table[char_idx]
        for d in range(1, self.q + 1):
            if self.q % d != 0:
                continue
            is_cond = True
            for i, n in enumerate(self.coprimes):
                if n % d == 1 % d:
                    if abs(row[i] - 1.0) > 1e-6:
                        is_cond = False
                        break
            if is_cond:
                return d
        return self.q

    def verify_orthogonality(self):
        print(f"\n--- Перевірка першої ортогональності (mod {self.q}) ---")
        for a in range(self.phi):
            for b in range(self.phi):
                dot = sum(self.table[a][i] * self.table[b][i].conjugate() for i in range(self.phi))
                expected = self.phi if a == b else 0
                assert abs(dot - expected) < 1e-5
        print("Перше співвідношення ортогональності підтверджено!")


if __name__ == "__main__":
    t = DirichletCharacterTable(5)
    for k in range(t.phi):
        d = t.compute_conductor(k)
        kind = "первісний" if d == t.q else "індукований"
        vals = [f"{z.real:.2f}+{z.imag:.2f}j" for z in t.table[k]]
        print(f"χ_{k} [d={d}, {kind}]: {vals}")
    t.verify_orthogonality()
```
:::

## 3. Детальний простежувальний розбір коду та життєвий цикл пам'яті

Щоб простежити роботу алгоритму у деталях, розглянемо виконання коду для модуля `q = 5`.

### 1. Простеження на прикладі `q = 5`

* **Пошук елементів приведеної системи залишків:**
  Функція `gcd(i, 5)` перевіряє числа `1, 2, 3, 4`. Усі чотири є взаємно простими з 5. Масив `coprimes` одержує значення `[1, 2, 3, 4]`, а `phi_q = 4`.

* **Знаходження первісного кореня:**
  Для `q = 5` функція `find_primitive_root` розкладає `phi_q = 4` на прості множники (єдиний дільник `p = 2`).
  Для кандидатного генератора `g = 2`: перевіряється умова `power_mod(2, 4/2, 5) = 2² mod 5 = 4 ≠ 1`. Умова виконується, отже `g = 2` є первісним коренем.

* **Побудова таблиці дискретного логарифма:**
  Цикл піднесення `g` до степенів будує послідовність остач:
  `2⁰ = 1` ⟹ `discrete_log[1] = 0`
  `2¹ = 2` ⟹ `discrete_log[2] = 1`
  `2² = 4` ⟹ `discrete_log[4] = 2`
  `2³ = 8 ≡ 3` ⟹ `discrete_log[3] = 3`

* **Заповнення матриці характерів:**
  Для кожного `k ∈ {0, 1, 2, 3}` та кожного `n ∈ {1, 2, 3, 4}` обчислюється кут `angle = 2 π k ind_g(n) / 4`.
  Наприклад, для `k = 2` (комплексний характер) та `n = 3` (`ind_g(3) = 3`):
  `angle = 2 π · 2 · 3 / 4 = 3 π`.
  `cos(3 π) = -1`, `sin(3 π) = 0`, отже `χ₂(3) = -1.0 + 0.0i`.

### 2. Життєвий цикл пам'яті у версії C

У C-реалізації використовується динамічне виділення пам'яті функціями `malloc`:
1. `discrete_log`: масив цілих чисел розміром `sizeof(int) * q` байт.
2. `char_table`: масив вказівників на рядки розміром `sizeof(Complex*) * phi_q`.
3. Кожен рядок `char_table[k]`: масив комплексних чисел розміром `sizeof(Complex) * phi_q`.

В кінці функції `main` проводиться послідовне звільнення пам'яті у зворотному порядку через `free(char_table[k])`, `free(char_table)` та `free(discrete_log)`. Це гарантує відсутність витоків пам'яті (memory leaks).

### 3. RAII та контейнери у C++

У C++ версії управління пам'яттю реалізовано за допомогою принципу RAII (Resource Acquisition Is Initialization) через контейнери `std::vector`:
* Матриця характерів `table_` зберігається як `std::vector<std::vector<Complex>>`.
* Пам'ять виділяється автоматично методом `assign` і звільняється у деструкторі при виході об'єкта `table` з області видимості.
* Для безпечної обробки відсутності первісного кореня функція `find_primitive_root` повертає тип `std::optional<int>`, що виключає використання магічних від'ємних індикаторів помилок.

## 4. Аналіз складності та обчислювальні пастки

При промисловому втіленні обчислення характерів слід враховувати такі три ключові фактори:

### 1. Асимптотична складність

Побудова всієї таблиці розміром `φ(q) × φ(q)` вимагає виконання `O(φ(q)²)` комплексних операцій множення та обчислення тригонометричних функцій `cos`/`sin`.
Знаходження дискретного логарифма методом прямого піднесення до степеня вимагає `O(φ(q))` кроків для циклічного модуля, а пошук первісного кореня — `O(q · log(q) · log(phi))` операцій.
Отже, сумарна часова складність побудови становить `O(q · log q + φ(q)²)`.

### 2. Чисельна стійкість плаваючої коми

Оскільки значення характерів обчислюються через стандартні бібліотечні функції `cos` та `sin` (або `std::polar` у C++), виникає накопичення похибок округлення чисел типу `double` (IEEE 754).
При перевірці умови первісності `χ(n) = 1` пряме порівняння `real == 1.0 && imag == 0.0` призведе до помилок на більшості модулів. Необхідно застосовувати допуск `std::abs(val - 1.0) < 1e-6`.

Для криптографічних застосувань із великими модулями `q` обчислення проводять не у комплексному полі `ℂ`, а у скінченному розширенні поля `𝔽_p` або кільці залишків за модулем достатньо великого простого числа, де корені з одиниці обчислюються точно без втрати розрядів.

### 3. Оптимізація пам'яті та симетрії

Для великих модулів зберігання всієї матриці потребує `8 · φ(q)²` байт пам'яті. Використання властивостей симетрії дає змогу зменшити обсяг пам'яті в 4 рази:
* Значення `χ(-n) = χ(-1) · χ(n)` відновлюється за парністю характера.
* Значення спряженого характера `χ̄_k(n)` відновлюється безпосередньо з `χ_k(n)` зміною знака уявної частини.
* Для складних модулів таблиця зберігається у вигляді ранг-1 факторів відповідно до компонентного розкладу CRT.
