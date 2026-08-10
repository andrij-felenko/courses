# ⚙️ Бінарний пошук ключів btrfs_key у листі B-дерева

Ця вставка пояснює ⚙️ бінарний пошук ключів btrfs_key у листі b-дерева та дозволяє зрозуміти її детальніше. Ця проектна стаття описує C-код алгоритму бінарного пошуку впорядкованого ключа `btrfs_key` всередині листка метаданих Btrfs, моделюючи внутрішню роботу ядерної функції `btrfs_bin_search()`.

Усі заголовки елементів `struct btrfs_item` у листі Btrfs розміщені підряд від початку листка і впорядковані за зростанням триплета ключа `(objectid, type, offset)`.

```c
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>

struct btrfs_key {
    uint64_t objectid;
    uint8_t type;
    uint64_t offset;
};

struct btrfs_item {
    struct btrfs_key key;
    uint32_t offset;
    uint32_t size;
};

// Порівняння двох ключів Btrfs (-1 якщо k1 < k2, 0 якщо k1 == k2, 1 якщо k1 > k2)
int comp_keys(const struct btrfs_key *k1, const struct btrfs_key *k2)
{
    if (k1->objectid < k2->objectid) return -1;
    if (k1->objectid > k2->objectid) return 1;

    if (k1->type < k2->type) return -1;
    if (k1->type > k2->type) return 1;

    if (k1->offset < k2->offset) return -1;
    if (k1->offset > k2->offset) return 1;

    return 0;
}

// Бінарний пошук ключа у масиві items листка
int btrfs_bin_search(const struct btrfs_item *items, int nritems, const struct btrfs_key *key, int *slot)
{
    int low = 0;
    int high = nritems - 1;

    while (low <= high) {
        int mid = (low + high) / 2;
        int ret = comp_keys(&items[mid].key, key);

        if (ret < 0) {
            low = mid + 1;
        } else if (ret > 0) {
            high = mid - 1;
        } else {
            *slot = mid;
            return 0; // Знайдено точний збіг
        }
    }

    *slot = low; // Найближчий слот вставки або наступний елемент
    return 1; // Точного збігу не знайдено
}
```

## Висока локальність та складність

Бінарний пошук усередині листка виконується за складність $O(\log_2 N)$, де $N$ — кількість елементів у листі (зазвичай від 100 до 500 записів). Оскільки весь листок (16 КБ) завантажується у L1/L2 кеш процесора як суцільний масив, пошук відбувається миттєво без промахів кешу.
