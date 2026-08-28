#include <stdio.h>
#include <stdlib.h>
#include <sys/auxv.h>
#include <errno.h>

void print_system_auxv_info(void) {
    /* Отримання розміру сторінки віртуальної пам'яті */
    unsigned long page_size = getauxval(AT_PAGESZ);
    
    /* Отримання адреси відображення vDSO */
    unsigned long vdso_addr = getauxval(AT_SYSINFO_EHDR);
    
    /* Отримання вказівника на криптографічну ентропію */
    const unsigned char *random_bytes = (const unsigned char *)getauxval(AT_RANDOM);

    printf("Розмір системної сторінки: %lu байтів\n", page_size);
    printf("Віртуальна адреса vDSO:    0x%lx\n", vdso_addr);

    if (random_bytes) {
        printf("Випадкові байти (AT_RANDOM): ");
        for (int i = 0; i < 16; i++) {
            printf("%02x ", random_bytes[i]);
        }
        printf("\n");
    }
}

int main(void) {
    print_system_auxv_info();
    return 0;
}
