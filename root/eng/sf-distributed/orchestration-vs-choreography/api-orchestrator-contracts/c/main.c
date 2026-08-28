#include <stdint.h>
#include <stdbool.h>

typedef struct {
    char step_id[64];
    char activity_name[64];
    char queue_name[64];
    uint32_t timeout_seconds;
    uint32_t heartbeat_timeout_seconds;
    uint32_t max_retries;
    double backoff_coefficient;
    bool is_compensation;
} ActivityMetadata;

typedef struct {
    char execution_id[64];
    char workflow_id[64];
    uint32_t attempt_number;
    const char *payload_json;
    size_t payload_len;
} ActivityTaskContext;
