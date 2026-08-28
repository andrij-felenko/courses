#define _GNU_SOURCE
#include <elf.h>
#include <fcntl.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <unistd.h>

/* Трансляція віртуальної адреси у зміщення всередині файлу за таблицею PT_LOAD */
static uint64_t vaddr_to_offset(const Elf64_Ehdr *hdr, uint64_t vaddr, size_t file_size) {
    if (hdr->e_type == ET_DYN) {
        /* Для Position-Independent Executable віртуальні адреси в PT_DYNAMIC збігаються зі зміщеннями */
        if (vaddr < file_size) {
            return vaddr;
        }
    }

    const Elf64_Phdr *ph = (const Elf64_Phdr *)((const uint8_t *)hdr + hdr->e_phoff);
    for (uint16_t i = 0; i < hdr->e_phnum; ++i) {
        if (ph[i].p_type == PT_LOAD) {
            if (vaddr >= ph[i].p_vaddr && vaddr < (ph[i].p_vaddr + ph[i].p_filesz)) {
                return ph[i].p_offset + (vaddr - ph[i].p_vaddr);
            }
        }
    }
    return 0;
}

static const char *machine_to_string(uint16_t machine) {
    switch (machine) {
        case EM_X86_64:  return "Advanced Micro Devices X86-64";
        case EM_AARCH64: return "ARM AArch64";
        case EM_ARM:     return "ARM 32-bit";
        case EM_RISCV:   return "RISC-V";
        case EM_386:     return "Intel 80386";
        default:         return "Unknown Architecture";
    }
}

static void inspect_elf(const uint8_t *data, size_t size) {
    if (size < sizeof(Elf64_Ehdr)) {
        fprintf(stderr, "Помилка: файл занадто малий для формату ELF64.\n");
        return;
    }

    const Elf64_Ehdr *hdr = (const Elf64_Ehdr *)data;

    /* 1. Перевірка магічних байтів \x7fELF */
    if (memcmp(hdr->e_ident, ELFMAG, SELFMAG) != 0) {
        fprintf(stderr, "Помилка: файл не є коректним ELF-образом (невірні магічні байти).\n");
        return;
    }

    if (hdr->e_ident[EI_CLASS] != ELFCLASS64) {
        fprintf(stderr, "Повідомлення: підтримуються лише 64-бітні бінарники ELFCLASS64.\n");
        return;
    }

    printf("=== ПАСПОРТ БІНАРНИКА ===\n");
    printf("Клас:              ELF64\n");
    printf("Порядок байтів:    %s\n", hdr->e_ident[EI_DATA] == ELFDATA2LSB ? "Little-Endian (LSB)" : "Big-Endian (MSB)");
    printf("Архітектура:       %s (0x%04x)\n", machine_to_string(hdr->e_machine), hdr->e_machine);
    printf("Тип файлу:         %s\n", hdr->e_type == ET_EXEC ? "ET_EXEC (Виконуваний із фіксованою адресою)" :
                                       hdr->e_type == ET_DYN ? "ET_DYN (Position-Independent Executable або Shared Object)" : "Інший");
    printf("Точка входу:       0x%016lx\n", (unsigned long)hdr->e_entry);

    /* 2. Аудит Program Headers */
    if (hdr->e_phoff + (hdr->e_phnum * sizeof(Elf64_Phdr)) > size) {
        fprintf(stderr, "Помилка: пошкоджена таблиця Program Headers виходить за межі файлу.\n");
        return;
    }

    const Elf64_Phdr *ph = (const Elf64_Phdr *)(data + hdr->e_phoff);
    const char *interp_path = NULL;
    bool has_nx_stack = true;
    bool has_relro = false;
    const Elf64_Phdr *dyn_ph = NULL;

    for (uint16_t i = 0; i < hdr->e_phnum; ++i) {
        if (ph[i].p_type == PT_INTERP) {
            if (ph[i].p_offset + ph[i].p_filesz <= size) {
                interp_path = (const char *)(data + ph[i].p_offset);
            }
        } else if (ph[i].p_type == PT_GNU_STACK) {
            if (ph[i].p_flags & PF_X) {
                has_nx_stack = false; /* Стек має право на виконання - небезпечно! */
            }
        } else if (ph[i].p_type == PT_GNU_RELRO) {
            has_relro = true;
        } else if (ph[i].p_type == PT_DYNAMIC) {
            dyn_ph = &ph[i];
        }
    }

    printf("\n=== ЗАХИСНІ МЕХАНІЗМИ ТА ІНТЕРПРЕТАТОР ===\n");
    printf("Тип зв'язування:   %s\n", interp_path ? "Динамічне (Dynamically linked)" : "Статичне (Statically linked)");
    if (interp_path) {
        printf("Інтерпретатор:     %s\n", interp_path);
    }
    printf("NX (No-Execute):   %s\n", has_nx_stack ? "Увімкнено (Стек захищено від виконання коду)" : "ВИМКНЕНО (Стек має права на виконання!)");
    printf("RELRO:             %s\n", has_relro ? "Присутній (PT_GNU_RELRO активний)" : "Відсутній (Таблиця GOT доступна для запису)");

    /* 3. Перевірка таблиці секцій на наявність .symtab (stripped / not stripped) */
    bool has_symtab = false;
    if (hdr->e_shoff > 0 && (hdr->e_shoff + (hdr->e_shnum * sizeof(Elf64_Shdr)) <= size)) {
        const Elf64_Shdr *sh = (const Elf64_Shdr *)(data + hdr->e_shoff);
        if (hdr->e_shstrndx < hdr->e_shnum) {
            const char *shstrtab = (const char *)(data + sh[hdr->e_shstrndx].sh_offset);
            for (uint16_t i = 0; i < hdr->e_shnum; ++i) {
                const char *sname = shstrtab + sh[i].sh_name;
                if (strcmp(sname, ".symtab") == 0) {
                    has_symtab = true;
                    break;
                }
            }
        }
    }
    printf("Символи:           %s\n", has_symtab ? "not stripped (Присутня повна таблиця .symtab)" : "stripped (Налагоджувальні символи видалено)");

    /* 4. Аудит динамічних залежностей (DT_NEEDED) */
    if (dyn_ph && dyn_ph->p_offset + dyn_ph->p_filesz <= size) {
        printf("\n=== ДИНАМІЧНІ ЗАЛЕЖНОСТІ (DT_NEEDED) ===\n");
        const Elf64_Dyn *dyn = (const Elf64_Dyn *)(data + dyn_ph->p_offset);
        size_t dyn_count = dyn_ph->p_filesz / sizeof(Elf64_Dyn);

        /* Знаходження таблиці рядків DT_STRTAB */
        uint64_t strtab_vaddr = 0;
        for (size_t i = 0; i < dyn_count && dyn[i].d_tag != DT_NULL; ++i) {
            if (dyn[i].d_tag == DT_STRTAB) {
                strtab_vaddr = dyn[i].d_un.d_ptr;
                break;
            }
        }

        uint64_t strtab_offset = strtab_vaddr ? vaddr_to_offset(hdr, strtab_vaddr, size) : 0;
        if (strtab_offset && strtab_offset < size) {
            const char *dynstr = (const char *)(data + strtab_offset);
            bool found_needed = false;

            for (size_t i = 0; i < dyn_count && dyn[i].d_tag != DT_NULL; ++i) {
                if (dyn[i].d_tag == DT_NEEDED) {
                    uint64_t str_idx = dyn[i].d_un.d_val;
                    if (strtab_offset + str_idx < size) {
                        printf("  * Потрібна бібліотека: %s\n", dynstr + str_idx);
                        found_needed = true;
                    }
                } else if (dyn[i].d_tag == DT_RUNPATH) {
                    uint64_t str_idx = dyn[i].d_un.d_val;
                    if (strtab_offset + str_idx < size) {
                        printf("  * Вшитий RUNPATH:     %s\n", dynstr + str_idx);
                    }
                } else if (dyn[i].d_tag == DT_RPATH) {
                    uint64_t str_idx = dyn[i].d_un.d_val;
                    if (strtab_offset + str_idx < size) {
                        printf("  * Вшитий RPATH:       %s (Застарілий)\n", dynstr + str_idx);
                    }
                }
            }

            if (!found_needed) {
                printf("  (Записів DT_NEEDED не виявлено)\n");
            }
        } else {
            printf("  [Увага: не вдалося розв'язати зміщення таблиці DT_STRTAB]\n");
        }
    }
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Використання: %s <шлях-до-elf-файлу>\n", argv[0]);
        return EXIT_FAILURE;
    }

    int fd = open(argv[1], O_RDONLY | O_CLOEXEC);
    if (fd < 0) {
        perror("open");
        return EXIT_FAILURE;
    }

    struct stat st;
    if (fstat(fd, &st) < 0) {
        perror("fstat");
        close(fd);
        return EXIT_FAILURE;
    }

    if (st.st_size == 0) {
        fprintf(stderr, "Помилка: файл порожній.\n");
        close(fd);
        return EXIT_FAILURE;
    }

    void *map = mmap(NULL, (size_t)st.st_size, PROT_READ, MAP_PRIVATE, fd, 0);
    if (map == MAP_FAILED) {
        perror("mmap");
        close(fd);
        return EXIT_FAILURE;
    }

    inspect_elf((const uint8_t *)map, (size_t)st.st_size);

    munmap(map, (size_t)st.st_size);
    close(fd);
    return EXIT_SUCCESS;
}
