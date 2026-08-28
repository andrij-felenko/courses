#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

#define CHUNK_SIZE 4096
#define MAX_LINE_LEN 65536

typedef struct {
    char buffer[MAX_LINE_LEN];
    size_t unread_bytes;
} ndjson_stream_t;

typedef void (*record_callback_t)(const char *json_line, size_t length, void *user_data);

void ndjson_stream_init(ndjson_stream_t *stream) {
    stream->unread_bytes = 0;
}

/* Обробляє порційний блок даних із джерела */
bool ndjson_stream_feed(ndjson_stream_t *stream, const char *chunk, size_t chunk_len,
                        record_callback_t on_record, void *user_data) {
    if (stream->unread_bytes + chunk_len > MAX_LINE_LEN) {
        /* Переповнення: окремий запис перевищив максимальний ліміт пам'яті */
        return false;
    }

    /* Додаємо нові байти в кінець накопиченого залишку */
    memcpy(stream->buffer + stream->unread_bytes, chunk, chunk_len);
    stream->unread_bytes += chunk_len;

    size_t processed_offset = 0;

    for (size_t i = 0; i < stream->unread_bytes; ++i) {
        if (stream->buffer[i] == '\n') {
            size_t line_len = i - processed_offset;

            /* Відкидаємо можливий '\r' перед '\n' */
            if (line_len > 0 && stream->buffer[processed_offset + line_len - 1] == '\r') {
                line_len--;
            }

            /* Ігноруємо порожні рядки між записами */
            if (line_len > 0) {
                on_record(stream->buffer + processed_offset, line_len, user_data);
            }

            processed_offset = i + 1;
        }
    }

    /* Зсуваємо незавершений залишок на початок буфера */
    if (processed_offset > 0) {
        size_t remaining = stream->unread_bytes - processed_offset;
        if (remaining > 0) {
            memmove(stream->buffer, stream->buffer + processed_offset, remaining);
        }
        stream->unread_bytes = remaining;
    }

    return true;
}

/* Обробка кінця потоку для перевірки залишкового запису */
void ndjson_stream_flush(ndjson_stream_t *stream, record_callback_t on_record, void *user_data) {
    if (stream->unread_bytes > 0) {
        size_t len = stream->unread_bytes;
        if (stream->buffer[len - 1] == '\r') {
            len--;
        }
        if (len > 0) {
            on_record(stream->buffer, len, user_data);
        }
        stream->unread_bytes = 0;
    }
}

static void print_record(const char *json_line, size_t length, void *user_data) {
    int *count = (int *)user_data;
    (*count)++;
    printf("[%d] Отримано запис (%zu байтів): %.*s\n", *count, length, (int)length, json_line);
}

int main(void) {
    ndjson_stream_t stream;
    ndjson_stream_init(&stream);
    int records_count = 0;

    /* Симуляція надходження частин повідомлення з сокета */
    const char *chunk1 = "{\"id\":101,\"event\":\"login\"}\n{\"id\":102,\"event\":\"tra";
    const char *chunk2 = "nsfer\",\"amount\":450}\r\n{\"id\":103,\"event\":\"logout\"}\n";

    ndjson_stream_feed(&stream, chunk1, strlen(chunk1), print_record, &records_count);
    ndjson_stream_feed(&stream, chunk2, strlen(chunk2), print_record, &records_count);
    ndjson_stream_flush(&stream, print_record, &records_count);

    return 0;
}
