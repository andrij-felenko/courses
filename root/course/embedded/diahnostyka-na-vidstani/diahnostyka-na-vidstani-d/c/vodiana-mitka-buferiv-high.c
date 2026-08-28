#include <stdint.h>

typedef struct {
    uint32_t tcp_retrans_total;
    uint32_t socket_econnreset_count;
    uint32_t socket_etimedout_count;
    uint32_t dns_lookup_time_ms_last;
    uint32_t dns_lookup_failures;
    uint32_t tls_handshake_failures;
    uint16_t pbuf_pool_free_min;      // High-water mark пулу LwIP
    uint32_t heap_free_bytes;         // Загальний обсяг вільної купи
    uint32_t heap_largest_free_block; // Найбільший неперервний блок купи
} net_diag_metrics_t;
