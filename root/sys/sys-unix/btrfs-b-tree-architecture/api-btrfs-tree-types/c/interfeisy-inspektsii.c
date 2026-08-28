#include <linux/btrfs.h>

// Параметри запиту до ioctl(BTRFS_IOC_TREE_SEARCH)
struct btrfs_ioctl_search_args {
    struct btrfs_ioctl_search_key key; // Діапазон пошуку ключів
    u64 buf_size;                       // Розмір наданого буфера
    u8 buf[];                           // Повернуті заголовки та дані
};

struct btrfs_ioctl_search_key {
    u64 tree_id;       // ID дерева (5 для FS_TREE, 1 для ROOT_TREE, 2 для EXTENT_TREE)

    // Мінімальні межі пошукового діапазону
    u64 min_objectid;
    u64 max_objectid;
    u64 min_offset;
    u64 max_offset;
    u64 min_transid;
    u64 max_transid;
    u32 min_type;
    u32 max_type;

    u32 nr_items;      // Повернута кількість знайдених елементів
};
