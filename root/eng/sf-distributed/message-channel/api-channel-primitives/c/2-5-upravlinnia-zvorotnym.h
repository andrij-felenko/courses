typedef enum {
    FLOW_CONTROL_RESUME = 0,     // Відновити прийом нових пакетів
    FLOW_CONTROL_PAUSE  = 1      // Призупинити продюсерів (активувати зворотний тиск)
} flow_signal_t;

typedef struct {
    uint64_t messages_sent;      // Загальна кількість успішно надісланих повідомлень
    uint64_t messages_received;  // Загальна кількість вичитаних повідомлень
    uint64_t bytes_transferred;  // Загальний обсяг переданих даних
    uint32_t current_depth;      // Поточна кількість елементів у буфері
    uint32_t waiting_producers;  // Кількість заблокованих потоків-відправників
    uint32_t waiting_consumers;  // Кількість заблокованих потоків-отримувачів
    uint64_t high_watermark_hits;// Лічильник спрацювань зворотного тиску
} channel_metrics_t;

int channel_set_flow(msg_channel_t *chan, flow_signal_t signal);
int channel_get_metrics(const msg_channel_t *chan, channel_metrics_t *metrics_out);
