#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <elf.h>
#include <sys/stat.h>
#include <sys/mman.h>

/* Інспекція заголовків ELF та динамічних тегів RUNPATH / RPATH */
int inspect_elf(const char *filepath) {
    int fd = open(filepath, O_RDONLY);
    if (fd < 0) {
        perror("Помилка відкриття файлу");
        return -1;
    }

    struct stat st;
    if (fstat(fd, &st) < 0) {
        perror("Помилка fstat");
        close(fd);
        return -1;
    }

    uint8_t *map = (uint8_t *)mmap(NULL, st.st_size, PROT_READ, MAP_PRIVATE, fd, 0);
    if (map == MAP_FAILED) {
        perror("Помилка mmap");
        close(fd);
        return -1;
    }

    Elf64_Ehdr *ehdr = (Elf64_Ehdr *)map;
    if (memcmp(ehdr->e_ident, ELFMAG, SELFMAG) != 0) {
        fprintf(stderr, "Файл не є валідним ELF\n");
        munmap(map, st.st_size);
        close(fd);
        return -1;
    }

    Elf64_Shdr *sections = (Elf64_Shdr *)(map + ehdr->e_shoff);
    Elf64_Shdr *dyn_shdr = NULL;
    Elf64_Shdr *str_shdr = NULL;

    for (int i = 0; i < ehdr->e_shnum; i++) {
        if (sections[i].sh_type == SHT_DYNAMIC) {
            dyn_shdr = &sections[i];
        }
    }

    if (!dyn_shdr) {
        printf("Бінарник є статичним або не має секції .dynamic\n");
        munmap(map, st.st_size);
        close(fd);
        return 0;
    }

    str_shdr = &sections[dyn_shdr->sh_link];
    const char *dynstr = (const char *)(map + str_shdr->sh_offset);
    Elf64_Dyn *dyn_entries = (Elf64_Dyn *)(map + dyn_shdr->sh_offset);
    size_t count = dyn_shdr->sh_size / sizeof(Elf64_Dyn);

    int has_rpath = 0, has_runpath = 0;
    for (size_t i = 0; i < count; i++) {
        if (dyn_entries[i].d_tag == DT_RPATH) {
            has_rpath = 1;
            printf("[!] Знайдено DT_RPATH: %s\n", dynstr + dyn_entries[i].d_un.d_val);
        } else if (dyn_entries[i].d_tag == DT_RUNPATH) {
            has_runpath = 1;
            printf("[✓] Знайдено DT_RUNPATH: %s\n", dynstr + dyn_entries[i].d_un.d_val);
        }
    }

    if (!has_runpath && !has_rpath) {
        printf("[-] У бінарнику немає записів RPATH або RUNPATH\n");
    }

    munmap(map, st.st_size);
    close(fd);
    return 0;
}

int main(int argc, char **argv) {
    if (argc < 2) {
        fprintf(stderr, "Використання: %s <elf_binary>\n", argv[0]);
        return 1;
    }
    return inspect_elf(argv[1]) == 0 ? 0 : 1;
}
