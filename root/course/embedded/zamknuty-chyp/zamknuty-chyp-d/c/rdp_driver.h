// rdp_driver.h — Драйвер апаратного захисту Option Bytes (C99 / C11)
#ifndef RDP_DRIVER_H
#define RDP_DRIVER_H

#include <stdint.h>
#include <stdbool.h>

// Магічні ключі авторизації для доступу до Option Bytes
#define FLASH_OPTKEY1         0x08192A3BU
#define FLASH_OPTKEY2         0x4C5D6E7FU

// Базові адреси та регістри Flash Controller
#define FLASH_BASE_ADDR       0x40023C00U
#define FLASH_OPTKEYR_REG     (*(volatile uint32_t *)(FLASH_BASE_ADDR + 0x08U))
#define FLASH_SR_REG          (*(volatile uint32_t *)(FLASH_BASE_ADDR + 0x0CU))
#define FLASH_CR_REG          (*(volatile uint32_t *)(FLASH_BASE_ADDR + 0x10U))
#define FLASH_OPTCR_REG       (*(volatile uint32_t *)(FLASH_BASE_ADDR + 0x14U))

// Бітові маски стану контролера Flash
#define FLASH_SR_BSY_BIT      (1U << 16)

// Бітові маски регістра керування FLASH_OPTCR
#define FLASH_OPTCR_OPTLOCK   (1U << 0)
#define FLASH_OPTCR_OPTSTRT   (1U << 1)
#define FLASH_OPTCR_BOR_LEV_3 (0U << 2) // Найвищий поріг скидання за напругою (2.7 В)
#define FLASH_OPTCR_RDP_POS   8U
#define FLASH_OPTCR_RDP_MASK  (0xFFU << FLASH_OPTCR_RDP_POS)

// Константи рівнів захисту RDP
typedef enum {
    RDP_LEVEL_0 = 0xAAU, // Відкрито для налагодження
    RDP_LEVEL_1 = 0x55U, // Захист Flash (відкат виконує Mass Erase)
    RDP_LEVEL_2 = 0xCCU  // Незворотне апаратне блокування кристала
} rdp_level_t;

typedef enum {
    RDP_STATUS_OK = 0,
    RDP_STATUS_BUSY,
    RDP_STATUS_UNLOCK_FAILED,
    RDP_STATUS_VERIFY_ERROR,
    RDP_STATUS_ALREADY_LOCKED
} rdp_status_t;

// Інтерфейс драйвера
rdp_status_t rdp_get_level(rdp_level_t *out_level);
rdp_status_t rdp_set_level(rdp_level_t target_level);
bool rdp_is_hardened(void);

#endif // RDP_DRIVER_H
