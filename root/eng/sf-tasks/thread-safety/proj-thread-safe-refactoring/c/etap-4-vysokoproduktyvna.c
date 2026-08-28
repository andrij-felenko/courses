#include <stdint.h>

/* Локальні змінні потоку в секції TLS */
static _Thread_local uint64_t tls_thread_bytes = 0;
static _Thread_local uint64_t tls_thread_errors = 0;

void tls_metrics_record(int status_code, uint64_t bytes) {
    tls_thread_bytes += bytes;
    if (status_code >= 400) {
        tls_thread_errors++;
    }
}

void tls_metrics_get_local(uint64_t *out_bytes, uint64_t *out_errors) {
    if (out_bytes != NULL) *out_bytes = tls_thread_bytes;
    if (out_errors != NULL) *out_errors = tls_thread_errors;
}
