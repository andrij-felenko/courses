// Відкриття джерела та первинний розбір заголовків контейнера
int demuxer_open(const char *url, void **context);

// Отримання кількості знайдених треків у медіаконтейнері
uint32_t demuxer_get_stream_count(void *context);

// Зчитування параметрів конкретного треку за його індексом
int demuxer_get_stream_info(void *context, uint32_t stream_index, StreamInfo *info);

// Послідовне зчитування наступного пакета кадрів з контейнера
int demuxer_read_packet(void *context, MediaPacket *packet);

// Звільнення пам'яті пакета після завершення обробки в декодері
void demuxer_free_packet(MediaPacket *packet);

// Точне або ключове позиціонування за часовим штампом (Seek)
int demuxer_seek(void *context, uint32_t stream_index, int64_t target_pts, int flags);

// Закриття контейнера та повне звільнення усіх системних ресурсів
void demuxer_close(void *context);
