#include <stdint.h>
#include <stddef.h>
#include "stm32f4xx.h"      /* CMSIS: CRC, RCC, __RBIT */

/* buf має бути вирівняний на 4 і кратний 4 байтам */
uint32_t crc32_zlib_hw(const uint32_t *buf, size_t words)
{
    RCC->AHB1ENR |= RCC_AHB1ENR_CRCEN;   /* без цього блок мовчить */
    CRC->CR = CRC_CR_RESET;              /* DR ← 0xFFFFFFFF */

    for (size_t i = 0; i < words; i++)
        CRC->DR = __RBIT(buf[i]);        /* відбиття входу — руками */

    return __RBIT(CRC->DR) ^ 0xFFFFFFFF; /* відбиття виходу + xorout */
}
