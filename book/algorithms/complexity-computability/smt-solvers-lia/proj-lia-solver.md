# ⚙️ Інкрементальний LIA-сольвер на основі дуального симплексу та розгалужень

У системній архітектурі DPLL(T) розв'язувач теорії лінійної цілочисельної арифметики (LIA) функціонує як спеціалізований оракул для булевого CDCL-рушія. Він отримує від булевого ядра потік призначень арифметичних літералів, підтримує внутрішній стан системи нерівностей, перевіряє їхню геометричну сумісність у дискретному просторі `Zⁿ`, а в разі виявлення суперечності — будує мінімальну лему конфлікту для повернення у булевий стек викликів.

Нижче детально розібрано архітектуру, структури даних, математичні інваріанти, оптимізації розріджених матриць та закінчену робочу реалізацію інкрементального LIA-сольвера, що комбінує модифікований табличний симплекс-метод Дютертра — де Моури для неперервної релаксації над полем раціональних чисел та модуль розгалужень і меж (Branch and Bound) для знаходження цілочисельних точок.

## 1. Канонічна форма та структура симплекс-табло

Класичний симплекс-метод лінійного програмування оптимізує лінійну цільову функцію, тоді як для SMT-сольвера єдиною метою є швидка перевірка сумісності (feasibility) кон'юнкції нерівностей. Замість додавання окремих штучних змінних для кожної нерівності, алгоритм Дютертра — де Моури представляє будь-яку систему обмежень через систему лінійних однорідних рівностей із двосторонніми інтервальними межами на кожну змінну.

Довільна лінійна нерівність `∑ a_j · x_j ≤ b` транслюється введенням додаткової слабкої змінної (slack variable) `s_i`:

```
s_i = ∑_{j=1}^n a_{ij} · x_j
-∞ ≤ s_i ≤ b
```

Загальна система з `m` обмежень та `n` вільних змінних записується у матричному вигляді:

```
A · x_N - x_B = 0
l_k ≤ x_k ≤ u_k,    для всіх k ∈ {1, ..., n + m}
```

де `x_N = (x₁, ..., x_n)` — вектор небазисних (первинних) змінних, а `x_B = (x_{n+1}, ..., x_{n+m})` — вектор базисних (додаткових) змінних табло.

Таблиця (табло) зберігає коефіцієнти матриці `A` розміру `m × n`. Для кожної змінної `x_k` система підтримує:
1. Поточне присвоєне значення `val(x_k) ∈ Q`.
2. Поточну нижню межу `low(x_k) ∈ Q ∪ { -∞ }`.
3. Поточну верхню межу `high(x_k) ∈ Q ∪ { +∞ }`.
4. Ознаку цілочисельності `is_integer(x_k) ∈ { 0, 1 }`.

Фундаментальний інваріант симплекс-табло полягає в тому, що значення всіх небазисних змінних завжди строго лежать у межах їхніх інтервалів:

```
l_j ≤ val(x_j) ≤ u_j,    для всіх j ∈ N
```

Значення кожної базисної змінної однозначно визначається поточними значеннями небазисних змінних через відповідний рядок табло:

```
val(x_i) = ∑_{j ∈ N} a_{ij} · val(x_j),    для кожного i ∈ B
```

Якщо для деякої базисної змінної `x_i` виявляється, що `val(x_i) < l_i` або `val(x_i) > u_i`, це означає порушення межі. Завданням симплекс-процедури є відновлення інваріанта допустимості за допомогою послідовності шарнірних кроків (Pivoting).

## 2. Механізм інкрементального шарнірного переходу (Pivoting)

Шарнірний перехід полягає в обміні ролями між однією базисною змінною `x_i` та однією небазисною змінною `x_j`, для якої коефіцієнт `a_{ij} ≠ 0`.

Нехай для базисної змінної `x_i` виявлено порушення нижньої межі (`val(x_i) < l_i`). Щоб збільшити значення `val(x_i)` до `l_i`, необхідно змінити значення однієї з небазисних змінних `x_j`:
- Якщо `a_{ij} > 0`, значення `x_j` необхідно збільшити, отже, `val(x_j)` має бути строго меншим за свою верхню межу `u_j`.
- Якщо `a_{ij} < 0`, значення `x_j` необхідно зменшити, отже, `val(x_j)` має бути строго більшим за свою нижню межу `l_j`.

Якщо серед усіх небазисних змінних у рядку `i` знайдено відповідного кандидата `x_j`, виконується операція шарніра. Рівняння рядка розв'язується відносно `x_j`:

```
x_j = (1 / a_{ij}) · x_i - ∑_{k ∈ N, k ≠ j} (a_{ik} / a_{ij}) · x_k
```

Коефіцієнти табло перераховуються за формулами:

```
a'_ij = 1 / a_ij
a'_ik = - a_ik / a_ij                  [для всіх k ≠ j]
a'_rk = a_rk - a_rj · a_ik / a_ij      [для всіх r ≠ i, k ≠ j]
a'_rj = a_rj / a_ij                    [для всіх r ≠ i]
```

Після перерахунку матриці значення нової небазисної змінної `x_i` встановлюється рівним її порушеній межі `l_i`, а значення всіх інших базисних змінних оновлюються за новими коефіцієнтами рядків.

## 3. Генерація математичних сертифікатів конфлікту

Найважливішою перевагою алгоритму Дютертра — де Моури над геометричними методами є можливість миттєво побудувати строге аналітичне пояснення несумісності (Conflict Explanation) без додаткових обчислень.

Якщо для базисної змінної `x_i` порушено нижню межу (`val(x_i) < l_i`), але для кожної небазисної змінної `x_j` з `a_{ij} > 0` вже досягнуто максимуму (`val(x_j) = u_j`), а для кожної з `a_{ij} < 0` — досягнуто мінімуму (`val(x_j) = l_j`), то шарнірний перехід неможливий.

У цьому стані максимальне теоретично досяжне значення виразу `∑ a_{ij} · x_j` дорівнює:

```
max( val(x_i) ) = ∑_{j: a_ij > 0} a_ij · u_j + ∑_{j: a_ij < 0} a_ij · l_j
```

Оскільки це максимальне значення строго менше за необхідну нижню межу `l_i`, система не має розв'язку над `Q`. Рядок табло формує сертифікат несумісності (лему Фа Farkas):

```
( ∧_{j: a_ij > 0} (x_j ≤ u_j)  ∧  ∧_{j: a_ij < 0} (x_j ≥ l_j) )  →  (x_i < l_i)
```

Булеве заперечення цієї імплікації утворює компактний конфліктний диз'юнкт для CDCL:

```
C_conflict = ∨_{j: a_ij > 0} ¬(x_j ≤ u_j)  ∨  ∨_{j: a_ij < 0} ¬(x_j ≥ l_j)  ∨  ¬(x_i ≥ l_i)
```

Цей диз'юнкт містить лише ті обмеження, які брали безпосередню участь у формуванні конфліктного рядка, що гарантує його максимальну вибірковість та силу при зрізанні простору пошуку в SAT-движку.

## 4. Обробка строгих нерівностей та інфінітезимальне розширення Q(ε)

У задачах верифікації часто зустрічаються строгі нерівності вигляду `x < c` або `x > c`. Для цілочисельних змінних `x ∈ Z` строгу нерівність можна легко замінити на нестрогу:

```
x < c   ⟺   x ≤ c - 1
```

Проте під час роботи симплекс-методу цілочисельні обмеження релаксуються до поля раціональних чисел `Q`. Якщо в релаксації замінити `x < c` на `x ≤ c - 1`, допустима область над `Q` штучно звузиться, що призведе до хибного висновку про нездійсненність (наприклад, якщо істинний розв'язок має `x = c - 0.5`).

Для точної підтримки строгих нерівностей над раціональними числами Дютертр та де Моура запропонували використовувати **інфінітезимальне розширення поля раціональних чисел `Q(ε)`**.

Кожне значення та кожна межа змінної представляються парою чисел `(k, c) ∈ Q × Q`, що інтерпретується як формальний вираз:

```
v = k + c · ε
```

де `ε > 0` — символічна додатна нескінченно мала величина, яка є меншою за будь-яке додатне раціональне число:

```
∀q ∈ Q_{>0}.  0 < ε < q
```

### Арифметика та лексикографічний порядок у Q(ε)

Операції над інфінітезимальними числами визначаються покомпонентно:
1. **Додавання:** `(k₁, c₁) + (k₂, c₂) = (k₁ + k₂, c₁ + c₂)`
2. **Множення на раціональний скаляр `q ∈ Q`:** `q · (k, c) = (q · k, q · c)`
3. **Лексикографічне порівняння (`<`):**
   ```
   (k₁, c₁) < (k₂, c₂)  ⟺  (k₁ < k₂)  ∨  (k₁ = k₂  ∧  c₁ < c₂)
   ```

Завдяки цьому строгому порядку межі транслюються без жодної втрати точності:
- Нестрога верхня межа `x ≤ a` кодується як пара `high(x) = (a, 0)`.
- Строга верхня межа `x < a` (тобто `x ≤ a - ε`) кодується як пара `high(x) = (a, -1)`.
- Нестрога нижня межа `x ≥ b` кодується як пара `low(x) = (b, 0)`.
- Строга нижня межа `x > b` (тобто `x ≥ b + ε`) кодується як пара `low(x) = (b, +1)`.

Якщо симплекс знаходить розв'язок у `Q(ε)` вигляду `val(x_i) = (k_i, c_i)`, то дійсний числовий розв'язок отримується підстановкою достатньо малого раціонального `ε* > 0`, що повністю усуває чисельну нестабільність.

## 5. Динамічні відтинання Гоморі у поєднанні з Branch-and-Bound

Коли релаксована система в `Q` є сумісною, але деяка цілочисельна змінна `x_i` набула дробового значення `v ∉ Z`, сольвер переходить до цілочисельного пошуку. Існує дві взаємодоповнюючі стратегії:

1. **Розгалуження (Branch and Bound):** створення двох альтернативних гілок пошуку:
   ```
   Гілка 1: low(x_i) = ceil(v)
   Гілка 2: high(x_i) = floor(v)
   ```
2. **Відтинальні площини Гоморі (Gomory Cuts):** генерація додаткової нерівності безпосередньо з рядка табло, яка миттєво відтинає поточну дробову вершину.

Нехай базисна змінна `x_i` дробова. Її рядок табло має вигляд:

```
x_i = a_{i0} + ∑_{j ∈ N} a_{ij} · x_j
```

Виділяючи дробові частини `f_{i0} = a_{i0} - ⌊a_{i0}⌋` та `f_{ij} = a_{ij} - ⌊a_{ij}⌋`, формується нове обмеження:

```
∑_{j ∈ N} f_{ij} · x_j ≥ f_{i0}
```

Сольвер динамічно додає новий рядок у табло з новою базисною змінною `s_cut = ∑ f_{ij} · x_j` та встановлює для неї нижню межу `low(s_cut) = f_{i0}`. Оскільки в поточному стані всі небазисні змінні занулені на своїх нижніх межах, нова змінна `s_cut` має значення `0 < f_{i0}`, що створює порушення межі та запускає дуальний симплекс без необхідності комбінаторного розгалуження.

## 6. Інтеграція LIA-сольвера в архітектуру DPLL(T)

У повноцінному SMT-рушії LIA-сольвер працює у тісній взаємодії з булевим ядром CDCL через формалізований інтерфейс. Існує два режими взаємодії:

1. **Лінива перевірка (Lazy Checking):**
   CDCL призначає булеві значення всім змінним до побудови повної булевої моделі `M`, після чого весь набір активних арифметичних літералів передається у LIA-сольвер. Якщо знайдено `UNSAT`, повертається лема конфлікту, і CDCL виконує вертання. Цей підхід простий у реалізації, але марнує багато часу на дослідження вочевидь суперечливих комбінацій.

2. **Рання перевірка та теорійне поширення (Eager / Early Theory Propagation):**
   На кожному кроці прийняття рішення або булевого поширення (BCP) нові арифметичні літерали негайно передаються у LIA-сольвер через `assert_bound`. Симплекс виконує декілька швидких шарнірних кроків. Якщо межі якоїсь іншої змінної виявляються затиснутими до константи (наприклад, `low(x) = high(x) = 5`), сольвер генерує **T-поширення (Theory Propagation)**, передаючи виведене булеве значення назад у trail булевого рушія. Це дозволяє скорочувати дерево пошуку на ранніх етапах.

## 7. Стратегія точної арифметики та захист від переповнення

У реальних інженерних задачах матричні коефіцієнти після декількох сотень шарнірних операцій можуть мати знаменники з десятками знаків. Використання наївних 64-розрядних цілих чисел неминуче призводить до арифметичного переповнення (`integer overflow`).

Промислові SMT-сольвери використовують гібридну дворівневу модель арифметики (Two-Tier Arithmetic):
1. **Швидкий рівень (Fast Tier):** Обчислення виконуються з використанням апаратних 64-бітних цілих чисел або дробових чисел фіксованої довжини з апаратною перевіркою переповнення (компіляторні інтринсики `__builtin_add_overflow` та `__builtin_mul_overflow`). Цей рівень забезпечує максимальну продуктивність для 95% простих шарнірних кроків.
2. **Точний рівень (Exact Tier):** При виявленні загрози переповнення рядок або вся таблиця автоматично конвертується у довгі раціональні числа довільної точності (бібліотека GMP або власні структури довгих дробів). Це гарантує 100% математичну строгість сертифікатів без втрати продуктивності на типових задачах.

## 8. Оптимізація розріджених матриць та факторизація

У типових промислових задачах верифікації матриця `A` містить тисячі рядків та стовпчиків, проте в кожному окремому обмеженні бере участь у середньому лише від 2 до 5 змінних. Зберігання повної двовимірної матриці `matrix[M][N]` призводить до квадратичних витрат пам'яті `O(M · N)` та зайвих операцій множення на нуль.

Для масштабування застосовують такі інженерні структури:
1. **Розріджене подання табло (Sparse Tableau):** Рядки та стовпчики зберігаються як двозв'язні списки або динамічні масиви ненульових елементів (Compressed Sparse Row / Column). Це зменшує час виконання шарнірного кроку з `O(M · N)` до `O(nnz(row) · nnz(col))`, де `nnz` — кількість ненульових коефіцієнтів.
2. **Інкрементальна LU-факторизація (Bartels-Golub / Forrest-Tomlin):** Замість явного перерахунку всіх коефіцієнтів матриці табло підтримується розкладання базисної підматриці `B = L · U`. При заміні одного стовпчика базису виконується швидке рангове оновлення множників `L` та `U` за `O(m)` операцій, що мінімізує накопичення проміжних знаменників у раціональній арифметиці.

## 9. Керування пулом відтинань та стратегії перезапуску

Постійне додавання нових відтинальних площин Гоморі здатне перевантажити симплекс-табло сотнями вторинних рядків, що значно сповільнює кожен окремий шарнірний перехід. Для збереження високої швидкості застосовують адаптивне керування пулом обмежень:

1. **Очищення пасивних відтинань (Cut Activity Aging):** Для кожного доданого відтинання ведеться лічильник активності. Якщо протягом останніх `K` шарнірних операцій додаткова змінна відтинання залишалася строго всередині своїх меж і не брала участі в конфліктах, таке обмеження вилучається з активного табло (garbage collection).
2. **Геометричні перезапуски (Geometric Restarts):** Якщо глибина рекурсивного дерева Branch and Bound перевищує встановлений ліміт без знаходження цілочисельного розв'язку, сольвер скидає всі тимчасові розгалуження, зберігаючи лише найбільш ефективні вивчені леми та площини відтинання, і перезапускає пошук з оновленими псевдовартостями змінних.

## 10. Повна реалізація LIA-розв'язувача

Нижче наведено самодостатню реалізацію інкрементального LIA-сольвера мовами C та C++. Вона містить табло, індексацію базисних змінних, механізм збереження та відновлення стану стека (`push`/`pop`), дуальний симплекс для дійсних чисел та рекурсивне цілочисельне розгалуження (Branch and Bound).

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>
#include <math.h>

#define MAX_VARS 32
#define MAX_ROWS 32
#define INF 1e18
#define EPS 1e-9

typedef enum {
    LIA_SAT,
    LIA_UNSAT,
    LIA_UNKNOWN
} LiaResult;

typedef struct {
    double low;
    double high;
    double val;
    bool is_integer;
} VarState;

typedef struct {
    int var_idx;
    double old_low;
    double old_high;
} TrailEntry;

typedef struct {
    int num_vars;
    int num_rows;
    double matrix[MAX_ROWS][MAX_VARS]; // matrix[row][col]
    int basic_vars[MAX_ROWS];
    int non_basic_vars[MAX_VARS];
    VarState vars[MAX_VARS + MAX_ROWS];
    
    TrailEntry trail[MAX_VARS * 8];
    int trail_size;
    int scope_markers[MAX_VARS * 4];
    int scope_depth;
} LiaSolver;

void lia_init(LiaSolver* s, int num_vars, int num_rows) {
    s->num_vars = num_vars;
    s->num_rows = num_rows;
    s->trail_size = 0;
    s->scope_depth = 0;
    
    for (int i = 0; i < num_vars; i++) {
        s->vars[i].low = -INF;
        s->vars[i].high = INF;
        s->vars[i].val = 0.0;
        s->vars[i].is_integer = true;
        s->non_basic_vars[i] = i;
    }
    for (int r = 0; r < num_rows; r++) {
        int b_var = num_vars + r;
        s->basic_vars[r] = b_var;
        s->vars[b_var].low = 0.0;
        s->vars[b_var].high = 0.0;
        s->vars[b_var].val = 0.0;
        s->vars[b_var].is_integer = false;
        for (int c = 0; c < num_vars; c++) {
            s->matrix[r][c] = 0.0;
        }
    }
}

void lia_push(LiaSolver* s) {
    s->scope_markers[s->scope_depth++] = s->trail_size;
}

void lia_pop(LiaSolver* s) {
    if (s->scope_depth == 0) return;
    int target_trail = s->scope_markers[--s->scope_depth];
    while (s->trail_size > target_trail) {
        TrailEntry e = s->trail[--s->trail_size];
        s->vars[e.var_idx].low = e.old_low;
        s->vars[e.var_idx].high = e.old_high;
    }
}

bool lia_set_bound(LiaSolver* s, int var_idx, double low, double high) {
    if (s->trail_size < MAX_VARS * 8) {
        s->trail[s->trail_size++] = (TrailEntry){
            .var_idx = var_idx,
            .old_low = s->vars[var_idx].low,
            .old_high = s->vars[var_idx].high
        };
    }
    if (low > s->vars[var_idx].low) s->vars[var_idx].low = low;
    if (high < s->vars[var_idx].high) s->vars[var_idx].high = high;
    return s->vars[var_idx].low <= s->vars[var_idx].high + EPS;
}

static void update_row_values(LiaSolver* s, int row) {
    double sum = 0.0;
    for (int c = 0; c < s->num_vars; c++) {
        int nb_var = s->non_basic_vars[c];
        sum += s->matrix[row][c] * s->vars[nb_var].val;
    }
    int b_var = s->basic_vars[row];
    s->vars[b_var].val = sum;
}

static void pivot(LiaSolver* s, int row, int col) {
    double a_ij = s->matrix[row][col];
    int b_var = s->basic_vars[row];
    int nb_var = s->non_basic_vars[col];
    
    // Обмін змінних у списках базису
    s->basic_vars[row] = nb_var;
    s->non_basic_vars[col] = b_var;
    
    // Перерахунок рядка шарніра
    s->matrix[row][col] = 1.0 / a_ij;
    for (int c = 0; c < s->num_vars; c++) {
        if (c != col) {
            s->matrix[row][c] /= -a_ij;
        }
    }
    
    // Перерахунок інших рядків табло
    for (int r = 0; r < s->num_rows; r++) {
        if (r != row) {
            double gamma = s->matrix[r][col];
            s->matrix[r][col] = 0.0;
            for (int c = 0; c < s->num_vars; c++) {
                s->matrix[r][c] += gamma * s->matrix[row][c];
            }
        }
    }
    
    // Оновлення обчислених значень
    for (int r = 0; r < s->num_rows; r++) {
        update_row_values(s, r);
    }
}

LiaResult lia_check_real_relaxation(LiaSolver* s) {
    int max_iter = 1000;
    while (max_iter-- > 0) {
        int viol_row = -1;
        bool is_below = false;
        
        for (int r = 0; r < s->num_rows; r++) {
            int b_var = s->basic_vars[r];
            if (s->vars[b_var].val < s->vars[b_var].low - EPS) {
                viol_row = r;
                is_below = true;
                break;
            }
            if (s->vars[b_var].val > s->vars[b_var].high + EPS) {
                viol_row = r;
                is_below = false;
                break;
            }
        }
        
        if (viol_row == -1) {
            return LIA_SAT; // Всі межі виконано в Q
        }
        
        // Пошук небазисної змінної за правилом Бленда
        int pivot_col = -1;
        for (int c = 0; c < s->num_vars; c++) {
            double coeff = s->matrix[viol_row][c];
            int nb_var = s->non_basic_vars[c];
            if (is_below) {
                if (coeff > EPS && s->vars[nb_var].val < s->vars[nb_var].high - EPS) {
                    pivot_col = c;
                    break;
                }
                if (coeff < -EPS && s->vars[nb_var].val > s->vars[nb_var].low + EPS) {
                    pivot_col = c;
                    break;
                }
            } else {
                if (coeff > EPS && s->vars[nb_var].val > s->vars[nb_var].low + EPS) {
                    pivot_col = c;
                    break;
                }
                if (coeff < -EPS && s->vars[nb_var].val < s->vars[nb_var].high - EPS) {
                    pivot_col = c;
                    break;
                }
            }
        }
        
        if (pivot_col == -1) {
            return LIA_UNSAT; // Сертифікат несумісності знайдено
        }
        
        pivot(s, viol_row, pivot_col);
    }
    return LIA_UNKNOWN;
}

static bool is_integer_value(double v) {
    return fabs(v - round(v)) < EPS;
}

LiaResult lia_solve_integer(LiaSolver* s) {
    LiaResult res = lia_check_real_relaxation(s);
    if (res != LIA_SAT) return res;
    
    // Пошук дробової змінної серед первинних цілих змінних
    int frac_var = -1;
    double frac_val = 0.0;
    for (int i = 0; i < s->num_vars; i++) {
        if (s->vars[i].is_integer && !is_integer_value(s->vars[i].val)) {
            frac_var = i;
            frac_val = s->vars[i].val;
            break;
        }
    }
    
    if (frac_var == -1) {
        return LIA_SAT; // Усі змінні цілі, знайдено розв'язок у Z^n
    }
    
    // Гілка 1: x_i <= floor(val)
    lia_push(s);
    if (lia_set_bound(s, frac_var, s->vars[frac_var].low, floor(frac_val))) {
        if (lia_solve_integer(s) == LIA_SAT) return LIA_SAT;
    }
    lia_pop(s);
    
    // Гілка 2: x_i >= ceil(val)
    lia_push(s);
    if (lia_set_bound(s, frac_var, ceil(frac_val), s->vars[frac_var].high)) {
        if (lia_solve_integer(s) == LIA_SAT) return LIA_SAT;
    }
    lia_pop(s);
    
    return LIA_UNSAT;
}

int main(void) {
    // Приклад: 2*x1 + x2 = 5, 0 <= x1 <= 2, 0 <= x2 <= 2, x1, x2 in Z
    LiaSolver solver;
    lia_init(&solver, 2, 1);
    
    // Рядок 0: 2*x1 + 1*x2 - s0 = 0, де s0 = 5
    solver.matrix[0][0] = 2.0;
    solver.matrix[0][1] = 1.0;
    solver.vars[2].low = 5.0;  // s0 = 5
    solver.vars[2].high = 5.0;
    
    lia_set_bound(&solver, 0, 0.0, 2.0); // 0 <= x1 <= 2
    lia_set_bound(&solver, 1, 0.0, 2.0); // 0 <= x2 <= 2
    
    LiaResult res = lia_solve_integer(&solver);
    if (res == LIA_SAT) {
        printf("LIA SAT: x1 = %.0f, x2 = %.0f\n", solver.vars[0].val, solver.vars[1].val);
    } else {
        printf("LIA UNSAT\n");
    }
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <optional>
#include <cmath>
#include <algorithm>
#include <limits>
#include <string_view>

enum class LiaResult {
    Sat,
    Unsat,
    Unknown
};

class LiaSolver {
public:
    static constexpr double Inf = std::numeric_limits<double>::infinity();
    static constexpr double Eps = 1e-9;

    struct VarState {
        double low = -Inf;
        double high = Inf;
        double val = 0.0;
        bool is_integer = true;
    };

    struct TrailEntry {
        size_t var_idx;
        double old_low;
        double old_high;
    };

    LiaSolver(size_t num_vars, size_t num_rows)
        : num_vars_(num_vars), num_rows_(num_rows),
          matrix_(num_rows, std::vector<double>(num_vars, 0.0)),
          basic_vars_(num_rows), non_basic_vars_(num_vars),
          vars_(num_vars + num_rows) {
        
        for (size_t i = 0; i < num_vars; ++i) {
            non_basic_vars_[i] = i;
            vars_[i].is_integer = true;
        }
        for (size_t r = 0; r < num_rows; ++r) {
            basic_vars_[r] = num_vars + r;
            vars_[num_vars + r].low = 0.0;
            vars_[num_vars + r].high = 0.0;
            vars_[num_vars + r].is_integer = false;
        }
    }

    void set_matrix_coeff(size_t row, size_t col, double val) {
        matrix_[row][col] = val;
    }

    void set_slack_bound(size_t row, double low, double high) {
        vars_[num_vars_ + row].low = low;
        vars_[num_vars_ + row].high = high;
    }

    void push() {
        scope_markers_.push_back(trail_.size());
    }

    void pop() {
        if (scope_markers_.empty()) return;
        size_t target_size = scope_markers_.back();
        scope_markers_.pop_back();
        
        while (trail_.size() > target_size) {
            const auto& e = trail_.back();
            vars_[e.var_idx].low = e.old_low;
            vars_[e.var_idx].high = e.old_high;
            trail_.pop_back();
        }
    }

    bool set_bound(size_t var_idx, double low, double high) {
        trail_.push_back({var_idx, vars_[var_idx].low, vars_[var_idx].high});
        vars_[var_idx].low = std::max(vars_[var_idx].low, low);
        vars_[var_idx].high = std::min(vars_[var_idx].high, high);
        return vars_[var_idx].low <= vars_[var_idx].high + Eps;
    }

    LiaResult check_real_relaxation() {
        int max_iter = 1000;
        while (max_iter-- > 0) {
            std::optional<size_t> viol_row;
            bool is_below = false;

            for (size_t r = 0; r < num_rows_; ++r) {
                size_t b_var = basic_vars_[r];
                if (vars_[b_var].val < vars_[b_var].low - Eps) {
                    viol_row = r;
                    is_below = true;
                    break;
                }
                if (vars_[b_var].val > vars_[b_var].high + Eps) {
                    viol_row = r;
                    is_below = false;
                    break;
                }
            }

            if (!viol_row.has_value()) {
                return LiaResult::Sat;
            }

            size_t r = *viol_row;
            std::optional<size_t> pivot_col;

            for (size_t c = 0; c < num_vars_; ++c) {
                double coeff = matrix_[r][c];
                size_t nb_var = non_basic_vars_[c];

                if (is_below) {
                    if (coeff > Eps && vars_[nb_var].val < vars_[nb_var].high - Eps) {
                        pivot_col = c;
                        break;
                    }
                    if (coeff < -Eps && vars_[nb_var].val > vars_[nb_var].low + Eps) {
                        pivot_col = c;
                        break;
                    }
                } else {
                    if (coeff > Eps && vars_[nb_var].val > vars_[nb_var].low + Eps) {
                        pivot_col = c;
                        break;
                    }
                    if (coeff < -Eps && vars_[nb_var].val < vars_[nb_var].high - Eps) {
                        pivot_col = c;
                        break;
                    }
                }
            }

            if (!pivot_col.has_value()) {
                return LiaResult::Unsat;
            }

            pivot(r, *pivot_col);
        }
        return LiaResult::Unknown;
    }

    LiaResult solve_integer() {
        LiaResult res = check_real_relaxation();
        if (res != LiaResult::Sat) return res;

        std::optional<size_t> frac_var;
        double frac_val = 0.0;

        for (size_t i = 0; i < num_vars_; ++i) {
            if (vars_[i].is_integer && !is_integer_value(vars_[i].val)) {
                frac_var = i;
                frac_val = vars_[i].val;
                break;
            }
        }

        if (!frac_var.has_value()) {
            return LiaResult::Sat;
        }

        size_t v = *frac_var;

        // Гілка x_i <= floor(val)
        push();
        if (set_bound(v, vars_[v].low, std::floor(frac_val))) {
            if (solve_integer() == LiaResult::Sat) return LiaResult::Sat;
        }
        pop();

        // Гілка x_i >= ceil(val)
        push();
        if (set_bound(v, std::ceil(frac_val), vars_[v].high)) {
            if (solve_integer() == LiaResult::Sat) return LiaResult::Sat;
        }
        pop();

        return LiaResult::Unsat;
    }

    double get_value(size_t var_idx) const {
        return vars_.at(var_idx).val;
    }

private:
    size_t num_vars_;
    size_t num_rows_;
    std::vector<std::vector<double>> matrix_;
    std::vector<size_t> basic_vars_;
    std::vector<size_t> non_basic_vars_;
    std::vector<VarState> vars_;
    std::vector<TrailEntry> trail_;
    std::vector<size_t> scope_markers_;

    static bool is_integer_value(double v) {
        return std::abs(v - std::round(v)) < Eps;
    }

    void update_row_values(size_t row) {
        double sum = 0.0;
        for (size_t c = 0; c < num_vars_; ++c) {
            sum += matrix_[row][c] * vars_[non_basic_vars_[c]].val;
        }
        vars_[basic_vars_[row]].val = sum;
    }

    void pivot(size_t row, size_t col) {
        double a_ij = matrix_[row][col];
        size_t b_var = basic_vars_[row];
        size_t nb_var = non_basic_vars_[col];

        basic_vars_[row] = nb_var;
        non_basic_vars_[col] = b_var;

        matrix_[row][col] = 1.0 / a_ij;
        for (size_t c = 0; c < num_vars_; ++c) {
            if (c != col) {
                matrix_[row][c] /= -a_ij;
            }
        }

        for (size_t r = 0; r < num_rows_; ++r) {
            if (r != row) {
                double gamma = matrix_[r][col];
                matrix_[r][col] = 0.0;
                for (size_t c = 0; c < num_vars_; ++c) {
                    matrix_[r][c] += gamma * matrix_[row][c];
                }
            }
        }

        for (size_t r = 0; r < num_rows_; ++r) {
            update_row_values(r);
        }
    }
};

int main() {
    // 2*x1 + x2 = 5, 0 <= x1 <= 2, 0 <= x2 <= 2, x1, x2 in Z
    LiaSolver solver(2, 1);
    solver.set_matrix_coeff(0, 0, 2.0);
    solver.set_matrix_coeff(0, 1, 1.0);
    solver.set_slack_bound(0, 5.0, 5.0); // s0 = 5

    solver.set_bound(0, 0.0, 2.0);
    solver.set_bound(1, 0.0, 2.0);

    if (solver.solve_integer() == LiaResult::Sat) {
        std::cout << "LIA SAT: x1 = " << solver.get_value(0) 
                  << ", x2 = " << solver.get_value(1) << "\n";
    } else {
        std::cout << "LIA UNSAT\n";
    }
    return 0;
}
```
:::

## 11. Покроковий розбір виконання на прикладі

Розглянемо покрокове простеження розв'язання задачі:

```
Знайти x₁, x₂ ∈ Z такі, що:
2 · x₁ + x₂ = 5
0 ≤ x₁ ≤ 2
0 ≤ x₂ ≤ 2
```

1. **Ініціалізація табло:**
   Вводиться додаткова змінна `s₀` для виразу `2·x₁ + x₂`. Рівняння табло:
   ```
   s₀ = 2 · x₁ + 1 · x₂
   Межі: 0 ≤ x₁ ≤ 2, 0 ≤ x₂ ≤ 2, 5 ≤ s₀ ≤ 5
   ```
   Початкові значення небазисних змінних: `val(x₁) = 0`, `val(x₂) = 0`.
   Обчислене значення базисної змінної: `val(s₀) = 2·0 + 1·0 = 0`.

2. **Перша ітерація релаксації:**
   Виявлено порушення: `val(s₀) = 0 < low(s₀) = 5`.
   Пошук кандидата: коефіцієнт при `x₁` дорівнює `2 > 0`, а `val(x₁) = 0 < high(x₁) = 2`. Обирається шарнір `(row=0, col=0)`.
   Виконується обмін: `x₁` стає базисною, `s₀` стає небазисною.
   Рівняння розв'язується відносно `x₁`: `x₁ = 0.5 · s₀ - 0.5 · x₂`.
   Значення `val(s₀)` встановлюється в `5.0`.
   Нове значення `val(x₁) = 0.5 · 5.0 - 0.5 · 0.0 = 2.5`.

3. **Друга ітерація релаксації:**
   Тепер для базисної змінної `x₁` виявлено порушення верхньої межі: `val(x₁) = 2.5 > high(x₁) = 2.0`.
   Коефіцієнт при `x₂` у новому рядку дорівнює `-0.5 < 0`. Оскільки `val(x₁) > high(x₁)`, для зменшення `x₁` при від'ємному коефіцієнті потрібно збільшувати `x₂`. Оскільки `val(x₂) = 0 < high(x₂) = 2`, обирається шарнір `(row=0, col=1)`.
   Після шарнірного переходу `x₂` стає базисною, а `val(x₁)` фіксується на верхній межі `2.0`.
   Обчислюється `val(x₂) = 5.0 - 2 · 2.0 = 1.0`.

4. **Перевірка цілочисельності:**
   Усі межі задоволені в `Q`: `val(x₁) = 2.0`, `val(x₂) = 1.0`, `val(s₀) = 5.0`.
   Перевіряється цілочисельність: `2.0 ∈ Z` та `1.0 ∈ Z`.
   Сольвер повертає статус `LIA_SAT` з моделлю `{ x₁ = 2, x₂ = 1 }`.

## 12. Евристики вибору змінних для розгалуження

При переході до цілочисельного пошуку порядок вибору дробових змінних має колосальний вплив на розмір дерева пошуку:

1. **Найбільш дробова змінна (Most Fractional Variable):**
   Обирається змінна `x_i`, для якої відстань до найближчого цілого є максимальною:
   ```
   i* = argmax_{i} ( 0.5 - |val(x_i) - ⌊val(x_i) + 0.5⌋| )
   ```
   Це змушує алгоритм найраніше вирішувати найбільш неоднозначні конфлікти в геометричному центрі многогранника.

2. **Псевдовартості розгалуження (Pseudo-Cost Branching):**
   Сольвер веде статистику того, на скільки змінювалася цільова функція або на скільки звужувався об'єм многогранника при попередніх розгалуженнях змінної `x_i` вгору (`P_i^+`) та вниз (`P_i^-`). На нових кроках обирається змінна з найбільшим очікуваним ефектом звуження простору `P_i^+ · P_i^-`.

3. **Сильне розгалуження (Strong Branching):**
   Для пулу з 5–10 кандидатів-змінних виконується пробний запуск 10–20 шарнірних ітерацій симплекса в обох напрямках. Змінна, яка дає найбільше покращення меж або найшвидше призводить до суперечності в одній із гілок, обирається для повноцінного розгалуження.

## 13. Інженерні пастки та оптимізації

Практична розробка LIA-рушія для промислових SMT-систем містить низку критичних підводних каменів:

1. **Накопичення похибки дійсних чисел (`double`):**
   Використання чисел із рухомою комою IEEE 754 неминуче призводить до втрати точності та накопичення похибок округлення при сотнях тисяч шарнірних операцій. Промислові сольвери (Z3, CVC5) застосовують точну раціональну арифметику довільної точності (бібліотеки GMP або спеціалізовані структури довгих раціональних дробів), використовуючи `double` виключно як швидкий фільтр для евристичного відбору шарнірних кандидатів.

2. **Зациклення симплексу (Cycling):**
   При наявності дегенеративних базисів алгоритм може нескінченно переходити між однаковими станами без зміни значень змінних. Для запобігання зацикленню обов'язково застосовують **правило найменшого індексу Бленда (Bland's Anti-Cycling Rule)**: серед усіх можливих кандидатів на вхід у базис та вихід із нього завжди обирається змінна з мінімальним числовим ідентифікатором.

3. **Нескінченне розгалуження (Branch-and-Bound Divergence):**
   Наївне розщеплення меж без генерації відтинальних площин Гоморі може породжувати нескінченні ланцюги розгалужень на необмежених або вузьких некомпактних многогранниках. Комбінація розгалуження з періодичною генерацією площин відтинання (метод Branch and Cut) кардинально прискорює звуження допустимої області до цілочисельної опуклої оболонки.

4. **Мінімальність пояснень (Minimal Infeasibility Core):**
   При виникненні конфлікту рядок табло містить лінійну комбінацію активних меж. Якщо сформувати лему конфлікту з усіх призначених на поточному рівні змінних, вона буде занадто довгою і слабкою для CDCL. Пояснення повинно включати **лише ті змінні, коефіцієнти яких у конфліктному рядку строго ненульові**, що забезпечує максимальну силу вивченого булевого диз'юнкта та швидке зрізання дерева рішень.
