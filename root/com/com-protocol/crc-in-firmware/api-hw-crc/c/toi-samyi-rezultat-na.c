#include <stdint.h>
#include <stddef.h>
#include "stm32l4xx.h"

uint32_t crc32_zlib_hw_bytes(const uint8_t *buf, size_t len)
{
    RCC->AHB1ENR |= RCC_AHB1ENR_CRCEN;

    CRC->POL  = 0x04C11DB7;                 /* нормальний запис полінома */
    CRC->INIT = 0xFFFFFFFF;
    CRC->CR   = (0u << CRC_CR_POLYSIZE_Pos)  /* 00 = 32 біти            */
              | (1u << CRC_CR_REV_IN_Pos)    /* 01 = відбиття по байту  */
              | CRC_CR_REV_OUT               /* відбиття результату     */
              | CRC_CR_RESET;                /* DR ← INIT               */

    for (size_t i = 0; i < len; i++)
        *(volatile uint8_t *)&CRC->DR = buf[i];   /* саме STRB! */

    return CRC->DR ^ 0xFFFFFFFF;
}
