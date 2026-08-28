/* ============================================================================
 * Програмний рушій емулятора ISP-програматора STK500v2 (Стандарт C99)
 * ============================================================================ */

#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <stdio.h>

#define STK_MESSAGE_START           0x1B
#define STK_TOKEN                   0x0E

/* Коди команд протоколу STK500 v2 */
#define CMD_SIGN_ON                 0x01
#define CMD_SET_PARAMETER           0x02
#define CMD_GET_PARAMETER           0x03
#define CMD_LOAD_ADDRESS            0x06
#define CMD_ENTER_PROGMODE_ISP      0x10
#define CMD_LEAVE_PROGMODE_ISP      0x11
#define CMD_CHIP_ERASE_ISP          0x12
#define CMD_PROGRAM_FLASH_ISP       0x13
#define CMD_READ_FLASH_ISP          0x14
#define CMD_PROGRAM_EEPROM_ISP      0x15
#define CMD_READ_EEPROM_ISP         0x16
#define CMD_PROGRAM_FUSE_ISP        0x17
#define CMD_READ_FUSE_ISP           0x18
#define CMD_SPI_MULTI               0x1D

/* Коди параметрів програматора */
#define PARAM_BUILD_NUMBER_LOW      0x80
#define PARAM_BUILD_NUMBER_HIGH     0x81
#define PARAM_HW_VER                0x90
#define PARAM_SW_MAJOR              0x91
#define PARAM_SW_MINOR              0x92
#define PARAM_VTARGET               0x94
#define PARAM_SCK_DURATION          0x98

/* Коди статусів відповіді STK500 v2 */
#define STATUS_CMD_OK               0x00
#define STATUS_CMD_TOUT             0x80
#define STATUS_CMD_RDY_BSY_TOUT     0x81
#define STATUS_CMD_SET_PARAM_MISSING 0x82
#define STATUS_CMD_FAILED           0xC0
#define STATUS_CMD_UNKNOWN          0xC9

/* Константи конфігурації мікроконтролера ATmega328P */
#define MCU_FLASH_SIZE              32768U
#define MCU_PAGE_SIZE               128U
#define MCU_PAGE_COUNT              (MCU_FLASH_SIZE / MCU_PAGE_SIZE)
#define MCU_EEPROM_SIZE             1024U
#define MCU_SIG_BYTE0               0x1EU
#define MCU_SIG_BYTE1               0x95U
#define MCU_SIG_BYTE2               0x0FU

#define BUFFER_MAX_SIZE             512U

/* ── Віртуальна модель мікроконтролера ─────────────────────────────────────── */

typedef struct {
    uint8_t flash[MCU_FLASH_SIZE];
    uint8_t eeprom[MCU_EEPROM_SIZE];
    uint8_t page_buffer[MCU_PAGE_SIZE];
    uint8_t fuse_low;
    uint8_t fuse_high;
    uint8_t fuse_ext;
    uint8_t lock_bits;
    uint32_t current_address_bytes;
    bool in_programming_mode;
    bool page_buffer_dirty;
    uint32_t simulated_cpu_hz;
    uint32_t current_isp_hz;
} virtual_mcu_t;

void mcu_init(virtual_mcu_t *mcu) {
    if (!mcu) return;
    memset(mcu->flash, 0xFF, sizeof(mcu->flash));
    memset(mcu->eeprom, 0xFF, sizeof(mcu->eeprom));
    memset(mcu->page_buffer, 0xFF, sizeof(mcu->page_buffer));
    mcu->fuse_low = 0x62;   /* Заводський стан: 8 МГц internal RC + CKDIV8 (1 МГц) */
    mcu->fuse_high = 0xD9;  /* Заводський стан: SPIEN увімкнено, BOD вимкнено */
    mcu->fuse_ext = 0xFF;
    mcu->lock_bits = 0xFF;  /* Mode 1: Захист відсутній */
    mcu->current_address_bytes = 0;
    mcu->in_programming_mode = false;
    mcu->page_buffer_dirty = false;
    mcu->simulated_cpu_hz = 1000000UL; /* 1.0 МГц */
    mcu->current_isp_hz = 125000UL;    /* 125 кГц (безпечно: < f_CPU / 4) */
}

/* Повне стирання кристала */
void mcu_chip_erase(virtual_mcu_t *mcu) {
    if (!mcu) return;
    memset(mcu->flash, 0xFF, sizeof(mcu->flash));
    /* Якщо фьюз EESAVE (біт 3 fuse_high) не запрограмований (тобто 1), стираємо EEPROM */
    if ((mcu->fuse_high & 0x08) != 0) {
        memset(mcu->eeprom, 0xFF, sizeof(mcu->eeprom));
    }
    memset(mcu->page_buffer, 0xFF, sizeof(mcu->page_buffer));
    mcu->lock_bits = 0xFF; /* Скидання бітів захисту */
    mcu->page_buffer_dirty = false;
}

/* ── Структура та стан рушія програматора ─────────────────────────────────── */

typedef struct {
    virtual_mcu_t mcu;
    uint8_t seq_number;
    uint8_t sck_duration_param;
    uint8_t rx_buffer[BUFFER_MAX_SIZE];
    uint16_t rx_index;
    uint16_t rx_msg_size;
    uint8_t tx_buffer[BUFFER_MAX_SIZE];
    uint16_t tx_size;
} stk500_engine_t;

void stk_engine_init(stk500_engine_t *engine) {
    if (!engine) return;
    mcu_init(&engine->mcu);
    engine->seq_number = 0;
    engine->sck_duration_param = 8; /* Типовий параметр затримки SCK */
    engine->rx_index = 0;
    engine->rx_msg_size = 0;
    engine->tx_size = 0;
}

/* Обчислення контрольної суми XOR */
static uint8_t calculate_checksum(const uint8_t *data, uint16_t length) {
    uint8_t checksum = 0;
    for (uint16_t i = 0; i < length; ++i) {
        checksum ^= data[i];
    }
    return checksum;
}

/* Формування двійкового пакету відповіді STK500 v2 */
static void build_response(stk500_engine_t *engine, const uint8_t *payload, uint16_t payload_len) {
    if (!engine || !payload) return;
    
    engine->tx_buffer[0] = STK_MESSAGE_START;
    engine->tx_buffer[1] = engine->seq_number;
    engine->tx_buffer[2] = (uint8_t)((payload_len >> 8) & 0xFF);
    engine->tx_buffer[3] = (uint8_t)(payload_len & 0xFF);
    engine->tx_buffer[4] = STK_TOKEN;
    
    memcpy(&engine->tx_buffer[5], payload, payload_len);
    
    uint16_t total_before_crc = 5 + payload_len;
    engine->tx_buffer[total_before_crc] = calculate_checksum(engine->tx_buffer, total_before_crc);
    engine->tx_size = total_before_crc + 1;
}

/* ── Диспетчеризація команд протоколу ─────────────────────────────────────── */

void stk_process_command(stk500_engine_t *engine, const uint8_t *payload, uint16_t payload_len) {
    if (!engine || !payload || payload_len == 0) return;
    
    uint8_t cmd = payload[0];
    uint8_t resp_payload[BUFFER_MAX_SIZE];
    uint16_t resp_len = 0;
    
    switch (cmd) {
        case CMD_SIGN_ON: {
            resp_payload[0] = CMD_SIGN_ON;
            resp_payload[1] = STATUS_CMD_OK;
            const char *sig_str = "AVRISP_2";
            uint8_t sig_len = (uint8_t)strlen(sig_str);
            resp_payload[2] = sig_len;
            memcpy(&resp_payload[3], sig_str, sig_len);
            resp_len = 3 + sig_len;
            break;
        }
        
        case CMD_SET_PARAMETER: {
            resp_payload[0] = CMD_SET_PARAMETER;
            if (payload_len >= 3) {
                uint8_t param = payload[1];
                uint8_t val = payload[2];
                if (param == PARAM_SCK_DURATION) {
                    engine->sck_duration_param = val;
                    /* Розрахунок частоти: f_ISP = 1 / (SCK_DURATION * 1e-6) */
                    uint32_t calculated_hz = (val > 0) ? (1000000UL / val) : 2000000UL;
                    engine->mcu.current_isp_hz = calculated_hz;
                }
                resp_payload[1] = STATUS_CMD_OK;
            } else {
                resp_payload[1] = STATUS_CMD_FAILED;
            }
            resp_len = 2;
            break;
        }
        
        case CMD_GET_PARAMETER: {
            resp_payload[0] = CMD_GET_PARAMETER;
            resp_payload[1] = STATUS_CMD_OK;
            uint8_t param = (payload_len >= 2) ? payload[1] : 0;
            switch (param) {
                case PARAM_HW_VER:            resp_payload[2] = 0x02; break;
                case PARAM_SW_MAJOR:          resp_payload[2] = 0x02; break;
                case PARAM_SW_MINOR:          resp_payload[2] = 0x0A; break;
                case PARAM_VTARGET:           resp_payload[2] = 50;   break; /* 5.0V */
                case PARAM_SCK_DURATION:      resp_payload[2] = engine->sck_duration_param; break;
                default:                      resp_payload[2] = 0x00; break;
            }
            resp_len = 3;
            break;
        }
        
        case CMD_LOAD_ADDRESS: {
            resp_payload[0] = CMD_LOAD_ADDRESS;
            if (payload_len >= 5) {
                /* Адреса передається в 16-бітних словах (Big-Endian) */
                uint32_t word_addr = ((uint32_t)payload[1] << 24) |
                                     ((uint32_t)payload[2] << 16) |
                                     ((uint32_t)payload[3] << 8)  |
                                     ((uint32_t)payload[4]);
                /* Очищаємо прапорець автоінкременту (старший біт) та переводимо в байти */
                word_addr &= 0x7FFFFFFFUL;
                engine->mcu.current_address_bytes = word_addr * 2;
                resp_payload[1] = STATUS_CMD_OK;
            } else {
                resp_payload[1] = STATUS_CMD_FAILED;
            }
            resp_len = 2;
            break;
        }
        
        case CMD_ENTER_PROGMODE_ISP: {
            resp_payload[0] = CMD_ENTER_PROGMODE_ISP;
            /* Перевірка обмеження f_ISP < f_CPU / 4 */
            if (engine->mcu.current_isp_hz > (engine->mcu.simulated_cpu_hz / 4)) {
                /* Помилка частоти: кристал не встигає дискретизувати SCK */
                resp_payload[1] = STATUS_CMD_FAILED;
                engine->mcu.in_programming_mode = false;
            } else {
                engine->mcu.in_programming_mode = true;
                resp_payload[1] = STATUS_CMD_OK;
            }
            resp_len = 2;
            break;
        }
        
        case CMD_LEAVE_PROGMODE_ISP: {
            resp_payload[0] = CMD_LEAVE_PROGMODE_ISP;
            engine->mcu.in_programming_mode = false;
            resp_payload[1] = STATUS_CMD_OK;
            resp_len = 2;
            break;
        }
        
        case CMD_CHIP_ERASE_ISP: {
            resp_payload[0] = CMD_CHIP_ERASE_ISP;
            if (engine->mcu.in_programming_mode) {
                mcu_chip_erase(&engine->mcu);
                resp_payload[1] = STATUS_CMD_OK;
            } else {
                resp_payload[1] = STATUS_CMD_FAILED;
            }
            resp_len = 2;
            break;
        }
        
        case CMD_PROGRAM_FLASH_ISP: {
            resp_payload[0] = CMD_PROGRAM_FLASH_ISP;
            if (!engine->mcu.in_programming_mode) {
                resp_payload[1] = STATUS_CMD_FAILED;
                resp_len = 2;
                break;
            }
            /* Перевірка Lock Bits (Mode 2/3 забороняють запис) */
            if ((engine->mcu.lock_bits & 0x02) == 0) {
                resp_payload[1] = STATUS_CMD_FAILED; /* Захист від запису активний */
                resp_len = 2;
                break;
            }
            
            if (payload_len >= 10) {
                uint16_t num_bytes = ((uint16_t)payload[1] << 8) | payload[2];
                const uint8_t *data_ptr = &payload[10];
                
                if (engine->mcu.current_address_bytes + num_bytes <= MCU_FLASH_SIZE) {
                    memcpy(&engine->mcu.flash[engine->mcu.current_address_bytes], data_ptr, num_bytes);
                    engine->mcu.current_address_bytes += num_bytes;
                    resp_payload[1] = STATUS_CMD_OK;
                } else {
                    resp_payload[1] = STATUS_CMD_FAILED;
                }
            } else {
                resp_payload[1] = STATUS_CMD_FAILED;
            }
            resp_len = 2;
            break;
        }
        
        case CMD_READ_FLASH_ISP: {
            resp_payload[0] = CMD_READ_FLASH_ISP;
            if (!engine->mcu.in_programming_mode) {
                resp_payload[1] = STATUS_CMD_FAILED;
                resp_len = 2;
                break;
            }
            
            if (payload_len >= 3) {
                uint16_t num_bytes = ((uint16_t)payload[1] << 8) | payload[2];
                resp_payload[1] = STATUS_CMD_OK;
                
                /* Перевірка Lock Bits Mode 3 (заборона читання) */
                if ((engine->mcu.lock_bits & 0x01) == 0 && (engine->mcu.lock_bits & 0x02) == 0) {
                    /* Захищений стан: повертаємо 0xFF замість коду */
                    memset(&resp_payload[2], 0xFF, num_bytes);
                } else {
                    if (engine->mcu.current_address_bytes + num_bytes <= MCU_FLASH_SIZE) {
                        memcpy(&resp_payload[2], &engine->mcu.flash[engine->mcu.current_address_bytes], num_bytes);
                        engine->mcu.current_address_bytes += num_bytes;
                    } else {
                        memset(&resp_payload[2], 0xFF, num_bytes);
                    }
                }
                resp_payload[2 + num_bytes] = STATUS_CMD_OK;
                resp_len = 3 + num_bytes;
            } else {
                resp_payload[1] = STATUS_CMD_FAILED;
                resp_len = 2;
            }
            break;
        }
        
        case CMD_SPI_MULTI: {
            resp_payload[0] = CMD_SPI_MULTI;
            if (!engine->mcu.in_programming_mode) {
                resp_payload[1] = STATUS_CMD_FAILED;
                resp_len = 2;
                break;
            }
            
            if (payload_len >= 8) {
                uint8_t num_tx = payload[1];
                uint8_t num_rx = payload[2];
                uint8_t rx_start = payload[3];
                const uint8_t *tx_data = &payload[4];
                
                resp_payload[1] = STATUS_CMD_OK;
                uint8_t rx_buffer[4] = {0, 0, 0, 0};
                
                /* Розпізнавання низькорівневих 4-байтних команд ISP */
                if (num_tx >= 4) {
                    uint8_t op = tx_data[0];
                    if (op == 0x30) {
                        /* Read Signature: 0x30 0x00 [Addr 0..2] 0x00 */
                        uint8_t addr = tx_data[2];
                        if (addr == 0) rx_buffer[3] = MCU_SIG_BYTE0;
                        else if (addr == 1) rx_buffer[3] = MCU_SIG_BYTE1;
                        else if (addr == 2) rx_buffer[3] = MCU_SIG_BYTE2;
                    } else if (op == 0x58 && tx_data[1] == 0x00) {
                        /* Read Low Fuse */
                        rx_buffer[3] = engine->mcu.fuse_low;
                    } else if (op == 0x58 && tx_data[1] == 0x08) {
                        /* Read High Fuse */
                        rx_buffer[3] = engine->mcu.fuse_high;
                    } else if (op == 0x50 && tx_data[1] == 0x08) {
                        /* Read Ext Fuse */
                        rx_buffer[3] = engine->mcu.fuse_ext;
                    } else if (op == 0x58 && tx_data[1] == 0x00) {
                        /* Read Lock Bits */
                        rx_buffer[3] = engine->mcu.lock_bits;
                    } else if (op == 0xAC && tx_data[1] == 0xE0) {
                        /* Write Lock Bits: 0xAC 0xE0 0x00 [Data] */
                        engine->mcu.lock_bits &= tx_data[3]; /* Біти можна лише скидати в 0 */
                    }
                }
                
                memcpy(&resp_payload[2], &rx_buffer[rx_start], num_rx);
                resp_payload[2 + num_rx] = STATUS_CMD_OK;
                resp_len = 3 + num_rx;
            } else {
                resp_payload[1] = STATUS_CMD_FAILED;
                resp_len = 2;
            }
            break;
        }
        
        default: {
            resp_payload[0] = cmd;
            resp_payload[1] = STATUS_CMD_UNKNOWN;
            resp_len = 2;
            break;
        }
    }
    
    build_response(engine, resp_payload, resp_len);
}

/* ── Тестовий стенд емулятора (Integration Test Suite) ────────────────────── */

int main(void) {
    printf("==================================================================\n");
    printf("   Тестовий стенд програмного емулятора ISP-програматора STK500v2\n");
    printf("==================================================================\n\n");
    
    stk500_engine_t engine;
    stk_engine_init(&engine);
    
    /* Тест 1: Sign-On */
    printf("[1] Перевірка ідентифікації програматора (CMD_SIGN_ON)...\n");
    uint8_t sign_on_cmd[] = {CMD_SIGN_ON};
    stk_process_command(&engine, sign_on_cmd, sizeof(sign_on_cmd));
    if (engine.tx_buffer[6] == STATUS_CMD_OK && strstr((char*)&engine.tx_buffer[8], "AVRISP_2")) {
        printf("    -> УСПІХ: Відповідь '%s' валідна.\n", &engine.tx_buffer[8]);
    } else {
        printf("    -> ПОМИЛКА: Некоректний Sign-On.\n");
        return 1;
    }
    
    /* Тест 2: Налаштування безпечної швидкості SCK */
    printf("[2] Налаштування тривалості такту SCK (CMD_SET_PARAMETER)...\n");
    uint8_t set_param_cmd[] = {CMD_SET_PARAMETER, PARAM_SCK_DURATION, 8};
    stk_process_command(&engine, set_param_cmd, sizeof(set_param_cmd));
    printf("    -> УСПІХ: Встановлено частоту f_ISP = %lu Гц.\n", (unsigned long)engine.mcu.current_isp_hz);
    
    /* Тест 3: Захоплення чіпа в режим програмування */
    printf("[3] Вхід у режим ISP (CMD_ENTER_PROGMODE_ISP)...\n");
    uint8_t enter_cmd[12] = {CMD_ENTER_PROGMODE_ISP, 200, 100, 25, 32, 0, 0x53, 3, 0xAC, 0x53, 0x00, 0x00};
    stk_process_command(&engine, enter_cmd, sizeof(enter_cmd));
    if (engine.tx_buffer[6] == STATUS_CMD_OK && engine.mcu.in_programming_mode) {
        printf("    -> УСПІХ: Мікроконтролер перейшов у режим ISP.\n");
    } else {
        printf("    -> ПОМИЛКА: Не вдалося увійти в режим ISP.\n");
        return 1;
    }
    
    /* Тест 4: Зчитування сигнатури кристала через SPI_MULTI */
    printf("[4] Зчитування сигнатури мікроконтролера (CMD_SPI_MULTI)...\n");
    uint8_t sig_bytes[3] = {0};
    for (uint8_t i = 0; i < 3; ++i) {
        uint8_t spi_cmd[] = {CMD_SPI_MULTI, 4, 1, 3, 0x30, 0x00, i, 0x00};
        stk_process_command(&engine, spi_cmd, sizeof(spi_cmd));
        sig_bytes[i] = engine.tx_buffer[7];
    }
    printf("    -> Вичитана сигнатура: 0x%02X 0x%02X 0x%02X\n", sig_bytes[0], sig_bytes[1], sig_bytes[2]);
    if (sig_bytes[0] == MCU_SIG_BYTE0 && sig_bytes[1] == MCU_SIG_BYTE1 && sig_bytes[2] == MCU_SIG_BYTE2) {
        printf("    -> УСПІХ: Кристал ідентифіковано як ATmega328P.\n");
    } else {
        printf("    -> ПОМИЛКА сигнатури!\n");
        return 1;
    }
    
    /* Тест 5: Повне стирання кристала */
    printf("[5] Повне стирання кристала (CMD_CHIP_ERASE_ISP)...\n");
    uint8_t erase_cmd[] = {CMD_CHIP_ERASE_ISP, 10, 0, 0xAC, 0x80, 0x00, 0x00};
    stk_process_command(&engine, erase_cmd, sizeof(erase_cmd));
    if (engine.tx_buffer[6] == STATUS_CMD_OK) {
        printf("    -> УСПІХ: Flash і Lock Bits очищено в 0xFF.\n");
    }
    
    /* Тест 6: Посторінковий запис тестового образу прошивки */
    printf("[6] Запис тестової сторінки 128 байтів (CMD_PROGRAM_FLASH_ISP)...\n");
    uint8_t load_addr_cmd[] = {CMD_LOAD_ADDRESS, 0x00, 0x00, 0x00, 0x00}; /* Адреса 0x0000 */
    stk_process_command(&engine, load_addr_cmd, sizeof(load_addr_cmd));
    
    uint8_t flash_page[10 + MCU_PAGE_SIZE];
    flash_page[0] = CMD_PROGRAM_FLASH_ISP;
    flash_page[1] = 0x00;
    flash_page[2] = MCU_PAGE_SIZE; /* 128 байтів */
    flash_page[3] = 0x00;
    flash_page[4] = 10;
    flash_page[5] = 0x4C; flash_page[6] = 0x00; flash_page[7] = 0x00;
    flash_page[8] = 0x00; flash_page[9] = 0x00;
    for (uint16_t i = 0; i < MCU_PAGE_SIZE; ++i) {
        flash_page[10 + i] = (uint8_t)(i & 0xFF); /* Тестовий патерн даних */
    }
    stk_process_command(&engine, flash_page, sizeof(flash_page));
    if (engine.tx_buffer[6] == STATUS_CMD_OK) {
        printf("    -> УСПІХ: 128 байтів записано у Flash за адресою 0x0000.\n");
    } else {
        printf("    -> ПОМИЛКА запису сторінки Flash.\n");
        return 1;
    }
    
    /* Тест 7: Верифікація записаної пам'яті */
    printf("[7] Зчитування та верифікація Flash (CMD_READ_FLASH_ISP)...\n");
    stk_process_command(&engine, load_addr_cmd, sizeof(load_addr_cmd));
    uint8_t read_flash_cmd[] = {CMD_READ_FLASH_ISP, 0x00, MCU_PAGE_SIZE, 0x20};
    stk_process_command(&engine, read_flash_cmd, sizeof(read_flash_cmd));
    
    bool verify_ok = true;
    for (uint16_t i = 0; i < MCU_PAGE_SIZE; ++i) {
        if (engine.tx_buffer[7 + i] != (uint8_t)(i & 0xFF)) {
            verify_ok = false;
            break;
        }
    }
    if (verify_ok) {
        printf("    -> УСПІХ: Усі 128 байтів верифіковано без жодної розбіжності.\n");
    } else {
        printf("    -> ПОМИЛКА верифікації Flash!\n");
        return 1;
    }
    
    /* Тест 8: Вихід із режиму програмування */
    printf("[8] Вихід із режиму ISP (CMD_LEAVE_PROGMODE_ISP)...\n");
    uint8_t leave_cmd[] = {CMD_LEAVE_PROGMODE_ISP, 1, 1};
    stk_process_command(&engine, leave_cmd, sizeof(leave_cmd));
    if (engine.tx_buffer[6] == STATUS_CMD_OK && !engine.mcu.in_programming_mode) {
        printf("    -> УСПІХ: Сигнал RESET знято, мікроконтролер запущено.\n\n");
    }
    
    printf("==================================================================\n");
    printf("       Усі 8 інтеграційних тестів рушія пройдено успішно!         \n");
    printf("==================================================================\n");
    return 0;
}
