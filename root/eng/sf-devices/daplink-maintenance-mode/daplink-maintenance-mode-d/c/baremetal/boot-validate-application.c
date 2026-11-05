#include <stdint.h>
#include <stdbool.h>

#define SRAM_BASE_ADDR        0x20000000U
#define SRAM_SIZE_BYTES       (32U * 1024U)
#define FLASH_APP_START_ADDR  0x00008000U
#define FLASH_APP_END_ADDR    0x00020000U
#define FLASH_SECTOR_SIZE     2048U
#define MAINTENANCE_MAGIC     0x544E4941U

typedef enum {
    STATE_INIT,
    STATE_CHECK_TRIGGER,
    STATE_MAINTENANCE_RUN,
    STATE_VERIFY_AND_BOOT
} boot_state_t;

typedef struct {
    uint32_t initial_msp;
    uint32_t reset_handler;
} vector_table_t;

// Зовнішні апаратні функції платформи (BSP)
extern bool bsp_is_button_pressed(void);
extern void bsp_watchdog_feed(void);
extern bool bsp_flash_erase_sector(uint32_t sector_addr);
extern bool bsp_flash_write_block(uint32_t dest_addr, const uint8_t *data, uint32_t len);
extern void bsp_usb_disconnect(void);
extern void bsp_system_reset(void);

// Спільна комірка пам'яті для передачі маркера між застосунком та завантажувачем
static volatile uint32_t shared_boot_flag __attribute__((section(".noinit")));

// Перевірка цілісності векторів застосунку перед передачею керування
bool boot_validate_application(uint32_t app_addr) {
    const vector_table_t *vt = (const vector_table_t *)app_addr;
    if (vt->initial_msp < SRAM_BASE_ADDR || vt->initial_msp > (SRAM_BASE_ADDR + SRAM_SIZE_BYTES)) {
        return false;
    }
    if (vt->reset_handler < app_addr || vt->reset_handler >= FLASH_APP_END_ADDR) {
        return false;
    }
    return (vt->reset_handler & 0x01U) != 0U;
}

// Запис сектора даних LBA з динамічним контролем меж секторів Flash
bool boot_process_lba_write(uint32_t flash_offset, const uint8_t *buffer, uint32_t length) {
    uint32_t target_addr = FLASH_APP_START_ADDR + flash_offset;
    if ((target_addr + length) > FLASH_APP_END_ADDR) {
        return false;
    }
    if ((target_addr % FLASH_SECTOR_SIZE) == 0U) {
        bsp_watchdog_feed();
        if (!bsp_flash_erase_sector(target_addr)) {
            return false;
        }
        bsp_watchdog_feed();
    }
    return bsp_flash_write_block(target_addr, buffer, length);
}

// Деініціалізація периферії та перехід у робочу прошивку
void boot_jump_to_application(uint32_t app_addr) {
    const vector_table_t *vt = (const vector_table_t *)app_addr;
    bsp_usb_disconnect();
    __asm volatile ("cpsid i" : : : "memory");
    
    // Релокація таблиці векторів переривань у регістрі VTOR
    volatile uint32_t *vtor = (volatile uint32_t *)0xE000ED08U;
    *vtor = app_addr;
    
    __asm volatile (
        "msr msp, %0
"
        "bx %1
"
        : : "r" (vt->initial_msp), "r" (vt->reset_handler) : "memory"
    );
}

// Головний диспетчер завантажувача DAPLink
void daplink_bootloader_main(void) {
    boot_state_t state = STATE_INIT;
    bool enter_maintenance = false;

    while (1) {
        bsp_watchdog_feed();
        switch (state) {
            case STATE_INIT:
                state = STATE_CHECK_TRIGGER;
                break;
            case STATE_CHECK_TRIGGER:
                if (bsp_is_button_pressed() || (shared_boot_flag == MAINTENANCE_MAGIC)) {
                    shared_boot_flag = 0U;
                    enter_maintenance = true;
                }
                if (!boot_validate_application(FLASH_APP_START_ADDR)) {
                    enter_maintenance = true;
                }
                state = enter_maintenance ? STATE_MAINTENANCE_RUN : STATE_VERIFY_AND_BOOT;
                break;
            case STATE_MAINTENANCE_RUN:
                // Обробка запитів USB MSC та виклики boot_process_lba_write
                break;
            case STATE_VERIFY_AND_BOOT:
                if (boot_validate_application(FLASH_APP_START_ADDR)) {
                    boot_jump_to_application(FLASH_APP_START_ADDR);
                }
                state = STATE_MAINTENANCE_RUN;
                break;
            default:
                bsp_system_reset();
                break;
        }
    }
}
