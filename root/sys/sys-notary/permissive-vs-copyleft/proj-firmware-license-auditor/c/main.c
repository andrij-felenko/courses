#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <elf.h>
#include <sys/stat.h>
#include <sys/mman.h>

typedef enum {
    LIC_PERMISSIVE,
    LIC_WEAK_COPYLEFT,
    LIC_STRONG_COPYLEFT,
    LIC_UNKNOWN
} LicenseCategory;

typedef struct {
    const char *lib_name;
    const char *license;
    LicenseCategory category;
} LibraryLicenseEntry;

static const LibraryLicenseEntry KNOWN_LIBRARIES[] = {
    {"libc.so.6", "LGPL-2.1-or-later", LIC_WEAK_COPYLEFT},
    {"libm.so.6", "LGPL-2.1-or-later", LIC_WEAK_COPYLEFT},
    {"libcrypto.so.3", "Apache-2.0", LIC_PERMISSIVE},
    {"libssl.so.3", "Apache-2.0", LIC_PERMISSIVE},
    {"libz.so.1", "Zlib", LIC_PERMISSIVE},
    {"libsqlite3.so.0", "Public-Domain", LIC_PERMISSIVE},
    {"libgpl_engine.so.1", "GPL-3.0-only", LIC_STRONG_COPYLEFT},
    {NULL, NULL, LIC_UNKNOWN}
};

static const LibraryLicenseEntry* lookup_license(const char *lib_name) {
    for (int i = 0; KNOWN_LIBRARIES[i].lib_name != NULL; ++i) {
        if (strcmp(KNOWN_LIBRARIES[i].lib_name, lib_name) == 0) {
            return &KNOWN_LIBRARIES[i];
        }
    }
    return NULL;
}

int audit_elf_dependencies(const char *filepath) {
    int fd = open(filepath, O_RDONLY);
    if (fd < 0) {
        perror("Не вдалося відкрити ELF-файл");
        return -1;
    }

    struct stat st;
    if (fstat(fd, &st) < 0) {
        perror("Помилка fstat");
        close(fd);
        return -1;
    }

    uint8_t *map = (uint8_t*)mmap(NULL, st.st_size, PROT_READ, MAP_PRIVATE, fd, 0);
    if (map == MAP_FAILED) {
        perror("Помилка mmap");
        close(fd);
        return -1;
    }

    Elf64_Ehdr *ehdr = (Elf64_Ehdr*)map;
    if (memcmp(ehdr->e_ident, ELFMAG, SELFMAG) != 0 || ehdr->e_ident[EI_CLASS] != ELFCLASS64) {
        fprintf(stderr, "Помилка: невалідний 64-бітний ELF-файл: %s\n", filepath);
        munmap(map, st.st_size);
        close(fd);
        return -1;
    }

    Elf64_Phdr *phdr = (Elf64_Phdr*)(map + ehdr->e_phoff);
    Elf64_Dyn *dynamic = NULL;
    uint64_t dyn_size = 0;

    for (int i = 0; i < ehdr->e_phnum; ++i) {
        if (phdr[i].p_type == PT_DYNAMIC) {
            dynamic = (Elf64_Dyn*)(map + phdr[i].p_offset);
            dyn_size = phdr[i].p_filesz;
            break;
        }
    }

    if (!dynamic) {
        printf("Бінарник статично скомпільований (сегмент PT_DYNAMIC відсутній).\n");
        munmap(map, st.st_size);
        close(fd);
        return 0;
    }

    /* Знаходимо секцію рядків через таблицю секцій для точного відображення */
    const char *strtab = NULL;
    int num_dyn = dyn_size / sizeof(Elf64_Dyn);

    Elf64_Shdr *shdr = (Elf64_Shdr*)(map + ehdr->e_shoff);
    for (int i = 0; i < ehdr->e_shnum; ++i) {
        if (shdr[i].sh_type == SHT_STRTAB && i != ehdr->e_shstrndx) {
            strtab = (const char*)(map + shdr[i].sh_offset);
            break;
        }
    }

    int violations_count = 0;
    printf("=== Аудит динамічних залежностей ELF: %s ===\n", filepath);

    for (int i = 0; num_dyn > i; ++i) {
        if (dynamic[i].d_tag == DT_NEEDED && strtab != NULL) {
            const char *lib_name = strtab + dynamic[i].d_un.d_val;
            const LibraryLicenseEntry *entry = lookup_license(lib_name);

            if (!entry) {
                printf("  [?] %-20s -> Ліцензія НЕВІДОМА (потрібен ручний аналіз)\n", lib_name);
            } else if (entry->category == LIC_STRONG_COPYLEFT) {
                printf("  [!] %-20s -> %s (КРИТИЧНО: Ризик ліцензійного зараження!)\n", lib_name, entry->license);
                violations_count++;
            } else {
                printf("  [✓] %-20s -> %s (Дозволено для динамічного лінку)\n", lib_name, entry->license);
            }
        }
    }

    munmap(map, st.st_size);
    close(fd);
    return violations_count;
}
