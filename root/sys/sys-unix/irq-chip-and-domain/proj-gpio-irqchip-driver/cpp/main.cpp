#include <iostream>
#include <vector>
#include <array>
#include <memory>
#include <mutex>
#include <functional>
#include <cstdint>

namespace gpio_driver {

constexpr uint32_t GPIO_DATA_IN   = 0x00;
constexpr uint32_t GPIO_DIR       = 0x04;
constexpr uint32_t GPIO_INT_MASK  = 0x08;
constexpr uint32_t GPIO_INT_STAT  = 0x0C;
constexpr uint32_t GPIO_INT_TYPE  = 0x10;
constexpr size_t NR_PINS          = 32;

struct GpioRegisters {
    uint32_t data_in{};
    uint32_t dir{};
    uint32_t int_mask{p};
    uint32_t int_stat{0};
    uint32_t int_type{0};
};

class GpioIrqChip {
public:
    explicit GpioIrqChip(int parent_irq) : parent_irq_(parent_irq) {
        handlers_.fill(nullptr);
    }

    void mask(uint32_t pin) {
        std::lock_guard<std::mutex> lock(mutex_);
        if (pin < NR_PINS) regs_.int_mask &= ~(1U << pin);
    }

    void unmask(uint32_t pin) {
        std::lock_guard<std::mutex> lock(mutex_);
        if (pin < NR_PINS) regs_.int_mask |= (1U << pin);
    }

    void ack(uint32_t pin) {
        std::lock_guard<std::mutex> lock(mutex_);
        if (pin < NR_PINS) regs_.int_stat &= ~(1U << pin);
    }

    int set_type(uint32_t pin, uint32_t type) {
        std::lock_guard<std::mutex> lock(mutex_);
        if (pin >= NR_PINS) return -1;
        if (type == 1) regs_.int_type |= (1U << pin);
        else regs_.int_type &= ~(1U << pin);
        return 0;
    }

    void register_handler(uint32_t pin, std::function<void(uint32_t)> handler) {
        std::lock_guard<std::mutex> lock(mutex_);
        if (pin < NR_PINS) handlers_[pin] = std::move(handler);
    }

    void dispatch_chained_irq() {
        std::lock_guard<std::mutex> lock(mutex_);
        uint32_t pending = regs_.int_stat & regs_.int_mask;
        for (uint32_t pin = 0; pin < NR_PINS; ++pin) {
            if (pending & (1U << pin)) {
                if (handlers_[pin]) handlers_[pin](pin);
                regs_.int_stat &= ~(1U << pin);
            }
        }
    }

    void simulate_pin_event(uint32_t pin) {
        std::lock_guard<std::mutex> lock(mutex_);
        if (pin < NR_PINS) regs_.int_stat |= (1U << pin);
    }

private:
    int parent_irq_{0};
    mutable std::mutex mutex_;
    GpioRegisters regs_{};
    std::array<std::function<void(uint32_t), NR_PINS> handlers_{};
};

} // namespace gpio_driver

int main() {
    auto chip = std::make_unique<gpio_driver::GpioIrqChip>(42);
    chip->unmask(5);
    chip->register_handler(5, [](uint32_t pin) {
        std::cout << "GPIO IRQ fired on pin: " << pin << std::endl;
    });

    chip->simulate_pin_event(5);
    chip->dispatch_chained_irq();

    return 0;
}
