/*
 * Верхній шар: обробник SCSI WRITE (10) стека TinyUSB і порт Flash для RP2040.
 * Саме тут вирішується, що відповісти хосту, — і саме тут ховається найгрубіша
 * помилка завантажувача: сказати «збій носія» на службовий сектор файлової системи.
 */
#include "uf2_session.h"

#include "tusb.h"
#include "RP2040.h"            /* CMSIS кристала: NVIC_SystemReset() */
#include "hardware/flash.h"    /* flash_range_erase / flash_range_program */
#include "hardware/sync.h"     /* save_and_disable_interrupts */
#include "hardware/regs/addressmap.h" /* XIP_BASE */
#include "pico/time.h"

#include <string.h>

#define UF2_FAMILY_RP2040 0xE48BFF56UL /* значення з uf2families.json */

#define APP_FLASH_START (XIP_BASE + 256u * 1024u) /* перші 256 КіБ — сам завантажувач */
#define APP_FLASH_SIZE  (1792u * 1024u)

/* Пауза, щоб USB-стек устиг віддати хосту статус останнього запису. */
#define REBOOT_DELAY_US 50000ull

static uf2_session_t s_session;
static uint64_t      s_reboot_at_us; /* 0 — перезавантаження не заплановане */

void uf2_msc_init(void)
{
    uf2_session_init(&s_session, UF2_FAMILY_RP2040, APP_FLASH_START, APP_FLASH_SIZE);
    s_reboot_at_us = 0;
}

/* Порт Flash: pico-sdk працює зі зсувами від XIP_BASE, а не з абсолютними адресами. */
bool uf2_flash_erase_sector(uint32_t address)
{
    uint32_t offset = address - XIP_BASE;
    uint32_t saved  = save_and_disable_interrupts();
    flash_range_erase(offset, UF2_FLASH_SECTOR_SIZE);
    restore_interrupts(saved);
    return true;
}

bool uf2_flash_program(uint32_t address, const uint8_t *data, uint32_t length)
{
    /*
     * Програмувати можна лише цілими сторінками по 256 байтів, тому короткий
     * хвіст образу доводимо нулями у власному буфері: у стертій Flash і так
     * скрізь 0xFF, а нулі просто не змінять нічого поза корисними байтами.
     */
    static uint8_t page[FLASH_PAGE_SIZE];
    if (length > FLASH_PAGE_SIZE || (address % FLASH_PAGE_SIZE) != 0) {
        return false;
    }
    memset(page, 0xFF, sizeof(page));
    memcpy(page, data, length);

    uint32_t offset = address - XIP_BASE;
    uint32_t saved  = save_and_disable_interrupts();
    flash_range_program(offset, page, FLASH_PAGE_SIZE);
    restore_interrupts(saved);
    return true;
}

/* Хост записує; емульований диск завжди приймає запис. */
bool tud_msc_is_writable_cb(uint8_t lun)
{
    (void)lun;
    return true;
}

/*
 * Callback стека: lba — номер логічного сектора, buffer — його вміст.
 * Повертається кількість прийнятих байтів; від'ємне значення означає
 * CHECK CONDITION, тобто «носій зламався» на боці хоста.
 */
int32_t tud_msc_write10_cb(uint8_t lun, uint32_t lba, uint32_t offset,
                           uint8_t *buffer, uint32_t bufsize)
{
    (void)lun;
    (void)lba;

    /*
     * CFG_TUD_MSC_EP_BUFSIZE у цьому проєкті = 512, тож сектор приходить цілим.
     * Якщо стек усе ж розрізав його на частини — мовчки приймаємо байти:
     * зібрати їх ніде, а помилку хосту віддавати не можна.
     */
    if (offset != 0 || bufsize < UF2_BLOCK_SIZE) {
        return (int32_t)bufsize;
    }

    uf2_status_t st = uf2_session_accept_sector(&s_session, buffer, bufsize);

    if (uf2_is_foreign_sector(st)) {
        /*
         * Це не блок UF2, а запис каталогу, таблиці FAT чи .DS_Store.
         * Кажемо GOOD і нічого не робимо: CHECK CONDITION тут перерве
         * копіювання файлу й покаже користувачу «диск пошкоджено».
         */
        return (int32_t)bufsize;
    }

    if (st != UF2_OK && st != UF2_SKIPPED) {
        /*
         * А це вже справжня біда: чуже сімейство, адреса поза межами,
         * збій Flash. Тут мовчати не можна — хай копіювання зупиниться.
         */
        TU_LOG1("UF2: %s\r\n", uf2_status_str(st));
        tud_msc_set_sense(lun, SCSI_SENSE_MEDIUM_ERROR, 0x03, 0x00);
        return -1;
    }

    if (uf2_session_complete(&s_session) && s_reboot_at_us == 0) {
        s_reboot_at_us = time_us_64() + REBOOT_DELAY_US;
    }
    return (int32_t)bufsize;
}

/*
 * Викликається з головного циклу поруч із tud_task(). Перезавантаження
 * робиться саме тут, а не всередині callback: скинути ядро до того, як стек
 * віддав хосту CSW останнього запису, — це «пристрій зник» і помилка копіювання.
 */
void uf2_msc_task(void)
{
    if (s_reboot_at_us == 0 || time_us_64() < s_reboot_at_us) {
        return;
    }
    tud_disconnect(); /* коректний USB disconnect, щоб хост прибрав том */
    sleep_ms(10);
    NVIC_SystemReset();
}
