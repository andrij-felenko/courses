#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>

/* Тип операції редагування */
typedef enum {
    DIFF_OP_KEEP = 0,
    DIFF_OP_INSERT = 1,
    DIFF_OP_DELETE = 2
} diff_op_type_t;

/* Окремий крок у сценарії редагування */
typedef struct {
    diff_op_type_t type;
    size_t line_a; /* 1-індексований номер рядка у файлі A (0, якщо insert) */
    size_t line_b; /* 1-індексований номер рядка у файлі B (0, якщо delete) */
    const char* text;
    size_t text_len;
} diff_step_t;

/* Результат порівняння */
typedef struct {
    diff_step_t* steps;
    size_t count;
    size_t capacity;
    size_t edit_distance;
} diff_script_t;

/* Окремий рядок із попередньо обчисленим 64-бітним хешем FNV-1a */
typedef struct {
    const char* ptr;
    size_t len;
    uint64_t hash;
} diff_line_t;

/* Обчислення швидкого некриптографічного хешу FNV-1a */
static uint64_t hash_line_fnv1a(const char* str, size_t len) {
    uint64_t h = 14695981039346656037ULL;
    for (size_t i = 0; i < len; ++i) {
        h ^= (uint8_t)str[i];
        h *= 1099511628211ULL;
    }
    return h;
}

/* Розбиття вихідного тексту на масив рядків */
static diff_line_t* split_text_lines(const char* src, size_t* out_count) {
    if (!src || !out_count) return NULL;
    size_t cap = 32;
    size_t cnt = 0;
    diff_line_t* lines = (diff_line_t*)malloc(cap * sizeof(diff_line_t));
    if (!lines) return NULL;

    const char* p = src;
    while (*p) {
        const char* start = p;
        while (*p && *p != '\n') p++;
        size_t len = (size_t)(p - start);
        if (len > 0 && start[len - 1] == '\r') len--; /* Відсікаємо CR */

        if (cnt >= cap) {
            cap *= 2;
            diff_line_t* tmp = (diff_line_t*)realloc(lines, cap * sizeof(diff_line_t));
            if (!tmp) { free(lines); return NULL; }
            lines = tmp;
        }

        lines[cnt].ptr = start;
        lines[cnt].len = len;
        lines[cnt].hash = hash_line_fnv1a(start, len);
        cnt++;

        if (*p == '\n') p++;
    }

    *out_count = cnt;
    return lines;
}

/* Порівняння двох рядків через порівняння хешів та довжин */
static inline bool lines_are_equal(const diff_line_t* a, const diff_line_t* b) {
    if (a->hash != b->hash || a->len != b->len) return false;
    return memcmp(a->ptr, b->ptr, a->len) == 0;
}

/* Основна функція алгоритму Маєрса */
diff_script_t* myers_diff(const char* text_a, const char* text_b) {
    size_t n = 0, m = 0;
    diff_line_t* a = split_text_lines(text_a, &n);
    diff_line_t* b = split_text_lines(text_b, &m);

    diff_script_t* script = (diff_script_t*)calloc(1, sizeof(diff_script_t));
    if (!script || (!a && n > 0) || (!b && m > 0)) {
        free(a); free(b); free(script);
        return NULL;
    }

    size_t max_d = n + m;
    size_t v_size = 2 * max_d + 1;
    int* v = (int*)malloc(v_size * sizeof(int));
    
    /* Історія станів V для зворотного проходу */
    int** trace = (int**)malloc((max_d + 1) * sizeof(int*));
    if (!v || !trace) {
        free(a); free(b); free(v); free(trace); free(script);
        return NULL;
    }

    /* Базовий стан на кроці D = 0 */
    for (size_t i = 0; i < v_size; ++i) v[i] = -1;
    int offset = (int)max_d;
    
    /* Початкова змія (спільний префікс) */
    int x0 = 0, y0 = 0;
    while ((size_t)x0 < n && (size_t)y0 < m && lines_are_equal(&a[x0], &b[y0])) {
        x0++; y0++;
    }
    v[offset + 0] = x0;

    trace[0] = (int*)malloc(v_size * sizeof(int));
    memcpy(trace[0], v, v_size * sizeof(int));

    size_t final_d = 0;
    bool found = (x0 == (int)n && y0 == (int)m);

    for (size_t d = 1; d <= max_d && !found; ++d) {
        trace[d] = (int*)malloc(v_size * sizeof(int));
        int d_int = (int)d;

        for (int k = -d_int; k <= d_int; k += 2) {
            int x;
            /* Вибір оптимального попереднього кроку */
            if (k == -d_int || (k != d_int && v[offset + k - 1] < v[offset + k + 1])) {
                x = v[offset + k + 1]; /* Крок вниз (вставка з B) */
            } else {
                x = v[offset + k - 1] + 1; /* Крок вправо (видалення з A) */
            }

            int y = x - k;

            /* Протягування змії (діагональні збіги) */
            while ((size_t)x < n && (size_t)y < m && lines_are_equal(&a[x], &b[y])) {
                x++; y++;
            }

            v[offset + k] = x;

            if (x >= (int)n && y >= (int)m) {
                final_d = d;
                found = true;
                break;
            }
        }
        memcpy(trace[d], v, v_size * sizeof(int));
    }

    script->edit_distance = final_d;

    /* Зворотний прохід (Backtracking) для побудови послідовності кроків */
    size_t max_steps = n + m + 1;
    diff_step_t* rev_steps = (diff_step_t*)malloc(max_steps * sizeof(diff_step_t));
    size_t step_count = 0;

    int cur_x = (int)n;
    int cur_y = (int)m;

    for (int d = (int)final_d; d > 0; --d) {
        int k = cur_x - cur_y;
        int prev_k;
        int* v_prev = trace[d - 1];

        if (k == -d || (k != d && v_prev[offset + k - 1] < v_prev[offset + k + 1])) {
            prev_k = k + 1;
        } else {
            prev_k = k - 1;
        }

        int prev_x = v_prev[offset + prev_k];
        int prev_y = prev_x - prev_k;

        /* Запис діагональних збігів (змія) */
        while (cur_x > prev_x && cur_y > prev_y) {
            cur_x--; cur_y--;
            rev_steps[step_count++] = (diff_step_t){
                .type = DIFF_OP_KEEP,
                .line_a = (size_t)(cur_x + 1),
                .line_b = (size_t)(cur_y + 1),
                .text = a[cur_x].ptr,
                .text_len = a[cur_x].len
            };
        }

        /* Запис недіагонального кроку (вставка або видалення) */
        if (cur_x > prev_x) {
            cur_x--;
            rev_steps[step_count++] = (diff_step_t){
                .type = DIFF_OP_DELETE,
                .line_a = (size_t)(cur_x + 1),
                .line_b = 0,
                .text = a[cur_x].ptr,
                .text_len = a[cur_x].len
            };
        } else if (cur_y > prev_y) {
            cur_y--;
            rev_steps[step_count++] = (diff_step_t){
                .type = DIFF_OP_INSERT,
                .line_a = 0,
                .line_b = (size_t)(cur_y + 1),
                .text = b[cur_y].ptr,
                .text_len = b[cur_y].len
            };
        }
    }

    /* Початкова змія на кроці D = 0 */
    while (cur_x > 0 && cur_y > 0) {
        cur_x--; cur_y--;
        rev_steps[step_count++] = (diff_step_t){
            .type = DIFF_OP_KEEP,
            .line_a = (size_t)(cur_x + 1),
            .line_b = (size_t)(cur_y + 1),
            .text = a[cur_x].ptr,
            .text_len = a[cur_x].len
        };
    }

    /* Розвертаємо кроки у прямому хронологічному порядку */
    script->steps = (diff_step_t*)malloc(step_count * sizeof(diff_step_t));
    script->count = step_count;
    for (size_t i = 0; i < step_count; ++i) {
        script->steps[i] = rev_steps[step_count - 1 - i];
    }

    /* Звільнення робочої пам'яті */
    for (size_t d = 0; d <= final_d; ++d) free(trace[d]);
    free(trace);
    free(v);
    free(rev_steps);
    free(a);
    free(b);

    return script;
}

/* Звільнення пам'яті результату */
void free_diff_script(diff_script_t* script) {
    if (!script) return;
    free(script->steps);
    free(script);
}

/* Друк уніфікованого diff */
void print_unified_diff(const diff_script_t* script) {
    if (!script) return;
    printf("--- a/original\n");
    printf("+++ b/modified\n");
    for (size_t i = 0; i < script->count; ++i) {
        const diff_step_t* s = &script->steps[i];
        char prefix = (s->type == DIFF_OP_KEEP) ? ' ' :
                      (s->type == DIFF_OP_INSERT) ? '+' : '-';
        printf("%c %.*s\n", prefix, (int)s->text_len, s->text);
    }
}
