#include <stdio.h>
#include <string.h>

typedef struct {
    int rst_cause;
    int gpio15;
    int gpio0;
    int gpio2;
} esp_boot_status_t;

bool parse_rom_log(const char *log, esp_boot_status_t *out_status) {
    int raw_boot = 0;
    if (sscanf(log, "rst cause:%d, bootmode:(%*d,%d)", &out_status->rst_cause, &raw_boot) == 2) {
        out_status->gpio15 = (raw_boot >> 2) & 1;
        out_status->gpio0  = (raw_boot >> 1) & 1;
        out_status->gpio2  = raw_boot & 1;
        return true;
    }
    return false;
}
