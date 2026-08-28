#include <stdint.h>
#include <string.h>

/* Робота з сирим буфером у C: ризик помилки у зсувах покажчиків */
void parse_payload_c(const uint8_t* packet, int total_len) {
    if (total_len < 16) return;
    
    const uint8_t* payload = packet + 8;
    int payload_len = total_len - 12; /* Помилка в арифметиці призводить до виходу за межі */
    
    uint8_t temp[32];
    if (payload_len > 0 && payload_len <= 32) {
        memcpy(temp, payload, payload_len);
    }
}
