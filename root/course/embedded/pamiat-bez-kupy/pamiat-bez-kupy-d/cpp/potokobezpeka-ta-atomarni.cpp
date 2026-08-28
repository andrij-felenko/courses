/* RAII-охорона переривань: автоматичне відновлення стану при виході з області */
struct InterruptLock {
    uint32_t primask{__get_PRIMASK()};
    InterruptLock() noexcept { __disable_irq(); }
    ~InterruptLock() noexcept { __set_PRIMASK(primask); }
    InterruptLock(const InterruptLock&) = delete;
    InterruptLock& operator=(const InterruptLock&) = delete;
};

// Безпечне використання у коді:
{
    InterruptLock lock;
    // Безпечна модифікація вільного списку пула
}
