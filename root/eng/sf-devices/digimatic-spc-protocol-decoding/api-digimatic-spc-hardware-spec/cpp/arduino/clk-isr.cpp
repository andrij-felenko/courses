#include <Arduino.h>

const int PIN_CLK = 2;
const int PIN_DATA = 3;

volatile uint64_t current_packet = 0;
volatile int bit_count = 0;
volatile bool packet_ready = false;

void clk_isr() {
    int data_bit = !digitalRead(PIN_DATA);
    current_packet |= ((uint64_t)data_bit << bit_count);
    bit_count++;
    
    if (bit_count >= 52) {
        packet_ready = true;
        bit_count = 0;
    }
}
