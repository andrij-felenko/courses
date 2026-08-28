#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <elf.h>
#include <string.h>

static const char* get_segment_type(uint32_t p_type) {
    switch (p_type) {
        case PT_NULL:         return "PT_NULL";
        case PT_LOAD:         return "PT_LOAD";
        case PT_DYNAMIC:      return "PT_DYNAMIC";
        case PT_INTERP:       return "PT_INTERP";
        case PT_NOTE:         return "PT_NOTE";
        case PT_PHDR:         return "PT_PHDR";
        case PT_TLS:          return "PT_TLS";
        case PT_GNU_EH_FRAME: return "PT_GNU_EH_FRAME";
        case PT_GNU_STACK:    return "PT_GNU_STACK";
        case PT_GNU_RELRO:    return "PT_GNU_RELRO";
        default:              return "UNKNOWN";
    }
}

static void print_flags(uint32_t flags, char *out) {
    out[0] = (flags & PF_R) ? 'R' : '-';
    out[1] = (flags & PF_W) ? 'W' : '-';
    out[2] = (flags & PF_X) ? 'E' : '-';
    out[3] = '\0';
}

int inspect_elf(const char *filename) {
    int fd = open(filename, O_RDONLY);
    if (fd < 0) {
        perror("Помилка відкриття файла");
        return 1;
    }

    struct stat st;
    if (fstat(fd, &st) < 0) {
        perror("Помилка отримання статусу fstat");
        close(fd);
        return 1;
    }

    if ((size_t)st.st_size < sizeof(Elf64_Ehdr)) {
        fprintf(stderr, "Помилка: Файл занадто малий для розміщення заголовка ELF\n");
        close(fd);
        return 1;
    }

    void *map = mmap(NULL, st.st_size, PROT_READ, MAP_PRIVATE, fd, 0);
    close(fd); /* Описус файла більше не потрібен після створення відображення mmap */

    if (map == MAP_FAILED) {
        perror("Помилка створення відображення mmap");
        return 1;
    }

    const Elf64_Ehdr *ehdr = (const Elf64_Ehdr*)map;

    /* 1. Перевірка магічних байтів */
    if (memcmp(ehdr->e_ident, ELFMAG, SELFMAG) != 0) {
        fprintf(stderr, "Помилка: Невалідний магічний підпис ELF\n");
        munmap(map, st.st_size);
        return 1;
    }

    if (ehdr->e_ident[EI_CLASS] != ELFCLASS64) {
        fprintf(stderr, "Помилка: Підтримуються лише 64-бітні ELF-файли\n");
        munmap(map, st.st_size);
        return 1;
    }

    printf("=== Аналіз заголовка ELF: %s ===\n", filename);
    printf("Точка входу (e_entry): 0x%lx\n", ehdr->e_entry);
    printf("Зсув PHT (e_phoff): %lu байтів\n", ehdr->e_phoff);
    printf("Кількість програмних заголовків: %u\n\n", ehdr->e_phnum);

    /* 2. Перевірка меж таблиці PHT */
    size_t pht_end = ehdr->e_phoff + (size_t)ehdr->e_phnum * sizeof(Elf64_Phdr);
    if (pht_end > (size_t)st.st_size) {
        fprintf(stderr, "Помилка: Таблиця PHT виходить за межі файла\n");
        munmap(map, st.st_size);
        return 1;
    }

    const Elf64_Phdr *phdr = (const Elf64_Phdr*)((const char*)map + ehdr->e_phoff);

    printf("%-16s %-10s %-18s %-10s %-10s %-5s\n",
           "Тип", "Зсув", "Вірт. адреса", "FileSiz", "MemSiz", "Права");
    printf("-------------------------------------------------------------------------\n");

    for (uint16_t i = 0; i < ehdr->e_phnum; i++) {
        char flags_str[4];
        print_flags(phdr[i].p_flags, flags_str);

        printf("%-16s 0x%08lx 0x%016lx 0x%08lx 0x%08lx %-5s\n",
               get_segment_type(phdr[i].p_type),
               phdr[i].p_offset,
               phdr[i].p_vaddr,
               phdr[i].p_filesz,
               phdr[i].p_memsz,
               flags_str);

        if (phdr[i].p_type == PT_INTERP) {
            if (phdr[i].p_offset + phdr[i].p_filesz <= (size_t)st.st_size) {
                const char *interp = (const char*)map + phdr[i].p_offset;
                printf("  [Інтерпретатор: %s]\n", interp);
            }
        } else if (phdr[i].p_type == PT_LOAD && phdr[i].p_memsz > phdr[i].p_filesz) {
            printf("  [Область .bss у пам'яті: +%lu байтів нулів]\n",
                   phdr[i].p_memsz - phdr[i].p_filesz);
        }
    }

    munmap(map, st.st_size);
    return 0;
}

int main(int argc, char **argv) {
    if (argc < 2) {
        fprintf(stderr, "Використання: %s <path-to-elf>\n", argv[0]);
        return 1;
    }
    return inspect_elf(argv[1]);
}
