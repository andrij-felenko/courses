typedef struct {
    Elf64_Addr   r_offset; /* Віртуальна адреса або зсув, що підлягає модифікації */
    Elf64_Xword  r_info;   /* Індекс символу у таблиці та тип релокації */
    Elf64_Sxword r_addend; /* Явний доданок (Explicit Addend) */
} Elf64_Rela;

typedef struct {
    Elf64_Addr  r_offset;  /* Віртуальна адреса або зсув, що підлягає модифікації */
    Elf64_Xword r_info;    /* Індекс символу у таблиці та тип релокації */
} Elf64_Rel;
