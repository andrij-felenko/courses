typedef struct {
    uint32_t stream_index;        // Індекс треку, якому належить даний пакет
    uint8_t *data;                 // Буфер зі стисненим кадром (наприклад, NAL-одиниця)
    size_t size;                   // Розмір бувера у байтах
    int64_t pts;                   // Presentation Time Stamp (у тиках time_base)
    int64_t dts;                   // Decode Time Stamp (у тиках time_base)
    int64_t duration;              // Тривалість відтворення кадру у тиках
    uint32_t flags;                // Бітові прапорці стану пакета
} MediaPacket;

#define PACKET_FLAG_KEYFRAME (1 << 0)  // Пакет містить IDR / Ключовий кадр
#define PACKET_FLAG_CORRUPT  (1 << 1)  // Пакет містить виявлені завади каналу
