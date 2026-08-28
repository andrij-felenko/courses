// АНТИПАТЕРН: хибна абстракція через змішування деталей за прапорцем
typedef struct {
    uint8_t buf[128];
    size_t len;
    size_t expected_len;
    uint8_t state;
    uint8_t crc;
    bool is_gnss; // ← Прапорець типу джерела
} bad_framer_t;

bool bad_framer_feed(bad_framer_t* p, uint8_t byte, void (*cb)(const uint8_t*, size_t)) {
    if (p->is_gnss) {
        // Розгалуження для першого протоколу
        if (p->state == 0 && byte == 0xAA) p->state = 1;
        // ...
    } else {
        // Розгалуження для другого протоколу
        if (p->state == 0 && byte == 0x24) p->state = 1;
        // ...
    }
    return false;
}
