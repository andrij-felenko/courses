#include <stddef.h>
#include <stdint.h>

#define __IO volatile
#define __I  volatile const
#define __O  volatile

typedef struct {
    __IO uint32_t CR1;       /* Offset 0x00 */
    __IO uint32_t CR2;       /* Offset 0x04 */
    uint8_t       RESERVED0[8]; /* Offset 0x08..0x0F */
    __IO uint32_t SR;        /* Offset 0x10 */
    __IO uint32_t DR;        /* Offset 0x14 */
} SPI_TypeDef;

/* Статична валідація розмітки пам'яті компілятором */
_Static_assert(offsetof(SPI_TypeDef, CR1) == 0x00, "SPI CR1 offset mismatch!");
_Static_assert(offsetof(SPI_TypeDef, CR2) == 0x04, "SPI CR2 offset mismatch!");
_Static_assert(offsetof(SPI_TypeDef, SR)  == 0x10, "SPI SR offset mismatch!");
_Static_assert(offsetof(SPI_TypeDef, DR)  == 0x14, "SPI DR offset mismatch!");
_Static_assert(sizeof(SPI_TypeDef)        == 0x18, "SPI struct size mismatch!");
