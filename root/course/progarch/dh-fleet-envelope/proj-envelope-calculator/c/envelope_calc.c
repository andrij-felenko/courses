/* envelope_calc.c - C implementation of DH Capacity Calculator */
#include <stdio.h>
#include <stdint.h>
#include <math.h>

typedef struct {
    uint64_t fleet_size;           /* Кількість пристроїв (наприклад, 200000) */
    double   telemetry_interval_s; /* Інтервал між повідомленнями у секундах (30.0) */
    uint32_t payload_bytes;        /* Розмір корисної телеметрії у байтах (500) */
    double   peak_multiplier;      /* Коефіцієнт піку (3.0) */
    double   reconnect_window_s;   /* Вікно реконекту при блекаут штормі (60.0) */
    double   reconnect_fraction;   /* Частка пристроїв у реконекті (0.50) */
    double   tls_resumption_rate;  /* Частка скористанних TLS Session Tickets (0.80) */
} fleet_config_t;

typedef struct {
    double   msg_rate_steady;     /* msg/s у штатному режимі */
    double   msg_rate_peak;       /* msg/s у вечірній пік */
    double   ram_sockets_gb;      /* Пам'ять під TCP/TLS сесії у GB */
    double   net_bandwidth_mbps;  /* Мережева смуга у Mbps */
    double   cpu_crypto_cores;    /* Необхідні ядра CPU під TLS хендшейки у пік */
    double   cpu_parse_cores;     /* Необхідні ядра CPU під парсинг Protobuf */
    uint32_t iops_raw;            /* IOPS без батчингу */
    uint32_t iops_batched;        /* IOPS з батчингом (100 ms) */
    double   storage_gb_per_day;  /* Добовий обсяг збереження у GB */
} capacity_report_t;

void calculate_capacity(const fleet_config_t* cfg, capacity_report_t* out) {
    /* 1. Інтенсивність повідомлень */
    out->msg_rate_steady = (double)cfg->fleet_size / cfg->telemetry_interval_s;
    out->msg_rate_peak   = out->msg_rate_steady * cfg->peak_multiplier;

    /* 2. Пам'ять (48 KB на з'єднання: 16K kernel rx/tx + 16K TLS + 16K app state) */
    const double bytes_per_session = 48.0 * 1024.0;
    out->ram_sockets_gb = ((double)cfg->fleet_size * bytes_per_session) / (1024.0 * 1024.0 * 1024.0);

    /* 3. Мережева смуга (корисне навантаження + 107B оверхед L2-L4/TLS) */
    const double frame_bytes = (double)cfg->payload_bytes + 107.0;
    out->net_bandwidth_mbps = (out->msg_rate_peak * frame_bytes * 8.0) / 1000000.0;

    /* 4. CPU для TLS-хендшейків під час реконект шторму */
    double reconnect_events = (double)cfg->fleet_size * cfg->reconnect_fraction;
    double handshakes_per_sec = reconnect_events / cfg->reconnect_window_s;

    double full_handshake_ms = 0.60;
    double resume_handshake_ms = 0.05;

    double avg_handshake_ms = (handshakes_per_sec * (1.0 - cfg->tls_resumption_rate) * full_handshake_ms) +
                              (handshakes_per_sec * cfg->tls_resumption_rate * resume_handshake_ms);
    out->cpu_crypto_cores = avg_handshake_ms / 1000.0;

    /* 5. CPU для парсингу евентів (припустимо 5 µs на Protobuf декодування) */
    out->cpu_parse_cores = (out->msg_rate_peak * 0.000005);

    /* 6. Дискові IOPS та обсяг зберігання */
    out->iops_raw = (uint32_t)out->msg_rate_peak;
    out->iops_batched = 10; /* 100 ms flush window = 10 IOPS */

    double daily_bytes = out->msg_rate_steady * 86400.0 * (double)cfg->payload_bytes;
    out->storage_gb_per_day = daily_bytes / (1024.0 * 1024.0 * 1024.0);
}

int main(void) {
    fleet_config_t cfg = {
        .fleet_size = 200000,
        .telemetry_interval_s = 30.0,
        .payload_bytes = 500,
        .peak_multiplier = 3.0,
        .reconnect_window_s = 60.0,
        .reconnect_fraction = 0.50,
        .tls_resumption_rate = 0.80
    };

    capacity_report_t rep;
    calculate_capacity(&cfg, &rep);

    printf("=== DH Fleet Capacity Report (200k devices) ===\n");
    printf("Steady Msg Rate:   %.1f msg/s\n", rep.msg_rate_steady);
    printf("Peak Msg Rate:     %.1f msg/s\n", rep.msg_rate_peak);
    printf("RAM Sockets State: %.2f GB\n", rep.ram_sockets_gb);
    printf("Peak Bandwidth:    %.2f Mbps\n", rep.net_bandwidth_mbps);
    printf("TLS Crypto Cores:  %.2f cores\n", rep.cpu_crypto_cores);
    printf("Event Parse Cores: %.2f cores\n", rep.cpu_parse_cores);
    printf("Raw Disk IOPS:     %u IOPS\n", rep.iops_raw);
    printf("Batched Disk IOPS: %u IOPS\n", rep.iops_batched);
    printf("Storage Growth:    %.2f GB/day\n", rep.storage_gb_per_day);

    return 0;
}
