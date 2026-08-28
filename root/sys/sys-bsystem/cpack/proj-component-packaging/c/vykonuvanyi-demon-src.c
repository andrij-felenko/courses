#include "telemetry/metrics.h"
#include <stdio.h>
#include <unistd.h>

int main(void) {
    printf("Starting Telemetry Daemon v1.4.2...\n");
    telemetry_snapshot_t snapshot;
    char buffer[256];

    for (int i = 0; i < 3; ++i) {
        if (telemetry_collect_metrics(&snapshot) == 0) {
            telemetry_format_json(&snapshot, buffer, sizeof(buffer));
            fputs(buffer, stdout);
        }
        sleep(1);
    }
    return 0;
}
