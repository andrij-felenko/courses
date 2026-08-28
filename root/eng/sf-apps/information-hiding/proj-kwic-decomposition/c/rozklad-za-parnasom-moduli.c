#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

/* =========================================================================
 * МОДУЛЬ 1: Сховище рядків.
 * ТАЄМНИЦЯ: як саме лежать байти в пам'яті.
 * ========================================================================= */
typedef struct line_storage line_storage_t;

struct line_storage {
    char   *buffer;
    size_t *line_offsets;
    size_t *line_lengths;
    size_t  line_count;
    size_t  capacity_bytes;
};

line_storage_t* line_storage_create(void) {
    line_storage_t *ls = (line_storage_t*)malloc(sizeof(line_storage_t));
    ls->capacity_bytes = 4096;
    ls->buffer = (char*)malloc(ls->capacity_bytes);
    ls->line_offsets = (size_t*)malloc(sizeof(size_t) * 128);
    ls->line_lengths = (size_t*)malloc(sizeof(size_t) * 128);
    ls->line_count = 0;
    return ls;
}

void line_storage_destroy(line_storage_t *ls) {
    if (!ls) return;
    free(ls->buffer);
    free(ls->line_offsets);
    free(ls->line_lengths);
    free(ls);
}

void line_storage_add_line(line_storage_t *ls, const char *line) {
    size_t len = strlen(line);
    size_t offset = (ls->line_count == 0) ? 0 : 
                    (ls->line_offsets[ls->line_count - 1] + ls->line_lengths[ls->line_count - 1]);
    
    memcpy(&ls->buffer[offset], line, len);
    ls->line_offsets[ls->line_count] = offset;
    ls->line_lengths[ls->line_count] = len;
    ls->line_count++;
}

size_t line_storage_line_count(const line_storage_t *ls) {
    return ls->line_count;
}

size_t line_storage_line_length(const line_storage_t *ls, size_t line_idx) {
    return ls->line_lengths[line_idx];
}

char line_storage_get_char(const line_storage_t *ls, size_t line_idx, size_t char_idx) {
    if (char_idx >= ls->line_lengths[line_idx]) return '\0';
    size_t offset = ls->line_offsets[line_idx] + char_idx;
    return ls->buffer[offset];
}

/* =========================================================================
 * МОДУЛЬ 2: Циклічні зсуви.
 * ТАЄМНИЦЯ: формула відображення зсунутого індексу на вихідний символ рядка.
 * ========================================================================= */
typedef struct {
    size_t line_idx;
    size_t start_word_char_idx;
} shift_item_t;

typedef struct {
    const line_storage_t *storage;
    shift_item_t         *shifts;
    size_t                shift_count;
} circular_shifts_t;

circular_shifts_t* circular_shifts_create(const line_storage_t *ls) {
    circular_shifts_t *cs = (circular_shifts_t*)malloc(sizeof(circular_shifts_t));
    cs->storage = ls;
    cs->shifts = (shift_item_t*)malloc(sizeof(shift_item_t) * 512);
    cs->shift_count = 0;
    
    size_t total_lines = line_storage_line_count(ls);
    for (size_t l = 0; l < total_lines; l++) {
        size_t len = line_storage_line_length(ls, l);
        bool in_word = false;
        for (size_t c = 0; c < len; c++) {
            char ch = line_storage_get_char(ls, l, c);
            if (ch != ' ' && !in_word) {
                in_word = true;
                cs->shifts[cs->shift_count].line_idx = l;
                cs->shifts[cs->shift_count].start_word_char_idx = c;
                cs->shift_count++;
            } else if (ch == ' ') {
                in_word = false;
            }
        }
    }
    return cs;
}

void circular_shifts_destroy(circular_shifts_t *cs) {
    if (!cs) return;
    free(cs->shifts);
    free(cs);
}

size_t circular_shifts_count(const circular_shifts_t *cs) {
    return cs->shift_count;
}

char circular_shifts_get_char(const circular_shifts_t *cs, size_t shift_idx, size_t pos) {
    size_t line_idx = cs->shifts[shift_idx].line_idx;
    size_t offset = cs->shifts[shift_idx].start_word_char_idx;
    size_t len = line_storage_line_length(cs->storage, line_idx);
    
    if (pos >= len) return '\0';
    size_t mapped_idx = (offset + pos) % (len + 1);
    if (mapped_idx == len) {
        return ' ';
    }
    return line_storage_get_char(cs->storage, line_idx, mapped_idx);
}

/* =========================================================================
 * МОДУЛЬ 3: Упорядкування.
 * ТАЄМНИЦЯ: алгоритм сортування та індекс перестановки.
 * ========================================================================= */
typedef struct {
    const circular_shifts_t *shifts;
    size_t                  *order;
    size_t                   count;
} alphabetizer_t;

static int shift_cmp(const circular_shifts_t *cs, size_t a, size_t b) {
    size_t pos = 0;
    while (true) {
        char ca = circular_shifts_get_char(cs, a, pos);
        char cb = circular_shifts_get_char(cs, b, pos);
        if (ca != cb) return (unsigned char)ca - (unsigned char)cb;
        if (ca == '\0') return 0;
        pos++;
    }
}

alphabetizer_t* alphabetizer_create(const circular_shifts_t *cs) {
    alphabetizer_t *az = (alphabetizer_t*)malloc(sizeof(alphabetizer_t));
    az->shifts = cs;
    az->count = circular_shifts_count(cs);
    az->order = (size_t*)malloc(sizeof(size_t) * az->count);
    
    for (size_t i = 0; i < az->count; i++) az->order[i] = i;
    
    for (size_t i = 0; i < az->count; i++) {
        for (size_t j = i + 1; j < az->count; j++) {
            if (shift_cmp(cs, az->order[i], az->order[j]) > 0) {
                size_t tmp = az->order[i];
                az->order[i] = az->order[j];
                az->order[j] = tmp;
            }
        }
    }
    return az;
}

void alphabetizer_destroy(alphabetizer_t *az) {
    if (!az) return;
    free(az->order);
    free(az);
}

size_t alphabetizer_get_sorted_shift_index(const alphabetizer_t *az, size_t pos) {
    return az->order[pos];
}

/* =========================================================================
 * МОДУЛЬ 4: Вивід покажчика.
 * ТАЄМНИЦЯ: формат оформлення.
 * ========================================================================= */
void output_print_all(const alphabetizer_t *az, const circular_shifts_t *cs) {
    size_t total = circular_shifts_count(cs);
    for (size_t i = 0; i < total; i++) {
        size_t shift_idx = alphabetizer_get_sorted_shift_index(az, i);
        size_t char_pos = 0;
        while (true) {
            char c = circular_shifts_get_char(cs, shift_idx, char_pos++);
            if (c == '\0') break;
            putchar(c);
        }
        putchar('\n');
    }
}
