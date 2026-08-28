typedef struct {
    __IO uint32_t CR;            /* 0x00 */
    __IO uint32_t PLLCFGR;       /* 0x04 */
    __IO uint32_t CFGR;          /* 0x08 */
    __IO uint32_t CIR;           /* 0x0C */
    __IO uint32_t AHB1RSTR;      /* 0x10 */
    __IO uint32_t AHB2RSTR;      /* 0x14 */
    __IO uint32_t AHB3RSTR;      /* 0x18 */
    uint32_t      RESERVED0;     /* 0x1C — зарезервовано */
    __IO uint32_t APB1RSTR;      /* 0x20 */
    __IO uint32_t APB2RSTR;      /* 0x24 */
    uint32_t      RESERVED1[2];  /* 0x28–0x2C — зарезервовано */
    __IO uint32_t AHB1ENR;       /* 0x30 */
    /* … */
} RCC_TypeDef;
