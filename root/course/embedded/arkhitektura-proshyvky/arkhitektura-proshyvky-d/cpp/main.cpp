// main.cpp — Головний диспетчер у C++
int main() {
    board::init();
    services::EventQueue<32> queue;
    app::Coordinator coordinator;

    while (true) {
        if (auto evt = queue.pop()) {
            coordinator.dispatch(*evt);
        } else {
            asm volatile("wfi"); // Перехід ядра Cortex-M у сон
        }
    }
}
