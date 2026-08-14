# 📋 Інтерфейс та специфікація API Дерева Меркла

Цей документ містить формальну специфікацію програмного інтерфейсу (API) та бінарного контракту мережевого протоколу передачі доказів бібліотеки керування Деревом Меркла (`libmerkletree`). Специфікація визначає типи даних, структури, коди помилок, функціональні сигнатури, гарантії безпеки та бінарний формат серіалізації доказів включення.

## 1. Загальні принципи та архітектура API

Бібліотека `libmerkletree` розроблена за принципом модульного низькорівневого C-інтерфейсу, що дозволяє легко інтегрувати її в будь-які мови програмування (C++, Rust, Python, Go, Java) через механізм FFI (Foreign Function Interface).

Основними принципами архітектури є:

- **Строге розділення доменів (Domain Separation)**: Усі внутрішні виклики хешування автоматично додають криптографічні префікси `0x00` (для листків даних) та `0x01` (для внутрішніх вузлів об'єднання). Користувачеві API не потрібно додавати префікси вручну.
- **Незмінність об'єктів (Immutability)**: Створене дерево `merkle_tree_t` є об'єктом «тільки для читання» (read-only). Воно не допускає модифікацій після побудови і є повністю безпечним для паралельного читання з багатьох потоків (thread-safe concurrent access).
- **Передбачуваність пам'яті (Explicit Memory Allocation)**: Усі функції, які виділяють динамічну пам'ять у кучі, мають парні функції звільнення (`merkle_proof_free`, `merkle_tree_destroy`). Жодна функція верифікації не виділяє пам'ять у кучі, що дозволяє використовувати їх в операційних системах реального часу (RTOS) та мікроконтролерах.

---

## 2. Основні константи та коди повернення

### 2.1. Криптографічні константи

- `MERKLE_HASH_SIZE = 32`: Розмір криптографічного хешу у байтах (256 біт). Відповідає стандартам SHA-256 та BLAKE3.
- `MERKLE_PREFIX_LEAF = 0x00`: Перший байт, що додається до буфера перед хешуванням первинних даних користувача.
- `MERKLE_PREFIX_INTERNAL = 0x01`: Перший байт, що додається перед хешуванням двох 32-байтових нащадків.
- `MERKLE_MAX_DEPTH = 64`: Максимально дозволена глибина дерева. Обмеження запобігає переповненню системного стека і дозволяє підтримувати масиви обсягом до `2⁶⁴` листків.

### 2.2. Перелічення кодів повернення (`merkle_status_t`)

Кожна функція бібліотеки повертає цілочисельний статус виконання:

:::tabs
```c
typedef enum {
    MERKLE_SUCCESS            =  0,  /* Операція виконана успішно */
    MERKLE_ERROR_NULL_POINTER = -1,  /* Передано вказівник NULL у критичний аргумент */
    MERKLE_ERROR_INVALID_SIZE = -2,  /* Некоректний розмір входів (наприклад, count == 0) */
    MERKLE_ERROR_OUT_OF_BOUNDS= -3,  /* Запитаний індекс перевищує кількість листків у дереві */
    MERKLE_ERROR_NO_MEMORY    = -4,  /* Помилка виділення динамічної пам'яті в кучі */
    MERKLE_ERROR_CORRUPTED    = -5,  /* Некоректний або пошкоджений бінарний пакет доказу */
    MERKLE_ERROR_VERIFY_FAILED= -6   /* Верифікація доказу не пройшла (фальсифікація або помилка даних) */
} merkle_status_t;
```
```cpp
enum class MerkleStatus : int32_t {
    Success          =  0,  // Операція виконана успішно
    NullPointer      = -1,  // Передано nullptr у критичний аргумент
    InvalidSize      = -2,  // Некоректний розмір входів (наприклад, count == 0)
    OutOfBounds       = -3,  // Запитаний індекс перевищує кількість листків у дереві
    NoMemory         = -4,  // Помилка виділення динамічної пам'яті в кучі
    Corrupted        = -5,  // Некоректний або пошкоджений бінарний пакет доказу
    VerifyFailed     = -6   // Верифікація доказу не пройшла (фальсифікація або помилка даних)
};
```
:::

#### Деталізація кодів помилок:
- `MERKLE_SUCCESS`: Означає, що операція завершилася без жодних зауважень, вихідні буфери заповнено коректними даними.
- `MERKLE_ERROR_NULL_POINTER`: Виникає, якщо один із обов'язкових аргументів-вказівників (наприклад, `out_tree` або `expected_root`) є рівним `NULL`.
- `MERKLE_ERROR_INVALID_SIZE`: Виникає під час спроби побудувати дерево з 0 елементів або передачі від'ємної довжини блоку.
- `MERKLE_ERROR_OUT_OF_BOUNDS`: Виникає при виклику `merkle_proof_generate` з індексом `leaf_index >= leaf_count`.
- `MERKLE_ERROR_NO_MEMORY`: Сигналізує про виснаження системної оперативної пам'яті під час виконання `malloc`.
- `MERKLE_ERROR_CORRUPTED`: Виникає при синтаксичному парсингу серіалізованого бінарного пакета, якщо заголовок (Magic bytes) не збігається з `"MRKL"` або вказана довжина перевищує фактичний розмір пакета.
- `MERKLE_ERROR_VERIFY_FAILED`: Криптографічна помилка. Означає, що обчислений під час перевірки корінь не збігається з наданим коренем.

---

## 3. Опис структур даних

:::tabs
```c
typedef struct {
    uint8_t bytes[MERKLE_HASH_SIZE];
} merkle_hash_t;

typedef enum {
    MERKLE_DIR_LEFT  = 0,  /* Сестра розташована ліворуч від поточного вузла */
    MERKLE_DIR_RIGHT = 1   /* Сестра розташована праворуч від поточного вузла */
} merkle_direction_t;

typedef struct {
    merkle_hash_t sibling_hash;
    merkle_direction_t direction;
} merkle_proof_node_t;

typedef struct {
    merkle_proof_node_t* nodes;
    size_t node_count;
} merkle_proof_t;

typedef struct merkle_tree_s merkle_tree_t;
```
```cpp
using MerkleHash = std::array<uint8_t, MERKLE_HASH_SIZE>;

enum class MerkleDirection {
    Left  = 0,  // Сестра розташована ліворуч від поточного вузла
    Right = 1   // Сестра розташована праворуч від поточного вузла
};

struct MerkleProofNode {
    MerkleHash sibling_hash;
    MerkleDirection direction;
};

using MerkleProof = std::vector<MerkleProofNode>;

class MerkleTree; // Непрозорий клас-контейнер Дерева Меркла (RAII)
```
:::

### Деталізація полів структур:
- `merkle_hash_t`: Фіксований масив із 32 беззнакових байтів (`uint8_t`), який зберігає результати обчислення криптографічного хешу.
- `merkle_direction_t`: Перелічення, що вказує відносне положення сестринського вузла при підйомі по дереву. Значення `MERKLE_DIR_LEFT` означає, що при хешуванні сестра ставиться першим аргументом `Combine(Sibling, Current)`. Значення `MERKLE_DIR_RIGHT` означає, що сестра ставиться другим аргументом `Combine(Current, Sibling)`.
- `merkle_proof_node_t`: Один крок доказу включення. Містить 32-байтний хеш сестри та напрямок.
- `merkle_proof_t`: Повний доказ включення. Включає вказівник на динамічний масив кроків `nodes` та їхню кількість `node_count = ⌈log₂ N⌉`.
- `merkle_tree_t`: Непрозора (opaque) структура, яка приховує внутрішнє представлення вузлів дерева.

---

## 4. Специфікація функцій C API

### 4.1. `merkle_tree_create`
Створення та побудова Дерева Меркла у пам'яті.

:::tabs
```c
merkle_status_t merkle_tree_create(
    const void* const* data_blocks,
    const size_t* block_sizes,
    size_t count,
    merkle_tree_t** out_tree
);
```
```cpp
static MerkleStatus MerkleTree::create(
    std::span<const std::string_view> data_blocks,
    MerkleTree& out_tree
);
```
:::

#### Опис параметрів:
- `data_blocks` [in]: Масив вказівників на бінарні блоки даних. Жоден елемент масиву не повинен бути `NULL`.
- `block_sizes` [in]: Масив розмірів (у байтах) для кожного відповідно блоку даних.
- `count` [in]: Загальна кількість блоків у масиві (мусить бути `> 0`).
- `out_tree` [out]: Вказівник на змінну-вказівник, куди буде записано адресу створеного об'єкта дерева.

#### Поведінка та інваріанти:
Функція копіює дані у листові хеші й будує вищі рівні. Сам вхідний масив `data_blocks` після завершення виклику можна безпечно звільняти, оскільки дерево зберігає лише хеш-значення, а не самі первинні дані.

---

### 4.2. `merkle_tree_get_root`
Отримання підсумкового 32-байтного кореня (Merkle Root).

:::tabs
```c
merkle_status_t merkle_tree_get_root(
    const merkle_tree_t* tree,
    merkle_hash_t* out_root
);
```
```cpp
[[nodiscard]] MerkleHash MerkleTree::get_root() const noexcept;
```
:::

#### Опис параметрів:
- `tree` [in]: Вказівник на ініціалізоване Дерево Меркла.
- `out_root` [out]: Вказівник на буфер пам'яті розміром не менше 32 байтів, куди буде скопійовано значення кореня.

#### Поведінка:
Функція виконує копіювання за сталий час `O(1)`, оскільки корінь обчислено під час побудови дерева.

---

### 4.3. `merkle_proof_generate`
Формування аудиторського доказу включення для заданого елемента.

:::tabs
```c
merkle_status_t merkle_proof_generate(
    const merkle_tree_t* tree,
    size_t leaf_index,
    merkle_proof_t* out_proof
);
```
```cpp
MerkleStatus MerkleTree::generate_proof(
    size_t leaf_index,
    MerkleProof& out_proof
) const;
```
:::

#### Опис параметрів:
- `tree` [in]: Вказівник на Дерево Меркла.
- `leaf_index` [in]: Індекс елемента в початковому масиві (від `0` до `count - 1`).
- `out_proof` [out]: Вказівник на структуру `merkle_proof_t`. Функція виділяє пам'ять під масив `nodes` усередині структури.

#### Поведінка:
Обходить дерево від листка `leaf_index` до кореня, збираючи по одному сестринському хешу на кожному рівні. Часова складність `O(log N)`.

---

### 4.4. `merkle_proof_verify`
Автономна верифікація доказу на боці клієнта.

:::tabs
```c
merkle_status_t merkle_proof_verify(
    const void* data_block,
    size_t block_size,
    const merkle_proof_t* proof,
    const merkle_hash_t* expected_root
);
```
```cpp
static MerkleStatus MerkleTree::verify_proof(
    std::span<const std::byte> data_block,
    const MerkleProof& proof,
    const MerkleHash& expected_root
);
```
:::

#### Опис параметрів:
- `data_block` [in]: Вказівник на перевіряємий бінарний блок даних.
- `block_size` [in]: Розмір блоку у байтах.
- `proof` [in]: Вказівник на структуру доказу.
- `expected_root` [in]: Очікуване 32-байтне значення кореня Меркла.

#### Поведінка:
Обчислює листовий хеш `Hash(0x00 || data_block)` і послідовно застосовує об'єднання `Combine` із сестринськими хешами з `proof`. Повертає `MERKLE_SUCCESS` у разі співпадіння з `expected_root` або `MERKLE_ERROR_VERIFY_FAILED` при розходженні.

---

### 4.5. Звільнення ресурсів

:::tabs
```c
void merkle_proof_free(merkle_proof_t* proof);
void merkle_tree_destroy(merkle_tree_t* tree);
```
```cpp
// У C++ виділення та звільнення ресурсів відбувається автоматично за допомогою RAII
// std::vector<MerkleProofNode> та клас MerkleTree звільняють пам'ять у своїх деструкторах
~MerkleTree() noexcept = default;
```
:::

#### Поведінка:
Функція `merkle_proof_free` звільняє масив `proof->nodes` і скидає `node_count` до 0. Функція `merkle_tree_destroy` звільняє всі внутрішні масиви вузлів та саму структуру дерева. Передача `NULL` є безпечною і мовчки ігнорується.

---

## 5. Формат серіалізації доказів у мережевих протоколах (Proof Wire Format)

Для передачі доказів через мережеві сокети або збереження у дискових файлах визначено стандартизований бінарний формат без падінгу та залежності від архітектури процесора (Big-Endian network byte order).

### 5.1. Структура бінарного пакета

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
| Magic Byte 0  | Magic Byte 1  | Magic Byte 2  | Magic Byte 3  |
|     'M'       |     'R'       |     'K'       |     'L'       |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
| Version (0x01)| Reserved (0x0)| Node Count (High) | (Low)     |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
| Direction Bitfield (0 .. 7)   | Direction Bitfield (8 .. 15)  |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                                                               |
+                       Sibling Hash 0 (32 Bytes)               +
|                                                               |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                                                               |
+                       Sibling Hash 1 (32 Bytes)               +
|                                                               |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

### 5.2. Опис полів пакета:
1. **Magic Header** (4 байти): Рядок ASCII `"MRKL"` (`0x4D, 0x52, 0x4B, 0x4C`). Гарантує ідентифікацію типа пакета в сокетному потоці.
2. **Version** (1 байт): Версія бінарного формату. Поточна версія `0x01`.
3. **Reserved** (1 байт): Зарезервовано під майбутні розширення (мусить дорівнювати `0x00`).
4. **Node Count** (2 байти, Big-Endian): Кількість вузлів у доказі `K` (`0 <= K <= 64`).
5. **Direction Bitfield** (`⌈K / 8⌉` байтів): Упаковані біти напрямку (упорядковані від найменшого до найбільшого кроку). Біт `0` означає `LEFT`, біт `1` означає `RIGHT`.
6. **Array of Hashes** (`K × 32` байтів): Послідовний масив 32-байтових сестринських хешів без додаткових розділювачів.

---

## 6. Серіалізаційні функції C API

:::tabs
```c
merkle_status_t merkle_proof_serialize(
    const merkle_proof_t* proof,
    uint8_t* out_buffer,
    size_t buffer_capacity,
    size_t* out_written_bytes
);

merkle_status_t merkle_proof_deserialize(
    const uint8_t* in_buffer,
    size_t buffer_size,
    merkle_proof_t* out_proof
);
```
```cpp
MerkleStatus serialize_proof(
    const MerkleProof& proof,
    std::vector<uint8_t>& out_buffer
);

MerkleStatus deserialize_proof(
    std::span<const uint8_t> in_buffer,
    MerkleProof& out_proof
);
```
:::

### Опис серіалізації:
- `merkle_proof_serialize`: Приймає структуру доказу `proof` і пакує її у бінарний буфер `out_buffer`. Якщо `buffer_capacity` менша за необхідний розмір пакета `(8 + ⌈K/8⌉ + K*32)`, функція повертає `MERKLE_ERROR_INVALID_SIZE` і повертає необхідний розмір у `out_written_bytes`.
- `merkle_proof_deserialize`: Приймає бінарний буфер `in_buffer`, перевіряє заголовок `"MRKL"`, розпаковує бітове поле напрямків та копіює масив хешів у нововиділений об'єкт `out_proof`. При виявленні пошкодження даних повертає `MERKLE_ERROR_CORRUPTED`.
