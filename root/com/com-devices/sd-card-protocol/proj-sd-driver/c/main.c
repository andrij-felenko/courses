#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

// Типи статусів та кодів помилок драйвера SD
typedef enum {
    SD_OK = 0,
    SD_ERR_TIMEOUT,
    SD_ERR_CRC,
    SD_ERR_UNSUPPORTED_CARD,
    SD_ERR_BAD_RESPONSE,
    SD_ERR_WRITE_FAILED
} sd_status_t;

// Структура дескриптора карти пам'яті
typedef struct {
    uint16_t rca;          // Відносна адреса карти (RCA)
    bool is_sdhc;          // Прапорець: true = SDHC/SDXC (блокова адреса), false = SDSC
    bool is_4bit_mode;     // Прапорець активації 4-бітної шини DAT0..DAT3
} sd_card_t;

// Апаратні заглушки низькорівневого рівня (HAL)
extern void hal_sd_set_clock_freq(uint32_t freq_hz);
extern void hal_sd_send_cmd_raw(uint8_t cmd, uint32_t arg, uint8_t crc7);
extern bool hal_sd_wait_response_r1(uint32_t *response, uint32_t timeout_ms);
extern bool hal_sd_wait_response_r2(uint8_t cid_csd_out[16], uint32_t timeout_ms);
extern bool hal_sd_wait_response_r3_r7(uint32_t *response, uint32_t timeout_ms);
extern bool hal_sd_wait_response_r6(uint16_t *rca_out, uint32_t timeout_ms);
extern void hal_sd_set_bus_width_4bit(bool enable);
extern bool hal_sd_read_dat_payload(uint8_t *buffer, size_t len_bytes);
extern bool hal_sd_write_dat_payload(const uint8_t *buffer, size_t len_bytes);
extern bool hal_sd_is_dat0_busy(void);
extern void hal_sd_delay_ms(uint32_t ms);

// Розрахунок 7-бітного CRC7 для команди
static uint8_t sd_calc_crc7(const uint8_t *data, size_t len) {
    uint8_t crc = 0;
    for (size_t i = 0; i < len; ++i) {
        uint8_t byte = data[i];
        for (int bit = 0; bit < 8; ++bit) {
            crc <<= 1;
            if ((byte ^ crc) & 0x80) {
                crc ^= 0x09;
            }
            byte <<= 1;
        }
    }
    return (crc & 0x7F);
}

// Допоміжна функція надсилання 48-бітної команди
static void sd_send_command(uint8_t cmd, uint32_t arg) {
    uint8_t frame[5];
    frame[0] = 0x40 | (cmd & 0x3F);
    frame[1] = (uint8_t)(arg >> 24);
    frame[2] = (uint8_t)(arg >> 16);
    frame[3] = (uint8_t)(arg >> 8);
    frame[4] = (uint8_t)(arg);
    uint8_t crc7 = sd_calc_crc7(frame, 5);
    hal_sd_send_cmd_raw(cmd, arg, (uint8_t)((crc7 << 1) | 0x01));
}

// Ініціалізація карти пам'яті
sd_status_t sd_init(sd_card_t *card) {
    uint32_t resp;
    uint8_t cid[16];

    card->rca = 0;
    card->is_sdhc = false;
    card->is_4bit_mode = false;

    // 1. Подача 74+ тактів на частоті 400 кГц
    hal_sd_set_clock_freq(400000);
    hal_sd_delay_ms(10);

    // 2. CMD0: Скидання автомата в стан Idle
    sd_send_command(0, 0x00000000);
    hal_sd_delay_ms(2);

    // 3. CMD8: Перевірка інтерфейсу (VHS = 2.7–3.6В, Check pattern = 0xAA)
    sd_send_command(8, 0x000001AA);
    if (!hal_sd_wait_response_r3_r7(&resp, 100)) {
        return SD_ERR_UNSUPPORTED_CARD; // Карта SD v1.x або MMC не підтримується
    }
    if ((resp & 0xFF) != 0xAA) {
        return SD_ERR_BAD_RESPONSE;     // Неспівпадіння тестового шаблону
    }

    // 4. Цикл опитування ACMD41 з бітом HCS (Host Capacity Support)
    uint32_t timeout_ms = 1000;
    bool ready = false;
    while (timeout_ms > 0) {
        // CMD55: Префікс команд додатків
        sd_send_command(55, 0x00000000);
        if (!hal_sd_wait_response_r1(&resp, 50)) {
            return SD_ERR_TIMEOUT;
        }

        // ACMD41: Запит робочих умов (HCS = 1, VDD = 2.7–3.6В)
        sd_send_command(41, 0x40FF8000);
        if (!hal_sd_wait_response_r3_r7(&resp, 50)) {
            return SD_ERR_TIMEOUT;
        }

        // Перевірка біта Busy (біт 31)
        if (resp & (1UL << 31)) {
            ready = true;
            // Перевірка біта CCS (біт 30): 1 = SDHC/SDXC, 0 = SDSC
            card->is_sdhc = (resp & (1UL << 30)) != 0;
            break;
        }

        hal_sd_delay_ms(10);
        timeout_ms -= (timeout_ms > 10) ? 10 : timeout_ms;
    }

    if (!ready) {
        return SD_ERR_TIMEOUT;
    }

    // 5. CMD2: Зчитування ідентифікатора CID
    sd_send_command(2, 0x00000000);
    if (!hal_sd_wait_response_r2(cid, 100)) {
        return SD_ERR_TIMEOUT;
    }

    // 6. CMD3: Публікація відносної адреси RCA
    sd_send_command(3, 0x00000000);
    if (!hal_sd_wait_response_r6(&card->rca, 100)) {
        return SD_ERR_TIMEOUT;
    }

    // 7. CMD7: Вибір карти за адресою RCA (перехід у Transfer State)
    sd_send_command(7, ((uint32_t)card->rca) << 16);
    if (!hal_sd_wait_response_r1(&resp, 100)) {
        return SD_ERR_TIMEOUT;
    }

    // 8. Підвищення частоти шини до 25 МГц
    hal_sd_set_clock_freq(25000000);

    // 9. ACMD6: Перемикання в 4-бітний режим DAT0..DAT3
    sd_send_command(55, ((uint32_t)card->rca) << 16);
    if (hal_sd_wait_response_r1(&resp, 50)) {
        sd_send_command(6, 0x00000002); // 0x02 = 4-бітний режим
        if (hal_sd_wait_response_r1(&resp, 50)) {
            hal_sd_set_bus_width_4bit(true);
            card->is_4bit_mode = true;
        }
    }

    return SD_OK;
}

// Зчитування одиночного блоку 512 байтів
sd_status_t sd_read_block(const sd_card_t *card, uint32_t block_addr, uint8_t buffer_out[512]) {
    uint32_t arg = card->is_sdhc ? block_addr : (block_addr * 512);
    uint32_t resp;

    // CMD17: Читання одиночного блоку
    sd_send_command(17, arg);
    if (!hal_sd_wait_response_r1(&resp, 100)) {
        return SD_ERR_TIMEOUT;
    }
    if (resp & 0xFFD98008) { // Перевірка прапорців помилок у Card Status
        return SD_ERR_BAD_RESPONSE;
    }

    // Прийом корисного навантаження по лініях DAT
    if (!hal_sd_read_dat_payload(buffer_out, 512)) {
        return SD_ERR_CRC;
    }

    return SD_OK;
}

// Запис одиночного блоку 512 байтів
sd_status_t sd_write_block(const sd_card_t *card, uint32_t block_addr, const uint8_t buffer_in[512]) {
    uint32_t arg = card->is_sdhc ? block_addr : (block_addr * 512);
    uint32_t resp;

    // CMD24: Запис одиночного блоку
    sd_send_command(24, arg);
    if (!hal_sd_wait_response_r1(&resp, 100)) {
        return SD_ERR_TIMEOUT;
    }
    if (resp & 0xFFD98008) {
        return SD_ERR_BAD_RESPONSE;
    }

    // Передача даних по лініях DAT
    if (!hal_sd_write_dat_payload(buffer_in, 512)) {
        return SD_ERR_WRITE_FAILED;
    }

    // Очікування завершення внутрішнього циклу програмування Flash (Busy на DAT0)
    uint32_t busy_timeout = 500; // До 500 мс на операцію запису Flash
    while (hal_sd_is_dat0_busy() && busy_timeout > 0) {
        hal_sd_delay_ms(1);
        busy_timeout--;
    }

    if (busy_timeout == 0) {
        return SD_ERR_TIMEOUT;
    }

    return SD_OK;
}
