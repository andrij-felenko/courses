struct fdt_header {
    uint32_t magic;             /* 0xd00dfeed (FDT_MAGIC) */
    uint32_t totalsize;         /* Загальний розмір бінарного DTB у байтах */
    uint32_t off_dt_struct;     /* Зсув у байтах до блоку структур (dt_struct) */
    uint32_t off_dt_strings;    /* Зсув у байтах до блоку рядків (dt_strings) */
    uint32_t off_mem_rsvmap;    /* Зсув до таблиці зарезервованої пам'яті */
    uint32_t version;           /* Версія специфікації FDT (наразі 17) */
    uint32_t last_comp_version; /* Найменша сумісна версія (зазвичай 16) */
    uint32_t boot_cpuid_phys;   /* Фізичний ID ядра CPU для первинного завантаження */
    uint32_t size_dt_strings;   /* Розмір блоку рядків у байтах */
    uint32_t size_dt_struct;    /* Розмір блоку структур у байтах */
};
