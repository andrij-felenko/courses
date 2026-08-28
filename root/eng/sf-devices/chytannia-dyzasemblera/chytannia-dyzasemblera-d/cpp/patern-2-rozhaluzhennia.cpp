#include <cstdint>

enum class Command : uint8_t {
    Ping  = 0,
    Data  = 1,
    Ack   = 2,
    Reset = 3
};

void handle_packet(Command cmd) {
    switch (cmd) {
        case Command::Ping:  process_ping(); break;
        case Command::Data:  process_data(); break;
        case Command::Ack:   process_ack();  break;
        case Command::Reset: process_reset(); break;
        default:             process_error(); break;
    }
}
