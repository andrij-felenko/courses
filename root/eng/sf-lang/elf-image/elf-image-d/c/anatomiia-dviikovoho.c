#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define EI_NIDENT 16

/* Константи типу двійкового файлу e_type */
#define ET_NONE 0
#define ET_REL  1  /* Relocatable file (.o) */
#define ET_EXEC 2  /* Executable file (.elf) */
#define ET_DYN  3  /* Shared object / Position-Independent Executable */

/* Архітектурні коди процесорів e_machine */
#define EM_ARM     40  /* 0x28: ARM 32-bit Architecture */
#define EM_RISCV  243  /* 0xF3: RISC-V Architecture */
#define EM_XTENSA  94  /* 0x5E: Tensilica Xtensa (ESP32) */

typedef struct {
    uint8_t  e_ident[EI_NIDENT];
    uint16_t e_type;
    uint16_t e_machine;
    uint32_t e_version;
    uint32_t e_entry;      /* Адреса точки входу */
    uint32_t e_phoff;      /* Зміщення Program Header Table від початку файлу */
    uint32_t e_shoff;      /* Зміщення Section Header Table від початку файлу */
    uint32_t e_flags;      /* Прапорці архітектури та ABI */
    uint16_t e_ehsize;     /* Розмір цього заголовка */
    uint16_t e_phentsize;  /* Розмір одного запису в таблиці сегментів */
    uint16_t e_phnum;      /* Кількість сегментів */
    uint16_t e_shentsize;  /* Розмір одного запису в таблиці секцій */
    uint16_t e_shnum;      /* Кількість секцій */
    uint16_t e_shstrndx;   /* Індекс секції .shstrtab для назв секцій */
} Elf32_Ehdr_Custom;

bool validate_elf32_header(const Elf32_Ehdr_Custom* hdr, size_t file_size) {
    if (!hdr) return false;
    if (file_size < sizeof(Elf32_Ehdr_Custom)) return false;

    if (hdr->e_ident[0] != 0x7F || hdr->e_ident[1] != 'E' ||
        hdr->e_ident[2] != 'L'  || hdr->e_ident[3] != 'F') {
        return false;
    }
    if (hdr->e_ident[4] != 1) return false; /* Перевірка: лише 32-бітний ELF */
    if (hdr->e_version != 1) return false;

    /* Перевірка меж таблиць у межах фізичного розміру файлу */
    if (hdr->e_phoff != 0) {
        uint64_t ph_end = (uint64_t)hdr->e_phoff + ((uint64_t)hdr->e_phentsize * hdr->e_phnum);
        if (ph_end > file_size) return false;
    }
    if (hdr->e_shoff != 0) {
        uint64_t sh_end = (uint64_t)hdr->e_shoff + ((uint64_t)hdr->e_shentsize * hdr->e_shnum);
        if (sh_end > file_size) return false;
    }
    return true;
}
