#include "startup.h"

/* Три змінні, кожна у своїй секції: перша несе початкове значення у
   Flash, дві інші в прошивці не займають жодного байта. */
int target_voltage = 3300;   /* .data */
int current_reading = 0;     /* .bss  */
uint8_t dma_buffer[16384];   /* .bss: 16 КБ, яких у прошивці немає */

int main(void)
{
    /* Перевіряємо, що стартовий код справді відпрацював. Якби .data не
       скопіювали з Flash, тут лежало б увімкнене сміття SRAM. */
    if (target_voltage != 3300) {
        startup_trap();
    }
    for (size_t i = 0; i < sizeof dma_buffer; ++i) {
        if (dma_buffer[i] != 0U) { /* .bss не занулено */
            startup_trap();
        }
    }

    /* Далі була б прикладна логіка; поки що — сон до переривання */
    for (;;) {
        current_reading = target_voltage;
        __asm volatile("wfi");
    }
}
