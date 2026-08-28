#include <stdio.h>
#include <stdlib.h>

typedef enum {
    CLIENT_STATE_IDLE,
    CLIENT_STATE_OPENING,
    CLIENT_STATE_BURST_STREAMING,
    CLIENT_STATE_GAP_RECOVERY,
    CLIENT_STATE_CLOSING,
    CLIENT_STATE_VERIFY_CRC,
    CLIENT_STATE_SUCCESS,
    CLIENT_STATE_FAILED
} client_state_t;

typedef struct {
    client_state_t state;
    uint8_t        session;
    uint16_t       next_seq;
    uint16_t       expected_burst_seq;
    uint32_t       file_size;
    uint32_t       bytes_received;
    uint8_t       *file_buffer;
    size_t         buffer_capacity;
    uint32_t       remote_crc;
    char           remote_path[MAVFTP_MAX_DATA_LEN];
    uint32_t       retry_count;
    uint32_t       max_retries;
} mavftp_client_t;

/* Ініціалізація клієнта */
bool mavftp_client_init(mavftp_client_t *c, size_t max_file_size) {
    memset(c, 0, sizeof(*c));
    c->state = CLIENT_STATE_IDLE;
    c->max_retries = 5;
    c->buffer_capacity = max_file_size;
    c->file_buffer = (uint8_t *)malloc(max_file_size);
    return (c->file_buffer != NULL);
}

void mavftp_client_free(mavftp_client_t *c) {
    if (c->file_buffer) {
        free(c->file_buffer);
        c->file_buffer = NULL;
    }
}

/* Старт завантаження */
void mavftp_client_start(mavftp_client_t *c, const char *path, mavftp_pkt_t *out_req) {
    c->state = CLIENT_STATE_OPENING;
    c->bytes_received = 0;
    c->file_size = 0;
    c->retry_count = 0;
    strncpy(c->remote_path, path, sizeof(c->remote_path) - 1);
    c->remote_path[sizeof(c->remote_path) - 1] = '\0';
    mavftp_build_open_ro(out_req, ++c->next_seq, path);
}

/* Обробка вхідного пакета MAVFTP */
void mavftp_client_on_packet(mavftp_client_t *c, const mavftp_pkt_t *pkt, mavftp_pkt_t *out_reply, bool *has_reply) {
    *has_reply = false;
    uint16_t seq = le16(pkt->seq_number);
    uint32_t off = le32(pkt->offset);

    /* Обробка негативного підтвердження NAK */
    if (pkt->opcode == MAVFTP_OP_NAK) {
        uint8_t err = pkt->data[0];
        if (err == MAVFTP_ERR_EOF && c->state == CLIENT_STATE_BURST_STREAMING) {
            /* Досягнуто кінця файлу через NAK(EOF) — переходимо до закриття */
            c->state = CLIENT_STATE_CLOSING;
            mavftp_build_terminate(out_reply, ++c->next_seq, c->session);
            *has_reply = true;
            return;
        }
        printf("[MAVFTP] NAK помилка: %u, операція: %u\n", err, pkt->req_opcode);
        c->state = CLIENT_STATE_FAILED;
        return;
    }

    if (pkt->opcode != MAVFTP_OP_ACK) {
        return;
    }

    switch (c->state) {
    case CLIENT_STATE_OPENING:
        if (pkt->req_opcode == MAVFTP_OP_OPEN_FILE_RO) {
            c->session = pkt->session;
            if (pkt->size >= 4) {
                uint32_t sz;
                memcpy(&sz, pkt->data, 4);
                c->file_size = le32(sz);
            }
            printf("[MAVFTP] Сесію відкрито: ID=%u, розмір=%u байтів\n", c->session, c->file_size);

            /* Запуск пакетного вичитування */
            c->state = CLIENT_STATE_BURST_STREAMING;
            c->bytes_received = 0;
            c->expected_burst_seq = seq + 1;
            c->retry_count = 0;

            mavftp_build_burst_read(out_reply, ++c->next_seq, c->session, 0);
            *has_reply = true;
        }
        break;

    case CLIENT_STATE_BURST_STREAMING:
    case CLIENT_STATE_GAP_RECOVERY:
        if (pkt->req_opcode == MAVFTP_OP_BURST_READ_FILE || pkt->req_opcode == MAVFTP_OP_READ_FILE) {
            /* Перевірка послідовності номерів пакетів */
            if (c->state == CLIENT_STATE_BURST_STREAMING && seq != c->expected_burst_seq) {
                printf("[MAVFTP] Пропуск! Очікували seq=%u, прийшов seq=%u. Відновлюємо з offset=%u\n",
                       c->expected_burst_seq, seq, c->bytes_received);
                c->state = CLIENT_STATE_GAP_RECOVERY;
                c->retry_count++;
                if (c->retry_count > c->max_retries) {
                    c->state = CLIENT_STATE_FAILED;
                    return;
                }
                mavftp_build_burst_read(out_reply, ++c->next_seq, c->session, c->bytes_received);
                *has_reply = true;
                return;
            }

            /* Збереження отриманого блоку */
            if (off == c->bytes_received && (c->bytes_received + pkt->size) <= c->buffer_capacity) {
                memcpy(c->file_buffer + off, pkt->data, pkt->size);
                c->bytes_received += pkt->size;
                c->expected_burst_seq = seq + 1;
                c->state = CLIENT_STATE_BURST_STREAMING;
                c->retry_count = 0;
            }

            /* Перевірка фінішу потоку */
            if (pkt->burst_complete == 1 || (c->file_size > 0 && c->bytes_received >= c->file_size)) {
                printf("[MAVFTP] Завантаження завершено (%u байтів). Закриваємо сесію...\n", c->bytes_received);
                c->state = CLIENT_STATE_CLOSING;
                mavftp_build_terminate(out_reply, ++c->next_seq, c->session);
                *has_reply = true;
            }
        }
        break;

    case CLIENT_STATE_CLOSING:
        if (pkt->req_opcode == MAVFTP_OP_TERMINATE_SESSION) {
            printf("[MAVFTP] Сесію закрито. Запитуємо CRC32 файлу...\n");
            c->state = CLIENT_STATE_VERIFY_CRC;
            mavftp_build_calc_crc32(out_reply, ++c->next_seq, c->remote_path);
            *has_reply = true;
        }
        break;

    case CLIENT_STATE_VERIFY_CRC:
        if (pkt->req_opcode == MAVFTP_OP_CALC_FILE_CRC32 && pkt->size == 4) {
            uint32_t remote_crc;
            memcpy(&remote_crc, pkt->data, 4);
            c->remote_crc = le32(remote_crc);

            uint32_t local_crc = mavftp_crc32(c->file_buffer, c->bytes_received);
            if (local_crc == c->remote_crc) {
                printf("[MAVFTP] CRC32 збігається: 0x%08X. Успіх!\n", local_crc);
                c->state = CLIENT_STATE_SUCCESS;
            } else {
                printf("[MAVFTP] Помилка CRC: локальний 0x%08X != віддалений 0x%08X\n", local_crc, c->remote_crc);
                c->state = CLIENT_STATE_FAILED;
            }
        }
        break;

    default:
        break;
    }
}
