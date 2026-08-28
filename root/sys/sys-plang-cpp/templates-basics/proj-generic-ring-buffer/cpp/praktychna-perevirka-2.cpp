void test_lazy_compilation() {
    // 1. Успішна компіляція для HardwareFrame:
    RingBuffer<HardwareFrame, 32> telemetry_queue;
    telemetry_queue.emplace(101, 0xA4F2, 42.001);
    telemetry_queue.emplace(102, 0x11B0, 42.002);

    auto frame = telemetry_queue.pop();
    if (frame) {
        std::cout << "Отримано апаратний кадр #" << frame->packet_id << "\n";
    }

    // Компілятор успішно інстанціює emplace, pop, деструктор.
    // Метод dump() НЕ викликається, тому компілятор не перевіряє operator<<.

    // 2. Якщо розкоментувати наступний рядок, трансляція зупиниться з помилкою:
    // telemetry_queue.dump("Telemetry");
    // [error: no match for 'operator<<' (operand types are 'std::ostream' and 'HardwareFrame')]
}
