struct tcp_info {
    uint8_t   tcpi_state;           /* Стан TCP з'єднання (TCP_ESTABLISHED, TCP_SYN_SENT тощо) */
    uint8_t   tcpi_ca_state;        /* Стан автомата заторів (TCP_CA_Open, TCP_CA_Disorder, TCP_CA_Recovery, TCP_CA_Loss) */
    uint8_t   tcpi_retransmits;     /* Кількість послідовних незавершених повторних передач */
    uint8_t   tcpi_probes;          /* Кількість надісланих зондувальних пакетів keepalive */
    uint8_t   tcpi_backoff;         /* Ступінь експоненціального відкату таймера RTO */
    uint8_t   tcpi_options;         /* Прапорці активних опцій TCP (Window Scale, SACK, Timestamps) */
    uint8_t   tcpi_snd_wscale : 4,  /* Масштаб вікна відправника (Window Scaling Factor) */
              tcpi_rcv_wscale : 4;  /* Масштаб вікна приймача (Window Scaling Factor) */

    uint32_t  tcpi_rto;             /* Поточне значення тайм-ауту RTO (у мікросекундах) */
    uint32_t  tcpi_ato;             /* Затримка відкладеного підтвердження ACK (у μs) */
    uint32_t  tcpi_snd_mss;         /* Максимальний розмір сегмента відправника (MSS у байтах) */
    uint32_t  tcpi_rcv_mss;         /* Максимальний розмір сегмента приймача (MSS у байтах) */

    uint32_t  tcpi_unacked;         /* Кількість пакетів у польоті, ще не підтверджених ACK */
    uint32_t  tcpi_sacked;          /* Кількість пакетів, підтверджених через вибірковий SACK */
    uint32_t  tcpi_lost;            /* Кількість пакетів, позначених як втрачені у мережі */
    uint32_t  tcpi_retrans;         /* Кількість повторно надісланих пакетів, що перебувають у польоті */
    uint32_t  tcpi_fackets;         /* Кількість пакетів між найвищим SACK та розривом */

    /* Динамічні часові позначки */
    uint32_t  tcpi_last_data_sent;  /* Час із моменту відправки останнього пакета даних (мс) */
    uint32_t  tcpi_last_ack_sent;   /* Час із моменту відправки останнього ACK (мс) */
    uint32_t  tcpi_last_data_recv;  /* Час із моменту отримання останнього пакета даних (мс) */
    uint32_t  tcpi_last_ack_recv;   /* Час із моменту отримання останнього ACK (мс) */

    uint32_t  tcpi_pmtu;            /* Визначений Path MTU для сокета */
    uint32_t  tcpi_rcv_ssthresh;    /* Поріг ssthresh приймача */
    uint32_t  tcpi_rtt;             /* Середній RTT у мікросекундах (μs) */
    uint32_t  tcpi_rttvar;          /* Варіація RTT (дисперсія затримки) у μs */
    uint32_t  tcpi_snd_ssthresh;    /* Поточний поріг ssthresh у сегментах MSS */
    uint32_t  tcpi_snd_cwnd;        /* Поточний розмір вікна заторів cwnd (у сегментах MSS) */
    uint32_t  tcpi_advmss;          /* Анонсований MSS */
    uint32_t  tcpi_reordering;      /* Поріг переупорядкування пакетів */

    uint32_t  tcpi_rcv_rtt;         /* RTT приймача (μs) */
    uint32_t  tcpi_rcv_space;       /* Поточний обсяг приймального буфера */

    uint32_t  tcpi_total_retrans;   /* Загальна кількість повторів за весь час життя з'єднання */

    uint64_t  tcpi_pacing_rate;     /* Поточна швидкість пейсингу (байтів на секунду) */
    uint64_t  tcpi_max_pacing_rate; /* Максимальна дозволена швидкість пейсингу */
    uint64_t  tcpi_bytes_acked;     /* Загальна кількість підтверджених байтів даних */
    uint64_t  tcpi_bytes_received;  /* Загальна кількість прийнятих байтів даних */
    uint32_t  tcpi_notsent_bytes;   /* Обсяг даних у буфері запису, ще не надісланих у мережу */
    uint32_t  tcpi_min_rtt;         /* Мінімальний виміряний RTT (чистий RTprop) у μs */
    uint32_t  tcpi_data_segs_in;    /* Загальна кількість вхідних сегментів із даними */
    uint32_t  tcpi_data_segs_out;   /* Загальна кількість вихідних сегментів із даними */

    uint64_t  tcpi_delivery_rate;   /* Виміряна швидкість доставки BBR (байтів на секунду) */
};
