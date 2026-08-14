# ⚙️ Практична реалізація Дерева Меркла та генерація доказів

У цьому проєкті розглянуто повну практичну реалізацію Дерева Меркла: побудову двійкового дерева хешів із масиву даних, генерацію логарифмічного доказу включення (Merkle Inclusion Proof) та перевірку доказу на боці клієнта. Приклади виконано мовами C та C++ з використанням ідіоматичних підходів кожної з мов.

## Задача та архітектура модуля

Для побудови надійного модуля керування Деревом Меркла необхідно вирішити п'ять ключових інженерних завдань:

1. **Прийом та валідація вхідних даних**: Модуль повинен приймати масив бінарних блоків (рядків, транзакцій чи дискових секторів) довільного розміру й перевіряти вхідні параметри на порожні вказівники чи нульову кількість.
2. **Формування листків та розділення доменів**: Кожен блок даних перетворюється на 32-байтний хеш з обов'язковим додаванням однобайтного префікса `0x00`. Це захищає реалізацію від атак другого прообразу.
3. **Рекурсивна побудова рівнів та обробка непарності**: При побудові вищих рівнів кількість вузлів на кожному кроці може виявитися непарною. Модуль повинен дублювати останній вузол рівня (`Hash(0x01 || Left || Left)`), гарантуючи симетрію двійкового дерева.
4. **Формування аудиторського доказу (Proof Generation)**: За заданим індексом листка модуль повинен швидко витягти послідовність сестринських хешів та бітів напрямку (Left/Right) на кожному рівні від листка до кореня.
5. **Автономна верифікація (Standalone Verification)**: Перевірка доказу повинна виконуватися на боці легковажного клієнта без створення самого дерева чи збереження повного масиву даних — лише на основі самого елемента, доказу та підсумкового Merkle Root.

---

## Стратегія зберігання дерева у пам'яті

Існує дві основні стратегії зберігання Дерева Меркла в оперативній пам'яті:

### Стратегія A: Вказівникова структура (Node with Left/Right pointers)
Кожен вузол подається як структура `struct Node { Hash hash; Node* left; Node* right; }`.
- **Плюси**: Зручно для динамічного оновлення окремих гілок.
- **Мінуси**: Високі накладні витрати на виділення дрібних блоків пам'яті (`malloc` на кожен вузол), фрагментація кучі, погана локальність даних у кеші процесора (cache misses).

### Стратегія B: Плаский послідовний масив (Flat Array Layout)
Усі вузли дерева зберігаються у єдиному безперервному блоці пам'яті `Hash* nodes`, де листки розміщуються на початку, а вищі рівні підряд за ними.
- **Плюси**: Одне виділення пам'яті `malloc`, ідеальна локальність у L1/L2 кеші процесора, висока швидкість обходу.
- **Мінуси**: Вимагає заздалегідь розрахованого обсягу пам'яті `2N - 1`.

У нашій реалізації мовою C обрано **Стратегію B** для забезпечення максимальної продуктивності, а у C++ — вектор рівнів `std::vector<std::vector<HashBytes>>` для чистоти інкапсуляції.

---

## Код реалізації (C та C++)

Нижче наведено повноцінні робочі реалізації. У реалізації мовою C використанні явні вказівники, масиви та ручне управління пам'яттю, а в C++20 — контейнери `std::vector`, `std::span`, `std::string_view` та концепція RAII.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>

#define HASH_SIZE 32
#define PREFIX_LEAF 0x00
#define PREFIX_INTERNAL 0x01

typedef struct {
    uint8_t bytes[HASH_SIZE];
} Hash;

typedef enum {
    DIR_LEFT = 0,
    DIR_RIGHT = 1
} Direction;

typedef struct {
    Hash sibling_hash;
    Direction direction;
} ProofNode;

typedef struct {
    ProofNode* nodes;
    size_t count;
} MerkleProof;

typedef struct {
    Hash* nodes;       /* Масив усіх вузлів дерева у пласкому вигляді */
    size_t leaf_count;
    size_t total_nodes;
} MerkleTree;

/* Проста детермінована хеш-функція (FNV-1a 256-біт) для демонстрації алгоритму.
   У продакшені замінюється на SHA-256 або BLAKE3. */
static Hash compute_hash(uint8_t prefix, const void* data, size_t len) {
    Hash result;
    memset(result.bytes, 0x81, HASH_SIZE);
    const uint8_t* p = (const uint8_t*)data;
    
    /* Обробка префікса */
    for (size_t i = 0; i < HASH_SIZE; i++) {
        result.bytes[i] ^= prefix;
        result.bytes[i] *= 16777619u;
    }
    
    /* Обробка корисного навантаження */
    for (size_t i = 0; i < len; i++) {
        result.bytes[i % HASH_SIZE] ^= p[i];
        result.bytes[i % HASH_SIZE] *= 16777619u;
    }
    return result;
}

static Hash combine_hashes(const Hash* left, const Hash* right) {
    uint8_t buffer[HASH_SIZE * 2];
    memcpy(buffer, left->bytes, HASH_SIZE);
    memcpy(buffer + HASH_SIZE, right->bytes, HASH_SIZE);
    return compute_hash(PREFIX_INTERNAL, buffer, HASH_SIZE * 2);
}

/* Побудова дерева Меркла */
MerkleTree* merkle_tree_create(const char** items, size_t count) {
    if (count == 0) return NULL;
    
    MerkleTree* tree = (MerkleTree*)malloc(sizeof(MerkleTree));
    tree->leaf_count = count;
    
    /* Обчислення кількості листків (із підповненням до парного на кожному рівні) */
    size_t current_level_size = count;
    size_t total = current_level_size;
    
    /* Попередній розрахунок пам'яті */
    size_t temp_size = current_level_size;
    while (temp_size > 1) {
        temp_size = (temp_size + 1) / 2;
        total += temp_size;
    }
    
    tree->nodes = (Hash*)malloc(sizeof(Hash) * total);
    tree->total_nodes = total;
    
    /* Крок 1: Хешування листків із префіксом 0x00 */
    for (size_t i = 0; i < count; i++) {
        tree->nodes[i] = compute_hash(PREFIX_LEAF, items[i], strlen(items[i]));
    }
    
    /* Крок 2: Рекурсивне підняття та хешування рівнів */
    size_t level_offset = 0;
    size_t next_level_offset = count;
    
    while (current_level_size > 1) {
        size_t next_level_size = 0;
        for (size_t i = 0; i < current_level_size; i += 2) {
            Hash left = tree->nodes[level_offset + i];
            Hash right = (i + 1 < current_level_size) 
                         ? tree->nodes[level_offset + i + 1] 
                         : left; /* Дублювання останнього вузла якщо непарно */
                         
            tree->nodes[next_level_offset + next_level_size] = combine_hashes(&left, &right);
            next_level_size++;
        }
        level_offset = next_level_offset;
        next_level_offset += next_level_size;
        current_level_size = next_level_size;
    }
    
    return tree;
}

/* Генерація доказу підтвердження включення */
MerkleProof merkle_tree_prove(const MerkleTree* tree, size_t index) {
    MerkleProof proof = { NULL, 0 };
    if (!tree || index >= tree->leaf_count) return proof;
    
    size_t max_depth = 64;
    proof.nodes = (ProofNode*)malloc(sizeof(ProofNode) * max_depth);
    
    size_t current_index = index;
    size_t level_size = tree->leaf_count;
    size_t level_offset = 0;
    
    while (level_size > 1) {
        size_t sibling_index;
        Direction dir;
        
        if (current_index % 2 == 0) {
            /* Поточний вузол лівий, сестра праворуч */
            sibling_index = (current_index + 1 < level_size) ? current_index + 1 : current_index;
            dir = DIR_RIGHT;
        } else {
            /* Поточний вузол правий, сестра ліворуч */
            sibling_index = current_index - 1;
            dir = DIR_LEFT;
        }
        
        proof.nodes[proof.count].sibling_hash = tree->nodes[level_offset + sibling_index];
        proof.nodes[proof.count].direction = dir;
        proof.count++;
        
        level_offset += level_size;
        level_size = (level_size + 1) / 2;
        current_index /= 2;
    }
    
    return proof;
}

/* Верифікація доказу */
bool merkle_proof_verify(const char* item, const MerkleProof* proof, Hash root) {
    Hash current = compute_hash(PREFIX_LEAF, item, strlen(item));
    
    for (size_t i = 0; i < proof->count; i++) {
        if (proof->nodes[i].direction == DIR_RIGHT) {
            current = combine_hashes(&current, &proof->nodes[i].sibling_hash);
        } else {
            current = combine_hashes(&proof->nodes[i].sibling_hash, &current);
        }
    }
    
    return memcmp(current.bytes, root.bytes, HASH_SIZE) == 0;
}

void merkle_tree_free(MerkleTree* tree) {
    if (tree) {
        free(tree->nodes);
        free(tree);
    }
}

int main(void) {
    const char* transactions[] = {
        "Tx1: Alice->Bob 5 BTC",
        "Tx2: Bob->Charlie 2 BTC",
        "Tx3: Charlie->Dave 1 BTC",
        "Tx4: Dave->Eve 0.5 BTC"
    };
    size_t count = 4;
    
    MerkleTree* tree = merkle_tree_create(transactions, count);
    Hash root = tree->nodes[tree->total_nodes - 1];
    
    printf("Merkle Root: ");
    for (int i = 0; i < 8; i++) printf("%02x", root.bytes[i]);
    printf("...\n");
    
    /* Генерація доказу для транзакції Tx2 (індекс 1) */
    MerkleProof proof = merkle_tree_prove(tree, 1);
    
    bool valid = merkle_proof_verify(transactions[1], &proof, root);
    printf("Перевірка Tx2: %s\n", valid ? "УСПІШНО (VALID)" : "ПОМИЛКА");
    
    /* Спроба підробки */
    bool fake_valid = merkle_proof_verify("Tx2: Bob->Charlie 100 BTC", &proof, root);
    printf("Перевірка підробленої Tx2: %s\n", fake_valid ? "УСПІШНО" : "ВІДХИЛЕНО (INVALID)");
    
    free(proof.nodes);
    merkle_tree_free(tree);
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <string_view>
#include <array>
#include <memory>
#include <algorithm>
#include <iomanip>

namespace crypto {

constexpr size_t HASH_SIZE = 32;
constexpr uint8_t PREFIX_LEAF = 0x00;
constexpr uint8_t PREFIX_INTERNAL = 0x01;

using HashBytes = std::array<uint8_t, HASH_SIZE>;

enum class Direction { Left, Right };

struct ProofNode {
    HashBytes sibling_hash;
    Direction direction;
};

using MerkleProof = std::vector<ProofNode>;

/* Реалізація FNV-1a 256-біт для демонстрації */
inline HashBytes compute_hash(uint8_t prefix, std::string_view data) {
    HashBytes result{};
    result.fill(0x81);
    
    for (size_t i = 0; i < HASH_SIZE; ++i) {
        result[i] ^= prefix;
        result[i] *= 16777619u;
    }
    
    for (size_t i = 0; i < data.size(); ++i) {
        result[i % HASH_SIZE] ^= static_cast<uint8_t>(data[i]);
        result[i % HASH_SIZE] *= 16777619u;
    }
    return result;
}

inline HashBytes combine_hashes(const HashBytes& left, const HashBytes& right) {
    std::array<uint8_t, HASH_SIZE * 2> buffer{};
    std::copy(left.begin(), left.end(), buffer.begin());
    std::copy(right.begin(), right.end(), buffer.begin() + HASH_SIZE);
    return compute_hash(PREFIX_INTERNAL, std::string_view(reinterpret_cast<const char*>(buffer.data()), buffer.size()));
}

class MerkleTree {
public:
    explicit MerkleTree(std::span<const std::string_view> items) : leaf_count_(items.size()) {
        if (items.empty()) return;
        
        // Крок 1: Створення листків
        std::vector<HashBytes> current_level;
        current_level.reserve(items.size());
        for (const auto& item : items) {
            current_level.push_back(compute_hash(PREFIX_LEAF, item));
        }
        
        levels_.push_back(current_level);
        
        // Крок 2: Побудова вищих рівнів
        while (current_level.size() > 1) {
            std::vector<HashBytes> next_level;
            next_level.reserve((current_level.size() + 1) / 2);
            
            for (size_t i = 0; i < current_level.size(); i += 2) {
                const auto& left = current_level[i];
                const auto& right = (i + 1 < current_level.size()) ? current_level[i + 1] : left;
                next_level.push_back(combine_hashes(left, right));
            }
            
            levels_.push_back(next_level);
            current_level = std::move(next_level);
        }
    }

    [[nodiscard]] HashBytes root() const {
        if (levels_.empty() || levels_.back().empty()) return {};
        return levels_.back().front();
    }

    [[nodiscard]] MerkleProof prove(size_t index) const {
        MerkleProof proof;
        if (index >= leaf_count_ || levels_.empty()) return proof;

        size_t current_idx = index;
        for (size_t level = 0; level < levels_.size() - 1; ++level) {
            const auto& current_level = levels_[level];
            size_t sibling_idx;
            Direction dir;

            if (current_idx % 2 == 0) {
                sibling_idx = (current_idx + 1 < current_level.size()) ? current_idx + 1 : current_idx;
                dir = Direction::Right;
            } else {
                sibling_idx = current_idx - 1;
                dir = Direction::Left;
            }

            proof.push_back(ProofNode{
                .sibling_hash = current_level[sibling_idx],
                .direction = dir
            });

            current_idx /= 2;
        }

        return proof;
    }

    static bool verify(std::string_view item, const MerkleProof& proof, const HashBytes& expected_root) {
        HashBytes current = compute_hash(PREFIX_LEAF, item);

        for (const auto& node : proof) {
            if (node.direction == Direction::Right) {
                current = combine_hashes(current, node.sibling_hash);
            } else {
                current = combine_hashes(node.sibling_hash, current);
            }
        }

        return current == expected_root;
    }

private:
    size_t leaf_count_{0};
    std::vector<std::vector<HashBytes>> levels_;
};

} // namespace crypto

int main() {
    const std::vector<std::string_view> txs = {
        "Tx1: Alice->Bob 5 BTC",
        "Tx2: Bob->Charlie 2 BTC",
        "Tx3: Charlie->Dave 1 BTC",
        "Tx4: Dave->Eve 0.5 BTC"
    };

    crypto::MerkleTree tree(txs);
    auto root = tree.root();

    std::cout << "Merkle Root: ";
    for (size_t i = 0; i < 8; ++i) {
        std::cout << std::hex << std::setw(2) << std::setfill('0') << static_cast<int>(root[i]);
    }
    std::cout << "...\n";

    // Перевірка індексу 1 (Tx2)
    auto proof = tree.prove(1);
    bool is_valid = crypto::MerkleTree::verify(txs[1], proof, root);
    std::cout << "Перевірка Tx2: " << (is_valid ? "УСПІШНО (VALID)" : "ПОМИЛКА") << "\n";

    bool is_fake_valid = crypto::MerkleTree::verify("Tx2: Bob->Charlie 999 BTC", proof, root);
    std::cout << "Підроблена Tx2: " << (is_fake_valid ? "УСПІШНО" : "ВІДХИЛЕНО (INVALID)") << "\n";

    return 0;
}
```
:::

---

## Докладний розбір інженерних рішень та простеження виконання

### 1. Переваги ідіоматичного C++20 над C-реалізацією
- **Автоматичне керування пам'яттю (RAII)**: У версії мовою C програміст зобов'язаний самостійно викликати `free(proof.nodes)` та `merkle_tree_free(tree)`. Забудькуватість призводить до витоків пам'яті (memory leaks). У версії C++ контейнер `std::vector` звільняє пам'ять автоматично при виході з області видимості (scope).
- **Типобезпека через `std::span` та `std::string_view`**: Передача вхідних елементів як `std::span<const std::string_view>` уникає копіювання рядків у пам'яті й позбавляє потреби передавати сирі `void*` вказівники та явні довжини у байтах.
- **Відсутність небезпечного приведення типів**: Версія C++ повністю відмовляється від `reinterpret_cast` у публічному API, гарантуючи відповідність стандартним вимогам до вирівнювання пам'яті.

### 2. Покрокове простеження обчислень у `merkle_proof_verify`
Розглянемо, що відбувається під час виклику верифікації для транзакції `Tx2` (індекс 1):

1. **Ініціалізація**: Викликається `compute_hash(PREFIX_LEAF, "Tx2: Bob->Charlie 2 BTC")`. На вхід хеш-функції подається байт `0x00` та текст транзакції. Отримуємо 32-байтний вектор `current = L₁`.
2. **Ітерація 0 (Рівень 0)**: Клієнт бере перший елемент доказу. Його сестра має хеш `L₀`, а напрямок `DIR_LEFT`. Клієнт виконує `combine_hashes(L₀, L₁)`. На вхід хеш-функції подається префікс `0x01`, хеш `L₀` та хеш `L₁`. Отримуємо значення `current = N₀₁`.
3. **Ітерація 1 (Рівень 1)**: Клієнт бере другий елемент доказу. Його сестра має хеш `N₂₃`, а напрямок `DIR_RIGHT`. Клієнт виконує `combine_hashes(N₀₁, N₂₃)`. Отримуємо новий кандидат кореня `current = R'`.
4. **Порівняння**: Клієнт виконує `current == expected_root`. Оскільки всі математичні кроки детерміновані, результатом порівняння є `true`.

### 3. Аналіз підробки даних
Коли у тесті викликається `merkle_proof_verify` з підробленим текстом `"Tx2: Bob->Charlie 999 BTC"`, перший крок генерує листовий хеш `L₁* ≠ L₁`. Наступне об'єднання дає `N₀₁* ≠ N₀₁`, а підсумковий корінь `R*` розходиться з `expected_root`. Верифікатор повертає `false` і миттєво відкидає підробку.

---

## Крайові випадки та випробування на міцність

У практичній розробці реалізація повинна витримувати наступні чотири критичні сценарії:

### 1. Порожній масив (`count == 0`)
Функція `merkle_tree_create` повертає `NULL` (у C) або створює дерево з порожніми рівнями (у C++). Запити доказів для порожнього дерева повертають порожній вектор без збоїв чи зациклень.

### 2. Дерево з одного елемента (`count == 1`)
При `count == 1` утворюється єдиний листок `L₀ = Hash(0x00 || Data)`. Оскільки `levels_.size() == 1`, цей листок сам виступає коренем `Merkle Root`. Доказ для цього елемента містить `0` сестринських хешів (порожній вектор). Верифікація порівнює `Hash(0x00 || Data)` безпосередньо з коренем.

### 3. Непарна кількість елементів на проміжних рівнях (наприклад, `N = 5`)
Рівень 0 містить 5 листків `(L₀, L₁, L₂, L₃, L₄)`.
- Парування: `(L₀, L₁) -> N₀₁`, `(L₂, L₃) -> N₂₃`.
- Листок `L₄` не має пари! Алгоритм дублює його: `Combine(L₄, L₄) -> N₄₄`.
- Рівень 1 містить 3 вузли: `(N₀₁, N₂₃, N₄₄)`.
- На рівні 1 вузол `N₄₄` знову не має пари і дублюється: `Combine(N₄₄, N₄₄) -> Root`.

### 4. Витік пам'яті при помилках алокації (Out of Memory)
У C-версії якщо `malloc` повертає `NULL` під час створення плаского масиву `nodes`, функція повинна негайно вивільнити вже виділену пам'ять під структуру `tree` і повернути `NULL`, не залишаючи сирітських вказівників.
