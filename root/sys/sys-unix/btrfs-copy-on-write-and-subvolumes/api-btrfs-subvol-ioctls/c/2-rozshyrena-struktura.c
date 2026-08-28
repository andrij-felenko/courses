struct btrfs_ioctl_vol_args_v2 {
    __s64 fd;                         // Відкритий файловий дескриптор джерельного субтому
    __u64 transid;                    // Сюди ядро повертає номер транзакції створення
    __u64 flags;                      // Бітова маска прапорців створення
    union {
        struct {
            __u64 size;                                  // Розмір масиву qgroups у структурі
            struct btrfs_qgroup_inherit *qgroup_inherit; // Вказівник на структуру успадкування квот
        };
        __u64 unused[4];
    };
    union {
        char name[BTRFS_SUBVOL_NAME_MAX + 1]; // Ім'я нового субтому у батьківському каталозі
        __u64 devid;                          // ID пристрою (операції з пристроями)
        __u64 subvolid;                       // ID субтому для BTRFS_IOC_SNAP_DESTROY_V2
    };
};
