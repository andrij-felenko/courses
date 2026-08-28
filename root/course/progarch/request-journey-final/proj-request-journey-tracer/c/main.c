/* C Implementation: Manual context extraction, struct layout, stack allocation */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

#define TRACE_ID_HEX_LEN 32
#define SPAN_ID_HEX_LEN  16

typedef struct {
    char trace_id[TRACE_ID_HEX_LEN + 1];
    char parent_span_id[SPAN_ID_HEX_LEN + 1];
    char current_span_id[SPAN_ID_HEX_LEN + 1];
    bool sampled;
} TraceContext;

typedef struct {
    char user_id[64];
    char home_id[64];
    char lock_id[64];
    TraceContext trace;
} UnlockCommand;

typedef struct {
    char lock_id[64];
    char desired_state[16];
    char reported_state[16];
    int version;
} DeviceTwin;

typedef struct {
    long id;
    char aggregate_id[64];
    char event_type[32];
    char payload_json[256];
    char trace_id[TRACE_ID_HEX_LEN + 1];
    char span_id[SPAN_ID_HEX_LEN + 1];
} OutboxEvent;

/* W3C Traceparent parser: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01 */
bool parse_traceparent(const char* header, TraceContext* ctx) {
    if (!header || strlen(header) < 55 || header[0] != '0' || header[1] != '0') {
        return false;
    }
    if (header[2] != '-' || header[35] != '-' || header[52] != '-') {
        return false;
    }

    strncpy(ctx->trace_id, header + 3, TRACE_ID_HEX_LEN);
    ctx->trace_id[TRACE_ID_HEX_LEN] = '\0';

    strncpy(ctx->parent_span_id, header + 36, SPAN_ID_HEX_LEN);
    ctx->parent_span_id[SPAN_ID_HEX_LEN] = '\0';

    /* Generate new span ID for current layer */
    snprintf(ctx->current_span_id, sizeof(ctx->current_span_id), "a1b2c3d4e5f67890");
    ctx->sampled = (header[54] == '1');

    return true;
}

bool db_execute_transaction(const DeviceTwin* twin, const OutboxEvent* event) {
    printf("[DB TX BEGIN]\n");
    printf("  UPDATE device_twins SET desired_state='%s', version=%d WHERE id='%s';\n",
           twin->desired_state, twin->version, twin->lock_id);
    printf("  INSERT INTO outbox_messages (aggregate_id, event_type, payload, trace_id, span_id)\n");
    printf("  VALUES ('%s', '%s', '%s', '%s', '%s');\n",
           event->aggregate_id, event->event_type, event->payload_json,
           event->trace_id, event->span_id);
    printf("[DB TX COMMIT] Success\n");
    return true;
}

bool handle_unlock_request(const char* traceparent_hdr, const char* lock_id, const char* user_id) {
    TraceContext trace_ctx;
    if (!parse_traceparent(traceparent_hdr, &trace_ctx)) {
        printf("Error: Invalid traceparent header\n");
        return false;
    }

    printf("[Trace: %s] Handling unlock for lock %s by user %s\n",
           trace_ctx.trace_id, lock_id, user_id);

    /* Load Aggregate */
    DeviceTwin twin = { .version = 1 };
    strncpy(twin.lock_id, lock_id, sizeof(twin.lock_id) - 1);
    strcpy(twin.reported_state, "LOCKED");
    strcpy(twin.desired_state, "UNLOCKED");
    twin.version += 1;

    /* Build Outbox Event */
    OutboxEvent event = {
        .id = 1001,
        .event_type = "LockUnlockCommanded"
    };
    strncpy(event.aggregate_id, lock_id, sizeof(event.aggregate_id) - 1);
    snprintf(event.payload_json, sizeof(event.payload_json),
             "{\"lock_id\":\"%s\",\"desired\":\"UNLOCKED\",\"user_id\":\"%s\"}", lock_id, user_id);
    strncpy(event.trace_id, trace_ctx.trace_id, sizeof(event.trace_id) - 1);
    strncpy(event.span_id, trace_ctx.current_span_id, sizeof(event.span_id) - 1);

    /* Commit DB Transaction */
    return db_execute_transaction(&twin, &event);
}

int main(void) {
    const char* hdr = "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01";
    handle_unlock_request(hdr, "lock_front_door", "user_alex_123");
    return 0;
}
