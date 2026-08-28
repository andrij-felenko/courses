/* core/src/syscalls.c */
#include <sys/stat.h>
#include <errno.h>
#include <stdint.h>

#undef errno
extern int errno;

extern uint32_t _end;     /* Символ початку купи з лінкер-скрипта */
extern uint32_t _estack;  /* Вершина стеку */

void* _sbrk(ptrdiff_t incr) {
    static uint8_t *heap_end = NULL;
    uint8_t *prev_heap_end;

    if (heap_end == NULL) {
        heap_end = (uint8_t*)&_end;
    }

    prev_heap_end = heap_end;

    /* Запобігання зіткненню купи зі стеком (залишаємо запас під стек 1 КБ) */
    if (heap_end + incr > (uint8_t*)&_estack - 0x400) {
        errno = ENOMEM;
        return (void*)-1;
    }

    heap_end += incr;
    return (void*)prev_heap_end;
}

/* Перенаправлення виводу printf у низькорівневий UART драйвер */
extern void uart_send_char(char c);

int _write(int file, char *ptr, int len) {
    (void)file;
    for (int i = 0; i < len; ++i) {
        uart_send_char(ptr[i]);
    }
    return len;
}

int _read(int file, char *ptr, int len) {
    (void)file; (void)ptr; (void)len;
    return 0;
}

int _close(int file) { (void)file; return -1; }
int _fstat(int file, struct stat *st) { (void)file; st->st_mode = S_IFCHR; return 0; }
int _isatty(int file) { (void)file; return 1; }
int _lseek(int file, int ptr, int dir) { (void)file; (void)ptr; (void)dir; return 0; }
