// fuzz_parser.c — fuzz-ціль для libFuzzer
#include <stdint.h>
#include <stddef.h>

int parse_frame(const uint8_t *data, size_t size);

// libFuzzer викликає цю функцію, підставляючи у (data, size) мутований вхід
int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
    parse_frame(data, size);   // просто згодовуємо вхід функції під тестом
    return 0;                  // 0 — «вхід оброблено»; аварію зловить санітайзер
}
