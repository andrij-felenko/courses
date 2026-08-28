#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define AVRO_SYNC_SIZE 16
#define AVRO_MAGIC_SIZE 4
static const uint8_t EXPECTED_MAGIC[AVRO_MAGIC_SIZE] = {'O', 'b', 'j', 0x01};

/* Зчитувач із буфера в пам'яті з контролем меж */
typedef struct {
    const uint8_t *data;
    size_t size;
    size_t offset;
} ByteReader;

static inline bool reader_has_bytes(const ByteReader *r, size_t n) {
    return r->offset + n <= r->size;
}

/* Декодування Zigzag Varint (64-бітне ціле зі знаком) */
static bool read_varint_long(ByteReader *r, int64_t *out_val) {
    uint64_t raw = 0;
    int shift = 0;

    while (reader_has_bytes(r, 1)) {
        uint8_t b = r->data[r->offset++];
        raw |= ((uint64_t)(b & 0x7F)) << shift;
        if ((b & 0x80) == 0) {
            /* Відновлення знаку з Zigzag-подання */
            *out_val = (int64_t)((raw >> 1) ^ (-(int64_t)(raw & 1)));
            return true;
        }
        shift += 7;
        if (shift >= 64) return false; /* Захист від некоректного varint */
    }
    return false;
}

/* Зчитування рядка (довжина у вигляді varint + байти) */
static bool read_avro_string(ByteReader *r, char **out_str, size_t *out_len) {
    int64_t len = 0;
    if (!read_varint_long(r, &len) || len < 0) return false;
    if (!reader_has_bytes(r, (size_t)len)) return false;

    char *buf = (char *)malloc((size_t)len + 1);
    if (!buf) return false;

    memcpy(buf, r->data + r->offset, (size_t)len);
    buf[len] = '\0';
    r->offset += (size_t)len;

    *out_str = buf;
    if (out_len) *out_len = (size_t)len;
    return true;
}

/* Зчитування двійкових байтів (довжина у вигляді varint + байти) */
static bool read_avro_bytes(ByteReader *r, uint8_t **out_bytes, size_t *out_len) {
    int64_t len = 0;
    if (!read_varint_long(r, &len) || len < 0) return false;
    if (!reader_has_bytes(r, (size_t)len)) return false;

    uint8_t *buf = (uint8_t *)malloc((size_t)len);
    if (!buf) return false;

    memcpy(buf, r->data + r->offset, (size_t)len);
    r->offset += (size_t)len;

    *out_bytes = buf;
    *out_len = (size_t)len;
    return true;
}

/* Метадані заголовка Avro OCF */
typedef struct {
    char *schema_json;
    char *codec;
    uint8_t sync_marker[AVRO_SYNC_SIZE];
} AvroHeader;

static void free_avro_header(AvroHeader *hdr) {
    if (hdr->schema_json) free(hdr->schema_json);
    if (hdr->codec) free(hdr->codec);
    hdr->schema_json = NULL;
    hdr->codec = NULL;
}

/* Розбір заголовка контейнера */
static bool parse_avro_header(ByteReader *r, AvroHeader *hdr) {
    memset(hdr, 0, sizeof(AvroHeader));

    /* 1. Перевірка 4 байтів Magic */
    if (!reader_has_bytes(r, AVRO_MAGIC_SIZE)) return false;
    if (memcmp(r->data + r->offset, EXPECTED_MAGIC, AVRO_MAGIC_SIZE) != 0) {
        return false;
    }
    r->offset += AVRO_MAGIC_SIZE;

    /* 2. Розбір карти метаданих (Metadata Map) */
    while (true) {
        int64_t count = 0;
        if (!read_varint_long(r, &count)) goto fail;
        if (count == 0) break; /* Кінець карти */

        if (count < 0) {
            /* Від'ємне число означає наявність сумарного розміру блоку карти в байтах */
            count = -count;
            int64_t byte_size = 0;
            if (!read_varint_long(r, &byte_size)) goto fail;
        }

        for (int64_t i = 0; i < count; i++) {
            char *key = NULL;
            uint8_t *val_bytes = NULL;
            size_t val_len = 0;

            if (!read_avro_string(r, &key, NULL)) goto fail;
            if (!read_avro_bytes(r, &val_bytes, &val_len)) {
                free(key);
                goto fail;
            }

            if (strcmp(key, "avro.schema") == 0) {
                hdr->schema_json = (char *)malloc(val_len + 1);
                if (hdr->schema_json) {
                    memcpy(hdr->schema_json, val_bytes, val_len);
                    hdr->schema_json[val_len] = '\0';
                }
            } else if (strcmp(key, "avro.codec") == 0) {
                hdr->codec = (char *)malloc(val_len + 1);
                if (hdr->codec) {
                    memcpy(hdr->codec, val_bytes, val_len);
                    hdr->codec[val_len] = '\0';
                }
            }

            free(key);
            free(val_bytes);
        }
    }

    /* 3. Зчитування 16-байтного синхромаркера */
    if (!reader_has_bytes(r, AVRO_SYNC_SIZE)) goto fail;
    memcpy(hdr->sync_marker, r->data + r->offset, AVRO_SYNC_SIZE);
    r->offset += AVRO_SYNC_SIZE;

    return true;

fail:
    free_avro_header(hdr);
    return false;
}

/* Імітація обробки записів із блоку з узгодженням схеми */
static void process_record_with_resolution(ByteReader *block_r) {
    /* Приклад схеми записувача (Writer): { id: int, name: string, legacy_tag: int }
       Приклад схеми зчитувача (Reader):   { id: long (розширено), name: string, email: string (default="") } */

    int64_t id_raw = 0;
    if (!read_varint_long(block_r, &id_raw)) return;

    char *name_str = NULL;
    if (!read_avro_string(block_r, &name_str, NULL)) return;

    /* Поле legacy_tag було у файлі, але не потрібне зчитувачу: пропускаємо байти */
    int64_t legacy_tag_discarded = 0;
    if (!read_varint_long(block_r, &legacy_tag_discarded)) {
        free(name_str);
        return;
    }

    /* Узгоджене представлення в пам'яті */
    int64_t resolved_id = id_raw;              /* Просування типу int -> long */
    const char *resolved_email = "default@none"; /* Підстановка значення за замовчуванням */

    printf("  [Запис] id: %lld, name: '%s', email: '%s' (legacy_tag %lld пропущено)\n",
           (long long)resolved_id, name_str, resolved_email, (long long)legacy_tag_discarded);

    free(name_str);
}

/* Ітерація по блоках даних контейнера */
static void parse_avro_data_blocks(ByteReader *r, const AvroHeader *hdr) {
    int block_index = 0;

    while (reader_has_bytes(r, 1)) {
        int64_t record_count = 0;
        int64_t byte_size = 0;

        if (!read_varint_long(r, &record_count)) break;
        if (!read_varint_long(r, &byte_size)) break;

        printf("Блок #%d: %lld записів, %lld байтів даних\n",
               ++block_index, (long long)record_count, (long long)byte_size);

        if (!reader_has_bytes(r, (size_t)byte_size)) {
            fprintf(stderr, "Помилка: неповний блок даних на зміщенні %zu\n", r->offset);
            return;
        }

        /* Створюємо підчитач для вмісту блоку */
        ByteReader block_r = {
            .data = r->data + r->offset,
            .size = (size_t)byte_size,
            .offset = 0
        };
        r->offset += (size_t)byte_size;

        /* Розбираємо записи всередині блоку */
        for (int64_t i = 0; i < record_count; i++) {
            process_record_with_resolution(&block_r);
        }

        /* Перевірка 16-байтного синхромаркера наприкінці блоку */
        if (!reader_has_bytes(r, AVRO_SYNC_SIZE)) {
            fprintf(stderr, "Помилка: відсутній маркер синхронізації блоку\n");
            return;
        }

        if (memcmp(r->data + r->offset, hdr->sync_marker, AVRO_SYNC_SIZE) != 0) {
            fprintf(stderr, "Критична помилка: маркер синхронізації блоку пошкоджено!\n");
            return;
        }
        r->offset += AVRO_SYNC_SIZE;
        printf("  -> Синхромаркер блоку верифіковано успішно.\n");
    }
}
