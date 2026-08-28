#include <stdint.h>
#include <stdbool.h>

#define RCC_BASE        0x40023800U
#define RCC_CR          (*(volatile uint32_t *)(RCC_BASE + 0x00U))
#define RCC_CFGR        (*(volatile uint32_t *)(RCC_BASE + 0x08U))
#define RCC_AHB1ENR     (*(volatile uint32_t *)(RCC_BASE + 0x30U))
#define RCC_APB1ENR     (*(volatile uint32_t *)(RCC_BASE + 0x40U))

#define GPIOA_BASE      0x40020000U
#define GPIOA_MODER     (*(volatile uint32_t *)(GPIOA_BASE + 0x00U))
#define GPIOA_ODR       (*(volatile uint32_t *)(GPIOA_BASE + 0x14U))
#define GPIOA_BSRR      (*(volatile uint32_t *)(GPIOA_BASE + 0x18U))

#define I2C1_BASE       0x40005400U
#define I2C1_CR1        (*(volatile uint32_t *)(I2C1_BASE + 0x00U))
#define I2C1_CR2        (*(volatile uint32_t *)(I2C1_BASE + 0x04U))
#define I2C1_SR1        (*(volatile uint32_t *)(I2C1_BASE + 0x14U))
#define I2C1_SR2        (*(volatile uint32_t *)(I2C1_BASE + 0x18U))
#define I2C1_DR         (*(volatile uint32_t *)(I2C1_BASE + 0x10U))

#define RCC_CR_HSIRDY   (1U << 1)
#define RCC_CR_HSEON    (1U << 16)
#define RCC_CR_HSERDY   (1U << 17)
#define RCC_CR_PLLON    (1U << 24)
#define RCC_CR_PLLRDY   (1U << 25)

#define I2C_SR1_SB      (1U << 0)
#define I2C_SR1_ADDR    (1U << 1)
#define I2C_SR1_AF      (1U << 10)
#define I2C_CR1_START   (1U << 8)
#define I2C_CR1_STOP    (1U << 9)
#define I2C_CR1_PE      (1U << 0)

typedef enum {
    BRINGUP_OK = 0,
    BRINGUP_ERR_HSE_TIMEOUT,
    BRINGUP_ERR_PLL_TIMEOUT,
    BRINGUP_ERR_I2C_TIMEOUT,
    BRINGUP_ERR_I2C_NACK
} bringup_status_t;

typedef struct {
    bool hsi_ready;
    bool hse_ready;
    bool pll_ready;
    uint8_t i2c_devices_found;
} bringup_report_t;

static void delay_cycles(volatile uint32_t cycles) {
    while (cycles > 0) {
        cycles--;
    }
}

bringup_status_t bringup_clock_check(bringup_report_t *report) {
    report->hsi_ready = (RCC_CR & RCC_CR_HSIRDY) != 0;
    
    RCC_CR |= RCC_CR_HSEON;
    uint32_t timeout = 50000;
    while (!(RCC_CR & RCC_CR_HSERDY) && timeout > 0) {
        timeout--;
    }
    report->hse_ready = (timeout > 0);
    if (!report->hse_ready) {
        return BRINGUP_ERR_HSE_TIMEOUT;
    }

    report->pll_ready = (RCC_CR & RCC_CR_PLLRDY) != 0;
    return BRINGUP_OK;
}

void bringup_gpio_toggle_testpoints(uint32_t iterations) {
    RCC_AHB1ENR |= (1U << 0);
    
    GPIOA_MODER &= ~((3U << (5 * 2)) | (3U << (6 * 2)) | (3U << (7 * 2)));
    GPIOA_MODER |=  ((1U << (5 * 2)) | (1U << (6 * 2)) | (1U << (7 * 2)));

    for (uint32_t i = 0; i < iterations; ++i) {
        GPIOA_BSRR = (1U << 5) | (1U << 6) | (1U << 7);
        delay_cycles(1000);
        
        GPIOA_BSRR = (1U << (5 + 16)) | (1U << (6 + 16)) | (1U << (7 + 16));
        delay_cycles(1000);
    }
}

bringup_status_t bringup_i2c_probe_address(uint8_t addr_7bit) {
    I2C1_CR1 |= I2C_CR1_START;
    uint32_t timeout = 20000;
    while (!(I2C1_SR1 & I2C_SR1_SB) && timeout > 0) {
        timeout--;
    }
    if (timeout == 0) {
        I2C1_CR1 |= I2C_CR1_STOP;
        return BRINGUP_ERR_I2C_TIMEOUT;
    }

    I2C1_DR = (uint32_t)(addr_7bit << 1);
    timeout = 20000;
    while (!(I2C1_SR1 & (I2C_SR1_ADDR | I2C_SR1_AF)) && timeout > 0) {
        timeout--;
    }
    
    if (I2C1_SR1 & I2C_SR1_AF) {
        I2C1_SR1 &= ~I2C_SR1_AF;
        I2C1_CR1 |= I2C_CR1_STOP;
        return BRINGUP_ERR_I2C_NACK;
    }

    (void)I2C1_SR1;
    (void)I2C1_SR2;
    I2C1_CR1 |= I2C_CR1_STOP;
    return BRINGUP_OK;
}

uint8_t bringup_scan_i2c_bus(void) {
    uint8_t found = 0;
    for (uint8_t addr = 0x08; addr < 0x78; ++addr) {
        if (bringup_i2c_probe_address(addr) == BRINGUP_OK) {
            found++;
        }
        delay_cycles(500);
    }
    return found;
}
