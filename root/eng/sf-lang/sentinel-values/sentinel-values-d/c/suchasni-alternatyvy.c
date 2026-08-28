#include <stdbool.h>
#include <stdint.h>

// Емуляція Option мовою C через структуру з прапорцем
typedef struct {
    bool has_value;
    uint32_t value;
} OptionalU32;

OptionalU32 lookup_id(const char* key) {
    if (key == NULL) {
        return (OptionalU32){ .has_value = false, .value = 0 };
    }
    return (OptionalU32){ .has_value = true, .value = 1001 };
}
