typedef struct {
    int16_t  rssi_dbm;         /* Згладжена потужність сигналу (дБм) */
    int8_t   snr_db;           /* Відношення сигнал/шум (дБ) */
    uint8_t  per_percent;      /* Коефіцієнт пакетних втрат (0..100%) */
    uint16_t rtt_ms;           /* Кругова затримка (Round-Trip Time, мс) */
    uint32_t throughput_bps;   /* Поточна пропускна здатність (біт/с) */
    uint32_t last_rx_mono_ms;  /* Монотонний час останнього успішного прийому (мс) */
    uint8_t  composite_score;  /* Інтегральний бал якості (0..100) */
    bool     is_link_alive;    /* Прапорець фізичної доступності трансивера */
} bearer_metrics_t;
