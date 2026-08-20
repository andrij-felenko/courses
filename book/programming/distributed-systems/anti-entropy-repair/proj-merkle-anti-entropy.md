# 🛠️ Практична реалізація Merkle Tree Anti-Entropy ремонту

У розподілених безлідерних базах даних (Cassandra, ScyllaDB, Dynamo, Riak) анти-ентропійний ремонт спирається на швидке знаходження несинхронізованих діапазонів даних між вузлами. Реалізація Merkle Tree на мовах низького рівня (C та C++) вимагає ефективного використання кешу процесора, мінімізації динамічних виділень пам'яті, потокового K-Way злиття файлів таблиці, асинхронного виконання, суворого контролю бюджету оперативної пам'яті та коректного вирішення конфліктів за правилом Last-Write-Wins (LWW).

---

## 1. Архітектура та організація структури в пам'яті

Класична реалізація бінарного дерева на покажчиках (`struct Node { Node *left; Node *right; uint64_t hash; };`) є вкрай неефективною для високопродуктивних рушіїв баз даних. Кожен внутрішній вузол створює відчутний оверхед на покажчики (16 байтів на 64-бітних архітектурах) та викликає масові промахи апаратного кешу L1/L2 через фрагментацію пам'яті в купі (heap fragmentation).

Для досягнення максимальної швидкості дерево Меркла розміщується в **одновимірному неперервному масиві (Flat Binary Heap)**:
- Корінь дерева розташовано за індексом `1`;
- Лівий нащадок вузла з індексом `i` розташований за адресою `2 · i`;
- Правий нащадок вузла з індексом `i` розташований за адресою `2 · i + 1`;
- Батьківський вузол для вузла `i` обчислюється швидким бітовим зсувом `i >> 1`.

```
                  [1] Корінь (Рівень 0)
                 /   \
              [2]     [3] (Рівень 1)
             /  \     /  \
           [4]  [5] [6]  [7] (Рівень 2)
          / \   / \ / \  / \
         8   9 10 11 12 13 14 15 (Листки, Рівень 3)
```

Таке послідовне представлення гарантує відмінну просторову та часову локальність даних: при обході дерева сусідні вузли завантажуються в кеш процесора однією апаратною транзакцією шини оперативної пам'яті. Для фіксованої глибини `DEPTH = 3` кількість листків становить `M = 2³ = 8`. Загальна кількість вузлів у дереві дорівнює `2^(DEPTH + 1) = 16`. Масив із 16 елементів `uint64_t` займає лише 128 байтів, що повністю вміщується у дві стандартні 64-байтні кеш-лінії сучасного процесора, унеможливлюючи появу затримок через очікування відповідей контролера RAM.

---

## 2. Квантування простору токенів на листки (Token Quantization)

Простір токенів розподіленої хеш-таблиці є 64-бітним беззнаковим цілим числом у діапазоні `[0, 2⁶⁴ - 1]`. Кожен листок дерева відповідає за рівний числовий піддіапазон кільця.

Для відображення довільного 64-бітного токена на відповідний листок дерева виконується операція бітового зсуву вправо:

```
leaf_index = token >> (64 - DEPTH)
```

При `DEPTH = 3` зміщення становить `64 - 3 = 61` біт. Токен зсувається на 61 біт праворуч, залишаючи 3 старші біти, що приймають значення від `0` до `7`. Знайдений `leaf_index` зміщується на початок ливарного рівня в масиві: `array_index = 8 + leaf_index`.

Коли в систему надходить запис `(key, value, timestamp, is_tombstone)`, алгоритм виконує такі кроки:
1. Обчислюється 64-бітний хеш первинного ключа алгоритмом FNV-1a або Murmur3 для визначення числового токена в просторі кільця.
2. Обчислюється комбінований хеш запису з урахуванням значення, монотонної часової мітки та прапорця надгробка видалення.
3. Отриманий хеш додається до відповідного листка шляхом каскадного хешування.

---

## 3. Програмна реалізація алгоритму Merkle Tree (C / C++)

Нижче наведено промислові реалізації повного циклу побудови дерев Меркла, бінарного спуску для швидкої діагностики розбіжностей та консолідації мутацій.

:::tabs

@tab C

```c
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define MERKLE_DEPTH 3
#define NUM_LEAVES (1 << MERKLE_DEPTH)
#define TREE_SIZE (1 << (MERKLE_DEPTH + 1))

/* Хеш-функція FNV-1a (64-bit) для швидкого хешування */
#define FNV_OFFSET 14695981039346656037ULL
#define FNV_PRIME  1099511628211ULL

static uint64_t fnv1a_hash(const void *data, size_t len) {
    const uint8_t *ptr = (const uint8_t *)data;
    uint64_t hash = FNV_OFFSET;
    for (size_t i = 0; i < len; ++i) {
        hash ^= ptr[i];
        hash *= FNV_PRIME;
    }
    return hash;
}

static uint64_t fnv1a_combine(uint64_t left, uint64_t right) {
    uint64_t hash = FNV_OFFSET;
    hash ^= left;  hash *= FNV_PRIME;
    hash ^= right; hash *= FNV_PRIME;
    return hash;
}

/* Структура запису таблиці */
typedef struct {
    uint64_t key_token;
    char key[32];
    char value[64];
    uint64_t timestamp;
    bool is_tombstone;
} DatabaseRecord;

/* Структура бінарного дерева Меркла */
typedef struct {
    uint64_t nodes[TREE_SIZE];
    uint64_t leaf_counts[NUM_LEAVES];
} MerkleTree;

/* Ініціалізація дерева */
void merkle_init(MerkleTree *tree) {
    memset(tree->nodes, 0, sizeof(tree->nodes));
    memset(tree->leaf_counts, 0, sizeof(tree->leaf_counts));
}

/* Додавання запису до листка дерева */
void merkle_add_record(MerkleTree *tree, const DatabaseRecord *rec) {
    /* Обчислюємо індекс листка за старшими бітами токена */
    uint32_t leaf_idx = (uint32_t)(rec->key_token >> (64 - MERKLE_DEPTH));
    uint32_t node_idx = NUM_LEAVES + leaf_idx;

    /* Хешуємо вміст запису */
    uint64_t rec_hash = fnv1a_hash(rec->key, strlen(rec->key));
    rec_hash = fnv1a_combine(rec_hash, fnv1a_hash(rec->value, strlen(rec->value)));
    rec_hash = fnv1a_combine(rec_hash, rec->timestamp);
    rec_hash = fnv1a_combine(rec_hash, (uint64_t)rec->is_tombstone);

    /* Акумулюємо хеш у листку */
    if (tree->leaf_counts[leaf_idx] == 0) {
        tree->nodes[node_idx] = rec_hash;
    } else {
        tree->nodes[node_idx] = fnv1a_combine(tree->nodes[node_idx], rec_hash);
    }
    tree->leaf_counts[leaf_idx]++;
}

/* Згортання дерева знизу вгору (Bottom-Up Rollup) */
void merkle_build(MerkleTree *tree) {
    for (int i = NUM_LEAVES - 1; i >= 1; --i) {
        uint64_t left = tree->nodes[2 * i];
        uint64_t right = tree->nodes[2 * i + 1];
        if (left == 0 && right == 0) {
            tree->nodes[i] = 0;
        } else {
            tree->nodes[i] = fnv1a_combine(left, right);
        }
    }
}

/* Рекурсивний пошук розбіжних листків */
void merkle_find_diffs(const MerkleTree *a, const MerkleTree *b, 
                       uint32_t node_idx, uint32_t depth,
                       uint32_t *diff_leaves, uint32_t *diff_count) {
    if (a->nodes[node_idx] == b->nodes[node_idx]) {
        return; /* Піддерева повністю ідентичні, пропускаємо */
    }

    if (depth == MERKLE_DEPTH) {
        /* Досягнуто листка з розбіжністю */
        diff_leaves[(*diff_count)++] = node_idx - NUM_LEAVES;
        return;
    }

    /* Спускаємося до лівого та правого нащадків */
    merkle_find_diffs(a, b, 2 * node_idx, depth + 1, diff_leaves, diff_count);
    merkle_find_diffs(a, b, 2 * node_idx + 1, depth + 1, diff_leaves, diff_count);
}

int main(void) {
    MerkleTree node_a, node_b;
    merkle_init(&node_a);
    merkle_init(&node_b);

    /* Спільний набір даних */
    DatabaseRecord r1 = { 0x1000000000000000ULL, "user:101", "Alice", 1000, false };
    DatabaseRecord r2 = { 0x4000000000000000ULL, "user:102", "Bob",   1000, false };
    DatabaseRecord r3 = { 0x8000000000000000ULL, "user:103", "Carol", 1000, false };

    merkle_add_record(&node_a, &r1);
    merkle_add_record(&node_a, &r2);
    merkle_add_record(&node_a, &r3);

    merkle_add_record(&node_b, &r1);
    merkle_add_record(&node_b, &r2);
    merkle_add_record(&node_b, &r3);

    /* Вузол A отримав оновлення, яке вузол B пропустив через мережевий збій */
    DatabaseRecord r4 = { 0xC000000000000000ULL, "user:104", "Dave_Updated", 2000, false };
    merkle_add_record(&node_a, &r4);

    merkle_build(&node_a);
    merkle_build(&node_b);

    printf("Корінь Репліки A: 0x%016llX\n", (unsigned long long)node_a.nodes[1]);
    printf("Корінь Репліки B: 0x%016llX\n", (unsigned long long)node_b.nodes[1]);

    uint32_t diff_leaves[NUM_LEAVES];
    uint32_t diff_count = 0;
    merkle_find_diffs(&node_a, &node_b, 1, 0, diff_leaves, &diff_count);

    printf("Знайдено розбіжних листків: %u\n", diff_count);
    for (uint32_t i = 0; i < diff_count; ++i) {
        uint64_t range_start = (uint64_t)diff_leaves[i] << (64 - MERKLE_DEPTH);
        uint64_t range_end = range_start + (1ULL << (64 - MERKLE_DEPTH)) - 1;
        printf("  -> Листок %u: діапазон токенів [0x%016llX, 0x%016llX]\n",
               diff_leaves[i], (unsigned long long)range_start, (unsigned long long)range_end);
    }

    return 0;
}
```

@tab C++

```cpp
#include <iostream>
#include <vector>
#include <array>
#include <string>
#include <string_view>
#include <cstdint>
#include <iomanip>

namespace storage {

constexpr size_t MerkleDepth = 3;
constexpr size_t NumLeaves = 1ULL << MerkleDepth;
constexpr size_t TreeSize = 1ULL << (MerkleDepth + 1);

constexpr uint64_t FnvOffset = 14695981039346656037ULL;
constexpr uint64_t FnvPrime  = 1099511628211ULL;

[[nodiscard]] constexpr uint64_t fnv1a(std::string_view data) noexcept {
    uint64_t hash = FnvOffset;
    for (char c : data) {
        hash ^= static_cast<uint8_t>(c);
        hash *= FnvPrime;
    }
    return hash;
}

[[nodiscard]] constexpr uint64_t fnv1a_combine(uint64_t left, uint64_t right) noexcept {
    uint64_t hash = FnvOffset;
    hash ^= left;  hash *= FnvPrime;
    hash ^= right; hash *= FnvPrime;
    return hash;
}

struct Record {
    uint64_t key_token;
    std::string key;
    std::string value;
    uint64_t timestamp;
    bool is_tombstone{false};

    [[nodiscard]] uint64_t hash() const noexcept {
        uint64_t h = fnv1a(key);
        h = fnv1a_combine(h, fnv1a(value));
        h = fnv1a_combine(h, timestamp);
        h = fnv1a_combine(h, static_cast<uint64_t>(is_tombstone));
        return h;
    }
};

class MerkleTree {
public:
    MerkleTree() {
        nodes_.fill(0);
        leaf_counts_.fill(0);
    }

    void add_record(const Record& rec) noexcept {
        const size_t leaf_idx = static_cast<size_t>(rec.key_token >> (64 - MerkleDepth));
        const size_t node_idx = NumLeaves + leaf_idx;

        const uint64_t h = rec.hash();
        if (leaf_counts_[leaf_idx] == 0) {
            nodes_[node_idx] = h;
        } else {
            nodes_[node_idx] = fnv1a_combine(nodes_[node_idx], h);
        }
        leaf_counts_[leaf_idx]++;
    }

    void build() noexcept {
        for (size_t i = NumLeaves - 1; i >= 1; --i) {
            const uint64_t left = nodes_[2 * i];
            const uint64_t right = nodes_[2 * i + 1];
            if (left == 0 && right == 0) {
                nodes_[i] = 0;
            } else {
                nodes_[i] = fnv1a_combine(left, right);
            }
        }
    }

    [[nodiscard]] uint64_t root() const noexcept {
        return nodes_[1];
    }

    [[nodiscard]] static std::vector<size_t> find_differences(
        const MerkleTree& a, const MerkleTree& b) {
        std::vector<size_t> diff_leaves;
        diff_leaves.reserve(NumLeaves);
        find_diffs_recursive(a, b, 1, 0, diff_leaves);
        return diff_leaves;
    }

private:
    static void find_diffs_recursive(
        const MerkleTree& a, const MerkleTree& b,
        size_t node_idx, size_t depth,
        std::vector<size_t>& diffs) {
        if (a.nodes_[node_idx] == b.nodes_[node_idx]) {
            return;
        }

        if (depth == MerkleDepth) {
            diffs.push_back(node_idx - NumLeaves);
            return;
        }

        find_diffs_recursive(a, b, 2 * node_idx, depth + 1, diffs);
        find_diffs_recursive(a, b, 2 * node_idx + 1, depth + 1, diffs);
    }

    std::array<uint64_t, TreeSize> nodes_;
    std::array<size_t, NumLeaves> leaf_counts_;
};

} // namespace storage

int main() {
    using namespace storage;

    MerkleTree node_a;
    MerkleTree node_b;

    const Record r1{ 0x1000000000000000ULL, "user:101", "Alice", 1000, false };
    const Record r2{ 0x4000000000000000ULL, "user:102", "Bob",   1000, false };
    const Record r3{ 0x8000000000000000ULL, "user:103", "Carol", 1000, false };

    node_a.add_record(r1); node_a.add_record(r2); node_a.add_record(r3);
    node_b.add_record(r1); node_b.add_record(r2); node_b.add_record(r3);

    const Record r4{ 0xC000000000000000ULL, "user:104", "Dave_Updated", 2000, false };
    node_a.add_record(r4);

    node_a.build();
    node_b.build();

    std::cout << std::hex << std::uppercase << std::setfill('0');
    std::cout << "Корінь Репліки A: 0x" << std::setw(16) << node_a.root() << "\n";
    std::cout << "Корінь Репліки B: 0x" << std::setw(16) << node_b.root() << "\n";

    const auto diffs = MerkleTree::find_differences(node_a, node_b);
    std::cout << std::dec << "Знайдено розбіжних листків: " << diffs.size() << "\n";

    for (size_t leaf : diffs) {
        const uint64_t range_start = static_cast<uint64_t>(leaf) << (64 - MerkleDepth);
        const uint64_t range_end = range_start + (1ULL << (64 - MerkleDepth)) - 1;
        std::cout << "  -> Листок " << leaf << ": діапазон токенів [0x"
                  << std::hex << std::setw(16) << range_start << ", 0x"
                  << std::setw(16) << range_end << "]\n" << std::dec;
    }

    return 0;
}
```

:::

---

## 4. Покроковий розбір трасування виконання

Розглянемо покрокове виконання наведеної програми для розуміння механізму роботи алгоритму:

1. **Ініціалізація дерев:**
   Обидва вузли виділяють масиви з 16 елементів і заповнюють їх нулями.
2. **Додавання однакових записів `r1`, `r2`, `r3`:**
   - Запис `r1` (`0x1000...`): старші 3 біти = `001₂ = 1`. Записується в листок 1 (`array_index = 8 + 1 = 9`).
   - Запис `r2` (`0x4000...`): старші 3 біти = `010₂ = 2`. Записується в листок 2 (`array_index = 8 + 2 = 10`).
   - Запис `r3` (`0x8000...`): старші 3 біти = `100₂ = 4`. Записується в листок 4 (`array_index = 8 + 4 = 12`).
3. **Додавання неузгодженого запису `r4` на Репліку A:**
   - Запис `r4` (`0xC000...`): старші 3 біти = `110₂ = 6`. Записується в листок 6 (`array_index = 8 + 6 = 14`).
   - На Репліці B листок 6 залишається порожнім (`nodes[14] == 0`).
4. **Згортання (Rollup):**
   - На Репліці A вузол 7 обчислюється як `fnv1a_combine(nodes[14], nodes[15])` і отримує ненульовий хеш.
   - Корінь `nodes[1]` на Репліці A формується комбінацією лівого і правого піддерев.
   - Оскільки на Репліці B листок 6 порожній, `nodes[7]` та `nodes[1]` на Репліці B мають зовсім інші хеші.
5. **Бінарний спуск (Traversal):**
   - На рівні 0: `nodes[1]` не збігаються. Алгоритм викликає перевірку лівого нащадка (`nodes[2]`) та правого (`nodes[3]`).
   - На рівні 1:
     - `nodes[2]` (покриває листки 0..3): хеші на обох вузлах повністю ідентичні! Рекурсія для лівого піддерева негайно зупиняється без жодного подальшого виклику.
     - `nodes[3]` (покриває листки 4..7): хеші відрізняються. Рекурсія спускається до `nodes[6]` та `nodes[7]`.
   - На рівні 2:
     - `nodes[6]` (покриває листки 4..5): хеші ідентичні (обидва містять запис `r3` у листку 4). Гілка негайно відсікається.
     - `nodes[7]` (покриває листки 6..7): хеші відрізняються. Спуск до листків 14 і 15.
   - На рівні 3 (листки):
     - Вузол 14 (листок 6): хеші відрізняються. Листок 6 реєструється як розбіжний.
     - Вузол 15 (листок 7): обидва нульові (збігаються).

Замість повного порівняння всіх записів таблиці алгоритм відкинув 7 із 8 листків усього за 3 скалярні операції порівняння 64-бітних чисел на процесорі.

---

## 5. Паралельне сканування кількох SSTables (K-Way Merge Iterator)

У промислових сховищах на базі LSM-дерев дані розподілені між багатьма незмінними файлами SSTables на різних рівнях ущільнення (Levels 0..L). Один і той самий первинний ключ може міститися в кількох файлах з різними часовими мітками. Якщо сканувати файли окремо, дерево Меркла отримає дублікати ключів і буде сформовано некоректний корінь.

Щоб дерево отримало детермінований і очищений набір найсвіжіших даних, процес побудови виконує **K-Way злиття через чергу з пріоритетами (Min-Heap)**:

```
[SSTable L0_1] ---> Iterator 1 ──┐
[SSTable L0_2] ---> Iterator 2 ──┼──> [ Min-Heap Priority Queue ] ──> [ Deduplicated Record ] ──> MerkleTree
[SSTable L1_1] ---> Iterator 3 ──┘          (Key ASC, TS DESC)
```

1. Ітератори всіх активних файлів таблиці ініціалізуються на першому записі та додаються до бінарної мін-купи.
2. Мін-купа сортує ітератори за первинним ключем (за зростанням), а для однакових ключів — за часовою міткою `timestamp` (за спаданням).
3. Головний цикл зчитує верхній елемент купи:
   - Якщо ключ збігається з попереднім обробленим ключем, поточний запис є застарілою тінню (shadowed update) і просто відкидається.
   - Якщо ключ новий, він передається в метод `merkle_add_record`.
4. Відповідний ітератор просувається на один запис уперед у своєму файлі та реорганізує купу за час `O(log K)`.

Така архітектура гарантує, що побудова дерева Меркла на обох репліках виконується строго над консолідованим логічним станом бази даних, навіть якщо фізичне розташування даних по SSTable-файлах на серверах відрізняється через незалежні цикли фонової компакції.

---

## 6. Механізм потокової передачі та вирішення конфліктів (LWW Resolution)

Після виявлення розбіжності для листка 6 репліки переходять до фази потокової синхронізації знайденого діапазону токенів `[0xC000000000000000, 0xDFFFFFFFFFFFFFFF]`.

```
Репліка B (Coordinator)                         Репліка A (Sender)
      │                                                │
      │──── 1. GetRangeStream(Leaf 6: [0xC000...]) ───>│
      │                                                │ [Відкриває SSTable]
      │                                                │ [Читає записи листка 6]
      │<─── 2. StreamData(Record r4, TS: 2000) ────────│
      │                                                │
[Виконує LWW злиття]                                   │
[Записує нову мутацію]                                 │
```

Коли Репліка B отримує запис `r4`, вона застосовує детерміновану матрицю вирішення конфліктів Last-Write-Wins:

| Локальний стан на Репліці B | Вхідний запис від Репліки A | Правило Last-Write-Wins | Результат на Репліці B |
| :--- | :--- | :--- | :--- |
| Запис відсутній | `r4 (v="Dave_Updated", TS=2000)` | Вхідний запис новіший за порожнечу | Запис створюється (`TS=2000`) |
| Запис існує (`TS=1000`) | `r4 (v="Dave_Updated", TS=2000)` | `TS_incoming > TS_local` | Локальний запис перезаписується |
| Запис існує (`TS=3000`) | `r4 (v="Dave_Updated", TS=2000)` | `TS_incoming < TS_local` | Вхідний запис ігнорується |
| Запис існує (`TS=1000`) | Надгробок `(Tombstone, TS=2000)` | `TS_incoming > TS_local` | Створюється надгробок (`TS=2000`) |
| Надгробок `(TS=1000)` | Запис `(v="Dave", TS=2000)` | `TS_incoming > TS_local` | Запис оживає зі свіжим `TS=2000` |
| Надгробок `(TS=2000)` | Запис `(v="Dave", TS=1000)` | `TS_local > TS_incoming` | Запис блокується надгробком |

Така семантика забезпечує математичну збіжність стану кластера до однакового детермінованого значення незалежно від порядку доставки мережевих пакетів.

---

## 7. Кільцевий буфер, Zero-Copy I/O та обмеження швидкості

Під час потокової передачі смуг даних головним ризиком є перевантаження мережевого стека та накопичувачів, що може спричинити деградацію клієнтського трафіку (latency spikes). Промислові рушії використовують такі низькорівневі оптимізації ядра:

### 7.1. Системний виклик `sendfile(2)` та Zero-Copy передача

Замість копіювання байтів з диска в буфер користувацького простору (`read`), а потім із простору користувача в сокет ядра (`write`), потоковий рушій передає файлові дескриптори безпосередньо через пам'ять ядра ОС:

:::tabs

@tab C

```c
/* Передача фрагмента SSTable напряму в мережевий сокет без копіювання в RAM */
off_t offset = range_offset_start;
size_t count = range_length_bytes;
ssize_t sent = sendfile(socket_fd, sstable_fd, &offset, count);
```

@tab C++

```cpp
// Передача фрагмента SSTable через POSIX sendfile з RAII дескрипторами
off_t offset = range_offset_start;
const size_t count = range_length_bytes;
const ssize_t sent = ::sendfile(socket.native_handle(), file.native_handle(), &offset, count);
```

:::

Це скорочує кількість перемикань контексту процесора з чотирьох до двох на кожну транзакцію та усуває навантаження на шину пам'яті сервера.

### 7.2. Маркерне відро (Token Bucket Rate Limiting)

Для обмеження максимальної швидкості передачі даних ремонтної сесії (параметр `stream_throughput_outbound_megabits_per_sec`) впроваджується алгоритм Token Bucket:

```cpp
class TokenBucketLimiter {
public:
    explicit TokenBucketLimiter(uint64_t bytes_per_sec)
        : rate_bytes_per_sec_(bytes_per_sec),
          available_tokens_(bytes_per_sec),
          last_refill_time_(get_monotonic_time_ns()) {}

    void throttle(uint64_t bytes_to_send) {
        refill();
        while (available_tokens_ < bytes_to_send) {
            uint64_t missing = bytes_to_send - available_tokens_;
            uint64_t sleep_ns = (missing * 1'000'000'000ULL) / rate_bytes_per_sec_;
            sleep_nanoseconds(sleep_ns);
            refill();
        }
        available_tokens_ -= bytes_to_send;
    }

private:
    void refill() {
        uint64_t now = get_monotonic_time_ns();
        uint64_t elapsed_ns = now - last_refill_time_;
        uint64_t added_tokens = (elapsed_ns * rate_bytes_per_sec_) / 1'000'000'000ULL;
        if (added_tokens > 0) {
            available_tokens_ = std::min(available_tokens_ + added_tokens, rate_bytes_per_sec_);
            last_refill_time_ = now;
        }
    }

    uint64_t rate_bytes_per_sec_;
    uint64_t available_tokens_;
    uint64_t last_refill_time_;
};
```

Перед кожним викликом `sendfile` або відправкою чергового пакету потік ремонту викликає `limiter.throttle(chunk_size)`. Якщо квоту вичерпано, потік засинає через високоточний таймер `nanosleep`, звільняючи процесорні ядра та смугу пропускання мережевої карти для обробки оперативних клієнтських запитів читання й запису.

---

## 8. Проектування бінарного протоколу обміну (Network Wire Framing)

Для передачі структур дерев Меркла між серверами використовується бінарний компактний протокол без додаткового виділення динамічної пам'яті (Zero-Allocation Wire Format).

Структура повідомлення складається з фіксованого заголовка та тіла змінної довжини:

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|       Magic (0x52455041)      |  Version (1)  | MsgType (0x02)|
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                     Session UUID (16 Bytes)                   |
|                                                               |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|          Tree Depth (1 Byte)  |       Reserved (3 Bytes)      |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                   Payload Length (4 Bytes)                    |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                   Merkle Tree Nodes Data ...                  |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                       CRC-32 Checksum                         |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

Типи повідомлень (`MsgType`):
- `0x01` (`MERKLE_REQUEST`): запит на обчислення дерева для вказаного діапазону токенів;
- `0x02` (`MERKLE_RESPONSE`): повернення серіалізованого масиву вузлів дерева;
- `0x03` (`DIFF_RANGES_LIST`): перелік діапазонів ливарних токенів, що потребують потокової передачі;
- `0x04` (`STREAM_DATA_CHUNK`): блок серіалізованих записів таблиці;
- `0x05` (`STREAM_COMPLETE_ACK`): підтвердження успішного прийому та перевірки цілісності фрагмента.

Такий суворий бінарний формат усуває витрати на текстовий парсинг JSON або XML і дозволяє десеріалізувати масиви хешів прямим відображенням байтів у пам'ять (Direct Memory Cast).

---

## 9. Асинхронна архітектура потоків (Thread-per-Core Model)

Сучасні високоефективні рушії (наприклад, ScyllaDB на базі фреймворку Seastar) відмовляються від традиційної моделі пулу потоків з блокуючими м'ютексами. Замість цього застосовується архітектура **Thread-per-Core (Shared-Nothing)**:

1. Кожне фізичне ядро процесора закріплюється за окремим системним потоком (`core affinity`).
2. Кожен потік (shard) монопольно володіє власним неперетинним підмножиною токенів і пам'яттю.
3. Побудова дерева Меркла виконується реактивно через неблокуючі черги завдань:
   - Потік зчитує блоки SSTable через несинхронний дисковий інтерфейс `io_uring` або `libaio`.
   - Обчислення хешів розбивається на кванти часу (time slices) по 500 мікросекунд, повертаючи керування реактору подій між порціями.
4. Якщо запит на ремонт охоплює діапазон кількох шардів, кожен шард будує власне локальне піддерево, після чого результати агрегуються через легковажні черги повідомлень без блокувань (lock-free SPSC queues).

Така реактивна модель унеможливлює зависання реактора та гарантує, що час відповіді (latency p99) основних клієнтських транзакцій читання і запису залишається меншим за 2 мілісекунди навіть під час інтенсивної побудови дерев Меркла.

---

## 10. Контроль бюджету оперативної пам'яті (Memory Budget & Backpressure)

Коли кластер обслуговує тисячі таблиць та сотні vnodes, одночасний запуск ремонту може спровокувати вичерпання оперативної пам'яті (Out-Of-Memory, OOM).

Для запобігання падінню процесів впроваджується глобальний лімітер пам'яті ремонту (`RepairMemoryLimiter`):
- Кожна ініційована сесія запитує квоту оперативної пам'яті розміром `(2^(DEPTH + 1) · 8 Б) + BufferSize`. Для дерева глибини 15 це становить близько 1.5 МБ.
- Якщо сумарна виділена пам'ять перевищує поріг `repair_session_space_in_mb` (типово 512 МБ), нові запити на побудову дерев не відхиляються з помилкою, а переходять у стан очікування `WAITING_FOR_MEMORY` у пріоритетній черзі сесій.
- Після завершення діагностики та передачі смуг даних виділена пам'ять повертається до пулу, автоматично активуючи наступну сесію з черги.

Цей механізм зворотного тиску (backpressure) гарантує залізобетонну стабільність демона бази даних навіть під час екстремального пікового навантаження на систему.

---

## 11. Повна кінцева машина станів сесії ремонту (Repair Session State Machine)

Кожна сесія анти-ентропійного ремонту виконується як детермінований скінченний автомат:

```
[INIT] ──> [SNAPSHOT] ──> [BUILD_TREES] ──> [DIFF_TREES] ──> [STREAMING] ──> [COMMIT] ──> [CLEANUP]
  │           │                │                 │                │
  └─── Відмова на будь-якому кроці ──────────────┴────────────────┴──────────> [ROLLBACK_AND_FAIL]
```

1. **`INIT`:** Валідація життєздатності всіх реплік, перевірка версій схеми даних та виділення слота пам'яті.
2. **`SNAPSHOT`:** Створення файлових жорстких посилань для фіксації незмінного зрізу SSTables.
3. **`BUILD_TREES`:** Послідовне K-Way сканування та заповнення масиву дерева Меркла.
4. **`DIFF_TREES`:** Бінарний рекурсивний спуск між репліками та визначення несинхронізованих ливарних діапазонів.
5. **`STREAMING`:** Потокова передача відсутніх мутацій з урахуванням обмеження швидкості Token Bucket.
6. **`COMMIT`:** Атомарне перейменування `.tmp` файлів на стороні одержувача та маркування діапазону як `Repaired`.
7. **`CLEANUP`:** Видалення тимчасових знімків файлової системи та повернення квоти пам'яті до пулу.

У разі виникнення таймауту або мережевого збою на будь-якому кроці автомат негайно переходить у стан `ROLLBACK_AND_FAIL`, безпечно видаляючи незавершені файли без пошкодження цілісності бази даних.

---

## 12. Профайлінг та аналіз апаратних метрик (Profiling & Bottlenecks)

При розгортанні анти-ентропійного рушія на багатоядерних серверах критично важливо аналізувати розподіл процесорного часу за допомогою інструментів системного аналізу Linux `perf` та eBPF:

```bash
# Профайлінг сесії побудови дерева Меркла за допомогою Linux perf
perf record -F 99 -g -p $(pgrep scylla) -- sleep 30
perf report -n --stdio
```

Типовий профіль навантаження процесора при оптимальній реалізації демонструє таку картину:
- **60–65% CPU:** дисковий I/O та десеріалізація блоків SSTable з формату LZ4/ZSTD;
- **20–25% CPU:** обчислення хеш-функції записів (Murmur3 / FNV-1a);
- **8–10% CPU:** операції вставки та оновлення бінарної мін-купи K-Way Merge;
- **< 2% CPU:** бінарний спуск та мережеве пакування повідомлень.

Якщо профайлер фіксує понад 5% часу в системних викликах ядра `sys_futex` або значну кількість подій `L1-dcache-load-misses`, це свідчить про наявність блокувань або неправильне динамічне виділення пам'яті всередині циклу сканування, що вимагає негайного переходу на одновимірний масив і thread-local буферизацію.

---

## 13. Практичний чекліст оптимізації операційної системи (Production Tuning)

Для досягнення максимальної швидкості роботи анти-ентропійного відновлення без деградації кластера необхідно налаштувати параметри ядра ОС Linux:

```bash
# Збільшення розміру буферів прийому та відправки мережевого стека для високих швидкостей потокової передачі
sysctl -w net.core.rmem_max=16777216
sysctl -w net.core.wmem_max=16777216
sysctl -w net.ipv4.tcp_rmem="4096 87380 16777216"
sysctl -w net.ipv4.tcp_wmem="4096 65536 16777216"

# Оптимізація поведінки фонового скидання брудних сторінок пам'яті на диск
sysctl -w vm.dirty_background_ratio=5
sysctl -w vm.dirty_ratio=10

# Вимкнення агресивного swap-механізму для захисту процесів бази даних від затримок
sysctl -w vm.swappiness=1
```

У конфігураційних файлах СУБД рекомендується встановити:
- `stream_throughput_outbound_megabits_per_sec`: `200–400` Мбіт/с на гігабітних мережах (або `2000` Мбіт/с на 10-гігабітних інтерфейсах);
- `repair_session_max_tree_depth`: `15` (оптимум між пам'яттю та гранулярністю передачі);
- `concurrent_merkle_tree_builds`: не більше ніж `2` на фізичний накопичувач NVMe, щоб запобігти вичерпанню черги дискових операцій IOPS.

Системний адміністратор також може перевірити активні сесії та відстежити швидкість потоків за допомогою стандартних утиліт командного рядка:
```bash
# Моніторинг активних ремонтних сесій та потокової передачі в Cassandra
nodetool netstats
nodetool repair_admin list
```

---

## 14. Обробка крайових випадків та системна відмовостійкість

У розподіленому середовищі алгоритм анти-ентропії стикається з низкою критичних аномалій:

```
+-------------------------------------------------------------------------------+
| Сценарій 1: Обрив TCP-з'єднання посеред потокової передачі SSTable            |
| • Проблема: Одержувач отримав половину файлу діапазону.                       |
| • Вирішення: Усі вхідні файли записуються з суфіксом .tmp (наприклад,         |
|   123_repair.db.tmp). Лише після отримання фінального підтвердження контрольної|
|   суми (CRC32/SHA256) файл атомарно перейменовується через rename(2).         |
|   У разі тайм-ауту незавершені .tmp файли видаляються без пошкодження бази.   |
+-------------------------------------------------------------------------------+
| Сценарій 2: Зміна топології кільця (Node Join / Decommission)                 |
| • Проблема: Під час ремонту діапазон токенів перерозподілився на новий вузол. |
| • Вирішення: Сесія ремонту підписана на Gossip-події кластера. При зміні     |
|   карти токенів координатор генерує TokenRangeMovementException, негайно      |
|   зупиняє спуск і відкидає часткові результати сесії.                         |
+-------------------------------------------------------------------------------+
| Сценарій 3: Конкурентне видалення старих SSTables процесом Compaction          |
| • Проблема: Під час сканування для побудови дерева фонове ущільнення          |
|   видаляє вихідні файли таблиці.                                              |
| • Вирішення: Перед запуском побудови дерева вузол створює hard link (snapshot)|
|   файлів SSTable. Linux/UNIX не видаляє inode з диска, доки лічильник посилань|
|   nlink > 0, навіть якщо фоновий процес викликав unlink() для оригінального   |
|   імені файлу.                                                                |
+-------------------------------------------------------------------------------+
```

Завдяки поєднанню атомарних операцій файлової системи, K-Way злиття на рівні ітераторів, маніпуляцій з інодами через жорсткі посилання, Thread-per-Core реактивної моделі, суворого контролю бюджету оперативної пам'яті та детермінованого бінарного спуску над одновимірним масивом досягається максимальна надійність і швидкість відновлення консистентності розподілених даних.
Це створює надійну практичну основу для побудови безвідмовних високопродуктивних розподілених сховищ, здатних витримувати масштабні мережеві збої, апаратні аварії та втрати окремих вузлів без найменшої загрози втрати цілісності даних.
Така комплексна інженерна реалізація гарантує, що система підтримує гарантії кінцевої узгодженості в автоматичному фоновому режимі 24/7.
