#include <cstdint>

// Той самий шар, але ніжка — параметр типу: адреси регістрів і номер біта
// відомі компіляторові, тож кожен виклик згортається в одну інструкцію.
template <std::uintptr_t DDR, std::uintptr_t PORT, std::uintptr_t PIN, std::uint8_t BIT>
struct OpenDrainPin {
    static constexpr std::uint8_t mask = std::uint8_t(1u << BIT);

    static volatile std::uint8_t& reg(std::uintptr_t a) {
        return *reinterpret_cast<volatile std::uint8_t*>(a);
    }
    static void init()    { reg(PORT) &= ~mask; reg(DDR) &= ~mask; }
    static void low()     { reg(DDR)  |=  mask; }   // вихід із нулем у засувці
    static void release() { reg(DDR)  &= ~mask; }   // вхід: високий опір
    static bool read()    { return (reg(PIN) & mask) != 0; }
};

// ATmega328P: PINC = 0x26, DDRC = 0x27, PORTC = 0x28
using Sda = OpenDrainPin<0x27, 0x28, 0x26, 4>;
using Scl = OpenDrainPin<0x27, 0x28, 0x26, 5>;
