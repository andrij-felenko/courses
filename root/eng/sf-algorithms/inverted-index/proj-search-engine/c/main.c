#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <stdbool.h>
#include <math.h>

#define BLOCK_SIZE 8
#define MAX_TERMS 1024

/* --- 1. Побайтове кодування змінної довжини (VByte / Varint) --- */

/* Кодування одного uint32_t числа у буфер VByte. Повертає кількість записаних байтів. */
size_t vbyte_encode(uint32_t val, uint8_t *out) {
    size_t bytes = 0;
    while (val >= 0x80) {
        out[bytes++] = (uint8_t)((val & 0x7F) | 0x80);
        val >>= 7;
    }
    out[bytes++] = (uint8_t)(val & 0x7F);
    return bytes;
}

/* Декодування одного uint32_t числа з буфера VByte. Зсуває вказівник читання. */
uint32_t vbyte_decode(const uint8_t **ptr) {
    uint32_t result = 0;
    uint32_t shift = 0;
    while (1) {
        uint8_t byte = **ptr;
        (*ptr)++;
        result |= (uint32_t)(byte & 0x7F) << shift;
        if (!(byte & 0x80)) {
            break;
        }
        shift += 7;
    }
    return result;
}

/* --- 2. Структури даних інвертованого індексу --- */

typedef struct {
    uint32_t max_doc_id;   /* Максимальний DocID у блоці для швидкого пропуску */
    size_t byte_offset;    /* Зміщення початку блоку в стисненому потоці */
} SkipBlock;

typedef struct {
    uint8_t *data;          /* Стиснений байтовий потік (VByte d-gaps + TF) */
    size_t data_len;
    size_t data_cap;
    SkipBlock *skips;       /* Масив скіп-вказівників над блоками */
    size_t skip_count;
    size_t skip_cap;
    uint32_t last_doc_id;   /* Останній доданий DocID для обчислення дельти */
    uint32_t doc_count;     /* Загальна кількість документів у постингу */
    size_t cur_block_items; /* Кількість елементів у поточному незавершеному блоці */
    size_t cur_block_start; /* Байт-зміщення поточного блоку */
} PostingList;

typedef struct {
    char term[64];
    PostingList postings;
} TermEntry;

typedef struct {
    TermEntry terms[MAX_TERMS];
    size_t term_count;
    uint32_t total_docs;
    double avg_doc_len;
    uint32_t doc_lengths[1024]; /* Довжини документів для BM25 */
} InvertedIndex;

/* Ініціалізація постингового списку */
void posting_list_init(PostingList *pl) {
    pl->data_cap = 64;
    pl->data_len = 0;
    pl->data = (uint8_t *)malloc(pl->data_cap);
    pl->skip_cap = 8;
    pl->skip_count = 0;
    pl->skips = (SkipBlock *)malloc(pl->skip_cap * sizeof(SkipBlock));
    pl->last_doc_id = 0;
    pl->doc_count = 0;
    pl->cur_block_items = 0;
    pl->cur_block_start = 0;
}

void posting_list_free(PostingList *pl) {
    free(pl->data);
    free(pl->skips);
}

/* Додавання документа до постингового списку */
void posting_list_append(PostingList *pl, uint32_t doc_id, uint32_t tf) {
    if (pl->doc_count == 0) {
        pl->cur_block_start = 0;
    }

    uint32_t dgap = (pl->doc_count == 0) ? doc_id : (doc_id - pl->last_doc_id);
    pl->last_doc_id = doc_id;
    pl->doc_count++;

    /* Запис d-gap та tf у VByte буфер */
    uint8_t buf[10];
    size_t enc_sz = vbyte_encode(dgap, buf);
    enc_sz += vbyte_encode(tf, buf + enc_sz);

    if (pl->data_len + enc_sz > pl->data_cap) {
        pl->data_cap *= 2;
        pl->data = (uint8_t *)realloc(pl->data, pl->data_cap);
    }
    memcpy(pl->data + pl->data_len, buf, enc_sz);
    pl->data_len += enc_sz;

    pl->cur_block_items++;
    if (pl->cur_block_items == BLOCK_SIZE) {
        /* Фіксація завершеного блоку в Skip Index */
        if (pl->skip_count >= pl->skip_cap) {
            pl->skip_cap *= 2;
            pl->skips = (SkipBlock *)realloc(pl->skips, pl->skip_cap * sizeof(SkipBlock));
        }
        pl->skips[pl->skip_count].max_doc_id = doc_id;
        pl->skips[pl->skip_count].byte_offset = pl->cur_block_start;
        pl->skip_count++;

        pl->cur_block_items = 0;
        pl->cur_block_start = pl->data_len;
    }
}

/* Фіналізація індексу: закриття останнього неповного блоку */
void posting_list_finalize(PostingList *pl) {
    if (pl->cur_block_items > 0) {
        if (pl->skip_count >= pl->skip_cap) {
            pl->skip_cap += 1;
            pl->skips = (SkipBlock *)realloc(pl->skips, pl->skip_cap * sizeof(SkipBlock));
        }
        pl->skips[pl->skip_count].max_doc_id = pl->last_doc_id;
        pl->skips[pl->skip_count].byte_offset = pl->cur_block_start;
        pl->skip_count++;
        pl->cur_block_items = 0;
    }
}

/* --- 3. Ітератор постингового списку зі Skip-підтримкою --- */

typedef struct {
    const PostingList *pl;
    const uint8_t *cursor;
    const uint8_t *end;
    size_t current_skip_idx;
    uint32_t current_doc_id;
    uint32_t current_tf;
    bool at_end;
} PostingIterator;

void iterator_init(PostingIterator *it, const PostingList *pl) {
    it->pl = pl;
    it->cursor = pl->data;
    it->end = pl->data + pl->data_len;
    it->current_skip_idx = 0;
    it->current_doc_id = 0;
    it->current_tf = 0;
    it->at_end = (pl->doc_count == 0);
    if (!it->at_end) {
        /* Читання першого запису */
        uint32_t dgap = vbyte_decode(&it->cursor);
        it->current_doc_id = dgap;
        it->current_tf = vbyte_decode(&it->cursor);
    }
}

/* Перехід до наступного елемента */
void iterator_next(PostingIterator *it) {
    if (it->cursor >= it->end) {
        it->at_end = true;
        return;
    }
    uint32_t dgap = vbyte_decode(&it->cursor);
    it->current_doc_id += dgap;
    it->current_tf = vbyte_decode(&it->cursor);
}

/* Стрибок (Advance / Skip) до документа з DocID >= target_doc */
void iterator_advance(PostingIterator *it, uint32_t target_doc) {
    if (it->at_end || it->current_doc_id >= target_doc) {
        return;
    }

    /* 1. Стрибок по скіп-індексу через цілі блоки */
    while (it->current_skip_idx + 1 < it->pl->skip_count &&
           it->pl->skips[it->current_skip_idx].max_doc_id < target_doc) {
        it->current_skip_idx++;
        it->cursor = it->pl->data + it->pl->skips[it->current_skip_idx].byte_offset;
        /* Перезапуск базового doc_id для нового блоку */
        if (it->current_skip_idx > 0) {
            it->current_doc_id = it->pl->skips[it->current_skip_idx - 1].max_doc_id;
        } else {
            it->current_doc_id = 0;
        }
    }

    /* 2. Лінійне сканування всередині цільового блоку */
    while (!it->at_end && it->current_doc_id < target_doc) {
        if (it->cursor >= it->end) {
            it->at_end = true;
            break;
        }
        uint32_t dgap = vbyte_decode(&it->cursor);
        it->current_doc_id += dgap;
        it->current_tf = vbyte_decode(&it->cursor);
    }
}

/* --- 4. Ранжування Okapi BM25 та перетин списків (AND) --- */

double compute_bm25(uint32_t tf, uint32_t doc_len, double avg_doc_len,
                    uint32_t total_docs, uint32_t doc_freq) {
    double k1 = 1.2;
    double b = 0.75;
    double idf = log(((double)total_docs - (double)doc_freq + 0.5) / ((double)doc_freq + 0.5) + 1.0);
    double b_scale = (1.0 - b) + b * ((double)doc_len / avg_doc_len);
    double tf_norm = ((double)tf * (k1 + 1.0)) / ((double)tf + k1 * b_scale);
    return idf * tf_norm;
}

void search_and_rank(InvertedIndex *idx, const char *term1, const char *term2) {
    PostingList *pl1 = NULL, *pl2 = NULL;
    for (size_t i = 0; i < idx->term_count; i++) {
        if (strcmp(idx->terms[i].term, term1) == 0) pl1 = &idx->terms[i].postings;
        if (strcmp(idx->terms[i].term, term2) == 0) pl2 = &idx->terms[i].postings;
    }

    if (!pl1 || !pl2) {
        printf("Один із термів не знайдено в індексі.\n");
        return;
    }

    PostingIterator it1, it2;
    iterator_init(&it1, pl1);
    iterator_init(&it2, pl2);

    printf("Результати пошуку [ %s AND %s ]:\n", term1, term2);

    while (!it1.at_end && !it2.at_end) {
        if (it1.current_doc_id == it2.current_doc_id) {
            uint32_t did = it1.current_doc_id;
            uint32_t dlen = idx->doc_lengths[did];
            double s1 = compute_bm25(it1.current_tf, dlen, idx->avg_doc_len, idx->total_docs, pl1->doc_count);
            double s2 = compute_bm25(it2.current_tf, dlen, idx->avg_doc_len, idx->total_docs, pl2->doc_count);
            double total_score = s1 + s2;

            printf("  -> DocID: %u | Довжина: %u | BM25 Скор: %.4f (TF1: %u, TF2: %u)\n",
                   did, dlen, total_score, it1.current_tf, it2.current_tf);

            iterator_next(&it1);
            iterator_next(&it2);
        } else if (it1.current_doc_id < it2.current_doc_id) {
            iterator_advance(&it1, it2.current_doc_id);
        } else {
            iterator_advance(&it2, it1.current_doc_id);
        }
    }
}

int main(void) {
    InvertedIndex idx;
    memset(&idx, 0, sizeof(idx));
    idx.total_docs = 100;
    idx.avg_doc_len = 150.0;
    for (uint32_t d = 0; d < 100; d++) {
        idx.doc_lengths[d] = 100 + (d * 7) % 120;
    }

    strcpy(idx.terms[0].term, "алгоритм");
    posting_list_init(&idx.terms[0].postings);
    strcpy(idx.terms[1].term, "пошук");
    posting_list_init(&idx.terms[1].postings);
    idx.term_count = 2;

    /* Додаємо документи до списків */
    posting_list_append(&idx.terms[0].postings, 5, 2);
    posting_list_append(&idx.terms[0].postings, 18, 1);
    posting_list_append(&idx.terms[0].postings, 42, 4);
    posting_list_append(&idx.terms[0].postings, 85, 1);
    posting_list_finalize(&idx.terms[0].postings);

    posting_list_append(&idx.terms[1].postings, 2, 1);
    posting_list_append(&idx.terms[1].postings, 18, 3);
    posting_list_append(&idx.terms[1].postings, 30, 1);
    posting_list_append(&idx.terms[1].postings, 42, 2);
    posting_list_append(&idx.terms[1].postings, 99, 1);
    posting_list_finalize(&idx.terms[1].postings);

    search_and_rank(&idx, "алгоритм", "пошук");

    posting_list_free(&idx.terms[0].postings);
    posting_list_free(&idx.terms[1].postings);
    return 0;
}
