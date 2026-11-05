#include <Arduino.h>

class DigimaticDriver {
private:
    uint8_t pin_clock;
    uint8_t pin_data;
    uint8_t pin_req;
    
    volatile uint64_t raw_buffer = 0;
    volatile uint8_t bit_count = 0;
    volatile bool data_ready = false;

    // Статичний метод для використання як ISR
    static void isr_handler(void* instance) {
        DigimaticDriver* dev = static_cast<DigimaticDriver*>(instance);
        uint8_t bit = digitalRead(dev->pin_data);
        dev->raw_buffer |= ((uint64_t)bit << dev->bit_count);
        dev->bit_count++;
        
        if (dev->bit_count >= 52) {
            dev->data_ready = true;
            dev->bit_count = 0;
        }
    }

public:
    DigimaticDriver(uint8_t clock, uint8_t data, uint8_t req) 
        : pin_clock(clock), pin_data(data), pin_req(req) {}
        
    void begin() {
        pinMode(pin_clock, INPUT_PULLUP);
        pinMode(pin_data, INPUT_PULLUP);
        pinMode(pin_req, OUTPUT);
        
        // Ардуїно вимагає глобальної функції для переривання
        attachInterrupt(digitalPinToInterrupt(pin_clock), 
                        reinterpret_cast<void(*)()>(&DigimaticDriver::isr_handler), 
                        FALLING);
    }
};
