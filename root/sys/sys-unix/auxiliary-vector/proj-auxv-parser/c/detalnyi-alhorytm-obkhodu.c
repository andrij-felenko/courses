#include <stdint.h>
#include <elf.h>

/* Функція ручного аналізу стека без залучення glibc */
void parse_raw_stack_frame(uint64_t *raw_rsp) {
    if (!raw_rsp) return;

    /* 1. Читаємо argc */
    uint64_t argc = *raw_rsp;
    uint64_t *argv = raw_rsp + 1;
    
    /* 2. Обчислюємо позицію envp: пропускаємо argc вказівників + 1 NULL термінатор */
    uint64_t *envp = argv + argc + 1;
    
    /* 3. Проходити масив envp до нульового термінатора */
    uint64_t *env_runner = envp;
    while (*env_runner != 0) {
        env_runner++;
    }
    
    /* 4. Зсув за NULL термінатор envp на початок auxv */
    env_runner++; 
    Elf64_auxv_t *auxv = (Elf64_auxv_t *)env_runner;

    /* 5. Цикл читання записів auxv */
    while (auxv->a_type != AT_NULL) {
        if (auxv->a_type == AT_PAGESZ) {
            uint64_t page_size = auxv->a_un.a_val;
            (void)page_size;
        } else if (auxv->a_type == AT_SYSINFO_EHDR) {
            void *vdso_ptr = auxv->a_un.a_ptr;
            (void)vdso_ptr;
        }
        auxv++;
    }
}
