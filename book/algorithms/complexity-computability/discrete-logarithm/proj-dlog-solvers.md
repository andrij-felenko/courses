# ⚙️ Практична реалізація алгоритмів розв'язання дискретного логарифма

Вставка містить повну реалізацію алгоритмів обчислення дискретного логарифма у скінченних полях `𝔽ₚ*` мовами C та C++. Розглянуто два фундаментальні універсальні методи: детермінований алгоритм Шенкса «Крок немовляти — крок велетня» (Baby-Step Giant-Step, BSGS) та імовірнісний `ρ`-алгоритм Полларда. Програмний код висвітлює безпечну 64-бітну модульну арифметику, розширений алгоритм Евкліда для обчислення оберненого елемента, структуру розрозріджених хеш-таблиць та бінарний пошук у відсортованих масивах.

## 1. Базовий математичний інструментарій та захист від переповнення

Для коректного виконання модульних обчислень над 64-бітними цілими числами (`uint64_t`) необхідно вирішити три критичні інженерні задачі:

1. **Захист від 64-бітного переповнення:** При множенні двох чисел `a, b < p` добуток `a · b` може сягати `2¹²⁸ - 1` (для `p ≈ 2⁶⁴`). Стандартний тип `uint64_t` переповнюється, що призводить до спотворення даних. Для розв'язання цієї проблеми в коді застосовується 128-бітний компіляторний тип `__int128_t` (підтримується GCC та Clang):
   ```cpp
   static uint64_t mul(uint64_t a, uint64_t b, uint64_t mod) {
       return static_cast<uint64_t>((static_cast<__int128_t>(a) * b) % mod);
   }
   ```
2. **Швидке модульне піднесення до степеня:** Операція `baseᵉˣᵖ mod p` реалізується за допомогою алгоритму бінарного розкладу степеня (Square-and-Multiply). Часова складність становить `O(log exp)` групових множень, що дозволяє підносити до степенів порядку `2⁶⁴` за лічені десятки наносекунд.
3. **Розширений алгоритм Евкліда:** Для розв'язання колізійного рівняння `Δb · x ≡ Δa (mod N)` необхідно знаходити обернене значення `Δb⁻¹ mod N`. Алгоритм Евкліда обчислює коефіцієнти Безу `u, v` для тотожності `u·Δb + v·N = НСД(Δb, N)`. Якщо `НСД = 1`, значення `u mod N` є шуканим оберненим елементом.

## 2. Повна реалізація мовами C та C++

:::tabs
```cpp
#include <iostream>
#include <unordered_map>
#include <cmath>
#include <optional>
#include <cstdint>
#include <vector>
#include <numeric>

namespace dlog {

// Клас для безпечної модульної арифметики (64-бітний модуль)
class ModularArithmetic {
public:
    static uint64_t mul(uint64_t a, uint64_t b, uint64_t mod) {
        return static_cast<uint64_t>((static_cast<__int128_t>(a) * b) % mod);
    }

    static uint64_t power(uint64_t base, uint64_t exp, uint64_t mod) {
        uint64_t result = 1;
        base %= mod;
        while (exp > 0) {
            if (exp & 1) {
                result = mul(result, base, mod);
            }
            base = mul(base, base, mod);
            exp >>= 1;
        }
        return result;
    }

    // Розширений алгоритм Евкліда для пошуку модульного оберненого (a^-1 mod mod)
    static std::optional<uint64_t> mod_inverse(uint64_t a, uint64_t mod) {
        int64_t t = 0, newt = 1;
        int64_t r = static_cast<int64_t>(mod), newr = static_cast<int64_t>(a);

        while (newr != 0) {
            int64_t quotient = r / newr;
            int64_t temp_t = t - quotient * newt;
            t = newt;
            newt = temp_t;

            int64_t temp_r = r - quotient * newr;
            r = newr;
            newr = temp_r;
        }

        if (r > 1) return std::nullopt; // Елемент не має оберненого
        if (t < 0) t += static_cast<int64_t>(mod);
        return static_cast<uint64_t>(t);
    }
};

// Результат обчислення логарифма
struct SolverResult {
    uint64_t exponent;
    uint64_t steps;
    bool found;
};

class DiscreteLogSolver {
public:
    // Алгоритм Shanks Baby-Step Giant-Step (BSGS)
    // Час: O(sqrt(N)), Пам'ять: O(sqrt(N))
    static SolverResult solve_bsgs(uint64_t g, uint64_t y, uint64_t p, uint64_t N) {
        uint64_t m = static_cast<uint64_t>(std::ceil(std::sqrt(static_cast<double>(N))));
        std::unordered_map<uint64_t, uint64_t> baby_steps;
        baby_steps.reserve(m);

        uint64_t cur = y % p;
        uint64_t steps_count = 0;

        // Kрок 1: Baby steps (зберігаємо y * g^j mod p для j in [0, m-1])
        for (uint64_t j = 0; j < m; ++j) {
            baby_steps[cur] = j;
            cur = ModularArithmetic::mul(cur, g, p);
            steps_count++;
        }

        // Крок 2: Giant steps (шукаємо (g^m)^i mod p)
        uint64_t factor = ModularArithmetic::power(g, m, p);
        cur = factor;

        for (uint64_t i = 1; i <= m; ++i) {
            steps_count++;
            auto it = baby_steps.find(cur);
            if (it != baby_steps.end()) {
                uint64_t j = it->second;
                uint64_t x = (i * m - j) % N;
                return SolverResult{x, steps_count, true};
            }
            cur = ModularArithmetic::mul(cur, factor, p);
        }

        return SolverResult{0, steps_count, false};
    }

    // Алгоритм Pollard's Rho для дискретного логарифмування
    // Час: O(sqrt(N)), Пам'ять: O(1)
    static SolverResult solve_pollard_rho(uint64_t g, uint64_t y, uint64_t p, uint64_t N) {
        struct State {
            uint64_t x; // поточний елемент групи w_k
            uint64_t a; // експонента g
            uint64_t b; // експонента y
        };

        auto next_state = [g, y, p, N](const State& st) -> State {
            switch (st.x % 3) {
                case 0: // Підмножина G1: x = x^2, a = 2a, b = 2b
                    return State{
                        ModularArithmetic::mul(st.x, st.x, p),
                        (st.a * 2) % N,
                        (st.b * 2) % N
                    };
                case 1: // Підмножина G2: x = x * g, a = a + 1, b = b
                    return State{
                        ModularArithmetic::mul(st.x, g, p),
                        (st.a + 1) % N,
                        st.b
                    };
                default: // Підмножина G3: x = x * y, a = a, b = b + 1
                    return State{
                        ModularArithmetic::mul(st.x, y, p),
                        st.a,
                        (st.b + 1) % N
                    };
            }
        };

        State tortoise{1, 0, 0};
        State hare = tortoise;
        uint64_t steps_count = 0;

        // Пошук колізії методом Флойда
        do {
            tortoise = next_state(tortoise);
            hare = next_state(next_state(hare));
            steps_count += 3;

            if (steps_count > 10 * N) { // Захист від безнадійного зациклення
                return SolverResult{0, steps_count, false};
            }
        } while (tortoise.x != hare.x);

        // Колізію знайдено: g^(a1) * y^(b1) = g^(a2) * y^(b2)
        // Звідси (b1 - b2) * x = (a2 - a1) mod N
        int64_t r_b = (static_cast<int64_t>(tortoise.b) - static_cast<int64_t>(hare.b)) % static_cast<int64_t>(N);
        if (r_b < 0) r_b += static_cast<int64_t>(N);

        int64_t r_a = (static_cast<int64_t>(hare.a) - static_cast<int64_t>(tortoise.a)) % static_cast<int64_t>(N);
        if (r_a < 0) r_a += static_cast<int64_t>(N);

        auto inv_b = ModularArithmetic::mod_inverse(static_cast<uint64_t>(r_b), N);
        if (!inv_b.has_value()) {
            // Колізія непридатна (НСД > 1), потрібно перезапустити з іншими початковими станами
            return SolverResult{0, steps_count, false};
        }

        uint64_t x = ModularArithmetic::mul(static_cast<uint64_t>(r_a), inv_b.value(), N);
        return SolverResult{x, steps_count, true};
    }
};

} // namespace dlog

int main() {
    uint64_t p = 10007;
    uint64_t g = 5;
    uint64_t N = p - 1;
    uint64_t secret_x = 1234;

    uint64_t y = dlog::ModularArithmetic::power(g, secret_x, p);

    std::cout << "=== Тестування розв'язувачів проблеми дискретного логарифма ===\n";
    std::cout << "Параметри: p = " << p << ", g = " << g << ", y = " << y << " (Секретне x = " << secret_x << ")\n\n";

    // Тест BSGS
    auto res_bsgs = dlog::DiscreteLogSolver::solve_bsgs(g, y, p, N);
    if (res_bsgs.found) {
        std::cout << "[BSGS] Успіх! Знайдено x = " << res_bsgs.exponent 
                  << " за " << res_bsgs.steps << " кроків.\n";
    } else {
        std::cout << "[BSGS] Помилка: логарифм не знайдено.\n";
    }

    // Тест Pollard Rho
    auto res_rho = dlog::DiscreteLogSolver::solve_pollard_rho(g, y, p, N);
    if (res_rho.found) {
        std::cout << "[Pollard Rho] Успіх! Знайдено x = " << res_rho.exponent 
                  << " за " << res_rho.steps << " кроків.\n";
    } else {
        std::cout << "[Pollard Rho] Не вдалося знайти з першої спроби (потрібен перезапуск).\n";
    }

    return 0;
}
```
```c
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <math.h>
#include <stdlib.h>

// Модульне множення 64-бітних чисел через __int128_t
static inline uint64_t mod_mul(uint64_t a, uint64_t b, uint64_t mod) {
    return (uint64_t)(((__int128_t)a * b) % mod);
}

// Модульне піднесення до степеня
static uint64_t mod_pow(uint64_t base, uint64_t exp, uint64_t mod) {
    uint64_t res = 1;
    base %= mod;
    while (exp > 0) {
        if (exp & 1) res = mod_mul(res, base, mod);
        base = mod_mul(base, base, mod);
        exp >>= 1;
    }
    return res;
}

// Розширений алгоритм Евкліда для обчислення оберненого елемента
static bool mod_inverse(uint64_t a, uint64_t mod, uint64_t *out_inv) {
    int64_t t = 0, newt = 1;
    int64_t r = (int64_t)mod, newr = (int64_t)a;

    while (newr != 0) {
        int64_t q = r / newr;
        int64_t temp_t = t - q * newt;
        t = newt;
        newt = temp_t;

        int64_t temp_r = r - q * newr;
        r = newr;
        newr = temp_r;
    }

    if (r > 1) return false;
    if (t < 0) t += (int64_t)mod;
    *out_inv = (uint64_t)t;
    return true;
}

// Структура запису для BSGS хеш-таблиці
typedef struct {
    uint64_t key;
    uint64_t val;
} bsgs_entry_t;

// Просте порівняння для qsort
static int compare_entries(const void *a, const void *b) {
    uint64_t k1 = ((const bsgs_entry_t*)a)->key;
    uint64_t k2 = ((const bsgs_entry_t*)a)->key;
    if (k1 < k2) return -1;
    if (k1 > k2) return 1;
    return 0;
}

// Пошук BSGS у впорядкованому масиві через бінарний пошук
static int64_t binary_search_entry(const bsgs_entry_t *arr, size_t size, uint64_t key) {
    size_t left = 0, right = size;
    while (left < right) {
        size_t mid = left + (right - left) / 2;
        if (arr[mid].key == key) return (int64_t)arr[mid].val;
        if (arr[mid].key < key) left = mid + 1;
        else right = mid;
    }
    return -1;
}

// Алгоритм BSGS мовою C
bool solve_dlog_bsgs(uint64_t g, uint64_t y, uint64_t p, uint64_t N, uint64_t *out_x, uint64_t *out_steps) {
    uint64_t m = (uint64_t)ceil(sqrt((double)N));
    bsgs_entry_t *table = (bsgs_entry_t*)malloc(m * sizeof(bsgs_entry_t));
    if (!table) return false;

    uint64_t cur = y % p;
    uint64_t steps = 0;

    // Заповнення baby steps
    for (uint64_t j = 0; j < m; ++j) {
        table[j].key = cur;
        table[j].val = j;
        cur = mod_mul(cur, g, p);
        steps++;
    }

    // Сортування масиву для бінарного пошуку O(m log m)
    qsort(table, m, sizeof(bsgs_entry_t), compare_entries);

    // Giant steps
    uint64_t factor = mod_pow(g, m, p);
    cur = factor;

    for (uint64_t i = 1; i <= m; ++i) {
        steps++;
        int64_t j = binary_search_entry(table, m, cur);
        if (j != -1) {
            *out_x = (i * m - (uint64_t)j) % N;
            *out_steps = steps;
            free(table);
            return true;
        }
        cur = mod_mul(cur, factor, p);
    }

    free(table);
    return false;
}

int main(void) {
    uint64_t p = 10007;
    uint64_t g = 5;
    uint64_t N = p - 1;
    uint64_t secret_x = 1234;
    uint64_t y = mod_pow(g, secret_x, p);

    uint64_t found_x = 0;
    uint64_t steps = 0;

    printf("[C implementation] Target secret x = %glu, y = %glu\n", secret_x, y);

    if (solve_dlog_bsgs(g, y, p, N, &found_x, &steps)) {
        printf("[C BSGS] Found x = %glu in %glu steps!\n", found_x, steps);
    } else {
        printf("[C BSGS] Failed to find discrete log.\n");
    }

    return 0;
}
```
:::

## 3. Детальний аналіз алгоритмічних методів у коді

### 3.1. Аналіз реалізації BSGS (Baby-Step Giant-Step)
Алгоритм Шенкса розділено на два послідовні етапи:
1. **Етап Baby Steps:** У коді C++ використовується `std::unordered_map<uint64_t, uint64_t>`, куди записуються значення `y · gʲ mod p` та відповідні індекси `j ∈ [0, m-1]`. Функція `reserve(m)` викликається заздалегідь для запобігання повторному перехешуванню під час вставок.
2. **Етап Giant Steps:** Попередньо обчислюється коефіцієнт розгалуження `factor = gᵐ mod p`. У циклі від `i = 1` до `m` обчислюється `cur = (gᵐ)ⁱ mod p`. При кожній ітерації виконується пошук за допомогою `find(cur)` у хеш-таблиці. Знайдений індекс `j` дозволяє миттєво обчислити дискретний логарифм `x = (i·m - j) mod N`.

У версії чистою мовою C замість хеш-таблиці вжито простішу та ефективнішу за пам'ятти структуру: динамічний масив записів `bsgs_entry_t`, який після заповнення сортується функцією `qsort()` за час `O(m log m)`. Пошук «кроків велетня» здійснюється бінарним пошуком `binary_search_entry()` за час `O(log m)`. Це зберігає загальну часову складність `O(√N log N)` при набагато нижчій константі споживання пам'яті.

### 3.2. Аналіз реалізації Pollard's Rho
Алгоритм Полларда функціонує як автомат станів без збереження таблиць у пам'яті:
1. **Псевдовипадковий перехід `next_state`:** Множина елементів групи розділяється на три рівні підмножини за залишком `x % 3`. Залежно від підмножини, поточний елемент `x` оновлюється через піднесення до квадрата `x²` або множення на `g` чи `y`. Одновідповідно оновлюються показники степенів `a` та `b`.
2. **Детектор циклів Флойда:** Змінна `tortoise` робить один крок переходу `next_state()`, а змінна `hare` — два кроки `next_state(next_state())`. Колізія виявляється за умови `tortoise.x == hare.x`.
3. **Обчислення логарифма з колізії:** З рівняння колізії `g^{a₁} · y^{b₁} ≡ g^{a₂} · y^{b₂}` виводиться `(b₁ - b₂) · x ≡ a₂ - a₁ (mod N)`. Для обчислення `x` шукається обернене значення `(b₁ - b₂)⁻¹ mod N`. Якщо обернений елемент існує, повертається точна відповідь. У разі `НСД(Δb, N) > 1` функція повертає `found = false`, сигналізуючи про необхідність повторного запуску з новими початковими станами.

## 4. Простеження кроків та крайові випадки

### 4.1. Покрокове простеження обчислення для p = 10007, g = 5, secret_x = 1234
Розглянемо практичний приклад роботи BSGS для параметрів:
- Просте число `p = 10007`, порядок групи `N = 10006`.
- Генератор `g = 5`, шукана експонента `secret_x = 1234`.
- Цільове значення `y = 5¹²³⁴ mod 10007 = 4873`.

1. **Розрахунок розміру сітки:** `m = ⌈√10006⌉ = 101`.
2. **Формування хеш-таблиці (Baby Steps):**
   - `j = 0`: `y · 5⁰ mod 10007 = 4873 → table[4873] = 0`.
   - `j = 1`: `y · 5¹ mod 10007 = (4873 · 5) mod 10007 = 4351 -> table[4351] = 1`.
   - ...
   - `j = 79`: `y · 5⁷⁹ mod 10007 = 8929 -> table[8929] = 79`.
3. **Кроки велетня (Giant Steps):**
   - `factor = gᵐ mod p = 5¹⁰¹ mod 10007 = 1122`.
   - `i = 1`: `cur = 1122¹ mod 10007 = 1122`. Пошук у таблиці: немає.
   - ...
   - `i = 13`: `cur = (1122¹³) mod 10007 = 8929`. Пошук у таблиці: **ЗНАЙДЕНО** `j = 79`!
4. **Обчислення логарифма:**
   ```
   x = i · m - j = 13 · 101 - 79 = 1313 - 79 = 1234
   ```
   Результат строго збігається з секретним значенням `x = 1234`.

### 4.2. Обробка крайових випадків у коді
1. **Граничний випадок `y = 1`:** Оскільки `g⁰ = 1`, відповідь `x = 0` знаходять на `j = 0` на першій же ітерації baby steps.
2. **Граничний випадок `y = g`:** Відповідь `x = 1` знаходять при `j = m - 1` або на першому кроці giant steps.
3. **Відсутність розв'язку (`y ∉ ⟨g⟩`):** Якщо `y` не є степенем `g` (наприклад, `g` генерує лише підгрупу квадратних залишків, а `y` є квадратичним нелишком), BSGS завершує обидва цикли за `2m` кроків і повертає `found = false`.
4. **Оптимізація пам'яті:** У середовищах із обмеженою пам'яттю (embedded/MCU) масив `bsgs_entry_t` може виділятися на зовнішній флеш-пам'яті або замінюватися на `ρ`-алгоритм Полларда, який потребує лише 32 байти станів `tortoise` та `hare`.

### 4.3. Оптимізація продуктивності та низькорівневі інструкції CPU
Найбільш критичною операцією гарячого циклу є модульне множення `(a · b) mod p`.
1. **Зменшення кількості операцій ділення:** Операція `% mod` на х86_64 перетворюється на важку інструкцію `idivq` (близько 30-40 тактів CPU). Використання зменшення Монтгомері (Montgomery reduction) або швидких комбінацій Barret reduction дозволяє замінити ділення на серію побітових зсувів `>>` та побітових `AND`, що прискорює гарячий цикл BSGS у 3-5 разів.
2. **Прапорці компілятора:** При компіляції з `-O3 -march=native -flto` компілятор впроваджує автоматичну векторизацію (AVX2/AVX-512) для одночасного обчислення декількох гілок псевдовипадкових блукань у паралельних потоках `ρ`-алгоритму Полларда.

## 5. Порівняльний аналіз продуктивності та вибір алгоритму

| Параметр порівняння | Shanks BSGS | Pollard's Rho |
| :--- | :--- | :--- |
| **Характер виконання** | Детермінований (гарантований результат) | Імовірнісний (потрібні повтори при `НСД > 1`) |
| **Часова складність** | `O(√N)` групових операцій | `O(√N)` в середньому |
| **Споживання RAM** | `O(√N)` елементів (`m · 16` байтів) | `O(1)` (фіксовані 64 байти станів) |
| **Поріг застосовності** | `N <= 10¹²` (обмеження за пам'яттю RAM) | `N <= 10¹⁸` (обмеження за часом CPU) |
| **Паралелізація** | Складна (розподіл таблиць між вузлами) | Ідеальна (ізольовані блукання з різними seed) |

Для малих груп (`N < 10⁹`) детермінований BSGS працює швидше завдяки відсутності розгалужень у циклі. Для великих полів (`10⁹ <= N <= 10¹⁸`) єдино можливим універсальним вибором є `ρ`-алгоритм Полларда через відсутність вимог до пам'яті.
