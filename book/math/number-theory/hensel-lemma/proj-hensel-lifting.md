# ⚙️ Реалізація підйому Гензеля: корені та факторизація

Ця практична вставка містить готові до використання реалізації лінійного та квадратичного підйому Гензеля для пошуку коренів многочленів за модулем `pᵏ`, а також для підйому розкладу многочленів на множники. Вона розкриває архітектурні особливості обчислення модульних коренів, аналіз обчислювальної складності та інженерні рішення для уникнення переповнення типів даних.

## 1. Архітектурні принципи та вибір типів даних

Реалізація модульного підйому Гензеля вимагає суворого дотримання трьох інженерних вимог:

1. **Захист від від'ємних остач:** У мовах програмування C та C++ оператор `%` реалізує усічене ділення (*truncated division*), при якому остача від ділення від'ємного числа залишається від'ємною (наприклад, `-7 % 3 = -1`, а не `2`). Оскільки модульна арифметика працює виключно в невід'ємному кільці лишків `Z/nZ`, будь-який результат операції `%` має додатково коригуватися за допомогою виразу `(x % mod + mod) % mod`.
2. **Захист від цілочисельного переповнення:** Підйом кореня за модулем `pᵏ` вимагає обчислення значень `pᵏ` та `p^{k+1}`. Для `p = 3` та `k = 5` значення `3⁵ = 243` легко вміщується в тип `int`. Однак для `p = 2` та `k = 64` значення `2⁶⁴` виходить за межі діапазону знакових 64-бітних цілих чисел (`int64_t`). У практичних алгоритмах слід застосовувати тип `uint64_t` або розширений 128-бітний тип `__int128_t` компіляторів GCC/Clang.
3. **Обчислення похідної та схем Горнера:** Для мінімізації кількості операцій множення при обчисленні многочлена `f(x)` та його похідної `f'(x)` застосовується схема Горнера. Це зменшує кількість множень з `O(deg²)` до `O(deg)` на кожну оцінку.

## 2. Алгоритм лінійного та квадратичного підйому коренів

Вхідні дані для підйому кореня:
- Многочлен `f(x) = c_n·xⁿ + ... + c₀` з цілими коефіцієнтами;
- Просте число `p`;
- Початковий корінь `a₁`, такий що `f(a₁) ≡ 0 (mod p)` та `f'(a₁) ≢ 0 (mod p)`;
- Цільовий показник степеня `k`.

Вихідні дані:
- Унікальний корінь `a_k (mod pᵏ)`.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>

/* Обчислення модульного оберненого елемента за розширеним алгоритмом Евкліда */
static int64_t mod_inverse(int64_t a, int64_t m) {
    int64_t m0 = m;
    int64_t y = 0, x = 1;
    if (m == 1) return 0;
    
    a = (a % m + m) % m;
    while (a > 1) {
        int64_t q = a / m;
        int64_t t = m;
        m = a % m;
        a = t;
        t = y;
        y = x - q * y;
        x = t;
    }
    if (x < 0) x += m0;
    return x;
}

/* Обчислення значення багаточлена f(x) за допомогою схеми Горнера */
static int64_t eval_poly(const int64_t* poly, size_t deg, int64_t x, int64_t mod) {
    int64_t result = 0;
    for (ssize_t i = (ssize_t)deg; i >= 0; --i) {
        result = (result * x + poly[i]) % mod;
        if (result < 0) result += mod;
    }
    return result;
}

/* Обчислення значення похідної f'(x) за допомогою схеми Горнера */
static int64_t eval_derivative(const int64_t* poly, size_t deg, int64_t x, int64_t mod) {
    if (deg == 0) return 0;
    int64_t result = 0;
    for (ssize_t i = (ssize_t)deg; i >= 1; --i) {
        int64_t coeff = (poly[i] * i) % mod;
        result = (result * x + coeff) % mod;
        if (result < 0) result += mod;
    }
    return result;
}

/* Лінійний підйом Гензеля: збільшує степінь модулю на 1 на кожному кроці */
bool hensel_lift_linear(const int64_t* poly, size_t deg, int64_t p, int target_k, int64_t r1, int64_t* out_root) {
    int64_t current_root = r1 % p;
    if (current_root < 0) current_root += p;

    /* Перевірка умови звичайного підйому */
    int64_t f_prime = eval_derivative(poly, deg, current_root, p);
    if (f_prime % p == 0) {
        fprintf(stderr, "Error: f'(r1) = 0 (mod p). Root is singular.\n");
        return false;
    }

    int64_t p_pow = p;
    for (int step = 1; step < target_k; ++step) {
        /* Обчислюємо q = f(current_root) / p_pow */
        int64_t p_next = p_pow * p;
        int64_t f_val = eval_poly(poly, deg, current_root, p_next);
        int64_t q = f_val / p_pow;

        /* Знаходимо обернену похідну за модулем p */
        int64_t v = mod_inverse(f_prime, p);
        int64_t t = (-q * v) % p;
        if (t < 0) t += p;

        current_root = current_root + t * p_pow;
        p_pow = p_next;
    }

    *out_root = current_root;
    return true;
}

int main(void) {
    /* Приклад: f(x) = x^2 - 7 = 0 (mod 3^5) */
    int64_t poly[3] = {-7, 0, 1}; /* -7 + 0*x + 1*x^2 */
    size_t deg = 2;
    int64_t p = 3;
    int target_k = 5; /* 3^5 = 243 */
    int64_t root1 = 1; /* f(1) = -6 = 0 (mod 3) */

    int64_t lifted_root = 0;
    if (hensel_lift_linear(poly, deg, p, target_k, root1, &lifted_root)) {
        printf("Root mod %ld^%d (%ld): %ld\n", p, target_k, (long)(243), (long)lifted_root);
        int64_t check = eval_poly(poly, deg, lifted_root, 243);
        printf("Verification f(%ld) mod 243 = %ld\n", (long)lifted_root, (long)check);
    }
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <optional>
#include <numeric>
#include <cstdint>
#include <stdexcept>

class HenselSolver {
public:
    static std::int64_t mod_inverse(std::int64_t a, std::int64_t m) {
        std::int64_t m0 = m, y = 0, x = 1;
        if (m == 1) return 0;
        a = (a % m + m) % m;
        while (a > 1) {
            std::int64_t q = a / m;
            std::int64_t t = m;
            m = a % m; a = t;
            t = y;
            y = x - q * y;
            x = t;
        }
        return (x < 0) ? x + m0 : x;
    }

    /* Оцінка значення многочлена за допомогою схеми Горнера */
    static std::int64_t eval_poly(const std::vector<std::int64_t>& poly, std::int64_t x, std::int64_t mod) {
        std::int64_t res = 0;
        for (auto it = poly.rbegin(); it != poly.rend(); ++it) {
            res = (res * x + *it) % mod;
            if (res < 0) res += mod;
        }
        return res;
    }

    /* Оцінка значення похідної за допомогою схеми Горнера */
    static std::int64_t eval_derivative(const std::vector<std::int64_t>& poly, std::int64_t x, std::int64_t mod) {
        if (poly.size() <= 1) return 0;
        std::int64_t res = 0;
        for (std::size_t i = poly.size() - 1; i >= 1; --i) {
            std::int64_t coeff = (poly[i] * static_cast<std::int64_t>(i)) % mod;
            res = (res * x + coeff) % mod;
            if (res < 0) res += mod;
        }
        return res;
    }

    /* Квадратичний підйом Гензеля (подвоєння степеня p на кожному кроці) */
    static std::optional<std::int64_t> lift_quadratic(
        const std::vector<std::int64_t>& poly,
        std::int64_t p,
        std::size_t target_k,
        std::int64_t initial_root) 
    {
        std::int64_t root = (initial_root % p + p) % p;
        std::int64_t f_prime = eval_derivative(poly, root, p);
        if (f_prime % p == 0) {
            return std::nullopt; /* Особливий корінь */
        }

        std::int64_t current_mod = p;
        while (current_mod < power(p, target_k)) {
            std::int64_t next_mod = current_mod * current_mod;
            std::int64_t f_val = eval_poly(poly, root, next_mod);
            std::int64_t df_val = eval_derivative(poly, root, next_mod);
            
            std::int64_t inv_df = mod_inverse(df_val, next_mod);
            std::int64_t correction = (f_val * inv_df) % next_mod;
            root = (root - correction + next_mod) % next_mod;
            
            current_mod = next_mod;
        }

        std::int64_t target_mod = power(p, target_k);
        return (root % target_mod + target_mod) % target_mod;
    }

private:
    static std::int64_t power(std::int64_t base, std::size_t exp) {
        std::int64_t res = 1;
        for (std::size_t i = 0; i < exp; ++i) res *= base;
        return res;
    }
};

int main() {
    /* Рівняння x^2 - 7 = 0 (mod 3^5) */
    std::vector<std::int64_t> poly = {-7, 0, 1};
    std::int64_t p = 3;
    std::size_t target_k = 5;
    std::int64_t r1 = 1;

    auto result = HenselSolver::lift_quadratic(poly, p, target_k, r1);
    if (result.has_value()) {
        std::cout << "Kvadratychnyy pidyom mod 3^5 (243): " << result.value() << "\n";
        std::int64_t check = HenselSolver::eval_poly(poly, result.value(), 243);
        std::cout << "Perevirka f(root) mod 243 = " << check << "\n";
    } else {
        std::cout << "Pidyom nemozhlyvyy (osoblyvyy korin)\n";
    }

    return 0;
}
```
:::

## 3. Детальний аналіз алгоритмічних функцій

### Функція `mod_inverse`

Функція обчислює мультиплікативний обернений елемент `a⁻¹ (mod m)` за допомогою розширеного алгоритму Евкліда. Алгоритм знаходить такі цілі коефіцієнти Безу `x` та `y`, що `a · x + m · y = gcd(a, m) = 1`.

Складність цієї операції становить `O(log(m))` кроків ділення. Якщо `gcd(a, m) != 1`, оберненого елемента не існує, і алгоритм повертає помилку.

### Функція `eval_poly` (Схема Горнера)

Замість прямого обчислення степенів `xᵏ`, який вимагав би `O(deg²)` множень, схема Горнера виражає багаточлен у формі вкладених дужок:

```
f(x) = c₀ + x·(c₁ + x·(c₂ + ... + x·(c_{n-1} + x·c_n)...))
```

Обчислення проводиться за циклом у зворотному напрямку від `c_n` до `c₀`. На кожному кроці виконується одна операція множення та одна операція додавання з негайною приведеною остачею за модулем `mod`. Це гарантує складову асимптотичну складність `O(deg)` та захищає від проміжних переповнень.

### Порівняння лінійного та квадратичного підйомів

1. **Лінійний підйом (`hensel_lift_linear`):**
   - На кожному кроці степінь модулю збільшується на 1: `p¹ → p² → p³ → ... → pᵏ`.
   - Потрібно `k - 1` ітерацій.
   - Складність становить `O(k · deg)` операцій.
   - Плюсом є обчислення оберненого елемента `(f'(a₁))⁻¹` лише **один раз** за малим модулем `p`.

2. **Квадратичний підйом (`lift_quadratic`):**
   - На кожному кроці степінь модулю подвоюється: `p¹ → p² → p⁴ → p⁸ → ... → p^{2ᵐ}`.
   - Потрібно лише `log₂(k)` ітерацій.
   - Складність становить `O(log(k) · deg)` великих модульних операцій.
   - Для великих степенів `k > 100` квадратичний підйом працює в сотні разів швидше за лінійний.

## 4. Алгоритм підйому факторизації многочленів

Окрім пошуку коренів, в інженерних застосуваннях та комп'ютерній алгебрі (CAS) фундаментальне значення має підйом розкладу многочленів на множники.

Якщо вхідний багаточлен `f(x) ∈ Z[x]` за малим простоим модулем `p` розкладено на два взаємно прості множники `f(x) ≡ g₁(x) · h₁(x) (mod p)`, алгоритм підйому факторів обчислює послідовність многочленів `g_k(x)` та `h_k(x)` за модулем `pᵏ`.

### Структура кроку підйому факторизації:

1. **Обчислення лишку неузгодженості:** Обчислюється многочлен `m_k(x) = (f(x) - g_k(x) · h_k(x)) / pᵏ (mod p)`.
2. **Розв'язання поліноміального рівняння Безу:** За допомогою розширеного алгоритму Евкліда для многочленів у полі `F_p[x]` знаходяться багаточлени `u(x)` та `v(x)`, що задовольняють `g_k · v + h_k · u ≡ m_k (mod p)` при умові `deg(u) < deg(g₁)` та `deg(v) < deg(h₁)`.
3. **Оновлення множників:** Повертаються підняті множники `g_{k+1}(x) = g_k(x) + u(x) · pᵏ` та `h_{k+1}(x) = h_k(x) + v(x) · pᵏ`.

Завдяки цьому підходу складність факторизації багаточленів великих степенів у `Z[x]` зменшується з експоненціальної до поліноміальної.

## 5. Профілювання, пам'ять та оптимізація продуктивності

Для високоефективного виконання алгоритму Гензеля в обчислювальних ядрах (криптографічні прискорювачі, алгебраїчні процесори) важливу роль відіграють наступні інженерні рішення:

1. **Локальність кеш-пам'яті (Cache Locality):** Масиви коефіцієнтів многочленів у мові C мають зберігатися в безперервному блоці пам'яті (наприклад, у векторному масиві `int64_t[]`). Це гарантує послідовне завантаження коефіцієнтів у L1-кеш процесора під час виконання циклів схеми Горнера.
2. **Уникнення динамічного виділення пам'яті (`std::vector` проти масивів на стеку):** Для многочленів невеликого степеня (наприклад, `deg ≤ 16`) виділення динамічної пам'яті через `new` або `std::vector` створює суттєві накладні витрати на роботу з кучею (*heap*). У C++ доцільно використовувати `std::array<std::int64_t, N>` або локальний стек.
3. **Передбачення розгалужень (Branch Prediction):** Цикли схеми Горнера мають фіксовану кількість ітерацій, що дорівнює ступеню багаточлена `deg`. Передбачувач розгалужень сучасних процесорів (Branch Target Buffer) передбачає ці переходи зі точністю до 99%, уникаючи скидання конвеєра інструкцій (*pipeline flush*).

## 6. Помилки реалізації та крайові випадки

При практичному розробленні алгоритмів підйому Гензеля розробники найчастіше стикаються з трьома категоріями помилок:

1. **Переповнення типів при обчисленні `pᵏ`**: При `p = 2` та `k = 64` значення `pᵏ` виходить за межі `uint64_t`. Необхідно використовувати відповідну бібліотеку довгої арифметики (GMP чи `__int128_t`) при великих покажчиках.
2. **Від'ємне значення остачі від ділення у C/C++**: Оператор `%` у мовах C/C++ повертає від'ємне значення, якщо ділене від'ємне (наприклад `-6 % 9 = -6`). Завжди коригуйте результат до позитивного діапазону: `(x % mod + mod) % mod`.
3. **Особливі корені (`f'(a) ≡ 0 (mod p)`)**: Для таких коренів звичайний алгоритм повертає помилку або ділить на нуль. Необхідно реалізовувати узагальнену лему Гензеля з обчисленням p-адичного нормування похідної `v_p(f'(a))`.
