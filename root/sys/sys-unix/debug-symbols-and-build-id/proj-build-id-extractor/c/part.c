#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <elf.h>

#ifndef NT_GNU_BUILD_ID
#define NT_GNU_BUILD_ID 3
#endif

// Вирівнювання зміщення дескриптора примітки до межі 4 або 8 байтів
static inline size_t align_up(size_t offset, size_t alignment) {
    return (offset + alignment - 1) & ~(alignment - 1);
}

// Видобування Build ID із сирого буфера секції приміток (SHT_NOTE / PT_NOTE)
static bool extract_build_id_from_note(const uint8_t *note_data, size_t note_size,
                                      char *hex_out, size_t hex_max) {
    size_t offset = 0;
    while (offset + sizeof(Elf64_Nhdr) <= note_size) {
        const Elf64_Nhdr *nhdr = (const Elf64_Nhdr *)(note_data + offset);
        offset += sizeof(Elf64_Nhdr);

        const char *name = (const char *)(note_data + offset);
        offset = align_up(offset + nhdr->n_namesz, 4);

        const uint8_t *desc = note_data + offset;
        offset = align_up(offset + nhdr->n_descsz, 4);

        if (offset > note_size) {
            break; // Захист від пошкоджених зміщень у заголовку
        }

        // Перевіряємо тип примітки NT_GNU_BUILD_ID та ім'я "GNU"
        if (nhdr->n_type == NT_GNU_BUILD_ID && nhdr->n_namesz == 4 &&
            strncmp(name, "GNU", 4) == 0) {
            if (nhdr->n_descsz * 2 + 1 > hex_max) {
                return false;
            }
            for (uint32_t i = 0; i < nhdr->n_descsz; ++i) {
                snprintf(hex_out + (i * 2), 3, "%02x", desc[i]);
            }
            hex_out[nhdr->n_descsz * 2] = '\0';
            return true;
        }
    }
    return false;
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Використання: %s <шлях-до-elf-бінарника>\n", argv[0]);
        return EXIT_FAILURE;
    }

    const char *filepath = argv[1];
    int fd = open(filepath, O_RDONLY);
    if (fd < 0) {
        perror("Помилка відкриття файлу");
        return EXIT_FAILURE;
    }

    struct stat st;
    if (fstat(fd, &st) < 0 || st.st_size < (off_t)sizeof(Elf64_Ehdr)) {
        perror("Некоректний розмір файлу");
        close(fd);
        return EXIT_FAILURE;
    }

    const uint8_t *mapped = mmap(NULL, st.st_size, PROT_READ, MAP_PRIVATE, fd, 0);
    close(fd); // Дескриптор більше не потрібен після mmap
    if (mapped == MAP_FAILED) {
        perror("Помилка mmap");
        return EXIT_FAILURE;
    }

    // Валідація магічних байтів ELF
    const Elf64_Ehdr *ehdr = (const Elf64_Ehdr *)mapped;
    if (memcmp(ehdr->e_ident, ELFMAG, SELFMAG) != 0) {
        fprintf(stderr, "Помилка: файл не є форматом ELF.\n");
        munmap((void *)mapped, st.st_size);
        return EXIT_FAILURE;
    }

    if (ehdr->e_ident[EI_CLASS] != ELFCLASS64) {
        fprintf(stderr, "Помилка: підтримується лише 64-бітний ELF (ELFCLASS64).\n");
        munmap((void *)mapped, st.st_size);
        return EXIT_FAILURE;
    }

    // Перевірка меж таблиці заголовків секцій
    if (ehdr->e_shoff == 0 || ehdr->e_shoff + ehdr->e_shnum * sizeof(Elf64_Shdr) > (size_t)st.st_size) {
        fprintf(stderr, "Помилка: пошкоджена або відсутня таблиця секцій (SHT).\n");
        munmap((void *)mapped, st.st_size);
        return EXIT_FAILURE;
    }

    const Elf64_Shdr *shdrs = (const Elf64_Shdr *)(mapped + ehdr->e_shoff);
    const Elf64_Shdr *shstrtab_hdr = &shdrs[ehdr->e_shstrndx];
    const char *shstrtab = (const char *)(mapped + shstrtab_hdr->sh_offset);

    char build_id_hex[128] = {0};
    bool found_build_id = false;
    char debuglink_name[256] = {0};
    uint32_t debuglink_crc = 0;
    bool found_debuglink = false;

    for (uint16_t i = 0; i < ehdr->e_shnum; ++i) {
        const char *sec_name = shstrtab + shdrs[i].sh_name;
        
        // 1. Пошук .note.gnu.build-id
        if (shdrs[i].sh_type == SHT_NOTE && strcmp(sec_name, ".note.gnu.build-id") == 0) {
            const uint8_t *sec_data = mapped + shdrs[i].sh_offset;
            size_t sec_size = shdrs[i].sh_size;
            if (extract_build_id_from_note(sec_data, sec_size, build_id_hex, sizeof(build_id_hex))) {
                found_build_id = true;
            }
        }

        // 2. Пошук .gnu_debuglink
        if (strcmp(sec_name, ".gnu_debuglink") == 0 && shdrs[i].sh_size >= 5) {
            const uint8_t *sec_data = mapped + shdrs[i].sh_offset;
            size_t sec_size = shdrs[i].sh_size;
            
            // Назва файлу завершується нульовим байтом, а останні 4 байти — CRC32
            size_t name_len = strnlen((const char *)sec_data, sec_size - 4);
            if (name_len < sizeof(debuglink_name)) {
                memcpy(debuglink_name, sec_data, name_len);
                debuglink_name[name_len] = '\0';
                // Останні 4 байти секції — CRC32 у форматі little-endian
                debuglink_crc = *(const uint32_t *)(sec_data + sec_size - 4);
                found_debuglink = true;
            }
        }
    }

    printf("Аналіз бінарника: %s\n", filepath);
    if (found_build_id) {
        printf("  [✓] Build ID:       %s\n", build_id_hex);
        printf("      Канонічний шлях: /usr/lib/debug/.build-id/%.2s/%s.debug\n",
               build_id_hex, build_id_hex + 2);
    } else {
        printf("  [✗] Build ID:       відсутній\n");
    }

    if (found_debuglink) {
        printf("  [✓] gnu_debuglink:  %s (CRC32: 0x%08x)\n", debuglink_name, debuglink_crc);
    } else {
        printf("  [✗] gnu_debuglink:  відсутній\n");
    }

    munmap((void *)mapped, st.st_size);
    return EXIT_SUCCESS;
}
