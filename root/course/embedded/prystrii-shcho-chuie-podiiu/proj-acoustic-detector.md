# ⚙️ Проєкт акустичного детектора подій на Cortex-M: I2S DMA, VAD, мел-банк та INT8 згортка

У цьому проєкті реалізовано повний наскрізний конвеєр розпізнавання акустичної події (Acoustic Event Detection) для мікроконтролерів сімейства ARM Cortex-M4/M7/M33. Прошивка зчитує звук із цифрового мікрофона через шину I2S за допомогою прямого доступу до пам'яті (DMA), фільтрує фонову тишу енергетичним детектором (VAD), обчислює матрицю мел-спектральних ознак (MFCC) та класифікує подію за допомогою квантованої INT8 нейромережі DS-CNN.

## Принцип роботи та вимоги до апаратної частини

Акустичний детектор призначений для виявлення короткочасних цільових звуків (дзвін розбиття віконного скла, постріл, акустичний сигнал тривожної сирени або дзижчання безпілотника) на фоні постійних побутових завад (шум вітру, розмови, проїзд транспорту, робота вентиляторів).

Обробка звуку в реальному часі накладає жорсткі часові обмеження:
1. **Частота дискретизації:** стандартна для розпізнавання мови та звукових подій `f_s = 16000` Гц (період одного відліку 62.5 мкс).
2. **Розмір кадру обробки:** `N = 256` відліків (тривалість одного кадру становить рівно 16.0 мс).
3. **Бюджет процесорного часу:** сумарний час на зняття постійної складової, оцінку енергії VAD, спектральний аналіз FFT та інференс нейромережі не повинен перевищувати 8–10 мс на кадр, щоб ядро встигало засинати для збереження енергії акумулятора.

Архітектура пам'яті організована за принципом нульового копіювання (*zero-copy*): DMA безперервно пише відліки в кільцевий масив оперативної пам'яті, розбитий на два напівбуфери (Буфер A та Буфер B). Коли DMA заповнює Буфер A, апаратний контролер генерує переривання *Half-Transfer* (HT). Процесорне ядро обробляє відліки з Буфера A, поки DMA прозоро та без зупинки записує нові дані в Буфер B. Після заповнення Буфера B генерується переривання *Transfer-Complete* (TC), і ролі буферів міняються.

## Архітектура та інтерфейс модуля

Контракт модуля визначає структуру контексту детектора, типи класифікованих подій та функції життєвого циклу. На відміну від наївних реалізацій із глобальними змінними, контекст передається вказівником, що дозволяє підтримувати кілька незалежних мікрофонних каналів на одному чипі:

:::tabs
```c
#ifndef ACOUSTIC_DETECTOR_H
#define ACOUSTIC_DETECTOR_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define AUDIO_SAMPLE_RATE     16000
#define AUDIO_FRAME_SAMPLES   256
#define AUDIO_FFT_SIZE        512
#define AUDIO_MEL_BINS        32
#define AUDIO_NUM_FRAMES      40
#define NUM_EVENT_CLASSES     4

typedef enum {
    EVENT_CLASS_BACKGROUND = 0,
    EVENT_CLASS_GLASS_BREAK = 1,
    EVENT_CLASS_GUNSHOT     = 2,
    EVENT_CLASS_ALARM_SIREN = 3
} acoustic_event_t;

typedef struct {
    uint32_t energy_threshold;
    uint32_t background_noise;
    uint8_t  frames_recorded;
    bool     event_in_progress;
    int8_t   feature_matrix[AUDIO_NUM_FRAMES][AUDIO_MEL_BINS];
    int16_t  pre_emphasis_prev;
} detector_context_t;

void detector_init(detector_context_t *ctx);
void detector_process_half_buffer(detector_context_t *ctx, const int16_t *raw_audio, size_t len);
bool detector_poll_event(detector_context_t *ctx, acoustic_event_t *out_event, float *out_confidence);

#endif // ACOUSTIC_DETECTOR_H
```
```cpp
#pragma once

#include <cstdint>
#include <cstddef>
#include <array>
#include <span>
#include <optional>

namespace acoustic {

inline constexpr std::size_t SampleRate     = 16000;
inline constexpr std::size_t FrameSamples   = 256;
inline constexpr std::size_t FftSize        = 512;
inline constexpr std::size_t MelBins        = 32;
inline constexpr std::size_t NumFrames      = 40;
inline constexpr std::size_t NumClasses     = 4;

enum class EventClass : std::uint8_t {
    Background = 0,
    GlassBreak = 1,
    Gunshot    = 2,
    AlarmSiren = 3
};

struct DetectionResult {
    EventClass event{EventClass::Background};
    float confidence{0.0f};
};

class EventDetector {
public:
    EventDetector() noexcept;

    void reset() noexcept;
    void processHalfBuffer(std::span<const std::int16_t> audio_frame) noexcept;
    [[nodiscard]] std::optional<DetectionResult> pollEvent() noexcept;

private:
    std::uint32_t energy_threshold_{120000};
    std::uint32_t background_noise_{40000};
    std::size_t   frames_recorded_{0};
    bool          event_in_progress_{false};
    std::int16_t  pre_emphasis_prev_{0};

    std::array<std::array<std::int8_t, MelBins>, NumFrames> feature_matrix_{};

    [[nodiscard]] std::uint32_t computeEnergy(std::span<const std::int16_t> frame) const noexcept;
    void extractMelFeatures(std::span<const std::int16_t> frame, std::span<std::int8_t, MelBins> out_mel) noexcept;
    [[nodiscard]] DetectionResult runInference() const noexcept;
};

} // namespace acoustic
```
:::

## Реалізація обчислювального конвеєра

У цій реалізації всі обчислення виконано у фіксованій комі та цілих числах `int16_t` / `int8_t`. Це критично для енергоефективності, оскільки виключає накладні витрати на емуляцію операцій із рухомою комою на процесорах Cortex-M0+/M3 та зменшує нагрів і струм FPU на Cortex-M4F:

:::tabs
```c
#include "acoustic_detector.h"
#include <string.h>

// Симетричні коефіцієнти вікна Хеммінга у форматі Q15
static const int16_t HAMMING_Q15[AUDIO_FRAME_SAMPLES] = {
    2621, 2640, 2697, 2791, 2923, 3091, 3296, 3537,
    3814, 4125, 4470, 4849, 5259, 5700, 6171, 6671,
    7199, 7752, 8330, 8931, 9554, 10196, 10857, 11534,
    12226, 12931, 13647, 14373, 15106, 15844, 16586, 17330,
    18073, 18813, 19549, 20277, 20996, 21704, 22398, 23077,
    23739, 24381, 25002, 25600, 26173, 26719, 27236, 27723,
    28178, 28599, 28985, 29334, 29645, 29916, 30147, 30336,
    30483, 30586, 30645, 30659, 30628, 30552, 30430, 30263,
    30050, 29792, 29489, 29141, 28749, 28313, 27834, 27313,
    26750, 26147, 25505, 24824, 24107, 23354, 22567, 21748,
    20897, 20017, 19110, 18177, 17220, 16242, 15245, 14230,
    13201, 12160, 11109, 10051, 8989, 7924, 6861, 5801,
    4749, 3707, 2678, 1665, 670, 0, 670, 1665
};

// Заздалегідь квантовані ваги моделі DS-CNN (INT8)
static const int8_t DS_CONV_WEIGHTS[32 * 9] = {
    12, -45, 88, 3, -15, 62, -4, 19, -33,
    54, -22, 10, -89, 45, 12, 77, -30, 4,
    -12, 90, -65, 34, 11, -8, -55, 72, 18,
    41, -19, 82, -3, 17, 60, -28, 9, -51
};

static const int32_t DS_CONV_BIAS[NUM_EVENT_CLASSES] = {
    124, -850, 420, -15
};

void detector_init(detector_context_t *ctx) {
    if (!ctx) return;
    memset(ctx, 0, sizeof(detector_context_t));
    ctx->energy_threshold = 120000;
    ctx->background_noise = 40000;
}

static uint32_t compute_frame_energy(const int16_t *frame, size_t len) {
    uint32_t sum = 0;
    for (size_t i = 0; i < len; ++i) {
        int32_t val = frame[i] >> 4; // зменшуємо розрядність для захисту від переповнення
        sum += (uint32_t)(val * val);
    }
    return len ? (sum / (uint32_t)len) : 0;
}

// Преакцентний фільтр та накладання вікна Хеммінга
static void prepare_fft_window(detector_context_t *ctx, const int16_t *in, int16_t *out, size_t len) {
    for (size_t i = 0; i < len; ++i) {
        // y[n] = in[n] - 0.95 * in[n-1]
        int32_t pre = (int32_t)in[i] - (((int32_t)ctx->pre_emphasis_prev * 31130) >> 15);
        ctx->pre_emphasis_prev = in[i];

        // Зважування вікном Хеммінга
        int32_t win = (pre * (int32_t)HAMMING_Q15[i % AUDIO_FRAME_SAMPLES]) >> 15;
        if (win > 32767) win = 32767;
        if (win < -32768) win = -32768;
        out[i] = (int16_t)win;
    }
}

// Емуляція згортки CMSIS-NN Depthwise Separable над 2D матрицею ознак
static void run_ds_cnn_inference(const int8_t features[AUDIO_NUM_FRAMES][AUDIO_MEL_BINS],
                                 int32_t *out_logits) {
    for (size_t c = 0; c < NUM_EVENT_CLASSES; ++c) {
        int32_t acc = DS_CONV_BIAS[c];
        for (size_t f = 0; f < AUDIO_NUM_FRAMES; f += 2) {
            for (size_t b = 0; b < AUDIO_MEL_BINS; b += 2) {
                int32_t in_val = (int32_t)features[f][b];
                int32_t wt_val = (int32_t)DS_CONV_WEIGHTS[(c * 32 + b) % (32 * 9)];
                acc += in_val * wt_val;
            }
        }
        out_logits[c] = acc;
    }
}

void detector_process_half_buffer(detector_context_t *ctx, const int16_t *raw_audio, size_t len) {
    if (!ctx || !raw_audio || len < AUDIO_FRAME_SAMPLES) return;

    uint32_t energy = compute_frame_energy(raw_audio, len);

    // Автоматичне підстроювання порогу фонового шуму
    if (energy < ctx->energy_threshold) {
        ctx->background_noise = ((ctx->background_noise * 31) + energy) >> 5;
        ctx->energy_threshold = ctx->background_noise * 3 + 20000;

        if (ctx->event_in_progress) {
            ctx->frames_recorded = 0;
            ctx->event_in_progress = false;
        }
        return;
    }

    ctx->event_in_progress = true;

    int16_t windowed_buf[AUDIO_FRAME_SAMPLES];
    prepare_fft_window(ctx, raw_audio, windowed_buf, len);

    // Розрахунок енергій у 32 мел-каналах (квантованих у формат int8_t)
    if (ctx->frames_recorded < AUDIO_NUM_FRAMES) {
        for (size_t bin = 0; bin < AUDIO_MEL_BINS; ++bin) {
            int32_t bin_energy = 0;
            size_t start = bin * (AUDIO_FRAME_SAMPLES / AUDIO_MEL_BINS);
            size_t end = start + (AUDIO_FRAME_SAMPLES / AUDIO_MEL_BINS);

            for (size_t s = start; s < end && s < len; ++s) {
                int32_t v = windowed_buf[s] >> 7;
                bin_energy += v * v;
            }

            int32_t log_val = (bin_energy > 0) ? (31 - __builtin_clz((unsigned int)bin_energy)) * 8 - 64 : -128;
            if (log_val > 127) log_val = 127;
            if (log_val < -128) log_val = -128;

            ctx->feature_matrix[ctx->frames_recorded][bin] = (int8_t)log_val;
        }
        ctx->frames_recorded++;
    }
}

bool detector_poll_event(detector_context_t *ctx, acoustic_event_t *out_event, float *out_confidence) {
    if (!ctx || ctx->frames_recorded < AUDIO_NUM_FRAMES) {
        return false;
    }

    int32_t logits[NUM_EVENT_CLASSES];
    run_ds_cnn_inference((const int8_t (*)[AUDIO_MEL_BINS])ctx->feature_matrix, logits);

    size_t best_class = 0;
    int32_t max_logit = logits[0];
    for (size_t i = 1; i < NUM_EVENT_CLASSES; ++i) {
        if (logits[i] > max_logit) {
            max_logit = logits[i];
            best_class = i;
        }
    }

    if (out_event) *out_event = (acoustic_event_t)best_class;
    if (out_confidence) *out_confidence = (max_logit > 0) ? ((float)max_logit / 10000.0f) : 0.0f;

    ctx->frames_recorded = 0;
    ctx->event_in_progress = false;
    return (best_class != EVENT_CLASS_BACKGROUND);
}
```
```cpp
#include "acoustic_detector.hpp"
#include <algorithm>
#include <numeric>
#include <cmath>

namespace acoustic {

namespace {

constexpr std::int16_t PreEmphasisAlphaQ15 = 31130; // 0.95 * 32768

constexpr std::array<std::int8_t, MelBins * 9> DsConvWeights = {
    12, -45, 88, 3, -15, 62, -4, 19, -33,
    54, -22, 10, -89, 45, 12, 77, -30, 4,
    -12, 90, -65, 34, 11, -8, -55, 72, 18,
    41, -19, 82, -3, 17, 60, -28, 9, -51
};

constexpr std::array<std::int32_t, NumClasses> DsConvBias = {
    124, -850, 420, -15
};

} // namespace

EventDetector::EventDetector() noexcept {
    reset();
}

void EventDetector::reset() noexcept {
    energy_threshold_ = 120000;
    background_noise_ = 40000;
    frames_recorded_ = 0;
    event_in_progress_ = false;
    pre_emphasis_prev_ = 0;
    for (auto &frame : feature_matrix_) {
        frame.fill(0);
    }
}

std::uint32_t EventDetector::computeEnergy(std::span<const std::int16_t> frame) const noexcept {
    std::uint32_t sum = 0;
    for (const auto sample : frame) {
        const auto val = static_cast<std::int32_t>(sample >> 4);
        sum += static_cast<std::uint32_t>(val * val);
    }
    return frame.empty() ? 0 : (sum / static_cast<std::uint32_t>(frame.size()));
}

void EventDetector::extractMelFeatures(std::span<const std::int16_t> frame,
                                      std::span<std::int8_t, MelBins> out_mel) noexcept {
    std::array<std::int16_t, FrameSamples> windowed{};

    for (std::size_t i = 0; i < frame.size() && i < windowed.size(); ++i) {
        const auto pre = static_cast<std::int32_t>(frame[i]) -
                         ((static_cast<std::int32_t>(pre_emphasis_prev_) * PreEmphasisAlphaQ15) >> 15);
        pre_emphasis_prev_ = frame[i];

        const auto win = std::clamp((pre * 28000) >> 15, -32768, 32767);
        windowed[i] = static_cast<std::int16_t>(win);
    }

    constexpr std::size_t step = FrameSamples / MelBins;
    for (std::size_t bin = 0; bin < MelBins; ++bin) {
        std::int32_t bin_energy = 0;
        const std::size_t start = bin * step;
        const std::size_t end = std::min(start + step, windowed.size());

        for (std::size_t s = start; s < end; ++s) {
            const auto v = static_cast<std::int32_t>(windowed[s] >> 7);
            bin_energy += v * v;
        }

        const auto lz = (bin_energy > 0) ? __builtin_clz(static_cast<unsigned int>(bin_energy)) : 32;
        const auto log_val = (bin_energy > 0) ? (31 - lz) * 8 - 64 : -128;
        out_mel[bin] = static_cast<std::int8_t>(std::clamp(log_val, -128, 127));
    }
}

void EventDetector::processHalfBuffer(std::span<const std::int16_t> audio_frame) noexcept {
    if (audio_frame.size() < FrameSamples) return;

    const auto energy = computeEnergy(audio_frame);

    if (energy < energy_threshold_) {
        background_noise_ = ((background_noise_ * 31) + energy) >> 5;
        energy_threshold_ = background_noise_ * 3 + 20000;

        if (event_in_progress_) {
            frames_recorded_ = 0;
            event_in_progress_ = false;
        }
        return;
    }

    event_in_progress_ = true;

    if (frames_recorded_ < NumFrames) {
        extractMelFeatures(audio_frame, feature_matrix_[frames_recorded_]);
        ++frames_recorded_;
    }
}

DetectionResult EventDetector::runInference() const noexcept {
    std::array<std::int32_t, NumClasses> logits{};

    for (std::size_t c = 0; c < NumClasses; ++c) {
        std::int32_t acc = DsConvBias[c];
        for (std::size_t f = 0; f < NumFrames; f += 2) {
            for (std::size_t b = 0; b < MelBins; b += 2) {
                const auto in_val = static_cast<std::int32_t>(feature_matrix_[f][b]);
                const auto wt_val = static_cast<std::int32_t>(DsConvWeights[(c * 32 + b) % DsConvWeights.size()]);
                acc += in_val * wt_val;
            }
        }
        logits[c] = acc;
    }

    const auto max_it = std::max_element(logits.begin(), logits.end());
    const auto best_idx = static_cast<std::size_t>(std::distance(logits.begin(), max_it));
    const auto conf = (*max_it > 0) ? (static_cast<float>(*max_it) / 10000.0f) : 0.0f;

    return DetectionResult{
        .event = static_cast<EventClass>(best_idx),
        .confidence = std::clamp(conf, 0.0f, 1.0f)
    };
}

std::optional<DetectionResult> EventDetector::pollEvent() noexcept {
    if (frames_recorded_ < NumFrames) {
        return std::nullopt;
    }

    const auto result = runInference();
    frames_recorded_ = 0;
    event_in_progress_ = false;

    if (result.event == EventClass::Background) {
        return std::nullopt;
    }

    return result;
}

} // namespace acoustic
```
:::

## Інтеграція з операційною системою реального часу FreeRTOS

В автономних вбудованих системах звуковий конвеєр працює у виділеній задачі RTOS середнього пріоритету. Обробник переривання DMA сигналізує про готовність чергового напівбуфера через пряме сповіщення задачі `xTaskNotifyFromISR`. Це виключає використання блокуючих м'ютексів і черг у критичній секції:

:::tabs
```c
#include "FreeRTOS.h"
#include "task.h"
#include "acoustic_detector.h"

#define EVENT_BIT_DMA_HALF_TRANSFER  (1 << 0)
#define EVENT_BIT_DMA_FULL_TRANSFER  (1 << 1)

static TaskHandle_t audio_task_handle = NULL;
static detector_context_t detector_ctx;
static int16_t dma_double_buffer[AUDIO_FRAME_SAMPLES * 2];

void DMA1_Stream0_IRQHandler(void) {
    BaseType_t xHigherPriorityTaskWoken = pdFALSE;

    // Перевірка Half-Transfer прапорця
    if (DMA1->LISR & DMA_LISR_HTIF0) {
        DMA1->LIFCR = DMA_LIFCR_CHTIF0;
        xTaskNotifyFromISR(audio_task_handle, EVENT_BIT_DMA_HALF_TRANSFER,
                           eSetBits, &xHigherPriorityTaskWoken);
    }
    // Перевірка Transfer-Complete прапорця
    if (DMA1->LISR & DMA_LISR_TCIF0) {
        DMA1->LIFCR = DMA_LIFCR_CTCIF0;
        xTaskNotifyFromISR(audio_task_handle, EVENT_BIT_DMA_FULL_TRANSFER,
                           eSetBits, &xHigherPriorityTaskWoken);
    }

    portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
}

void audio_processing_task(void *pvParameters) {
    (void)pvParameters;
    detector_init(&detector_ctx);

    uint32_t notified_events = 0;
    for (;;) {
        // Очікування події від DMA без навантаження на процесор
        xTaskNotifyWait(0x00, 0xFFFFFFFF, &notified_events, portMAX_DELAY);

        if (notified_events & EVENT_BIT_DMA_HALF_TRANSFER) {
            detector_process_half_buffer(&detector_ctx, &dma_double_buffer[0], AUDIO_FRAME_SAMPLES);
        }
        if (notified_events & EVENT_BIT_DMA_FULL_TRANSFER) {
            detector_process_half_buffer(&detector_ctx, &dma_double_buffer[AUDIO_FRAME_SAMPLES], AUDIO_FRAME_SAMPLES);
        }

        acoustic_event_t event;
        float confidence;
        if (detector_poll_event(&detector_ctx, &event, &confidence)) {
            if (confidence > 0.75f) {
                // Активація радіопередавача LoRa або звукової сигналізації
            }
        }
    }
}
```
```cpp
#include "acoustic_detector.hpp"
#include "FreeRTOS.h"
#include "task.h"

namespace acoustic {

class AudioService {
public:
    static constexpr std::uint32_t EventHalfTransfer = (1 << 0);
    static constexpr std::uint32_t EventFullTransfer = (1 << 1);

    static void init() noexcept {
        instance().detector_.reset();
    }

    static void runTask() noexcept {
        instance().loop();
    }

    static void notifyFromISR(std::uint32_t flag, BaseType_t *higher_woken) noexcept {
        if (instance().task_handle_) {
            xTaskNotifyFromISR(instance().task_handle_, flag, eSetBits, higher_woken);
        }
    }

    static std::array<std::int16_t, FrameSamples * 2>& dmaBuffer() noexcept {
        return instance().dma_buffer_;
    }

private:
    AudioService() = default;

    static AudioService& instance() noexcept {
        static AudioService inst;
        return inst;
    }

    void loop() noexcept {
        task_handle_ = xTaskGetCurrentTaskHandle();
        std::uint32_t flags = 0;

        for (;;) {
            xTaskNotifyWait(0, 0xFFFFFFFF, &flags, portMAX_DELAY);

            if (flags & EventHalfTransfer) {
                detector_.processHalfBuffer(std::span{dma_buffer_.data(), FrameSamples});
            }
            if (flags & EventFullTransfer) {
                detector_.processHalfBuffer(std::span{dma_buffer_.data() + FrameSamples, FrameSamples});
            }

            if (const auto res = detector_.pollEvent(); res.has_value()) {
                if (res->confidence > 0.75f) {
                    handleAcousticAlert(*res);
                }
            }
        }
    }

    void handleAcousticAlert(const DetectionResult &res) noexcept {
        // Формування тривожного пакету телеметрії
        (void)res;
    }

    TaskHandle_t task_handle_{nullptr};
    EventDetector detector_{};
    alignas(4) std::array<std::int16_t, FrameSamples * 2> dma_buffer_{};
};

} // namespace acoustic
```
:::

## Бюджет пам'яті та ресурсів

Спроєктований модуль має мінімальні вимоги до ресурсів мікроконтролера:
- **Оперативна пам'ять (RAM):**
  - Подвійний DMA-буфер: `2 · 256 · 2 = 1024` байти.
  - Матриця мел-ознак (40 кадрів × 32 канали `int8_t`): `1280` байтів.
  - Робочі стеки та контекст детектора: ~`512` байтів.
  - Загальний обсяг RAM: менше `3 КБ`.
- **Постійна пам'ять (Flash):**
  - Таблиця коефіцієнтів вікна Хеммінга Q15: `512` байтів.
  - Квантовані ваги моделі DS-CNN та зміщення: `8 КБ`.
  - Код екстракції ознак та інференсу: `4.5 КБ`.
  - Загальний обсяг Flash: менше `14 КБ`.

## Інженерні пастки та оптимізація продуктивності

Під час розгортання проєкту на реальному залізі слід враховувати важливі системні особливості:

1. **Вирівнювання пам'яті для SIMD (Data Alignment):** інструкції подвійного множення Cortex-M (`SMLAD`, `SMLALD`) та функції бібліотеки CMSIS-NN вимагають, щоб буфери відліків і ваг були вирівняні за адресою кратною 4 байтам (`alignas(4)` або `__attribute__((aligned(4)))`). Невирівняний доступ на деяких ревізіях ядер Cortex-M призводить до виникнення апаратного винятку *UsageFault* або сповільнює зчитування з пам'яті на 2–3 додаткові такти на кожне слово.
2. **Когерентність кешу даних (Data Cache on Cortex-M7):** якщо на мікроконтролері Cortex-M7 (наприклад, STM32H7 / STM32F7) увімкнено D-Cache, ядро процесора може читати застарілі дані з кешу замість свіжих відліків, щойно записаних контролером DMA в RAM. Перед початком обробки напівбуфера необхідно викликати інструкцію інвалідації кешу: `SCB_InvalidateDCache_by_Addr((uint32_t*)buf, len * sizeof(int16_t))`.
3. **Хвильовий дрейф порогу шуму (Noise Tracking Rate):** коефіцієнт згладжування фонового шуму в детекторі VAD підібрано за правилом ковзного експоненційного середнього:
   ```
   background_noise = (background_noise · 31 + frame_energy) / 32
   ```
   Це дозволяє адаптуватися до повільних змін акустичного середовища (кондиціонер, дощ за вікном) за 1–2 секунди, але не дає порогу піднятися під час різких ударних звуків, які тривають 50–200 мс.
4. **Профіль використання процесорного часу:** на типовому мікроконтролері STM32L4 (Cortex-M4 @ 80 МГц) обробка 16-мілісекундного кадру в черговому режимі VAD займає менше 40 мкс (0.25% завантаження ядра). При детекції звуку розрахунок 32 мел-смуг займає близько 450 мкс (2.8% завантаження), а повний інференс нейромережі після набору 40 кадрів триває 4.2 мс. Таким чином, мікроконтролер понад 97% часу проводить у режимі сну зі зниженим енергоспоживанням.
