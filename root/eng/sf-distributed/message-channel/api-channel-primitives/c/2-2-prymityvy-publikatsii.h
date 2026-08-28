typedef struct {
    const void *payload;         // Вказівник на бінарні дані повідомлення
    size_t length;               // Довжина даних у байтах
    uint64_t correlation_id;     // Ідентифікатор запиту для зв'язування відповіді
    uint32_t message_type;       // Ідентифікатор схеми (Datatype Channel ID)
    uint32_t flags;              // Прапорці доставки (наприклад, PERSISTENT, URGENT)
} message_t;

int channel_send(msg_channel_t *chan, const message_t *msg);
int channel_try_send(msg_channel_t *chan, const message_t *msg);
int channel_send_timeout(msg_channel_t *chan, const message_t *msg, uint32_t timeout_ms);
