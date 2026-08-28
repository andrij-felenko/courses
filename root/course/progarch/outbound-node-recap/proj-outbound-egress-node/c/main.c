#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <stdbool.h>

typedef enum { CB_CLOSED, CB_OPEN, CB_HALF_OPEN } cb_state_t;

typedef struct {
    cb_state_t state;
    int failure_count;
    int threshold;
    time_t next_attempt_time;
    int reset_timeout_sec;
} circuit_breaker_t;

typedef struct {
    char id[64];
    char url[256];
    char payload[1024];
    int attempt;
    int max_attempts;
} outbound_msg_t;

void cb_init(circuit_breaker_t* cb, int threshold, int reset_sec) {
    cb->state = CB_CLOSED;
    cb->failure_count = 0;
    cb->threshold = threshold;
    cb->next_attempt_time = 0;
    cb->reset_timeout_sec = reset_sec;
}

bool cb_can_execute(circuit_breaker_t* cb, time_t now) {
    if (cb->state == CB_OPEN) {
        if (now >= cb->next_attempt_time) {
            cb->state = CB_HALF_OPEN;
            return true;
        }
        return false;
    }
    return true;
}

void cb_on_success(circuit_breaker_t* cb) {
    cb->failure_count = 0;
    cb->state = CB_CLOSED;
}

void cb_on_failure(circuit_breaker_t* cb, time_t now) {
    cb->failure_count++;
    if (cb->failure_count >= cb->threshold) {
        cb->state = CB_OPEN;
        cb->next_attempt_time = now + cb->reset_timeout_sec;
    }
}

const char* process_outbound_msg(circuit_breaker_t* cb, outbound_msg_t* msg, int (*transport_fn)(const char*, const char*)) {
    time_t now = time(NULL);
    if (!cb_can_execute(cb, now)) {
        return "RETRY";
    }

    int status = transport_fn(msg->url, msg->payload);
    if (status >= 200 && status < 300) {
        cb_on_success(cb);
        return "SENT";
    }
    if (status >= 400 && status < 500 && status != 429) {
        return "DLQ";
    }

    cb_on_failure(cb, time(NULL));
    if (msg->attempt + 1 >= msg->max_attempts) {
        return "DLQ";
    }
    return "RETRY";
}
