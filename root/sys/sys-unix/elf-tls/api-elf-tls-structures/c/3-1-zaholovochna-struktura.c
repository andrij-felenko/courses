typedef struct {
    void *tcb;              /* fs:0x00 — Вказівник на самого себе (self-pointer) */
    dtv_t *dtv;             /* fs:0x08 — Вказівник на Динамічний Вектор Потоку (DTV) */
    void *self;             /* fs:0x10 — Вказівник на управляючу структуру struct pthread */
    int multiple_threads;   /* fs:0x18 — Прапорець наявності багатьох активних потоків */
    int gscope_flag;        /* fs:0x1c — Прапорець синхронізації глобальної області */
    uintptr_t sysinfo;      /* fs:0x20 — Точка входу в системні виклики (для 32-бітних режимів) */
    uintptr_t stack_guard;  /* fs:0x28 — Канарейка захисту стеку від переповнення */
    uintptr_t pointer_guard;/* fs:0x30 — Маска шифрування вказівників функцій (Mangling) */
    unsigned long int vgetcpu_cache[2]; /* fs:0x38 — Кеш системного виклику vgetcpu */
    unsigned int feature_1; /* fs:0x48 — Прапорці апаратних можливостей процесора (CET/IBT) */
} tcbhead_t;
