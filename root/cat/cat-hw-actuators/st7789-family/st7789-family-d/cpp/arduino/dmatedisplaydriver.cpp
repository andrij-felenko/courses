// C++ (Arduino / Modern C++ DMA & TE Sync wrapper)
#include <Arduino.h>

class DmaTeDisplayDriver {
private:
    uint8_t te_pin;
    volatile bool frame_pending;
    const uint8_t* volatile active_buffer;
    size_t buffer_length;

public:
    DmaTeDisplayDriver(uint8_t tePin) 
        : te_pin(tePin), frame_pending(false), active_buffer(nullptr), buffer_length(0) {}

    void begin() {
        pinMode(te_pin, INPUT);
        attachInterruptParam(digitalPinToInterrupt(te_pin), onTeInterrupt, RISING, this);
    }

    void drawFrameDma(const uint8_t* buffer, size_t len) {
        active_buffer = buffer;
        buffer_length = len;
        frame_pending = true;
    }

private:
    static void ARDUINO_ISR_ATTR onTeInterrupt(void* arg) {
        auto* driver = static_cast<DmaTeDisplayDriver*>(arg);
        if (driver->frame_pending && driver->active_buffer != nullptr) {
            driver->startHardwareDmaTransfer(driver->active_buffer, driver->buffer_length);
            driver->frame_pending = false;
        }
    }

    void startHardwareDmaTransfer(const uint8_t* buf, size_t len) {
        // Низькорівневий виклик периферії SPI DMA
    }
};
