#include <stdint.h>

// байт із RTC у форматі пакованого BCD -> звичайне число 0..99
uint8_t bcd_to_bin(uint8_t bcd) {
    uint8_t hi = bcd >> 4;        // старша тетрада — десятки
    uint8_t lo = bcd & 0x0F;      // молодша тетрада — одиниці
    return hi * 10 + lo;          // складаємо десяткову вагу
}

// приклад: у регістрі секунд лежить 0x49
uint8_t raw = 0x49;              // так чип віддає «сорок дев'ять»
uint8_t sec = bcd_to_bin(raw);   // hi=4, lo=9 -> 4*10 + 9 = 49  ✓
