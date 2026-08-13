# ⚙️ Конвертер колірних сіток 4:4:4 ↔ 4:2:0 з КІХ-фільтрацією

У цьому проєкті реалізовано двостороннє перетворення графічного кадру між повнорозмірним форматом YUV 4:4:4 та плоским ущільненим форматом YUV420p (4:2:0). Основна прогалина багатьох наївних реалізацій полягає у спробі проредити колірні канали простим вилученням кожного другого відліку без низькочастотної фільтрації. Тут детально розібрано алгоритмічний конвеєр із 2D КІХ-фільтрацією проти аліасингу, математикою просторової інтерполяції, обробкою крайових умов та вирівнюванням пам'яті при роботі з реальними графічними буферами.

### Структура пам'яті та вирівнювання рядків (Stride / Pitch)

При програмуванні низькорівневих графічних конвеєрів та обробці відеопотоків важливо розрізняти тип організації колірних площин у оперативній пам'яті:

1. **Плоска організація (Planar / YUV420p / I420):**
   Усі три канали зберігаються в пам'яті як три суцільні незалежні масиви. Спочатку лежить повна площина яркості `Y` розміром `W × H` байтів, за нею — площина `Cb` розміром `(W/2) × (H/2)` байтів, а за нею — площина `Cr` аналогічного розміру. Загальний обсяг пам'яті становить строго `1.5 · W · H` байтів.
2. **Напівплоска організація (Semi-Planar / NV12 / NV21):**
   Використовується в апаратних декодерах GPU (NVIDIA NVENC, Intel QuickSync, Apple VideoToolbox) та камерах Android. Канал `Y` лежить окремим масивом `W × H`, а канали `Cb` та `Cr` об'єднані в єдиний чередувальний масив `CbCrCbCr...` розміром `W × (H/2)`. Це покращує локальність даних у L2-кеші відеокарти при виклику фрагментних шейдерів.
3. **Крок рядка в пам'яті (Stride або Pitch):**
   У реальних відеокадрах ширина рядка в пам'яті `stride` часто є більшою за реальну ширину зображення `width`. Драйвери відеокарт та SIMD-інструкції (AVX2, ARM NEON) вимагають вирівнювання початку кожного рядка на межу 16, 32 або 64 байти. Тому пряма адресація пікселя за формулою `y * width + x` призводить до викривлення кадру (*skewing*), якщо `stride != width`. У нашому коді показано базовий варіант для вирівняних буферів, де `stride = width`.

#### Схема адресації байтів у YUV420p (Planar):
```
Площина Y  (W × H байтів):     [ Y(0,0)   Y(1,0)   ...  Y(W-1, 0)   ]
                              [ Y(0,1)   Y(1,1)   ...  Y(W-1, 1)   ]
                              [ ...                                ]

Площина Cb ((W/2) × (H/2)):   [ Cb(0,0)  Cb(1,0)  ...  Cb(W/2-1, 0)]
                              [ Cb(0,1)  Cb(1,1)  ...  Cb(W/2-1, 1)]

Площина Cr ((W/2) × (H/2)):   [ Cr(0,0)  Cr(1,0)  ...  Cr(W/2-1, 0)]
                              [ Cr(0,1)  Cr(1,1)  ...  Cr(W/2-1, 1)]
```

### Алгоритмічна механіка 2D КІХ-фільтрації та білінійного відновлення

Процес конвертації між 4:4:4 та 4:2:0 складається з двох дзеркальних операцій.

#### Прямий хід: 4:4:4 → 4:2:0 (Downsampling із 2D ФНЧ)
Просте проріджування колірних каналів без фільтрації зрізає межу Найквіста з `0.5` до `0.25` циклів/піксель. Високі просторові частоти (наприклад, різкі межі кольорів) відбиваються в низькочастотну область, утворюючи колірні сходинки.

Щоб запобігти цьому, застосовується двовимірний КІХ-фільтр низьких частот із ядром `2×2`. Для кожної комірки `2×2` у повнорозмірному масиві `4:4:4` обчислюється зважена середня величина:

```
Cb_filtered(cx, cy) = (Cb(2x, 2y) + Cb(2x+1, 2y) + Cb(2x, 2y+1) + Cb(2x+1, 2y+1) + 2) / 4
```

Додавання цілочислового константного зсуву `+2` перед зсувом праворуч `>> 2` реалізує точне математичне округлення до найближчого цілого числа без використання повільних операцій із плаваючою крапкою.

Крайові випадки (наприклад, коли ширина або висота кадру є непарною) обробляються за допомогою затискання координат `std::min(x + 1, width - 1)`, що запобігає виходу за межі виділеного буфера та зчитуванню «сміття» з сусідніх ділянок пам'яті.

#### Зворотний хід: 4:2:0 → 4:4:4 (Upsampling білінійною інтерполяцією)
Для відновлення відсутніх колірних точок у кожному пікселі `(x, y)` обчислюються дробові координати у вихідній сітці 4:2:0. З урахуванням лівого фазування (H.264 standard) відносна координата колірного вузла становить:

```
cx_f = x / 2.0 - 0.25
cy_f = y / 2.0 - 0.25
```

За 4 найближчими колірними вузлами `(x0, y0)`, `(x1, y0)`, `(x0, y1)`, `(x1, y1)` розраховуються дробові зсуви `fx = cx_f - x0` та `fy = cy_f - y0`, після чого обчислюються чотири білінійні ваги:

```
w00 = (1 - fx) · (1 - fy)
w10 = fx · (1 - fy)
w01 = (1 - fx) · fy
w11 = fx · fy
```

Підсумкове значення кольору є лінійною комбінацією чотирьох сусідніх вузлів: `Cb = w00·Cb00 + w10·Cb10 + w01·Cb01 + w11·Cb11`.

### Крайові умови та некоректні розміри зображення

У реальних медіафайлах ширина чи висота кадру може не ділитися націло на 2 (наприклад, зображення 1921×1081 пікселів). Це створює два критичні ризики для стабільності програмного забезпечення:

1. **Непарний крок матриці:** Якщо `width = 1921`, то колірний масив має розмірність `(width / 2) = 960` пікселів. Останній піксель кадру з індексом `x = 1920` при обчисленні відносної координати звертатиметься до неіснуючої комірки `x1 = 961`.
2. **Захисне розширення буфера (Padding):** Кодери відео завжди вирівнюють внутрішній розмір макроблоків кадру до кратності 16 (або 32) пікселів. Кадр 1921×1081 у пам'яті розширюється до 1936×1088 пікселів, а крайні пікселі заповнюються дублюванням крайніх кольорів (*clamp-to-edge*).

У нашому коді для захисту від виходу за межі використано алгоритм насичення індексів:

```
x1 = (x0 + 1 < cw) ? x0 + 1 : x0;
y1 = (y0 + 1 < ch) ? y0 + 1 : y0;
```

Це гарантує, що при досягненні правих або нижніх межових пікселів функція інтерполяції не зчитує неініціалізовану пам'ять із купи (*heap*).

### Реалізація коду

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

// Структура плоского буфера YUV420p
typedef struct {
    int width;
    int height;
    uint8_t *y;
    uint8_t *cb;
    uint8_t *cr;
} Yuv420pFrame;

// Структура повнорозмірного буфера YUV444
typedef struct {
    int width;
    int height;
    uint8_t *y;
    uint8_t *cb;
    uint8_t *cr;
} Yuv444Frame;

// Виділення пам'яті під 4:4:4 кадр
Yuv444Frame* yuv444_create(int width, int height) {
    Yuv444Frame *frame = (Yuv444Frame*)malloc(sizeof(Yuv444Frame));
    if (!frame) return NULL;
    frame->width = width;
    frame->height = height;
    size_t size = (size_t)width * height;
    frame->y = (uint8_t*)malloc(size);
    frame->cb = (uint8_t*)malloc(size);
    frame->cr = (uint8_t*)malloc(size);
    if (!frame->y || !frame->cb || !frame->cr) {
        free(frame->y); free(frame->cb); free(frame->cr); free(frame);
        return NULL;
    }
    return frame;
}

void yuv444_free(Yuv444Frame *frame) {
    if (frame) {
        free(frame->y); free(frame->cb); free(frame->cr); free(frame);
    }
}

// Виділення пам'яті під 4:2:0 planar кадр
Yuv420pFrame* yuv420p_create(int width, int height) {
    Yuv420pFrame *frame = (Yuv420pFrame*)malloc(sizeof(Yuv420pFrame));
    if (!frame) return NULL;
    frame->width = width;
    frame->height = height;
    size_t y_size = (size_t)width * height;
    size_t c_size = (size_t)(width / 2) * (height / 2);
    frame->y = (uint8_t*)malloc(y_size);
    frame->cb = (uint8_t*)malloc(c_size);
    frame->cr = (uint8_t*)malloc(c_size);
    if (!frame->y || !frame->cb || !frame->cr) {
        free(frame->y); free(frame->cb); free(frame->cr); free(frame);
        return NULL;
    }
    return frame;
}

void yuv420p_free(Yuv420pFrame *frame) {
    if (frame) {
        free(frame->y); free(frame->cb); free(frame->cr); free(frame);
    }
}

// Пряме субдискретування 4:4:4 -> 4:2:0 з антиаліасинговим КІХ 2x2
void yuv444_to_420p(const Yuv444Frame *src, Yuv420pFrame *dst) {
    int w = src->width;
    int h = src->height;

    // 1. Канал Y копіюється без змін
    memcpy(dst->y, src->y, (size_t)w * h);

    // 2. Колірні канали фільтруються ФНЧ 2x2 та проріджуються
    int cw = w / 2;
    int ch = h / 2;

    for (int cy = 0; cy < ch; cy++) {
        for (int cx = 0; cx < cw; cx++) {
            int x0 = cx * 2;
            int y0 = cy * 2;
            int x1 = (x0 + 1 < w) ? x0 + 1 : x0;
            int y1 = (y0 + 1 < h) ? y0 + 1 : y0;

            // Зважене усереднення 2x2 для Cb
            uint32_t sum_cb = src->cb[y0 * w + x0] + src->cb[y0 * w + x1] +
                              src->cb[y1 * w + x0] + src->cb[y1 * w + x1];
            dst->cb[cy * cw + cx] = (uint8_t)((sum_cb + 2) >> 2);

            // Зважене усереднення 2x2 для Cr
            uint32_t sum_cr = src->cr[y0 * w + x0] + src->cr[y0 * w + x1] +
                              src->cr[y1 * w + x0] + src->cr[y1 * w + x1];
            dst->cr[cy * cw + cx] = (uint8_t)((sum_cr + 2) >> 2);
        }
    }
}

// Зворотне відновлення 4:2:0 -> 4:4:4 білінійною інтерполяцією
void yuv420p_to_444(const Yuv420pFrame *src, Yuv444Frame *dst) {
    int w = src->width;
    int h = src->height;
    int cw = w / 2;

    // 1. Канал Y копіюється без змін
    memcpy(dst->y, src->y, (size_t)w * h);

    // 2. Білінійна інтерполяція Cb та Cr для кожної точки Y
    for (int y = 0; y < h; y++) {
        for (int x = 0; x < w; x++) {
            // Відносні координати в колірній сітці
            float cx_f = (float)x / 2.0f - 0.25f;
            float cy_f = (float)y / 2.0f - 0.25f;

            int x0 = (int)cx_f;
            int y0 = (int)cy_f;
            if (x0 < 0) x0 = 0;
            if (y0 < 0) y0 = 0;
            int x1 = (x0 + 1 < cw) ? x0 + 1 : x0;
            int y1 = (y0 + 1 < (h / 2)) ? y0 + 1 : y0;

            float fx = cx_f - (float)x0;
            float fy = cy_f - (float)y0;
            if (fx < 0.0f) fx = 0.0f;
            if (fy < 0.0f) fy = 0.0f;

            // Ваги білінійної інтерполяції
            float w00 = (1.0f - fx) * (1.0f - fy);
            float w10 = fx * (1.0f - fy);
            float w01 = (1.0f - fx) * fy;
            float w11 = fx * fy;

            float val_cb = w00 * src->cb[y0 * cw + x0] + w10 * src->cb[y0 * cw + x1] +
                           w01 * src->cb[y1 * cw + x0] + w11 * src->cb[y1 * cw + x1];
            float val_cr = w00 * src->cr[y0 * cw + x0] + w10 * src->cr[y0 * cw + x1] +
                           w01 * src->cr[y1 * cw + x0] + w11 * src->cr[y1 * cw + x1];

            dst->cb[y * w + x] = (uint8_t)(val_cb + 0.5f);
            dst->cr[y * w + x] = (uint8_t)(val_cr + 0.5f);
        }
    }
}
```
```cpp
#include <iostream>
#include <vector>
#include <cstdint>
#include <algorithm>
#include <cmath>

// Клас кадру YUV444 з керуванням пам'яттю через RAII
class Yuv444Frame {
public:
    int width;
    int height;
    std::vector<uint8_t> y;
    std::vector<uint8_t> cb;
    std::vector<uint8_t> cr;

    Yuv444Frame(int w, int h) 
        : width(w), height(h), y(w * h), cb(w * h), cr(w * h) {}
};

// Клас плоского кадру YUV420p (4:2:0)
class Yuv420pFrame {
public:
    int width;
    int height;
    std::vector<uint8_t> y;
    std::vector<uint8_t> cb;
    std::vector<uint8_t> cr;

    Yuv420pFrame(int w, int h) 
        : width(w), height(h), 
          y(w * h), 
          cb((w / 2) * (h / 2)), 
          cr((w / 2) * (h / 2)) {}
};

// Перетворення 4:4:4 у 4:2:0 із 2D ФНЧ антиаліасингом
Yuv420pFrame convert_444_to_420p(const Yuv444Frame& src) {
    const int w = src.width;
    const int h = src.height;
    Yuv420pFrame dst(w, h);

    // 1. Канал Y копіюється без змін
    std::copy(src.y.begin(), src.y.end(), dst.y.begin());

    const int cw = w / 2;
    const int ch = h / 2;

    // 2. Двовимірна фільтрація КІХ 2x2 та субдискретизація Cb/Cr
    for (int cy = 0; cy < ch; ++cy) {
        for (int cx = 0; cx < cw; ++cx) {
            const int x0 = cx * 2;
            const int y0 = cy * 2;
            const int x1 = std::min(x0 + 1, w - 1);
            const int y1 = std::min(y0 + 1, h - 1);

            const uint32_t sum_cb = src.cb[y0 * w + x0] + src.cb[y0 * w + x1] +
                                    src.cb[y1 * w + x0] + src.cb[y1 * w + x1];
            dst.cb[cy * cw + cx] = static_cast<uint8_t>((sum_cb + 2) >> 2);

            const uint32_t sum_cr = src.cr[y0 * w + x0] + src.cr[y0 * w + x1] +
                                    src.cr[y1 * w + x0] + src.cr[y1 * w + x1];
            dst.cr[cy * cw + cx] = static_cast<uint8_t>((sum_cr + 2) >> 2);
        }
    }

    return dst;
}

// Зворотне відновлення 4:2:0 у 4:4:4 через білінійну інтерполяцію
Yuv444Frame convert_420p_to_444(const Yuv420pFrame& src) {
    const int w = src.width;
    const int h = src.height;
    const int cw = w / 2;
    const int ch = h / 2;
    Yuv444Frame dst(w, h);

    std::copy(src.y.begin(), src.y.end(), dst.y.begin());

    for (int y = 0; y < h; ++y) {
        for (int x = 0; x < w; ++x) {
            const float cx_f = std::max(0.0f, static_cast<float>(x) / 2.0f - 0.25f);
            const float cy_f = std::max(0.0f, static_cast<float>(y) / 2.0f - 0.25f);

            const int x0 = static_cast<int>(cx_f);
            const int y0 = static_cast<int>(cy_f);
            const int x1 = std::min(x0 + 1, cw - 1);
            const int y1 = std::min(y0 + 1, ch - 1);

            const float fx = cx_f - static_cast<float>(x0);
            const float fy = cy_f - static_cast<float>(y0);

            const float w00 = (1.0f - fx) * (1.0f - fy);
            const float w10 = fx * (1.0f - fy);
            const float w01 = (1.0f - fx) * fy;
            const float w11 = fx * fy;

            const float val_cb = w00 * src.cb[y0 * cw + x0] + w10 * src.cb[y0 * cw + x1] +
                                 w01 * src.cb[y1 * cw + x0] + w11 * src.cb[y1 * cw + x1];
            const float val_cr = w00 * src.cr[y0 * cw + x0] + w10 * src.cr[y0 * cw + x1] +
                                 w01 * src.cr[y1 * cw + x0] + w11 * src.cr[y1 * cw + x1];

            dst.cb[y * w + x] = static_cast<uint8_t>(std::clamp(val_cb + 0.5f, 0.0f, 255.0f));
            dst.cr[y * w + x] = static_cast<uint8_t>(std::clamp(val_cr + 0.5f, 0.0f, 255.0f));
        }
    }

    return dst;
}
```
:::

### Оптимізація продуктивності: SIMD та цілочислова арифметика

Представлений вище базовий код написаний для наочності алгоритму. У високонавантажених медіапроцесорах (FFmpeg, libjpeg-turbo, x264) прямі обчислення з плаваючою крапкою `float` для кожного пікселя є занадто повільними.

Використовуються дві ключові техніки оптимізації:

1. **Фіксована крапка (Fixed-point arithmetic):**
   Усі вагові коефіцієнти білінійної інтерполяції масштабуються в цілі числа із зсувом на 8 або 16 біт (`Q8` або `Q16`). Операція `val_cb = (w00 * Cb00 + w10 * Cb10 + ...) >> 8` виконується за один такт цілочислового арифметичного блоку ALU.
2. **Векторизація SIMD (AVX2 / ARM NEON):**
   Оскільки операції над колірними відліками є повністю незалежними для кожного пікселя, SIMD-інструкції (наприклад, `_mm256_avg_epu8` в x86 або `vhadd_u8` в ARM NEON) обчислюють усереднення 2×2 одразу для 16 або 32 пікселів паралельно за один векторний такт, прискорюючи конвертацію у 10–15 разів.
