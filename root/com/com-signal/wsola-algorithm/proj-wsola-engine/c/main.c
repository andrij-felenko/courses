#include <stdlib.h>
#include <string.h>
#include <math.h>

#define WSOLA_PI 3.14159265358979323846

typedef struct {
    int frame_size;     /* N: розмір кадру аналізу й синтезу */
    int synth_hop;      /* Hs: крок синтезу (N / 2) */
    int seek_range;     /* Δ: радіус пошуку зміщення */
    int template_size;  /* L: довжина еталонного шаблону */
    float tempo;        /* α: коефіцієнт темпу */

    float *window;      /* вагові коефіцієнти вікна Ганна */
    float *in_buf;      /* кільцевий вхідний буфер */
    int in_cap;         /* місткість вхідного буфера */
    int in_len;         /* кількість доступних відліків */

    float *out_buf;     /* буфер акумуляції overlap-add */
    int out_cap;        /* місткість вихідного буфера */
    int out_len;        /* кількість готових відліків для вивантаження */

    int last_tau;       /* попередня позиція зсуву τ_{k-1} */
    float ana_pos;      /* накопичена номінальна позиція аналізу k·Ha */
} wsola_stream_t;

/* Ініціалізація структури потокового масштабування */
wsola_stream_t* wsola_create(int frame_size, int seek_range, float tempo) {
    wsola_stream_t *w = (wsola_stream_t*)malloc(sizeof(wsola_stream_t));
    if (!w) return NULL;

    w->frame_size = frame_size;
    w->synth_hop = frame_size / 2;
    w->seek_range = seek_range;
    w->template_size = frame_size / 2;
    w->tempo = tempo;

    /* Обчислення вікна Ганна: w[n] = 0.5 * (1 - cos(2*pi*n / N)) */
    w->window = (float*)malloc(sizeof(float) * frame_size);
    for (int i = 0; i < frame_size; ++i) {
        w->window[i] = 0.5f * (1.0f - cosf(2.0f * (float)WSOLA_PI * i / (float)frame_size));
    }

    w->in_cap = (frame_size + seek_range) * 4;
    w->in_buf = (float*)calloc(w->in_cap, sizeof(float));
    w->in_len = 0;

    w->out_cap = frame_size * 4;
    w->out_buf = (float*)calloc(w->out_cap, sizeof(float));
    w->out_len = 0;

    w->last_tau = 0;
    w->ana_pos = 0.0f;

    return w;
}

/* Звільнення ресурсів */
void wsola_destroy(wsola_stream_t *w) {
    if (!w) return;
    free(w->window);
    free(w->in_buf);
    free(w->out_buf);
    free(w);
}

/* Додавання нових вхідних відліків у буфер */
int wsola_push_input(wsola_stream_t *w, const float *src, int count) {
    if (w->in_len + count > w->in_cap) {
        /* Зсув наявних даних на початок буфера */
        if (w->in_len > 0) {
            memmove(w->in_buf, w->in_buf + (w->in_cap - w->in_len), sizeof(float) * w->in_len);
        }
    }
    memcpy(w->in_buf + w->in_len, src, sizeof(float) * count);
    w->in_len += count;
    return count;
}

/* Знаходження найкращого зсуву δ у вікні [-seek_range, +seek_range] */
static int find_best_shift(const wsola_stream_t *w, int base_pos, int ref_pos) {
    float best_corr = -1e30f;
    int best_delta = 0;

    for (int d = -w->seek_range; d <= w->seek_range; ++d) {
        int cand_pos = base_pos + d;
        if (cand_pos < 0 || cand_pos + w->template_size > w->in_len) {
            continue;
        }

        float corr = 0.0f;
        for (int m = 0; m < w->template_size; ++m) {
            corr += w->in_buf[ref_pos + m] * w->in_buf[cand_pos + m];
        }

        if (corr > best_corr) {
            best_corr = corr;
            best_delta = d;
        }
    }

    return best_delta;
}

/* Виконання одного кроку синтезу кадру WSOLA */
int wsola_process_frame(wsola_stream_t *w) {
    int nom_pos = (int)w->ana_pos;
    int req_lookahead = nom_pos + w->seek_range + w->frame_size;

    /* Перевірка достатності даних у вхідному потоці */
    if (w->in_len < req_lookahead) {
        return 0; /* бракує відліків, чекаємо наступної порції */
    }

    /* Опорна точка природного продовження: ref = τ_{k-1} + Hs */
    int ref_pos = w->last_tau + w->synth_hop;
    if (ref_pos + w->template_size > w->in_len) {
        ref_pos = nom_pos;
    }

    /* Пошук оптимального зміщення δ_k */
    int delta = find_best_shift(w, nom_pos, ref_pos);
    int tau_k = nom_pos + delta;

    /* Накладання вікна та додавання у вихідний акумулятор */
    for (int n = 0; n < w->frame_size; ++n) {
        w->out_buf[n] += w->in_buf[tau_k + n] * w->window[n];
    }

    w->out_len += w->synth_hop;
    w->last_tau = tau_k;
    w->ana_pos += (float)w->synth_hop * w->tempo;

    /* Видалення обробленої історії з вхідного буфера */
    int consume = w->synth_hop;
    if (consume > 0 && consume <= w->in_len) {
        memmove(w->in_buf, w->in_buf + consume, sizeof(float) * (w->in_len - consume));
        w->in_len -= consume;
        w->last_tau -= consume;
        w->ana_pos -= (float)consume;
    }

    return 1;
}

/* Отримання готових відліків */
int wsola_pull_output(wsola_stream_t *w, float *dst, int max_count) {
    int to_read = (w->out_len < max_count) ? w->out_len : max_count;
    if (to_read <= 0) return 0;

    memcpy(dst, w->out_buf, sizeof(float) * to_read);

    /* Зсув вихідного буфера перекриття-додавання */
    memmove(w->out_buf, w->out_buf + to_read, sizeof(float) * (w->out_cap - to_read));
    memset(w->out_buf + (w->out_cap - to_read), 0, sizeof(float) * to_read);
    w->out_len -= to_read;

    return to_read;
}
