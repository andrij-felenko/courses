#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

#if defined(_WIN32) || defined(_WIN64)
#include <windows.h>
#else
#include <sys/mman.h>
#include <unistd.h>
#endif

/* Сигнатура функції, яку генерує JIT */
typedef int64_t (*jit_func_t)(int64_t, int64_t);

/* Структура для керування виконуваною сторінкою */
typedef struct {
    uint8_t *code;
    size_t size;
} jit_buffer_t;

/* 1. Виділення пам'яті (W=1, X=0) */
int jit_buffer_init(jit_buffer_t *buf, size_t size) {
    buf->size = size;
#if defined(_WIN32) || defined(_WIN64)
    buf->code = (uint8_t *)VirtualAlloc(NULL, size, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
    if (!buf->code) return -1;
#else
    buf->code = (uint8_t *)mmap(NULL, size, PROT_READ | PROT_WRITE,
                                MAP_ANONYMOUS | MAP_PRIVATE, -1, 0);
    if (buf->code == MAP_FAILED) {
        buf->code = NULL;
        return -1;
    }
#endif
    return 0;
}

/* 2. Генерація байтів x86-64 для f(a, b) = a * b + constant */
size_t jit_emit_mul_add(jit_buffer_t *buf, int32_t constant) {
    uint8_t *p = buf->code;

#if defined(_WIN32) || defined(_WIN64)
    /* imul rcx, rdx */
    *p++ = 0x48; *p++ = 0x0F; *p++ = 0xAF; *p++ = 0xCA;
    /* add rcx, constant (imm32) */
    *p++ = 0x48; *p++ = 0x81; *p++ = 0xC1;
    memcpy(p, &constant, sizeof(int32_t));
    p += sizeof(int32_t);
    /* mov rax, rcx */
    *p++ = 0x48; *p++ = 0x89; *p++ = 0xC8;
#else
    /* imul rdi, rsi */
    *p++ = 0x48; *p++ = 0x0F; *p++ = 0xAF; *p++ = 0xFE;
    /* add rdi, constant (imm32) */
    *p++ = 0x48; *p++ = 0x81; *p++ = 0xC7;
    memcpy(p, &constant, sizeof(int32_t));
    p += sizeof(int32_t);
    /* mov rax, rdi */
    *p++ = 0x48; *p++ = 0x89; *p++ = 0xF8;
#endif
    /* ret */
    *p++ = 0xC3;

    return (size_t)(p - buf->code);
}

/* 3. Перемикання прав на виконання (W=0, X=1) згідно з W^X */
int jit_buffer_protect(jit_buffer_t *buf) {
#if defined(_WIN32) || defined(_WIN64)
    DWORD old_protect;
    if (!VirtualProtect(buf->code, buf->size, PAGE_EXECUTE_READ, &old_protect)) {
        return -1;
    }
#else
    if (mprotect(buf->code, buf->size, PROT_READ | PROT_EXEC) != 0) {
        return -1;
    }
    /* Скидання кешу інструкцій (Instruction Cache flush) */
    __builtin___clear_cache((char *)buf->code, (char *)buf->code + buf->size);
#endif
    return 0;
}

/* 4. Звільнення виконуваної сторінки */
void jit_buffer_free(jit_buffer_t *buf) {
    if (!buf->code) return;
#if defined(_WIN32) || defined(_WIN64)
    VirtualFree(buf->code, 0, MEM_RELEASE);
#else
    munmap(buf->code, buf->size);
#endif
    buf->code = NULL;
}

int main(void) {
    jit_buffer_t jit;
    const size_t page_size = 4096;

    if (jit_buffer_init(&jit, page_size) != 0) {
        perror("Не вдалося виділити JIT-пам'ять");
        return 1;
    }

    /* Емітуємо код обчислення: f(a, b) = a * b + 42 */
    jit_emit_mul_add(&jit, 42);

    /* Захищаємо пам'ять від запису й дозволяємо виконання */
    if (jit_buffer_protect(&jit) != 0) {
        perror("mprotect помилка");
        jit_buffer_free(&jit);
        return 1;
    }

    /* Викликаємо згенеровану функцію через покажчик */
    jit_func_t fn = (jit_func_t)(uintptr_t)jit.code;
    int64_t a = 7, b = 8;
    int64_t result = fn(a, b);

    printf("JIT f(%lld, %lld) = %lld (очікувано 7 * 8 + 42 = 98)\n",
           (long long)a, (long long)b, (long long)result);

    jit_buffer_free(&jit);
    return 0;
}
