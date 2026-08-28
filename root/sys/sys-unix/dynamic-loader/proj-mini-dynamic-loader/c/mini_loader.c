/* mini_loader.c — Мінімалістичний ELF-завантажувач мовою C */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/mman.h>
#include <elf.h>

typedef int (*entry_func_t)(void);

static void log_error(const char *msg) {
    perror(msg);
}

int load_and_run_elf(const char *filename) {
    int fd = open(filename, O_RDONLY);
    if (fd < 0) {
        log_error("Failed to open ELF file");
        return -1;
    }

    Elf64_Ehdr ehdr;
    if (read(fd, &ehdr, sizeof(ehdr)) != sizeof(ehdr)) {
        log_error("Failed to read ELF header");
        close(fd);
        return -1;
    }

    /* Перевірка Magic-байтів ELF */
    if (memcmp(ehdr.e_ident, ELFMAG, SELFMAG) != 0) {
        fprintf(stderr, "Invalid ELF magic header\n");
        close(fd);
        return -1;
    }

    /* Виділення пам'яті під заголовки програм */
    Elf64_Phdr *phdrs = malloc(ehdr.e_phnum * sizeof(Elf64_Phdr));
    if (!phdrs) {
        close(fd);
        return -1;
    }

    lseek(fd, ehdr.e_phoff, SEEK_SET);
    if (read(fd, phdrs, ehdr.e_phnum * sizeof(Elf64_Phdr)) != (ssize_t)(ehdr.e_phnum * sizeof(Elf64_Phdr))) {
        log_error("Failed to read Program Headers");
        free(phdrs);
        close(fd);
        return -1;
    }

    /* Розрахунок загального розміру віртуальної пам'яті */
    uintptr_t min_vaddr = (uintptr_t)-1;
    uintptr_t max_vaddr = 0;

    for (int i = 0; i < ehdr.e_phnum; i++) {
        if (phdrs[i].p_type == PT_LOAD) {
            if (phdrs[i].p_vaddr < min_vaddr) min_vaddr = phdrs[i].p_vaddr;
            if (phdrs[i].p_vaddr + phdrs[i].p_memsz > max_vaddr) {
                max_vaddr = phdrs[i].p_vaddr + phdrs[i].p_memsz;
            }
        }
    }

    size_t total_size = max_vaddr - min_vaddr;
    
    /* Виділення анонімної пам'яті під бінарник */
    void *load_base = mmap(NULL, total_size, PROT_READ | PROT_WRITE | PROT_EXEC,
                           MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (load_base == MAP_FAILED) {
        log_error("mmap failed");
        free(phdrs);
        close(fd);
        return -1;
    }

    uintptr_t delta = (uintptr_t)load_base - min_vaddr;

    /* Відображення сегментів PT_LOAD */
    Elf64_Dyn *dyn_section = NULL;
    size_t dyn_size = 0;

    for (int i = 0; i < ehdr.e_phnum; i++) {
        if (phdrs[i].p_type == PT_LOAD) {
            void *seg_dest = (void *)((uintptr_t)load_base + (phdrs[i].p_vaddr - min_vaddr));
            lseek(fd, phdrs[i].p_offset, SEEK_SET);
            if (read(fd, seg_dest, phdrs[i].p_filesz) != (ssize_t)phdrs[i].p_filesz) {
                log_error("Failed to read segment data");
                munmap(load_base, total_size);
                free(phdrs);
                close(fd);
                return -1;
            }
            /* Обнулення секції .bss */
            if (phdrs[i].p_memsz > phdrs[i].p_filesz) {
                memset((char *)seg_dest + phdrs[i].p_filesz, 0, phdrs[i].p_memsz - phdrs[i].p_filesz);
            }
        } else if (phdrs[i].p_type == PT_DYNAMIC) {
            dyn_section = (Elf64_Dyn *)((uintptr_t)load_base + (phdrs[i].p_vaddr - min_vaddr));
            dyn_size = phdrs[i].p_memsz;
        }
    }

    free(phdrs);
    close(fd);

    /* Обробка релокацій у секції .dynamic */
    if (dyn_section) {
        Elf64_Rela *rela_table = NULL;
        size_t rela_size = 0;
        size_t rela_ent = sizeof(Elf64_Rela);

        for (Elf64_Dyn *d = dyn_section; d->d_tag != DT_NULL; d++) {
            if (d->d_tag == DT_RELA) {
                rela_table = (Elf64_Rela *)(delta + d->d_un.d_ptr);
            } else if (d->d_tag == DT_RELASZ) {
                rela_size = d->d_un.d_val;
            } else if (d->d_tag == DT_RELAENT) {
                rela_ent = d->d_un.d_val;
            }
        }

        if (rela_table && rela_size > 0) {
            size_t count = rela_size / rela_ent;
            for (size_t i = 0; i < count; i++) {
                Elf64_Rela *rel = &rela_table[i];
                if (ELF64_R_TYPE(rel->r_info) == R_X86_64_RELATIVE) {
                    uintptr_t *target = (uintptr_t *)(delta + rel->r_offset);
                    *target = delta + rel->r_addend;
                }
            }
        }
    }

    /* Передача керування точці входу */
    uintptr_t entry_point = delta + ehdr.e_entry;
    entry_func_t entry = (entry_func_t)entry_point;
    printf("[rtld-mini] Jumping to entry point at %p...\n", (void *)entry_point);
    
    int result = entry();

    munmap(load_base, total_size);
    return result;
}

int main(int argc, char **argv) {
    if (argc < 2) {
        printf("Usage: %s <elf_binary>\n", argv[0]);
        return 1;
    }
    return load_and_run_elf(argv[1]);
}
