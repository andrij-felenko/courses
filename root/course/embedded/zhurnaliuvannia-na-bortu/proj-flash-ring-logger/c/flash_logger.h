/* Кільцевий журнал у SPI NOR Flash: сканування, запис, ротація, вивантаження.
 *
 * Ядро не знає ні про RTOS, ні про переривання, ні про годинник: мітку часу
 * подає викликач, доступ до кристала — три вказівники в flash_hal_t.
 * Динамічної пам'яті немає взагалі — найбільший буфер це один кадр на стеку. */

#ifndef FLASH_LOGGER_H
#define FLASH_LOGGER_H

#include "log_format.h"

typedef enum {
    LOG_OK = 0,
    LOG_ERR_HAL,       /* кристал не відповів або всі сектори дефектні */
    LOG_ERR_TOO_BIG,   /* навантаження не влазить у кадр, або буфер вивантаження малий */
    LOG_ERR_RANGE,     /* індекс сектора поза кільцем */
    LOG_ERR_EMPTY      /* вивантажувати нічого: жодного заповненого сектора */
} log_status_t;

/* Драйвер кристала. ctx передається назад у кожен виклик — так один логер
 * не тягне за собою глобальних змінних і на платі з двома мікросхемами
 * Flash живуть два незалежні журнали. */
typedef struct {
    bool (*read)(uint32_t addr, uint8_t *buf, size_t len, void *ctx);
    bool (*write)(uint32_t addr, const uint8_t *buf, size_t len, void *ctx);
    bool (*erase_sector)(uint32_t sector_addr, void *ctx);
    void *ctx;
} flash_hal_t;

typedef struct {
    flash_hal_t hal;
    uint32_t base_addr;          /* адреса сектора 0 в адресному просторі кристала */
    uint32_t active_sector;      /* голова кільця — сюди пишемо */
    uint32_t write_offset;       /* зсув першого вільного байта в активному секторі */
    uint32_t tail_sector;        /* хвіст кільця — звідси вивантажуємо */
    uint32_t seq_num;            /* найбільший виданий номер послідовності */
    uint32_t bad_mask;           /* бітова маска секторів, які кристал не тримає */
    uint32_t pending_bad;        /* сектор, про який ще треба записати службовий кадр */
    uint32_t last_timestamp_ms;  /* мітка останнього прикладного запису */
    bool     in_service_write;   /* захист від рекурсії службового запису */
} flash_logger_t;

/* Сканує всі сектори, знаходить голову й хвіст, відновлює write_offset після
 * аварійного скидання. Якщо активного сектора немає — відкриває новий. */
log_status_t flash_logger_init(flash_logger_t *logger, const flash_hal_t *hal, uint32_t base_addr);

/* Додає кадр. Сам ротує сектор, коли місця не лишилося, сам обходить
 * дефектні сектори й сам доповідає про них службовим записом. */
log_status_t flash_logger_write(flash_logger_t *logger, log_level_t level, uint8_t module_id,
                                uint32_t timestamp_ms, uint32_t token_id,
                                const uint8_t *payload, uint8_t payload_len);

/* Вичитує найстаріший ЗАПОВНЕНИЙ сектор пачкою — рівно ті байти, що їх
 * радіомодем віддає на сервер. Активний сектор не віддається: він ще росте.
 * out має вміщати FLASH_SECTOR_SIZE байтів. */
log_status_t flash_logger_read_batch(flash_logger_t *logger, uint8_t *out, size_t out_cap,
                                     uint32_t *out_sector, size_t *out_len, uint32_t *out_records);

/* Сервер підтвердив пачку — сектор стає DIRTY, хвіст їде далі. */
log_status_t flash_logger_commit_tail(flash_logger_t *logger, uint32_t sector_idx);

/* Скільки байтів у активному секторі ще вільно (для діагностики й тестів). */
uint32_t flash_logger_free_space(const flash_logger_t *logger);

#endif /* FLASH_LOGGER_H */
