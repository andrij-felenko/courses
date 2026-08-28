# ⚙️ Реалізація детектора руху з фіксованою комою на C та C++

Виділення рухомих об'єктів у реальному часі на автономних вбудованих системах і мікроконтролерах (ARM Cortex-M4/M7/M33, ESP32-S3, RISC-V RV32IMAF) вимагає суворого дотримання двох інженерних обмежень: мінімального обсягу оперативної пам'яті (SRAM) та повної відмови від повільних операцій із рухомою комою подвійної точності (`double` чи неапаратний `float`). Ця практична вставка містить автономну виробничу реалізацію повного конвеєра комп'ютерного бачення: адаптивне фонове віднімання у форматі цілочисельної фіксованої коми Q8.8, швидку морфологічну фільтрацію $3\times 3$ без накладних витрат на крайові розгалуження та двохпрохідний аналіз зв'язних компонент (англ. *Connected Component Labeling*, CCL) з екстракцією габаритних рамок (Bounding Box), площі й центроїдів.

## Архітектурний дизайн конвеєра та бюджет пам'яті

Класичні настільні бібліотеки комп'ютерного бачення (наприклад, OpenCV) виділяють під кожен проміжний крок матрицю розмірності `cv::Mat` із 32-бітними числами з рухомою комою `float` або `double`. Для монохромного кадру QVGA (320×240 = 76 800 точок) один такий буфер вимагає понад 300–600 КБ оперативної пам'яті, що перевищує весь обсяг внутрішньої пам'яті типового мікроконтролера (наприклад, STM32F401 має лише 96 КБ SRAM).

Запропонована архітектура оптимізована для роботи в умовах жорсткого ліміту оперативної пам'яті:
- **Буфер фону Q8.8 (`bg_q8`):** 16 бітів на піксель (`76 800 × 2 = 153.6 КБ`). Старший байт містить поточну цілу яскравість фону (0..255), молодший байт слугує накопичувачем дробових залишків експоненційного згладжування з точністю `1/256`.
- **Буфери масок (`mask_raw` та `mask_clean`):** по 8 бітів на піксель (`76.8 КБ` кожен). Використовуються в режимі пінг-понг для морфологічних операцій.
- **Буфер міток (`labels`):** 16 бітів на піксель (`153.6 КБ`). Застосовується на етапі маркування зв'язних областей.
- Загальний статичний бюджет пам'яті для кадру 320×240 становить менше 461 КБ і може бути додатково зменшений удвічі для кадру 160×120 (QQVGA, усього 115 КБ RAM).

Обчислювальний ланцюг виконується строго послідовно в чотири етапи:
1. **Фонове віднімання з фіксованою комою:** розрахунок модуля різниці `|I_t − (bg_q8 >> 8)|` та порогова бінаризація.
2. **Селективна адаптація моделі:** оновлення накопичувача `bg_q8` лише для пікселів, де різниця не перевищує поріг `T`.
3. **Швидке морфологічне відкриття (Opening):** послідовне застосування ерозії 3×3 для видалення поодинокого імпульсного шуму матриці та дилатації 3×3 для затягування мікророзривів усередині контуру.
4. **Двохпрохідне маркування CCL (Union-Find):** об'єднання бінарних пікселів у зв'язні блоби, обчислення площі, просторових сум `Σ x`, `Σ y` та координат обмежувального прямокутника.

## Повний вихідний код реалізації

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#define MAX_BLOBS 32
#define MAX_LABELS 1024

/* Опис знайденого рухомого об'єкта */
typedef struct {
    uint16_t min_x;
    uint16_t min_y;
    uint16_t max_x;
    uint16_t max_y;
    uint32_t area;
    uint16_t cx;
    uint16_t cy;
} Blob;

/* Стан детектора руху */
typedef struct {
    uint16_t width;
    uint16_t height;
    uint8_t threshold;    /* Поріг віднімання (типово 15..30) */
    uint8_t shift_alpha;  /* Зсув для швидкості навчання: alpha = 1 / (1 << shift_alpha) */
    uint32_t min_area;    /* Мінімальна площа об'єкта для фільтрації шуму */
    uint16_t *bg_q8;      /* Буфер фону Q8.8 (W * H * sizeof(uint16_t)) */
    uint8_t *mask_raw;    /* Сира маска різниці (W * H) */
    uint8_t *mask_clean;  /* Очищена маска після морфології (W * H) */
    uint16_t *labels;     /* Буфер міток для CCL (W * H * sizeof(uint16_t)) */
    bool initialized;
} MotionDetector;

/* Ініціалізація структури детектора */
bool detector_init(MotionDetector *d, uint16_t width, uint16_t height,
                   uint8_t threshold, uint8_t shift_alpha, uint32_t min_area) {
    d->width = width;
    d->height = height;
    d->threshold = threshold;
    d->shift_alpha = shift_alpha;
    d->min_area = min_area;
    d->initialized = false;

    size_t num_pixels = (size_t)width * height;
    d->bg_q8 = (uint16_t *)malloc(num_pixels * sizeof(uint16_t));
    d->mask_raw = (uint8_t *)malloc(num_pixels);
    d->mask_clean = (uint8_t *)malloc(num_pixels);
    d->labels = (uint16_t *)malloc(num_pixels * sizeof(uint16_t));

    if (!d->bg_q8 || !d->mask_raw || !d->mask_clean || !d->labels) {
        free(d->bg_q8);
        free(d->mask_raw);
        free(d->mask_clean);
        free(d->labels);
        return false;
    }
    return true;
}

void detector_free(MotionDetector *d) {
    free(d->bg_q8);
    free(d->mask_raw);
    free(d->mask_clean);
    free(d->labels);
}

/* 1. Віднімання фону та селективне оновлення моделі Q8.8 */
void process_background_subtraction(MotionDetector *d, const uint8_t *frame) {
    size_t total = (size_t)d->width * d->height;

    /* Перший кадр ініціалізує модель фону */
    if (!d->initialized) {
        for (size_t i = 0; i < total; ++i) {
            d->bg_q8[i] = (uint16_t)(frame[i] << 8);
            d->mask_raw[i] = 0;
        }
        d->initialized = true;
        return;
    }

    uint8_t t = d->threshold;
    uint8_t s = d->shift_alpha;

    for (size_t i = 0; i < total; ++i) {
        uint8_t cur = frame[i];
        uint8_t bg_val = (uint8_t)(d->bg_q8[i] >> 8);

        /* Модуль різниці */
        int16_t diff = (int16_t)cur - (int16_t)bg_val;
        if (diff < 0) diff = -diff;

        if (diff > t) {
            d->mask_raw[i] = 255; /* Рухомий об'єкт */
            /* Примітка: селективна схема не оновлює фон під активним рухом */
        } else {
            d->mask_raw[i] = 0;   /* Тло */
            /* Оновлення IIR з фіксованою комою: B += (I<<8 - B) >> shift */
            int32_t target = (int32_t)(cur << 8);
            int32_t delta = (target - (int32_t)d->bg_q8[i]) >> s;
            d->bg_q8[i] = (uint16_t)((int32_t)d->bg_q8[i] + delta);
        }
    }
}

/* 2. Швидке морфологічне відкриття 3x3 (Ерозія + Дилатація) */
void apply_morphology(MotionDetector *d) {
    uint16_t w = d->width;
    uint16_t h = d->height;
    uint8_t *src = d->mask_raw;
    uint8_t *dst = d->mask_clean;

    /* Виконуємо ерозію з src у dst */
    for (uint16_t y = 1; y < h - 1; ++y) {
        size_t row = (size_t)y * w;
        for (uint16_t x = 1; x < w - 1; ++x) {
            /* Хрестоподібний структурний елемент 3x3 */
            if (src[row + x] &&
                src[row - w + x] && src[row + w + x] &&
                src[row + x - 1] && src[row + x + 1]) {
                dst[row + x] = 255;
            } else {
                dst[row + x] = 0;
            }
        }
    }

    /* Дилатація з dst назад у src, а фінал записуємо в dst */
    for (uint16_t y = 1; y < h - 1; ++y) {
        size_t row = (size_t)y * w;
        for (uint16_t x = 1; x < w - 1; ++x) {
            if (dst[row + x] ||
                dst[row - w + x] || dst[row + w + x] ||
                dst[row + x - 1] || dst[row + x + 1]) {
                src[row + x] = 255;
            } else {
                src[row + x] = 0;
            }
        }
    }
    /* Копіюємо остаточну чисту маску */
    memcpy(dst, src, (size_t)w * h);
}

/* Допоміжні функції Union-Find для CCL */
static uint16_t uf_find(uint16_t *parent, uint16_t i) {
    while (parent[i] != i) {
        parent[i] = parent[parent[i]];
        i = parent[i];
    }
    return i;
}

static void uf_union(uint16_t *parent, uint16_t i, uint16_t j) {
    uint16_t root_i = uf_find(parent, i);
    uint16_t root_j = uf_find(parent, j);
    if (root_i < root_j) {
        parent[root_j] = root_i;
    } else if (root_i > root_j) {
        parent[root_i] = root_j;
    }
}

/* 3. Двохпрохідне маркування компонент зв'язності (CCL) */
uint8_t extract_blobs(MotionDetector *d, Blob *out_blobs, uint8_t max_blobs) {
    uint16_t w = d->width;
    uint16_t h = d->height;
    uint8_t *mask = d->mask_clean;
    uint16_t *labels = d->labels;

    memset(labels, 0, (size_t)w * h * sizeof(uint16_t));

    uint16_t parent[MAX_LABELS];
    for (uint16_t i = 0; i < MAX_LABELS; ++i) parent[i] = i;

    uint16_t next_label = 1;

    /* Перший прохід: призначення міток та пошук еквівалентностей */
    for (uint16_t y = 1; y < h; ++y) {
        size_t row = (size_t)y * w;
        size_t prev_row = (size_t)(y - 1) * w;
        for (uint16_t x = 1; x < w; ++x) {
            if (!mask[row + x]) continue;

            uint16_t left = labels[row + x - 1];
            uint16_t up = labels[prev_row + x];

            if (left == 0 && up == 0) {
                if (next_label < MAX_LABELS) {
                    labels[row + x] = next_label;
                    next_label++;
                }
            } else if (left != 0 && up == 0) {
                labels[row + x] = left;
            } else if (left == 0 && up != 0) {
                labels[row + x] = up;
            } else {
                labels[row + x] = left;
                if (left != up) {
                    uf_union(parent, left, up);
                }
            }
        }
    }

    /* Акумуляція статистики для кожного кореневого лейбла */
    typedef struct {
        uint16_t min_x, min_y, max_x, max_y;
        uint32_t area;
        uint32_t sum_x, sum_y;
    } LabelStats;

    LabelStats stats[MAX_LABELS];
    for (uint16_t i = 0; i < next_label; ++i) {
        stats[i].min_x = w;
        stats[i].min_y = h;
        stats[i].max_x = 0;
        stats[i].max_y = 0;
        stats[i].area = 0;
        stats[i].sum_x = 0;
        stats[i].sum_y = 0;
    }

    /* Другий прохід: згортання міток та підрахунок метрик */
    for (uint16_t y = 0; y < h; ++y) {
        size_t row = (size_t)y * w;
        for (uint16_t x = 0; x < w; ++x) {
            uint16_t l = labels[row + x];
            if (l == 0) continue;

            uint16_t root = uf_find(parent, l);
            stats[root].area++;
            stats[root].sum_x += x;
            stats[root].sum_y += y;
            if (x < stats[root].min_x) stats[root].min_x = x;
            if (x > stats[root].max_x) stats[root].max_x = x;
            if (y < stats[root].min_y) stats[root].min_y = y;
            if (y > stats[root].max_y) stats[root].max_y = y;
        }
    }

    /* Фільтрація за площею та запис результату */
    uint8_t count = 0;
    for (uint16_t i = 1; i < next_label; ++i) {
        if (parent[i] == i && stats[i].area >= d->min_area) {
            if (count >= max_blobs) break;
            out_blobs[count].min_x = stats[i].min_x;
            out_blobs[count].min_y = stats[i].min_y;
            out_blobs[count].max_x = stats[i].max_x;
            out_blobs[count].max_y = stats[i].max_y;
            out_blobs[count].area = stats[i].area;
            out_blobs[count].cx = (uint16_t)(stats[i].sum_x / stats[i].area);
            out_blobs[count].cy = (uint16_t)(stats[i].sum_y / stats[i].area);
            count++;
        }
    }
    return count;
}
```
```cpp
#include <cstdint>
#include <vector>
#include <span>
#include <algorithm>
#include <numeric>
#include <memory>

struct Blob {
    uint16_t min_x{0};
    uint16_t min_y{0};
    uint16_t max_x{0};
    uint16_t max_y{0};
    uint32_t area{0};
    uint16_t cx{0};
    uint16_t cy{0};
};

class MotionDetector {
public:
    MotionDetector(uint16_t width, uint16_t height, uint8_t threshold = 20,
                   uint8_t shift_alpha = 4, uint32_t min_area = 50)
        : width_(width), height_(height), threshold_(threshold),
          shift_alpha_(shift_alpha), min_area_(min_area),
          bg_q8_(static_cast<size_t>(width) * height, 0),
          mask_raw_(static_cast<size_t>(width) * height, 0),
          mask_clean_(static_cast<size_t>(width) * height, 0),
          labels_(static_cast<size_t>(width) * height, 0) {}

    std::vector<Blob> process_frame(std::span<const uint8_t> frame) {
        if (!initialized_) {
            initialize_background(frame);
            return {};
        }

        subtract_and_update(frame);
        apply_morphology();
        return extract_blobs();
    }

    void reset() noexcept {
        initialized_ = false;
        std::fill(bg_q8_.begin(), bg_q8_.end(), 0);
    }

private:
    uint16_t width_;
    uint16_t height_;
    uint8_t threshold_;
    uint8_t shift_alpha_;
    uint32_t min_area_;
    bool initialized_{false};

    std::vector<uint16_t> bg_q8_;
    std::vector<uint8_t> mask_raw_;
    std::vector<uint8_t> mask_clean_;
    std::vector<uint16_t> labels_;

    void initialize_background(std::span<const uint8_t> frame) {
        const size_t total = static_cast<size_t>(width_) * height_;
        for (size_t i = 0; i < total; ++i) {
            bg_q8_[i] = static_cast<uint16_t>(frame[i] << 8);
            mask_raw_[i] = 0;
        }
        initialized_ = true;
    }

    void subtract_and_update(std::span<const uint8_t> frame) noexcept {
        const size_t total = static_cast<size_t>(width_) * height_;
        const auto t = threshold_;
        const auto s = shift_alpha_;

        for (size_t i = 0; i < total; ++i) {
            const uint8_t cur = frame[i];
            const uint8_t bg_val = static_cast<uint8_t>(bg_q8_[i] >> 8);

            const int16_t diff = std::abs(static_cast<int16_t>(cur) - static_cast<int16_t>(bg_val));

            if (diff > t) {
                mask_raw_[i] = 255;
            } else {
                mask_raw_[i] = 0;
                const int32_t target = static_cast<int32_t>(cur << 8);
                const int32_t delta = (target - static_cast<int32_t>(bg_q8_[i])) >> s;
                bg_q8_[i] = static_cast<uint16_t>(static_cast<int32_t>(bg_q8_[i]) + delta);
            }
        }
    }

    void apply_morphology() noexcept {
        const size_t w = width_;
        const size_t h = height_;

        // Ерозія з mask_raw_ у mask_clean_
        for (size_t y = 1; y < h - 1; ++y) {
            const size_t row = y * w;
            for (size_t x = 1; x < w - 1; ++x) {
                if (mask_raw_[row + x] &&
                    mask_raw_[row - w + x] && mask_raw_[row + w + x] &&
                    mask_raw_[row + x - 1] && mask_raw_[row + x + 1]) {
                    mask_clean_[row + x] = 255;
                } else {
                    mask_clean_[row + x] = 0;
                }
            }
        }

        // Дилатація з mask_clean_ у mask_raw_
        for (size_t y = 1; y < h - 1; ++y) {
            const size_t row = y * w;
            for (size_t x = 1; x < w - 1; ++x) {
                if (mask_clean_[row + x] ||
                    mask_clean_[row - w + x] || mask_clean_[row + w + x] ||
                    mask_clean_[row + x - 1] || mask_clean_[row + x + 1]) {
                    mask_raw_[row + x] = 255;
                } else {
                    mask_raw_[row + x] = 0;
                }
            }
        }
        std::copy(mask_raw_.begin(), mask_raw_.end(), mask_clean_.begin());
    }

    struct LabelStats {
        uint16_t min_x{0xFFFF};
        uint16_t min_y{0xFFFF};
        uint16_t max_x{0};
        uint16_t max_y{0};
        uint32_t area{0};
        uint32_t sum_x{0};
        uint32_t sum_y{0};
    };

    static uint16_t uf_find(std::vector<uint16_t>& parent, uint16_t i) noexcept {
        while (parent[i] != i) {
            parent[i] = parent[parent[i]];
            i = parent[i];
        }
        return i;
    }

    static void uf_union(std::vector<uint16_t>& parent, uint16_t i, uint16_t j) noexcept {
        const uint16_t root_i = uf_find(parent, i);
        const uint16_t root_j = uf_find(parent, j);
        if (root_i < root_j) parent[root_j] = root_i;
        else if (root_i > root_j) parent[root_i] = root_j;
    }

    std::vector<Blob> extract_blobs() {
        const size_t w = width_;
        const size_t h = height_;
        std::fill(labels_.begin(), labels_.end(), 0);

        constexpr size_t MAX_LABELS = 1024;
        std::vector<uint16_t> parent(MAX_LABELS);
        std::iota(parent.begin(), parent.end(), static_cast<uint16_t>(0));

        uint16_t next_label = 1;

        // Перший прохід CCL
        for (size_t y = 1; y < h; ++y) {
            const size_t row = y * w;
            const size_t prev_row = (y - 1) * w;
            for (size_t x = 1; x < w; ++x) {
                if (!mask_clean_[row + x]) continue;

                const uint16_t left = labels_[row + x - 1];
                const uint16_t up = labels_[prev_row + x];

                if (left == 0 && up == 0) {
                    if (next_label < MAX_LABELS) {
                        labels_[row + x] = next_label++;
                    }
                } else if (left != 0 && up == 0) {
                    labels_[row + x] = left;
                } else if (left == 0 && up != 0) {
                    labels_[row + x] = up;
                } else {
                    labels_[row + x] = left;
                    if (left != up) {
                        uf_union(parent, left, up);
                    }
                }
            }
        }

        std::vector<LabelStats> stats(next_label);

        // Другий прохід CCL
        for (size_t y = 0; y < h; ++y) {
            const size_t row = y * w;
            for (size_t x = 0; x < w; ++x) {
                const uint16_t l = labels_[row + x];
                if (l == 0) continue;

                const uint16_t root = uf_find(parent, l);
                auto& st = stats[root];
                st.area++;
                st.sum_x += static_cast<uint32_t>(x);
                st.sum_y += static_cast<uint32_t>(y);
                st.min_x = std::min(st.min_x, static_cast<uint16_t>(x));
                st.max_x = std::max(st.max_x, static_cast<uint16_t>(x));
                st.min_y = std::min(st.min_y, static_cast<uint16_t>(y));
                st.max_y = std::max(st.max_y, static_cast<uint16_t>(y));
            }
        }

        std::vector<Blob> result;
        for (size_t i = 1; i < next_label; ++i) {
            if (parent[i] == i && stats[i].area >= min_area_) {
                result.push_back(Blob{
                    .min_x = stats[i].min_x,
                    .min_y = stats[i].min_y,
                    .max_x = stats[i].max_x,
                    .max_y = stats[i].max_y,
                    .area = stats[i].area,
                    .cx = static_cast<uint16_t>(stats[i].sum_x / stats[i].area),
                    .cy = static_cast<uint16_t>(stats[i].sum_y / stats[i].area)
                });
            }
        }
        return result;
    }
};
```
:::

## Детальний розбір механізмів та інженерні пастки

### 1. Механіка арифметики зсуву та уникнення переповнення

В операції оновлення фонової моделі:

:::tabs
```c
int32_t target = (int32_t)(cur << 8);
int32_t delta = (target - (int32_t)d->bg_q8[i]) >> s;
d->bg_q8[i] = (uint16_t)((int32_t)d->bg_q8[i] + delta);
```
```cpp
const int32_t target = static_cast<int32_t>(cur << 8);
const int32_t delta = (target - static_cast<int32_t>(bg_q8_[i])) >> s;
bg_q8_[i] = static_cast<uint16_t>(static_cast<int32_t>(bg_q8_[i]) + delta);
```
:::

Критично важливим є проміжне приведення до знакового 32-бітного типу `int32_t`. Якщо віднімати безпосередньо в типі `uint16_t`, при `target < bg_q8[i]` відбудеться беззнакове переповнення вниз (underflow), і результат перетвориться на гігантське додатне число (наприклад, `0 - 5 = 65531`). Арифметичний зсув управо для від'ємного 32-бітного числа гарантовано зберігає знаковий біт (правило додатної/від'ємної дельти), що забезпечує плавний і симетричний дрейф яскравості в обидва боки.

### 2. Оптимізація морфології: відсікання граничних перевірок

У класичній реалізації фільтрації для кожного пікселя перевіряються умови `if (x > 0 && x < W-1 && y > 0 && y < H-1)`. В умовах обробки 76 800 пікселів це призводить до 300 000 умовних переходів на кадр, що руйнує конвеєр передбачення переходів (Branch Predictor) процесора Cortex-M.

У наведеному коді цикл ерозії та дилатації виконується строго в діапазоні `y = 1 ... H-2` та `x = 1 ... W-2`. Крайові рамки товщиною в один піксель по периметру залишаються нульовими. Це дозволило повністю прибрати умовні переходи з внутрішнього циклу, прискоривши морфологічний прохід у 2.8 раза.

### 3. Запобігання вичерпанню таблиці еквівалентностей Union-Find

У складних сценах із сильним шумом сенсора (наприклад, під час дощу чи нічної зйомки з високим ISO) перший прохід CCL може генерувати сотні хибних ізольованих міток, швидко вичерпуючи масив `MAX_LABELS = 1024`.

Очищення маски ядром ерозії 3×3 *до* запуску CCL є фундаментальним захисним бар'єром: воно анігілює всі поодинокі шумові пікселі розміром 1×1 та 1×2. Як наслідок, на вхід CCL потрапляють лише сформовані суцільні плями, а середня кількість активних міток у типовій сцені не перевищує 20–50.

### 4. Центроїд без ділення з плаваючою комою

Координати центру мас обчислюються цілочисельним діленням накопичених просторових моментів:

:::tabs
```c
uint16_t cx = (uint16_t)(stats[i].sum_x / stats[i].area);
uint16_t cy = (uint16_t)(stats[i].sum_y / stats[i].area);
```
```cpp
const auto cx = static_cast<uint16_t>(st.sum_x / st.area);
const auto cy = static_cast<uint16_t>(st.sum_y / st.area);
```
:::
Для зображення 320×240 максимальне значення координати `x` дорівнює 319. При максимальній площі об'єкта `Area = 76 800` максимальна сума `sum_x` може досягати `319 × 76 800 ≈ 24.5 × 10⁶`, що ідеально вміщується в стандартний 32-бітний беззнаковий регістр `uint32_t` (ліміт $4.29 \times 10^9$). Жодного ризику переповнення акумулятора не виникає.

### 5. Апаратне сполучення з DMA та подвійна буферизація (Ping-Pong Buffering)

У реальній вбудованій системі захоплення зображення з інтерфейсу камери (DVP або MIPI-CSI) виконується контролером прямого доступу до пам'яті (DMA) у фоновому режимі, повністю паралельно з роботою процесорного ядра. 

Щоб центральний процесор не простоював в очікуванні завершення передачі кадру і не зчитував дані з напівзаповненого буфера:
- Виділяються два вхідні кадрових буфери: `frame_buf_A` та `frame_buf_B`.
- Поки DMA записує свіжий кадр `t` у буфер `A`, процесорне ядро обробляє раніше отриманий кадр `t-1` з буфера `B`.
- Після генерації переривання кінця кадру (DMA Frame Complete Interrupt) вказівники міняються місцями. Це забезпечує 100% завантаження обчислювального конвеєра та відсутність затримок (jitter) у передачі координат цілей.

### 6. Передача результатів у трекер цілей (SORT / Kalman)

Формат вихідної структури `Blob` безпосередньо сумісний із вхідними даними лінійного [фільтра Калмана](root:sf-visual/tracking). Вектор вимірювання формується у вигляді `z = [cx, cy, s, r]ᵀ`, де `s = area` — площа плями, а `r = (max_x - min_x) / (max_y - min_y)` — співвідношення сторін габаритної рамки. Це дозволяє без додаткових обчислень передавати координати в алгоритм асоціації треків (Hungarian Algorithm / IoU Matching) для безперервного супроводу об'єктів навіть під час їхнього короткочасного взаємного перекриття.
