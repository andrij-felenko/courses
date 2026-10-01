#include "daplink_board.h"

// Глобальний екземпляр конфігурації порту
DAP_PortConfig_t g_dap_port_config = {
    .clock_speed_hz = 1000000U,
    .swdio_mode = SWDIO_MODE_OUTPUT_PP,
    .reset_active = false
};

// Ініціалізація виводів GPIO для інтерфейсу SWD на STM32F103
void gpio_driver_init(void) {
    // Вмикаємо тактування порту GPIOA через регістр RCC_APB2ENR (bit 2)
    RCC->APB2ENR |= (1U << 2);

    // Конфігурація CRL (Control Register Low) для PA5, PA6, PA7 (байти 20-31)
    // Маскуємо біти для PA5, PA6, PA7
    uint32_t crl = GPIOA->CRL;
    crl &= ~((0xFU << (PIN_SWCLK * 4)) | (0xFU << (PIN_SWDIO * 4)) | (0xFU << (PIN_NRESET * 4)));

    // PA5 (SWCLK): Output 50MHz Push-Pull -> MODE=11 (0x3), CNF=00 (0x0) => 0x3
    crl |= (0x3U << (PIN_SWCLK * 4));

    // PA6 (SWDIO): Output 50MHz Push-Pull початково -> MODE=11 (0x3), CNF=00 (0x0) => 0x3
    crl |= (0x3U << (PIN_SWDIO * 4));

    // PA7 (nRESET): Output 50MHz Open-Drain -> MODE=11 (0x3), CNF=01 (0x1) => 0x7
    crl |= (0x7U << (PIN_NRESET * 4));

    GPIOA->CRL = crl;

    // Встановлюємо початкові рівні: SWCLK=0, SWDIO=1, nRESET=1 (пасивний стан)
    SWCLK_LOW();
    SWDIO_HIGH();
    NRESET_HIGH();
}

// Динамічна зміна напрямку виводу SWDIO (Output Push-Pull vs Input Input Pull-Up)
void gpio_set_swdio_mode(SWDIO_Mode_t mode) {
    uint32_t crl = GPIOA->CRL;
    crl &= ~(0xFU << (PIN_SWDIO * 4));

    if (mode == SWDIO_MODE_OUTPUT_PP) {
        // Output 50MHz Push-Pull: MODE=11 (0x3), CNF=00 (0x0)
        crl |= (0x3U << (PIN_SWDIO * 4));
    } else {
        // Input Pull-Up / Floating: MODE=00 (0x0), CNF=10 (0x2)
        crl |= (0x8U << (PIN_SWDIO * 4));
        // Вмикаємо підтяжку до VCC через ODR
        SWDIO_HIGH();
    }

    GPIOA->CRL = crl;
    g_dap_port_config.swdio_mode = mode;
}

// Керування лінією апаратного скидання цільового мікроконтролера (nRESET)
void gpio_set_nreset(bool assert_reset) {
    if (assert_reset) {
        NRESET_LOW();
        g_dap_port_config.reset_active = true;
    } else {
        NRESET_HIGH();
        g_dap_port_config.reset_active = false;
    }
}
