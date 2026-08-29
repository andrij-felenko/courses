#ifndef LINK_STATS_H
#define LINK_STATS_H

#include <stdbool.h>
#include <stdint.h>

#define STATS_WINDOW 32u   /* ширина вікна втрат у кадрах */

/* Метрики одного носія. RSSI та SNR тримаємо у форматі Q8 (одиниця = 1/256 dBm):
   ціле арифметичне згладжування без жодної плаваючої крапки. */
typedef struct {
    int32_t  rssi_q8;
    int32_t  snr_q8;
    bool     seeded;            /* перший кадр задає фільтр, а не тягне його з нуля */
    uint32_t rx_packet_mask;       /* 1 = очікуваний кадр дійшов */
    uint32_t slot_deadline_ms;  /* коли чекати наступний кадр */
    uint16_t slot_ms;
    uint16_t last_seq;
    bool     have_seq;
    uint32_t last_rx_time;
    uint8_t  per_percent;
    uint8_t  score;
    uint32_t rx_total;
    uint32_t lost_total;
} link_stats_t;

void     link_stats_init(link_stats_t *s, uint16_t slot_ms, uint32_t now_ms);
/* Повертає, скільки кадрів загубилося перед цим (за розривом у seq). */
uint16_t link_stats_on_packet_rx(link_stats_t *s, uint16_t seq, int16_t rssi_dbm,
                          int8_t snr_db, uint32_t now_ms);
void     link_stats_on_tick(link_stats_t *s, uint32_t now_ms);
void     link_stats_resume(link_stats_t *s, uint32_t now_ms);  /* приймач знову слухає */
void     link_stats_reset(link_stats_t *s, uint32_t now_ms);   /* чиста сторінка вимірювання */
int16_t  link_stats_rssi_dbm(const link_stats_t *s);
int8_t   link_stats_snr_db(const link_stats_t *s);
uint32_t link_stats_silence_ms(const link_stats_t *s, uint32_t now_ms);

/* --- Ковзне вікно дедуплікації на приймачі ---------------------------------
   LoRa віддає кадр за 40..120 мс, Wi-Fi за 2..5 мс. Після перемикання старий
   кадр із резерву прилітає ПІСЛЯ свіжого з основного — і критичні команди ми
   ще й навмисно дублюємо в обидва носії. Вікно приймає спізнілий кадр, якого
   ще не бачили, і викидає повтор або надто старий номер. */
typedef struct {
    uint16_t newest_seq;
    uint32_t seen_mask;
    bool     primed;
    uint32_t duplicates;
    uint32_t too_old;
} dedup_window_t;

void dedup_init(dedup_window_t *d);
bool dedup_accept(dedup_window_t *d, uint16_t seq);

#endif /* LINK_STATS_H */
