#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <assert.h>

#define SMBUS_CRC8_POLYNOMIAL 0x07

static uint8_t smbus_crc8_lut[256];
static bool lut_initialized = false;

/* Генерація таблиці пошуку 256 байтів для полінома x^8 + x^2 + x + 1 */
void smbus_crc8_init_table(void) {
    for (int i = 0; i < 256; ++i) {
        uint8_t curr = (uint8_t)i;
        for (int bit = 0; bit < 8; ++bit) {
            if (curr & 0x80) {
                curr = (uint8_t)((curr << 1) ^ SMBUS_CRC8_POLYNOMIAL);
            } else {
                curr = (uint8_t)(curr << 1);
            }
        }
        smbus_crc8_lut[i] = curr;
    }
    lut_initialized = true;
}

/* Оновлення біжучого залишку CRC-8 одним байтом */
uint8_t smbus_crc8_update(uint8_t crc, uint8_t data) {
    if (!lut_initialized) {
        smbus_crc8_init_table();
    }
    return smbus_crc8_lut[crc ^ data];
}

/* Обчислення PEC для масиву байтів довільної довжини */
uint8_t smbus_crc8_block(uint8_t initial_crc, const uint8_t *data, size_t len) {
    uint8_t crc = initial_crc;
    for (size_t i = 0; i < len; ++i) {
        crc = smbus_crc8_update(crc, data[i]);
    }
    return crc;
}

/* Розрахунок PEC для транзакції Write Word:
   Потік: [SlaveAddr | Wr] -> [Command] -> [DataLow] -> [DataHigh] */
uint8_t smbus_calc_write_word_pec(uint8_t slave_addr_7bit, uint8_t cmd, uint16_t word_val) {
    uint8_t addr_wr = (uint8_t)(slave_addr_7bit << 1); // R/W = 0 (Write)
    uint8_t data_low = (uint8_t)(word_val & 0xFF);
    uint8_t data_high = (uint8_t)((word_val >> 8) & 0xFF);

    uint8_t crc = 0x00;
    crc = smbus_crc8_update(crc, addr_wr);
    crc = smbus_crc8_update(crc, cmd);
    crc = smbus_crc8_update(crc, data_low);
    crc = smbus_crc8_update(crc, data_high);
    return crc;
}

/* Перевірка цілісності транзакції Read Word:
   Потік: [SlaveAddr | Wr] -> [Command] -> [SlaveAddr | Rd] -> [DataLow] -> [DataHigh] */
bool smbus_verify_read_word_pec(uint8_t slave_addr_7bit, uint8_t cmd,
                                uint8_t data_low, uint8_t data_high, uint8_t rx_pec) {
    uint8_t addr_wr = (uint8_t)(slave_addr_7bit << 1);          // R/W = 0
    uint8_t addr_rd = (uint8_t)((slave_addr_7bit << 1) | 0x01); // R/W = 1

    uint8_t crc = 0x00;
    crc = smbus_crc8_update(crc, addr_wr);
    crc = smbus_crc8_update(crc, cmd);
    crc = smbus_crc8_update(crc, addr_rd);
    crc = smbus_crc8_update(crc, data_low);
    crc = smbus_crc8_update(crc, data_high);

    return (crc == rx_pec);
}

/* Розрахунок PEC для транзакції Block Write:
   Потік: [SlaveAddr | Wr] -> [Command] -> [Byte Count N] -> [Data 1 .. N] */
uint8_t smbus_calc_block_write_pec(uint8_t slave_addr_7bit, uint8_t cmd,
                                   const uint8_t *data, uint8_t length) {
    uint8_t addr_wr = (uint8_t)(slave_addr_7bit << 1);
    uint8_t crc = 0x00;
    crc = smbus_crc8_update(crc, addr_wr);
    crc = smbus_crc8_update(crc, cmd);
    crc = smbus_crc8_update(crc, length);
    for (uint8_t i = 0; i < length; ++i) {
        crc = smbus_crc8_update(crc, data[i]);
    }
    return crc;
}

/* Логіка обробки прийому кадру Write Word веденим пристроєм */
bool smbus_slave_process_write_word(uint8_t slave_addr_7bit, uint8_t cmd,
                                    uint8_t low, uint8_t high, uint8_t rx_pec,
                                    uint16_t *out_valid_word) {
    uint8_t expected_pec = smbus_calc_write_word_pec(slave_addr_7bit, cmd,
                                                     (uint16_t)((high << 8) | low));
    if (expected_pec != rx_pec) {
        return false; // Відкинути пошкоджені дані
    }
    if (out_valid_word != NULL) {
        *out_valid_word = (uint16_t)((high << 8) | low);
    }
    return true; // Дані верифіковано успішно
}

/* Автоматизований тест алгоритму */
bool smbus_pec_run_selftest(void) {
    /* Стандартний тестовий вектор: рядок "123456789" -> 0xF4 */
    const uint8_t test_vector[] = {0x31, 0x32, 0x33, 0x34, 0x35, 0x36, 0x37, 0x38, 0x39};
    uint8_t crc = smbus_crc8_block(0x00, test_vector, sizeof(test_vector));
    if (crc != 0xF4) {
        return false;
    }

    /* Тест Write Word: Адреса 0x16 (0x2C на шині), Команда 0x09 (Voltage), Значення 0x0FA0 (4000 мВ) */
    uint8_t pec = smbus_calc_write_word_pec(0x16, 0x09, 0x0FA0);
    /* Спотворення одного біта в даних мусить гарантовано змінити PEC */
    uint8_t corrupted_pec = smbus_calc_write_word_pec(0x16, 0x09, 0x0FA1);
    if (pec == corrupted_pec) {
        return false;
    }

    uint16_t received_val = 0;
    if (!smbus_slave_process_write_word(0x16, 0x09, 0xA0, 0x0F, pec, &received_val)) {
        return false;
    }
    if (received_val != 0x0FA0) {
        return false;
    }

    return true;
}
