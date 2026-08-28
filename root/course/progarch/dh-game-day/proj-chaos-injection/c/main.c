#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>
#include <unistd.h>

typedef struct {
    int latency_ms;
    int error_rate_percent;
    bool is_ready;
} chaos_config_t;

int process_request_c(const chaos_config_t* cfg, const char* target_header, const char* input, char* output, size_t max_len) {
    if (target_header != NULL && strcmp(target_header, "twin-cache") == 0) {
        if (cfg->latency_ms > 0) {
            usleep(cfg->latency_ms * 1000);
        }
        if (cfg->error_rate_percent > 0) {
            if ((rand() % 100) < cfg->error_rate_percent) {
                return 500; // Simulated Internal Server Error
            }
        }
    }
    snprintf(output, max_len, "%s", input);
    return 200;
}

bool check_liveness_c(void) {
    return true;
}

bool check_readiness_c(const chaos_config_t* cfg) {
    return cfg->is_ready;
}
