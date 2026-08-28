#include <stdint.h>

void handle_packet(uint8_t cmd) {
    switch (cmd) {
        case 0:  process_ping(); break;
        case 1:  process_data(); break;
        case 2:  process_ack();  break;
        case 3:  process_reset(); break;
        default: process_error(); break;
    }
}
