/* Безпечне вилучення шляху до динамічного лінкера (PT_INTERP) з ELF64 файлу. */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <elf.h>
#include <sys/stat.h>

int main(int argc, char *argv[])
{
    if (argc < 2) {
        fprintf(stderr, "Використання: %s <elf-binary>\n", argv[0]);
        return 1;
    }

    int fd = open(argv[1], O_RDONLY);
    if (fd < 0) {
        perror("open");
        return 1;
    }

    Elf64_Ehdr ehdr;
    if (read(fd, &ehdr, sizeof(ehdr)) != sizeof(ehdr)) {
        fprintf(stderr, "Помилка: не вдалося прочитати заголовок ELF\n");
        close(fd);
        return 1;
    }

    /* Перевірка сигнатури \x7fELF */
    if (memcmp(ehdr.e_ident, ELFMAG, SELFMAG) != 0 || ehdr.e_ident[EI_CLASS] != ELFCLASS64) {
        fprintf(stderr, "Помилка: файл не є 64-бітним ELF\n");
        close(fd);
        return 1;
    }

    /* Зчитування таблиці програмних заголовків */
    Elf64_Phdr *phdrs = malloc(ehdr.e_phnum * sizeof(Elf64_Phdr));
    if (!phdrs) {
        perror("malloc");
        close(fd);
        return 1;
    }

    if (pread(fd, phdrs, ehdr.e_phnum * sizeof(Elf64_Phdr), (off_t)ehdr.e_phoff) < 0) {
        perror("pread");
        free(phdrs);
        close(fd);
        return 1;
    }

    int found = 0;
    for (int i = 0; i < ehdr.e_phnum; i++) {
        if (phdrs[i].p_type == PT_INTERP) {
            char interp[512];
            size_t len = phdrs[i].p_filesz < sizeof(interp) - 1 ? phdrs[i].p_filesz : sizeof(interp) - 1;
            if (pread(fd, interp, len, (off_t)phdrs[i].p_offset) > 0) {
                interp[len] = '\0';
                printf("ELF Інтерпретатор (PT_INTERP): %s\n", interp);
                found = 1;
            }
            break;
        }
    }

    if (!found) {
        printf("Файл скомпільовано статично або заголовок PT_INTERP відсутній.\n");
    }

    free(phdrs);
    close(fd);
    return 0;
}
