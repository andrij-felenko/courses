// C99: Сигнатури низькорівневих шинних функцій зворотного виклику
#include <stdint.h>

typedef int32_t (*chip_bus_read_fn)(
    void *user_ctx,
    uint8_t reg_addr,
    uint8_t *data,
    uint16_t len
);

typedef int32_t (*chip_bus_write_fn)(
    void *user_ctx,
    uint8_t reg_addr,
    const uint8_t *data,
    uint16_t len
);

typedef void (*chip_delay_ms_fn)(
    uint32_t ms
);
