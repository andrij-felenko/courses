typedef struct msg_channel msg_channel_t;

typedef struct {
    size_t capacity;              // Максимальна кількість елементів у буфері (0 для Rendezvous)
    size_t max_message_size;      // Максимальний розмір корисного навантаження (байтів)
    uint32_t flags;               // Бітові прапорці конфігурації
    uint32_t watermark_high;      // Поріг активації зворотного тиску (кількість msg)
    uint32_t watermark_low;       // Поріг відновлення прийому даних
} channel_config_t;

int channel_open(msg_channel_t **chan_out, const channel_config_t *config);
int channel_close(msg_channel_t *chan);
int channel_destroy(msg_channel_t *chan);
