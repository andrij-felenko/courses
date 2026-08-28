#include <avr/io.h>
#include <avr/interrupt.h>

void disable_jtag_runtime(void) {
    uint8_t sreg = SREG;
    cli(); // Забороняємо переривання, щоб не порушити 4-тактове вікно
    
    // Запис 1 у біт JTD двічі поспіль протягом 4 тактів
    MCUCR |= (1 << JTD);
    MCUCR |= (1 << JTD);
    
    SREG = sreg; // Відновлюємо стан переривань
}
