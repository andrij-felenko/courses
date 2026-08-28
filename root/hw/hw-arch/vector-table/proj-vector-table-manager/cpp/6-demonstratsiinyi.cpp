#include "vector_table_types.h"

namespace {

constexpr int16_t demo_tim3_irqn = 29;
constexpr uintptr_t tim3_sr_addr = 0x40000410;

volatile uint32_t g_event_counter = 0;
volatile bool g_fault_triggered = false;

void dynamic_tim3_callback() noexcept {
    g_event_counter++;
    auto* const tim3_sr = reinterpret_cast<volatile uint32_t*>(tim3_sr_addr);
    *tim3_sr = 0;
}

} // namespace

extern "C" void MemManage_Handler() noexcept {
    g_fault_triggered = true;
    auto* const cfsr = reinterpret_cast<volatile uint32_t*>(0xE000ED28);
    *cfsr = 0xFF;
}

int main() {
    auto& manager = vtm::vector_manager::instance();

    // 1. Ініціалізація та релокація в SRAM
    if (auto init_res = manager.initialize(); !init_res) {
        while (true) { asm volatile ("bkpt #0"); }
    }

    // 2. Реєстрація хука обробника TIM3
    auto prev_isr = manager.register_handler(demo_tim3_irqn, dynamic_tim3_callback);
    if (!prev_isr) {
        while (true) { asm volatile ("bkpt #0"); }
    }

    // 3. Очікування 500 подій
    while (g_event_counter < 500) {
        asm volatile ("wfi");
    }

    // 4. Перевірка спрацювання MPU
    auto* const table_ptr = reinterpret_cast<volatile uint32_t*>(manager.get_table_address());
    *table_ptr = 0xDEADBEEFUL; // Викликає MemManage Fault

    // 5. Відновлення стандартного вектора
    if (auto unreg_res = manager.unregister_handler(demo_tim3_irqn); !unreg_res) {
        while (true) { asm volatile ("bkpt #0"); }
    }

    while (true) {
        asm volatile ("wfi");
    }
}
