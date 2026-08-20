# ⚙️ Реалізація алгоритму Квайна–Мак-Класкі

Програмна реалізація методу Квайна–Мак-Класкі вимагає ефективного двійкового подання для логічних термів із трьома можливими станами кожного розряду: пряма змінна (`1`), інвертована змінна (`0`) та елімінована змінна (`-`, прочерк). Зберігати такі терми у вигляді символьних рядків чи масивів символів у пам'яті вкрай нераціонально: рядкові операції повільні, вимагають динамічного виділення пам'яті для кожного порівняння та не використовують паралелізм процесорних інструкцій.

Оптимальне машинне подання спирається на **бітову пару чисел**:
1. `bits` (32- або 64-розрядне ціле число) — значення фіксованих розрядів змінних (де біт `0` означає інверсію змінної, а біт `1` — пряме входження).
2. `mask` (ціле число тієї самої розрядності) — маска прочерків, де біт `1` позначає позицію змінної, яка випала внаслідок склеювання, а біт `0` — змінну, що залишилася у виразі.

Таке розділення дозволяє звести всі базові операції мінімізації (перевірку сумісності, склеювання та перевірку покриття) до кількох швидких побітових інструкцій процесора.

## Двійкова арифметика склеювання та перевірки покриття

Нехай маємо два терми `A` і `B`. Вони можуть склеїтися в єдиний більший підкуб за тотожністю `X·Y + X·Ȳ = X` тоді й лише тоді, коли виконуються дві умови:
- **Умова 1 (ідентичність масок):** терми мають абсолютно однакові позиції прочерків (`A.mask == B.mask`). Якщо в одному термі випала змінна `C`, а в іншому — змінна `D`, вони не утворюють спільну грань гіперкуба.
- **Умова 2 (одинична відстань Геммінга):** за невипадними розрядами терми різняться **рівно в одній позиції**.

Для перевірки другої умови обчислюють бітову різницю незмінних розрядів:

```
diff = (A.bits ^ B.bits) & ~A.mask
```

Якщо значення `diff` є ненульовим і становить точний степінь двійки (містить рівно один встановлений біт), склеювання можливе. У двійковій арифметиці наявність рівно одного встановленого біта перевіряється класичним виразом:

```
is_single_bit = (diff != 0) && ((diff & (diff - 1)) == 0)
```

Операція `diff & (diff - 1)` скидає наймолодший встановлений біт у нуль. Якщо після цього число перетворюється на нуль, у ньому був присутній рівно один одиничний біт. Новоутворений терм отримує оновлену маску `A.mask | diff` та нормалізовані біти значень `A.bits & ~diff`.

Так само блискавично виконується операція перевірки, чи накриває простий імплікант `P` конкретний числовий мінтерм `M`:

```
is_covered = ((M & ~P.mask) == (P.bits & ~P.mask))
```

Ми просто накладаємо інвертовану маску прочерків на обидва числа й порівнюємо результат: якщо всі значущі біти збігаються, мінтерм належить цьому підкубу.

## Архітектура двох фаз у коді

Програма організована за модульним принципом відповідно до двох фаз алгоритму:

1. **Фаза 1 — Поколінне каскадне склеювання:**
   - Початкові мінтерми та невизначені стани (`don't-care`) ініціалізуються з маскою `mask = 0` (0-куби).
   - Алгоритм ітерує за поколіннями (0-куби → 1-куби → 2-куби → 4-куби …).
   - У кожному поколінні перебираються всі пари сумісних термів. Якщо пару склеєно, обидва вихідні терми отримують прапорець `used = true`.
   - Оскільки один і той самий 2-куб може утворитися різними шляхами (наприклад, злиття пар `(0, 1)` та `(8, 9)` дає той самий куб `-00-`, що й злиття пар `(0, 8)` та `(1, 9)`), кожне новоутворене значення перевіряється на унікальність перед додаванням до наступного покоління.
   - Терми, які залишилися з прапорцем `used == false`, додаються до списку **простих імплікантів** (Prime Implicants).

2. **Фаза 2 — Матриця покриття та вибір мінімуму:**
   - Будується двовимірна булева матриця `chart[p][m]`, де рядок `p` відповідає простому імпліканту, а стовпець `m` — обов'язковому мінтерму функції.
   - Алгоритм сканує стовпці: якщо стовпець містить рівно одну позначку `1`, відповідний імплікант є **істотним** (Essential Prime Implicant, EPI) і обов'язково включається до розв'язку.
   - Усі мінтерми, покриті знайденими EPI, помічаються як закриті.
   - Для залишку стовпців застосовується жадібний добір: на кожному кроці обирається імплікант, який накриває найбільшу кількість ще непокритих мінтермів.

## Відмінності між реалізаціями на C та C++

- **Реалізація на C:** орієнтована на мінімальний оверхед і вбудовані системи. Використовує фіксовані статичні буфери без динамічного виділення пам'яті (`malloc`/`free`), що унеможливлює витоки пам'яті та фрагментацію купи в прошивках мікроконтролерів.
- **Реалізація на C++:** побудована за сучасними стандартами C++20 з використанням ідіоми RAII. Замість сирих покажчиків і фіксованих масивів застосовано динамічні контейнери `std::vector`, строгу типізацію методів класу `QuineMcCluskeySolver`, стандартні алгоритми `std::find`, `std::all_of` та атрибути `[[nodiscard]]`. Пам'ять звільняється автоматично деструкторами при виході з області видимості.

## Робочий код на C та C++

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_VARS 16
#define MAX_TERMS 512

typedef struct {
    unsigned bits;   // значення незмінних бітів
    unsigned mask;   // 1 на позиціях прочерків '-'
    int      used;   // прапорець: чи склеївся терм у більший куб
} Term;

// Підрахунок одиничних бітів (вага Геммінга)
static int popcount(unsigned x) {
    int c = 0;
    while (x) {
        c += (x & 1);
        x >>= 1;
    }
    return c;
}

// Перевірка, чи різняться терми рівно в одному незмінному біті
static int can_merge(Term a, Term b, unsigned *diff_bit) {
    if (a.mask != b.mask) return 0;
    unsigned d = (a.bits ^ b.bits) & ~a.mask;
    if (d && (d & (d - 1)) == 0) {
        *diff_bit = d;
        return 1;
    }
    return 0;
}

// Перевірка чи терм накриває конкретний числовий мінтерм
static int covers(Term pi, unsigned minterm) {
    return ((minterm & ~pi.mask) == (pi.bits & ~pi.mask));
}

// Друк імпліканта символами '0', '1', '-'
static void print_term(Term t, int nvars) {
    for (int i = nvars - 1; i >= 0; --i) {
        if (t.mask & (1U << i)) {
            putchar('-');
        } else if (t.bits & (1U << i)) {
            putchar('1');
        } else {
            putchar('0');
        }
    }
}

// Головна функція мінімізації
void quine_mccluskey(int nvars, const int *minterms, int n_min, const int *dontcares, int n_dc) {
    Term current[MAX_TERMS];
    int n_curr = 0;

    // Завантажуємо мінтерми та don't-care стани
    for (int i = 0; i < n_min; ++i) {
        current[n_curr++] = (Term){ .bits = (unsigned)minterms[i], .mask = 0, .used = 0 };
    }
    for (int i = 0; i < n_dc; ++i) {
        current[n_curr++] = (Term){ .bits = (unsigned)dontcares[i], .mask = 0, .used = 0 };
    }

    Term primes[MAX_TERMS];
    int n_primes = 0;

    // Фаза 1: Ітеративне каскадне склеювання
    while (n_curr > 0) {
        Term next_gen[MAX_TERMS];
        int n_next = 0;

        for (int i = 0; i < n_curr; ++i) {
            for (int j = i + 1; j < n_curr; ++j) {
                unsigned diff = 0;
                if (can_merge(current[i], current[j], &diff)) {
                    current[i].used = 1;
                    current[j].used = 1;

                    Term merged = {
                        .bits = current[i].bits & ~diff,
                        .mask = current[i].mask | diff,
                        .used = 0
                    };

                    // Усуваємо дублікати в новому поколінні
                    int exists = 0;
                    for (int k = 0; k < n_next; ++k) {
                        if (next_gen[k].bits == merged.bits && next_gen[k].mask == merged.mask) {
                            exists = 1;
                            break;
                        }
                    }
                    if (!exists && n_next < MAX_TERMS) {
                        next_gen[n_next++] = merged;
                    }
                }
            }
        }

        // Усі несклеєні терми поточного раунду є простими імплікантами
        for (int i = 0; i < n_curr; ++i) {
            if (!current[i].used) {
                int exists = 0;
                for (int k = 0; k < n_primes; ++k) {
                    if (primes[k].bits == current[i].bits && primes[k].mask == current[i].mask) {
                        exists = 1;
                        break;
                    }
                }
                if (!exists && n_primes < MAX_TERMS) {
                    primes[n_primes++] = current[i];
                }
            }
        }

        memcpy(current, next_gen, sizeof(Term) * n_next);
        n_curr = n_next;
    }

    // Фаза 2: Таблиця покриття
    int chart[MAX_TERMS][MAX_TERMS] = {0};
    for (int p = 0; p < n_primes; ++p) {
        for (int m = 0; m < n_min; ++m) {
            if (covers(primes[p], (unsigned)minterms[m])) {
                chart[p][m] = 1;
            }
        }
    }

    int covered_minterms[MAX_TERMS] = {0};
    int chosen_primes[MAX_TERMS] = {0};

    // Знаходження істотних простих імплікантів (EPI)
    for (int m = 0; m < n_min; ++m) {
        int count = 0;
        int last_p = -1;
        for (int p = 0; p < n_primes; ++p) {
            if (chart[p][m]) {
                count++;
                last_p = p;
            }
        }
        if (count == 1 && last_p != -1 && !chosen_primes[last_p]) {
            chosen_primes[last_p] = 1;
            for (int j = 0; j < n_min; ++j) {
                if (chart[last_p][j]) {
                    covered_minterms[j] = 1;
                }
            }
        }
    }

    // Жадібне докриття залишкових мінтермів
    while (1) {
        int all_done = 1;
        for (int m = 0; m < n_min; ++m) {
            if (!covered_minterms[m]) {
                all_done = 0;
                break;
            }
        }
        if (all_done) break;

        int best_p = -1;
        int max_new_cover = -1;
        for (int p = 0; p < n_primes; ++p) {
            if (chosen_primes[p]) continue;
            int new_cov = 0;
            for (int m = 0; m < n_min; ++m) {
                if (!covered_minterms[m] && chart[p][m]) {
                    new_cov++;
                }
            }
            if (new_cov > max_new_cover) {
                max_new_cover = new_cov;
                best_p = p;
            }
        }

        if (best_p == -1 || max_new_cover == 0) break;
        chosen_primes[best_p] = 1;
        for (int m = 0; m < n_min; ++m) {
            if (chart[best_p][m]) covered_minterms[m] = 1;
        }
    }

    // Друк підсумкової мінімальної ДНФ
    printf("Minimal SOP terms:\n");
    int first = 1;
    for (int p = 0; p < n_primes; ++p) {
        if (chosen_primes[p]) {
            if (!first) printf(" + ");
            print_term(primes[p], nvars);
            first = 0;
        }
    }
    printf("\n");
}

int main(void) {
    // Приклад F(A,B,C,D) = Σ m(0, 1, 2, 5, 6, 7, 8, 9, 10, 14)
    int minterms[] = {0, 1, 2, 5, 6, 7, 8, 9, 10, 14};
    int n_min = sizeof(minterms) / sizeof(minterms[0]);
    quine_mccluskey(4, minterms, n_min, NULL, 0);
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <string>
#include <algorithm>
#include <cstdint>
#include <bit>

struct Term {
    uint32_t bits{0};  // Значення визначених бітів
    uint32_t mask{0};  // Маска прочерків '-' (1 де змінна випала)
    bool used{false};  // Чи склеївся терм у наступне покоління

    bool operator==(const Term& other) const noexcept {
        return bits == other.bits && mask == other.mask;
    }

    [[nodiscard]] bool covers(uint32_t minterm) const noexcept {
        return (minterm & ~mask) == (bits & ~mask);
    }

    [[nodiscard]] std::string to_string(int nvars) const {
        std::string s;
        s.reserve(nvars);
        for (int i = nvars - 1; i >= 0; --i) {
            if (mask & (1U << i)) {
                s.push_back('-');
            } else if (bits & (1U << i)) {
                s.push_back('1');
            } else {
                s.push_back('0');
            }
        }
        return s;
    }
};

class QuineMcCluskeySolver {
public:
    QuineMcCluskeySolver(int nvars, std::vector<uint32_t> minterms, std::vector<uint32_t> dontcares = {})
        : nvars_(nvars), minterms_(std::move(minterms)), dontcares_(std::move(dontcares)) {}

    [[nodiscard]] std::vector<Term> solve() {
        std::vector<Term> current;
        current.reserve(minterms_.size() + dontcares_.size());

        for (uint32_t m : minterms_) current.push_back(Term{.bits = m, .mask = 0, .used = false});
        for (uint32_t d : dontcares_) current.push_back(Term{.bits = d, .mask = 0, .used = false});

        std::vector<Term> prime_implicants;

        // Фаза 1: Каскадне склеювання поколінь
        while (!current.empty()) {
            std::vector<Term> next_generation;

            for (size_t i = 0; i < current.size(); ++i) {
                for (size_t j = i + 1; j < current.size(); ++j) {
                    if (current[i].mask != current[j].mask) continue;

                    uint32_t diff = (current[i].bits ^ current[j].bits) & ~current[i].mask;
                    if (diff != 0 && (diff & (diff - 1)) == 0) {
                        current[i].used = true;
                        current[j].used = true;

                        Term merged{
                            .bits = current[i].bits & ~diff,
                            .mask = current[i].mask | diff,
                            .used = false
                        };

                        if (std::find(next_generation.begin(), next_generation.end(), merged) == next_generation.end()) {
                            next_generation.push_back(merged);
                        }
                    }
                }
            }

            for (const auto& term : current) {
                if (!term.used) {
                    if (std::find(prime_implicants.begin(), prime_implicants.end(), term) == prime_implicants.end()) {
                        prime_implicants.push_back(term);
                    }
                }
            }

            current = std::move(next_generation);
        }

        // Фаза 2: Вибір покриття
        return select_minimal_cover(prime_implicants);
    }

private:
    int nvars_;
    std::vector<uint32_t> minterms_;
    std::vector<uint32_t> dontcares_;

    [[nodiscard]] std::vector<Term> select_minimal_cover(const std::vector<Term>& primes) const {
        if (primes.empty() || minterms_.empty()) return {};

        std::vector<std::vector<bool>> chart(primes.size(), std::vector<bool>(minterms_.size(), false));
        for (size_t p = 0; p < primes.size(); ++p) {
            for (size_t m = 0; m < minterms_.size(); ++m) {
                chart[p][m] = primes[p].covers(minterms_[m]);
            }
        }

        std::vector<bool> covered_minterms(minterms_.size(), false);
        std::vector<bool> chosen_primes(primes.size(), false);

        // 1. Пошук істотних простих імплікантів (EPI)
        for (size_t m = 0; m < minterms_.size(); ++m) {
            int count = 0;
            int last_p = -1;
            for (size_t p = 0; p < primes.size(); ++p) {
                if (chart[p][m]) {
                    count++;
                    last_p = static_cast<int>(p);
                }
            }
            if (count == 1 && last_p != -1 && !chosen_primes[last_p]) {
                chosen_primes[last_p] = true;
                for (size_t j = 0; j < minterms_.size(); ++j) {
                    if (chart[last_p][j]) covered_minterms[j] = true;
                }
            }
        }

        // 2. Жадібний вибір для залишку стовпців
        while (true) {
            if (std::all_of(covered_minterms.begin(), covered_minterms.end(), [](bool v) { return v; })) {
                break;
            }

            int best_p = -1;
            int max_new_cover = 0;

            for (size_t p = 0; p < primes.size(); ++p) {
                if (chosen_primes[p]) continue;
                int new_cover = 0;
                for (size_t m = 0; m < minterms_.size(); ++m) {
                    if (!covered_minterms[m] && chart[p][m]) {
                        new_cover++;
                    }
                }
                if (new_cover > max_new_cover) {
                    max_new_cover = new_cover;
                    best_p = static_cast<int>(p);
                }
            }

            if (best_p == -1 || max_new_cover == 0) break;

            chosen_primes[best_p] = true;
            for (size_t m = 0; m < minterms_.size(); ++m) {
                if (chart[best_p][m]) covered_minterms[m] = true;
            }
        }

        std::vector<Term> result;
        for (size_t p = 0; p < primes.size(); ++p) {
            if (chosen_primes[p]) result.push_back(primes[p]);
        }
        return result;
    }
};

int main() {
    // Приклад F(A,B,C,D) = Σ m(0, 1, 2, 5, 6, 7, 8, 9, 10, 14)
    QuineMcCluskeySolver solver(4, {0, 1, 2, 5, 6, 7, 8, 9, 10, 14});
    auto result = solver.solve();

    std::cout << "Minimal SOP terms:\n";
    for (size_t i = 0; i < result.size(); ++i) {
        if (i > 0) std::cout << " + ";
        std::cout << result[i].to_string(4);
    }
    std::cout << '\n';
    return 0;
}
```
:::

## Крайові випадки та аналіз продуктивності

Під час практичного використання алгоритму слід враховувати кілька важливих граничних станів:

1. **Тотожна одиниця (`F ≡ 1`):** якщо задано всі `2ⁿ` мінтермів, каскадне склеювання послідовно згорне всі вершини гіперкуба в єдиний терм із повною маскою прочерків (`mask = (1 << n) - 1`, рядок `----`), що відповідає константі 1 (нуль вентилів).
2. **Тотожний нуль (`F ≡ 0`):** якщо список мінтермів порожній, алгоритм завершує роботу на етапі ініціалізації та повертає порожній набір імплікантів.
3. **Невизначені стани (`don't-care`):** терми `dontcares` обов'язково беруть участь у склеюванні на Фазі 1, щоб допомогти утворити якомога ширші прості імпліканти з меншою кількістю літер. Проте вони не додаються у стовпці матриці на Фазі 2, оскільки алгоритм не зобов'язаний покривати стани, вихід яких не має значення для системи.
4. **Вибух кількості імплікантів:** для функцій із кількістю змінних `n > 14` масив `MAX_TERMS` у статичній реалізації на C може переповнитися через експоненційне зростання кількості проміжних підкубів. У промислових САПР для таких випадків застосовують динамічні бітові хеш-таблиці або переходять до евристичних алгоритмів оптимізації.
