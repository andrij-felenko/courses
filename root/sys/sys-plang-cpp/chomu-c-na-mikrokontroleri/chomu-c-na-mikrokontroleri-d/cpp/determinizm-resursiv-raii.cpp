// Критична секція мовою C++ із гарантованим деструктором
#include <cstdint>
#include <optional>

class [[nodiscard]] InterruptLock {
public:
    InterruptLock() noexcept {
        asm volatile ("mrs %0, primask\ncpsid i" : "=r"(primask_) :: "memory");
    }

    ~InterruptLock() noexcept {
        asm volatile ("msr primask, %0" :: "r"(primask_) : "memory");
    }

    InterruptLock(const InterruptLock&) = delete;
    InterruptLock& operator=(const InterruptLock&) = delete;

private:
    uint32_t primask_{0};
};

std::optional<uint32_t> process_sensor_cpp(int sensor_id) noexcept {
    InterruptLock lock; // Переривання заблоковано

    if (sensor_id < 0) {
        return std::nullopt; // Деструктор lock відпрацює автоматично!
    }

    uint32_t val = *reinterpret_cast<volatile uint32_t*>(0x40001000UL);
    return val; // Деструктор lock відпрацює автоматично!
}
