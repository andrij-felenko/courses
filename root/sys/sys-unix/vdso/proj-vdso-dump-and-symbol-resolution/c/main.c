#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <sys/auxv.h>
#include <sys/syscall.h>
#include <unistd.h>
#include <elf.h>

/* Сигнатура функції clock_gettime у vDSO */
typedef int (*vdso_clock_gettime_t)(clockid_t clk_id, struct timespec *tp);

/* Пошук символу у vDSO за базовою адресою ELF */
static const Elf64_Sym *find_vdso_symbol(uintptr_t vdso_base, const char *sym_name) {
    const Elf64_Ehdr *ehdr = (const Elf64_Ehdr *)vdso_base;
    
    /* Перевірка магічного числа ELF */
    if (memcmp(ehdr->e_ident, ELFMAG, SELFMAG) != 0) {
        return NULL;
    }

    const Elf64_Phdr *phdr = (const Elf64_Phdr *)(vdso_base + ehdr->e_phoff);
    const Elf64_Dyn *dyn = NULL;

    /* Пошук сегмента PT_DYNAMIC */
    for (size_t i = 0; i < ehdr->e_phnum; i++) {
        if (phdr[i].p_type == PT_DYNAMIC) {
            dyn = (const Elf64_Dyn *)(vdso_base + phdr[i].p_offset);
            break;
        }
    }

    if (!dyn) return NULL;

    const Elf64_Sym *symtab = NULL;
    const char *strtab = NULL;

    /* Вилучення адрес таблиць символів та рядків */
    for (const Elf64_Dyn *d = dyn; d->d_tag != DT_NULL; d++) {
        if (d->d_tag == DT_SYMTAB) {
            symtab = (const Elf64_Sym *)(vdso_base + d->d_un.d_ptr);
        } else if (d->d_tag == DT_STRTAB) {
            strtab = (const char *)(vdso_base + d->d_un.d_ptr);
        }
    }

    if (!symtab || !strtab) return NULL;

    /* Лінійний обхід динамічної таблиці символів */
    for (size_t i = 0; symtab[i].st_name != 0 || i == 0; i++) {
        if (i > 0 && symtab[i].st_name != 0) {
            const char *name = strtab + symtab[i].st_name;
            if (strcmp(name, sym_name) == 0) {
                return &symtab[i];
            }
        }
    }

    return NULL;
}

int main(void) {
    /* Крок 1: Зчитування адреси vDSO з Auxiliary Vector */
    unsigned long aux_vdso = getauxval(AT_SYSINFO_EHDR);
    if (!aux_vdso) {
        fprintf(stderr, "Помилка: vDSO не знайдено в Auxiliary Vector\n");
        return EXIT_FAILURE;
    }

    printf("[+] Базова адреса vDSO з AT_SYSINFO_EHDR: 0x%lx\n", aux_vdso);

    /* Крок 2: Пошук символу __vdso_clock_gettime */
    const char *target_sym = "__vdso_clock_gettime";
    const Elf64_Sym *sym = find_vdso_symbol(aux_vdso, target_sym);

    if (!sym) {
        fprintf(stderr, "Помилка: Символ %s не знайдено у vDSO\n", target_sym);
        return EXIT_FAILURE;
    }

    /* Крок 3: Обчислення адреси вказівника на функцію */
    vdso_clock_gettime_t vdso_fn = (vdso_clock_gettime_t)(aux_vdso + sym->st_value);
    printf("[+] Знайдено символ %s за адресою: %p\n", target_sym, (void *)vdso_fn);

    struct timespec ts_vdso, ts_syscall;
    const int iterations = 5000000;

    /* Крок 4: Вимірювання часу виконання vDSO */
    struct timespec start, end;
    clock_gettime(CLOCK_MONOTONIC, &start);

    for (int i = 0; i < iterations; i++) {
        vdso_fn(CLOCK_REALTIME, &ts_vdso);
    }

    clock_gettime(CLOCK_MONOTONIC, &end);
    double vdso_time = (end.tv_sec - start.tv_sec) + (end.tv_nsec - start.tv_nsec) / 1e9;

    /* Крок 5: Вимірювання часу виконання прямого системного виклику syscall */
    clock_gettime(CLOCK_MONOTONIC, &start);

    for (int i = 0; i < iterations; i++) {
        syscall(SYS_clock_gettime, CLOCK_REALTIME, &ts_syscall);
    }

    clock_gettime(CLOCK_MONOTONIC, &end);
    double syscall_time = (end.tv_sec - start.tv_sec) + (end.tv_nsec - start.tv_nsec) / 1e9;

    /* Крок 6: Вивід результатів бенчмарку */
    printf("\n=== Результати бенчмарку продуктивності (%d викликів) ===\n", iterations);
    printf("Час виконання vDSO:     %.4f сек (%.2f ns/call)\n", vdso_time, (vdso_time / iterations) * 1e9);
    printf("Час виконання syscall:  %.4f сек (%.2f ns/call)\n", syscall_time, (syscall_time / iterations) * 1e9);
    printf("Прискорення vDSO:       у %.2f разів швидше!\n", syscall_time / vdso_time);

    return EXIT_SUCCESS;
}
