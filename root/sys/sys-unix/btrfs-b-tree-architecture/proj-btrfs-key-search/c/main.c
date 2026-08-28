#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <stdlib.h>

// Поле типу ключа Btrfs
#define BTRFS_INODE_ITEM_KEY 1
#define BTRFS_INODE_REF_KEY  12
#define BTRFS_XATTR_ITEM_KEY 24
#define BTRFS_EXTENT_DATA_KEY 108

// 3-компонентний ключ Btrfs (17 байтів у ядрі)
struct btrfs_key {
    uint64_t objectid; // ID іноди, субтому або екстента
    uint8_t  type;     // Тип метаданих (INODE_ITEM, DIR_ITEM тощо)
    uint64_t offset;   // Байтовий зсув у файлі або хеш імені
};

// Заголовок елемента всередині листка (25 байтів у ядрі)
struct btrfs_item {
    struct btrfs_key key;
    uint32_t offset;   // Зсув до даних від початку області даних (за заголовком)
    uint32_t size;     // Розмір даних у байтах
};

// Лексикографічне порівняння двох ключів Btrfs
// Повертає -1 якщо k1 < k2, 0 якщо k1 == k2, 1 якщо k1 > k2
int btrfs_comp_keys(const struct btrfs_key *k1, const struct btrfs_key *k2)
{
    if (k1->objectid < k2->objectid) return -1;
    if (k1->objectid > k2->objectid) return 1;

    if (k1->type < k2->type) return -1;
    if (k1->type > k2->type) return 1;

    if (k1->offset < k2->offset) return -1;
    if (k1->offset > k2->offset) return 1;

    return 0;
}

// Бінарний пошук ключа key у масиві items тривалістю nritems
// Повертає 0 у разі точного збігу, або 1 якщо ключа немає
// У змінну *slot записується індекс точного збігу або індекс місця вставки
int btrfs_bin_search(const struct btrfs_item *items, int nritems,
                     const struct btrfs_key *key, int *slot)
{
    int low = 0;
    int high = nritems - 1;

    while (low <= high) {
        int mid = low + (high - low) / 2;
        int ret = btrfs_comp_keys(&items[mid].key, key);

        if (ret < 0) {
            low = mid + 1;
        } else if (ret > 0) {
            high = mid - 1;
        } else {
            *slot = mid;
            return 0; // Точний збіг знайдено
        }
    }

    *slot = low; // Найближчий слот вставки (перший елемент, більший за пошуковий)
    return 1;    // Точного збігу не знайдено
}

int main(void)
{
    // Моделювання впорядкованого масиву елементів у листку
    struct btrfs_item leaf_items[] = {
        { {257, BTRFS_INODE_ITEM_KEY, 0},          16123, 160 },
        { {257, BTRFS_INODE_REF_KEY, 256},         16107, 16 },
        { {257, BTRFS_XATTR_ITEM_KEY, 0x8a9b1c2d}, 16067, 40 },
        { {257, BTRFS_EXTENT_DATA_KEY, 0},         16014, 53 },
        { {257, BTRFS_EXTENT_DATA_KEY, 4096},      15961, 53 },
        { {258, BTRFS_INODE_ITEM_KEY, 0},          15801, 160 }
    };
    int nritems = sizeof(leaf_items) / sizeof(leaf_items[0]);

    // Пошуковий ключ: шукаємо другий екстент файлу 257 (зсув 4096)
    struct btrfs_key search_key = {257, BTRFS_EXTENT_DATA_KEY, 4096};
    int slot = -1;

    int res = btrfs_bin_search(leaf_items, nritems, &search_key, &slot);

    if (res == 0) {
        printf("Знайдено точний збіг у слоті %d: objectid=%lu, type=%u, offset=%lu\n",
               slot, (unsigned long)leaf_items[slot].key.objectid,
               leaf_items[slot].key.type, (unsigned long)leaf_items[slot].key.offset);
    } else {
        printf("Точного збігу немає. Слот вставки: %d\n", slot);
    }

    return 0;
}
