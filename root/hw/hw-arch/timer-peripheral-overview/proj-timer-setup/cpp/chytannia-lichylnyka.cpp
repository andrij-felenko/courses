// RAII блокування переривань у C++
struct irq_lock {
    uint8_t sreg = SREG;
    irq_lock() { cli(); }
    ~irq_lock() { SREG = sreg; }
};

uint16_t tcnt1_read() {
    irq_lock lock;
    return TCNT1;
}
