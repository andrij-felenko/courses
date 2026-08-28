namespace drivers {

struct UartDriver {
    static void init() noexcept {
        RCC->AHB1ENR |= RCC_AHB1ENR_GPIOAEN;
        GPIOA->MODER |= (2u << (9 * 2)) | (2u << (10 * 2));
        GPIOA->AFR[1] |= (7u << ((9 - 8) * 4)) | (7u << ((10 - 8) * 4));
    }
};

struct SpiDriver {
    static void init() noexcept {
        RCC->AHB1ENR |= RCC_AHB1ENR_GPIOAEN;
        GPIOA->MODER |= (2u << (5 * 2)) | (2u << (6 * 2)) | (2u << (7 * 2));
        GPIOA->AFR[0] |= (5u << (5 * 4)) | (5u << (6 * 4)) | (5u << (7 * 4));
    }
};

struct LedDriver {
    static void init() noexcept {
        RCC->AHB1ENR |= RCC_AHB1ENR_GPIOAEN;
        /* Помилка: затирає попередній стан регістра іншого модуля */
        GPIOA->MODER &= ~(3u << (9 * 2));
        GPIOA->MODER |= (1u << (9 * 2));
    }
};

} // namespace drivers
