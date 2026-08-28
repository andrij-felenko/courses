#include <avr/io.h>
#include <avr/interrupt.h>
#include <cstdint>

void disable_jtag_runtime() noexcept {
    const uint8_t sreg = SREG;
    cli();
    
    // Атомарна часова послідовність запису в регістр MCUCR
    const uint8_t mcucr_val = MCUCR | static_cast<uint8_t>(1 << JTD);
    MCUCR = mcucr_val;
    MCUCR = mcucr_val;
    
    SREG = sreg;
}
