typedef enum {
    UPLOAD_STATE_IDLE,
    UPLOAD_STATE_CREATING,
    UPLOAD_STATE_WRITING,
    UPLOAD_STATE_CLOSING,
    UPLOAD_STATE_SUCCESS,
    UPLOAD_STATE_FAILED
} upload_state_t;

typedef struct {
    upload_state_t state;
    uint8_t        session;
    uint16_t       next_seq;
    const uint8_t *file_data;
    size_t         total_size;
    size_t         bytes_written;
    uint32_t       retry_count;
} mavftp_uploader_t;

void mavftp_uploader_start(mavftp_uploader_t *u, const char *remote_path, const uint8_t *data, size_t size, mavftp_pkt_t *out_req) {
    memset(u, 0, sizeof(*u));
    u->state = UPLOAD_STATE_CREATING;
    u->file_data = data;
    u->total_size = size;
    mavftp_build_create_file(out_req, ++u->next_seq, remote_path);
}

void mavftp_uploader_on_packet(mavftp_uploader_t *u, const mavftp_pkt_t *pkt, mavftp_pkt_t *out_req, bool *has_req) {
    *has_req = false;

    if (pkt->opcode == MAVFTP_OP_NAK) {
        printf("[MAVFTP-UP] Помилка NAK: %u під час запису\n", pkt->data[0]);
        u->state = UPLOAD_STATE_FAILED;
        return;
    }

    if (pkt->opcode != MAVFTP_OP_ACK) return;

    switch (u->state) {
    case UPLOAD_STATE_CREATING:
        if (pkt->req_opcode == MAVFTP_OP_CREATE_FILE) {
            u->session = pkt->session;
            u->state = UPLOAD_STATE_WRITING;
            u->bytes_written = 0;

            /* Відправка першого блоку даних */
            size_t chunk = u->total_size - u->bytes_written;
            if (chunk > MAVFTP_MAX_DATA_LEN) chunk = MAVFTP_MAX_DATA_LEN;

            mavftp_build_write_file(out_req, ++u->next_seq, u->session, 0, u->file_data, (uint8_t)chunk);
            *has_req = true;
        }
        break;

    case UPLOAD_STATE_WRITING:
        if (pkt->req_opcode == MAVFTP_OP_WRITE_FILE) {
            size_t last_chunk = u->total_size - u->bytes_written;
            if (last_chunk > MAVFTP_MAX_DATA_LEN) last_chunk = MAVFTP_MAX_DATA_LEN;
            u->bytes_written += last_chunk;

            if (u->bytes_written < u->total_size) {
                /* Відправка наступного фрагмента */
                size_t next_chunk = u->total_size - u->bytes_written;
                if (next_chunk > MAVFTP_MAX_DATA_LEN) next_chunk = MAVFTP_MAX_DATA_LEN;

                mavftp_build_write_file(out_req, ++u->next_seq, u->session, (uint32_t)u->bytes_written,
                                        u->file_data + u->bytes_written, (uint8_t)next_chunk);
                *has_req = true;
            } else {
                /* Запис завершено, закриваємо сесію */
                u->state = UPLOAD_STATE_CLOSING;
                mavftp_build_terminate(out_req, ++u->next_seq, u->session);
                *has_req = true;
            }
        }
        break;

    case UPLOAD_STATE_CLOSING:
        if (pkt->req_opcode == MAVFTP_OP_TERMINATE_SESSION) {
            u->state = UPLOAD_STATE_SUCCESS;
            printf("[MAVFTP-UP] Файл успішно завантажено на борт (%zu байтів)\n", u->total_size);
        }
        break;

    default:
        break;
    }
}
