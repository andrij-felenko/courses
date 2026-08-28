// Ідіоматична C++ структура елемента PHT
struct Elf64_Phdr {
    Elf64_Word  p_type;   // Тип сегмента (PT_LOAD, PT_INTERP, etc.)
    Elf64_Word  p_flags;  // Прапорці доступу (PF_R | PF_W | PF_X)
    Elf64_Off   p_offset; // Зсув у файлі
    Elf64_Addr  p_vaddr;  // Віртуальна адреса
    Elf64_Addr  p_paddr;  // Фізична адреса
    Elf64_Xword p_filesz; // Розмір у файлі
    Elf64_Xword p_memsz;  // Розмір у пам'яті
    Elf64_Xword p_align;  // Вирівнювання
};
