// Ідіоматичне C++20 представлення заголовка ELF
struct Elf64_Ehdr {
    std::array<unsigned char, 16> e_ident; // Магічні байти та ідентифікатори
    Elf64_Half    e_type;      // Тип об'єкта (ET_EXEC, ET_DYN)
    Elf64_Half    e_machine;   // Архітектура (EM_X86_64, EM_AARCH64)
    Elf64_Word    e_version;   // Версія специфікації
    Elf64_Addr    e_entry;     // Точка входу
    Elf64_Off     e_phoff;     // Зсув PHT
    Elf64_Off     e_shoff;     // Зсув SHT
    Elf64_Word    e_flags;     // Прапорці архітектури
    Elf64_Half    e_ehsize;    // Розмір заголовка
    Elf64_Half    e_phentsize; // Розмір запису PHT
    Elf64_Half    e_phnum;     // Кількість записів PHT
    Elf64_Half    e_shentsize; // Розмір запису SHT
    Elf64_Half    e_shnum;     // Кількість записів SHT
    Elf64_Half    e_shstrndx;  // Індекс таблиці імен секцій
};
