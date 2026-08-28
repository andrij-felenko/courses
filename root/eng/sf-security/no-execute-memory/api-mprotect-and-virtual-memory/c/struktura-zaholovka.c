#include <elf.h>

typedef struct {
    uint32_t   p_type;   /* Тип сегмента */
    uint32_t   p_flags;  /* Прапорці прав доступу (PF_R, PF_W, PF_X) */
    Elf64_Off  p_offset; /* Зміщення у файлі */
    Elf64_Addr p_vaddr;  /* Віртуальна адреса завантаження */
    Elf64_Addr p_paddr;  /* Фізична адреса */
    uint64_t   p_filesz; /* Розмір даних у файлі */
    uint64_t   p_memsz;  /* Розмір сегмента в RAM */
    uint64_t   p_align;  /* Вирівнювання (4096 байтів) */
} Elf64_Phdr;
