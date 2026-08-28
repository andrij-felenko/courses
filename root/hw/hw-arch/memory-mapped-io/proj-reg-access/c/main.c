#include <stdint.h>
#define REG      (*(volatile uint32_t *)0x40008000u)
#define SET_REG  (*(volatile uint32_t *)0x40008008u)   // write-1-to-set
#define CLR_REG  (*(volatile uint32_t *)0x4000800Cu)   // write-1-to-clear
#define STATUS   (*(volatile uint32_t *)0x40008010u)

// RMW (зручно, але НЕ атомарно):
REG |=  (1u << n);                          // встановити біт
REG &= ~(1u << n);                          // скинути біт
REG ^=  (1u << n);                          // перемкнути біт
REG  = (REG & ~mask) | (val << shift);      // записати поле з кількох бітів

// Атомарно (одним записом, без читання):
SET_REG = (1u << n);                        // встановити біт
CLR_REG = (1u << n);                        // скинути біт

// Скинути прапорець статусу типу write-1-to-clear:
STATUS = (1u << READY);                     // писати ЛИШЕ потрібний біт, не |=
