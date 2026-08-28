// Заголовок вузла/листка B-дерева Btrfs (fs/btrfs/ctree.h)
struct btrfs_header {
    u8 csum[32];               // Контрольна сума всього вузла (CRC32c, xxHash64, SHA256 або BLAKE2b)
    u8 fsid[16];               // Унікальний UUID файлової системи
    __le64 bytenr;             // Логічна адреса цього вузла на диску
    __le64 flags;              // Прапорці стану вузла
    u8 chunk_tree_uuid[16];    // UUID дерева чанків
    __le64 generation;         // Номер транзакції (Transaction ID), коли написано вузол
    __le64 owner;              // ID дерева-власника (наприклад, ROOT_TREE_OBJECTID)
    __le32 nritems;            // Кількість елементів у вузлі/листку
    u8 level;                  // Рівень у дереві (0 = leaf, 1..7 = internal node)
} __attribute__ ((packed));
