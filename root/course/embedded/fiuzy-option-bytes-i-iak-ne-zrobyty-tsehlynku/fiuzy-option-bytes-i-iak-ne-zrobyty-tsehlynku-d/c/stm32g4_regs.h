#ifndef STM32G4_REGS_H
#define STM32G4_REGS_H

#include <stdint.h>

/*
 * Мінімальна карта регістрів STM32G4 (RM0440) — рівно ті блоки, яких торкається
 * робота з Option Bytes. Повний CMSIS-заголовок сховав би за тисячами рядків
 * саме те, що тут важливо бачити: за якими адресами читаються конфігураційні
 * біти й куди йде запис, після якого чип уже може не повернутися.
 */

/* --- контролер вбудованої Flash --- */
typedef struct {
    volatile uint32_t ACR;       /* 0x00  затримки читання */
    volatile uint32_t PDKEYR;    /* 0x04  ключі режиму power-down */
    volatile uint32_t KEYR;      /* 0x08  ключі розблокування CR */
    volatile uint32_t OPTKEYR;   /* 0x0C  ключі розблокування Option Bytes */
    volatile uint32_t SR;        /* 0x10  стан і прапорці помилок */
    volatile uint32_t CR;        /* 0x14  керування */
    volatile uint32_t ECCR;      /* 0x18  корекція помилок */
    volatile uint32_t RESERVED0; /* 0x1C */
    volatile uint32_t OPTR;      /* 0x20  тіньова копія Option Bytes */
} flash_regs_t;

#define FLASH  ((flash_regs_t *)0x40022000UL)

/* Магічні константи розблокування. Порядок запису критичний: помилка в
   послідовності блокує контролер Flash до наступного скидання чипа. */
#define FLASH_KEY1     0x45670123UL
#define FLASH_KEY2     0xCDEF89ABUL
#define FLASH_OPTKEY1  0x08192A3BUL
#define FLASH_OPTKEY2  0x4C5D6E7FUL

/* FLASH_SR */
#define FLASH_SR_EOP      (1UL << 0)
#define FLASH_SR_OPERR    (1UL << 1)
#define FLASH_SR_PROGERR  (1UL << 3)
#define FLASH_SR_WRPERR   (1UL << 4)
#define FLASH_SR_PGAERR   (1UL << 5)
#define FLASH_SR_SIZERR   (1UL << 6)
#define FLASH_SR_PGSERR   (1UL << 7)
#define FLASH_SR_MISERR   (1UL << 8)
#define FLASH_SR_FASTERR  (1UL << 9)
#define FLASH_SR_OPTVERR  (1UL << 15)  /* Option Bytes не пройшли перевірку при завантаженні */
#define FLASH_SR_BSY      (1UL << 16)

#define FLASH_SR_ERRORS  (FLASH_SR_OPERR   | FLASH_SR_PROGERR | FLASH_SR_WRPERR  | \
                          FLASH_SR_PGAERR  | FLASH_SR_SIZERR  | FLASH_SR_PGSERR  | \
                          FLASH_SR_MISERR  | FLASH_SR_FASTERR | FLASH_SR_OPTVERR)

/* FLASH_CR */
#define FLASH_CR_OPTSTRT     (1UL << 17)
#define FLASH_CR_OBL_LAUNCH  (1UL << 27)
#define FLASH_CR_OPTLOCK     (1UL << 30)
#define FLASH_CR_LOCK        (1UL << 31)

/* FLASH_OPTR: розкладка полів, які нас цікавлять */
#define FLASH_OPTR_RDP_MSK   0x000000FFUL
#define FLASH_OPTR_BOR_POS   8
#define FLASH_OPTR_BOR_MSK   (0x7UL << FLASH_OPTR_BOR_POS)
#define FLASH_OPTR_IWDG_SW   (1UL << 16)   /* 1 = програмний старт, 0 = апаратний */
#define FLASH_OPTR_NSWBOOT0  (1UL << 26)   /* 1 = BOOT0 береться з ніжки */
#define FLASH_OPTR_NBOOT0    (1UL << 27)   /* значення BOOT0, коли ніжка вимкнена */
#define FLASH_OPTR_NRST_POS  28
#define FLASH_OPTR_NRST_MSK  (0x3UL << FLASH_OPTR_NRST_POS)

/* --- блок керування живленням: детектор просідання PVD --- */
typedef struct {
    volatile uint32_t CR1;  /* 0x00 */
    volatile uint32_t CR2;  /* 0x04  PVDE, PVDLS */
    volatile uint32_t CR3;  /* 0x08 */
    volatile uint32_t CR4;  /* 0x0C */
    volatile uint32_t SR1;  /* 0x10 */
    volatile uint32_t SR2;  /* 0x14  PVDO */
} pwr_regs_t;

#define PWR  ((pwr_regs_t *)0x40007000UL)

#define PWR_CR2_PVDE       (1UL << 0)
#define PWR_CR2_PVDLS_POS  1
#define PWR_CR2_PVDLS_MSK  (0x7UL << PWR_CR2_PVDLS_POS)
#define PWR_SR2_PVDO       (1UL << 11)  /* 1 = VDD НИЖЧЕ обраного порога */

/* --- тактування периферії --- */
#define RCC_APB1ENR1        (*(volatile uint32_t *)(0x40021000UL + 0x58))
#define RCC_APB1ENR1_PWREN  (1UL << 28)

/* --- ITM: діагностика, яка живе, поки живий налагоджувач --- */
#define CORE_DEMCR         (*(volatile uint32_t *)0xE000EDFCUL)
#define CORE_DEMCR_TRCENA  (1UL << 24)
#define ITM_STIM0_U32      (*(volatile uint32_t *)0xE0000000UL)
#define ITM_STIM0_U8       (*(volatile uint8_t  *)0xE0000000UL)
#define ITM_TER            (*(volatile uint32_t *)0xE0000E00UL)

#endif /* STM32G4_REGS_H */
