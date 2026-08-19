# 📋 Інтерфейс та контракт операцій Splay-дерева

Ця довідка містить вичерпний опис програмного інтерфейсу (API), контрактів складності, інваріантів структури даних та правил керування пам'яттю для Splay-дерева мовами C та C++. Splay-дерево є самонастроюваним двійковим деревом пошуку, де кожна операція доступу модифікує структуру для наближення запитаних вузлів до кореня з амортизованою гарантією `O(log N)`.

## Загальні інваріанти та властивості структури даних

1. **Інваріант двійкового дерева пошуку (BST Invariant)**:
   Для будь-якого вузла `x`, усі ключі в його лівому піддереві строго менші за `x->key`, а всі ключі в правому піддереві строго більші за `x->key`:
   ```
   ∀ y ∈ left_subtree(x):  y->key < x->key
   ∀ z ∈ right_subtree(x): z->key > x->key
   ```
   Це гарантує симетричний порядок обходу ключів за зростанням.

2. **Інваріант вершини (Splay Root Invariant)**:
   Після завершення будь-якої операції пошуку, вставки чи видалення елемент, до якого зверталися (або останній відвіданий вузол у разі відсутності шуканого ключа), обов'язково стає новим коренем дерева `tree->root`.

3. **Відсутність збереження метаданих балансу**:
   Вузли дерева не містять полів висоти, фактора балансу чи кольору. Це зменшує розмір вузла до мінімального: ключ, корисне навантаження та два покажчики на лівого і правого нащадків.

## Специфікація складності операцій

| Операція | Амортизований час | Найгірший час (Worst-case) | Найкращий час (Best-case) | Додаткова пам'ять | Мутує дерево? |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `splay(x)` | `O(log N)` | `O(N)` | `O(1)` | `O(1)` | **Так** |
| `find(key)` | `O(log N)` | `O(N)` | `O(1)` (якщо в корені) | `O(1)` | **Так** (піднімає вузол) |
| `contains(key)` | `O(log N)` | `O(N)` | `O(1)` | `O(1)` | **Так** |
| `insert(key, val)`| `O(log N)` | `O(N)` | `O(1)` | `O(1)` | **Так** |
| `erase(key)` | `O(log N)` | `O(N)` | `O(1)` | `O(1)` | **Так** |
| `split(key)` | `O(log N)` | `O(N)` | `O(1)` | `O(1)` | **Так** |
| `join(T1, T2)` | `O(log N)` | `O(N)` | `O(1)` | `O(1)` | **Так** |
| `min() / max()` | `O(log N)` | `O(N)` | `O(1)` | `O(1)` | **Так** |
| `size()` | `O(1)` | `O(1)` | `O(1)` | `O(1)` | **Ні** |
| `empty()` | `O(1)` | `O(1)` | `O(1)` | `O(1)` | **Ні** |
| `clear()` | `O(N)` | `O(N)` | `O(N)` | `O(1)` | **Так** |

## C-інтерфейс (`splay_tree.h`)

Нижче наведено повний заголовочний файл із типами та сигнатурами функцій для мови C:

:::tabs
```c
#ifndef SPLAY_TREE_H
#define SPLAY_TREE_H

#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct splay_node {
    int key;
    int value;
    struct splay_node *left;
    struct splay_node *right;
} splay_node_t;

typedef struct splay_tree {
    splay_node_t *root;
    size_t size;
} splay_tree_t;

/* Створення та знищення */
splay_tree_t *splay_tree_create(void);
void splay_tree_destroy(splay_tree_t *tree);
void splay_tree_clear(splay_tree_t *tree);

/* Пошук та доступ */
bool splay_tree_find(splay_tree_t *tree, int key, int *out_val);
bool splay_tree_contains(splay_tree_t *tree, int key);
bool splay_tree_min(splay_tree_t *tree, int *out_key, int *out_val);
bool splay_tree_max(splay_tree_t *tree, int *out_key, int *out_val);

/* Модифікатори */
bool splay_tree_insert(splay_tree_t *tree, int key, int value);
bool splay_tree_erase(splay_tree_t *tree, int key);

/* Спеціальні структурні операції */
bool splay_tree_split(splay_tree_t *src, int key, splay_tree_t **left_out, splay_tree_t **right_out);
splay_tree_t *splay_tree_join(splay_tree_t *left_tree, splay_tree_t *right_tree);

/* Стан контейнера */
size_t splay_tree_size(const splay_tree_t *tree);
bool splay_tree_empty(const splay_tree_t *tree);

#ifdef __cplusplus
}
#endif

#endif /* SPLAY_TREE_H */
```
```cpp
#pragma once

#include <optional>
#include <functional>
#include <memory>
#include <utility>
#include <cstddef>

template <
    typename Key,
    typename Value,
    typename Compare = std::less<Key>,
    typename Allocator = std::allocator<std::pair<const Key, Value>>
>
class SplayTree {
public:
    using key_type = Key;
    using mapped_type = Value;
    using value_type = std::pair<const Key, Value>;
    using size_type = std::size_t;
    using key_compare = Compare;

    struct Node {
        Key key;
        Value value;
        std::unique_ptr<Node> left{nullptr};
        std::unique_ptr<Node> right{nullptr};

        Node(Key k, Value v) : key(std::move(k)), value(std::move(v)) {}
    };

    // Створення та життєвий цикл
    SplayTree() = default;
    ~SplayTree() = default;

    SplayTree(const SplayTree&) = delete;
    SplayTree& operator=(const SplayTree&) = delete;

    SplayTree(SplayTree&&) noexcept = default;
    SplayTree& operator=(SplayTree&&) noexcept = default;

    // Стан контейнера
    [[nodiscard]] size_type size() const noexcept;
    [[nodiscard]] bool empty() const noexcept;
    void clear() noexcept;

    // Модифікатори та пошук
    bool insert(Key key, Value value);
    bool erase(const Key& key);
    
    [[nodiscard]] std::optional<Value> find(const Key& key);
    [[nodiscard]] bool contains(const Key& key);
    [[nodiscard]] std::optional<std::pair<Key, Value>> min();
    [[nodiscard]] std::optional<std::pair<Key, Value>> max();

    // Операції розрізання та злиття
    std::pair<SplayTree, SplayTree> split(const Key& key);
    static SplayTree join(SplayTree left_tree, SplayTree right_tree);
};
```
:::

## Детальний контракт поведінки та специфікація функцій

### 1. `splay_tree_create` / Конструктор за замовчуванням
- **Призначення**: виділяє пам'ять та ініціалізує порожнє Splay-дерево.
- **Передумова**: наявність вільної оперативної пам'яті.
- **Післяумова**: `root == NULL`, `size == 0`.
- **Повертає**: покажчик на створену структуру `splay_tree_t` або `NULL` при вичерпанні пам'яті.

### 2. `splay_tree_destroy` / Деструктор
- **Призначення**: рекурсивно або ітеративно звільняє всі виділені вузли дерева та саму структуру.
- **Передумова**: покажчик `tree` є валідним або дорівнює `NULL` (у разі `NULL` функція є безпечною no-op операцією).
- **Післяумова**: уся виділена пам'ять повертається операційній системі; покажчик стає недійсним.

### 3. `splay_tree_find` / `find`
- **Призначення**: пошук значення за ключем із автоматичним підйомом вузла в корінь.
- **Аргументи**:
  - `tree`: покажчик на дерево.
  - `key`: шуканий ключ.
  - `out_val`: покажчик на змінну, куди буде записано знайдене значення (може бути `NULL`).
- **Алгоритм та поведінка**:
  1. Якщо дерево порожнє (`root == NULL`), повертає `false`.
  2. Виконується спуск від кореня за правилом двійкового пошуку.
  3. Якщо вузол знайдено, викликається `splay(root, key)`. Знайдений вузол стає новим коренем `tree->root`.
  4. Якщо вузол відсутній, `splay` викликається для останнього відвіданого вузла. Цей найближчий наявний вузол піднімається в корінь.
  5. Записує значення у `*out_val` (якщо покажчик ненульовий).
- **Повертає**: `true`, якщо ключ знайдено; `false`, якщо ключа немає.
- **Важливе зауваження**: операція є мутуючою. Навіть при невдалому пошуку форма дерева змінюється.

### 4. `splay_tree_insert` / `insert`
- **Призначення**: вставка нової пари ключ-значення або оновлення існуючого значення.
- **Аргументи**: ключ `key` та корисне навантаження `value`.
- **Алгоритм та поведінка**:
  1. Якщо дерево порожнє, створюється новий вузол, який стає коренем (`size = 1`), повертається `true`.
  2. Викликається `splay(root, key)`. Найближчий або ідентичний вузол стає коренем.
  3. Якщо `root->key == key`, оновлюється поле `value`, розмір не змінюється, повертається `false`.
  4. Якщо `key < root->key`: створюється новий вузол, колишній корінь стає його правим сином, ліве піддерево колишнього кореня стає лівим сином нового вузла.
  5. Якщо `key > root->key`: симетрична операція (колишній корінь стає лівим сином нового вузла).
  6. Новий вузол призначається коренем `tree->root`, `size` збільшується на 1, повертається `true`.

### 5. `splay_tree_erase` / `erase`
- **Призначення**: видалення вузла за ключем зі збереженням балансу.
- **Аргументи**: ключ `key`.
- **Алгоритм та поведінка**:
  1. Якщо дерево порожнє, повертає `false`.
  2. Викликається `splay(root, key)`. Якщо ключ є в дереві, він опиняється в корені.
  3. Якщо `root->key != key`, вузол відсутній, повертає `false`.
  4. Якщо ключ знайдено:
     - Якщо ліве піддерево відсутнє (`root->left == NULL`), новим коренем стає `root->right`.
     - Якщо ліве піддерево існує, викликається `splay(root->left, key)`. Оскільки всі ключі лівого піддерева менші за `key`, `splay` підніме в корінь найбільший елемент лівого піддерева. У цього нового кореня гарантовано **відсутній правий нащадок**.
     - До правого покажчика лівого кореня приєднується `root->right`.
     - Звільняється пам'ять старого кореневого вузла.
  5. `size` зменшується на 1, повертається `true`.

### 6. `splay_tree_split` / `split`
- **Призначення**: розрізання дерева `src` на два незалежні дерева за пороговим значенням `key`.
- **Вихідні дерева**:
  - `left_out`: містить усі елементи з ключами `≤ key`.
  - `right_out`: містить усі елементи з ключами `> key`.
- **Поведінка**: викликається `splay(src, key)`. Якщо `root->key <= key`, праве піддерево від'єднується як `right_out`, а корінь із лівим піддеревом стає `left_out`. Якщо `root->key > key`, ліве піддерево від'єднується як `left_out`, а корінь із правим піддеревом стає `right_out`.

### 7. `splay_tree_join` / `join`
- **Призначення**: злиття двох окремих дерев `left_tree` та `right_tree`.
- **Строга передумова**: усі ключі у `left_tree` повинні бути строго меншими за будь-який ключ у `right_tree`:
  ```
  ∀ k1 ∈ left_tree, ∀ k2 ∈ right_tree: k1 < k2
  ```
- **Поведінка**:
  1. Якщо одне з дерев порожнє, повертається інше дерево.
  2. Викликається `splay(max(left_tree))` — максимальний елемент `left_tree` піднімається в його корінь.
  3. Оскільки це максимум, його правий покажчик дорівнює `NULL`.
  4. Корінь `right_tree` під'єднується як правий син кореня `left_tree`.
  5. Повертається об'єднане дерево.

## Правила безпеки потоків (Thread Safety)

1. **Відсутність підтримки конкурентного читання**:
   У стандартних STL-контейнерах (`std::map`, `std::set`) операція `find` є константною (`const`) і безпечно виконується паралельно з довільної кількості потоків без блокувань. У Splay-дереві операція `find` модифікує дерево. Виклик `find` з двох потоків одночасно без синхронізації призводить до стану гонитви (data race) та пошкодження пам'яті (undefined behavior).
2. **Необхідність ексклюзивного блокування**:
   Будь-який доступ до Splay-дерева у багатопотоковому середовищі повинен захищатися ексклюзивним м'ютексом (`std::mutex` або `pthread_mutex_t`). Використання reader-writer lock (`std::shared_mutex`) у режимі спільного володіння (`shared_lock`) для читання є забороненим.
3. **Рекомендована архітектура для багатопотокових систем**:
   У серверах з високим паралелізмом Splay-дерева використовуються локально для кожного робочого потоку (Thread-Local Cache) без міжпотокової синхронізації.

## Зразок використання API

Нижче наведено приклад побудови кешу робочої множини:

:::tabs
```c
#include "splay_tree.h"
#include <stdio.h>

int main(void) {
    splay_tree_t *cache = splay_tree_create();

    /* Вставка даних */
    splay_tree_insert(cache, 19216801, 80);   /* IP 192.168.0.1 -> Port 80 */
    splay_tree_insert(cache, 10000001, 443);  /* IP 10.0.0.1 -> Port 443 */
    splay_tree_insert(cache, 17216001, 8080); /* IP 172.16.0.1 -> Port 8080 */

    /* Швидкий доступ до гарячого ключа */
    int port = 0;
    if (splay_tree_find(cache, 10000001, &port)) {
        printf("Знайдено порт: %d (вузол піднято в корінь)\n", port);
    }

    /* Наступне звернення до того самого ключа виконається за O(1) */
    splay_tree_find(cache, 10000001, &port);

    splay_tree_destroy(cache);
    return 0;
}
```
```cpp
#include "splay_tree.hpp"
#include <iostream>

int main() {
    SplayTree<int, std::string> dns_cache;

    dns_cache.insert(101, "gateway.local");
    dns_cache.insert(202, "auth.internal");
    dns_cache.insert(303, "db.primary");

    // Гарячий доступ
    if (auto host = dns_cache.find(202)) {
        std::cout << "Хост знайдено: " << *host << "\n";
    }

    dns_cache.erase(101);
    return 0;
}
```
:::
