#include <cstdint>

namespace Diag {

struct alignas(4) NetDiagMetrics {
    uint32_t tcp_retrans_total{0};
    uint32_t socket_econnreset_count{0};
    uint32_t socket_etimedout_count{0};
    uint32_t dns_lookup_time_ms_last{0};
    uint32_t dns_lookup_failures{0};
    uint32_t tls_handshake_failures{0};
    uint16_t pbuf_pool_free_min{0};      // High-water mark пулу LwIP
    uint32_t heap_free_bytes{0};         // Загальний обсяг вільної купи
    uint32_t heap_largest_free_block{0}; // Найбільший неперервний блок купи
};

} // namespace Diag
