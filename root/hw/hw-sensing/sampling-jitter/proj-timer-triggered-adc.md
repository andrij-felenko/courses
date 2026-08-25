# ⚙️ Апаратне тактування АЦП через тригери таймера та DMA без участі процесора

У задачах цифрової обробки сигналів, спектрального аналізу (ШПФ), векторного керування електродвигунами (FOC) та радіовимірювань стабільність кроку дискретизації є настільки ж критичною, як і номінальна розрядність перетворювача. Спроба запускати вимірювання АЦП програмно — у нескінченному циклі `while(1)` або навіть усередині обробника переривань таймера (ISR) — призводить до неконтрольованого часового тремтіння (джиттеру) тривалістю від десятків наносекунд до кількох мікросекунд через затримки конвеєра, очікування Flash-пам'яті (Wait States), вкладені переривання та блокування критичних секцій.

Нижче наведено практичну архітектуру, покроковий інженерний аналіз та повну реалізацію апаратного запуску АЦП за внутрішнім сигналом таймера (Timer Trigger Out, TRGO) з автономним перенесенням відліків у пам'ять контролером прямого доступу (DMA) у режимі кільцевого подвійного буфера (Double Buffering), підтримкою кеш-когерентності, багатоканальним скануванням, синхронізацією з ШІМ-інверторами (Center-Aligned PWM), чергуванням двох АЦП (Dual Interleaved ADC), розрахунком цілочисельних дільників таймера, правилами фільтрації опорної напруги та алгоритмами спектральної верифікації.

## 1. Архітектурне порівняння: три підходи до тактування АЦП

Розглянемо три способи реалізації періодичного зчитування АЦП у сучасних вбудованих системах:

1. **Програмне опитування (Software Polling / Delay):**
   Процесор викликає функцію запуску перетворення `HAL_ADC_Start()` або `analogRead()` у циклі із затримкою `delayMicroseconds()`. Будь-яке переривання від UART, USB, Wi-Fi або системного таймера SysTick зміщує момент запуску на непередбачувану величину. Рівень джиттеру сягає `1 ... 50 мкс`. Оцифрування синусоїди частотою вище 1 кГц призводить до катастрофічного зростання шумової доріжки, а ефективна розрядність 12-бітного перетворювача деградує до рівня 4–6 біт.
2. **Запуск всередині ISR таймера (Timer Interrupt Triggered):**
   Апаратний таймер генерує періодичне переривання з частотою `f_s`. Усередині функції `TIMx_IRQHandler()` процесор програмно встановлює біт `SWSTART` у регістрі керування АЦП. Хоча таймер рахує такти точно, затримка входу процесора в ISR (Interrupt Latency) варіюється від 12 до 35 тактів ядра залежно від стану шини пам'яті, глибини стеку, наявності інших пріоритетних переривань та виконання атомарних інструкцій ядра (`LDREX`/`STREX` або блокувань `__disable_irq()`). Рівень джиттеру становить `50 ... 500 нс`.
3. **Апаратний тригер таймера + DMA (Hardware TRGO + Circular DMA):**
   Апаратний таймер налаштовується на генерацію події оновлення (Update Event), яка комутується на внутрішню кремнієву шину `TRGO`. АЦП налаштовується на зовнішній апаратний запуск від `TIMx_TRGO` по висхідному фронту. Контролер прямого доступу до пам'яті (DMA) прив'язується до вихідного регістра даних АЦП `ADC_DR` та автоматично копіює кожне оцифроване слово в кільцевий буфер в оперативній пам'яті (SRAM). Процесор взагалі не бере участі в запусках і прокидається лише двічі за повний цикл буфера: за подіями Half Transfer (заповнено 50%) та Full Transfer (заповнено 100%). Рівень джиттеру падає до субнаносекундних величин (`< 50 пс`), обумовлених виключно фазовим шумом опорного кварцового генератора.

## 2. Розрахунок регістрів таймера та уникнення періодичного дискретного джиттеру

Для забезпечення рівномірної сітки відліків частота дискретизації `f_s` повинна точно ділити частоту тактування таймера `f_TIM`:

```
f_s = f_TIM / [ (PSC + 1) · (ARR + 1) ]
```

де `PSC` — 16-бітний регістр попереднього дільника (Prescaler), а `ARR` — регістр автоперезавантаження (Auto-Reload Register).

Критичне правило прецизійного тактування: **коефіцієнт ділення `(f_TIM / f_s)` повинен бути строго цілим числом**. Якщо розробник намагається отримати дробову частоту дискретизації (наприклад, 44.1 кГц при частоті таймера 84 МГц, де ділення дає `84000000 / 44100 = 1904.7619`), чергування періодів `ARR = 1904` та `ARR = 1905` створює систематичний детермінований джиттер амплітудою в один повний такт таймера (11.9 нс). Цей стрибок діє як фазова модуляція сигналу вибірки й породжує дискретні паразитні гармоніки (Spurious Tones) у спектрі сигналу.

Для точних стандартних частот аудіо (44.1 кГц, 48 кГц, 96 кГц) або радіозв'язку тактовий генератор мікроконтролера (PLL) повинен налаштовуватися на спеціалізовані частоти (наприклад, PLL I2S з частотою 192 МГц або 12.288 МГц), де коефіцієнт ділення є строго цілим.

## 3. Синхронізація вибірки з центром ШІМ (Center-Aligned PWM Triggering)

У симетричних перетворювачах живлення, сервоприводах та системах FOC вимірювання струму фази мотора через шунти в нижньому плечі напівмоста має виконуватися в строго фіксований момент: рівно посередині стану увімкнення нижніх транзисторів, коли перехідні процеси комутації силових MOSFET/IGBT вже завершилися, а індуктивний струм не спотворений ємнісним шумом `dV/dt`.

Для цього таймер керування двигуном (TIM1 або TIM8 у STM32) налаштовується в симетричний режим рахунку вгору-вниз (Center-Aligned Mode 1/2/3). Подія запуску TRGO налаштовується на подію `TIM_TRGO_UPDATE`, яка генерується рівно в нижній точці перегину лічильника (`CNT = 0`), або на подію порівняння каналу `TIM_TRGO_OC4REF`, коли лічильник досягає вершини (`CNT = ARR`).

АЦП запускається апаратно в центрі ШІМ-періоду з абсолютною синхронністю до фази силіконових ключів. Програмний запуск у такому сценарії є неприпустимим: затримка навіть у 200 наносекунд призводить до потрапляння моменту вибірки на фронт перемикання силового транзистора, викликаючи стрибок вимірюваного струму на сотні міліампер і зрив петлі регулювання струму.

## 4. Реалізація апаратного конвеєра: Timer TRGO → ADC → DMA

Усі компоненти конвеєра налаштовуються так, щоб працювати як єдиний автономний апаратний автомат без навантаження на ядро процесора.

:::tabs
```stm32
/* 
 * Реалізація на мові C (STM32 HAL / Register Level)
 * Конфігурація TIM2 (генератор TRGO) + ADC1 (Hardware Trigger) + DMA2
 */

#include "stm32f4xx_hal.h"
#include <stdbool.h>

#define BUFFER_SIZE     2048
#define HALF_BUFFER     (BUFFER_SIZE / 2)

/* Подвійний буфер відліків АЦП (вирівняний для DMA) */
static uint16_t adc_dma_buffer[BUFFER_SIZE] __attribute__((aligned(4)));

/* Прапорці готовності половин буфера для фонового обробника */
static volatile bool g_half_ready = false;
static volatile bool g_full_ready = false;

ADC_HandleTypeDef hadc1;
TIM_HandleTypeDef htim2;
DMA_HandleTypeDef hdma_adc1;

/**
 * @brief Налаштування таймера TIM2 як генератора тактових тригерів TRGO
 * @param sampling_freq Частота дискретизації в Герцах (наприклад, 100000 для 100 кГц)
 */
void Timer2_TRGO_Init(uint32_t sampling_freq) {
    __HAL_RCC_TIM2_CLK_ENABLE();

    /* Частота шини APB1 Timer Clock = 84 МГц */
    uint32_t timer_clock = 84000000;
    uint32_t period = (timer_clock / sampling_freq) - 1;

    htim2.Instance = TIM2;
    htim2.Init.Prescaler = 0;                     /* Без попереднього ділення */
    htim2.Init.CounterMode = TIM_COUNTERMODE_UP;
    htim2.Init.Period = period;                   /* Автоперезавантаження ARR */
    htim2.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
    htim2.Init.AutoReloadPreload = TIM_AUTORELOAD_PRELOAD_ENABLE;
    HAL_TIM_Base_Init(&htim2);

    /* Комутація події оновлення (Update Event) на вихідний тригер TRGO */
    TIM_MasterConfigTypeDef sMasterConfig = {0};
    sMasterConfig.MasterOutputTrigger = TIM_TRGO_UPDATE;
    sMasterConfig.MasterSlaveMode = TIM_MASTERSLAVEMODE_DISABLE;
    HAL_TIMEx_MasterConfigSynchronization(&htim2, &sMasterConfig);
}

/**
 * @brief Налаштування АЦП ADC1 на апаратний запуск від TIM2 TRGO та роботу з DMA
 */
void ADC1_HardwareTrigger_DMA_Init(void) {
    __HAL_RCC_ADC1_CLK_ENABLE();
    __HAL_RCC_DMA2_CLK_ENABLE();
    __HAL_RCC_GPIOA_CLK_ENABLE();

    /* Налаштування аналогового входу PA0 (ADC1_IN0) */
    GPIO_InitTypeDef gpio = {0};
    gpio.Pin = GPIO_PIN_0;
    gpio.Mode = GPIO_MODE_ANALOG;
    gpio.Pull = GPIO_NOPULL;
    HAL_GPIO_Init(GPIOA, &gpio);

    /* Налаштування DMA2 Stream 0 для ADC1 */
    hdma_adc1.Instance = DMA2_Stream0;
    hdma_adc1.Init.Channel = DMA_CHANNEL_0;
    hdma_adc1.Init.Direction = DMA_PERIPH_TO_MEMORY;
    hdma_adc1.Init.PeriphInc = DMA_PINC_DISABLE;
    hdma_adc1.Init.MemInc = DMA_MINC_ENABLE;
    hdma_adc1.Init.PeriphDataAlignment = DMA_PDATAALIGN_HALFWORD; /* 16 біт */
    hdma_adc1.Init.MemDataAlignment = DMA_MDATAALIGN_HALFWORD;    /* 16 біт */
    hdma_adc1.Init.Mode = DMA_CIRCULAR;                           /* Кільцевий режим */
    hdma_adc1.Init.Priority = DMA_PRIORITY_HIGH;
    hdma_adc1.Init.FIFOMode = DMA_FIFOMODE_DISABLE;
    HAL_DMA_Init(&hdma_adc1);

    __HAL_LINKDMA(&hadc1, DMA_Handle, hdma_adc1);

    /* Налаштування самого АЦП */
    hadc1.Instance = ADC1;
    hadc1.Init.ClockPrescaler = ADC_CLOCK_SYNC_PCLK_DIV4;         /* 21 МГц */
    hadc1.Init.Resolution = ADC_RESOLUTION_12B;
    hadc1.Init.ScanConvMode = DISABLE;
    hadc1.Init.ContinuousConvMode = DISABLE;                      /* Суворо по тригеру! */
    hadc1.Init.DiscontinuousConvMode = DISABLE;
    hadc1.Init.ExternalTrigConvEdge = ADC_EXTERNALTRIGCONVEDGE_RISING;
    hadc1.Init.ExternalTrigConv = ADC_EXTERNALTRIGCONV_T2_TRGO;   /* Апаратний запуск TIM2 TRGO */
    hadc1.Init.DataAlign = ADC_DATAALIGN_RIGHT;
    hadc1.Init.NbrOfConversion = 1;
    hadc1.Init.DMAContinuousRequests = ENABLE;                     /* Постійні запити DMA */
    hadc1.Init.EOCSelection = ADC_EOC_SINGLE_CONV;
    HAL_ADC_Init(&hadc1);

    /* Налаштування регулярного каналу: мінімальний час вибірки 3 цикли */
    ADC_ChannelConfTypeDef sConfig = {0};
    sConfig.Channel = ADC_CHANNEL_0;
    sConfig.Rank = 1;
    sConfig.SamplingTime = ADC_SAMPLETIME_3CYCLES;
    HAL_ADC_ConfigChannel(&hadc1, &sConfig);

    /* Увімкнення переривань DMA в контролері NVIC */
    HAL_NVIC_SetPriority(DMA2_Stream0_IRQn, 0, 0);
    HAL_NVIC_EnableIRQ(DMA2_Stream0_IRQn);
}

/**
 * @brief Колбек половини передачі DMA: заповнено першу половину adc_dma_buffer[0 ... 1023]
 */
void HAL_ADC_ConvHalfCpltCallback(ADC_HandleTypeDef* hadc) {
    if (hadc->Instance == ADC1) {
        g_half_ready = true;
    }
}

/**
 * @brief Колбек повної передачі DMA: заповнено другу половину adc_dma_buffer[1024 ... 2047]
 */
void HAL_ADC_ConvCpltCallback(ADC_HandleTypeDef* hadc) {
    if (hadc->Instance == ADC1) {
        g_full_ready = true;
    }
}

/**
 * @brief Запуск збору даних з нульовим програмним джиттером
 */
void Start_Acquisition(void) {
    HAL_ADC_Start_DMA(&hadc1, (uint32_t*)adc_dma_buffer, BUFFER_SIZE);
    HAL_TIM_Base_Start(&htim2);
}
```
```esp-idf
/*
 * Реалізація для ESP-IDF (ESP32)
 * Неперервне зчитування ADC Continuous Driver через DMA + Hardware Timer
 */

#include <stdio.h>
#include <string.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_adc/adc_continuous.h"
#include "esp_log.h"

#define EXAMPLE_READ_LEN    1024
#define SAMPLE_FREQ_HZ      100000  /* 100 кГц апаратний тактовий запуск */

static const char *TAG = "ADC_TIMER_DMA";
static adc_continuous_handle_t s_adc_handle = NULL;

static bool IRAM_ATTR s_conv_done_cb(adc_continuous_handle_t handle, 
                                     const adc_continuous_evt_data_t *edata, 
                                     void *user_data) {
    BaseType_t must_yield = pdFALSE;
    TaskHandle_t task_to_notify = (TaskHandle_t)user_data;
    vTaskNotifyGiveFromISR(task_to_notify, &must_yield);
    return (must_yield == pdTRUE);
}

void app_main(void) {
    TaskHandle_t main_task = xTaskGetCurrentTaskHandle();

    /* 1. Конфігурація неперервного драйвера АЦП на базі апаратного таймера/I2S-DMA */
    adc_continuous_handle_cfg_t adc_config = {
        .max_store_buf_size = 4096,
        .conv_frame_size = EXAMPLE_READ_LEN,
    };
    ESP_ERROR_CHECK(adc_continuous_new_handle(&adc_config, &s_adc_handle));

    /* 2. Налаштування шаблону сканування та апаратної частоти вибірки */
    adc_continuous_config_t dig_cfg = {
        .sample_freq_hz = SAMPLE_FREQ_HZ,
        .conv_mode = ADC_CONV_SINGLE_UNIT_1,
        .format = ADC_DIGI_OUTPUT_FORMAT_TYPE1,
    };

    adc_digi_pattern_config_t adc_pattern = {
        .atten = ADC_ATTEN_DB_12,
        .channel = ADC_CHANNEL_0,
        .unit = ADC_UNIT_1,
        .bit_width = ADC_BITWIDTH_12,
    };
    dig_cfg.pattern_num = 1;
    dig_cfg.adc_pattern = &adc_pattern;
    ESP_ERROR_CHECK(adc_continuous_config(s_adc_handle, &dig_cfg));

    /* 3. Реєстрація ISR колбеку завершення кадру DMA */
    adc_continuous_evt_cbs_t cbs = {
        .on_conv_done = s_conv_done_cb,
    };
    ESP_ERROR_CHECK(adc_continuous_register_event_callbacks(s_adc_handle, &cbs, (void*)main_task));

    /* 4. Апаратний старт перетворень */
    ESP_ERROR_CHECK(adc_continuous_start(s_adc_handle));
    ESP_LOGI(TAG, "ADC hardware DMA acquisition started at %d Hz", SAMPLE_FREQ_HZ);

    uint8_t result_bytes[EXAMPLE_READ_LEN];
    uint32_t ret_num = 0;

    while (1) {
        /* Чекаємо апаратного сповіщення від DMA ISR без навантаження CPU */
        ulTaskNotifyTake(pdTRUE, portMAX_DELAY);

        esp_err_t ret = adc_continuous_read(s_adc_handle, result_bytes, EXAMPLE_READ_LEN, &ret_num, 0);
        if (ret == ESP_OK) {
            /* Опрацювання готового блоку відліків у фоновому потоці */
        }
    }
}
```
```arduino
/*
 * Реалізація на Arduino (з використанням прямих регістрів таймера та АЦП)
 * Демонстрація апаратного запуску на платах з ядром SAMD21 / STM32
 */

#define SAMPLE_RATE_HZ 50000
#define BUFFER_SIZE    512

volatile uint16_t adc_buffer[BUFFER_SIZE];
volatile bool buffer_ready = false;

void setupHardwareTimerTrigger() {
    /* 
     * Пряме конфігурування апаратного таймера та АЦП без використання повільного analogRead()
     * Таймер генерує строб вибірки безпосередньо в логіку АЦП через систему подій EVSYS.
     */
#if defined(ARDUINO_ARCH_SAMD)
    PM->APBCMASK.reg |= PM_APBCMASK_EVSYS | PM_APBCMASK_ADC | PM_APBCMASK_TC5;
    
    // Комутація виходу TC5 на подію старту АЦП
    EVSYS->USER.reg = EVSYS_USER_CHANNEL(1) | EVSYS_USER_USER(EVSYS_ID_USER_ADC_START);
    EVSYS->CHANNEL.reg = EVSYS_CHANNEL_CHANNEL(0) | EVSYS_CHANNEL_PATH_SYNCHRONOUS | EVSYS_CHANNEL_EVGEN(EVSYS_ID_GEN_TC5_OVF);

    // Увімкнення апаратного тригера в АЦП
    ADC->EVCTRL.reg |= ADC_EVCTRL_STARTEI;
#endif
}

void setup() {
    Serial.begin(115200);
    setupHardwareTimerTrigger();
}

void loop() {
    if (buffer_ready) {
        buffer_ready = false;
        // Обробка блоку відліків без програмного тремтіння тактування
    }
}
```
:::

## 5. Подвійний чергований АЦП (Dual Interleaved Mode) для подвоєння частоти вибірки

Коли граничної швидкості одного АЦП недостатньо для оцифрування швидкого сигналу (наприклад, необхідно отримати 4 MSPS при максимальній частоті одного АЦП 2 MSPS), використовують апаратне чергування двох незалежних перетворювачів (ADC1 та ADC2), підключених до одного спільного аналогового каналу.

Для усунення фазового джиттеру між двома перетворювачами таймер налаштовується на генерацію двох взаємно зсунутих тригерів:
- **ADC1** запускається за подією оновлення `TIM_TRGO_UPDATE` (фаза 0°);
- **ADC2** запускається за подією порівняння каналу 1 `TIM_TRGO_OC1REF` (фаза 180°), коли лічильник досягає значення `ARR / 2`.

Контролер DMA працює в 32-бітному комбінованому режимі (Dual Regular Simultaneous / Interleaved Mode), де за одну транзакцію DMA зчитує спільний 32-бітний регістр `ADC_CDR`, у якому молодші 16 біт містять відлік `ADC1`, а старші 16 біт — відлік `ADC2`.

Критичною вимогою чергованого режиму є абсолютна симетрія апертурної затримки обох каналів: якщо внутрішні затримки `t_a1` та `t_a2` різняться навіть на 100 пікосекунд, виникає періодичний детермінований джиттер (Timing Skew), що породжує дзеркальні паразитні спектральні гармоніки (Image Spurs) на частоті `f_s / 2 - f_in`.

## 6. Ідіоматична обгортка на C++: RAII, Span та керування кеш-пам'яттю

Для чистої інтеграції в сучасне вбудоване програмне забезпечення на C++ апаратний конвеєр інкапсулюється в шаблонний клас драйвера, що використовує семантику RAII, гарантує безпеку пам'яті за допомогою `std::span` та керує когерентністю кешу даних ARM Cortex-M7 (D-Cache Invalidation).

:::tabs
```cpp
#include <array>
#include <span>
#include <cstdint>
#include <concepts>
#include <functional>

/**
 * @brief Концепт споживача блоків відліків АЦП
 */
template <typename T>
concept SampleConsumer = requires(T consumer, std::span<const uint16_t> block) {
    { consumer.on_block_ready(block) } -> std::same_as<void>;
};

/**
 * @brief Диспетчер подвійного буфера АЦП на базі DMA
 * @tparam BufferSize Загальний розмір буфера (мусить бути парним і кратним розміру рядка кешу 32 байти)
 */
template <std::size_t BufferSize>
class AdcCircularBuffer {
    static_assert(BufferSize % 2 == 0, "Розмір буфера мусить ділитися на 2 для роботи Half/Full DMA");
    static_assert((BufferSize * sizeof(uint16_t)) % 32 == 0, "Буфер мусить бути вирівняний по лінії D-Cache 32 байти");

public:
    static constexpr std::size_t HalfSize = BufferSize / 2;

    AdcCircularBuffer() = default;

    /* Заборона копіювання через володіння апаратним буфером */
    AdcCircularBuffer(const AdcCircularBuffer&) = delete;
    AdcCircularBuffer& operator=(const AdcCircularBuffer&) = delete;

    /**
     * @brief Отримати покажчик на сирий масив для апаратного налаштування DMA
     */
    [[nodiscard]] constexpr uint16_t* raw_data() noexcept {
        return m_buffer.data();
    }

    [[nodiscard]] constexpr std::size_t size() const noexcept {
        return BufferSize;
    }

    /**
     * @brief Викликається з обробника Half-Transfer ISR
     */
    void handle_half_complete_isr() noexcept {
        m_half_pending = true;
    }

    /**
     * @brief Викликається з обробника Full-Transfer ISR
     */
    void handle_full_complete_isr() noexcept {
        m_full_pending = true;
    }

    /**
     * @brief Опитування та передача готових половин буфера у споживач
     */
    template <SampleConsumer Consumer>
    void process_pending(Consumer& consumer) {
        if (m_half_pending) {
            m_half_pending = false;
            // Для ядер з D-Cache (Cortex-M7) інвалідуємо першу половину буфера
            #if defined(__DCACHE_PRESENT) && (__DCACHE_PRESENT == 1U)
            SCB_InvalidateDCache_by_Addr(reinterpret_cast<uint32_t*>(m_buffer.data()), HalfSize * sizeof(uint16_t));
            #endif
            consumer.on_block_ready(std::span<const uint16_t>(m_buffer.data(), HalfSize));
        }
        if (m_full_pending) {
            m_full_pending = false;
            #if defined(__DCACHE_PRESENT) && (__DCACHE_PRESENT == 1U)
            SCB_InvalidateDCache_by_Addr(reinterpret_cast<uint32_t*>(m_buffer.data() + HalfSize), HalfSize * sizeof(uint16_t));
            #endif
            consumer.on_block_ready(std::span<const uint16_t>(m_buffer.data() + HalfSize, HalfSize));
        }
    }

private:
    alignas(32) std::array<uint16_t, BufferSize> m_buffer{};
    volatile bool m_half_pending{false};
    volatile bool m_full_pending{false};
};

/**
 * @brief Приклад обробника спектрального аналізатора
 */
class SpectralProcessor {
public:
    void on_block_ready(std::span<const uint16_t> block) {
        // block.data() містить гарантовано стабільні за часом відліки
        // Виконання ШПФ над block.size() елементами
    }
};
```
```c
/* Еквівалентна структура на чистому C */

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define ADC_BUFFER_SIZE 2048
#define ADC_HALF_SIZE   (ADC_BUFFER_SIZE / 2)

typedef struct {
    uint16_t buffer[ADC_BUFFER_SIZE] __attribute__((aligned(32)));
    volatile bool half_ready;
    volatile bool full_ready;
} AdcDoubleBuffer_t;

static AdcDoubleBuffer_t g_adc_buf;

void AdcBuffer_Init(AdcDoubleBuffer_t* buf) {
    buf->half_ready = false;
    buf->full_ready = false;
}

void AdcBuffer_OnHalfISR(AdcDoubleBuffer_t* buf) {
    buf->half_ready = true;
}

void AdcBuffer_OnFullISR(AdcDoubleBuffer_t* buf) {
    buf->full_ready = true;
}

void AdcBuffer_Process(AdcDoubleBuffer_t* buf, void (*process_fn)(const uint16_t* data, size_t len)) {
    if (buf->half_ready) {
        buf->half_ready = false;
        process_fn(&buf->buffer[0], ADC_HALF_SIZE);
    }
    if (buf->full_ready) {
        buf->full_ready = false;
        process_fn(&buf->buffer[ADC_HALF_SIZE], ADC_HALF_SIZE);
    }
}
```
:::

## 7. Багатоканальне сканування (Scan Mode) та фазовий зсув між каналами

Коли один АЦП перетворює кілька аналогових каналів послідовно (наприклад, струми трьох фаз двигуна `I_u`, `I_v`, `I_w` або напруги акселерометра `X`, `Y`, `Z`), запуск від таймера ініціює перетворення всього ланцюжка каналів.

Важливо розуміти, що при використанні одного мультиплексованого АЦП канали перетворюються **не одночасно**, а послідовно в часі:
- Канал 1 фіксується в момент `t_0`;
- Канал 2 фіксується в момент `t_0 + t_conv`;
- Канал 3 фіксується в момент `t_0 + 2 · t_conv`.

Цей часовий зсув `t_conv` між відліками діє як систематичний фазовий дрейф між сигналами. У трифазних інверторах з векторним керуванням це призводить до помилки оцінки вектора струму статора.

Для повного усунення фазового зсуву між каналами застосовують мікроконтролери з кількома незалежними ядрами АЦП (ADC1, ADC2, ADC3), які запускаються одночасно від одного спільного сигналу `TIM_TRGO` (Triple Simultaneous Regular Mode).

## 8. Пастки та інженерні нюанси реалізації

Під час проектування апаратного тракту тактування АЦП розробники найчастіше стикаються з п'ятьма прихованими проблемами:

### Пастка 1: Множник тактової частоти шини APB (Таймер працює на подвійній частоті)
В архітектурах STM32 тактування таймерів на шинах APB1 та APB2 має апаратну особливість: якщо дільник шини APB (`PPRE1` або `PPRE2`) не дорівнює 1 (наприклад, `HCLK / 4`), апаратний помножувач автоматично подвоює частоту, яка надходить на лічильник таймера (`CK_INT = 2 × PCLK1`). Якщо розробник розраховує період автоперезавантаження `ARR` виходячи зі звичайної частоти `PCLK1`, реальна частота дискретизації виявиться рівно вдвічі вищою за очікувану, що призведе до грубих помилок масштабування спектра ШПФ.

### Пастка 2: Недостатній час заряду вхідної ємності вибірки (Sampling Time)
Внутрішня схема вибірки-зберігання АЦП містить аналоговий перемикач з власним опором `R_switch` (типово 1–6 кОм) та конденсатор вибірки `C_sample` (типово 4–12 пФ). При апаратному запуску за високої частоти дискретизації час підключення конденсатора до аналогового піна `t_sample` повинен бути достатнім для повного перезаряду:

```
t_sample ≥ ( R_source + R_switch ) · C_sample · ln( 2^{N+1} )
```

Для 12-бітного АЦП `ln(2¹³) ≈ 9.01` сталих часу `RC`. Якщо вихідний опір джерела сигналу `R_source = 10 кОм`, а час вибірки налаштовано на мінімальні 3 такти АЦП (при частоті 21 МГц це лише `142 нс`), конденсатор не встигає зарядитися до повної напруги. Виникає ефект міжканального перехресного затікання заряду (Memory Crosstalk) та додаткова динамічна нелінійність.

### Пастка 3: Конфлікти на матриці шин (Bus Matrix Contention) та переповнення FIFO DMA
Коли процесор інтенсивно виконує доступ до пам'яті через ту саму шину, що й контролер DMA (наприклад, звертається до зовнішньої пам'яті SDRAM або виконує важкі операції копіювання `memcpy`), арбітраж матриці шин може затримати DMA-транзакцію читання регістра `ADC_DR`. Якщо чергове перетворення завершиться до того, як DMA вичитає попереднє значення, виникає помилка переповнення АЦП (ADC Overrun, біт `OVR` у регістрі `ADC_SR`), що призводить до втрати синхронізації та зміщення вибірок у пам'яті. Для запобігання цьому пріоритет потоку DMA для АЦП завжди встановлюють у стан `DMA_PRIORITY_VERY_HIGH`.

### Пастка 4: Кеш-когерентність (D-Cache Stale Data на Cortex-M7)
У високопродуктивних мікроконтролерах із увімкненим кешем даних (наприклад, STM32F7, STM32H7, i.MX RT) контролер DMA записує відліки безпосередньо в фізичну пам'ять SRAM, минаючи L1 D-Cache процесора. Якщо процесор зчитує масив `adc_dma_buffer` без попередньої інвалідації кеш-рядків (`SCB_InvalidateDCache_by_Addr`), він отримує застарілі дані з кешу. Результатом є періодична поява "мертвих" або старих блоків сигналу.

### Пастка 5: Неправильний вибір події TRGO (Trigger Output Source)
Якщо в регістрі конфігурації таймера `CR2` як джерело TRGO помилково обрано `TIM_TRGO_OC1REF` замість `TIM_TRGO_UPDATE`, тригер вибірки генеруватиметься лише тоді, коли значення лічильника збігається з регістром захоплення-порівняння `CCR1`. Якщо значення `CCR1` випадково виявиться більшим за період автоперезавантаження `ARR`, генерація тригерів повністю заблокується, і АЦП перестане отримувати імпульси вибірки.

## 9. Методика вимірювання джиттеру та верифікація спектра

Для експериментальної верифікації чистоти тактування використовують два незалежні методи:

### Апаратне вимірювання осцилографом
1. **Тестовий сигнал:** На таймері налаштовується апаратний вихід каналу 1 (CH1) у режимі PWM/Toggle, що синхронізований із подією оновлення `UPDATE` (TRGO).
2. **Програмний строб:** Усередині програмного обробника переривань `TIMx_IRQHandler()` першим рядком коду додається перемикання окремого GPIO-піна: `GPIOB->BSRR = GPIO_PIN_1; GPIOB->BSRR = (GPIO_PIN_1 << 16);`.
3. **Вимірювання:** Осцилограф підключається двома каналами до апаратного та програмного пінів. Осцилограф синхронізується (Trigger) по апаратному піну CH1, а режим нескінченного післясвітіння (Infinite Persistence) вмикається для другого каналу.
На екрані чітко спостерігається результат: апаратний сигнал стоїть абсолютно нерухомо (джиттер менше роздільної здатності приладу), тоді як програмний фронт утворює розмиту смугу шириною від 60 до 800 наносекунд через варіацію затримки процесора.

### Спектральний аналіз відліків (ШПФ-тест)
На вхід АЦП від прецизійного генератора подається чиста синусоїда частотою `f_in = 45 кГц` з амплітудою -0.5 dBFS. Обчислюється 2048-точкове ШПФ з вікном Блекмана-Гарріса:
- При програмному опитуванні шумова доріжка піднімається на 35–40 дБ, з'являються паразитні гармоніки від частоти системного тику (1000 Гц SysTick), а виміряний `ENOB` падає до 5.8 біт;
- При апаратному тактуванні `TIM2_TRGO + DMA` шумова доріжка опускається до теоретичного рівня квантування (-74 дБ для 12 біт), коефіцієнт гармонік THD становить менше -72 дБ, а `ENOB` сягає номінальних 11.4 біт.

## 10. Трасування друкованої плати для мінімізації наведеного джиттеру

Навіть ідеально налаштований таймер не врятує перетворювач від апертурного джиттеру, якщо топологія друкованої плати допускає проникнення цифрових перешкод у тракт тактування.

Основні правила проектування високошвидкісних вузлів вибірки:
1. **Виділена лінія тактування:** Сигнал тактування АЦП (або вихід зовнішнього кварцового генератора) повинен трасуватися як диференціальна пара з контрольованим хвильовим опором (100 Ом) або копланарний хвилевід над суцільним шаром аналогової землі.
2. **Розділення аналогової та цифрової землі:** Під мікросхемою перетворювача земляний полігон має бути єдиним цілісним шаром, без розрізів під лініями тактування, щоб зворотний струм високої частоти не утворював паразитних петель індуктивності.
3. **Локальні блокувальні конденсатори:** Виводи живлення цифрового буфера тактування та аналогового вузла вибірки повинні блокуватися керамічними конденсаторами типорозміру 0402 (ємністю 100 нФ та 10 пФ з високою власною резонансною частотою), розміщеними на відстані не більше 1 мм від пінів мікросхеми.
4. **Фільтрація джерела опорної напруги (VREF):** Будь-які імпульсні шуми на виводі `VREF+` модулюють коефіцієнт перетворення АЦП синхронно з частотою перемикання цифрових шин, що сприймається алгоритмами спектрального аналізу як додатковий комбінований джиттер амплітуди й фази. Вивід `VREF+` вимагає комбінованого блокування танталовим або керамічним конденсатором ємністю 10–47 мкФ у парі з прецизійним феритовим фільтром (Ferrite Bead).
5. **Використання CML/LVDS замість CMOS:** Для тактових частот вище 50 МГц слід відмовитися від логічних рівнів CMOS (де перепади 3.3 В генерують імпульсні струми амплітудою в сотні міліампер) на користь низьковольтних диференціальних інтерфейсів LVDS або CML зі струмовим керуванням і розмахом 350 мВ, що забезпечують мінімальний рівень електромагнітних наводок на вхідні ключі вибірки.
