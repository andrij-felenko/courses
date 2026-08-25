# 📋 Інтерфейс та структура даних бібліотеки Nauty

Бібліотека Nauty (No AUTomorphisms, Yes?), створена австралійським математиком Бренданом Маккеєм (Brendan McKay) у 1981 році та розширена разом із Адольфо Піперно (Adolfo Piperno, модуль Traces), є світовим стандартом програмного забезпечення для обчислення груп автоморфізмів та побудови канонічних маркувань графів. Nauty лежить у основі багатьох систем комп'ютерної алгебри (GAP, SageMath, Magma) і дозволяє канонізувати графи з сотнями тисяч вершин за частки мілісекунди.

Ця вставка надає детальний довідник публічного С-інтерфейсу Nauty/Traces, описує структури даних `optionblk`, `statsblk`, списки розбиття `lab`/`ptn`, а також наводить робочий приклад обчислення канонічного формату графа.

## Загальна архітектура та принципи Nauty

Головна ідея Nauty полягає у перетворенні довільного графа `G` на його **канонічну форму** `C(G)`. Канонічна форма являє собою перестановку вершин графа, яка є єдиною та унікальною для всього класу ізоморфізму. Це означає, що якщо два графи `G₁` та `G₂` є ізоморфними (`G₁ ≅ G₂`), їхні канонічні графи `C(G₁)` та `C(G₂)` є абсолютно тотожними матрицями суміжності:

```
G₁ ≅ G₂  ⇔  C(G₁) = C(G₂)
```

Для обчислення канонічного представлення Nauty будує дерево індивідуалізації та ущільнення (individualization-refinement tree). На кожному вузлі дерева алгоритм виконує 1-WL ущільнення кольорів осередків. Якщо розбиття лишається недискретним, обирається цільовий осередок (target cell), і одна з його вершин фіксується (індивідуалізується), після чого ущільнення повторюється.

Ключова сила Nauty полягає у динамічному знаходженні автоморфізмів: як тільки два листки дерева дають однаковиий граф, алгоритм виявляє автоморфізм `γ ∈ Aut(G)`. Цей автоморфізм використовується для миттєвого відсікання цілих ізоморфних піддерев пошуку, скорочуючи загальну складність з `O(n!)` до кількох кроків.

## Докладний опис конфігураційної структури `optionblk`

Структура `optionblk` керує всіма аспектами поведінки алгоритму Nauty: від вибору генераторів груп автоморфізмів до підключення користувальницьких функцій розщеплення та ущільнення осередків.

:::tabs
```c
typedef struct optionblk {
    boolean getcanon;      /* TRUE: обчислити канонічний граф canon */
    boolean digraph;       /* TRUE: орієнтований граф; FALSE: неорієнтований */
    boolean writeautoms;   /* TRUE: друкувати генератори Aut(G) у stdout */
    boolean writemarkers;  /* TRUE: друкувати маркери дерева пошуку */
    int defaultptn;        /* TRUE: початкове розбиття є тотожно дискретним */
    int cartesian;         /* Налаштування обчислення векторних продуктів */
    int linelength;        /* Довжина рядка при виводі */
    FILE *outfile;         /* Потік для текстового виводу результатів */
    void (*userrefproc)(void*, int*, int*, int, int*, int*, set*, int*, int, int);
    void (*userautomproc)(int, int*, int*, int, int, int);
    void (*userlevelproc)(int*, int*, int, int*, int*, int, int, int);
    void (*nodeaction)(graph*, int*, int*, int, int, int, int);
    boolean tc_degree;     /* Пріоритет вибору цільового осередку за степенями */
    boolean minvarbyfreq;  /* Варіація інваріанта за частотою кольорів */
    int maxinvarlevel;     /* Максимальний рівень використання важких інваріантів */
    int invararg;          /* Додатковий параметр інваріанта */
} optionblk;
```
```cpp
// У C++ структура використовується через extern "C" або виклик з заголовків nauty.h:
extern "C" {
#include "nauty.h"
}

// У C++ об'єкт налаштувань ініціалізується макросом:
optionblk options;
DEFAULTOPTIONS_GRAPH(&options);
options.getcanon = TRUE;
options.writeautoms = FALSE;
```
:::

### Опис ключових полів `optionblk`

1. `getcanon` (`boolean`): Головний прапор обчислення канонічної форми. Якщо встановлено в `TRUE`, Nauty розраховує канонічну матрицю суміжності `canon` та записує перестановку вершин у масив `lab`. Якщо `FALSE`, алгоритм шукає лише групу автоморфізмів `Aut(G)` та орбіти.
2. `digraph` (`boolean`): Визначає тип графа. При `FALSE` граф вважається симетричним неорієнтованим, що дозволяє оптимізувати збереження матриць суміжності. При `TRUE` алгоритм обробляє напрямлені ребра.
3. `defaultptn` (`boolean`): Якщо `TRUE`, Nauty вважає початкове розбиття унітарним (усі вершини належать одному осередку). Якщо `FALSE`, користувач повинен самостійно заповнити масиви `lab` та `ptn`, задавши початкове розфарбування (наприклад, за типами атомів у хімічній молекулі).
4. `userrefproc`: Вказівник на користувальницьку функцію ущільнення. Дозволяє підключати власні комбінаторні інваріанти замість стандартного 1-WL.
5. `userautomproc`: Callback-функція, яка викликається кожного разу, коли Nauty знаходить новий генератор автоморфізму. Корисна для інтеграції з комп'ютерними алгебрами (GAP / Magma).

Макрос `DEFAULTOPTIONS_GRAPH(options)` ініціалізує структуру стандартними оптимізованими значеннями для неорієнтованих графів.

## Докладний опис структури статистики `statsblk`

Після виконання функції `nauty()` структура `statsblk` містить повні метрики обчислювального процесу:

:::tabs
```c
typedef struct statsblk {
    double grpsize1;       /* Порядок групи Aut(G) = grpsize1 * 10^(grpsize2) */
    int grpsize2;          /* Порядок степеня 10 для великих груп */
    int numorbits;         /* Кількість орбіт вершин під дією Aut(G) */
    int numgenerators;     /* Кількість знайдених генераторів Aut(G) */
    unsigned long numnodes;/* Кількість відвіданих вузлів у дереві пошуку */
    unsigned long numbadleaves; /* Кількість некорисних листків */
    int maxlevel;          /* Максимальна глибина рекурсивного дерева */
    unsigned long canupdates;   /* Кількість оновлень канонічного підпису */
    int invarcounts;       /* Кількість викликів важкого інваріанта */
    int invarlevel;        /* Рівень, на якому інваріант був ефективним */
} statsblk;
```
```cpp
// Обгортка статистики в C++ для безпечного читання метрик:
struct NautyStats {
    double aut_group_size;
    int num_orbits;
    unsigned long nodes_visited;
    unsigned long canonical_updates;

    static NautyStats from_c_stats(const statsblk& stats) {
        return NautyStats{
            stats.grpsize1 * std::pow(10.0, stats.grpsize2),
            stats.numorbits,
            stats.numnodes,
            stats.canupdates
        };
    }
};
```
:::

### Опис метрик статистики

- `grpsize1` та `grpsize2`: Розмір групи автоморфізмів подається у плаваючій формі з експонентою `grpsize1 × 10^(grpsize2)`. Це дозволяє уникати переповнення цілочисельних типів для симетричних графів (наприклад, для повного графа `K₆₀` розмір `60!` перевищує `8 × 10⁸¹`).
- `numorbits`: Кількість незалежних еквівалентних класифікацій вершин. Якщо `numorbits == 1`, граф є вершинно-транзитивним (vertex-transitive).
- `numnodes`: Загальна кількість вузлів дерева індивідуалізації. Чим менше це число порівняно з `n!`, тим ефективніше спрацювало відсікання за автоморфізмами.

## Пам'ять та представлення графів: Щільний формат (Dense Graph)

У щільному форматі (Dense Graph) граф зберігається як масив бітових векторів типу `set`. Матриця суміжності займає `n × m` слів типу `setword`, де `m = (n + WORDSIZE - 1) / WORDSIZE`.

Значення `WORDSIZE` зазвичай становить 64 (на 64-бітних архітектурах).

:::tabs
```c
// Спеціальні макроси Nauty для ефективного маніпулювання бітовими векторами:
#define SETWORDSNEEDED(n) (((n) + WORDSIZE - 1) / WORDSIZE)
#define GRAPHROW(g, v, m) ((g) + (size_t)(v) * (m))
#define ADDONEEDGE(g, u, v, m) \
    do { \
        GRAPHROW(g, u, m)[SETWORDINDEX(v)] |= SETBIT(SETBITINDEX(v)); \
        GRAPHROW(g, v, m)[SETWORDINDEX(u)] |= SETBIT(SETBITINDEX(u)); \
    } while(0)
#define DELONEEDGE(g, u, v, m) \
    do { \
        GRAPHROW(g, u, m)[SETWORDINDEX(v)] &= ~SETBIT(SETBITINDEX(v)); \
        GRAPHROW(g, v, m)[SETWORDINDEX(u)] &= ~SETBIT(SETBITINDEX(u)); \
    } while(0)
#define ISELEMENT(setptr, pos) \
    ((*(setptr + SETWORDINDEX(pos)) & SETBIT(SETBITINDEX(pos))) != 0)
```
```cpp
// У C++ бітові макроси мапуються на виклики std::vector або std::span:
class DenseGraphBuffer {
public:
    DenseGraphBuffer(size_t n) : n_(n), m_(SETWORDSNEEDED(n)), data_(n * m_, 0) {}

    void add_edge(size_t u, size_t v) {
        ADDONEEDGE(data_.data(), u, v, m_);
    }

    bool has_edge(size_t u, size_t v) const {
        return ISELEMENT(GRAPHROW(data_.data(), u, m_), v);
    }

    graph* data() { return data_.data(); }
    int m() const { return m_; }
    int n() const { return static_cast<int>(n_); }

private:
    size_t n_;
    int m_;
    std::vector<graph> data_;
};
```
:::

## Представлення розбиття: Масиви `lab` та `ptn`

Розбиття (partition) множини вершин `V` зберігається за допомогою двох паралельних цілочисельних масивів `lab` та `ptn` довжини `n`:

- `lab[0...n-1]`: Перестановка вершин графа, у якій вершины одного осередку (кольорового класу) розміщені суміжно один біля одного.
- `ptn[0...n-1]`: Масив прапорців меж осередків. Значення `ptn[i] = 0` означає, що вершина `lab[i]` є останньою вершиною у своєму осередку; значення `ptn[i] > 0` означає, що осередок продовжується на наступний елемент.

**Приклад розбиття:**
Нехай `lab = [2, 4, 0, 1, 3]` та `ptn = [1, 0, 1, 1, 0]`.
Це відповідає двом осередкам:
- Перший осередок: `{2, 4}` (оскільки `ptn[0] = 1`, а `ptn[1] = 0`);
- Другий осередок: `{0, 1, 3}` (оскільки `ptn[2] = 1`, `ptn[3] = 1`, а `ptn[4] = 0`).

## Сигнатура та робочий цикл функції `nauty()`

Головна функція `nauty()` виконує побудову дерева індивідуалізації:

:::tabs
```c
void nauty(
    graph *g,           /* Вхідна матриця суміжності графа */
    int *lab,           /* Вхідне/вихідне розбиття (порядок вершин) */
    int *ptn,           /* Прапорці меж осередків розбиття */
    int *active,        /* Масив активних осередків для 1-WL */
    int *orbits,        /* Вихідний масив орбіт вершин */
    optionblk *options, /* Параметри алгоритму */
    statsblk *stats,    /* Вихідна статистика обчислень */
    set *workspace,     /* Робочий масив пам'яті */
    int worksize,       /* Розмір робочого масиву пам'яті */
    int m,              /* Кількість setword на рядок графа */
    int n,              /* Кількість вершин у графі */
    graph *canon        /* Вихідний канонічний граф (якщо options->getcanon == TRUE) */
);
```
```cpp
// У C++ виклик сигнатури nauty() обгортається у типбезпечний метод:
namespace nauty_cpp {
    inline void run(graph* g, int* lab, int* ptn, int* orbits,
                    optionblk* options, statsblk* stats,
                    set* workspace, int worksize, int m, int n, graph* canon) {
        ::nauty(g, lab, ptn, nullptr, orbits, options, stats, workspace, worksize, m, n, canon);
    }
}
```
:::

## Повний робочий приклад обчислення канонічної форми

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include "nauty.h"

int main(void) {
    int n = 5;
    int m = SETWORDSNEEDED(n);

    nauty_check(WORDSIZE, m, n, NAUTYVERSION);

    graph *g = (graph*)malloc(m * n * sizeof(graph));
    graph *cg = (graph*)malloc(m * n * sizeof(graph));
    int *lab = (int*)malloc(n * sizeof(int));
    int *ptn = (int*)malloc(n * sizeof(int));
    int *orbits = (int*)malloc(n * sizeof(int));

    optionblk options;
    statsblk stats;
    DEFAULTOPTIONS_GRAPH(&options);
    options.getcanon = TRUE;

    EMPTYGRAPH(g, m, n);
    ADDONEEDGE(g, 0, 1, m);
    ADDONEEDGE(g, 1, 2, m);
    ADDONEEDGE(g, 2, 3, m);
    ADDONEEDGE(g, 3, 4, m);
    ADDONEEDGE(g, 4, 0, m);

    #define WORKSIZE (16 * SETWORDSNEEDED(5))
    set workspace[WORKSIZE];

    nauty(g, lab, ptn, NULL, orbits, &options, &stats, workspace, WORKSIZE, m, n, cg);

    printf("Порядок групи автоморфізмів Aut(G): %.0f\n", stats.grpsize1);
    printf("Кількість орбіт вершин: %d\n", stats.numorbits);
    printf("Канонічне маркування вершин (lab):\n");
    for (int i = 0; i < n; i++) {
        printf("  v[%d] -> canonical[%d]\n", i, lab[i]);
    }

    free(g);
    free(cg);
    free(lab);
    free(ptn);
    free(orbits);
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <memory>
#include <cmath>

extern "C" {
#include "nauty.h"
}

class NautyWrapper {
public:
    explicit NautyWrapper(int n)
        : n_(n), m_(SETWORDSNEEDED(n)),
          g_(m_ * n_), cg_(m_ * n_),
          lab_(n_), ptn_(n_), orbits_(n_) {
        nauty_check(WORDSIZE, m_, n_, NAUTYVERSION);
        EMPTYGRAPH(g_.data(), m_, n_);
    }

    void add_edge(int u, int v) {
        ADDONEEDGE(g_.data(), u, v, m_);
    }

    struct Result {
        double aut_group_size;
        int num_orbits;
        std::vector<int> canonical_labeling;
    };

    Result compute_canonical_form() {
        optionblk options;
        statsblk stats;
        DEFAULTOPTIONS_GRAPH(&options);
        options.getcanon = TRUE;

        std::vector<set> workspace(16 * m_);

        nauty(g_.data(), lab_.data(), ptn_.data(), nullptr,
              orbits_.data(), &options, &stats,
              workspace.data(), static_cast<int>(workspace.size()),
              m_, n_, cg_.data());

        return Result{
            stats.grpsize1 * std::pow(10.0, stats.grpsize2),
            stats.numorbits,
            lab_
        };
    }

private:
    int n_;
    int m_;
    std::vector<graph> g_;
    std::vector<graph> cg_;
    std::vector<int> lab_;
    std::vector<int> ptn_;
    std::vector<int> orbits_;
};

int main() {
    NautyWrapper g(5);
    g.add_edge(0, 1);
    g.add_edge(1, 2);
    g.add_edge(2, 3);
    g.add_edge(3, 4);
    g.add_edge(4, 0);

    auto res = g.compute_canonical_form();
    std::cout << "Розмір Aut(G): " << res.aut_group_size << "\n";
    std::cout << "Орбіти: " << res.num_orbits << "\n";
    std::cout << "Канонічний порядок: ";
    for (int v : res.canonical_labeling) {
        std::cout << v << " ";
    }
    std::cout << "\n";
    return 0;
}
```
:::

## Розріджений формат (`sparsegraph`) та модуль Traces

Для великих графів із тисячами вершин та незначною середньою щільністю ребер Nauty надає модуль `sparsegraph` та альтернативний алгоритм **Traces**.

### Опис структури `sparsegraph`

:::tabs
```c
typedef struct {
    int nv;         /* Кількість вершин */
    int nde;        /* Кількість спрямованих ребер */
    int *v;         /* Масив індексів початку списку ребер для кожної вершини */
    int *d;         /* Масив степенів вершин */
    int *e;         /* Масив суміжних вершин */
    size_t vlen;    /* Виділена довжина масиву v */
    size_t dlen;    /* Виділена довжина масиву d */
    size_t elen;    /* Виділена довжина масиву e */
} sparsegraph;
```
```cpp
// C++ RAII обгортка для структури sparsegraph:
class SparseGraphWrapper {
public:
    sparsegraph sg;

    SparseGraphWrapper() {
        SG_INIT(sg);
    }

    ~SparseGraphWrapper() {
        SG_FREE(sg);
    }

    SparseGraphWrapper(const SparseGraphWrapper&) = delete;
    SparseGraphWrapper& operator=(const SparseGraphWrapper&) = delete;
};
```
:::

### Порівняння Nauty та Traces

1. **Стратегія обходу дерева:** Nauty реалізує пошук у глибину (Depth-First Search, DFS) з фіксацією цільового осередку на кожному рівні. Traces використовує стратегію обходу в ширину (Breadth-First Search, BFS), порівнюючи траєкторії декількох альтернативних шляхів одночасно.
2. **Тип графів:** Nauty показує максимальну швидкість на жорстких комбінаторних графах малого та середнього розміру з високим рівнем симетрії. Traces оптимізовано для величезних розріджених графів із мільйонами вершин, де DFS-дерева споживають забагато пам'яті під стек.
3. **Пам'ять:** При використанні `sparsegraph` модуль Traces споживає суттєво менше пам'яті, дозволяючи канонізувати розріджені мережі зв'язку та молекулярні графи за лінійний від кількості ребер час.

## Практичні поради щодо інтеграції Nauty/Traces

При інтеграції бібліотеки у власні високонавантажені C/C++ проекти слід дотримуватись трьох правил продуктивності:
- **Перевикористання пам'яті:** Уникайте виділення `malloc` на кожному виклику `nauty()`. Масиви `lab`, `ptn`, `orbits` та `workspace` слід виділяти один раз на потік (Thread-Local Storage) та перевикористовувати для послідовних графів однакового розміру.
- **Вхідні кольори:** Якщо об'єкти мають початкові мітки (типи атомів у хімічних сполуках чи типи вентилів у VLSI), передавайте їх через масиви `lab` та `ptn` із прапорцем `options.defaultptn = FALSE`. Це відсікає неможливі відображення ще до побудови дерева індивідуалізації.
- **Преверірка степенів:** Завжди перевіряйте сумісність послідовностей степенів перед викликом `nauty()`, оскільки це миттєво відсікає 90% неізоморфних графів без потреби побудови канонічного підпису.
