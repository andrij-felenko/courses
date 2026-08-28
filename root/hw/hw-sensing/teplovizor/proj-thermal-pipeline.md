# ⚙️ Повний конвеєр обробки тепловізійного кадру: NUC, BPR, AGC та Ironbow

Сирий вихід мікроболометричної матриці (FPA) являє собою масив 14-бітних цілих чисел (Digital Numbers, DN у діапазоні від 0 до 16383). У цьому сирому потоці корисний сигнал температурного рельєфу сцени практично непомітний: він повністю перекритий технологічним розкидом параметрів пікселів (просторово-фіксованим шумом FPN), дрейфом температури підкладки та наявністю непрацездатних («битих») елементів.

Щоб отримати чітку, контрастну 8-бітну термограму з частотою 30–60 кадрів на секунду, вбудований процесор обробки сигналів (Thermal ISP) повинен послідовно виконати чотири ключові алгоритмічні етапи:
1. **Заміну дефектних пікселів (BPR, Bad Pixel Replacement);**
2. **Двоточкову корекцію неоднорідності (Two-Point NUC) з відніманням кадру зачиненої шторки;**
3. **Адаптивне стиснення динамічного діапазону (Plateau Histogram Equalization, AGC);**
4. **Псевдокольорове кодування палітрою Ironbow для формування 24-бітного відеопотоку RGB888.**

## Архітектура конвеєра та математика обробки

### 1. Заміна дефектних пікселів (BPR)
Будь-яка мікроелектромеханічна матриця містить від 0.1% до 1% дефектних пікселів. Дефекти виникають через обрив підвісних ніжок мембрани, замикання на підкладку, нерівномірність осадження плівки оксиду ванадію або надмірний телеграфний шум (RTS, Random Telegraph Signal).

Під час заводського тестування формується бітова маска дефектів `Bad_Mask[x, y]`:
- `0` — піксель справний;
- `1` — піксель дефектний (не реагує на випромінювання або видає граничні значення 0 чи 16383).

У конвеєрі обробки кожен дефектний піксель замінюється середнім арифметичним або медіаною його валідних сусідів у вікні `3 × 3`. Алгоритм перевіряє 8 сусідніх координат, відкидає ті з них, які виходять за межі кадру або самі позначені як дефектні, та обчислює середнє значення лише по справних елементах. Якщо дефектними виявляються цілі кластери сусідніх пікселів, алгоритм розширює вікно пошуку до `5 × 5` або інтерполює значення за градієнтом рядків.

### 2. Корекція неоднорідності (NUC)
Сирий відгук `i`-го пікселя коригується двоточковою калібрувальною моделлю:
```
NUC_out[i] = (Raw[i] - Shutter[i]) · Gain[i] + Global_Baseline
```
де `Shutter[i]` — значення відліку, записане під час останнього закриття механічної шторки за температури корпусу сенсора, `Gain[i]` — коефіцієнт нормування чутливості, обчислений за двома чорними тілами на заводі, а `Global_Baseline` — зміщення середини динамічного діапазону (зазвичай 8192 для 14-бітної шкали).

### 3. Стиснення динамічного діапазону (Plateau Equalization)
Діапазон відліків після NUC становить 14 біт (16384 рівні), тоді як стандартні дисплеї та відеотракти працюють з 8 бітами на канал (0–255). Звичайне лінійне розтягування діапазону (`(DN - Min) * 255 / (Max - Min)`) працює незадовільно: якщо в холодній кімнаті (+20 °C) з'явиться гаряча паяльна станція (+350 °C), лінійне квантування виділить на всю кімнату лише 2–3 рівні яскравості, перетворивши навколишні предмети на суцільну темряву.

Класична еквелізація гістограми (Histogram Equalization, HE) має зворотний дефект: на ділянках із великою кількістю однакових пікселів (наприклад, чисте небо або холодна стіна) вона роздуває шум, створюючи неприємні візуальні плями.

Алгоритм **Plateau Equalization** розв'язує цю проблему через обмеження висоти стовпчиків гістограми:
1. Будується гістограма вхідного 14-бітного кадру `Hist[0..16383]`.
2. Значення кожного біна обмежується зверху порогом плато `Plateau_Limit`:
   ```
   Hist_Clipped[b] = min(Hist[b], Plateau_Limit)
   ```
3. Обчислюється кумулятивна функція розподілу (CDF):
   ```
   CDF[b] = ∑[k = 0 .. b] Hist_Clipped[b]
   ```
4. Значення кожного пікселя перераховується у вихідний 8-бітний код:
   ```
   Output_8bit[i] = (CDF[Pixel_Bin[i]] · 255) / CDF[16383]
   ```

Поріг `Plateau_Limit` вибирають динамічно залежно від дисперсії кадру. За малого розкиду температур поріг знижують, наближаючи перетворення до лінійного, що виключає штучне підсилення шумів однорідного фону.

### 4. Псевдокольорова палітра Ironbow
Отриманий 8-бітний монохромний кадр відображається в триколірний простір RGB888 за допомогою попередньо згенерованої таблиці перекодування `Ironbow_LUT[256]`. Палітра Ironbow імітує колір нагрівання металу:
- `0..63` (холодні ділянки): від чорного `(0, 0, 0)` до темно-синього `(0, 0, 255)`;
- `64..127`: від синього через фіолетовий до насиченого червоного `(255, 0, 128)`;
- `128..191`: від червоного через оранжевий до яскраво-жовтого `(255, 255, 0)`;
- `192..255` (найгарячіші ділянки): від жовтого до чистого білого `(255, 255, 255)`.

Нижче наведено повну реалізацію цього конвеєра на C та ідіоматичному C++.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

#define THERMAL_WIDTH   160
#define THERMAL_HEIGHT  120
#define THERMAL_PIXELS  (THERMAL_WIDTH * THERMAL_HEIGHT)
#define HIST_BINS       16384
#define PLATEAU_LIMIT   20

typedef struct {
    uint8_t r;
    uint8_t g;
    uint8_t b;
} Rgb888;

typedef struct {
    float   gain[THERMAL_PIXELS];        /* Калібрувальний коефіцієнт підсилення */
    int32_t offset[THERMAL_PIXELS];      /* Базовий зсув заводського калібрування */
    int32_t shutter[THERMAL_PIXELS];     /* Останній кадр закритої механічної шторки */
    uint8_t bad_mask[THERMAL_PIXELS];    /* 1 = дефектний («битий») піксель, 0 = справний */
    Rgb888  ironbow_lut[256];            /* Таблиця перекодування палітри Ironbow */
    float   global_baseline;             /* Цільовий базовий рівень NUC */
} ThermalPipelineContext;

/* Ініціалізація та генерація таблиці Ironbow LUT */
void thermal_pipeline_init(ThermalPipelineContext *ctx) {
    memset(ctx, 0, sizeof(ThermalPipelineContext));
    ctx->global_baseline = 8192.0f;

    for (int i = 0; i < THERMAL_PIXELS; ++i) {
        ctx->gain[i] = 1.0f;
        ctx->offset[i] = 0;
        ctx->shutter[i] = 0;
        ctx->bad_mask[i] = 0;
    }

    /* Генерація палітри Ironbow (256 кольорів: чорний -> синій -> червоний -> жовтий -> білий) */
    for (int i = 0; i < 256; ++i) {
        float x = (float)i / 255.0f;
        float r, g, b;

        if (x < 0.25f) {
            float t = x / 0.25f;
            r = 0.0f;
            g = 0.0f;
            b = t;
        } else if (x < 0.50f) {
            float t = (x - 0.25f) / 0.25f;
            r = t;
            g = 0.0f;
            b = 1.0f - 0.5f * t;
        } else if (x < 0.75f) {
            float t = (x - 0.50f) / 0.25f;
            r = 1.0f;
            g = t;
            b = 0.5f * (1.0f - t);
        } else {
            float t = (x - 0.75f) / 0.25f;
            r = 1.0f;
            g = 1.0f;
            b = t;
        }

        ctx->ironbow_lut[i].r = (uint8_t)(fminf(fmaxf(r * 255.0f, 0.0f), 255.0f));
        ctx->ironbow_lut[i].g = (uint8_t)(fminf(fmaxf(g * 255.0f, 0.0f), 255.0f));
        ctx->ironbow_lut[i].b = (uint8_t)(fminf(fmaxf(b * 255.0f, 0.0f), 255.0f));
    }
}

/* Оновлення кадру шторки під час спрацювання механічного калібратора */
void thermal_update_shutter(ThermalPipelineContext *ctx, const uint16_t *raw_shutter_frame) {
    for (int i = 0; i < THERMAL_PIXELS; ++i) {
        ctx->shutter[i] = (int32_t)raw_shutter_frame[i];
    }
}

/* Етап 1: NUC-корекція підсилення та зміщення шторки */
void thermal_apply_nuc(const ThermalPipelineContext *ctx, const uint16_t *raw_in, float *nuc_out) {
    for (int i = 0; i < THERMAL_PIXELS; ++i) {
        /* Віднімання ізотермічного зміщення шторки та множення на коефіцієнт підсилення */
        float diff = (float)((int32_t)raw_in[i] - ctx->shutter[i]);
        nuc_out[i] = diff * ctx->gain[i] + ctx->global_baseline;
    }
}

/* Етап 2: Заміна дефектних пікселів (BPR) просторовою медіаною/середнім */
void thermal_replace_bad_pixels(const ThermalPipelineContext *ctx, const float *img_in, float *img_out) {
    for (int y = 0; y < THERMAL_HEIGHT; ++y) {
        for (int x = 0; x < THERMAL_WIDTH; ++x) {
            int idx = y * THERMAL_WIDTH + x;

            if (ctx->bad_mask[idx] == 0) {
                img_out[idx] = img_in[idx];
                continue;
            }

            /* Усереднення по валідних 8-сусідах */
            float sum = 0.0f;
            int count = 0;

            for (int dy = -1; dy <= 1; ++dy) {
                int ny = y + dy;
                if (ny < 0 || ny >= THERMAL_HEIGHT) continue;

                for (int dx = -1; dx <= 1; ++dx) {
                    if (dx == 0 && dy == 0) continue;
                    int nx = x + dx;
                    if (nx < 0 || nx >= THERMAL_WIDTH) continue;

                    int nidx = ny * THERMAL_WIDTH + nx;
                    if (ctx->bad_mask[nidx] == 0) {
                        sum += img_in[nidx];
                        count++;
                    }
                }
            }

            img_out[idx] = (count > 0) ? (sum / (float)count) : ctx->global_baseline;
        }
    }
}

/* Етап 3: Plateau Equalization — стиснення 14-біт до 8-біт */
void thermal_plateau_equalization(const float *img_in, uint8_t *img_8bit_out) {
    uint32_t hist[HIST_BINS] = {0};
    uint32_t cdf[HIST_BINS] = {0};

    float min_val = img_in[0];
    float max_val = img_in[0];

    for (int i = 1; i < THERMAL_PIXELS; ++i) {
        if (img_in[i] < min_val) min_val = img_in[i];
        if (img_in[i] > max_val) max_val = img_in[i];
    }

    if (max_val - min_val < 1.0f) {
        memset(img_8bit_out, 128, THERMAL_PIXELS);
        return;
    }

    /* Побудова гістограми вхідних відліків */
    for (int i = 0; i < THERMAL_PIXELS; ++i) {
        int bin = (int)(img_in[i]);
        if (bin < 0) bin = 0;
        if (bin >= HIST_BINS) bin = HIST_BINS - 1;
        hist[bin]++;
    }

    /* Застосування плато-ліміту (Plateau Clipping) для усунення домінування однорідного фону */
    for (int b = 0; b < HIST_BINS; ++b) {
        if (hist[b] > PLATEAU_LIMIT) {
            hist[b] = PLATEAU_LIMIT;
        }
    }

    /* Обчислення кумулятивної функції розподілу (CDF) */
    uint32_t accum = 0;
    for (int b = 0; b < HIST_BINS; ++b) {
        accum += hist[b];
        cdf[b] = accum;
    }

    uint32_t total_clipped = cdf[HIST_BINS - 1];
    if (total_clipped == 0) total_clipped = 1;

    /* Відображення кожного пікселя в діапазон 0..255 */
    for (int i = 0; i < THERMAL_PIXELS; ++i) {
        int bin = (int)(img_in[i]);
        if (bin < 0) bin = 0;
        if (bin >= HIST_BINS) bin = HIST_BINS - 1;

        uint32_t val = (cdf[bin] * 255) / total_clipped;
        img_8bit_out[i] = (uint8_t)(val > 255 ? 255 : val);
    }
}

/* Етап 4: Застосування палітри Ironbow (конвертація 8-біт -> 24-біт RGB888) */
void thermal_apply_colormap(const ThermalPipelineContext *ctx, const uint8_t *img_8bit_in, Rgb888 *rgb_out) {
    for (int i = 0; i < THERMAL_PIXELS; ++i) {
        uint8_t val = img_8bit_in[i];
        rgb_out[i] = ctx->ironbow_lut[val];
    }
}

/* Головна функція обробки одного кадру */
void thermal_process_frame(const ThermalPipelineContext *ctx, const uint16_t *raw_frame, Rgb888 *rgb_output) {
    float nuc_buffer[THERMAL_PIXELS];
    float bpr_buffer[THERMAL_PIXELS];
    uint8_t gray_buffer[THERMAL_PIXELS];

    thermal_apply_nuc(ctx, raw_frame, nuc_buffer);
    thermal_replace_bad_pixels(ctx, nuc_buffer, bpr_buffer);
    thermal_plateau_equalization(bpr_buffer, gray_buffer);
    thermal_apply_colormap(ctx, gray_buffer, rgb_output);
}
```
```cpp
#include <cstdint>
#include <vector>
#include <array>
#include <span>
#include <algorithm>
#include <cmath>

struct Rgb888 {
    uint8_t r{0};
    uint8_t g{0};
    uint8_t b{0};
};

class ThermalPipeline {
public:
    static constexpr size_t Width = 160;
    static constexpr size_t Height = 120;
    static constexpr size_t PixelCount = Width * Height;
    static constexpr size_t HistBins = 16384;
    static constexpr uint32_t PlateauLimit = 20;

    ThermalPipeline() : globalBaseline_(8192.0f) {
        gain_.fill(1.0f);
        offset_.fill(0);
        shutter_.fill(0);
        badMask_.fill(0);
        initIronbowLut();
    }

    void updateShutter(std::span<const uint16_t, PixelCount> rawShutterFrame) noexcept {
        for (size_t i = 0; i < PixelCount; ++i) {
            shutter_[i] = static_cast<int32_t>(rawShutterFrame[i]);
        }
    }

    void setBadPixel(size_t x, size_t y, bool isBad) noexcept {
        if (x < Width && y < Height) {
            badMask_[y * Width + x] = isBad ? 1 : 0;
        }
    }

    void setGain(size_t x, size_t y, float gainVal) noexcept {
        if (x < Width && y < Height) {
            gain_[y * Width + x] = gainVal;
        }
    }

    void processFrame(std::span<const uint16_t, PixelCount> rawFrame,
                      std::span<Rgb888, PixelCount> rgbOutput) noexcept {
        std::array<float, PixelCount> nucBuffer;
        std::array<float, PixelCount> bprBuffer;
        std::array<uint8_t, PixelCount> grayBuffer;

        applyNuc(rawFrame, nucBuffer);
        replaceBadPixels(nucBuffer, bprBuffer);
        plateauEqualization(bprBuffer, grayBuffer);
        applyColormap(grayBuffer, rgbOutput);
    }

private:
    void initIronbowLut() noexcept {
        for (size_t i = 0; i < 256; ++i) {
            const float x = static_cast<float>(i) / 255.0f;
            float r{0.0f}, g{0.0f}, b{0.0f};

            if (x < 0.25f) {
                const float t = x / 0.25f;
                b = t;
            } else if (x < 0.50f) {
                const float t = (x - 0.25f) / 0.25f;
                r = t;
                b = 1.0f - 0.5f * t;
            } else if (x < 0.75f) {
                const float t = (x - 0.50f) / 0.25f;
                r = 1.0f;
                g = t;
                b = 0.5f * (1.0f - t);
            } else {
                const float t = (x - 0.75f) / 0.25f;
                r = 1.0f;
                g = 1.0f;
                b = t;
            }

            ironbowLut_[i] = Rgb888{
                static_cast<uint8_t>(std::clamp(r * 255.0f, 0.0f, 255.0f)),
                static_cast<uint8_t>(std::clamp(g * 255.0f, 0.0f, 255.0f)),
                static_cast<uint8_t>(std::clamp(b * 255.0f, 0.0f, 255.0f))
            };
        }
    }

    void applyNuc(std::span<const uint16_t, PixelCount> rawIn,
                  std::span<float, PixelCount> nucOut) const noexcept {
        for (size_t i = 0; i < PixelCount; ++i) {
            const float diff = static_cast<float>(static_cast<int32_t>(rawIn[i]) - shutter_[i]);
            nucOut[i] = diff * gain_[i] + globalBaseline_;
        }
    }

    void replaceBadPixels(std::span<const float, PixelCount> imgIn,
                          std::span<float, PixelCount> imgOut) const noexcept {
        for (size_t y = 0; y < Height; ++y) {
            for (size_t x = 0; x < Width; ++x) {
                const size_t idx = y * Width + x;
                if (badMask_[idx] == 0) {
                    imgOut[idx] = imgIn[idx];
                    continue;
                }

                float sum = 0.0f;
                int count = 0;

                for (int dy = -1; dy <= 1; ++dy) {
                    const int ny = static_cast<int>(y) + dy;
                    if (ny < 0 || ny >= static_cast<int>(Height)) continue;

                    for (int dx = -1; dx <= 1; ++dx) {
                        if (dx == 0 && dy == 0) continue;
                        const int nx = static_cast<int>(x) + dx;
                        if (nx < 0 || nx >= static_cast<int>(Width)) continue;

                        const size_t nidx = static_cast<size_t>(ny) * Width + static_cast<size_t>(nx);
                        if (badMask_[nidx] == 0) {
                            sum += imgIn[nidx];
                            ++count;
                        }
                    }
                }

                imgOut[idx] = (count > 0) ? (sum / static_cast<float>(count)) : globalBaseline_;
            }
        }
    }

    void plateauEqualization(std::span<const float, PixelCount> imgIn,
                             std::span<uint8_t, PixelCount> img8bitOut) const noexcept {
        std::array<uint32_t, HistBins> hist{};
        std::array<uint32_t, HistBins> cdf{};

        for (size_t i = 0; i < PixelCount; ++i) {
            const int bin = std::clamp(static_cast<int>(imgIn[i]), 0, static_cast<int>(HistBins - 1));
            hist[bin]++;
        }

        for (uint32_t& h : hist) {
            if (h > PlateauLimit) {
                h = PlateauLimit;
            }
        }

        uint32_t accum = 0;
        for (size_t b = 0; b < HistBins; ++b) {
            accum += hist[b];
            cdf[b] = accum;
        }

        const uint32_t totalClipped = std::max(cdf.back(), 1u);

        for (size_t i = 0; i < PixelCount; ++i) {
            const int bin = std::clamp(static_cast<int>(imgIn[i]), 0, static_cast<int>(HistBins - 1));
            const uint32_t val = (cdf[bin] * 255u) / totalClipped;
            img8bitOut[i] = static_cast<uint8_t>(std::min(val, 255u));
        }
    }

    void applyColormap(std::span<const uint8_t, PixelCount> img8bitIn,
                       std::span<Rgb888, PixelCount> rgbOut) const noexcept {
        for (size_t i = 0; i < PixelCount; ++i) {
            rgbOut[i] = ironbowLut_[img8bitIn[i]];
        }
    }

    std::array<float, PixelCount> gain_;
    std::array<int32_t, PixelCount> offset_;
    std::array<int32_t, PixelCount> shutter_;
    std::array<uint8_t, PixelCount> badMask_;
    std::array<Rgb888, 256> ironbowLut_;
    float globalBaseline_;
};
```
:::

## Радіометрія та обчислення абсолютної температури об'єкта

У радіометричних тепловізорах (наприклад, FLIR Lepton 3.5 або InfiRay Micro III) вихідний сигнал кожного пікселя перетворюється на абсолютну температуру в градусах Цельсія або Кельвінах.

Повна потужність теплового випромінювання `W_total`, що потрапляє на об'єктив, складається з трьох компонентів:
1. Власне випромінювання об'єкта з температурою `T_obj` та коефіцієнтом випромінювання `ε` (`0 < ε ≤ 1`), ослаблене пропусканням атмосфери `τ_atm`:
   ```
   W_1 = ε · τ_atm · W_bb(T_obj)
   ```
2. Відбите від поверхні об'єкта теплове випромінювання навколишнього середовища з температурою `T_refl`:
   ```
   W_2 = (1 - ε) · τ_atm · W_bb(T_refl)
   ```
3. Власне теплове випромінювання повітряного стовпа між камерою та об'єктом із температурою атмосфери `T_atm`:
   ```
   W_3 = (1 - τ_atm) · W_bb(T_atm)
   ```

Сумарне рівняння радіометрії:
```
W_total = ε · τ_atm · W_bb(T_obj) + (1 - ε) · τ_atm · W_bb(T_refl) + (1 - τ_atm) · W_bb(T_atm)
```

Вбудований процесор розв'язує це рівняння відносно `W_bb(T_obj)`, після чого перераховує потік у температуру через інвертовану формулу Планка:
```
T_obj = B / ln( R1 / (R2 · (W_bb(T_obj) + O)) + F )
```
де `R1, R2, B, O, F` — калібрувальні константи радіометричної моделі матриці, записані в незалежну пам'ять сенсора (EEPROM).

## Практичні особливості оптимізації для мікроконтролерів

При портуванні конвеєра на вбудовані платформи (ARM Cortex-M4/M7, ESP32-S3 або DSP) застосовують оптимізації продуктивності:
- **Фіксована кома Q15/Q16:** заміна дробових коефіцієнтів підсилення `Gain[i]` на цілочисельні 16-бітні множники дозволяє задіяти SIMD-інструкції векторного множення `SMLAD` або `VLOAD/VMUL`, що скорочує час NUC-корекції кадру 160×120 до менш ніж 1.5 мс.
- **Табличні обчислення (LUT):** генерація палітри кольору виконується один раз під час завантаження системи. У циклі обробки пікселя перетворення `8 біт -> 24 біти RGB` зводиться до прямого звернення за індексом у пам'яті SRAM.
- **Апаратний інтерфейс VoSPI та DMA-передача:** потоковий прийом сирих пакетів через SPI/MIPI за допомогою дескрипторів прямого доступу до пам'яті (DMA) дозволяє процесору обробляти попередній кадр у фоновому режимі, поки периферія збирає новий кадр без переривань на кожен байт.
