#include <stdint.h>

struct goal_anomaly_telemetry_s {
    uint64_t timestamp_us;        /* Системний час мікроконтролера */
    float    input_metric_value;  /* Поточне значення вимірюваної метрики */
    uint16_t active_goal_id;      /* Ідентифікатор активної цілі місії */
    uint16_t suppressed_switches; /* Кількість заблокованих спроб перемикання */
    uint8_t  switching_rate_hz;   /* Поточна частота запитів на перемикання (Гц) */
    uint8_t  detected_cycle_len;  /* Довжина зафіксованого N-грамного циклу */
    uint8_t  escalation_level;    /* Поточний ступінь відновлення (0..4) */
    uint8_t  flags;               /* Бітові прапорці стану фільтра */
};
