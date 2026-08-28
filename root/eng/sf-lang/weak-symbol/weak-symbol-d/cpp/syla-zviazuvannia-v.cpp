// elf_sym.hpp — опис структури символу у форматі ELF на C++20
#include <cstdint>

struct Elf64_Sym {
    std::uint32_t st_name;      // Зсув імені символу в таблиці рядків .strtab
    std::uint8_t  st_info;      // Тип символу (STT_*) та атрибут зв'язування (STB_*)
    std::uint8_t  st_other;     // Видимість символу (STV_DEFAULT тощо)
    std::uint16_t st_shndx;     // Індекс секції, де розташовано тіло символу
    std::uint64_t st_value;     // Адреса або зміщення символу всередині секції
    std::uint64_t st_size;      // Розмір об'єкта чи функції в байтах
};
