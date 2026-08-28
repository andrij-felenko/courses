#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <math.h>

/* Структура параметрів лінії зв'язку */
typedef struct {
    const char *name;              /* Назва інтерфейсу */
    double symbol_rate_baud;       /* Бодова швидкість (Baud) на одній лінії */
    uint32_t modulation_states_m;  /* Кількість станів модуляції M */
    uint32_t num_lanes;            /* Кількість паралельних ліній/пар */
    uint32_t line_code_k;          /* Корисні біти лінійного коду (наприклад, 8) */
    uint32_t line_code_n;          /* Повні біти лінійного коду (наприклад, 10) */
    uint32_t fec_k;                /* Інформаційні біти FEC (наприклад, 5) */
    uint32_t fec_n;                /* Повні біти FEC блоку (наприклад, 6) */
    uint32_t payload_bytes;        /* Байти корисного навантаження в пакеті */
    uint32_t header_bytes;         /* Байти заголовків усіх протокольних рівнів */
    uint32_t overhead_bytes;       /* Додаткові накладні витрати (CRC, преамбула, паузи) */
    double analog_bandwidth_hz;    /* Аналогова смуга каналу (для спектральної ефективності) */
} link_config_t;

/* Структура результатів розрахунку */
typedef struct {
    double bits_per_symbol;        /* k = log2(M) */
    double raw_bitrate_bps;        /* Фізичний бітрейт лінії */
    double gross_bitrate_bps;      /* Бітрейт після лінійного коду */
    double net_bitrate_bps;        /* Бітрейт після виправлення помилок FEC */
    double goodput_bps;            /* Корисна швидкість застосунку */
    double protocol_efficiency;    /* Goodput / Raw_Bitrate у відсотках */
    double spectral_efficiency;    /* Goodput / Смуга у біт/с/Гц */
} link_metrics_t;

/* Обчислення швидкостей каналу */
bool calculate_link_metrics(const link_config_t *cfg, link_metrics_t *out) {
    if (!cfg || !out) return false;
    if (cfg->symbol_rate_baud <= 0.0 || cfg->modulation_states_m < 2) return false;
    if (cfg->num_lanes == 0 || cfg->line_code_n == 0 || cfg->fec_n == 0) return false;

    /* 1. Кількість бітів на один символ */
    out->bits_per_symbol = log2((double)cfg->modulation_states_m);

    /* 2. Сирий бітрейт лінії */
    out->raw_bitrate_bps = cfg->symbol_rate_baud * out->bits_per_symbol * (double)cfg->num_lanes;

    /* 3. Брутто-бітрейт (після вирахування надлишковості лінійного коду) */
    double line_code_ratio = (double)cfg->line_code_k / (double)cfg->line_code_n;
    out->gross_bitrate_bps = out->raw_bitrate_bps * line_code_ratio;

    /* 4. Нетто-бітрейт (після вирахування надлишковості завадостійкого коду) */
    double fec_ratio = (double)cfg->fec_k / (double)cfg->fec_n;
    out->net_bitrate_bps = out->gross_bitrate_bps * fec_ratio;

    /* 5. Корисний бітрейт (Goodput) */
    uint32_t total_packet_bytes = cfg->payload_bytes + cfg->header_bytes + cfg->overhead_bytes;
    if (total_packet_bytes == 0) return false;

    double packet_efficiency = (double)cfg->payload_bytes / (double)total_packet_bytes;
    out->goodput_bps = out->net_bitrate_bps * packet_efficiency;

    /* 6. Загальна ефективність використання фізичної лінії */
    out->protocol_efficiency = (out->goodput_bps / out->raw_bitrate_bps) * 100.0;

    /* 7. Спектральна ефективність */
    if (cfg->analog_bandwidth_hz > 0.0) {
        out->spectral_efficiency = out->goodput_bps / cfg->analog_bandwidth_hz;
    } else {
        out->spectral_efficiency = 0.0;
    }

    return true;
}

/* Друк звіту розрахунку */
void print_link_report(const link_config_t *cfg, const link_metrics_t *m) {
    printf("==================================================================\n");
    printf(" ЗВІТ ШВИДКОСТЕЙ КАНАЛУ: %s\n", cfg->name);
    printf("==================================================================\n");
    printf(" Бодова швидкість (на лінію) : %12.2f бод (%.2f Мбод)\n",
           cfg->symbol_rate_baud, cfg->symbol_rate_baud / 1e6);
    printf(" Модуляція (M станів)        : %12u (k = %.2f біт/символ)\n",
           cfg->modulation_states_m, m->bits_per_symbol);
    printf(" Кількість ліній / потоків   : %12u\n", cfg->num_lanes);
    printf("------------------------------------------------------------------\n");
    printf(" 1. Сирий бітрейт (Raw Rate) : %12.2f Мбіт/с (%8.2f Мбайт/с)\n",
           m->raw_bitrate_bps / 1e6, m->raw_bitrate_bps / 8e6);
    printf(" 2. Брутто бітрейт (Gross)   : %12.2f Мбіт/с (код %u/%u)\n",
           m->gross_bitrate_bps / 1e6, cfg->line_code_k, cfg->line_code_n);
    printf(" 3. Нетто бітрейт (Net FEC)  : %12.2f Мбіт/с (FEC %u/%u)\n",
           m->net_bitrate_bps / 1e6, cfg->fec_k, cfg->fec_n);
    printf(" 4. Корисний Goodput         : %12.2f Мбіт/с (%8.2f Мбайт/с)\n",
           m->goodput_bps / 1e6, m->goodput_bps / 8e6);
    printf("------------------------------------------------------------------\n");
    printf(" Підсумковий ККД лінії       : %11.2f %%\n", m->protocol_efficiency);
    if (m->spectral_efficiency > 0.0) {
        printf(" Спектральна ефективність    : %11.2f біт/с/Гц\n", m->spectral_efficiency);
    }
    printf("==================================================================\n\n");
}

int main(void) {
    link_config_t interfaces[] = {
        /* 1. UART 115200 8N1 (1 старт, 8 даних, 1 стоп = 10 біт на кадр) */
        {
            .name = "UART RS-232 (115200 8N1)",
            .symbol_rate_baud = 115200.0,
            .modulation_states_m = 2,       /* 2-PAM / NRZ */
            .num_lanes = 1,
            .line_code_k = 1, .line_code_n = 1,
            .fec_k = 1, .fec_n = 1,
            .payload_bytes = 8,             /* 8 біт даних */
            .header_bytes = 1,              /* 1 старт-біт (еквівалент) */
            .overhead_bytes = 1,            /* 1 стоп-біт (еквівалент) */
            .analog_bandwidth_hz = 57600.0
        },
        /* 2. 1000BASE-T Gigabit Ethernet (4 виті пари по 125 Мбод, 4-PAM, MTU 1500) */
        {
            .name = "Ethernet 1000BASE-T (Cat5e, MTU 1500)",
            .symbol_rate_baud = 125000000.0,
            .modulation_states_m = 4,       /* 4-PAM (2 біти/символ) */
            .num_lanes = 4,                 /* 4 виті пари */
            .line_code_k = 1, .line_code_n = 1,
            .fec_k = 1, .fec_n = 1,         /* Trellis закладено в 5-й рівень PAM-5 */
            .payload_bytes = 1500,          /* MTU IP */
            .header_bytes = 14 + 20 + 20,   /* Ethernet(14) + IP(20) + TCP(20) */
            .overhead_bytes = 8 + 4 + 12,   /* Преамбула(8) + FCS(4) + IFG(12) */
            .analog_bandwidth_hz = 62500000.0 * 4.0
        },
        /* 3. PCI Express 6.0 x4 (32 Гбод, PAM-4, FLIT-пакети) */
        {
            .name = "PCIe 6.0 x4 (32 Гбод PAM-4 FLIT)",
            .symbol_rate_baud = 32000000000.0,
            .modulation_states_m = 4,       /* PAM-4 (2 біти/символ) */
            .num_lanes = 4,                 /* 4 лінії */
            .line_code_k = 1, .line_code_n = 1,
            .fec_k = 242, .fec_n = 256,     /* FLIT FEC захист */
            .payload_bytes = 216,           /* TLP дані у FLIT 256B */
            .header_bytes = 16,             /* Заголовки FLIT */
            .overhead_bytes = 10,           /* CRC та службові байти */
            .analog_bandwidth_hz = 16000000000.0 * 4.0
        },
        /* 4. Wi-Fi 6 (802.11ax, 80 МГц, 1024-QAM, 1 SS, FEC 5/6) */
        {
            .name = "Wi-Fi 6 (802.11ax, 80 МГц, 1024-QAM, 1 SS)",
            .symbol_rate_baud = 72058823.5, /* Сумарний символ-рейт 980 піднесучих */
            .modulation_states_m = 1024,    /* 1024-QAM (10 бітів/символ) */
            .num_lanes = 1,
            .line_code_k = 1, .line_code_n = 1,
            .fec_k = 5, .fec_n = 6,         /* LDPC кодова швидкість 5/6 */
            .payload_bytes = 1460,          /* TCP payload */
            .header_bytes = 24 + 20 + 20,   /* 802.11 MAC + IP + TCP */
            .overhead_bytes = 4 + 40,       /* FCS + A-MPDU / ACK накладні витрати */
            .analog_bandwidth_hz = 80000000.0
        }
    };

    size_t count = sizeof(interfaces) / sizeof(interfaces[0]);
    for (size_t i = 0; i < count; ++i) {
        link_metrics_t metrics;
        if (calculate_link_metrics(&interfaces[i], &metrics)) {
            print_link_report(&interfaces[i], &metrics);
        }
    }

    return 0;
}
