typedef struct {
    void *payload;               // Виділений буфер для запису отриманих даних
    size_t buffer_capacity;      // Доступна місткість буфера отримувача
    size_t received_length;      // Реальна довжина прочитаного повідомлення
    uint64_t correlation_id;     // Скопійований correlation_id відправника
    uint32_t message_type;       // Отриманий ідентифікатор типу даних
    uint64_t timestamp_ns;       // Часова мітка збереження в каналі (UNIX epoch ns)
} message_recv_t;

int channel_recv(msg_channel_t *chan, message_recv_t *msg_out);
int channel_try_recv(msg_channel_t *chan, message_recv_t *msg_out);
int channel_recv_timeout(msg_channel_t *chan, message_recv_t *msg_out, uint32_t timeout_ms);
