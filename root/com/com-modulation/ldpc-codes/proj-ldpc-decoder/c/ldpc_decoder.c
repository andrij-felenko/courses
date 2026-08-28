/* ldpc_decoder.c — Промислова реалізація Min-Sum декодера мовою C */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <float.h>
#include <stdint.h>
#include <stdbool.h>

typedef struct {
    int num_v;          /* Кількість символьних вузлів (n) */
    int num_c;          /* Кількість перевірочних вузлів (m) */
    int num_edges;      /* Загальна кількість ребер |E| */
    
    /* Списки суміжності для перевірочних вузлів (CN) */
    int *cn_degrees;    /* Масив ступенів кожного CN [num_c] */
    int **cn_nodes;     /* cn_nodes[c][k] -> індекс VN */
    int **cn_edge_idx;  /* cn_edge_idx[c][k] -> глобальний індекс ребра */

    /* Списки суміжності для символьних вузлів (VN) */
    int *vn_degrees;    /* Масив ступенів кожного VN [num_v] */
    int **vn_nodes;     /* vn_nodes[v][k] -> індекс CN */
    int **vn_edge_idx;  /* vn_edge_idx[v][k] -> глобальний індекс ребра */

    /* Пам'ять повідомлень на ребрах */
    float *msg_v2c;     /* Повідомлення VN -> CN [num_edges] */
    float *msg_c2v;     /* Повідомлення CN -> VN [num_edges] */
} ldpc_decoder_t;

/* Ініціалізація та виділення пам'яті для структури декодера */
ldpc_decoder_t* ldpc_decoder_create(int num_v, int num_c, const int *h_matrix) {
    ldpc_decoder_t *dec = (ldpc_decoder_t*)calloc(1, sizeof(ldpc_decoder_t));
    if (!dec) return NULL;

    dec->num_v = num_v;
    dec->num_c = num_c;

    dec->cn_degrees = (int*)calloc(num_c, sizeof(int));
    dec->vn_degrees = (int*)calloc(num_v, sizeof(int));

    /* Підрахунок ступенів вузлів */
    int total_edges = 0;
    for (int i = 0; i < num_c; i++) {
        for (int j = 0; j < num_v; j++) {
            if (h_matrix[i * num_v + j] != 0) {
                dec->cn_degrees[i]++;
                dec->vn_degrees[j]++;
                total_edges++;
            }
        }
    }
    dec->num_edges = total_edges;

    dec->cn_nodes = (int**)malloc(num_c * sizeof(int*));
    dec->cn_edge_idx = (int**)malloc(num_c * sizeof(int*));
    for (int i = 0; i < num_c; i++) {
        dec->cn_nodes[i] = (int*)malloc(dec->cn_degrees[i] * sizeof(int));
        dec->cn_edge_idx[i] = (int*)malloc(dec->cn_degrees[i] * sizeof(int));
    }

    dec->vn_nodes = (int**)malloc(num_v * sizeof(int*));
    dec->vn_edge_idx = (int**)malloc(num_v * sizeof(int*));
    for (int j = 0; j < num_v; j++) {
        dec->vn_nodes[j] = (int*)malloc(dec->vn_degrees[j] * sizeof(int));
        dec->vn_edge_idx[j] = (int*)malloc(dec->vn_degrees[j] * sizeof(int));
    }

    dec->msg_v2c = (float*)calloc(total_edges, sizeof(float));
    dec->msg_c2v = (float*)calloc(total_edges, sizeof(float));

    /* Заповнення списків суміжності та індексів ребер */
    int *cn_curr = (int*)calloc(num_c, sizeof(int));
    int *vn_curr = (int*)calloc(num_v, sizeof(int));
    int edge_count = 0;

    for (int i = 0; i < num_c; i++) {
        for (int j = 0; j < num_v; j++) {
            if (h_matrix[i * num_v + j] != 0) {
                int e = edge_count++;
                int c_pos = cn_curr[i]++;
                int v_pos = vn_curr[j]++;

                dec->cn_nodes[i][c_pos] = j;
                dec->cn_edge_idx[i][c_pos] = e;

                dec->vn_nodes[j][v_pos] = i;
                dec->vn_edge_idx[j][v_pos] = e;
            }
        }
    }

    free(cn_curr);
    free(vn_curr);
    return dec;
}

/* Звільнення пам'яті декодера */
void ldpc_decoder_destroy(ldpc_decoder_t *dec) {
    if (!dec) return;
    for (int i = 0; i < dec->num_c; i++) {
        free(dec->cn_nodes[i]);
        free(dec->cn_edge_idx[i]);
    }
    free(dec->cn_nodes);
    free(dec->cn_edge_idx);

    for (int j = 0; j < dec->num_v; j++) {
        free(dec->vn_nodes[j]);
        free(dec->vn_edge_idx[j]);
    }
    free(dec->vn_nodes);
    free(dec->vn_edge_idx);

    free(dec->cn_degrees);
    free(dec->vn_degrees);
    free(dec->msg_v2c);
    free(dec->msg_c2v);
    free(dec);
}

/* Перевірка синдрому: H * c^T == 0 (mod 2) */
static bool check_syndrome(const ldpc_decoder_t *dec, const uint8_t *bits) {
    for (int i = 0; i < dec->num_c; i++) {
        int sum = 0;
        for (int k = 0; k < dec->cn_degrees[i]; k++) {
            int v = dec->cn_nodes[i][k];
            sum ^= bits[v];
        }
        if (sum != 0) return false;
    }
    return true;
}

/* Виконання декодування Min-Sum */
bool ldpc_decode_min_sum(ldpc_decoder_t *dec, const float *channel_llr, 
                         int max_iter, float norm_factor, uint8_t *out_bits) {
    /* Крок 1: Ініціалізація повідомлень v2c початковими канальними LLR */
    for (int j = 0; j < dec->num_v; j++) {
        for (int k = 0; k < dec->vn_degrees[j]; k++) {
            int e = dec->vn_edge_idx[j][k];
            dec->msg_v2c[e] = channel_llr[j];
        }
    }

    for (int iter = 0; iter < max_iter; iter++) {
        /* Крок 2: Оновлення CN -> VN (Фаза Перевірочних Вузлів) */
        for (int i = 0; i < dec->num_c; i++) {
            int deg = dec->cn_degrees[i];
            for (int k = 0; k < deg; k++) {
                int target_edge = dec->cn_edge_idx[i][k];
                
                int sign_prod = 1;
                float min_val = FLT_MAX;

                for (int m = 0; m < deg; m++) {
                    if (m == k) continue;
                    int src_edge = dec->cn_edge_idx[i][m];
                    float val = dec->msg_v2c[src_edge];

                    if (val < 0.0f) sign_prod = -sign_prod;
                    float abs_val = fabsf(val);
                    if (abs_val < min_val) min_val = abs_val;
                }

                dec->msg_c2v[target_edge] = norm_factor * sign_prod * min_val;
            }
        }

        /* Крок 3: Оновлення VN -> CN та обчислення апостеріорного LLR */
        for (int j = 0; j < dec->num_v; j++) {
            float total_llr = channel_llr[j];
            for (int k = 0; k < dec->vn_degrees[j]; k++) {
                int e = dec->vn_edge_idx[j][k];
                total_llr += dec->msg_c2v[e];
            }

            /* Тверде рішення для поточного біта */
            out_bits[j] = (total_llr < 0.0f) ? 1 : 0;

            /* Формування зовнішньої інформації q_{v -> c} */
            for (int k = 0; k < dec->vn_degrees[j]; k++) {
                int e = dec->vn_edge_idx[j][k];
                dec->msg_v2c[e] = total_llr - dec->msg_c2v[e];
            }
        }

        /* Крок 4: Перевірка зупинки за синдромом */
        if (check_syndrome(dec, out_bits)) {
            return true; /* Успішна збіжність */
        }
    }

    return false; /* Досягнуто максимальну кількість ітерацій */
}
