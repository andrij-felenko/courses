#include <stdint.h>

// 64-бітна структура релокації з доданком (Rela)
typedef struct {
    uint64_t r_offset; // Віртуальна адреса (або зсув у GOT), куди записується результат
    uint64_t r_info;   // Індекс символу у .dynsym (верхні 32 біти) + тип релокації (нижні 32 біти)
    int64_t  r_addend; // Фіксований доданок (addend), що додається до обчисленого значення
} Elf64_Rela;

// 64-бітна структура релокації без доданка (Rel)
typedef struct {
    uint64_t r_offset; // Віртуальна адреса запису у GOT
    uint64_t r_info;   // Індекс символу та тип релокації
} Elf64_Rel;

// 64-бітний запис символу у таблиці .dynsym
typedef struct {
    uint32_t st_name;  // Зсув у таблиці рядків .dynstr до імені символу
    uint8_t  st_info;  // Тип символу (STT_FUNC, STT_OBJECT) та зв'язування (STB_GLOBAL)
    uint8_t  st_other; // Видимість символу (STV_DEFAULT, STV_HIDDEN)
    uint16_t st_shndx; // Індекс секції, де визначено символ (SHN_UNDEF для імпортованих)
    uint64_t st_value; // Віртуальна адреса символу або 0
    uint64_t st_size;  // Розмір об'єкта в байтах
} Elf64_Sym;
