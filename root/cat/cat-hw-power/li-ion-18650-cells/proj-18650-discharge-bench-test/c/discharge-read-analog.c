// Зчитування аналогових сигналів напруги й струму та аварійна відсічка навантаження при досягненні критичної температури чи порогової напруги
#include <avr/io.h>
#include <util/delay.h>

#define VOLTAGE_PIN ADC0
#define CURRENT_PIN ADC1
#define TEMP_PIN    ADC2
#define CUTOFF_VOLTAGE 2750 // 2.75V in mV
#define CUTOFF_TEMP    60   // 60 Celsius

void adc_init() {
    ADMUX = (1 << REFS0);
    ADCSRA = (1 << ADEN) | (1 << ADPS2) | (1 << ADPS1) | (1 << ADPS0);
}

uint16_t adc_read(uint8_t ch) {
    ADMUX = (ADMUX & 0xF0) | (ch & 0x0F);
    ADCSRA |= (1 << ADSC);
    while (ADCSRA & (1 << ADSC));
    return ADC;
}

void check_safety_and_read() {
    uint16_t mv = adc_read(0) * (5000UL / 1024UL); 
    uint16_t temp = adc_read(2); 
    uint8_t current_temp = (temp * 500) / 1024; // спрощений розрахунок LM35

    if (mv < CUTOFF_VOLTAGE || current_temp >= CUTOFF_TEMP) {
        PORTB &= ~(1 << PB0); // Відключення навантаження (реле або MOSFET)
    }
}
