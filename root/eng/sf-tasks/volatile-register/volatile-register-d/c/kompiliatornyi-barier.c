// Класичний компіляторний бар'єр GCC/Clang
#define COMPILER_BARRIER() asm volatile("" ::: "memory")

void send_packet_safe(void) {
    tx_buffer[0] = 0xAA;
    tx_buffer[1] = 0xBB;
    
    COMPILER_BARRIER(); // Компілятор скидає всі збережені змінні в RAM
    
    is_ready = 1;       // Цей запис гарантовано буде в asm після заповнення буфера
}
