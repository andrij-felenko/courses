// Заголовок кореня субтому в ядрі Linux (fs/btrfs/ctree.h / uapi/linux/btrfs_tree.h)
struct btrfs_root_item {
    struct btrfs_inode_item inode; // Метадані самого кореня субтому
    __le64 generation;             // Генерація останнього commit субтому
    __le64 root_dirid;             // Inode номер кореневої директорії (зазвичай 256)
    __le64 bytenr;                 // Логічна адреса кореневого вузла B-дерева
    __le64 byte_limit;             // Ліміт простору (якщо задано qgroups)
    __le64 bytes_used;             // Кількість задіяних байтів
    __le64 last_snapshot;          // Генерація останнього зробленого знімка
    __le64 flags;                  // Прапорці (наприклад, BTRFS_ROOT_SUBVOL_RDONLY)
    u8 uuid[BTRFS_UUID_SIZE];      // Унікальний UUID субтому
    u8 parent_uuid[BTRFS_UUID_SIZE];   // UUID батьківського субтому (якщо це snapshot)
    u8 received_uuid[BTRFS_UUID_SIZE]; // UUID вихідного субтому (для btrfs receive)
    __le64 ctransid;               // Генерація створення
    __le64 otransid;               // Генерація походження
    __le64 stransid;               // Генерація відправки (send)
    __le64 rtransid;               // Генерація отримання (receive)
} __attribute__ ((packed));
