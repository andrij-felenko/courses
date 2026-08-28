#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define MODBUS_BROADCAST_ADDR    0x00
#define MODBUS_READ_INPUT_REGS   0x04
#define MODBUS_ERR_OFFSET        0x80

typedef enum {
    MODBUS_OK = 0,
    MODBUS_ERR_TIMEOUT,
    MODBUS_ERR_CRC,
    MODBUS_ERR_EXCEPTION,
    MODBUS_ERR_WRONG_SLAVE,
    MODBUS_ERR_WRONG_FUNC,
    MODBUS_ERR_BUFFER_OVERFLOW
} ModbusStatus;

typedef struct {
    uint8_t slave_addr;
    uint16_t start_register;
    uint16_t register_count;
    uint32_t response_timeout_ms;
} ModbusRequestConfig;

/* Апаратний інтерфейс платформи (HAL) */
typedef struct {
    void (*set_de_pin)(bool high);
    void (*uart_write_bytes)(const uint8_t *data, size_t len);
    void (*uart_wait_tx_complete)(void);
    size_t (*uart_read_bytes)(uint8_t *buffer, size_t max_len, uint32_t timeout_ms);
    void (*delay_us)(uint32_t us);
} ModbusHal;

/* Табличний розрахунок полінома CRC16 Modbus (0xA001) */
static const uint16_t crc16_table[256] = {
    0x0000, 0xC0C1, 0xC181, 0x0140, 0xC301, 0x03C0, 0x0280, 0xC241,
    0xC601, 0x06C0, 0x0780, 0xC741, 0x0500, 0xC5C1, 0xC481, 0x0440,
    0xCC01, 0x0CC0, 0x0D80, 0xCD41, 0x0F00, 0xCFC1, 0xCE81, 0x0E40,
    0x0A00, 0xCAC1, 0xCB81, 0x0B40, 0xC901, 0x09C0, 0x0880, 0xC841,
    0xD801, 0x18C0, 0x1980, 0xD941, 0x1B00, 0xDBC1, 0xDA81, 0x1A40,
    0x1E00, 0xDEC1, 0xDF81, 0x1F40, 0xDD01, 0x1DC0, 0x1C80, 0xDC41,
    0x1400, 0xD4C1, 0xD581, 0x1540, 0xD701, 0x17C0, 0x1680, 0xD641,
    0xD201, 0x12C0, 0x1380, 0xD341, 0x1100, 0xD1C1, 0xD081, 0x1040,
    0xF001, 0x30C0, 0x3180, 0xF141, 0x3300, 0xF3C1, 0xF281, 0x3240,
    0x3600, 0xF6C1, 0xF781, 0x3740, 0xF501, 0x35C0, 0x3480, 0xF441,
    0x3C00, 0xFCC1, 0xFD81, 0x3D40, 0xFF01, 0x3FC0, 0x3E80, 0xFE41,
    0xFA01, 0x3AC0, 0x3B80, 0xFB41, 0x3900, 0xF9C1, 0xF881, 0x3840,
    0x2800, 0xE8C1, 0xE981, 0x2940, 0xEB01, 0x2BC0, 0x2A80, 0xEA41,
    0xEE01, 0x2EC0, 0x2F80, 0xEF41, 0x2D00, 0xEDC1, 0xEC81, 0x2C40,
    0xE401, 0x24C0, 0x2580, 0xE541, 0x2700, 0xE7C1, 0xE681, 0x2640,
    0x2200, 0xE2C1, 0xE381, 0x2340, 0xE101, 0x21C0, 0x2080, 0xE041,
    0xA001, 0x60C0, 0x6180, 0xA141, 0x6300, 0xA3C1, 0xA281, 0x6240,
    0x6600, 0xA6C1, 0xA781, 0x6740, 0xA501, 0x65C0, 0x6480, 0xA441,
    0x6C00, 0xACC1, 0xAD81, 0x6D40, 0xAF01, 0x6FC0, 0x6E80, 0xAE41,
    0xAA01, 0x6AC0, 0x6B80, 0xAB41, 0x6900, 0xA9C1, 0xA881, 0x6840,
    0x7800, 0xB8C1, 0xB981, 0x7940, 0xBB01, 0x2BC0, 0xBA80, 0xB641,
    0xBE01, 0x7EC0, 0x7F80, 0xBF41, 0x7D00, 0xBDC1, 0xBC81, 0x7C40,
    0xB401, 0x74C0, 0x7580, 0xB541, 0x7700, 0xB7C1, 0xB681, 0x7640,
    0x7200, 0xB2C1, 0xB381, 0x7340, 0xB101, 0x71C0, 0x7080, 0xB041,
    0x5000, 0x90C1, 0x9181, 0x5140, 0x9301, 0x53C0, 0x5280, 0x9241,
    0x9601, 0x56C0, 0x5780, 0x9741, 0x5500, 0x95C1, 0x9481, 0x5440,
    0x9C01, 0x5CC0, 0x5D80, 0x9D41, 0x5F00, 0x9FC1, 0x9E81, 0x5E40,
    0x5A00, 0x9AC1, 0x9B81, 0x5B40, 0x9901, 0x59C0, 0x5880, 0x9841,
    0x8801, 0x48C0, 0x4980, 0x8941, 0x4B00, 0x8BC1, 0x8A81, 0x4A40,
    0x4E00, 0x8EC1, 0x8F81, 0x4F40, 0x8D01, 0x4DC0, 0x4C80, 0x8C41,
    0x4400, 0x84C1, 0x8581, 0x4540, 0x8701, 0x47C0, 0x4680, 0x8641,
    0x8201, 0x42C0, 0x4380, 0x8341, 0x4100, 0x81C1, 0x8081, 0x4040
};

uint16_t modbus_calculate_crc(const uint8_t *buffer, size_t length) {
    uint16_t crc = 0xFFFF;
    for (size_t i = 0; i < length; ++i) {
        uint8_t index = (uint8_t)(crc ^ buffer[i]);
        crc = (uint16_t)((crc >> 8) ^ crc16_table[index]);
    }
    return crc;
}

ModbusStatus modbus_read_input_registers(
    const ModbusHal *hal,
    const ModbusRequestConfig *config,
    uint16_t *dest_registers,
    size_t max_dest_len
) {
    if (config->register_count > max_dest_len || config->register_count == 0) {
        return MODBUS_ERR_BUFFER_OVERFLOW;
    }

    uint8_t tx_frame[8];
    tx_frame[0] = config->slave_addr;
    tx_frame[1] = MODBUS_READ_INPUT_REGS;
    tx_frame[2] = (uint8_t)(config->start_register >> 8);
    tx_frame[3] = (uint8_t)(config->start_register & 0xFF);
    tx_frame[4] = (uint8_t)(config->register_count >> 8);
    tx_frame[5] = (uint8_t)(config->register_count & 0xFF);

    uint16_t tx_crc = modbus_calculate_crc(tx_frame, 6);
    tx_frame[6] = (uint8_t)(tx_crc & 0xFF);         /* CRC Lo */
    tx_frame[7] = (uint8_t)((tx_crc >> 8) & 0xFF);  /* CRC Hi */

    /* Перемикання трансивера в режим передачі TX */
    hal->set_de_pin(true);
    hal->delay_us(50); /* Затримка стабілізації драйвера лінії */

    hal->uart_write_bytes(tx_frame, sizeof(tx_frame));
    hal->uart_wait_tx_complete(); /* Чекаємо прапорця TC (Transmission Complete) */

    /* Перемикання трансивера в режим прийому RX */
    hal->set_de_pin(false);

    /* Очікування та прийом відповіді */
    uint8_t rx_buffer[256];
    size_t expected_payload_bytes = config->register_count * 2;
    size_t expected_total_bytes = 1 + 1 + 1 + expected_payload_bytes + 2;

    size_t bytes_received = hal->uart_read_bytes(
        rx_buffer,
        sizeof(rx_buffer),
        config->response_timeout_ms
    );

    if (bytes_received < 5) {
        return MODBUS_ERR_TIMEOUT;
    }

    /* Перевірка контрольної суми CRC16 отриманого кадру */
    uint16_t rx_crc = (uint16_t)(rx_buffer[bytes_received - 2] |
                                (rx_buffer[bytes_received - 1] << 8));
    uint16_t computed_crc = modbus_calculate_crc(rx_buffer, bytes_received - 2);

    if (rx_crc != computed_crc) {
        return MODBUS_ERR_CRC;
    }

    /* Перевірка адреси відправника */
    if (rx_buffer[0] != config->slave_addr) {
        return MODBUS_ERR_WRONG_SLAVE;
    }

    /* Обробка винятку Modbus (Exception) */
    if (rx_buffer[1] == (MODBUS_READ_INPUT_REGS | MODBUS_ERR_OFFSET)) {
        return MODBUS_ERR_EXCEPTION;
    }

    if (rx_buffer[1] != MODBUS_READ_INPUT_REGS) {
        return MODBUS_ERR_WRONG_FUNC;
    }

    uint8_t byte_count = rx_buffer[2];
    if (byte_count != expected_payload_bytes || bytes_received != expected_total_bytes) {
        return MODBUS_ERR_CRC;
    }

    /* Розпакування 16-бітних регістрів (Big-Endian на шині) */
    for (size_t i = 0; i < config->register_count; ++i) {
        size_t offset = 3 + i * 2;
        dest_registers[i] = (uint16_t)((rx_buffer[offset] << 8) | rx_buffer[offset + 1]);
    }

    return MODBUS_OK;
}
