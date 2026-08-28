#include <stdint.h>

typedef struct {
    int32_t raw_value;
} HandleC;

HandleC make_handle_c(int32_t v) {
    HandleC h = { v };
    return h;
}
