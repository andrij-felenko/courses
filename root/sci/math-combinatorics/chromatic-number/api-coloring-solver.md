# Інтерфейс бібліотеки розфарбування графів

Розподіл обмежених ресурсів у компіляторах, планувальниках обчислювальних кластерів та системах проєктування бездротових мереж зводиться до задачі вершинного розфарбування графа несумісності. Практичні застосування висувають суперечливі вимоги: бекенд компілятора потребує миттєвої поліноміальної евристики з гарантованим часом роботи для тисяч функцій, тоді як планувальник телекомунікаційних частот вимагає суворого глобального оптимуму, залучаючи точні комбінаторні методи, цілочисельне лінійне програмування та генерацію стовпчиків у просторі експоненціальної кількості конфігурацій.

Програмний інтерфейс розв'язувача розфарбування графів уніфікує доступ до спектра алгоритмічних рушіїв: швидких жадібних евристик DSATUR, точного пошуку з поверненням на основі відсікань, цілочисельного лінійного програмування (ILP) та декомпозиційного методу Branch-and-Price (колоночна генерація). Бібліотека надає детерміновані структури даних, прозорі інваріанти володіння пам'яттю, машинно-верифіковані сертифікати оптимальності та стандартизовані інтерфейси серіалізації DIMACS і JSON.

## Архітектура та моделі представлення графів

Комбінаторні розв'язувачі критично чутливі до просторової локальності даних та накладних витрат на виділення динамічної пам'яті. У задачах розфарбування понад вісімдесят відсотків процесорного часу витрачається на внутрішні цикли перевірки суміжності вершин, обчислення перетину множин сусідів та оновлення динамічних масок доступних кольорів. Бібліотека підтримує дві моделі внутрішнього представлення топології, оптимізовані під різні класи щільності графів:

1. **Щільна бітова матриця суміжності (Bitset Matrix):** для графів із кількістю вершин до 1024 суміжність зберігається у вигляді упакованих 64-бітних машинних слів (`uint64_t`). Матриця вирівнюється в пам'яті за 64-байтними межами кеш-ліній процесора, що унеможливлює розщеплені звернення (split loads). Перевірка наявності ребра між вершинами `u` та `v` зводиться до побітового зсуву та маскування `(adj[u][v / 64] & (1ULL << (v % 64))) != 0`. Обчислення спільних сусідів виконується векторними інструкціями побітового «І» (`AND`), а підрахунок ступенів насиченості — апаратними інструкціями підрахунку одиничних бітів (`POPCNT` в архітектурах x86-64 або `CNT` в ARM Neon), що виконуються за один такт процесора.
2. **Стиснений розріджений рядок (Compressed Sparse Row / CSR):** для великомасштабних розріджених графів (понад 10000 вершин і низька щільність ребер, типових для соціальних мереж чи веб-графів) матриця вимагала б сотень мегабайтів переважно нульової пам'яті. Модель CSR зберігає суміжність у двох неперервних масивах: масиві зміщень рядків `row_ptr` розміром `|V| + 1` та масиві цільових вершин `col_idx` розміром `2|E|`. Це усуває вказівникову фрагментацію стандартних списків суміжності та гарантує послідовне лінійне читання під час обходу околу вершини.

Крім базової топології ребер, дескриптор графа підтримує дві критичні спеціалізації:
- **Попередньо зафіксовані кольори (Pinned Colors):** масив попередньо призначених кольорових міток для моделювання апаратних регістрів цільової архітектури мікропроцесора. В архітектурах x86-64 або ARM певні змінні зобов'язані знаходитися у фіксованих фізичних регістрах під час виклику підпрограм відповідно до конвенцій ABI (наприклад, `RDI`, `RSI`, `RDX` для передачі перших аргументів або `RAX` для повернення значення). Фіксація кольору вилучає ці значення з вільного вибору та накладає жорсткі граничні умови на сусідні вершини.
- **Ваги вершин (Vertex Weights):** дійсні або цілочисельні ваги, що використовуються в зваженому розфарбуванні (weighted coloring) та в підзадачах генерації стовпчиків, де кожна вершина отримує двоїсту ціну від розв'язання релаксованої головної задачі.

```
   ┌─────────────────────────────────────────────────────────────────┐
   │                        ColoringGraph                            │
   │  - Кількість вершин:       num_vertices                         │
   │  - Кількість ребер:        num_edges                            │
   │  - Бітові маски суміжності: adj_matrix[V][(V + 63) / 64]        │
   │  - Зафіксовані кольори:    pinned_colors[V]                     │
   │  - Ваги вершин:            vertex_weights[V]                    │
   └────────────────────────────────┬────────────────────────────────┘
                                    │
            ┌───────────────────────┴───────────────────────┐
            ▼                                               ▼
   ┌──────────────────────────────────┐   ┌──────────────────────────────────┐
   │          ColoringConfig          │   │       ColoringDiagnostics        │
   │ - engine (DSATUR/ILP/B&P)        │   │ - last_error (ErrorCode)         │
   │ - time_limit_ms                  │   │ - error_message[256]             │
   │ - lower_bound_hint               │   │ - conflict_u, conflict_v         │
   │ - target_k / upper_bound         │   │ - peak_memory_bytes              │
   │ - symmetry_breaking_level        │   │ - simplex_iterations             │
   │ - ryan_foster_branching_rule     │   │ - generated_columns_count        │
   │ - kempe_opt_passes               │   │ - explored_nodes_count           │
   └────────────────┬─────────────────┘   └──────────────────────────────────┘
                    │
                    ▼
   ┌──────────────────────────────────┐
   │          ColoringResult          │
   │ - status (OPTIMAL/FEASIBLE/...)  │
   │ - chromatic_number (k)           │
   │ - colors[V] (0 .. k-1)           │
   │ - lower_bound, upper_bound       │
   │ - elapsed_us (тривалість)        │
   │ - certificate (CLIQUE/TREE/DUAL) │
   └──────────────────────────────────┘
```

## Алгоритмічні рушії та математичні контракти

Бібліотека інкапсулює чотири взаємодоповнювальні стратегії пошуку. Кожен рушій володіє чітко окресленою обчислювальною складністю, гарантіями якості та структурою внутрішнього стану.

### Рушій DSATUR (евристичний та точний пошук)

Алгоритм ступеня насиченості Даніеля Брелаза динамічно обирає для розфарбування ту вершину, яка має максимальну кількість різних кольорів серед своїх сусідів (`deg_sat(v)`). Якщо кілька вершин мають однаковий найвищий ступінь насиченості, правило розриву нічиєї (tie-breaker) обирає вершину з найбільшим степенем у нерозфарбованому підграфі.

- **Евристичний режим (`COLORING_ENGINE_GREEDY_DSATUR`):** виконує єдиний детермінований жадібний прохід. Для підтримки максимального елемента використовується масив бінарних куп або багаторівневих списків відер (bucket queues) за значенням насиченості. Оновлення насиченості сусідів після розфарбування вершини `v` виконується за час `O(deg(v))`. Загальна асимптотична складність становить `O(|V|²)` для щільних графів або `O((|V| + |E|) log |V|)` для розріджених. Евристика забезпечує якісну початкову верхню межу `k_upper` для всіх наступних точних методів.
- **Точний пошук Branch-and-Bound (`COLORING_ENGINE_EXACT_DSATUR`):** будує повне дерево комбінаторного перебору. Перед стартом рекурсивного пошуку виконується процедура виділення максимальної початкової кліки `K_p` (за допомогою алгоритму Брона — Кербоша з відсіканнями або жадібного пошуку кліки максимального степеня). Вершини цієї кліки фарбуються кольорами `1, 2, ..., p` один раз і залишаються фіксованими на всіх гілках пошуку. Це усуває `p!` ізоморфних перестановок кольорів на верхніх поверхах дерева пошуку.
- **Відсікання за межею (Pruning):** якщо на поточному кроці ступінь насиченості вершини досягає або перевищує поточну глобальну найкращу верхню межу `k_best`, гілка негайно відсікається. Якщо в процесі пошуку знайдено розфарбування з кількістю кольорів, що точно дорівнює розміру початкової кліки `k == p`, процедура негайно зупиняється з математичним доведенням оптимальності `χ(G) = p`.

### Рушій цілочисельного лінійного програмування (ILP)

Для задач, де граф має помірну кількість вершин (до 100–200) і високу щільність ребер, задача формулюється як бінарна оптимізаційна модель математичного програмування на множині вершин `V` та палітрі потенційних кольорів `C = {1, 2, ..., K}`, де `K` — початкова верхня межа від DSATUR.

Змінні моделі:
- `w_c ∈ {0, 1}`: булева змінна активації кольору `c` (дорівнює 1, якщо хоча б одна вершина графа отримала колір `c`);
- `x_{v,c} ∈ {0, 1}`: булева змінна призначення кольору `c` вершині `v`.

Математична формулювання задачі:

```
Мінімізувати:   ∑_{c=1}^K w_c

За обмежень:
(1) Обов'язковість призначення рівно одного кольору:
    ∑_{c=1}^K x_{v,c} = 1                    ∀ v ∈ V

(2) Заборона однакового кольору на кінцях кожного ребра:
    x_{u,c} + x_{v,c} ≤ w_c                 ∀ (u, v) ∈ E,  ∀ c ∈ {1, ..., K}

(3) Усунення симетрії палітри (Symmetry Breaking Constraints):
    w_c ≥ w_{c+1}                            ∀ c ∈ {1, ..., K - 1}
    x_{v,c} = 0                              ∀ c > v + 1
```

Без обмежень симетрії простір допустимих розв'язків містить `K!` ідентичних дзеркальних відображень кожного розфарбування, що змушує стандартні LP/MIP розв'язувачі (Simplex / Branch-and-Cut) багаторазово досліджувати однакові гілки перебору. Обмеження `w_c ≥ w_{c+1}` гарантують, що колір `c+1` не може використовуватися раніше, ніж колір `c`. Обмеження `x_{v,c} = 0` для `c > v + 1` фіксує, що перша вершина графа може отримати винятково колір 1, друга — колір 1 або 2, третя — колір 1, 2 або 3, тощо.

Для посилення LP-релаксації до моделі динамічно додаються **клікові нерівності (clique cuts)**: для будь-якої кліки `Q ⊆ V` діє обмеження `∑_{v ∈ Q} x_{v,c} ≤ w_c`. Оскільки кожна кліка може містити щонайбільше одну вершину кольору `c`, сума змінних призначення всередині кліки не перевищує 1, що значно звужує дробовий многогранник релаксації.

### Рушій Branch-and-Price та генерація стовпчиків

Коли кількість вершин графа перевищує кілька сотень, пряма модель ILP стає непридатною: LP-релаксація стає надто слабкою (дробові значення `w_c` часто спадають до малих часток), а кількість змінних `O(|V| · K)` та обмежень `O(|E| · K)` перевантажує симплекс-таблицю.

Для розв'язання таких задач бібліотека використовує декомпозицію Данціга — Вульфа, яка перетворює задачу розфарбування на задачу покриття множинами (Set Covering Formulation).

Нехай `𝓘 = {S₁, S₂, ..., S_M}` — множина всіх можливих незалежних множин графа `G`. Кількість незалежних множин `M` є експоненціальною величиною від кількості вершин. Для кожної незалежної множини `Sⱼ ∈ 𝓘` вводиться бінарна змінна `λⱼ ∈ {0, 1}`, яка показує, чи вибрано множину `Sⱼ` як один із кольорових класів підсумкового розфарбування.

Головна задача (Master Problem):

```
Мінімізувати:   ∑_{j=1}^M λⱼ

За обмежень:
    ∑_{j: v ∈ Sⱼ} λⱼ ≥ 1                     ∀ v ∈ V
    λⱼ ∈ {0, 1}                              ∀ j ∈ {1, ..., M}
```

Оскільки виписати всі `M` стовпчиків у пам'яті комп'ютера неможливо, алгоритм ініціалізує **обмежену головну задачу (Restricted Master Problem, RMP)**, що містить лише кілька початкових стовпчиків, сформованих жадібними проходами DSATUR та розбиттям вершин на окремі одномісні класи.

На кожній ітерації алгоритму RMP розв'язується як неперервна задача лінійного програмування за допомогою двоїстого симплекс-методу. Вектор двоїстого розв'язку визначає ціни вершинних обмежень `π_v ≥ 0` для кожної вершини `v ∈ V`.

Зведена вартість (reduced cost) потенційного нового стовпчика, що кодує незалежну множину `S`, визначається формулою лінійного програмування:

```
c̄_S = 1 - ∑_{v ∈ S} π_v
```

Новий стовпчик може покращити поточний план головної задачі тоді й лише тоді, коли його зведена вартість є строго від'ємною: `c̄_S < 0`, що еквівалентно умові `∑_{v ∈ S} π_v > 1`.

#### Підзадача ціноутворення стовпчиків (Pricing Subproblem)

Пошук найвигіднішого стовпчика формулюється як знаходження незалежної множини `S`, що мінімізує `c̄_S`, тобто максимізує суму цін `∑_{v ∈ S} π_v`. Це математично еквівалентно задачі про **найбільшу зважену незалежну множину (Maximum Weight Independent Set, MWIS)** на графі `G` з вагами вершин `w_v = π_v`:

```
Максимізувати:   ∑_{v ∈ V} π_v · y_v

За обмежень:
    y_u + y_v ≤ 1                            ∀ (u, v) ∈ E
    y_v ∈ {0, 1}                             ∀ v ∈ V
```

Для розв'язання підзадачі ціноутворення бібліотека реалізує багаторівневий конвеєр:
1. **Швидкий евристичний фільтр (GRASP / Heuristic Pricing):** швидка жадібна евристика на основі бітових масок намагається знайти незалежну множину з вагою `> 1` за мікросекунди. Якщо евристика знаходить кілька таких незалежних множин, вони пачкою додаються до RMP без виклику точного алгоритму.
2. **Точний розв'язувач MWIS:** якщо евристика не знаходить жодного стовпчика з від'ємною зведеною вартістю, викликається точний алгоритм гілок та меж для пошуку кліки в доповненні графа. Якщо точний оптимум MWIS має вагу `≤ 1`, це слугує строгим математичним доказом того, що жодного стовпчика з `c̄_S < 0` більше не існує, і поточний розв'язок LP-релаксації є строго оптимальним.

#### Стабілізація двоїстих цін

Класична генерація стовпчиків страждає від проблеми «хитання» двоїстих змінних (yo-yo effect або degeneracy): двоїсті ціни `π_v` різко змінюються між ітераціями, що призводить до повільної збіжності (хвостового ефекту). Бібліотека застосовує техніку **коробкової стабілізації (Box Stabilization / Smoothing)**: двоїсті змінні обмежуються околом попередніх стабільних розв'язків `[π̂_v - ε, π̂_v + ε]`, що прискорює збіжність генерації стовпчиків у 3–5 разів на щільних графах.

### Схема розгалуження Раяна — Фостера (Ryan-Foster Branching)

Якщо розв'язок LP-релаксації головної задачі містить дробові змінні `λⱼ`, декомпозиція вимагає побудови дерева розгалужень (Branch-and-Bound над Branch-and-Price).

Традиційне розгалуження за значенням змінної (`λⱼ = 0` або `λⱼ = 1`) виявляється непридатним: фіксація `λⱼ = 0` вимагає заборони генерації конкретної незалежної множини `Sⱼ` на всіх наступних ітераціях. Це означає, що підзадача ціноутворення MWIS отримує додаткові складні обмеження виключення множин, втрачає свою графову структуру та стає практично нерозв'язною.

Щоб зберегти графову структуру задачі ціноутворення, бібліотека використовує схему розгалуження Раяна — Фостера:
1. Серед усіх пар вершин обчислюється матриця сумісної присутності у стовпчиках:
   ```
   P(u, v) = ∑_{j: u ∈ Sⱼ, v ∈ Sⱼ} λⱼ
   ```
2. Знаходиться пара несуміжних вершин `(u, v) ∉ E`, значення `P(u, v)` для якої є найближчим до 0.5 (максимальна невизначеність).
3. Створюються дві дочірні гілки:
   - **Гілка «ОДНАКОВИЙ КОЛІР» (SAME / CONTRACT):** вершини `u` та `v` зобов'язані отримати один і той самий колір. Вершини `u` та `v` стягуються в єдину супер-вершину `uv`, сусідами якої стає об'єднання `N(u) ∪ N(v)`. Усі наявні стовпчики в RMP, які містили рівно одну з вершин `u` чи `v`, оголошуються недопустимими та вилучаються.
   - **Гілка «РІЗНІ КОЛЬОРИ» (DIFFERENT / EDGE):** вершини `u` та `v` зобов'язані мати різні кольори. До графа додається нове фіктивне ребро `(u, v)`. Усі наявні стовпчики в RMP, які містили обидві вершини `u` та `v` одночасно, вилучаються.

Обидві операції (стягування пари вершин або додавання нового ребра) трансформують вихідний граф в інший простий граф. Завдяки цьому підзадача ціноутворення MWIS залишається стандартною задачею про незалежну множину над модифікованим графом без жодних додаткових штучних обмежень.

## Інваріанти, перед- та післяумови

Надійність роботи бібліотеки гарантується системними контрактами на кожному етапі життєвого циклу обчислень:

### Передумови (Preconditions)
- **Коректність індексів:** кількість вершин `num_vertices` строго більша за 0 та не перевищує лімітів обраної моделі (1024 для щільної бітової матриці, `2³¹ - 1` для CSR). Усі індекси вершин у викликах належать діапазону `[0, num_vertices - 1]`.
- **Простота графа:** граф є простим, неорієнтованим і не містить кратних ребер та петель `(v, v)`. Матриця суміжності симетрична: `adj(u, v) == adj(v, u)`.
- **Несуперечливість фіксації:** якщо задано масив `pinned_colors`, для будь-якого ребра `(u, v) ∈ E` виконується умова: `pinned_colors[u] == COLORING_UNCOLORED || pinned_colors[v] == COLORING_UNCOLORED || pinned_colors[u] != pinned_colors[v]`. Спроба передати суміжні вершини з однаковим зафіксованим кольором повертає статус `COLORING_ERR_PINNED_CONFLICT`.
- **Валідність вказівників:** усі вхідні вказівники на структури графа, конфігурації та діагностичні звіти є ненульовими (`non-null`).

### Післяумови (Postconditions)
- **Повне розфарбування:** кожній вершині `v ∈ [0, num_vertices - 1]` присвоєно номер кольору `colors[v] ∈ [0, chromatic_number - 1]`. Значення `COLORING_UNCOLORED` у вихідному масиві відсутні.
- **Відсутність колізій:** для будь-якої пари суміжних вершин `(u, v) ∈ E` гарантується, що `colors[u] != colors[v]`.
- **Збереження фіксації:** для кожної вершини з `pinned_colors[v] != COLORING_UNCOLORED` гарантується `colors[v] == pinned_colors[v]`.
- **Оптимальність сертифіката:** у разі повернення статусу `COLORING_STATUS_OPTIMAL` сертифікат гарантує строгу рівність `lower_bound == chromatic_number == upper_bound`.

### Потокобезпечність (Thread-Safety) та ізоляція пам'яті
- Структура `ColoringGraph` після побудови є строго незмінною (read-only / immutable). Будь-яка кількість паралельних потоків виконання може одночасно запускати розв'язувачі над одним спільним екземпляром `ColoringGraph` без взаємних блокувань (lock-free read).
- Усі змінні стани, симплекс-таблиці, буфери генерації стовпчиків та списки дерева пошуку виділяються у внутрішній арені пам'яті (Memory Arena), ізольованій для конкретного виклику `coloring_solve()`.
- Бібліотека не містить глобальних змінних та статичних буферів стану. Генератор псевдовипадкових чисел для стохастичного відбору розгалужень ініціалізується з поля `config->random_seed` у локальному контексті потоку.

## Формати серіалізації: DIMACS та JSON

Бібліотека забезпечує стандартизовані інтерфейси для імпорту тестових топологій та експорту результатів розв'язання.

### Формат DIMACS (.col / .edge)

Формат DIMACS є загальноприйнятим стандартом у міжнародних комбінаторних дослідженнях та бенчмарках (наприклад, тестовий набір COLOR02/03/04). Структура файлу визначається такими типами рядків:
- `c [текст]` — коментарі, метадані та описи походження графа;
- `p edge [вершин] [ребер]` — заголовок задачі з указанням кількості вершин `|V|` та ребер `|E|`;
- `e [u] [v]` — ребро між вершинами `u` та `v`.

```
c Граф Грьотча (Mycielski M4)
c Вершин: 11, Ребер: 20, Хроматичне число: 4
p edge 11 20
e 1 2
e 2 3
e 3 4
e 4 5
e 5 1
e 1 7
e 2 8
e 3 9
e 4 10
e 5 6
e 6 8
e 6 9
e 7 9
e 7 10
e 8 10
e 6 11
e 7 11
e 8 11
e 9 11
e 10 11
```

*Примітка щодо індексації:* файли DIMACS використовують традиційну для математики 1-індексацію вершин (`1 .. |V|`). Функції імпорту `coloring_import_dimacs()` та експорту `coloring_export_dimacs()` автоматично транслюють їх у внутрішню 0-індексацію (`0 .. |V| - 1`) та навпаки.

### Схема JSON для конфігурацій та звітів

Для хмарної мікросервісної архітектури, CI/CD-тестування компіляторних оптимізацій та веб-візуалізацій розроблено формат JSON-обміну:

```json
{
  "graph": {
    "num_vertices": 11,
    "edges": [
      [0, 1], [1, 2], [2, 3], [3, 4], [4, 0],
      [0, 6], [1, 7], [2, 8], [3, 9], [4, 5],
      [5, 7], [5, 8], [6, 8], [6, 9], [7, 9],
      [5, 10], [6, 10], [7, 10], [8, 10], [9, 10]
    ],
    "pinned": {
      "0": 0,
      "1": 1
    }
  },
  "config": {
    "engine": "BRANCH_AND_PRICE",
    "time_limit_ms": 5000,
    "lower_bound_hint": 3,
    "symmetry_breaking_level": 2,
    "branching_rule": "RYAN_FOSTER"
  },
  "result": {
    "status": "OPTIMAL",
    "chromatic_number": 4,
    "colors": [0, 1, 0, 1, 2, 3, 2, 3, 2, 0, 1],
    "bounds": {
      "lower": 4,
      "upper": 4,
      "gap": 0.0
    },
    "certificate": {
      "type": "DUAL_BOUND_EXHAUSTION",
      "clique_size": 2,
      "explored_nodes": 7,
      "generated_columns": 34
    },
    "metrics": {
      "elapsed_us": 4120,
      "peak_memory_bytes": 65536
    }
  }
}
```

## Коди помилок та діагностика

Усі функції інтерфейсу повертають строгі значення переліку `ColoringErrorCode`. Повний перелік кодів помилок та діагностичних статусів:

| Код помилки | Числове значення | Опис причини виникнення |
|---|---|---|
| `COLORING_OK` | 0 | Операцію виконано успішно без зауважень |
| `COLORING_ERR_INVALID_ARGUMENT` | -1 | Передано некоректний або нульовий вказівник на структуру |
| `COLORING_ERR_VERTEX_OUT_OF_BOUNDS` | -2 | Індекс вершини виходить за межі діапазону `[0, num_vertices - 1]` |
| `COLORING_ERR_SELF_LOOP_DETECTED` | -3 | Спроба додати петлю `(v, v)` у неорієнтований граф |
| `COLORING_ERR_PINNED_CONFLICT` | -4 | Конфлікт попередньо зафіксованих кольорів між суміжними вершинами |
| `COLORING_ERR_OUT_OF_MEMORY` | -5 | Перевищено ліміт виділення оперативної пам'яті `memory_limit_bytes` |
| `COLORING_ERR_TIMEOUT` | -6 | Перевищено максимальний час виконання `time_limit_ms` |
| `COLORING_ERR_TARGET_INFEASIBLE` | -7 | Доведено неможливість розфарбування в цільову кількість кольорів `target_k` |
| `COLORING_ERR_INVALID_CERTIFICATE` | -8 | Верифікатор виявив некоректність розфарбування або колізію на ребрі |
| `COLORING_ERR_IO_FAILURE` | -9 | Помилка читання або запису файлу DIMACS або JSON на диску |
| `COLORING_ERR_SOLVER_DIVERGED` | -10 | Числова нестабільність або зациклення двоїстого симплекс-методу |

У разі виникнення помилки структура `ColoringDiagnostics` заповнюється детальним текстовим повідомленням, координатами конфліктного ребра `(conflict_u, conflict_v)` та метриками пікового використання пам'яті.

## Специфікація інтерфейсу мовами C та C++

Нижче наведено повні контракти заголовкових файлів мовами C (стандарт C99) та C++ (стандарт C++20).

:::tabs
```c
#ifndef COLORING_SOLVER_H
#define COLORING_SOLVER_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

#define COLORING_MAX_VERTICES_DENSE 1024
#define COLORING_UNCOLORED (-1)

typedef enum {
    COLORING_OK = 0,
    COLORING_ERR_INVALID_ARGUMENT = -1,
    COLORING_ERR_VERTEX_OUT_OF_BOUNDS = -2,
    COLORING_ERR_SELF_LOOP_DETECTED = -3,
    COLORING_ERR_PINNED_CONFLICT = -4,
    COLORING_ERR_OUT_OF_MEMORY = -5,
    COLORING_ERR_TIMEOUT = -6,
    COLORING_ERR_TARGET_INFEASIBLE = -7,
    COLORING_ERR_INVALID_CERTIFICATE = -8,
    COLORING_ERR_IO_FAILURE = -9,
    COLORING_ERR_SOLVER_DIVERGED = -10
} ColoringErrorCode;

typedef enum {
    COLORING_STATUS_UNSOLVED = 0,
    COLORING_STATUS_OPTIMAL = 1,
    COLORING_STATUS_FEASIBLE = 2,
    COLORING_STATUS_INFEASIBLE = 3,
    COLORING_STATUS_TIMEOUT = 4
} ColoringStatus;

typedef enum {
    COLORING_ENGINE_GREEDY_DSATUR = 0,
    COLORING_ENGINE_EXACT_DSATUR = 1,
    COLORING_ENGINE_ILP = 2,
    COLORING_ENGINE_BRANCH_AND_PRICE = 3
} ColoringEngine;

typedef enum {
    COLORING_CERT_NONE = 0,
    COLORING_CERT_MAX_CLIQUE = 1,
    COLORING_CERT_EXHAUSTIVE_TREE = 2,
    COLORING_CERT_DUAL_BOUND_EXHAUSTION = 3
} ColoringCertType;

/* Щільна структура графа на бітових масках */
typedef struct {
    int32_t num_vertices;
    int32_t num_edges;
    uint64_t* adj_matrix;        /* Розмір: num_vertices * ((num_vertices + 63) / 64) */
    int32_t* pinned_colors;      /* Розмір: num_vertices, за замовчуванням COLORING_UNCOLORED */
    double* vertex_weights;      /* Ваги вершин для зваженого розфарбування */
} ColoringGraph;

/* Конфігурація параметрів розв'язувача */
typedef struct {
    ColoringEngine engine;
    uint32_t time_limit_ms;
    int32_t lower_bound_hint;
    int32_t upper_bound_target;
    int32_t symmetry_breaking_level;
    bool enable_kempe_pass;
    uint32_t random_seed;
    size_t memory_limit_bytes;
} ColoringConfig;

/* Сертифікат розфарбування та метрики */
typedef struct {
    ColoringCertType cert_type;
    int32_t cert_size;
    int32_t* cert_vertices;      /* Наприклад, індекси вершин знайденої кліки K_k */
    uint64_t explored_nodes;
    uint64_t generated_columns;
    uint64_t simplex_iterations;
} ColoringCertificate;

/* Структура підсумкового результату */
typedef struct {
    ColoringStatus status;
    int32_t chromatic_number;
    int32_t* colors;             /* Розмір: num_vertices, значення 0 .. chromatic_number - 1 */
    int32_t lower_bound;
    int32_t upper_bound;
    uint64_t elapsed_us;
    ColoringCertificate certificate;
} ColoringResult;

/* Діагностичний звіт */
typedef struct {
    ColoringErrorCode last_error;
    char error_message[256];
    int32_t conflict_u;
    int32_t conflict_v;
    size_t peak_memory_bytes;
} ColoringDiagnostics;

/* Керування життєвим циклом графа */
ColoringErrorCode coloring_graph_create(int32_t num_vertices, ColoringGraph** out_graph);
void coloring_graph_free(ColoringGraph* graph);
ColoringErrorCode coloring_graph_add_edge(ColoringGraph* graph, int32_t u, int32_t v);
ColoringErrorCode coloring_graph_pin_color(ColoringGraph* graph, int32_t v, int32_t color);

/* Ініціалізація стандартної конфігурації */
void coloring_config_default(ColoringConfig* config);

/* Основний виклик розв'язувача */
ColoringErrorCode coloring_solve(
    const ColoringGraph* graph,
    const ColoringConfig* config,
    ColoringResult* result,
    ColoringDiagnostics* diag
);

/* Верифікація коректності та сертифіката */
ColoringErrorCode coloring_verify_result(
    const ColoringGraph* graph,
    const ColoringResult* result,
    ColoringDiagnostics* diag
);

/* Звільнення ресурсів результату */
void coloring_result_free(ColoringResult* result);

/* Серіалізація та десеріалізація */
ColoringErrorCode coloring_import_dimacs(const char* filepath, ColoringGraph** out_graph);
ColoringErrorCode coloring_export_dimacs(const char* filepath, const ColoringGraph* graph);
ColoringErrorCode coloring_export_json(const char* filepath, const ColoringGraph* graph, const ColoringResult* result);

#ifdef __cplusplus
}
#endif

#endif /* COLORING_SOLVER_H */
```
```cpp
#ifndef COLORING_SOLVER_HPP
#define COLORING_SOLVER_HPP

#include <cstdint>
#include <cstddef>
#include <string>
#include <string_view>
#include <vector>
#include <span>
#include <memory>
#include <expected>
#include <optional>
#include <chrono>

namespace coloring {

enum class ErrorCode : int32_t {
    Ok = 0,
    InvalidArgument = -1,
    VertexOutOfBounds = -2,
    SelfLoopDetected = -3,
    PinnedConflict = -4,
    OutOfMemory = -5,
    Timeout = -6,
    TargetInfeasible = -7,
    InvalidCertificate = -8,
    IoFailure = -9,
    SolverDiverged = -10
};

enum class Status : int32_t {
    Unsolved = 0,
    Optimal = 1,
    Feasible = 2,
    Infeasible = 3,
    Timeout = 4
};

enum class Engine : int32_t {
    GreedyDsatur = 0,
    ExactDsatur = 1,
    Ilp = 2,
    BranchAndPrice = 3
};

enum class CertificateType : int32_t {
    None = 0,
    MaxClique = 1,
    ExhaustiveTree = 2,
    DualBoundExhaustion = 3
};

struct Certificate {
    CertificateType type{CertificateType::None};
    std::vector<int32_t> vertices;
    uint64_t explored_nodes{0};
    uint64_t generated_columns{0};
    uint64_t simplex_iterations{0};
};

struct Result {
    Status status{Status::Unsolved};
    int32_t chromatic_number{0};
    std::vector<int32_t> colors;
    int32_t lower_bound{0};
    int32_t upper_bound{0};
    std::chrono::microseconds elapsed{0};
    Certificate certificate;
};

struct Diagnostics {
    ErrorCode last_error{ErrorCode::Ok};
    std::string message;
    int32_t conflict_u{-1};
    int32_t conflict_v{-1};
    size_t peak_memory_bytes{0};
};

struct SolverConfig {
    Engine engine{Engine::ExactDsatur};
    std::chrono::milliseconds time_limit{5000};
    std::optional<int32_t> lower_bound_hint;
    std::optional<int32_t> upper_bound_target;
    int32_t symmetry_breaking_level{2};
    bool enable_kempe_pass{true};
    uint32_t random_seed{42};
    size_t memory_limit_bytes{1024 * 1024 * 1024}; /* 1 ГБ */
};

class Graph {
public:
    explicit Graph(int32_t num_vertices);
    ~Graph() = default;

    Graph(const Graph&) = default;
    Graph& operator=(const Graph&) = default;
    Graph(Graph&&) noexcept = default;
    Graph& operator=(Graph&&) noexcept = default;

    [[nodiscard]] int32_t vertex_count() const noexcept { return num_vertices_; }
    [[nodiscard]] int32_t edge_count() const noexcept { return num_edges_; }

    [[nodiscard]] std::expected<void, ErrorCode> add_edge(int32_t u, int32_t v) noexcept;
    [[nodiscard]] std::expected<void, ErrorCode> pin_color(int32_t v, int32_t color) noexcept;
    [[nodiscard]] bool has_edge(int32_t u, int32_t v) const noexcept;
    [[nodiscard]] std::optional<int32_t> get_pinned_color(int32_t v) const noexcept;

    [[nodiscard]] std::span<const uint64_t> adjacency_row(int32_t v) const noexcept;

private:
    int32_t num_vertices_{0};
    int32_t num_edges_{0};
    size_t row_words_{0};
    std::vector<uint64_t> adj_matrix_;
    std::vector<int32_t> pinned_colors_;
};

class Solver {
public:
    explicit Solver(SolverConfig config = SolverConfig{});
    ~Solver() = default;

    [[nodiscard]] std::expected<Result, Diagnostics> solve(const Graph& graph) const;
    [[nodiscard]] static std::expected<void, Diagnostics> verify(const Graph& graph, const Result& result);

    [[nodiscard]] static std::expected<Graph, Diagnostics> import_dimacs(std::string_view filepath);
    [[nodiscard]] static std::expected<void, Diagnostics> export_dimacs(std::string_view filepath, const Graph& graph);
    [[nodiscard]] static std::expected<void, Diagnostics> export_json(
        std::string_view filepath,
        const Graph& graph,
        const Result& result
    );

private:
    SolverConfig config_;
};

} // namespace coloring

#endif /* COLORING_SOLVER_HPP */
```
:::

## Повний приклад використання: розв'язання на графі Грьотча

Нижче наведено закінчений робочий приклад: створення графа Грьотча (11 вершин, 20 ребер, без трикутників, хроматичне число `χ = 4`), конфігурація рушія Branch-and-Price з генерацією стовпчиків, виконання розв'язання, перевірка сертифіката та експорт звіту.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "coloring_solver.h"

int main(void) {
    ColoringGraph* graph = NULL;
    ColoringErrorCode err = coloring_graph_create(11, &graph);
    if (err != COLORING_OK) {
        fprintf(stderr, "Помилка виділення пам'яті для графа: %d\n", err);
        return EXIT_FAILURE;
    }

    /* Побудова ребер графа Грьотча M4 */
    /* Базовий цикл C5: 0-1-2-3-4-0 */
    coloring_graph_add_edge(graph, 0, 1);
    coloring_graph_add_edge(graph, 1, 2);
    coloring_graph_add_edge(graph, 2, 3);
    coloring_graph_add_edge(graph, 3, 4);
    coloring_graph_add_edge(graph, 4, 0);

    /* Тіньові вершини 5..9 з'єднані з сусідами 0..4 */
    coloring_graph_add_edge(graph, 5, 1);
    coloring_graph_add_edge(graph, 5, 4);
    coloring_graph_add_edge(graph, 6, 0);
    coloring_graph_add_edge(graph, 6, 2);
    coloring_graph_add_edge(graph, 7, 1);
    coloring_graph_add_edge(graph, 7, 3);
    coloring_graph_add_edge(graph, 8, 2);
    coloring_graph_add_edge(graph, 8, 4);
    coloring_graph_add_edge(graph, 9, 0);
    coloring_graph_add_edge(graph, 9, 3);

    /* Верхівка 10 з'єднана з усіма тінями 5..9 */
    for (int i = 5; i <= 9; ++i) {
        coloring_graph_add_edge(graph, 10, i);
    }

    /* Налаштування конфігурації Branch-and-Price */
    ColoringConfig config;
    coloring_config_default(&config);
    config.engine = COLORING_ENGINE_BRANCH_AND_PRICE;
    config.time_limit_ms = 10000;
    config.symmetry_breaking_level = 2;

    ColoringResult result;
    memset(&result, 0, sizeof(result));
    ColoringDiagnostics diag;
    memset(&diag, 0, sizeof(diag));

    printf("Запуск розв'язувача Branch-and-Price...\n");
    err = coloring_solve(graph, &config, &result, &diag);
    if (err != COLORING_OK) {
        fprintf(stderr, "Помилка розв'язання: %s (код %d)\n", diag.error_message, err);
        coloring_graph_free(graph);
        return EXIT_FAILURE;
    }

    printf("Статус: %d, Хроматичне число: %d (час: %llu мкс)\n",
           result.status, result.chromatic_number, (unsigned long long)result.elapsed_us);
    printf("Розподіл кольорів по вершинах:\n");
    for (int v = 0; v < graph->num_vertices; ++v) {
        printf("  Вершина %2d -> Колір %d\n", v, result.colors[v]);
    }

    /* Верифікація сертифіката */
    err = coloring_verify_result(graph, &result, &diag);
    if (err == COLORING_OK) {
        printf("Сертифікат розфарбування успішно верифіковано: колізій немає.\n");
    } else {
        fprintf(stderr, "Помилка верифікації! Конфлікт на ребрі (%d, %d)\n",
                diag.conflict_u, diag.conflict_v);
    }

    /* Експорт у JSON */
    coloring_export_json("grotzsch_result.json", graph, &result);

    /* Звільнення ресурсів */
    coloring_result_free(&result);
    coloring_graph_free(graph);

    return EXIT_SUCCESS;
}
```
```cpp
#include <iostream>
#include <format>
#include "coloring_solver.hpp"

int main() {
    using namespace coloring;

    Graph graph(11);

    /* Базовий цикл C5 */
    (void)graph.add_edge(0, 1);
    (void)graph.add_edge(1, 2);
    (void)graph.add_edge(2, 3);
    (void)graph.add_edge(3, 4);
    (void)graph.add_edge(4, 0);

    /* Тіньові вершини */
    (void)graph.add_edge(5, 1);
    (void)graph.add_edge(5, 4);
    (void)graph.add_edge(6, 0);
    (void)graph.add_edge(6, 2);
    (void)graph.add_edge(7, 1);
    (void)graph.add_edge(7, 3);
    (void)graph.add_edge(8, 2);
    (void)graph.add_edge(8, 4);
    (void)graph.add_edge(9, 0);
    (void)graph.add_edge(9, 3);

    /* Верхівка apex */
    for (int32_t i = 5; i <= 9; ++i) {
        (void)graph.add_edge(10, i);
    }

    SolverConfig config{
        .engine = Engine::BranchAndPrice,
        .time_limit = std::chrono::milliseconds{10000},
        .symmetry_breaking_level = 2,
        .enable_kempe_pass = true,
        .random_seed = 1337
    };

    Solver solver(config);

    auto solve_result = solver.solve(graph);
    if (!solve_result) {
        const auto& diag = solve_result.error();
        std::cerr << std::format("Помилка розв'язання: {} (код {})\n",
                                 diag.message, static_cast<int32_t>(diag.last_error));
        return 1;
    }

    const auto& res = *solve_result;
    std::cout << std::format("Отримано розв'язок: χ(G) = {}, знайдено за {} мкс\n",
                             res.chromatic_number, res.elapsed.count());

    for (size_t i = 0; i < res.colors.size(); ++i) {
        std::cout << std::format("  Вузол {:2} -> Колір {}\n", i, res.colors[i]);
    }

    /* Верифікація правильності розфарбування */
    auto verify_res = Solver::verify(graph, res);
    if (verify_res) {
        std::cout << "Верифікація успішна: розфарбування строго правильне, конфліктів немає.\n";
    } else {
        std::cerr << std::format("Помилка верифікації на ребрі ({}, {})\n",
                                 verify_res.error().conflict_u, verify_res.error().conflict_v);
    }

    /* Експорт результату в JSON */
    auto export_res = Solver::export_json("grotzsch_result.json", graph, res);
    if (!export_res) {
        std::cerr << "Не вдалося зберегти JSON-звіт.\n";
    }

    return 0;
}
```
:::
