#include <stdint.h>

typedef struct StreamDriver {
    const struct StreamDriverOps* ops;
    uint32_t buffer_size;
} StreamDriver;

typedef struct StreamDriverOps {
    void (*destructor)(StreamDriver* self);
    void (*write)(StreamDriver* self, uint8_t byte);
    uint8_t (*read)(StreamDriver* self);
} StreamDriverOps;

void send_byte(StreamDriver* dev, uint8_t b) {
    dev->ops->write(dev, b);
}
