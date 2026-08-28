#include <cstdint>

class StreamDriver {
public:
    virtual ~StreamDriver() = default;
    virtual void write(uint8_t byte) = 0;
    virtual uint8_t read() = 0;
protected:
    uint32_t buffer_size_{};
};

void send_byte(StreamDriver* dev, uint8_t b) {
    dev->write(b);
}
