// Ідіоматичний C++ RAII-вартовий для апаратного строб-піна
struct ScopedDebugPin {
    ScopedDebugPin() noexcept {
        GPIOA->BSRR = GPIO_BSRR_BS0; // GPIO0 = HIGH
    }
    ~ScopedDebugPin() noexcept {
        GPIOA->BSRR = GPIO_BSRR_BR0; // GPIO0 = LOW при виході з області видимості
    }
    ScopedDebugPin(const ScopedDebugPin&) = delete;
    ScopedDebugPin& operator=(const ScopedDebugPin&) = delete;
};

// Використання:
{
    const ScopedDebugPin strobe{};
    flash_sector_erase(SECTOR_4);
} // Автоматичне скидання піна навіть при ранньому return чи винятку
