#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    char refdes[16];
    char pin[8];
    char net_name[32];
    double x_mm;
    double y_mm;
} eda_pin_record_t;

void filter_net_pins(const eda_pin_record_t *records, size_t count, const char *target_net) {
    printf("Pins connected to net [%s]:\n", target_net);
    for (size_t i = 0; i < count; ++i) {
        if (strncmp(records[i].net_name, target_net, sizeof(records[i].net_name)) == 0) {
            printf("  Node %s.%s at (%.2f, %.2f) mm\n",
                   records[i].refdes, records[i].pin,
                   records[i].x_mm, records[i].y_mm);
        }
    }
}

int main(void) {
    eda_pin_record_t pins[] = {
        {"U1", "14", "VCC_3V3", 10.50, 20.00},
        {"C1", "1",  "VCC_3V3", 12.00, 19.50},
        {"R1", "2",  "VCC_3V3", 15.20, 22.10},
        {"U1", "7",  "GND",     10.50, 27.00},
        {"C1", "2",  "GND",     12.00, 26.50}
    };
    size_t count = sizeof(pins) / sizeof(pins[0]);
    filter_net_pins(pins, count, "VCC_3V3");
    return 0;
}
