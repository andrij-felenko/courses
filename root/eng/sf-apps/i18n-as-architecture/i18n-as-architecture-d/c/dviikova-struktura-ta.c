#include <stdint.h>
#include <stddef.h>
#include <string.h>
#include <stdbool.h>

#define MO_MAGIC_LE 0x950412DE
#define MO_MAGIC_BE 0xDE120495

typedef struct {
    uint32_t length;
    uint32_t offset;
} mo_string_desc_t;

typedef struct {
    const uint8_t *data;
    size_t size;
    uint32_t num_strings;
    const mo_string_desc_t *orig_table;
    const mo_string_desc_t *trans_table;
    bool swap_endian;
} mo_file_reader_t;

static inline uint32_t mo_swap32(uint32_t val, bool swap) {
    if (!swap) return val;
    return ((val >> 24) & 0xFF) |
           ((val >> 8)  & 0xFF00) |
           ((val << 8)  & 0xFF0000) |
           ((val << 24) & 0xFF000000);
}

bool mo_reader_init(mo_file_reader_t *reader, const uint8_t *buffer, size_t size) {
    if (!reader || !buffer || size < 28) return false;
    
    reader->data = buffer;
    reader->size = size;
    
    uint32_t magic;
    memcpy(&magic, buffer, sizeof(uint32_t));
    
    if (magic == MO_MAGIC_LE) {
        reader->swap_endian = false;
    } else if (magic == MO_MAGIC_BE) {
        reader->swap_endian = true;
    } else {
        return false;
    }
    
    uint32_t num_strings, orig_offset, trans_offset;
    memcpy(&num_strings,  buffer + 8,  sizeof(uint32_t));
    memcpy(&orig_offset,  buffer + 12, sizeof(uint32_t));
    memcpy(&trans_offset, buffer + 16, sizeof(uint32_t));
    
    reader->num_strings = mo_swap32(num_strings, reader->swap_endian);
    uint32_t off_orig   = mo_swap32(orig_offset, reader->swap_endian);
    uint32_t off_trans  = mo_swap32(trans_offset, reader->swap_endian);
    
    size_t table_bytes = (size_t)reader->num_strings * sizeof(mo_string_desc_t);
    if (off_orig + table_bytes > size || off_trans + table_bytes > size) {
        return false;
    }
    
    reader->orig_table  = (const mo_string_desc_t *)(buffer + off_orig);
    reader->trans_table = (const mo_string_desc_t *)(buffer + off_trans);
    return true;
}

const char *mo_reader_lookup(const mo_file_reader_t *reader, const char *msgid) {
    if (!reader || !reader->data || !msgid) return msgid;
    
    size_t target_len = strlen(msgid);
    int32_t low = 0;
    int32_t high = (int32_t)reader->num_strings - 1;
    
    while (low <= high) {
        int32_t mid = low + ((high - low) >> 1);
        uint32_t str_len = mo_swap32(reader->orig_table[mid].length, reader->swap_endian);
        uint32_t str_off = mo_swap32(reader->orig_table[mid].offset, reader->swap_endian);
        
        if (str_off + str_len >= reader->size) break;
        
        const char *cand = (const char *)(reader->data + str_off);
        int cmp = strcmp(msgid, cand);
        
        if (cmp == 0) {
            uint32_t tr_len = mo_swap32(reader->trans_table[mid].length, reader->swap_endian);
            uint32_t tr_off = mo_swap32(reader->trans_table[mid].offset, reader->swap_endian);
            if (tr_off + tr_len < reader->size) {
                return (const char *)(reader->data + tr_off);
            }
            break;
        } else if (cmp < 0) {
            high = mid - 1;
        } else {
            low = mid + 1;
        }
    }
    return msgid;
}
