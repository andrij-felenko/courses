/* Драйвер програмного SPI Master для ISP-програматора (C99) */
#include <stdint.h>
#include <stdbool.h>

/* Платформозалежні функції керування фізичними лініями GPIO */
extern void gpio_set_reset(bool level);
extern void gpio_set_sck(bool level);
extern void gpio_set_mosi(bool level);
extern bool gpio_get_miso(void);
extern void delay_us(uint32_t us);
extern void delay_ms(uint32_t ms);

typedef struct {
    uint32_t half_period_us; /* Напівперіод SCK (задає частоту f_ISP) */
    bool in_prog_mode;       /* Прапорець активного режиму ISP */
} isp_driver_t;

/* Ініціалізація параметрів драйвера з перевіркою обмеження частоти */
bool isp_init(isp_driver_t *drv, uint32_t target_cpu_hz, uint32_t desired_isp_hz) {
    if (!drv || target_cpu_hz == 0 || desired_isp_hz == 0) {
        return false;
    }
    
    /* Залізне правило безпеки: f_ISP <= f_CPU / 4 (з запасом беремо f_CPU / 6) */
    uint32_t max_safe_isp_hz = target_cpu_hz / 6;
    uint32_t actual_isp_hz = (desired_isp_hz > max_safe_isp_hz) ? max_safe_isp_hz : desired_isp_hz;
    
    /* Розрахунок тривалості напівперіоду в мікросекундах */
    drv->half_period_us = 1000000UL / (actual_isp_hz * 2);
    if (drv->half_period_us == 0) {
        drv->half_period_us = 1; /* Мінімум 1 мкс затримки */
    }
    drv->in_prog_mode = false;
    return true;
}

/* Побайтова передача по шині SPI Mode 0 (MSB First) */
static uint8_t isp_spi_transfer_byte(const isp_driver_t *drv, uint8_t data_out) {
    uint8_t data_in = 0;
    
    for (int i = 7; i >= 0; --i) {
        /* 1. Виставляємо біт MOSI по спадному фронту / до наростаючого */
        gpio_set_mosi((data_out >> i) & 0x01);
        delay_us(drv->half_period_us);
        
        /* 2. Формуємо наростаючий фронт SCK (Slave фіксує MOSI) */
        gpio_set_sck(true);
        delay_us(drv->half_period_us);
        
        /* 3. Зчитуємо біт відповіді з лінії MISO */
        if (gpio_get_miso()) {
            data_in |= (uint8_t)(1U << i);
        }
        
        /* 4. Формуємо спадний фронт SCK */
        gpio_set_sck(false);
    }
    return data_in;
}

/* Передача 4-байтної транзакції ISP */
bool isp_execute_transaction(const isp_driver_t *drv, const uint8_t cmd[4], uint8_t response[4]) {
    if (!drv) return false;
    for (int i = 0; i < 4; ++i) {
        uint8_t res = isp_spi_transfer_byte(drv, cmd[i]);
        if (response) {
            response[i] = res;
        }
    }
    return true;
}

/* Процедура апаратного захоплення цільового мікроконтролера в режим ISP */
bool isp_enter_programming_mode(isp_driver_t *drv) {
    if (!drv) return false;
    
    /* 1. Скидання всіх ліній у початковий пасивний стан */
    gpio_set_sck(false);
    gpio_set_mosi(false);
    gpio_set_reset(true);  /* RESET = High (VCC) */
    delay_ms(20);
    
    /* 2. Притискаємо RESET до 0V для заморожування ядра */
    gpio_set_reset(false); /* RESET = Low (0V) */
    delay_ms(25);          /* Пауза t_RST >= 20мс для стабілізації схеми */
    
    /* 3. Передача команди Programming Enable: 0xAC, 0x53, 0x00, 0x00 */
    uint8_t cmd[4] = {0xAC, 0x53, 0x00, 0x00};
    uint8_t resp[4] = {0};
    
    isp_execute_transaction(drv, cmd, resp);
    
    /* 4. Перевірка відлуння ключа 0x53 у третьому байті відповіді */
    if (resp[2] == 0x53) {
        drv->in_prog_mode = true;
        return true;
    }
    
    /* Невдача: відлуння не збіглося */
    gpio_set_reset(true); /* Звільняємо чіп */
    drv->in_prog_mode = false;
    return false;
}

/* Звільнення чіпа та вихід із режиму програмування */
void isp_leave_programming_mode(isp_driver_t *drv) {
    if (!drv) return;
    gpio_set_sck(false);
    gpio_set_mosi(false);
    gpio_set_reset(true); /* RESET = High -> старт виконання програми */
    drv->in_prog_mode = false;
    delay_ms(20);
}
