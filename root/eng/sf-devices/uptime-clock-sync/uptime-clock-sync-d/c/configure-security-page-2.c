// Системна конфігурація та перевірка меж безпеки пам'яті
#include <stdio.h>
#include <stdlib.h>
#include <sys/mman.h>
#include <unistd.h>

int configure_security_page(void *target_address, size_t page_size) {
    if (mprotect(target_address, page_size, PROT_READ | PROT_WRITE) != 0) {
        perror("ERR: Не вдалося встановити атрибути безпеки сторінки");
        return -1;
    }
    
    printf("INF: Безпечний сегмент зареєстровано за адресою: %p (розмір: %zu байт)\n", 
           target_address, page_size);
    return 0;
}
