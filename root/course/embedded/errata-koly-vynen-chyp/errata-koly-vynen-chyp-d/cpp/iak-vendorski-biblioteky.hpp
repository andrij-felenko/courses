/* Ідіоматичний C++ RAII-блокувальник переривань для захисту таймінгу Errata */
struct CriticalSectionGuard {
    CriticalSectionGuard() noexcept { __disable_irq(); }
    ~CriticalSectionGuard() noexcept { __enable_irq(); }
    CriticalSectionGuard(const CriticalSectionGuard&) = delete;
    CriticalSectionGuard& operator=(const CriticalSectionGuard&) = delete;
};

void prepare_i2c_last_bytes(I2C_TypeDef* instance) noexcept {
    CriticalSectionGuard guard;
    instance->CR1 &= ~I2C_CR1_ACK;
    volatile uint32_t dummy = instance->SR1;
    dummy = instance->SR2;
    static_cast<void>(dummy);
    asm volatile("dsb" ::: "memory");
}
