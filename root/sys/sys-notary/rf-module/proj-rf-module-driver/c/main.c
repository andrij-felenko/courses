#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

/* Адреси регістрів та маски RF-трансивера */
#define RF_REG_OP_MODE        0x01
#define RF_REG_FIFO           0x00
#define RF_REG_IRQ_FLAGS      0x12
#define RF_REG_PAYLOAD_LEN    0x22

#define RF_MODE_SLEEP         0x00
#define RF_MODE_STANDBY       0x01
#define RF_MODE_TX            0x03
#define RF_MODE_RX            0x05

#define RF_SPI_WRITE_MASK     0x80

/* Зовнішній апаратний інтерфейс (HAL) */
extern void hal_spi_select(bool enable);
extern uint8_t hal_spi_transfer_byte(uint8_t data);
extern void hal_gpio_set_tx_mode(bool tx_on);
extern void hal_delay_ms(uint32_t ms);

typedef enum {
    RF_OK = 0,
    RF_ERR_TIMEOUT,
    RF_ERR_PARAM
} rf_status_t;

/* Запис значення в регістр модуля */
rf_status_t rf_module_write_reg(uint8_t reg, uint8_t val) {
    hal_spi_select(true);
    hal_spi_transfer_byte(reg | RF_SPI_WRITE_MASK);
    hal_spi_transfer_byte(val);
    hal_spi_select(false);
    return RF_OK;
}

/* Читання значення з регістра модуля */
uint8_t rf_module_read_reg(uint8_t reg) {
    hal_spi_select(true);
    hal_spi_transfer_byte(reg & ~RF_SPI_WRITE_MASK);
    uint8_t val = hal_spi_transfer_byte(0x00);
    hal_spi_select(false);
    return val;
}

/* Зміна режиму роботи радіомодуля та керування T/R перемикачем */
rf_status_t rf_module_set_mode(uint8_t mode) {
    if (mode == RF_MODE_TX) {
        hal_gpio_set_tx_mode(true);  /* Перемикаємо FEM на TX (PA_EN = 1) */
    } else {
        hal_gpio_set_tx_mode(false); /* Перемикаємо FEM на RX/Standby */
    }
    return rf_module_write_reg(RF_REG_OP_MODE, mode);
}

/* Ініціалізація радіомодуля */
rf_status_t rf_module_init(void) {
    hal_spi_select(false);
    hal_gpio_set_tx_mode(false);
    
    rf_module_set_mode(RF_MODE_STANDBY);
    hal_delay_ms(5);
    
    /* Перевірка зв'язку з трансивером */
    uint8_t mode = rf_module_read_reg(RF_REG_OP_MODE);
    if ((mode & 0x07) != RF_MODE_STANDBY) {
        return RF_ERR_TIMEOUT;
    }
    return RF_OK;
}

/* Передача пакунка даних через FIFO */
rf_status_t rf_module_send_packet(const uint8_t *data, size_t len) {
    if (!data || len == 0 || len > 255) {
        return RF_ERR_PARAM;
    }

    rf_module_set_mode(RF_MODE_STANDBY);
    rf_module_write_reg(RF_REG_PAYLOAD_LEN, (uint8_t)len);

    /* Запис даних у FIFO буфер */
    hal_spi_select(true);
    hal_spi_transfer_byte(RF_REG_FIFO | RF_SPI_WRITE_MASK);
    for (size_t i = 0; i < len; i++) {
        hal_spi_transfer_byte(data[i]);
    }
    hal_spi_select(false);

    /* Запуск передачі в ефір */
    rf_module_set_mode(RF_MODE_TX);
    return RF_OK;
}

/* Обробник переривання IRQ (викликуваний з ISR хост-MCU) */
void rf_module_handle_irq(void) {
    uint8_t flags = rf_module_read_reg(RF_REG_IRQ_FLAGS);
    if (flags & 0x08) { /* TX Done */
        rf_module_write_reg(RF_REG_IRQ_FLAGS, 0x08); /* Скидання прапорця */
        rf_module_set_mode(RF_MODE_STANDBY);
    }
}
