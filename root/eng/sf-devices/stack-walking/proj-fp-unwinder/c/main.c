#define _GNU_SOURCE
#include <unistd.h>
#include <stdint.h>
#include <stddef.h>
#include <signal.h>
#include <sys/syscall.h>

#define MAX_FRAMES 64

// Структура класичного стекового кадру x86-64
struct stack_frame {
    struct stack_frame* saved_fp;
    void* return_address;
};

// Сигнально-безпечне перетворення 64-бітної адреси у шістнадцятковий рядок
static void print_hex(uintptr_t val, char* out_buf, size_t* out_len) {
    static const char hex_digits[] = "0123456789abcdef";
    out_buf[0] = '0';
    out_buf[1] = 'x';
    for (int i = 15; i >= 0; --i) {
        out_buf[2 + (15 - i)] = hex_digits[(val >> (i * 4)) & 0x0f];
    }
    out_buf[18] = '\n';
    *out_len = 19;
}

// Функція розмотування стека за ланцюгом Frame Pointer
int unwind_frame_pointer(void** buffer, int max_depth) {
    if (!buffer || max_depth <= 0) {
        return 0;
    }

    // Зчитуємо початкове значення базового покажчика кадру
    uintptr_t current_fp = (uintptr_t)__builtin_frame_address(0);
    int count = 0;

    // Орієнтовна верхня межа стека для перевірки діапазону адрес
    uintptr_t stack_limit = current_fp + (8 * 1024 * 1024); // 8 МБ ліміту

    while (current_fp != 0 && count < max_depth) {
        // Перевірка 1: перевірка кратності 8 байтам
        if (current_fp & (sizeof(void*) - 1)) {
            break;
        }

        struct stack_frame* frame = (struct stack_frame*)current_fp;
        
        // Зберігаємо адресу повернення для подальшого декодування
        buffer[count++] = frame->return_address;

        uintptr_t next_fp = (uintptr_t)frame->saved_fp;

        // Перевірка 2: монотонність зростання адрес і межі стека
        if (next_fp <= current_fp || next_fp >= stack_limit) {
            break;
        }

        current_fp = next_fp;
    }

    return count;
}

// Асинхронно-сигнально-безпечний друк зібраного стека у STDERR
void safe_print_stacktrace(void* const* buffer, int depth) {
    static const char header[] = "=== Stack Backtrace ===\n";
    (void)syscall(SYS_write, STDERR_FILENO, header, sizeof(header) - 1);

    char num_buf[32];
    for (int i = 0; i < depth; ++i) {
        size_t len = 0;
        print_hex((uintptr_t)buffer[i], num_buf, &len);
        (void)syscall(SYS_write, STDERR_FILENO, "  #", 3);
        (void)syscall(SYS_write, STDERR_FILENO, num_buf, len);
    }
}
