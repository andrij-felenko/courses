// Порушення Strict Aliasing (Type Punning через вказівник)
uint32_t swap_bytes_bad(uint32_t val) {
    uint8_t buffer[4];
    // Записуємо як uint32
    *(uint32_t *)buffer = val;

    // Читаємо як байти і міняємо місцями
    uint8_t tmp = buffer[0];
    buffer[0] = buffer[3];
    buffer[3] = tmp;

    // Компілятор у -O2 вважає, що запис у buffer[] не впливає на *(uint32_t*)buffer!
    // Він повертає вихідне значення val, повністю викинувши перестановку байтів!
    return *(uint32_t *)buffer;
}

// Правильний варіант: копіювання через memcpy
#include <string.h>
uint32_t swap_bytes_good(uint32_t val) {
    uint8_t buffer[4];
    memcpy(buffer, &val, 4);
    uint8_t tmp = buffer[0];
    buffer[0] = buffer[3];
    buffer[3] = tmp;
    uint32_t result;
    memcpy(&result, buffer, 4);
    return result; // Компілятор оптимізує memcpy у пряму інструкцію REV!
}
