/* Ідіоматична C++ RAII-обгортка для критичної секції */
class InterruptLock {
public:
    InterruptLock() noexcept {
        __disable_irq();
    }
    ~InterruptLock() noexcept {
        __enable_irq();
    }
    InterruptLock(const InterruptLock&) = delete;
    InterruptLock& operator=(const InterruptLock&) = delete;
};

void update_system_state() noexcept {
    InterruptLock lock; // Автоматичне блокування
    update_shared_resources();
} // Автоматичне розблокування при виході з області видимості
