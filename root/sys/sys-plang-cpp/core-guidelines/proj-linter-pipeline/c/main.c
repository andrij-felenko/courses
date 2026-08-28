/* Процедурний C: ручна алокація, сирі вказівники, сигналізація через коди */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    double timestamp;
    float value;
    int status_flags;
} TelemetryPacket;

int filter_active_packets(const TelemetryPacket* input, int count, 
                          TelemetryPacket** output, int* out_count) {
    if (!input || count <= 0 || !output || !out_count) {
        return -1;
    }

    TelemetryPacket* buffer = (TelemetryPacket*)malloc(sizeof(TelemetryPacket) * count);
    if (!buffer) {
        return -2;
    }

    int active = 0;
    for (int i = 0; i < count; ++i) {
        if ((input[i].status_flags & 0x01) != 0) {
            buffer[active++] = input[i];
        }
    }

    *output = buffer;
    *out_count = active;
    printf("Extracted %d active packets\n", active);
    return 0;
}
