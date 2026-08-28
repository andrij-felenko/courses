// Ідіоматична C++ структура запису релокацій з явним доданком
struct Elf64_Rela {
    Elf64_Addr   r_offset; // Адреса модифікації
    Elf64_Xword  r_info;   // Індекс символу та тип релокації
    Elf64_Sxword r_addend; // Явний доданок
};

struct Elf64_Rel {
    Elf64_Addr  r_offset;  // Адреса модифікації
    Elf64_Xword r_info;    // Індекс символу та тип релокації
};
