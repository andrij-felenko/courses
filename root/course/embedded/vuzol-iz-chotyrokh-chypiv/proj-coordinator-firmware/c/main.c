#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define TELEMETRY_RECORD_SIZE  24
#define FLASH_PAGE_SIZE        256
#define FLASH_SECTOR_SIZE      4096
#define RS485_RX_BUF_SIZE      64
#define RS485_TX_BUF_SIZE      64

/* ── Структури даних ──────────────────────────────────────────────────────── */

typedef struct __attribute__((packed)) {
    uint32_t timestamp;     /* Unix timestamp від DS3231 */
    int32_t  temperature;   /* Температура x100 (°C)     */
    uint32_t pressure;      /* Тиск x100 (Па)            */
    uint32_t humidity;      /* Вологість x1024 (%RH)     */
    uint16_t sequence_id;   /* Порядковий номер зрізу    */
    uint16_t status_flags;  /* Прапорці стану вузла      */
    uint16_t crc16;         /* Контрольна сума запису    */
} telemetry_record_t;

typedef enum {
    NODE_EVENT_NONE = 0,
    NODE_EVENT_RTC_TICK,
    NODE_EVENT_DATA_READY,
    NODE_EVENT_RS485_RX,
    NODE_EVENT_FLASH_SYNC
} node_event_t;

typedef struct {
    uint32_t write_address;
    uint32_t record_count;
    uint8_t  page_buffer[FLASH_PAGE_SIZE];
    uint16_t page_offset;
} flash_logger_t;

typedef struct {
    uint8_t  rx_buf[RS485_RX_BUF_SIZE];
    uint8_t  tx_buf[RS485_TX_BUF_SIZE];
    uint16_t rx_index;
    bool     frame_ready;
} rs485_channel_t;

typedef struct {
    flash_logger_t  logger;
    rs485_channel_t comm;
    uint16_t        seq_counter;
    volatile node_event_t pending_event;
} node_coordinator_t;

/* ── Апаратні інтерфейси (зовнішні драйвери) ──────────────────────────────── */

extern bool bme280_read_measurements(int32_t *t, uint32_t *p, uint32_t *h);
extern bool ds3231_get_unix_time(uint32_t *unix_time);
extern bool w25q128_page_program(uint32_t addr, const uint8_t *data, uint16_t len);
extern bool w25q128_sector_erase(uint32_t addr);
extern void rs485_set_de(bool enable);
extern void rs485_transmit_bytes(const uint8_t *data, uint16_t len);

/* ── Контрольна сума CRC-16 Modbus ────────────────────────────────────────── */

static uint16_t calculate_crc16(const uint8_t *data, uint16_t len) {
    uint16_t crc = 0xFFFF;
    for (uint16_t i = 0; i < len; i++) {
        crc ^= (uint16_t)data[i];
        for (uint8_t j = 0; j < 8; j++) {
            if (crc & 0x0001) {
                crc = (crc >> 1) ^ 0xA001;
            } else {
                crc = crc >> 1;
            }
        }
    }
    return crc;
}

/* ── Ініціалізація та обробка записів у Flash ─────────────────────────────── */

void node_init(node_coordinator_t *node) {
    memset(node, 0, sizeof(node_coordinator_t));
    node->logger.write_address = 0x000000;
    node->logger.page_offset = 0;
    node->seq_counter = 1;
    node->pending_event = NODE_EVENT_NONE;
    rs485_set_de(false);
}

static void logger_write_record(flash_logger_t *log, const telemetry_record_t *rec) {
    /* Якщо починається новий сектор (4096 байтів), очищуємо його */
    if ((log->write_address % FLASH_SECTOR_SIZE) == 0 && log->page_offset == 0) {
        w25q128_sector_erase(log->write_address);
    }

    /* Копіюємо запис у сторінковий буфер ОЗП */
    memcpy(&log->page_buffer[log->page_offset], rec, sizeof(telemetry_record_t));
    log->page_offset += sizeof(telemetry_record_t);
    log->record_count++;

    /* Якщо сторінка (256 байтів) заповнена, скидаємо її у Flash */
    if (log->page_offset + sizeof(telemetry_record_t) > FLASH_PAGE_SIZE) {
        w25q128_page_program(log->write_address, log->page_buffer, log->page_offset);
        log->write_address += FLASH_PAGE_SIZE;
        log->page_offset = 0;
        memset(log->page_buffer, 0xFF, FLASH_PAGE_SIZE);
    }
}

/* ── Обробка подій та протоколу RS-485 ────────────────────────────────────── */

void node_process_rs485_request(node_coordinator_t *node, const telemetry_record_t *last_rec) {
    if (!node->comm.frame_ready) return;

    /* Перевірка простого кадру запиту: [0x01 (Node ID)][0x03 (Read)][CRC16_L][CRC16_H] */
    if (node->comm.rx_index >= 4 && node->comm.rx_buf[0] == 0x01 && node->comm.rx_buf[1] == 0x03) {
        uint16_t rx_crc = (uint16_t)node->comm.rx_buf[2] | ((uint16_t)node->comm.rx_buf[3] << 8);
        if (calculate_crc16(node->comm.rx_buf, 2) == rx_crc) {
            /* Формування відповіді */
            node->comm.tx_buf[0] = 0x01; /* Node ID */
            node->comm.tx_buf[1] = 0x03; /* Function Code */
            node->comm.tx_buf[2] = sizeof(telemetry_record_t);
            memcpy(&node->comm.tx_buf[3], last_rec, sizeof(telemetry_record_t));

            uint16_t tx_len = 3 + sizeof(telemetry_record_t);
            uint16_t tx_crc = calculate_crc16(node->comm.tx_buf, tx_len);
            node->comm.tx_buf[tx_len]     = (uint8_t)(tx_crc & 0xFF);
            node->comm.tx_buf[tx_len + 1] = (uint8_t)((tx_crc >> 8) & 0xFF);
            tx_len += 2;

            /* Відправка через RS-485 з контролем виводу DE */
            rs485_set_de(true);
            rs485_transmit_bytes(node->comm.tx_buf, tx_len);
            rs485_set_de(false);
        }
    }

    node->comm.rx_index = 0;
    node->comm.frame_ready = false;
}

void node_task_step(node_coordinator_t *node) {
    static telemetry_record_t current_record;

    if (node->pending_event == NODE_EVENT_RTC_TICK) {
        node->pending_event = NODE_EVENT_NONE;

        uint32_t unix_ts = 0;
        int32_t  t = 0;
        uint32_t p = 0, h = 0;

        /* Послідовне зчитування з контролем статусу шини I2C */
        if (ds3231_get_unix_time(&unix_ts) && bme280_read_measurements(&t, &p, &h)) {
            current_record.timestamp   = unix_ts;
            current_record.temperature = t;
            current_record.pressure    = p;
            current_record.humidity    = h;
            current_record.sequence_id = node->seq_counter++;
            current_record.status_flags = 0x0001; /* OK flag */
            current_record.crc16       = calculate_crc16((const uint8_t *)&current_record,
                                                         sizeof(telemetry_record_t) - 2);

            /* Збереження у Flash через енергонезалежний логер */
            logger_write_record(&node->logger, &current_record);
        }
    }

    if (node->comm.frame_ready) {
        node_process_rs485_request(node, &current_record);
    }
}
