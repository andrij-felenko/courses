// Шаблонна генерація затримок на етапі компіляції.
// Повністю розгортає послідовність NOP без накладних витрат виклику циклу.
template <uint32_t Cycles>
struct ExactDelay {
    __attribute__((always_inline)) static inline void wait() {
        __asm__ volatile ("nop");
        ExactDelay<Cycles - 1>::wait();
    }
};

template <>
struct ExactDelay<0> {
    __attribute__((always_inline)) static inline void wait() {}
};

// Розрахунок тактів із наносекунд для заданої частоти ядра процесора
constexpr uint32_t ns_to_cycles(uint32_t ns, uint32_t f_cpu_hz) {
    return static_cast<uint32_t>((static_cast<uint64_t>(ns) * f_cpu_hz) / 1000000000ULL);
}

// Функція формує рівно 24 такти для затримки 500 нс на частоті 48 MHz
inline void delay_500ns_at_48mhz() {
    constexpr uint32_t cycles = ns_to_cycles(500, 48000000);
    ExactDelay<cycles>::wait();
}
