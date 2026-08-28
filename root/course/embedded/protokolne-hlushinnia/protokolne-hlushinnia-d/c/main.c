#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define SEC_LL_MAX_PAYLOAD       64
#define SEC_LL_TAG_SIZE          8
#define SEC_LL_REPLAY_WINDOW     32
#define SEC_LL_MAX_FAILURES      5
#define SEC_LL_CCA_TIMEOUT_TICKS 100

typedef enum {
    FRAME_TYPE_DATA       = 0x01,
    FRAME_TYPE_HEARTBEAT  = 0x02,
    FRAME_TYPE_DISCONNECT = 0x03, /* Захищений аналог Deauth */
    FRAME_TYPE_ACK        = 0x04
} sec_frame_type_t;

typedef enum {
    LINK_MODE_COOPERATIVE_CSMA = 0, /* Звичайний режим з перевіркою вільного каналу */
    LINK_MODE_FORCED_TX        = 1, /* Аварійний режим: ігнорування CCA, прямий постріл */
    LINK_MODE_CHANNEL_HOP      = 2  /* Активна зміна робочої частоти через глушіння */
} sec_link_mode_t;

/* Заголовок захищеного канального кадру (8 байтів) */
typedef struct __attribute__((packed)) {
    uint8_t  frame_type;
    uint8_t  src_id;
    uint8_t  dst_id;
    uint8_t  flags;
    uint32_t seq_num;
} sec_frame_header_t;

/* Повна структура кадру */
typedef struct __attribute__((packed)) {
    sec_frame_header_t header;
    uint8_t            payload[SEC_LL_MAX_PAYLOAD];
    uint8_t            payload_len;
    uint8_t            auth_tag[SEC_LL_TAG_SIZE];
} sec_packet_t;

/* Стан канального драйвера */
typedef struct {
    uint8_t         node_id;
    uint8_t         shared_key[16];
    uint32_t        tx_seq;
    uint32_t        rx_last_seq;
    uint32_t        replay_bitmask;
    
    sec_link_mode_t link_mode;
    uint16_t        attack_anomaly_counter;
    uint16_t        cca_block_counter;
    uint8_t         current_channel;
    bool            is_connected;
} sec_link_driver_t;

/* Спрощена імітація криптографічного тегу цілісності (Poly1305/CMAC) */
static void calculate_mac(const uint8_t *key, const uint8_t *data, size_t len, uint8_t *tag_out) {
    uint32_t hash = 0x811c9dc5;
    for (size_t i = 0; i < 16; i++) {
        hash = (hash ^ key[i]) * 0x01000193;
    }
    for (size_t i = 0; i < len; i++) {
        hash = (hash ^ data[i]) * 0x01000193;
    }
    /* Заповнюємо 8 байтів тегу */
    memcpy(tag_out, &hash, 4);
    hash = ~hash;
    memcpy(tag_out + 4, &hash, 4);
}

/* Ініціалізація драйвера */
void sec_link_init(sec_link_driver_t *drv, uint8_t node_id, const uint8_t key[16]) {
    memset(drv, 0, sizeof(sec_link_driver_t));
    drv->node_id = node_id;
    memcpy(drv->shared_key, key, 16);
    drv->link_mode = LINK_MODE_COOPERATIVE_CSMA;
    drv->current_channel = 1;
    drv->is_connected = true;
}

/* Перевірка захисту від повторів (Anti-Replay Sliding Window) */
static bool check_replay_window(sec_link_driver_t *drv, uint32_t seq) {
    if (seq > drv->rx_last_seq) {
        uint32_t diff = seq - drv->rx_last_seq;
        if (diff < SEC_LL_REPLAY_WINDOW) {
            drv->replay_bitmask <<= diff;
            drv->replay_bitmask |= 1;
        } else {
            drv->replay_bitmask = 1;
        }
        drv->rx_last_seq = seq;
        return true;
    }
    
    uint32_t diff = drv->rx_last_seq - seq;
    if (diff >= SEC_LL_REPLAY_WINDOW) {
        return false; /* Занадто старий пакет */
    }
    
    if (drv->replay_bitmask & (1UL << diff)) {
        return false; /* Цей номер уже був прийнятий */
    }
    
    drv->replay_bitmask |= (1UL << diff);
    return true;
}

/* Формування захищеного кадру для відправки */
int sec_link_build_packet(sec_link_driver_t *drv, uint8_t dst_id, sec_frame_type_t type,
                          const uint8_t *payload, uint8_t payload_len,
                          uint8_t *out_buf, size_t out_buf_max_len) {
    if (payload_len > SEC_LL_MAX_PAYLOAD) return -1;
    size_t total_size = sizeof(sec_frame_header_t) + payload_len + SEC_LL_TAG_SIZE;
    if (out_buf_max_len < total_size) return -2;

    sec_frame_header_t hdr;
    hdr.frame_type = (uint8_t)type;
    hdr.src_id = drv->node_id;
    hdr.dst_id = dst_id;
    hdr.flags = (uint8_t)drv->link_mode;
    hdr.seq_num = ++drv->tx_seq;

    memcpy(out_buf, &hdr, sizeof(sec_frame_header_t));
    if (payload_len > 0 && payload != NULL) {
        memcpy(out_buf + sizeof(sec_frame_header_t), payload, payload_len);
    }

    /* Рахуємо MAC над усім заголовком і тілом */
    uint8_t tag[SEC_LL_TAG_SIZE];
    calculate_mac(drv->shared_key, out_buf, sizeof(sec_frame_header_t) + payload_len, tag);
    memcpy(out_buf + sizeof(sec_frame_header_t) + payload_len, tag, SEC_LL_TAG_SIZE);

    return (int)total_size;
}

/* Обробка вхідного сирого кадру */
bool sec_link_process_rx(sec_link_driver_t *drv, const uint8_t *raw_data, size_t len,
                         uint8_t *payload_out, uint8_t *payload_len_out) {
    if (len < sizeof(sec_frame_header_t) + SEC_LL_TAG_SIZE) {
        drv->attack_anomaly_counter++;
        return false;
    }

    const sec_frame_header_t *hdr = (const sec_frame_header_t *)raw_data;
    size_t payload_len = len - sizeof(sec_frame_header_t) - SEC_LL_TAG_SIZE;
    const uint8_t *received_tag = raw_data + sizeof(sec_frame_header_t) + payload_len;

    /* 1. Криптографічна перевірка автентичності */
    uint8_t expected_tag[SEC_LL_TAG_SIZE];
    calculate_mac(drv->shared_key, raw_data, sizeof(sec_frame_header_t) + payload_len, expected_tag);

    if (memcmp(received_tag, expected_tag, SEC_LL_TAG_SIZE) != 0) {
        /* Пакет підроблено або спотворено */
        drv->attack_anomaly_counter++;
        if (drv->attack_anomaly_counter >= SEC_LL_MAX_FAILURES) {
            /* Виявлено атаку протокольного глушіння/спуфінгу -> Перемикаємо режим */
            drv->link_mode = LINK_MODE_FORCED_TX;
        }
        return false;
    }

    /* 2. Перевірка адресації */
    if (hdr->dst_id != drv->node_id && hdr->dst_id != 0xFF) {
        return false;
    }

    /* 3. Захист від Replay-атак */
    if (!check_replay_window(drv, hdr->seq_num)) {
        drv->attack_anomaly_counter++;
        return false;
    }

    /* 4. Обробка типу кадру */
    if (hdr->frame_type == FRAME_TYPE_DISCONNECT) {
        /* Валідно підписаний розрив сесії */
        drv->is_connected = false;
        return true;
    }

    if (payload_len > 0 && payload_out != NULL) {
        memcpy(payload_out, raw_data + sizeof(sec_frame_header_t), payload_len);
        *payload_len_out = (uint8_t)payload_len;
    }

    /* Успішний прийом валідного кадру знижує лічильник тривоги */
    if (drv->attack_anomaly_counter > 0) {
        drv->attack_anomaly_counter--;
    }

    return true;
}

/* Спроба передачі з контролем атак на рівні CCA */
bool sec_link_transmit(sec_link_driver_t *drv, const uint8_t *packet, size_t len,
                       bool (*radio_cca_check)(void), void (*radio_send)(const uint8_t *, size_t)) {
    if (drv->link_mode == LINK_MODE_COOPERATIVE_CSMA) {
        uint8_t attempts = 0;
        while (!radio_cca_check()) {
            attempts++;
            if (attempts > SEC_LL_CCA_TIMEOUT_TICKS) {
                /* Канал заблоковано через CCA Jamming! Переходимо в аварійний Forced TX */
                drv->cca_block_counter++;
                drv->link_mode = LINK_MODE_FORCED_TX;
                break;
            }
        }
    }

    /* Відправка пакета */
    radio_send(packet, len);

    if (drv->cca_block_counter > 10) {
        /* Тривале блокування: змінюємо радіочастотний канал */
        drv->current_channel = (drv->current_channel % 16) + 1;
        drv->cca_block_counter = 0;
        drv->link_mode = LINK_MODE_COOPERATIVE_CSMA;
    }

    return true;
}
