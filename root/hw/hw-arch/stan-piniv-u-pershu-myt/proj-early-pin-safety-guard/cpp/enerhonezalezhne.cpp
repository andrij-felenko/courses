// Збереження аварійного звіту засобами C++20 у бекап-регістри
inline void record_crash_dump(const DiagnosticReport& report, uintptr_t faulty_port_base) noexcept {
    // Дозвіл запису в домен Backup
    PWR->CR1 |= PWR_CR1_DBP;

    TAMP->BKP0R = 0xDEADBEEFUL;
    TAMP->BKP1R = static_cast<uint32_t>(report.status);
    TAMP->BKP2R = static_cast<uint32_t>(report.faulty_index);
    if (faulty_port_base != 0) {
        auto* port = reinterpret_cast<HardwareGpioPort*>(faulty_port_base);
        TAMP->BKP3R = port->IDR;
    }
}
