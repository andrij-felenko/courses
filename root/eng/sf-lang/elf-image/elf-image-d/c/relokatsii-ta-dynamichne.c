typedef struct {
    uint32_t r_offset; /* Адреса/зміщення у секції, яку треба модифікувати */
    uint32_t r_info;   /* Індекс символу у .symtab та тип релокації */
} Elf32_Rel;

typedef struct {
    uint32_t r_offset;
    uint32_t r_info;
    int32_t  r_addend; /* Явне додаткове зміщення (Addend) */
} Elf32_Rela;
