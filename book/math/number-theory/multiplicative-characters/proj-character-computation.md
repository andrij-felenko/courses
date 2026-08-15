# ⚙️ Обчислення характерів Діріхле, сум Ґаусса та перевірка ортогональності

Цей практичний документ описує розробку алгоритмів для обчислення таблиць характерів Діріхле за простим модулем, побудови таблиць дискретного логарифмування, точного знаходження сум Ґаусса та чисельної перевірки матричних співвідношень ортогональності мовами C та C++.

## 1. Постановка задачі та алгоритмічний аналіз

У обчислювальній теорії чисел, аналітичному кодуванні та криптографії виникає постійна потреба працювати з таблицями характерів Діріхле та спектральних сум Ґаусса. Для довільного простого модуля `p` мультиплікативна група лишків `(Z/pZ)*` є циклічною групою порядку `φ(p) = p - 1`.

Згідно з теоремою про структуру циклічних груп, у групі `(Z/pZ)*` завжди існує принаймні один генератор — так званий **первісний корінь** `g`. Якщо такий генератор фіксовано, кожен ненульовий елемент `x ∈ (Z/pZ)*` єдиним чином подається у вигляді степеня генератора:

```
x ≡ g^k (mod p),   де k ∈ {0, 1, ..., p - 2}
```

Показник степеня `k = ind_g(x)` називається **дискретним логарифмом** (або індексом) елемента `x` за основою `g`.

За допомогою дискретного логарифмування обчислення будь-якого з `p - 1` характерів Діріхле `χ_m` (де индекс характеру `m` пробігає значення `{0, 1, ..., p - 2}`) зводиться до обчислення точок на одиничному колі у комплексній площині:

```
χ_m(x) = exp( 2·π·i · m · ind_g(x) / (p - 1) )   [якщо gcd(x, p) = 1]
χ_m(x) = 0                                       [якщо gcd(x, p) > 1]
```

Для обчислення **спектральної суми Ґаусса** `g(χ_m)` виконується дискретне перетворення Фур'є мультиплікативного характеру по всій адитивній групі поля:

```
g(χ_m) = ∑_{x=1}^{p-1} χ_m(x) · exp( 2·π·i · x / p )
```

**Перевірка ортогональності характерів:** Матриця характерів `H` розміру `(p-1) × (p-1)`, де елемент на перетині `m`-го рядка та `x`-го стовпчика дорівнює `χ_m(x)`, повинна задовольняти умову унітарності. Множення матриці `H` на її ермітово-спряжену матрицю `H*` має утворювати скалярну діагональну матрицю:

```
(1 / (p - 1)) · ∑_{x=1}^{p-1} χ_i(x) · χ̄_j(x) = δ_{ij}
```

де `δ_{ij} = 1` при `i = j` та `δ_{ij} = 0` при `i ≠ j`.

## 2. Детальний покроковий аналіз алгоритмічних кроків

Процес комп'ютерного обчислення характерів та спектральних сум складається з п'яти послідовних і чітко структурованих етапів:

1. **Факторизація порядку групи `p - 1`:** Знаходження всіх унікальних простих дільників числа `p - 1`. Це необхідно для швидкої перевірки кандидата на первісний корінь за критерієм `g^{(p-1)/q} ≢ 1 (mod p)`.
2. **Пошук найменшого первісного кореня `g`:** Послідовне тестування кандидатів `g = 2, 3, 4, ...`. Для кожного кандидата виконується швидке піднесення до степеня за модулем. Перший елемент, який задовольняє критерій для всіх дільників `q`, є шуканим генератором.
3. **Побудова індексної таблиці дискретного логарифмування `dlog`:** Створення масиву розміру `p`, у якому за індексом `x` зберігається значення `k = ind_g(x)`. Таблиця будується за один прохід за час `O(p)` шляхом послідовного множення `val = (val * g) % p`.
4. **Обчислення комплексних значений характеру:** Для заданих `m` та `x` зчитується значення `k = dlog[x]`, обчислюється кут `angle = 2·π·m·k / (p - 1)` і будується комплексне число `cos(angle) + i·sin(angle)`.
5. **Акумуляція суми Ґаусса:** Для кожного `x ∈ {1, 2, ..., p - 1}` обчислюється добуток комплексно значення характеру `χ_m(x)` та адитивної фази `exp(2·π·i·x / p)`. Отримані значення додаються до загальної комплексної суми.

## 3. Порівняльний архітектурний аналіз C та C++ реалізацій

При реалізації чисельних алгоритмів теорії чисел важливе значення має вибір мовних засобів та управління ресурсами:

- **Модель C:** Використовує процедурний підхід із ручним керуванням пам'яттю через `malloc` та `free`. Структура `CharacterContext` інкапсулює покажчик на масив дискретних логарифмів. Для обчислення тригонометричних фаз застосовуються функції `cos()` та `sin()` зі стандартної бібліотеки `<math.h>` у поєднанні з типом `double complex` із заголовка `<complex.h>`.
- **Модель C++:** Використовує суворий шаблон RAII (Resource Acquisition Is Initialization). Клас `DirichletCharacterSystem` гарантує автоматичне виділення та очищення пам'яті через `std::vector<int>`. Для комплексної арифметики застосовується шаблонний клас `std::complex<double>` та стандартна функція `std::polar()`. Замість ручної перевірки покажчиків використовуються винятки `std::invalid_argument`.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <complex.h>
#include <stdbool.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

// Швидке піднесення до степеня за модулем: (base^exp) % mod
static long long power_mod(long long base, long long exp, long long mod) {
    long long res = 1;
    base %= mod;
    while (exp > 0) {
        if (exp % 2 == 1) res = (res * base) % mod;
        base = (base * base) % mod;
        exp /= 2;
    }
    return res;
}

// Пошук найменшого первісного кореня mod p
static int find_primitive_root(int p) {
    if (p == 2) return 1;
    int phi = p - 1;
    int n = phi;
    int prime_factors[32];
    int num_factors = 0;

    // Факторизація числа phi = p - 1
    for (int i = 2; i * i <= n; i++) {
        if (n % i == 0) {
            prime_factors[num_factors++] = i;
            while (n % i == 0) n /= i;
        }
    }
    if (n > 1) prime_factors[num_factors++] = n;

    // Перевірка кандидатів на первісний корінь
    for (int g = 2; g < p; g++) {
        bool ok = true;
        for (int i = 0; i < num_factors; i++) {
            if (power_mod(g, phi / prime_factors[i], p) == 1) {
                ok = false;
                break;
            }
        }
        if (ok) return g;
    }
    return -1;
}

// Структура контексту характерів Діріхле
typedef struct {
    int p;
    int g;
    int *dlog; // dlog[x] = k таке, що g^k = x mod p
} CharacterContext;

// Ініціалізація та виділення пам'яті під контекст
CharacterContext* char_ctx_create(int p) {
    CharacterContext *ctx = (CharacterContext*)malloc(sizeof(CharacterContext));
    if (!ctx) return NULL;
    ctx->p = p;
    ctx->g = find_primitive_root(p);
    ctx->dlog = (int*)calloc(p, sizeof(int));
    if (!ctx->dlog) {
        free(ctx);
        return NULL;
    }

    // Побудова таблиці дискретного логарифмування за O(p)
    long long val = 1;
    for (int k = 0; k < p - 1; k++) {
        ctx->dlog[val] = k;
        val = (val * ctx->g) % p;
    }
    return ctx;
}

// Звільнення динамічної пам'яті
void char_ctx_free(CharacterContext *ctx) {
    if (ctx) {
        free(ctx->dlog);
        free(ctx);
    }
}

// Обчислення значення характера χ_m(n)
double complex eval_character(const CharacterContext *ctx, int m, int n) {
    if (n % ctx->p == 0) return 0.0 + 0.0 * I;
    int k = ctx->dlog[n % ctx->p];
    double angle = 2.0 * M_PI * m * k / (ctx->p - 1);
    return cos(angle) + sin(angle) * I;
}

// Обчислення суми Ґаусса g(χ_m)
double complex compute_gauss_sum(const CharacterContext *ctx, int m) {
    double complex sum = 0.0 + 0.0 * I;
    int p = ctx->p;
    for (int x = 1; x < p; x++) {
        double complex chi_val = eval_character(ctx, m, x);
        double add_angle = 2.0 * M_PI * x / p;
        double complex add_val = cos(add_angle) + sin(add_angle) * I;
        sum += chi_val * add_val;
    }
    return sum;
}

// Перевірка ортогональності характерів
bool check_orthogonality(const CharacterContext *ctx) {
    int phi = ctx->p - 1;
    double eps = 1e-7;
    for (int i = 0; i < phi; i++) {
        for (int j = 0; j < phi; j++) {
            double complex sum = 0.0 + 0.0 * I;
            for (int x = 1; x < ctx->p; x++) {
                double complex c1 = eval_character(ctx, i, x);
                double complex c2 = eval_character(ctx, j, x);
                sum += c1 * conj(c2);
            }
            double expected = (i == j) ? (double)phi : 0.0;
            if (cabs(sum - expected) > eps) return false;
        }
    }
    return true;
}

int main(void) {
    int p = 7;
    CharacterContext *ctx = char_ctx_create(p);
    if (!ctx) {
        fprintf(stderr, "Помилка виділення пам'яті\n");
        return 1;
    }

    printf("=== Модуль p = %d, Первісний корінь g = %d ===\n", ctx->p, ctx->g);

    printf("\nТаблиця характерів χ_m(x):\n");
    printf("m\\x ");
    for (int x = 1; x < p; x++) printf("   x=%d  ", x);
    printf("\n");

    for (int m = 0; m < p - 1; m++) {
        printf("χ_%d ", m);
        for (int x = 1; x < p; x++) {
            double complex val = eval_character(ctx, m, x);
            printf("%+.1f%+.1fi ", creal(val), cimag(val));
        }
        printf("\n");
    }

    printf("\nСуми Ґаусса та перевірка |g(χ)| = √%d:\n", p);
    for (int m = 0; m < p - 1; m++) {
        double complex g_sum = compute_gauss_sum(ctx, m);
        double mod = cabs(g_sum);
        printf("g(χ_%d) = %+.3f %+.3fi | |g| = %.4f (теоретично: %.4f)\n",
               m, creal(g_sum), cimag(g_sum), mod, sqrt((double)p));
    }

    bool orth_ok = check_orthogonality(ctx);
    printf("\nОртогональність матриці характерів: %s\n", orth_ok ? "ПРОЙДЕНО" : "ПОМИЛКА");

    char_ctx_free(ctx);
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <complex>
#include <cmath>
#include <numeric>
#include <stdexcept>
#include <numbers>
#include <iomanip>

class DirichletCharacterSystem {
public:
    explicit DirichletCharacterSystem(int p) : p_(p) {
        if (p <= 1) {
            throw std::invalid_argument("Modulus must be prime > 1");
        }
        g_ = find_primitive_root(p);
        dlog_.resize(p, 0);

        // Побудова таблиці дискретного логарифмування за O(p)
        long long val = 1;
        for (int k = 0; k < p - 1; ++k) {
            dlog_[val] = k;
            val = (val * g_) % p;
        }
    }

    [[nodiscard]] int modulus() const noexcept { return p_; }
    [[nodiscard]] int generator() const noexcept { return g_; }

    // Обчислення значення характера χ_m(n)
    [[nodiscard]] std::complex<double> eval(int m, int n) const noexcept {
        if (n % p_ == 0) return {0.0, 0.0};
        int k = dlog_[n % p_];
        double angle = 2.0 * std::numbers::pi * m * k / (p_ - 1);
        return std::polar(1.0, angle);
    }

    // Обчислення суми Ґаусса g(χ_m)
    [[nodiscard]] std::complex<double> gauss_sum(int m) const noexcept {
        std::complex<double> sum{0.0, 0.0};
        for (int x = 1; x < p_; ++x) {
            auto chi_val = eval(m, x);
            double add_angle = 2.0 * std::numbers::pi * x / p_;
            auto add_val = std::polar(1.0, add_angle);
            sum += chi_val * add_val;
        }
        return sum;
    }

    // Перевірка ортогональності характерів
    [[nodiscard]] bool verify_orthogonality() const noexcept {
        int phi = p_ - 1;
        constexpr double eps = 1e-7;
        for (int i = 0; i < phi; ++i) {
            for (int j = 0; j < phi; ++j) {
                std::complex<double> dot{0.0, 0.0};
                for (int x = 1; x < p_; ++x) {
                    dot += eval(i, x) * std::conj(eval(j, x));
                }
                double expected = (i == j) ? static_cast<double>(phi) : 0.0;
                if (std::abs(dot - expected) > eps) return false;
            }
        }
        return true;
    }

private:
    int p_;
    int g_;
    std::vector<int> dlog_;

    static long long power_mod(long long base, long long exp, long long mod) noexcept {
        long long res = 1;
        base %= mod;
        while (exp > 0) {
            if (exp % 2 == 1) res = (res * base) % mod;
            base = (base * base) % mod;
            exp /= 2;
        }
        return res;
    }

    static int find_primitive_root(int p) {
        if (p == 2) return 1;
        int phi = p - 1;
        int n = phi;
        std::vector<int> prime_factors;

        for (int i = 2; i * i <= n; ++i) {
            if (n % i == 0) {
                prime_factors.push_back(i);
                while (n % i == 0) n /= i;
            }
        }
        if (n > 1) prime_factors.push_back(n);

        for (int g = 2; g < p; ++g) {
            bool ok = true;
            for (int factor : prime_factors) {
                if (power_mod(g, phi / factor, p) == 1) {
                    ok = false;
                    break;
                }
            }
            if (ok) return g;
        }
        return -1;
    }
};

int main() {
    constexpr int p = 7;
    try {
        DirichletCharacterSystem sys(p);

        std::cout << "=== [C++] Модуль p = " << sys.modulus() 
                  << ", Первісний корінь g = " << sys.generator() << " ===\n\n";

        std::cout << "Суми Ґаусса та перевірка модулів |g(χ)|:\n";
        for (int m = 0; m < sys.modulus() - 1; ++m) {
            auto g_sum = sys.gauss_sum(m);
            double mod = std::abs(g_sum);
            std::cout << std::format("g(χ_{}) = {:+.3f} {:+.3fi} | |g| = {:.4f} (теоретично: {:.4f})\n",
                                     m, g_sum.real(), g_sum.imag(), mod, std::sqrt(p));
        }

        bool ok = sys.verify_orthogonality();
        std::cout << "\nОртогональність характерів: " << (ok ? "ПРОЙДЕНО" : "ПОМИЛКА") << "\n";
    } catch (const std::exception& e) {
        std::cerr << "Помилка виконання: " << e.what() << "\n";
        return 1;
    }

    return 0;
}
```
:::

## 4. Аналіз результатів виконання для модуля p = 7

При запуску програми для модуля `p = 7` та обчисленого первісного кореня `g = 3` ми отримуємо наступні чисельні результати:

1. **Дискретне логарифмування:**
   Степені генератора `3⁰ ≡ 1`, `3¹ ≡ 3`, `3² ≡ 2`, `3³ ≡ 6`, `3⁴ ≡ 4`, `3⁵ ≡ 5` задають відповідність індексів `dlog`:
   `dlog[1] = 0`, `dlog[3] = 1`, `dlog[2] = 2`, `dlog[6] = 3`, `dlog[4] = 4`, `dlog[5] = 5`.

2. **Суми Ґаусса та їхні модулі:**
   Теоретичне значення модуля нетривіальної суми Ґаусса для `p = 7` дорівнює `√7 ≈ 2.6458`.
   - Для головного характеру `χ₀`: сума Ґаусса дорівнює `g(χ₀) = -1.000 + 0.000i`, модуль `|g(χ₀)| = 1.0000` (оскільки `χ₀` не є привідним для всієї групи).
   - Для всіх нетривіальних характерів `χ₁ ... χ₅`: обчислені модулі дійсних комплексних сум точно дорівнюють `2.6458`, що з точністю до `10⁻⁷` збігається з теорією.

3. **Ортогональність:**
   Скалярний добуток кожного рядка матриці характерів на себе дає значення `φ(7) = 6.0000`, а скалярний добуток різних рядків дає точний нуль `0.0000 + 0.0000i`.

## 5. Практичний розбір пасток, обчислювальної складності та крайових випадків

### Пастка 1: Втрата точності комплексних чисел при підсумовуванні
При обчисленні сум Ґаусса для великих модулів `p` нагромадження помилок округлення чисел з плаваючою крапкою `double` може спотворити перевірку ортогональності. Застосування `std::polar` або стандартних функцій `cos` / `sin` вимагає суворого порогу порівняння `eps = 1e-7`. Не можна порівнювати плаваючі числа через прямолінійну рівність `==`.

### Пастка 2: Аргумент zero та вироди функцій
Характер Діріхле розширюється на всі цілі числа `Z`. Проте для чисел `n`, що діляться на `p` (`n ≡ 0 mod p`), значення характеру строго дорівнює нулю `χ(n) = 0`, а не `1` і не `exp(0)`. Нехтування перевіркою `n % p == 0` призводить до фатальних помилок при обчисленні L-функцій та сум по всьому полю `F_p`.

### Пастка 3: Дискретне логарифмування та межі застосовності
Прямий алгоритм побудови таблиці `dlog` методом послідовного піднесення до степеня задовольняє навчальні та дослідницькі модулі `p < 10⁶` (часова складність `O(p)`, просторова складність `O(p)`). 

Для криптографічних модулів `p > 2²⁵⁶` дискретне логарифмування стає обчислювально нездійсненним (проблема Discrete Logarithm Problem — DLP). У таких застосуваннях (наприклад, криптографічні протоколи на базі залишків) використовують виключно квадратичні або кубічні характери (символ Лежандра чи Якобі), які обчислюються за допомогою розширеного алгоритму Евкліда за час `O(log² p)` без знаходження дискретного логарифму.

### Швидкодія та спектральні оптимізації (FFT)
Обчислення сум Ґаусса для всіх характерів за прямим алгоритмом вимагає `O(p²)` операцій. Оскільки сума Ґаусса являє собою циклічну згортку на групі `(Z/pZ)*`, її можна обчислити для всіх характерів одночасно за час `O(p log p)` за допомогою Швидкого Перетворення Фур'є (FFT). Це є ключовою оптимізацією у сучасних алгоритмах факторизації та розпізнавання простих чисел (алгоритм Агравала-Каяла-Саксени AKS).
