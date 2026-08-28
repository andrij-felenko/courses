#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <string.h>

#define DAISY_MAX_DEVICES   16
#define DAISY_WORD_SIZE     2   /* 16-бітні слова даних для кожного чипа */

typedef enum {
    DAISY_OK = 0,
    DAISY_ERR_INVALID_PARAM,
    DAISY_ERR_BUS_BUSY,
    DAISY_ERR_LOOPBACK_FAULT,
    DAISY_ERR_TIMEOUT
} daisy_status_t;

/* Структура конфігурації та стану каскаду */
typedef struct {
    uint8_t num_devices;                    /* Кількість мікросхем у каскаді */
    uint16_t shadow_tx[DAISY_MAX_DEVICES];  /* Логічний вихідний буфер */
    uint16_t shadow_rx[DAISY_MAX_DEVICES];  /* Логічний буфер зчитаних даних */
    uint8_t raw_tx[DAISY_MAX_DEVICES * 2];  /* Сирий буфер передачі (реверсний) */
    uint8_t raw_rx[DAISY_MAX_DEVICES * 2];  /* Сирий буфер прийому */
} daisy_cascade_t;

/* Прототипи функцій апаратно-залежного рівня (HAL) */
extern void hal_spi_cs_low(void);
extern void hal_spi_cs_high(void);
extern void hal_spi_delay_ns(uint32_t ns);
extern bool hal_spi_transfer_blocking(const uint8_t *tx, uint8_t *rx, size_t len);

/* Ініціалізація структури драйвера */
daisy_status_t daisy_init(daisy_cascade_t *dev, uint8_t num_devices) {
    if (!dev || num_devices == 0 || num_devices > DAISY_MAX_DEVICES) {
        return DAISY_ERR_INVALID_PARAM;
    }
    dev->num_devices = num_devices;
    memset(dev->shadow_tx, 0, sizeof(dev->shadow_tx));
    memset(dev->shadow_rx, 0, sizeof(dev->shadow_rx));
    hal_spi_cs_high();
    return DAISY_OK;
}

/* Оновлення логічного стану конкретного чипа в тіньовому буфері */
daisy_status_t daisy_set_device_value(daisy_cascade_t *dev, uint8_t index, uint16_t value) {
    if (!dev || index >= dev->num_devices) {
        return DAISY_ERR_INVALID_PARAM;
    }
    dev->shadow_tx[index] = value;
    return DAISY_OK;
}

/* Зчитування отриманого телеметричного значення конкретного чипа */
daisy_status_t daisy_get_device_feedback(const daisy_cascade_t *dev, uint8_t index, uint16_t *value) {
    if (!dev || !value || index >= dev->num_devices) {
        return DAISY_ERR_INVALID_PARAM;
    }
    *value = dev->shadow_rx[index];
    return DAISY_OK;
}

/* Повний синхронний обмін кадру каскаду */
daisy_status_t daisy_sync_transaction(daisy_cascade_t *dev) {
    if (!dev) return DAISY_ERR_INVALID_PARAM;

    const size_t total_bytes = dev->num_devices * DAISY_WORD_SIZE;

    /* Пакування слів у передавальний буфер у зворотному порядку (IC_N першим) */
    for (uint8_t i = 0; i < dev->num_devices; ++i) {
        uint8_t rev_idx = (dev->num_devices - 1) - i;
        uint16_t word = dev->shadow_tx[rev_idx];
        dev->raw_tx[i * 2 + 0] = (uint8_t)(word >> 8);    /* Старший байт (MSB) */
        dev->raw_tx[i * 2 + 1] = (uint8_t)(word & 0xFF);   /* Молодший байт (LSB) */
    }

    /* Початок кадру: переведення лінії CS у низький активний рівень */
    hal_spi_cs_low();
    hal_spi_delay_ns(50); /* Час випередження CS до першого фронту такту (t_setup_CS) */

    /* Повнодуплексна передача даних через апаратний SPI */
    bool ok = hal_spi_transfer_blocking(dev->raw_tx, dev->raw_rx, total_bytes);
    if (!ok) {
        hal_spi_cs_high();
        return DAISY_ERR_BUS_BUSY;
    }

    /* Завершення кадру: фіксація даних у вихідних засувках (Latch) */
    hal_spi_delay_ns(50); /* Час утримання CS після останнього фронту такту (t_hold_CS) */
    hal_spi_cs_high();
    hal_spi_delay_ns(100); /* Мінімальна тривалість імпульсу засувки (t_pulse_CS_high) */

    /* Розпакування прийнятих даних із черги MISO у логічний буфер */
    for (uint8_t i = 0; i < dev->num_devices; ++i) {
        uint8_t rev_idx = (dev->num_devices - 1) - i;
        uint16_t high_byte = dev->raw_rx[i * 2 + 0];
        uint16_t low_byte  = dev->raw_rx[i * 2 + 1];
        dev->shadow_rx[rev_idx] = (uint16_t)((high_byte << 8) | low_byte);
    }

    return DAISY_OK;
}

/* Комплексна діагностика цілісності кільця за допомогою тестової сигнатури */
daisy_status_t daisy_run_loopback_test(daisy_cascade_t *dev, uint8_t *first_faulty_index) {
    if (!dev || !first_faulty_index) return DAISY_ERR_INVALID_PARAM;

    const uint16_t test_magic = 0xA55A;

    /* Зберігаємо поточний робочий стан виходів */
    uint16_t saved_tx[DAISY_MAX_DEVICES];
    memcpy(saved_tx, dev->shadow_tx, sizeof(saved_tx));

    /* Заповнюємо каскад унікальними тестовими мітками */
    for (uint8_t i = 0; i < dev->num_devices; ++i) {
        dev->shadow_tx[i] = (uint16_t)(test_magic + i);
    }

    /* Перша транзакція: завантажуємо тестові сигнатури в зсувні регістри */
    daisy_status_t st = daisy_sync_transaction(dev);
    if (st != DAISY_OK) return st;

    /* Друга транзакція: виштовхуємо сигнатури на лінію MISO контролера */
    st = daisy_sync_transaction(dev);
    if (st != DAISY_OK) return st;

    /* Перевірка відповідності повернутих сигнатур очікуваним значенням */
    for (uint8_t i = 0; i < dev->num_devices; ++i) {
        uint16_t expected = (uint16_t)(test_magic + i);
        if (dev->shadow_rx[i] != expected) {
            *first_faulty_index = i;
            /* Відновлюємо робочий стан перед виходом */
            memcpy(dev->shadow_tx, saved_tx, sizeof(saved_tx));
            daisy_sync_transaction(dev);
            return DAISY_ERR_LOOPBACK_FAULT;
        }
    }

    /* Відновлюємо робочий стан */
    memcpy(dev->shadow_tx, saved_tx, sizeof(saved_tx));
    daisy_sync_transaction(dev);
    return DAISY_OK;
}
