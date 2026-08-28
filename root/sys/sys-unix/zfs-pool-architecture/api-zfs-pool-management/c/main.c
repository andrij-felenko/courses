struct zfs_cmd {
    char         zc_name[MAXPATHLEN];     /* Ім'я пулу або датасету */
    uint64_t     zc_nvlist_src;           /* Вказівник на NVList конфігурації (input) */
    uint64_t     zc_nvlist_src_size;      /* Розмір вхідного NVList буфера */
    uint64_t     zc_nvlist_dst;           /* Вказівник на NVList результату (output) */
    uint64_t     zc_nvlist_dst_size;      /* Розмір вихідного NVList буфера */
    uint64_t     zc_history;              /* Вказівник на журнал історії */
    uint64_t     zc_cookie;               /* Спеціальний ідентифікатор транзакції */
    uint64_t     zc_objset_type;          /* Тип об'єкта (DMU_OST_ZFS, DMU_OST_ZVOL) */
    uint64_t     zc_perm_action;          /* Права доступу та операція */
};
