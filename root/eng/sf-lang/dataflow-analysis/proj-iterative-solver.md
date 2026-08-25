# ⚙️ Реалізація ітеративного розв'язувача потоку даних (Worklist Solver)

Усі класичні задачі аналізу потоків даних над бітовими векторами розв'язуються єдиним універсальним механізмом — **алгоритмом робочого списку** (англ. *worklist algorithm*). Замість наївного багаторазового прогону по всіх базових блоках програми поспіль, алгоритм підтримує динамічну чергу лише тих блоків, чий вхідний або вихідний стан змінився на попередньому кроці.

Нижче наведено робочу реалізацію аналізатора живучості змінних (**Live Variables Analysis**). Це зворотний аналіз (Backward May-analysis), який визначає, які змінні можуть бути прочитані далі за ходом виконання програми без попереднього перезапису.

```
                  +-------------------------------+
                  |  Блок B: USE[B] та DEF[B]     |
                  +-------------------------------+
                                  ^
                                  |  IN[B] = USE[B] ∪ (OUT[B] \ DEF[B])
                  +---------------+---------------+
                  |             IN[B]             |
                  +-------------------------------+
                                  ^
                                  |  OUT[B] = ∪ IN[Succ] (Зворотний потік)
                  +---------------+---------------+
                  |      Наступники Succ(B)       |
                  +-------------------------------+
```

## Архітектура розв'язувача та бітові вектори

Аналізатор структурує програму на три взаємопов'язані рівні:
1. **Бітовий вектор (BitVector):** компактний масив бітів фіксованої довжини `V` (де кожен біт відповідає змінній або виразу). Завдяки побітовим інструкціям процесора (`OR`, `AND`, `NOT`), операції над множинами до 64 елементів виконуються за один такт процесора. Для сотень і тисяч змінних бітовий вектор розширюється до масиву 64-бітних слів (`uint64_t[]`).
2. **Базовий блок (BasicBlock):** містить попередньо обчислені локальні множини:
   - `USE[B]` — змінні, значення яких зчитується в блоці до будь-якого їхнього перезапису;
   - `DEF[B]` — змінні, яким присвоюється нове значення всередині блоку;
   - Динамічні множини `IN[B]` та `OUT[B]`, які уточнюються під час ітерацій.
3. **Граф потоку керування (CFG):** список суміжності попередників (`pred`) і наступників (`succ`) для кожного блоку.

## Реалізація аналізатора

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>
#include <string.h>

#define MAX_VARS 64
#define MAX_BLOCKS 16
#define MAX_EDGES 8

typedef struct {
    uint64_t bits;
} BitSet;

static inline BitSet bitset_create(void) {
    BitSet s = {0};
    return s;
}

static inline void bitset_set(BitSet *s, int var_id) {
    s->bits |= (1ULL << var_id);
}

static inline bool bitset_get(BitSet s, int var_id) {
    return (s.bits & (1ULL << var_id)) != 0;
}

static inline BitSet bitset_union(BitSet a, BitSet b) {
    BitSet res = { a.bits | b.bits };
    return res;
}

static inline BitSet bitset_diff(BitSet a, BitSet b) {
    BitSet res = { a.bits & ~b.bits };
    return res;
}

static inline bool bitset_equal(BitSet a, BitSet b) {
    return a.bits == b.bits;
}

typedef struct {
    int id;
    BitSet use;
    BitSet def;
    BitSet in;
    BitSet out;

    int succ_count;
    int succ[MAX_EDGES];
    int pred_count;
    int pred[MAX_EDGES];
} Block;

typedef struct {
    int num_blocks;
    int num_vars;
    Block blocks[MAX_BLOCKS];
} CFG;

void cfg_init(CFG *cfg, int num_blocks, int num_vars) {
    cfg->num_blocks = num_blocks;
    cfg->num_vars = num_vars;
    for (int i = 0; i < num_blocks; ++i) {
        cfg->blocks[i].id = i;
        cfg->blocks[i].use = bitset_create();
        cfg->blocks[i].def = bitset_create();
        cfg->blocks[i].in  = bitset_create();
        cfg->blocks[i].out = bitset_create();
        cfg->blocks[i].succ_count = 0;
        cfg->blocks[i].pred_count = 0;
    }
}

void cfg_add_edge(CFG *cfg, int from, int to) {
    Block *src = &cfg->blocks[from];
    Block *dst = &cfg->blocks[to];
    src->succ[src->succ_count++] = to;
    dst->pred[dst->pred_count++] = from;
}

void solve_live_variables(CFG *cfg) {
    int worklist[MAX_BLOCKS * 4];
    bool in_worklist[MAX_BLOCKS] = {false};
    int head = 0, tail = 0;

    /* Додаємо всі блоки у робочий список */
    for (int i = 0; i < cfg->num_blocks; ++i) {
        worklist[tail++] = i;
        in_worklist[i] = true;
    }

    while (head < tail) {
        int b_id = worklist[head++];
        in_worklist[b_id] = false;
        Block *b = &cfg->blocks[b_id];

        /* OUT[B] = ∪ IN[Succ] */
        BitSet new_out = bitset_create();
        for (int i = 0; i < b->succ_count; ++i) {
            int s_id = b->succ[i];
            new_out = bitset_union(new_out, cfg->blocks[s_id].in);
        }
        b->out = new_out;

        /* IN[B] = USE[B] ∪ (OUT[B] \ DEF[B]) */
        BitSet new_in = bitset_union(b->use, bitset_diff(b->out, b->def));

        /* Якщо IN[B] змінився, додаємо всіх попередників до робочого списку */
        if (!bitset_equal(new_in, b->in)) {
            b->in = new_in;
            for (int i = 0; i < b->pred_count; ++i) {
                int p_id = b->pred[i];
                if (!in_worklist[p_id]) {
                    worklist[tail++] = p_id;
                    in_worklist[p_id] = true;
                }
            }
        }
    }
}

void print_results(const CFG *cfg) {
    printf("=== Результати аналізу Live Variables ===\n");
    for (int i = 0; i < cfg->num_blocks; ++i) {
        const Block *b = &cfg->blocks[i];
        printf("Блок B%d:\n", b->id);
        printf("  USE: { ");
        for (int v = 0; v < cfg->num_vars; ++v) {
            if (bitset_get(b->use, v)) printf("v%d ", v);
        }
        printf("}\n  DEF: { ");
        for (int v = 0; v < cfg->num_vars; ++v) {
            if (bitset_get(b->def, v)) printf("v%d ", v);
        }
        printf("}\n  IN : { ");
        for (int v = 0; v < cfg->num_vars; ++v) {
            if (bitset_get(b->in, v)) printf("v%d ", v);
        }
        printf("}\n  OUT: { ");
        for (int v = 0; v < cfg->num_vars; ++v) {
            if (bitset_get(b->out, v)) printf("v%d ", v);
        }
        printf("}\n\n");
    }
}

int main(void) {
    /* 4 блоки, 3 змінні: v0 (a), v1 (b), v2 (c) */
    CFG cfg;
    cfg_init(&cfg, 4, 3);

    /* B0 (Entry): def = {v0, v1} (a = 1; b = 2;) */
    bitset_set(&cfg.blocks[0].def, 0);
    bitset_set(&cfg.blocks[0].def, 1);

    /* B1 (Loop Header): use = {v0}, def = {v2} (c = a + 1; if ...) */
    bitset_set(&cfg.blocks[1].use, 0);
    bitset_set(&cfg.blocks[1].def, 2);

    /* B2 (Loop Body): use = {v1, v2}, def = {v0} (a = b + c;) */
    bitset_set(&cfg.blocks[2].use, 1);
    bitset_set(&cfg.blocks[2].use, 2);
    bitset_set(&cfg.blocks[2].def, 0);

    /* B3 (Exit): use = {v2} (return c;) */
    bitset_set(&cfg.blocks[3].use, 2);

    /* Ребра: B0 -> B1; B1 -> B2, B1 -> B3; B2 -> B1 */
    cfg_add_edge(&cfg, 0, 1);
    cfg_add_edge(&cfg, 1, 2);
    cfg_add_edge(&cfg, 1, 3);
    cfg_add_edge(&cfg, 2, 1);

    solve_live_variables(&cfg);
    print_results(&cfg);

    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <queue>
#include <bitset>
#include <cstdint>

constexpr size_t MAX_VARS = 64;
using BitSet = std::bitset<MAX_VARS>;

struct Block {
    int id{0};
    BitSet use{};
    BitSet def{};
    BitSet in{};
    BitSet out{};

    std::vector<int> succ{};
    std::vector<int> pred{};
};

class DataflowSolver {
public:
    explicit DataflowSolver(size_t num_blocks, size_t num_vars)
        : num_vars_(num_vars), blocks_(num_blocks) {
        for (size_t i = 0; i < num_blocks; ++i) {
            blocks_[i].id = static_cast<int>(i);
        }
    }

    void add_edge(size_t from, size_t to) {
        blocks_[from].succ.push_back(static_cast<int>(to));
        blocks_[to].pred.push_back(static_cast<int>(from));
    }

    Block& block(size_t index) {
        return blocks_[index];
    }

    const Block& block(size_t index) const {
        return blocks_[index];
    }

    void solve_live_variables() {
        std::queue<int> worklist;
        std::vector<bool> in_worklist(blocks_.size(), true);

        for (const auto& b : blocks_) {
            worklist.push(b.id);
        }

        while (!worklist.empty()) {
            int b_id = worklist.front();
            worklist.pop();
            in_worklist[b_id] = false;
            auto& b = blocks_[b_id];

            // OUT[B] = ∪ IN[Succ]
            BitSet new_out{};
            for (int s_id : b.succ) {
                new_out |= blocks_[s_id].in;
            }
            b.out = new_out;

            // IN[B] = USE[B] ∪ (OUT[B] \ DEF[B])
            BitSet new_in = b.use | (b.out & ~b.def);

            if (new_in != b.in) {
                b.in = new_in;
                for (int p_id : b.pred) {
                    if (!in_worklist[p_id]) {
                        worklist.push(p_id);
                        in_worklist[p_id] = true;
                    }
                }
            }
        }
    }

    void print() const {
        std::cout << "=== Результати аналізу Live Variables (C++) ===\n";
        for (const auto& b : blocks_) {
            std::cout << "Блок B" << b.id << ":\n";
            std::cout << "  USE: { ";
            for (size_t v = 0; v < num_vars_; ++v) {
                if (b.use.test(v)) std::cout << "v" << v << " ";
            }
            std::cout << "}\n  DEF: { ";
            for (size_t v = 0; v < num_vars_; ++v) {
                if (b.def.test(v)) std::cout << "v" << v << " ";
            }
            std::cout << "}\n  IN : { ";
            for (size_t v = 0; v < num_vars_; ++v) {
                if (b.in.test(v)) std::cout << "v" << v << " ";
            }
            std::cout << "}\n  OUT: { ";
            for (size_t v = 0; v < num_vars_; ++v) {
                if (b.out.test(v)) std::cout << "v" << v << " ";
            }
            std::cout << "}\n\n";
        }
    }

private:
    size_t num_vars_{0};
    std::vector<Block> blocks_{};
};

int main() {
    DataflowSolver solver(4, 3);

    // B0 (Entry): def = {v0, v1} (a = 1; b = 2;)
    solver.block(0).def.set(0);
    solver.block(0).def.set(1);

    // B1 (Loop Header): use = {v0}, def = {v2} (c = a + 1; if ...)
    solver.block(1).use.set(0);
    solver.block(1).def.set(2);

    // B2 (Loop Body): use = {v1, v2}, def = {v0} (a = b + c;)
    solver.block(2).use.set(1);
    solver.block(2).use.set(2);
    solver.block(2).def.set(0);

    // B3 (Exit): use = {v2} (return c;)
    solver.block(3).use.set(2);

    // Ребра: B0 -> B1; B1 -> B2, B1 -> B3; B2 -> B1
    solver.add_edge(0, 1);
    solver.add_edge(1, 2);
    solver.add_edge(1, 3);
    solver.add_edge(2, 1);

    solver.solve_live_variables();
    solver.print();

    return 0;
}
```
:::

## Покрокове простеження виконання (Trace)

Простежмо, як змінюються множини `IN` та `OUT` для тестового графа з чотирма блоками та циклом:

1. **Початковий стан:** Робочий список містить усі блоки: `W = [B0, B1, B2, B3]`. Усі множини `IN` та `OUT` порожні: `{}`.
2. **Крок 1 (Обробка B0):**
   - `OUT[B0] = IN[B1] = {}`
   - `IN[B0] = USE[B0] ∪ (OUT[B0] \ DEF[B0]) = {} ∪ ({} \ {v0, v1}) = {}`
   - Змін немає.
3. **Крок 2 (Обробка B1):**
   - `OUT[B1] = IN[B2] ∪ IN[B3] = {} ∪ {} = {}`
   - `IN[B1] = {v0} ∪ ({} \ {v2}) = {v0}`
   - `IN[B1]` змінився з `{}` на `{v0}`! Додаємо попередників `B1` (блоки `B0` та `B2`) до робочого списку: `W = [B2, B3, B0]`.
4. **Крок 3 (Обробка B2):**
   - `OUT[B2] = IN[B1] = {v0}`
   - `IN[B2] = {v1, v2} ∪ ({v0} \ {v0}) = {v1, v2}`
   - `IN[B2]` змінився! Додаємо попередника `B1` до черги: `W = [B3, B0, B1]`.
5. **Крок 4 (Обробка B3):**
   - `OUT[B3] = {}`
   - `IN[B3] = {v2} ∪ {} = {v2}`
   - `IN[B3]` змінився! Додаємо `B1` до черги (він уже там є, прапорець `in_worklist` захищає від дублювання).
6. **Крок 5 (Повторна обробка B1):**
   - `OUT[B1] = IN[B2] ∪ IN[B3] = {v1, v2} ∪ {v2} = {v1, v2}`
   - `IN[B1] = {v0} ∪ ({v1, v2} \ {v2}) = {v0, v1}`
   - `IN[B1]` знову змінився (додалася змінна `v1`, яка циркулює в тілі циклу). Додаємо `B0` та `B2` до черги: `W = [B0, B2]`.
7. **Крок 6-7 (Стабілізація):**
   - Обробка `B0`: `OUT[B0] = {v0, v1}`, `IN[B0] = {} ∪ ({v0, v1} \ {v0, v1}) = {}`. Без змін.
   - Обробка `B2`: `OUT[B2] = {v0, v1}`, `IN[B2] = {v1, v2} ∪ ({v0, v1} \ {v0}) = {v1, v2}`. Без змін.
8. **Фініш:** Робочий список порожній. Досягнуто нерухомої точки.

## Адаптація до інших задач потоку даних

Щоб перетворити цей рушій на прямий аналізатор типу Must (наприклад, **Available Expressions**), потрібно змінити рівно три складові:

1. **Напрямок обходу:**
   - Замість `OUT[B] = ∪ IN[Succ]` обчислюємо `IN[B] = ∩ OUT[Pred]`.
   - Замість `IN[B] = USE ∪ (OUT \ DEF)` обчислюємо `OUT[B] = GEN ∪ (IN \ KILL)`.
   - При зміні `OUT[B]` до черги додаються наступники `Succ(B)`, а не попередники.
2. **Оператор злиття:**
   - Замість порозрядного `OR` (`|`) використовується порозрядний `AND` (`&`).
3. **Ініціалізація ґратки:**
   - Для задачі `Available Expressions` усі блоки (крім початкового `Entry`) ініціалізуються одиничними бітами (`ALL_ONES`), тоді як `OUT[Entry] = 0`. Якщо пропустити це правило й ініціалізувати всі блоки нулями, оператор `AND` знищить усі вирази на першому ж кроці.

## Від живучості змінних до розподілу регістрів

Обчислені множини `IN[B]` та `OUT[B]` не є кінцевою метою компілятора — вони слугують прямим входом для **розподілу регістрів** (англ. *register allocation*).

У класичному алгоритмі розфарбовування графа Чайтіна — Бріґґза (Chaitin-Briggs register allocator):
1. **Інтерференція (Interference):** дві віртуальні змінні `u` та `v` конфліктують за фізичний регістр, якщо вони одночасно живі в будь-якій точці програми.
2. **Побудова графа конфліктів:** аналізатор перевіряє кожну інструкцію: якщо інструкція визначає змінну `d`, між `d` та всіма іншими змінними, що є живими в цей момент (`LIVE \ {d}`), проводиться ребро нероздільності.
3. **Розфарбовування:** знайдений граф конфліктів розфарбовується `K` кольорами (де `K` — кількість фізичних регістрів процесора). Якщо хроматичне число перевищує `K`, компілятор обирає змінні для скидання в оперативну пам'ять (Spilling).

## Продуктивність, структури пам'яті та апаратна оптимізація

У реальних індустріальних компіляторах (LLVM, GCC) класичний розв'язувач оптимізується за кількома ключовими напрямками:

1. **Порядок обходу черги (Worklist Order):**
   - Проста FIFO-черга (як у коді вище) є наочною, але може змусити блок оновлюватися кілька зайвих разів.
   - Для прямого аналізу чергу організовують як пріоритетну чергу за **зворотним постпорядком (RPO)** обходу дерева домінування CFG. У такому разі інформація поширюється від кореня до листя за один прохід, і кожне тіло циклу потребує рівно `d + 1` ітерацій, де `d` — глибина вкладеності циклу.
   - Для зворотного аналізу (як наш Live Variables) чергу впорядковують за **постпорядком (PO)**.

2. **Розріджені бітові вектори (Sparse Bitvectors):**
   - Якщо у великій функції є 50 000 локальних змінних, але в кожному окремому блоці задіяні лише одиниці, звичайний масив бітів витрачає гігабайти пам'яті на порожні нулі.
   - У таких випадках класи `llvm::BitVector` замінюють на `llvm::SparseBitVector`, де біти зберігаються у зв'язаному списку невеликих ненульових чанків (наприклад, по 128 або 256 бітів).

3. **SIMD-векторизація та паралелізм слів:**
   - Порозрядні операції `ANDNOT`, `AND` та `OR` є ідеальними кандидатами для векторних розширень процесора (AVX-512 на x86-64 або Neon на ARM64). Інструкція `vpternlogd` в архітектурі x86 здатна виконати довільну булеву функцію від трьох операндів (наприклад, `GEN | (IN & ~KILL)`) за один машинний такт над 512 бітами одночасно.

4. **Врахування викликів функцій та покажчиків:**
   - Невідомий виклик функції `foo()` змушує компілятор консервативно вважати, що всі глобальні змінні та всі змінні, адреси яких були взяті (`&x`), можуть бути прочитані всередині виклику (вони додаються до `USE`) або змінені (додаються до `DEF`). Точність аналізу прямо залежить від якості супутнього аналізу покажчиків (Alias Analysis).
