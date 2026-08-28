#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define BOOT_MAGIC_HEADER      0x424F4F54UL  /* 'BOOT' */
#define BOOT_METADATA_MAGIC    0x4D455441UL  /* 'META' */
#define MAX_BOOT_ATTEMPTS      3

#define FLASH_SLOT_A_BASE      0x08014000UL
#define FLASH_SLOT_B_BASE      0x0808A000UL
#define FLASH_SLOT_SIZE        (470 * 1024UL)

#define SRAM_START_ADDR        0x20000000UL
#define SRAM_END_ADDR          0x20040000UL  /* 256 КБ SRAM */

/* Системні регістри Cortex-M */
#define SCB_VTOR               (*(volatile uint32_t *)0xE000ED08UL)

typedef enum {
    SLOT_A = 0,
    SLOT_B = 1,
    SLOT_NONE = 255
} slot_id_t;

typedef enum {
    SLOT_STATE_EMPTY     = 0xFF,
    SLOT_STATE_TRIAL     = 0xAA,
    SLOT_STATE_CONFIRMED = 0x55,
    SLOT_STATE_FAILED    = 0x00
} slot_state_t;

#pragma pack(push, 1)
typedef struct {
    uint32_t magic;
    uint32_t version;
    uint32_t security_counter;
    uint32_t payload_size;
    uint32_t payload_crc32;
    uint8_t  signature[64];
    uint32_t vector_offset;
    uint8_t  reserved[136];
} image_header_t;

typedef struct {
    uint32_t magic;
    uint32_t sequence;
    struct {
        uint8_t  state;
        uint8_t  boot_attempts;
        uint16_t reserved;
        uint32_t image_version;
        uint32_t security_counter;
    } slot[2];
    uint32_t metadata_crc32;
} boot_metadata_t;
#pragma pack(pop)

/* Програмний розрахунок CRC-32 (IEEE 802.3) */
uint32_t crc32_calculate(const uint8_t *data, size_t length)
{
    uint32_t crc = 0xFFFFFFFFUL;
    for (size_t i = 0; i < length; ++i) {
        crc ^= data[i];
        for (uint8_t j = 0; j < 8; ++j) {
            crc = (crc >> 1) ^ (0xEDB88320UL & (-(crc & 1UL)));
        }
    }
    return ~crc;
}

/* Перевірка цілісності бінарного образу у Flash */
bool bootloader_verify_image(uint32_t slot_base_addr)
{
    const image_header_t *hdr = (const image_header_t *)slot_base_addr;

    if (hdr->magic != BOOT_MAGIC_HEADER) {
        return false;
    }

    if (hdr->payload_size == 0 || hdr->payload_size > (FLASH_SLOT_SIZE - sizeof(image_header_t))) {
        return false;
    }

    const uint8_t *payload = (const uint8_t *)(slot_base_addr + sizeof(image_header_t));
    uint32_t calculated_crc = crc32_calculate(payload, hdr->payload_size);

    if (calculated_crc != hdr->payload_crc32) {
        return false;
    }

    /* Перевірка початкового покажчика стека (мусить лежати в межах SRAM) */
    uint32_t initial_msp = *(const uint32_t *)(slot_base_addr + sizeof(image_header_t));
    if (initial_msp < SRAM_START_ADDR || initial_msp > SRAM_END_ADDR) {
        return false;
    }

    return true;
}

/* Вибір найкращого слота для запуску */
slot_id_t bootloader_select_slot(boot_metadata_t *meta)
{
    slot_id_t candidate = SLOT_NONE;

    /* Спершу перевіряємо, чи є слот у режимі пробного запуску */
    for (int i = 0; i < 2; ++i) {
        if (meta->slot[i].state == SLOT_STATE_TRIAL) {
            uint32_t base = (i == 0) ? FLASH_SLOT_A_BASE : FLASH_SLOT_B_BASE;
            if (meta->slot[i].boot_attempts < MAX_BOOT_ATTEMPTS && bootloader_verify_image(base)) {
                return (slot_id_t)i;
            } else {
                /* Ліміт вичерпано або образ пошкоджено -> бракуємо слот */
                meta->slot[i].state = SLOT_STATE_FAILED;
            }
        }
    }

    /* Якщо пробних немає, шукаємо перевірений (CONFIRMED) із найновішою версією */
    uint32_t highest_version = 0;
    for (int i = 0; i < 2; ++i) {
        if (meta->slot[i].state == SLOT_STATE_CONFIRMED) {
            uint32_t base = (i == 0) ? FLASH_SLOT_A_BASE : FLASH_SLOT_B_BASE;
            if (bootloader_verify_image(base)) {
                if (candidate == SLOT_NONE || meta->slot[i].image_version >= highest_version) {
                    highest_version = meta->slot[i].image_version;
                    candidate = (slot_id_t)i;
                }
            } else {
                meta->slot[i].state = SLOT_STATE_FAILED;
            }
        }
    }

    return candidate;
}

typedef void (*app_entry_t)(void);

/* Безпечний перехід у застосунок */
void bootloader_jump_to_app(uint32_t slot_base_addr)
{
    uint32_t app_vector_table = slot_base_addr + sizeof(image_header_t);
    uint32_t initial_msp = *(volatile uint32_t *)(app_vector_table);
    uint32_t reset_handler_addr = *(volatile uint32_t *)(app_vector_table + 4);

    /* 1. Вимикаємо всі переривання процесора */
    __asm volatile ("cpsid i" : : : "memory");

    /* 2. Переносимо векторну таблицю */
    SCB_VTOR = app_vector_table;

    /* 3. Встановлюємо покажчик основного стека (MSP) */
    __asm volatile ("msr msp, %0" : : "r" (initial_msp) : "memory");

    /* 4. Бар'єр пам'яті */
    __asm volatile ("dsb" : : : "memory");
    __asm volatile ("isb" : : : "memory");

    /* 5. Стрибок у Reset_Handler застосунку */
    app_entry_t app_entry = (app_entry_t)reset_handler_addr;
    app_entry();

    /* Запобіжник: сюди процесор ніколи не повинен дійти */
    while (1) { }
}
