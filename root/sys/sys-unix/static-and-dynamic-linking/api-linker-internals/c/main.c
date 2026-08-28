#define _GNU_SOURCE
#include <dlfcn.h>

typedef struct {
    const char *dli_fname; /* Шлях до .so файла або бінарника, що містить адресу */
    void       *dli_fbase; /* Базова адреса завантаження модуля в пам'ять (mmap base) */
    const char *dli_sname; /* Ім'я найближчого символу (функції), що передує адресі */
    void       *dli_saddr; /* Точна віртуальна адреса початку цього символу */
} Dl_info;

int dladdr(const void *addr, Dl_info *info);
