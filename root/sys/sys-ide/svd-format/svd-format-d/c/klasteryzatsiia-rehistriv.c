typedef struct {
    __IO uint32_t CCR;    /* Offset 0x00 */
    __IO uint32_t CNDTR;  /* Offset 0x04 */
    __IO uint32_t CPAR;   /* Offset 0x08 */
    __IO uint32_t CMAR;   /* Offset 0x0C */
    uint32_t      RESERVED; /* Offset 0x10 padding to 0x14 stride */
} DMA_Channel_TypeDef;

typedef struct {
    __IO uint32_t       ISR;   /* Offset 0x00 */
    __IO uint32_t       IFCR;  /* Offset 0x04 */
    DMA_Channel_TypeDef CH[8]; /* Offset 0x08 .. 0xA7 */
} DMA_TypeDef;
