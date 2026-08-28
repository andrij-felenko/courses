#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define MAX_CHUNKS 64
#define STATIC_TABLE_SIZE 99

/* Спрощена статична таблиця QPACK (RFC 9204) */
typedef struct {
    const char *name;
    const char *value;
} qpack_static_entry_t;

static const qpack_static_entry_t QPACK_STATIC_TABLE[STATIC_TABLE_SIZE] = {
    [0]  = {":authority", ""},
    [1]  = {":path", "/"},
    [15] = {":method", "GET"},
    [17] = {":method", "POST"},
    [25] = {":status", "200"},
    [28] = {":status", "404"},
    [29] = {":status", "500"},
    [31] = {"accept-encoding", "gzip, deflate, br"},
    [45] = {"content-type", "application/json"},
    [95] = {"user-agent", "quic-client/1.0"}
};

/* Фрагмент запізненого або неупорядкованого пакета */
typedef struct {
    uint64_t offset;
    size_t length;
    uint8_t *data;
    bool used;
} stream_chunk_t;

/* Буфер дефрагментації окремого потоку QUIC */
typedef struct {
    uint64_t stream_id;
    uint64_t read_offset;
    uint64_t max_stream_data;
    bool fin_received;
    uint64_t final_size;
    stream_chunk_t chunks[MAX_CHUNKS];
    size_t chunk_count;
} quic_stream_t;

/* Ініціалізація нового потоку */
void quic_stream_init(quic_stream_t *stream, uint64_t stream_id, uint64_t max_data) {
    stream->stream_id = stream_id;
    stream->read_offset = 0;
    stream->max_stream_data = max_data;
    stream->fin_received = false;
    stream->final_size = 0;
    stream->chunk_count = 0;
    memset(stream->chunks, 0, sizeof(stream->chunks));
}

/* Звільнення ресурсів потоку */
void quic_stream_free(quic_stream_t *stream) {
    for (size_t i = 0; i < MAX_CHUNKS; i++) {
        if (stream->chunks[i].used && stream->chunks[i].data) {
            free(stream->chunks[i].data);
            stream->chunks[i].data = NULL;
            stream->chunks[i].used = false;
        }
    }
}

/* Додавання нового кадру STREAM у буфер з обробкою перекриттів */
bool quic_stream_insert_frame(quic_stream_t *stream, uint64_t offset, 
                              const uint8_t *data, size_t len, bool is_fin) {
    /* Перевірка Flow Control */
    if (offset + len > stream->max_stream_data) {
        fprintf(stderr, "[FLOW_CONTROL_ERROR] Stream %LLu: offset %LLu exceeds limit %LLu\n",
                (unsigned long long)stream->stream_id,
                (unsigned long long)(offset + len),
                (unsigned long long)stream->max_stream_data);
        return false;
    }

    if (is_fin) {
        if (stream->fin_received && stream->final_size != offset + len) {
            fprintf(stderr, "[FINAL_SIZE_ERROR] Conflicting final size for stream %LLu\n",
                    (unsigned long long)stream->stream_id);
            return false;
        }
        stream->fin_received = true;
        stream->final_size = offset + len;
    }

    /* Обрізання вже прочитаної частини даних */
    if (offset < stream->read_offset) {
        if (offset + len <= stream->read_offset) {
            return true; /* Усьому фрагменту вже задовільнено */
        }
        size_t overlap = (size_t)(stream->read_offset - offset);
        offset += overlap;
        data += overlap;
        len -= overlap;
    }

    /* Зберігаємо новий фрагмент у вільний слот */
    for (size_t i = 0; i < MAX_CHUNKS; i++) {
        if (!stream->chunks[i].used) {
            stream->chunks[i].offset = offset;
            stream->chunks[i].length = len;
            stream->chunks[i].data = (uint8_t *)malloc(len);
            if (!stream->chunks[i].data) return false;
            memcpy(stream->chunks[i].data, data, len);
            stream->chunks[i].used = true;
            stream->chunk_count++;
            return true;
        }
    }
    return false; /* Буфер фрагментів переповнено */
}

/* Просування суцільного блоку байтів до додатка */
size_t quic_stream_read_contiguous(quic_stream_t *stream, uint8_t *out_buf, size_t max_buf) {
    size_t total_read = 0;

    while (total_read < max_buf) {
        bool progress = false;
        for (size_t i = 0; i < MAX_CHUNKS; i++) {
            if (stream->chunks[i].used && stream->chunks[i].offset == stream->read_offset) {
                size_t to_copy = stream->chunks[i].length;
                if (total_read + to_copy > max_buf) {
                    to_copy = max_buf - total_read;
                }

                memcpy(out_buf + total_read, stream->chunks[i].data, to_copy);
                total_read += to_copy;
                stream->read_offset += to_copy;

                if (to_copy == stream->chunks[i].length) {
                    free(stream->chunks[i].data);
                    stream->chunks[i].data = NULL;
                    stream->chunks[i].used = false;
                    stream->chunk_count--;
                } else {
                    /* Частково прочитаний фрагмент */
                    memmove(stream->chunks[i].data, stream->chunks[i].data + to_copy, 
                            stream->chunks[i].length - to_copy);
                    stream->chunks[i].offset += to_copy;
                    stream->chunks[i].length -= to_copy;
                }
                progress = true;
                break;
            }
        }
        if (!progress) break;
    }
    return total_read;
}

/* Декодування простого QPACK Indexed Header Field */
void qpack_decode_static_indexed(uint8_t index) {
    if (index < STATIC_TABLE_SIZE && QPACK_STATIC_TABLE[index].name != NULL) {
        printf("  [QPACK Header] %s: %s\n", 
               QPACK_STATIC_TABLE[index].name, 
               QPACK_STATIC_TABLE[index].value);
    } else {
        printf("  [QPACK Header] Unknown static index %u\n", index);
    }
}
