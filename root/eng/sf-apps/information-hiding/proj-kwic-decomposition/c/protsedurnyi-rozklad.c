#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

#define MAX_CHARS 4096
#define MAX_WORDS 512
#define MAX_SHIFTS 512

/* СПІЛЬНА СТРУКТУРА: усі модулі знають її точну будову */
typedef struct {
    char chars[MAX_CHARS];         /* суцільний масив символів із нуль-термінаторами */
    size_t char_count;
    
    size_t line_starts[MAX_WORDS]; /* індекси початку кожного рядка в chars */
    size_t line_count;
    
    /* Зсув описується парою: (індекс рядка, номер першого слова в зсуві) */
    struct {
        size_t line_idx;
        size_t word_offset;
    } shifts[MAX_SHIFTS];
    size_t shift_count;
} shared_kwic_data_t;

/* Модуль 1: Ввід тексту */
void step_input(shared_kwic_data_t *data, const char **raw_lines, size_t count) {
    data->char_count = 0;
    data->line_count = 0;
    for (size_t i = 0; i < count; i++) {
        data->line_starts[data->line_count++] = data->char_count;
        size_t len = strlen(raw_lines[i]) + 1;
        memcpy(&data->chars[data->char_count], raw_lines[i], len);
        data->char_count += len;
    }
}

/* Модуль 2: Циклічний зсув (знає внутрішнє розташування символів у масиві chars) */
void step_circular_shift(shared_kwic_data_t *data) {
    data->shift_count = 0;
    for (size_t l = 0; l < data->line_count; l++) {
        const char *line = &data->chars[data->line_starts[l]];
        size_t word_idx = 0;
        bool in_word = false;
        
        for (size_t c = 0; line[c] != '\0'; c++) {
            if (line[c] != ' ' && !in_word) {
                in_word = true;
                data->shifts[data->shift_count].line_idx = l;
                data->shifts[data->shift_count].word_offset = c;
                data->shift_count++;
            } else if (line[c] == ' ') {
                in_word = false;
            }
        }
    }
}

/* Модуль 3: Упорядкування (порівнює рядки, рахуючи зміщення напряму в chars) */
static int compare_shifts(const void *a, const void *b, void *user_data) {
    const shared_kwic_data_t *data = (const shared_kwic_data_t *)user_data;
    const size_t *idx_a = (const size_t *)a;
    const size_t *idx_b = (const size_t *)b;
    
    const char *line_a = &data->chars[data->line_starts[data->shifts[*idx_a].line_idx]];
    const char *line_b = &data->chars[data->line_starts[data->shifts[*idx_b].line_idx]];
    
    const char *start_a = line_a + data->shifts[*idx_a].word_offset;
    const char *start_b = line_b + data->shifts[*idx_b].word_offset;
    
    return strcmp(start_a, start_b);
}

void step_alphabetize(shared_kwic_data_t *data, size_t *order) {
    for (size_t i = 0; i < data->shift_count; i++) {
        order[i] = i;
    }
    for (size_t i = 0; i < data->shift_count; i++) {
        for (size_t j = i + 1; j < data->shift_count; j++) {
            if (compare_shifts(&order[i], &order[j], data) > 0) {
                size_t tmp = order[i];
                order[i] = order[j];
                order[j] = tmp;
            }
        }
    }
}

/* Модуль 4: Вивід покажчика */
void step_output(const shared_kwic_data_t *data, const size_t *order) {
    for (size_t i = 0; i < data->shift_count; i++) {
        size_t s = order[i];
        size_t l = data->shifts[s].line_idx;
        size_t offset = data->shifts[s].word_offset;
        const char *line = &data->chars[data->line_starts[l]];
        
        printf("%s", line + offset);
        if (offset > 0) {
            printf(" / ");
            for (size_t k = 0; k < offset; k++) {
                putchar(line[k]);
            }
        }
        putchar('\n');
    }
}
