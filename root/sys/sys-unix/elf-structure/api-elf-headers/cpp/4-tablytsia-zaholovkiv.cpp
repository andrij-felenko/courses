// Ідіоматична C++ структура елемента SHT
struct Elf64_Shdr {
    Elf64_Word  sh_name;      // Зсув імені в .shstrtab
    Elf64_Word  sh_type;      // Тип секції (SHT_PROGBITS, SHT_NOBITS)
    Elf64_Xword sh_flags;     // Прапорці атрибутів (SHF_WRITE | SHF_ALLOC)
    Elf64_Addr  sh_addr;      // Віртуальна адреса
    Elf64_Off   sh_offset;    // Зсув у файлі
    Elf64_Xword sh_size;      // Розмір секції
    Elf64_Word  sh_link;      // Пов'язана секція
    Elf64_Word  sh_info;      // Додаткова інформація
    Elf64_Xword sh_addralign; // Вирівнювання
    Elf64_Xword sh_entsize;   // Розмір запису
};
