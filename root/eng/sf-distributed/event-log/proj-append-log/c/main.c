#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <time.h>
#include <errno.h>

#define INDEX_INTERVAL_BYTES 4096
#define MAX_SEGMENT_BYTES    (10 * 1024 * 1024) /* 10 МБ для навчального тесту */

/* Таблиця CRC32 IEEE 802.3 */
static uint32_t crc32_for_byte(uint32_t r) {
    for (int j = 0; j < 8; ++j)
        r = (r & 1 ? 0xEDB88320L : 0) ^ r >> 1;
    return r ^ 0xFF000000L;
}

static uint32_t calculate_crc32(const uint8_t *data, size_t length) {
    uint32_t crc = 0;
    while (length--) {
        static uint32_t table[256];
        static bool table_init = false;
        if (!table_init) {
            for (size_t i = 0; i < 256; ++i)
                table[i] = crc32_for_byte((uint32_t)i);
            table_init = true;
        }
        crc = table[(uint8_t)crc ^ *data++] ^ crc >> 8;
    }
    return crc;
}

#pragma pack(push, 1)
typedef struct {
    uint32_t relative_offset;
    uint32_t physical_pos;
} IndexEntry;

typedef struct {
    uint32_t crc;
    uint8_t  magic;
    uint8_t  flags;
    uint64_t offset;
    uint64_t timestamp;
    int32_t  key_len;
} RecordHeader;
#pragma pack(pop)

typedef struct {
    char log_path[256];
    char idx_path[256];
    FILE *log_file;
    FILE *idx_file;
    uint64_t base_offset;
    uint64_t next_offset;
    uint32_t current_log_size;
    uint32_t bytes_since_last_index;
} LogSegment;

/* Відкриття або створення нового сегмента */
int segment_open(LogSegment *seg, const char *dir, uint64_t base_offset) {
    memset(seg, 0, sizeof(LogSegment));
    seg->base_offset = base_offset;
    seg->next_offset = base_offset;

    snprintf(seg->log_path, sizeof(seg->log_path), "%s/%020llu.log", dir, (unsigned long long)base_offset);
    snprintf(seg->idx_path, sizeof(seg->idx_path), "%s/%020llu.index", dir, (unsigned long long)base_offset);

    seg->log_file = fopen(seg->log_path, "a+b");
    if (!seg->log_file) return -1;

    seg->idx_file = fopen(seg->idx_path, "a+b");
    if (!seg->idx_file) {
        fclose(seg->log_file);
        return -1;
    }

    fseek(seg->log_file, 0, SEEK_END);
    seg->current_log_size = (uint32_t)ftell(seg->log_file);
    seg->bytes_since_last_index = 0;

    return 0;
}

/* Закриття сегмента та скидання буферів */
void segment_close(LogSegment *seg) {
    if (seg->log_file) { fflush(seg->log_file); fclose(seg->log_file); seg->log_file = NULL; }
    if (seg->idx_file) { fflush(seg->idx_file); fclose(seg->idx_file); seg->idx_file = NULL; }
}

/* Послідовне додавання нового запису в сегмент */
int segment_append(LogSegment *seg, const uint8_t *key, int32_t key_len,
                   const uint8_t *val, int32_t val_len, uint64_t *assigned_offset) {
    if (!seg->log_file || !seg->idx_file) return -1;

    uint64_t offset = seg->next_offset;
    uint64_t now_ms = (uint64_t)time(NULL) * 1000;
    uint32_t record_pos = seg->current_log_size;

    int32_t valid_klen = (key_len > 0) ? key_len : 0;
    int32_t valid_vlen = (val_len > 0) ? val_len : 0;

    /* Обчислення розміру тіла для CRC (все, крім 4 байт поля CRC) */
    size_t payload_size = sizeof(RecordHeader) - sizeof(uint32_t) + valid_klen + sizeof(int32_t) + valid_vlen;
    uint8_t *buf = (uint8_t*)malloc(payload_size);
    if (!buf) return -ENOMEM;

    uint8_t *ptr = buf;
    uint8_t magic = 0x01;
    uint8_t flags = 0x00;

    memcpy(ptr, &magic, 1); ptr += 1;
    memcpy(ptr, &flags, 1); ptr += 1;
    memcpy(ptr, &offset, 8); ptr += 8;
    memcpy(ptr, &now_ms, 8); ptr += 8;
    memcpy(ptr, &key_len, 4); ptr += 4;
    if (valid_klen > 0) { memcpy(ptr, key, valid_klen); ptr += valid_klen; }
    memcpy(ptr, &val_len, 4); ptr += 4;
    if (valid_vlen > 0) { memcpy(ptr, val, valid_vlen); ptr += valid_vlen; }

    uint32_t crc = calculate_crc32(buf, payload_size);

    /* Запис: CRC32 та корисне навантаження */
    if (fwrite(&crc, sizeof(uint32_t), 1, seg->log_file) != 1 ||
        fwrite(buf, payload_size, 1, seg->log_file) != 1) {
        free(buf);
        return -EIO;
    }
    free(buf);

    size_t total_record_bytes = sizeof(uint32_t) + payload_size;
    seg->current_log_size += (uint32_t)total_record_bytes;
    seg->bytes_since_last_index += (uint32_t)total_record_bytes;

    /* Оновлення розрідженого індексу при перевищенні 4 КБ */
    if (seg->bytes_since_last_index >= INDEX_INTERVAL_BYTES || offset == seg->base_offset) {
        IndexEntry ie;
        ie.relative_offset = (uint32_t)(offset - seg->base_offset);
        ie.physical_pos = record_pos;

        if (fwrite(&ie, sizeof(IndexEntry), 1, seg->idx_file) != 1) {
            return -EIO;
        }
        fflush(seg->idx_file);
        seg->bytes_since_last_index = 0;
    }

    fflush(seg->log_file);
    seg->next_offset++;
    if (assigned_offset) *assigned_offset = offset;
    return 0;
}

/* Двофазний пошук запису за цільовим зсувом */
int segment_read_at(LogSegment *seg, uint64_t target_offset,
                    uint8_t *out_val, int32_t *out_val_len) {
    if (target_offset < seg->base_offset || target_offset >= seg->next_offset)
        return -ENOENT;

    /* Фаза 1: Двійковий пошук в індексному файлі найближчої нижньої межі */
    fseek(seg->idx_file, 0, SEEK_END);
    long idx_file_size = ftell(seg->idx_file);
    int num_entries = (int)(idx_file_size / sizeof(IndexEntry));

    uint32_t search_rel_offset = (uint32_t)(target_offset - seg->base_offset);
    uint32_t best_physical_pos = 0;

    int low = 0, high = num_entries - 1;
    while (low <= high) {
        int mid = low + (high - low) / 2;
        IndexEntry entry;
        fseek(seg->idx_file, mid * sizeof(IndexEntry), SEEK_SET);
        if (fread(&entry, sizeof(IndexEntry), 1, seg->idx_file) != 1) break;

        if (entry.relative_offset <= search_rel_offset) {
            best_physical_pos = entry.physical_pos;
            low = mid + 1; /* Звужуємо діапазон праворуч */
        } else {
            high = mid - 1;
        }
    }

    /* Фаза 2: Лінійне сканування максимум 4 КБ у .log від знайденого зсуву */
    fseek(seg->log_file, best_physical_pos, SEEK_SET);

    while (ftell(seg->log_file) < seg->current_log_size) {
        uint32_t stored_crc;
        if (fread(&stored_crc, sizeof(uint32_t), 1, seg->log_file) != 1) break;

        uint8_t magic, flags;
        uint64_t record_offset, ts;
        int32_t klen, vlen;

        if (fread(&magic, 1, 1, seg->log_file) != 1) break;
        if (fread(&flags, 1, 1, seg->log_file) != 1) break;
        if (fread(&record_offset, 8, 1, seg->log_file) != 1) break;
        if (fread(&ts, 8, 1, seg->log_file) != 1) break;
        if (fread(&klen, 4, 1, seg->log_file) != 1) break;

        if (klen > 0) fseek(seg->log_file, klen, SEEK_CUR);

        if (fread(&vlen, 4, 1, seg->log_file) != 1) break;

        if (record_offset == target_offset) {
            if (vlen > 0 && out_val) {
                if (fread(out_val, 1, vlen, seg->log_file) != (size_t)vlen) return -EIO;
                *out_val_len = vlen;
            } else {
                *out_val_len = 0;
            }
            return 0; /* Успішно знайдено */
        }

        if (vlen > 0) fseek(seg->log_file, vlen, SEEK_CUR);
    }

    return -ENOENT;
}
