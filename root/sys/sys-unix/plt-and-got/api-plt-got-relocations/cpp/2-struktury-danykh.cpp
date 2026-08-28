#include <cstdint>

// 64-бітна структура релокації з доданком (Rela)
struct Elf64_Rela {
    std::uint64_t r_offset; // Віртуальна адреса (або зсув у GOT), куди записується результат
    std::uint64_t r_info;   // Індекс символу у .dynsym (верхні 32 біти) + тип релокації (нижні 32 біти)
    std::int64_t  r_addend; // Фіксований доданок (addend), що додається до обчисленого значення
};

// 64-бітна структура релокації без доданка (Rel)
struct Elf64_Rel {
    std::uint64_t r_offset; // Віртуальна адреса запису у GOT
    std::uint64_t r_info;   // Індекс символу та тип релокації
};

// 64-бітний запис символу у таблиці .dynsym
struct Elf64_Sym {
    std::uint32_t st_name;  // Зсув у таблиці рядків .dynstr до імені символу
    std::uint8_t  st_info;  // Тип символу (STT_FUNC, STT_OBJECT) та зв'язування (STB_GLOBAL)
    std::uint8_t  st_other; // Видимість символу (STV_DEFAULT, STV_HIDDEN)
    std::uint16_t st_shndx; // Індекс секції, де визначено символ (SHN_UNDEF для імпортованих)
    std::uint64_t st_value; // Віртуальна адреса символу або 0
    std::uint64_t st_size;  // Розмір об'єкта в байтах
};
