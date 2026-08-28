// Тестовий сценарій: перевірка переповнення FIFO з RAII-блокуванням на C++
#include <chrono>
#include <thread>
#include <cassert>

class InterruptLock {
public:
    InterruptLock() noexcept { maskGlobalInterrupts(true); }
    ~InterruptLock() noexcept { maskGlobalInterrupts(false); }
    InterruptLock(const InterruptLock&) = delete;
    InterruptLock& operator=(const InterruptLock&) = delete;
};

void testFifoStarvationCpp(SensorDriver& driver) {
    driver.setOutputDataRate(1600);
    {
        const InterruptLock lock;
        std::this_thread::sleep_for(std::chrono::milliseconds(500));
    }
    // Перевірка коректності детектування прапорця переповнення та очищення буфера
    const auto result = driver.recoverFromOverflow();
    assert(result.has_value());
}
