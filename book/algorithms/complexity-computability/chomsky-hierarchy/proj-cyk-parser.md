# ⚙️ Алгоритм Кока–Янгера–Касамі (CYK) для синтаксичного аналізу

Синтаксичний аналіз (парсинг) загальних контекстно-вільних граматик — це центральна задача розпізнавання мов Типу 2 в ієрархії Хомського. Якщо для детермінованих підкласів (`LL(k)`, `LR(k)`) існують спеціалізовані лінійні парсери, то для довільної, потенційно неоднозначної контекстно-вільної граматики загальним стандартом є алгоритм Кока–Янгера–Касамі (Cocke–Younger–Kasami, CYK). Він розв'язує задачу належності слова мові за час `O(n³ · |R|)` за допомогою динамічного програмування.

## Проблема синтаксичного розбору довільної КВ-граматики

Нехай задано контекстно-вільну граматику `G = (V_N, V_T, R, S)` та вхідний ланцюжок термінальних символів `w = a₁a₂...aₙ` довжини `n`. Потрібно алгоритмічно відповісти на два питання:
1. **Задача розпізнавання (Recognition Problem):** чи належить слово `w` мові `L(G)`?
2. **Задача розбору (Parsing Problem):** якщо `w ∈ L(G)`, побудувати одне або всі дерева синтаксичного виведення (Parse Trees) для цього слова.

Наївний підхід полягає в переборі всіх можливих виведень з початкового нетермінала `S`. Проте якщо граматика містить правила, що не збільшують довжину рядка (наприклад, ланцюгові правила `A → B` або правила стирання `A → ε`), дерево виведення може містити нескінченні цикли. Навіть для нескорочувальних правил кількість можливих дерев виведення зростає експоненційно як `O(bⁿ)`, де `b` — максимальна кількість розгалужень у правилах.

Для подолання експоненціального вибуху використовують принцип динамічного програмування: підрядок `w[i .. j]` розбивається на всі можливі пари суміжних підрядків `w[i .. k]` та `w[k+1 .. j]`, а результати їхнього розпізнавання кешуються у двовимірній таблиці.

## Нормальна форма Хомського (CNF) та алгоритм приведення

Алгоритм CYK вимагає, щоб вхідна граматика була представлена в нормальній формі Хомського (Chomsky Normal Form, CNF). У цій формі кожне правило породження має один із двох суворих виглядів:
1. `A → BC` — нетермінал породжує рівно два нетермінали (`A, B, C ∈ V_N`);
2. `A → a` — нетермінал породжує рівно один термінальний символ (`A ∈ V_N, a ∈ V_T`).

Якщо мова містить порожнє слово `ε`, допускається єдине правило `S₀ → ε`, за умови що новий початковий символ `S₀` не зустрічається в правих частинах інших правил.

Приведення довільної контекстно-вільної граматики до CNF виконується за п'ять послідовних кроків:

### Крок 1: Створення нового стартового символу (START)
Додаємо новий початковий нетермінал `S₀` та правило `S₀ → S`. Це гарантує, що початковий символ ніколи не з'явиться в правій частині правил, що критично для коректної обробки порожнього слова `ε`.

### Крок 2: Усунення правил стирання (NULL)
Нетермінал `A` називається **анульованим** (nullable), якщо з нього можна вивести порожній рядок: `A ⇒* ε`.
1. Знаходимо всі анульовані нетермінали: спочатку додаємо ті, для яких є правило `A → ε`, а потім ітеративно додаємо `B`, якщо є правило `B → C₁C₂...C_k`, де всі `C_i` вже визнані анульованими.
2. Для кожного правила, що містить анульовані нетермінали у правій частині, генеруємо всі можливі комбінації з їхньою присутністю та відсутністю.
3. Видаляємо всі правила вигляду `A → ε` (крім правила `S₀ → ε`, якщо `S` був анульованим).

### Крок 3: Усунення ланцюгових правил (UNIT)
Правило називається **ланцюговим** (unit rule), якщо воно має вигляд `A → B`, де `A, B ∈ V_N`.
1. Для кожного нетермінала `A` будуємо множину досяжних нетерміналів `Unit(A) = { B ∈ V_N | A ⇒* B }` за допомогою пошуку в глибину на графі одиничних переходів.
2. Для кожного `B ∈ Unit(A)` та кожного неланцюгового правила `B → γ` додаємо нове правило `A → γ`.
3. Видаляємо всі ланцюгові правила `A → B`.

### Крок 4: Заміна терміналів у довгих правилах (TERM)
Якщо правило має довжину правої частини `≥ 2` і містить термінальні символи (наприклад, `A → a B` або `A → a b`), для кожного термінала `a` вводимо новий нетермінал `T_a` та правило `T_a → a`. У вихідному правилі замінюємо термінал `a` на `T_a` (отримуємо `A → T_a B`).

### Крок 5: Бінаризація довгих правил (BIN)
Якщо правило містить три або більше нетерміналів `A → B₁ B₂ B₃ ... B_k` (`k ≥ 3`), ми розбиваємо його на каскад бінарних правил за допомогою нових допоміжних нетерміналів `D₁, D₂, ...`:
- `A → B₁ D₁`
- `D₁ → B₂ D₂`
- `...`
- `D_{k-2} → B_{k-1} B_k`

Після цих п'яти перетворень уся граматика містить лише бінарні та термінальні правила, причому розмір нової граматики є поліноміальним від розміру вихідної: `|G_CNF| = O(|G|²)`.

## Принцип динамічного програмування

Нехай задано вхідний рядок `w = a₁a₂...aₙ` довжини `n`. Алгоритм CYK будує тривимірну таблицю динамічного програмування `P[l, i, A]`:
- `l ∈ {1, 2, ..., n}` — довжина аналізованого підрядка;
- `i ∈ {1, 2, ..., n - l + 1}` — початкова позиція підрядка в слові `w` (1-індексація);
- `A ∈ V_N` — нетермінал граматики.

Значення `P[l, i, A] = true` тоді й лише тоді, коли з нетермінала `A` за правилами граматики можна вивести підрядок `w[i .. i + l - 1] = a_i a_{i+1} ... a_{i+l-1}`.

Таблиця заповнюється пошарово — від найкоротших підрядків довжини 1 до повного слова довжини `n`:

### Базовий рівень (`l = 1`)
Кожна клітинка `P[1, i]` відповідає підрядку з одного символу `a_i`. Ми перевіряємо всі термінальні правила граматики:

```
P[1, i, A] = true   ⟺   (A → a_i) ∈ R
```

### Індуктивний перехід (`l = 2, 3, ..., n`)
Для підрядка довжини `l`, що починається в позиції `i`, розглядаються всі можливі способи розділити його на дві непорожні частини:
- ліву частину `w[i .. i + k - 1]` довжини `k` (`1 ≤ k < l`);
- праву частину `w[i + k .. i + l - 1]` довжини `l - k`.

Оскільки обидві частини мають довжину строго меншу за `l`, множини нетерміналів, що їх породжують, уже обчислені на попередніх кроках у клітинках `P[k, i]` та `P[l - k, i + k]`.

Правило `A → BC` виводить підрядок `w[i .. i + l - 1]`, якщо нетермінал `B` виводить ліву частину, а нетермінал `C` виводить праву частину:

```
P[l, i, A] = true   ⟺   ∃ (A → BC) ∈ R,  ∃ k ∈ {1, ..., l - 1} :
                         (P[k, i, B] = true) ∧ (P[l - k, i + k, C] = true)
```

Слово `w` належить мові `L(G)` тоді й лише тоді, коли початковий символ граматики `S` належить множині нетерміналів у вершині піраміди:

```
w ∈ L(G)   ⟺   P[n, 1, S] = true
```

## Покроковий ручний розбір на прикладі

Розглянемо граматику в CNF для правильних арифметичних виразів:
1. `S → A B`
2. `S → S S`
3. `S → L B` (де `L → '('`)
4. `B → S R`
5. `L → '('`
6. `R → ')'`
7. `S → 'a'`

Нехай вхідне слово: `w = ( a )`. Довжина слова `n = 3`: `w[1] = '('`, `w[2] = 'a'`, `w[3] = ')'`.

1. **Рівень 1 (`l = 1`):**
   - `P[1, 1]` для `w[1] = '('`: знайдено правило `L → '('`. Множина: `{L}`.
   - `P[1, 2]` для `w[2] = 'a'`: знайдено правило `S → 'a'`. Множина: `{S}`.
   - `P[1, 3]` для `w[3] = ')'`: знайдено правило `R → ')'`. Множина: `{R}`.

2. **Рівень 2 (`l = 2`):**
   - `P[2, 1]` (підрядок `( a`): точка розбиття `k = 1`. Перевіряємо `P[1, 1] ⋈ P[1, 2] = {L} ⋈ {S}`. Правил вигляду `X → L S` немає. Множина: `∅`.
   - `P[2, 2]` (підрядок `a )`): точка розбиття `k = 1`. Перевіряємо `P[1, 2] ⋈ P[1, 3] = {S} ⋈ {R}`. Існує правило `B → S R`. Множина: `{B}`.

3. **Рівень 3 (`l = 3`):**
   - `P[3, 1]` (все слово `( a )`):
     - `k = 1`: `P[1, 1] ⋈ P[2, 2] = {L} ⋈ {B}`. Існує правило `S → L B`! Додаємо `S` до множини.
     - `k = 2`: `P[2, 1] ⋈ P[1, 3] = ∅ ⋈ {R} = ∅`.
   - Множина у вершині `P[3, 1]`: `{S}`.

Оскільки `S ∈ P[3, 1]`, слово `( a )` успішно прийняте граматикою.

## Повна реалізація алгоритму на C++ та C

:::tabs
```cpp
#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <unordered_set>
#include <unordered_map>
#include <memory>

// Структура для бінарного правила A -> B C
struct BinaryRule {
    char lhs;
    char rhs1;
    char rhs2;
};

// Структура для термінального правила A -> a
struct TerminalRule {
    char lhs;
    char terminal;
};

// Вершина дерева синтаксичного розбору
struct ParseTreeNode {
    char symbol;
    std::shared_ptr<ParseTreeNode> left;
    std::shared_ptr<ParseTreeNode> right;

    explicit ParseTreeNode(char sym) : symbol(sym), left(nullptr), right(nullptr) {}
    ParseTreeNode(char sym, std::shared_ptr<ParseTreeNode> l, std::shared_ptr<ParseTreeNode> r)
        : symbol(sym), left(std::move(l)), right(std::move(r)) {}
};

class CYKParser {
public:
    char start_symbol;
    std::vector<TerminalRule> terminal_rules;
    std::vector<BinaryRule> binary_rules;
    std::unordered_set<char> nonterminals;

    explicit CYKParser(char start) : start_symbol(start) {
        nonterminals.insert(start);
    }

    void add_terminal_rule(char lhs, char terminal) {
        terminal_rules.push_back({lhs, terminal});
        nonterminals.insert(lhs);
    }

    void add_binary_rule(char lhs, char rhs1, char rhs2) {
        binary_rules.push_back({lhs, rhs1, rhs2});
        nonterminals.insert(lhs);
        nonterminals.insert(rhs1);
        nonterminals.insert(rhs2);
    }

    // Перевірка належності слова мові
    bool parse(std::string_view w) const {
        const size_t n = w.length();
        if (n == 0) return false;

        // DP таблиця: table[len][i] містить набір нетерміналів
        std::vector<std::vector<std::unordered_set<char>>> table(
            n + 1, std::vector<std::unordered_set<char>>(n)
        );

        // Крок 1: База індукції (підрядки довжини 1)
        for (size_t i = 0; i < n; ++i) {
            char ch = w[i];
            for (const auto& rule : terminal_rules) {
                if (rule.terminal == ch) {
                    table[1][i].insert(rule.lhs);
                }
            }
        }

        // Крок 2: Індуктивні рівні (довжина len від 2 до n)
        for (size_t len = 2; len <= n; ++len) {
            for (size_t i = 0; i <= n - len; ++i) {
                for (size_t k = 1; k < len; ++k) {
                    const auto& left_set = table[k][i];
                    const auto& right_set = table[len - k][i + k];

                    if (left_set.empty() || right_set.empty()) continue;

                    for (const auto& rule : binary_rules) {
                        if (left_set.count(rule.rhs1) && right_set.count(rule.rhs2)) {
                            table[len][i].insert(rule.lhs);
                        }
                    }
                }
            }
        }

        return table[n][0].count(start_symbol) > 0;
    }
};

int main() {
    CYKParser parser('S');
    parser.add_terminal_rule('A', '(');
    parser.add_terminal_rule('C', ')');
    parser.add_terminal_rule('B', ')');
    parser.add_binary_rule('S', 'A', 'B');
    parser.add_binary_rule('S', 'S', 'S');
    parser.add_binary_rule('B', 'S', 'C');

    std::string test1 = "(())()";
    std::string test2 = "(()))";

    std::cout << "Word \"" << test1 << "\": " 
              << (parser.parse(test1) ? "ACCEPTED" : "REJECTED") << "\n";
    std::cout << "Word \"" << test2 << "\": " 
              << (parser.parse(test2) ? "ACCEPTED" : "REJECTED") << "\n";

    return 0;
}
```
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

#define MAX_RULES 64
#define MAX_NONTERMINALS 26
#define MAX_WORD_LEN 128

typedef struct {
    char lhs;
    char rhs1;
    char rhs2;
} BinaryRule;

typedef struct {
    char lhs;
    char terminal;
} TerminalRule;

typedef struct {
    char start_symbol;
    BinaryRule binary_rules[MAX_RULES];
    int num_binary;
    TerminalRule terminal_rules[MAX_RULES];
    int num_terminal;
} Grammar;

void grammar_init(Grammar* g, char start) {
    g->start_symbol = start;
    g->num_binary = 0;
    g->num_terminal = 0;
}

void add_terminal_rule(Grammar* g, char lhs, char terminal) {
    if (g->num_terminal < MAX_RULES) {
        g->terminal_rules[g->num_terminal++] = (TerminalRule){lhs, terminal};
    }
}

void add_binary_rule(Grammar* g, char lhs, char rhs1, char rhs2) {
    if (g->num_binary < MAX_RULES) {
        g->binary_rules[g->num_binary++] = (BinaryRule){lhs, rhs1, rhs2};
    }
}

// Тривимірний масив для DP: dp[len][i][nonterminal_idx]
static bool dp[MAX_WORD_LEN][MAX_WORD_LEN][MAX_NONTERMINALS];

static inline int nt_to_idx(char nt) {
    return nt - 'A';
}

bool cyk_parse(const Grammar* g, const char* w) {
    int n = (int)strlen(w);
    if (n == 0 || n >= MAX_WORD_LEN) return false;

    memset(dp, 0, sizeof(dp));

    // Крок 1: Базовий рівень (довжина 1)
    for (int i = 0; i < n; ++i) {
        char ch = w[i];
        for (int r = 0; r < g->num_terminal; ++r) {
            if (g->terminal_rules[r].terminal == ch) {
                int idx = nt_to_idx(g->terminal_rules[r].lhs);
                if (idx >= 0 && idx < MAX_NONTERMINALS) {
                    dp[1][i][idx] = true;
                }
            }
        }
    }

    // Крок 2: Індуктивний перебір довжини підрядка
    for (int len = 2; len <= n; ++len) {
        for (int i = 0; i <= n - len; ++i) {
            for (int k = 1; k < len; ++k) {
                for (int r = 0; r < g->num_binary; ++r) {
                    int a_idx = nt_to_idx(g->binary_rules[r].lhs);
                    int b_idx = nt_to_idx(g->binary_rules[r].rhs1);
                    int c_idx = nt_to_idx(g->binary_rules[r].rhs2);

                    if (dp[k][i][b_idx] && dp[len - k][i + k][c_idx]) {
                        dp[len][i][a_idx] = true;
                    }
                }
            }
        }
    }

    int start_idx = nt_to_idx(g->start_symbol);
    return dp[n][0][start_idx];
}

int main(void) {
    Grammar g;
    grammar_init(&g, 'S');

    add_terminal_rule(&g, 'A', '(');
    add_terminal_rule(&g, 'B', ')');
    add_terminal_rule(&g, 'C', ')');
    add_binary_rule(&g, 'S', 'A', 'B');
    add_binary_rule(&g, 'S', 'S', 'S');
    add_binary_rule(&g, 'B', 'S', 'C');

    const char* test1 = "(())()";
    const char* test2 = "(()))";

    printf("Word \"%s\": %s\n", test1, cyk_parse(&g, test1) ? "ACCEPTED" : "REJECTED");
    printf("Word \"%s\": %s\n", test2, cyk_parse(&g, test2) ? "ACCEPTED" : "REJECTED");

    return 0;
}
```
:::

## Аналіз складності та оптимізації

Алгоритм CYK має строго визначені теоретичні та практичні характеристики:

1. **Часова складність:**
   Кількість ітерацій внутрішніх циклів визначається кількістю трійок `(len, i, k)`:
   ```
   ∑_{len=2}^{n} (n - len + 1) · (len - 1) = (n³ - n) / 6
   ```
   На кожному кроці ми перебираємо всі бінарні правила `|R_bin|`. Загальний час роботи становить `O(n³ · |R|)`.
   
2. **Просторова складність:**
   Таблиця зберігає стан для `n · (n + 1) / 2` підрядків. Для кожного підрядка зберігається множина розміру щонайбільше `|V_N|`. Використання бітових масок (bitsets) дозволяє зменшити обсяг пам'яті до `O(n² · (|V_N| / 64))` слів машинного коду та прискорити перевірку правил за допомогою побітових операцій.

3. **Алгоритм Валіанта та множення матриць:**
   У 1975 році Леслі Валіант (Leslie Valiant) довів, що синтаксичний аналіз контекстно-вільних граматик можна звести до множення булевих матриць. Використовуючи швидкі матричні алгоритми (як-от алгоритм Штрассена або алгоритм Копперсміта–Вінограда), час розбору КВ-граматик можна знизити до `O(n^ω)`, де `ω < 2.373` — показник степеня множення матриць.

4. **Ймовірнісний CYK (Probabilistic CYK, PCYK):**
   В обробці природних мов (NLP) та біоінформатиці граматики часто є неоднозначними. Стохастичні граматики (PCFG) приписують кожному правилу ймовірність `P(A → BC)`. Алгоритм PCYK модифікує рівняння динамічного програмування, замінюючи булеве «або» на взяття максимуму:
   ```
   Score[len, i, A] = max_{A → BC, k} ( P(A → BC) · Score[k, i, B] · Score[len - k, i + k, C] )
   ```
   Щоб запобігти зникненню порядку чисел при множенні малих ймовірностей (underflow), обчислення виконують у логарифмічній шкалі `log P`. Це дозволяє знаходити найбільш вірогідне синтаксичне дерево за алгоритмом Вітербі за той самий кубічний час `O(n³)`.
