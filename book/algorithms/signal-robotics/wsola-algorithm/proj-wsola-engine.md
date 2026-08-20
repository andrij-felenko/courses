# ⚙️ Потоковий рушій масштабування аудіо WSOLA

Повна реалізація алгоритму WSOLA для потокової обробки дискретного аудіосигналу в реальному часі. Рушій організовано за принципом інкрементального крокового автомата: дані надходять у кільцевий вхідний буфер порціями довільного розміру, обробляються з урахуванням мінімально необхідного заглядання вперед (*lookahead*), після чого синтезований сигнал вивантажується з буфера перекриття-додавання без затримок пам'яті.

### Архітектура потокової обробки та кільцева буферизація

Потоковий процесор масштабування аудіо повинен розв'язувати задачу неперервної обробки аудіопотоку з довільними розмірами блоків, які надходять від драйвера звукової карти або мережевого сокета. На відміну від пакетної (офлайн) обробки всього файлу, потоковий рушій підтримує внутрішній стан між послідовними викликами:
1. **Збереження історії аналізу:** Щоб побудувати еталонний шаблон `x_ref = x[τ_{k-1} + Hₛ]`, рушій зобов'язаний зберігати в пам'яті сегмент вхідного сигналу попереднього кадру навіть після того, як його частина вже була відтворена.
2. **Гарантія заглядання вперед (*Lookahead*):** Для сканування кандидатів у діапазоні `[k · Hₐ − Δ, k · Hₐ + Δ]` та взяття повного кадру довжиною `N` вхідний буфер повинен містити щонайменше `nom_pos + seek_range + frame_size` відліків.
3. **Акумуляція перекриттів у вихідному масиві:** Вихідний буфер працює як регістр зсуву довжиною `N + Hₛ`, де відбувається накладання спадних та наростаючих гілок вікон Ганна.

```
Мінімальний обсяг вхідних даних для одного кроку:
LOOKAHEAD = SEEK_RANGE + FRAME_SIZE
```

### Покроковий життєвий цикл виклику `wsola_process_frame`

Кожен виклик функції кроку виконує суворо детерміновану послідовність операцій:
- **Перевірка готовності:** Якщо кількість накопичених у буфері відліків `in_len` менша за необхідний рівень `req_lookahead`, функція повертає `0`, сигналізуючи системі про необхідність отримання нових даних від джерела.
- **Обчислення координат еталону:** Опорна точка `ref_pos` визначається як `last_tau + synth_hop`. Якщо через початковий запуск або граничний стан ця точка виходить за межі буфера, алгоритм автоматично підхоплює номінальну точку `nom_pos`.
- **Кореляційний пошук:** Внутрішній цикл перебирає всі цілочислові зміщення `d ∈ [-seek_range, +seek_range]`, обчислюючи скалярний добуток еталонного відрізка з кандидатом. Позиція з максимальним значенням суми добутків фіксується як оптимальне зміщення `delta`.
- **Віконне зважування та OLA:** Зріз вхідного сигналу довжиною `frame_size` від точки `tau_k = nom_pos + delta` поелементно множиться на попередньо розраховану таблицю вікна Ганна й підсумовується з наявними значеннями у вихідному акумуляторі `out_buf`.
- **Зсув часової шкали:** Із вхідного буфера вилучається `synth_hop` відпрацьованих відліків шляхом копіювання залишку пам'яті, а лічильник вихідних відліків `out_len` збільшується на `synth_hop`.

### Реалізація на C та C++

:::tabs
```c
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
```
```cpp
#include <vector>
#include <cmath>
#include <algorithm>
#include <numbers>
#include <span.h>

class WsolaEngine {
public:
    WsolaEngine(int frame_size, int seek_range, float tempo)
        : frame_size_(frame_size),
          synth_hop_(frame_size / 2),
          seek_range_(seek_range),
          template_size_(frame_size / 2),
          tempo_(tempo),
          window_(frame_size, 0.0f),
          in_buf_((frame_size + seek_range) * 4, 0.0f),
          out_buf_(frame_size * 4, 0.0f) {
        
        // Генерація вікна Ганна із задоволенням умови COLA
        for (int i = 0; i < frame_size_; ++i) {
            window_[i] = 0.5f * (1.0f - std::cos(2.0f * std::numbers::pi_v<float> * i / frame_size_));
        }
    }

    void set_tempo(float tempo) noexcept {
        tempo_ = tempo;
    }

    void push_input(std::span<const float> samples) {
        in_buf_.insert(in_buf_.end() - in_buf_free_count(), samples.begin(), samples.end());
        in_valid_count_ += static_cast<int>(samples.size());
    }

    bool process_frame() {
        const int nom_pos = static_cast<int>(ana_pos_);
        const int req_lookahead = nom_pos + seek_range_ + frame_size_;

        if (in_valid_count_ < req_lookahead) {
            return false; // Очікування додаткових відліків
        }

        int ref_pos = last_tau_ + synth_hop_;
        if (ref_pos + template_size_ > in_valid_count_) {
            ref_pos = nom_pos;
        }

        const int delta = find_best_shift(nom_pos, ref_pos);
        const int tau_k = nom_pos + delta;

        // Внесок у буфер акумуляції overlap-add
        for (int n = 0; n < frame_size_; ++n) {
            out_buf_[n] += in_buf_[tau_k + n] * window_[n];
        }

        out_valid_count_ += synth_hop_;
        last_tau_ = tau_k;
        ana_pos_ += static_cast<float>(synth_hop_) * tempo_;

        // Просування часової шкали
        const int consume = synth_hop_;
        std::copy(in_buf_.begin() + consume, in_buf_.begin() + in_valid_count_, in_buf_.begin());
        in_valid_count_ -= consume;
        last_tau_ -= consume;
        ana_pos_ -= static_cast<float>(consume);

        return true;
    }

    int pull_output(std::span<float> dst) {
        const int count = std::min(static_cast<int>(dst.size()), out_valid_count_);
        if (count <= 0) return 0;

        std::copy_n(out_buf_.begin(), count, dst.begin());

        // Зсув буфера синтезу та очищення вивільненої зони
        std::copy(out_buf_.begin() + count, out_buf_.end(), out_buf_.begin());
        std::fill(out_buf_.end() - count, out_buf_.end(), 0.0f);
        out_valid_count_ -= count;

        return count;
    }

private:
    int find_best_shift(int base_pos, int ref_pos) const noexcept {
        float best_corr = -1e30f;
        int best_delta = 0;

        for (int d = -seek_range_; d <= seek_range_; ++d) {
            const int cand_pos = base_pos + d;
            if (cand_pos < 0 || cand_pos + template_size_ > in_valid_count_) {
                continue;
            }

            float corr = 0.0f;
            for (int m = 0; m < template_size_; ++m) {
                corr += in_buf_[ref_pos + m] * in_buf_[cand_pos + m];
            }

            if (corr > best_corr) {
                best_corr = corr;
                best_delta = d;
            }
        }
        return best_delta;
    }

    [[nodiscard]] int in_buf_free_count() const noexcept {
        return static_cast<int>(in_buf_.size()) - in_valid_count_;
    }

    int frame_size_{512};
    int synth_hop_{256};
    int seek_range_{128};
    int template_size_{256};
    float tempo_{1.0f};

    std::vector<float> window_;
    std::vector<float> in_buf_;
    int in_valid_count_{0};

    std::vector<float> out_buf_;
    int out_valid_count_{0};

    int last_tau_{0};
    float ana_pos_{0.0f};
};
```
:::

### Гарантії реального часу та безалокаційний гарячий шлях

У системах низької затримки (наприклад, усередині аудіоколбека драйвера ALSA, PulseAudio, JACK або CoreAudio) виконання динамічних виділень пам'яті (`malloc`, `new`) або викликів блокувальних примітивів синхронізації (`mutex`, `semaphore`) категорично заборонене через ризик виникнення непередбачуваного спустошення буфера (*buffer underrun*).

Представлений рушій WSOLA відповідає суворим критеріям твердого реального часу:
1. **Попереднє виділення всіх буферів:** Усі масиви пам'яті (вхідний кільцевий буфер, вихідний акумулятор перекриття-додавання, таблиця вагових коефіцієнтів вікна) виділяються одноразово під час виклику конструктора або функції ініціалізації.
2. **Детермінований час виконання (WCET):** Кількість операцій у внутрішньому циклі `find_best_shift` строго фіксована і становить `(2 · seek_range + 1) · template_size` множень і додавань, що гарантує стабільний час обробки кожного кадру незалежно від амплітуди чи спектра сигналу.
3. **Безпека зміни темпу на льоту:** Функція `wsola_set_tempo` лише модифікує коефіцієнт приросту номінальної позиції `ana_pos`. Оскільки опорний шаблон завжди прив'язаний до точки `last_tau + synth_hop`, зміна темпу відбувається плавно на найближчому кадрі без фазового розриву, тріску чи необхідності очищення буферів.

### Векторизація SIMD та робота з фіксованою комою

Гарячим місцем алгоритму є внутрішнє обчислення скалярного добутку векторів. Для сучасних мікропроцесорів та DSP-ядер застосовують апаратну векторизацію:

- **Векторизація через ARM NEON:** На архітектурах Cortex-A / Apple Silicon застосовують інструкції `vld1q_f32` та `vmlaq_f32`. Це дозволяє обробляти по чотири 32-бітні числа з рухомою комою за один машинний такт, підвищуючи продуктивність корелятора в 3.5–3.8 раза.
- **Векторизація через AVX2 / FMA:** На процесорах x86_64 інструкція `_mm256_fmadd_ps` завантажує вісім відліків у 256-бітний регістр YMM, виконуючи одночасне множення й акумуляцію без додаткових витрат на округлення.
- **Цілочислова арифметика Q15/Q31 на Cortex-M4:** На мікроконтролерах без блоку подвійної точності FPU відліки аудіо нормалізують до 16-бітного формату Q15. Для обчислення скалярного добутку використовують інструкцію ядра `SMLAL` (32-бітне множення двох 16-бітних чисел з накопиченням у 64-бітний акумулятор), що повністю запобігає переповненню розрядної сітки.

### Інтеграція у конвеєр приховування втрат пакетів (PLC) та адаптації джитера

У сучасних протоколах голосового зв'язку (WebRTC, VoIP) рушій WSOLA є серцевиною підсистеми управління мережевим тремтінням (*jitter buffer*). Коли мережеві пакети надходять із затримкою або накопичуються у великій кількості, рушій виконує динамічну підгонку тривалості:
- **Збільшення черги (Buffer Bloat):** Якщо буфер переповнюється, рушій плавно встановлює темп `α = 1.05`–`1.10`. Відтворення незначно прискорюється, черга спорожнюється без відчутної для слухача зміни висоти голосу або швидкості мови.
- **Загроза спустошення (Buffer Starvation):** Якщо надходження наступного пакета затримується, рушій знижує темп до `α = 0.90`–`0.95`, розтягуючи наявні залишки звуку й надаючи мережі додатковий час для доставки загубленого пакета без виникнення мертвої тиші.
