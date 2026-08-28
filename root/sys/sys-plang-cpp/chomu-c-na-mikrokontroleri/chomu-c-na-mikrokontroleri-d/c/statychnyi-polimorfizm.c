/* Поліморфізм мовою C через структури з покажчиками на функції */
#include <stdint.h>

typedef struct {
    void (*write_byte)(uint8_t data);
    uint8_t (*read_byte)(void);
} BusInterface_C;

void send_packet_c(const BusInterface_C* bus, const uint8_t* data, uint32_t len) {
    for (uint32_t i = 0; i < len; ++i) {
        /* Непрямий виклик через вказівник у RAM: процесор не може виконати інлайнінг */
        bus->write_byte(data[i]);
    }
}
