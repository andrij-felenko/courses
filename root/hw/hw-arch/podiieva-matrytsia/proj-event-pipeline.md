# ⚙️ Автономний конвеєр збору даних на базі Nordic DPPI та STM32 DMAMUX

Цей практичний проект демонструє побудову повністю автономного вимірювального конвеєра, у якому периферійні вузли мікроконтролера синхронізуються, проводять вимірювання та пересилають дані в пам'ять без виконання жодної інструкції процесорного ядра під час вимірювального циклу.

У типових завданнях високошвидкісного збору даних (наприклад, реєстрація перехідних процесів у силових перетворювачах, моніторинг вібрацій або зчитування сейсмічних датчиків) використання класичних [переривань](root:hw-arch/interrupts) для запуску вибірки вносить неприпустимий фазовий джиттер та змушує ядро споживати міліампери струму в безперервному очікуванні події. Автономний конвеєр на базі подієвої матриці та [прямого доступу до пам'яті (DMA)](root:hw-arch/dma) розв'язує цю проблему апаратно: ядро лише один раз налаштовує топологію каналів, після чого засинає в [режимі глибокого енергозбереження](root:hw-arch/sleep-modes).

## Постановка інженерного завдання

Необхідно реалізувати наступний п'ятиланковий вимірювальний сценарій:
1. Зовнішній аналоговий сигнал перевищує заданий поріг на компараторі або фіксується фронт на виводі порту введення-виведення.
2. Подія миттєво запускає апаратний [таймер](root:hw-arch/timer-counter), який відраховує калібровану затримку (10 мкс) для згасання комутаційних шумів та брязкоту в системі.
3. Після закінчення затримки таймер формує вихідний імпульс (TRGO або EVENT), який запускає серію з 4 послідовних вибірок АЦП на різних каналах.
4. Кожне завершене перетворення АЦП апаратно генерує подію запиту, яка змушує DMA пересилати 16-бітний відлік у виділений кільцевий буфер у SRAM.
5. Процесорне ядро весь цей час перебуває в режимі сну (WFI / Sleep), споживаючи одиниці мікроамперів, і прокидається єдиним перериванням `Transfer Complete` лише після того, як DMA заповнить повний блок із 1024 відліків.

Розгляньмо дві провідні архітектурні реалізації: розподілену шину Nordic DPPI (nRF5340 / nRF9160) та тригерний мультиплексор STM32 DMAMUX.

## Архітектура 1: Nordic DPPI (Distributed PPI)

У сучасних чипах Nordic архітектура DPPI позбавлена централізованого комутатора: кожен модуль містить локальні регістри `PUBLISH_*` (передавач події на шину) та `SUBSCRIBE_*` (приймач задачі з шини).

Для нашого конвеєра виділимо два канали DPPI:
- **Канал 0 (`DPPI_CH_TRIGGER`):** компаратор `COMP->EVENTS_UP` транслює строб на канал 0, а таймер `TIMER0->SUBSCRIBE_START` підписаний на канал 0.
- **Канал 1 (`DPPI_CH_SAMPLE`):** подія порівняння таймера `TIMER0->EVENTS_COMPARE[0]` транслюється на канал 1, а блок послідовного АЦП `SAADC->SUBSCRIBE_SAMPLE` підписаний на канал 1.

Зверніть увагу на прапорець `SHORTS` у таймері: біт `COMPARE0_CLEAR` змушує таймер автоматично обнулити свій лічильник CNT у ту саму мить, коли спрацьовує канал порівняння, готуючи його до наступного тригера без участі програмного коду.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>

/* Базові структури регістрів для ілюстрації апаратної конфігурації DPPI */
#define DPPI_CH_TRIGGER   0U
#define DPPI_CH_SAMPLE    1U
#define BUFFER_SIZE_WORDS 1024U

/* Умовні вказівники на периферійні блоки nRF (CMSIS-сумісні) */
typedef struct {
    volatile uint32_t TASKS_START;
    volatile uint32_t TASKS_STOP;
    volatile uint32_t EVENTS_UP;
    volatile uint32_t PUBLISH_UP;
} COMP_Regs;

typedef struct {
    volatile uint32_t TASKS_START;
    volatile uint32_t TASKS_STOP;
    volatile uint32_t TASKS_CLEAR;
    volatile uint32_t EVENTS_COMPARE[4];
    volatile uint32_t CC[4];
    volatile uint32_t SHORTS;
    volatile uint32_t SUBSCRIBE_START;
    volatile uint32_t PUBLISH_COMPARE[4];
} TIMER_Regs;

typedef struct {
    volatile uint32_t TASKS_START;
    volatile uint32_t TASKS_SAMPLE;
    volatile uint32_t EVENTS_END;
    volatile uint32_t RESULT_PTR;
    volatile uint32_t RESULT_MAXCNT;
    volatile uint32_t SUBSCRIBE_SAMPLE;
} SAADC_Regs;

typedef struct {
    volatile uint32_t CHEN;
    volatile uint32_t CHENSET;
    volatile uint32_t CHENCLR;
} DPPI_Regs;

/* Зовнішні адреси блоків */
extern COMP_Regs  * const NRF_COMP;
extern TIMER_Regs * const NRF_TIMER0;
extern SAADC_Regs * const NRF_SAADC;
extern DPPI_Regs  * const NRF_DPPI;

/* Буфер даних для EasyDMA у пам'яті SRAM */
static uint16_t adc_dma_buffer[BUFFER_SIZE_WORDS] __attribute__((aligned(4)));

void pipeline_dppi_init(void) {
    /* 1. Налаштування джерела: Компаратор публікує подію перевищення порогу */
    /* Біт 31 (EN) = 1, Біти 0..7 = номер каналу (0) */
    NRF_COMP->PUBLISH_UP = (1UL << 31) | DPPI_CH_TRIGGER;

    /* 2. Налаштування проміжної ланки: Таймер слухає канал 0 та публікує на канал 1 */
    NRF_TIMER0->SUBSCRIBE_START = (1UL << 31) | DPPI_CH_TRIGGER;
    NRF_TIMER0->CC[0] = 160; /* 10 мкс при тактуванні 16 МГц */
    NRF_TIMER0->SHORTS = (1UL << 0); /* Автоскидання COMPARE0 -> CLEAR */
    NRF_TIMER0->PUBLISH_COMPARE[0] = (1UL << 31) | DPPI_CH_SAMPLE;

    /* 3. Налаштування споживача: SAADC підписаний на запуск вибірки з каналу 1 */
    NRF_SAADC->SUBSCRIBE_SAMPLE = (1UL << 31) | DPPI_CH_SAMPLE;
    NRF_SAADC->RESULT_PTR = (uint32_t)adc_dma_buffer;
    NRF_SAADC->RESULT_MAXCNT = BUFFER_SIZE_WORDS;

    /* 4. Активація каналів 0 та 1 у системному комутаторі DPPI */
    NRF_DPPI->CHENSET = (1UL << DPPI_CH_TRIGGER) | (1UL << DPPI_CH_SAMPLE);

    /* 5. Запуск EasyDMA для SAADC та переведення ядра в режим очікування */
    NRF_SAADC->TASKS_START = 1;
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <span>
#include <concepts>

namespace hal::dppi {

/* Безпечна типізована обгортка над каналом DPPI */
class Channel {
public:
    explicit constexpr Channel(uint8_t id) : id_(id) {}

    [[nodiscard]] constexpr uint32_t publish_config() const noexcept {
        return (1UL << 31) | (id_ & 0x1F);
    }

    [[nodiscard]] constexpr uint32_t subscribe_config() const noexcept {
        return (1UL << 31) | (id_ & 0x1F);
    }

    [[nodiscard]] constexpr uint32_t mask() const noexcept {
        return (1UL << id_);
    }

    [[nodiscard]] constexpr uint8_t id() const noexcept { return id_; }

private:
    uint8_t id_;
};

struct HardwareRegisters {
    struct Comp {
        volatile uint32_t TASKS_START;
        volatile uint32_t TASKS_STOP;
        volatile uint32_t EVENTS_UP;
        volatile uint32_t PUBLISH_UP;
    };

    struct Timer {
        volatile uint32_t TASKS_START;
        volatile uint32_t TASKS_STOP;
        volatile uint32_t TASKS_CLEAR;
        volatile uint32_t EVENTS_COMPARE[4];
        volatile uint32_t CC[4];
        volatile uint32_t SHORTS;
        volatile uint32_t SUBSCRIBE_START;
        volatile uint32_t PUBLISH_COMPARE[4];
    };

    struct Saadc {
        volatile uint32_t TASKS_START;
        volatile uint32_t TASKS_SAMPLE;
        volatile uint32_t EVENTS_END;
        volatile uint32_t RESULT_PTR;
        volatile uint32_t RESULT_MAXCNT;
        volatile uint32_t SUBSCRIBE_SAMPLE;
    };

    struct Dppi {
        volatile uint32_t CHEN;
        volatile uint32_t CHENSET;
        volatile uint32_t CHENCLR;
    };
};

/* RAII-драйвер автономного вимірювального конвеєра */
template <typename Regs = HardwareRegisters>
class AutonomousAcquisitionPipeline {
public:
    AutonomousAcquisitionPipeline(
        typename Regs::Comp* comp,
        typename Regs::Timer* timer,
        typename Regs::Saadc* saadc,
        typename Regs::Dppi* dppi,
        Channel trigger_channel,
        Channel sample_channel
    ) noexcept
        : comp_(comp), timer_(timer), saadc_(saadc), dppi_(dppi),
          trig_ch_(trigger_channel), sample_ch_(sample_channel) {}

    void setup(std::span<uint16_t> destination_buffer, uint32_t settling_ticks = 160) noexcept {
        /* Конфігурація публікації та підписки без магічних чисел */
        comp_->PUBLISH_UP = trig_ch_.publish_config();

        timer_->SUBSCRIBE_START = trig_ch_.subscribe_config();
        timer_->CC[0] = settling_ticks;
        timer_->SHORTS = 1UL << 0; /* Автоматичне скидання лічильника */
        timer_->PUBLISH_COMPARE[0] = sample_ch_.publish_config();

        saadc_->SUBSCRIBE_SAMPLE = sample_ch_.subscribe_config();
        saadc_->RESULT_PTR = reinterpret_cast<uint32_t>(destination_buffer.data());
        saadc_->RESULT_MAXCNT = static_cast<uint32_t>(destination_buffer.size());

        /* Активація каналів у матриці */
        dppi_->CHENSET = trig_ch_.mask() | sample_ch_.mask();

        /* Переведення АЦП у стан готовності приймати EasyDMA-тригери */
        saadc_->TASKS_START = 1;
    }

    void stop() noexcept {
        dppi_->CHENCLR = trig_ch_.mask() | sample_ch_.mask();
        saadc_->TASKS_STOP = 1;
        timer_->TASKS_STOP = 1;
        comp_->TASKS_STOP = 1;
    }

private:
    typename Regs::Comp*  comp_;
    typename Regs::Timer* timer_;
    typename Regs::Saadc* saadc_;
    typename Regs::Dppi*  dppi_;
    Channel trig_ch_;
    Channel sample_ch_;
};

} // namespace hal::dppi
```
:::

## Архітектура 2: STM32 DMAMUX та таймерні тригери TRGO

У мікроконтролерах STM32 (наприклад, серій STM32G4 або STM32H7) комутація подій побудована на взаємодії тригерних виходів таймерів (`TRGO`), каналів АЦП та блоку `DMAMUX Request Generator`.

Конвеєр працює за наступним детермінованим циклом:
1. Зовнішній сигнал на ніжці порту EXTI ініціює апаратний тригер для підлеглого таймера `TIM2` через внутрішню тригерну лінію `ITR1`.
2. Таймер `TIM2` відраховує паузу 10 мкс і виставляє імпульс `TRGO` (збіг у каналі порівняння OC1REF).
3. Сигнал `TRGO` з'єднаний безпосередньо зі входом зовнішнього тригера `EXTSEL` модуля `ADC1`. АЦП робить перетворення послідовності 4 аналогових каналів.
4. Сигнал закінчення перетворення регулярної групи (`ADC1_EOC`) надходить у блок `DMAMUX1`.
5. Модуль `DMAMUX1` транслює цей імпульс як запит для `DMA1_Channel1`, який копіює дані з регістра `ADC1->DR` у масив SRAM без втручання процесора.

:::tabs
```c
#include <stdint.h>

/* Регістрові зміщення та маски для STM32G4 DMAMUX */
#define DMAMUX_REQ_GEN_EXTI0   1U
#define DMAMUX_REQ_ADC1_EOC    5U

typedef struct {
    volatile uint32_t CCR[16];   /* Канали конфігурації DMA (Channel Control Registers) */
    volatile uint32_t RGCR[4];   /* Регістри генераторів запитів (Request Generator) */
    volatile uint32_t RGSR;      /* Статус генераторів запитів */
    volatile uint32_t RGCFR;     /* Скидання прапорців генераторів */
} DMAMUX_Channel_Regs;

typedef struct {
    volatile uint32_t CR1;
    volatile uint32_t CR2;
    volatile uint32_t SMCR;
    volatile uint32_t DIER;
    volatile uint32_t SR;
    volatile uint32_t EGR;
    volatile uint32_t CCMR1;
    volatile uint32_t CCER;
    volatile uint32_t CNT;
    volatile uint32_t PSC;
    volatile uint32_t ARR;
    volatile uint32_t CCR1;
} TIM_TypeDef_Lite;

typedef struct {
    volatile uint32_t ISR;
    volatile uint32_t IER;
    volatile uint32_t CR;
    volatile uint32_t CFGR;
    volatile uint32_t DR;
} ADC_TypeDef_Lite;

extern DMAMUX_Channel_Regs * const DMAMUX1_Regs;
extern TIM_TypeDef_Lite     * const TIM2_Regs;
extern ADC_TypeDef_Lite     * const ADC1_Regs;

void stm32_dmamux_pipeline_init(void) {
    /* 1. Налаштування TIM2 у режимі Master Mode (видача TRGO по збігу CCR1) */
    TIM2_Regs->PSC = 169;       /* 170 МГц / 170 = 1 МГц (1 мкс на тік) */
    TIM2_Regs->ARR = 1000;      /* Загальний період */
    TIM2_Regs->CCR1 = 10;       /* Імпульс через 10 мкс */
    
    /* CR2: MMS[2:0] = 0b100 (Compare Pulse - сигнал TRGO при збігу CC1IF) */
    TIM2_Regs->CR2 &= ~(0x7UL << 4);
    TIM2_Regs->CR2 |= (0x4UL << 4);

    /* SMCR: Slave Mode Selection - запуск по тригеру від EXTI (Trigger Mode) */
    TIM2_Regs->SMCR |= (0x6UL); /* SMS = 0b0110 (Trigger Mode) */

    /* 2. Налаштування ADC1: запуск від тригера TIM2_TRGO */
    /* CFGR: EXTEN = 0b01 (фронт), EXTSEL = 0b1011 (тригер від TIM2_TRGO) */
    ADC1_Regs->CFGR &= ~((0x3UL << 10) | (0x1FUL << 5));
    ADC1_Regs->CFGR |= (0x1UL << 10) | (0x0BUL << 5);
    ADC1_Regs->CFGR |= (1UL << 0); /* DMAEN: Дозвіл видачі DMA запитів */

    /* 3. Налаштування DMAMUX Channel 0 для маршрутизації сигналу ADC1 -> DMA1 Channel 1 */
    /* DMAMUX1 Channel 0 підключається до виходу запитів ADC1 (ідентифікатор 5) */
    DMAMUX1_Regs->CCR[0] = (DMAMUX_REQ_ADC1_EOC & 0x7FUL);

    /* 4. Запуск АЦП у режим очікування тригера */
    ADC1_Regs->CR |= (1UL << 2); /* ADSTART */
}
```
```cpp
#include <cstdint>
#include <cstddef>

namespace hal::stm32 {

enum class TriggerSource : uint8_t {
    Tim2Trgo = 0x0B,
    Tim3Trgo = 0x0E,
    ExtiLine11 = 0x06
};

enum class TriggerEdge : uint8_t {
    Disabled = 0x00,
    RisingEdge = 0x01,
    FallingEdge = 0x02,
    BothEdges = 0x03
};

struct DmaMuxConfig {
    uint8_t dma_request_id;
    bool enable_sync;
    TriggerSource sync_trigger;
    TriggerEdge sync_edge;
};

class HardwarePipelineBuilder {
public:
    static void configure_timer_master(uintptr_t tim_base, uint32_t delay_ticks) noexcept {
        auto* tim = reinterpret_cast<volatile uint32_t*>(tim_base);
        // CR2 (зсув 0x04): встановлюємо MMS = 0b100 (Compare pulse)
        tim[1] = (tim[1] & ~(0x7UL << 4)) | (0x4UL << 4);
        // CCR1 (зсув 0x34): записуємо затримку
        tim[13] = delay_ticks;
    }

    static void configure_adc_external_trigger(
        uintptr_t adc_base,
        TriggerSource trigger,
        TriggerEdge edge
    ) noexcept {
        auto* cfgr = reinterpret_cast<volatile uint32_t*>(adc_base + 0x0C);
        uint32_t val = *cfgr;
        val &= ~((0x3UL << 10) | (0x1FUL << 5));
        val |= (static_cast<uint32_t>(edge) << 10);
        val |= (static_cast<uint32_t>(trigger) << 5);
        val |= (1UL << 0); // DMAEN
        *cfgr = val;
    }

    static void route_dmamux(uintptr_t dmamux_base, uint8_t channel, uint8_t request_source) noexcept {
        auto* ccr = reinterpret_cast<volatile uint32_t*>(dmamux_base + channel * 4);
        *ccr = (request_source & 0x7FUL);
    }
};

} // namespace hal::stm32
```
:::

## Подвійна буферизація та обслуговування переривань

Коли контролер DMA заповнює половину або повний об'єм буфера пам'яті, він виставляє запити на переривання `Half Transfer` (HT) та `Transfer Complete` (TC). Це дозволяє реалізувати класичну схему **подвійної буферизації** (англ. *Ping-Pong Buffering*):
- Поки ядро процесора спокійно опрацьовує першу половину буфера (відліки `0..511`), апаратний DMA-контролер у фоновому режимі наповнює другу половину буфера (`512..1023`).
- Конвеєр не зупиняється ані на мікросекунду: відсутні пропуски відліків, а обчислювальне навантаження ядра розтягується в часі рівномірно.

## Захист від гонок та керування бар'єрами пам'яті

Під час роботи повністю апаратного конвеєра критично важливо дотримуватися дисципліни синхронізації пам'яті та периферійних шин:

1. **Інструкції бар'єрів пам'яті (`DMB` / `DSB`):**
   Перед переведенням процесора в сон після конфігурації дескрипторів DMA та регістрів подієвої матриці слід виконати інструкцію `__DSB()` (*Data Synchronization Barrier*). Вона гарантує, що всі шинні буфери запису ядра спорожнені, а конфігурація фізично записана в кремнієві тригери модулів до переходу в сон.
2. **Когерентність кеша даних (D-Cache Invalidation):**
   Якщо процесорне ядро має увімкнений D-Cache (наприклад, у чипах Cortex-M7 або Cortex-M33), область буфера SRAM перед стартом DMA необхідно очистити або інвалідувати (*Invalidate D-Cache*). Якщо цього не зробити, ядро після пробудження зчитає застарілі дані з кеш-ліній замість свіжих відліків, записаних контролером DMA напряму в SRAM.
3. **Вирівнювання буферів у пам'яті:**
   Буфери прямого доступу обов'язково вирівнюються за межею кеш-лінії (зазвичай 32 байти, `__attribute__((aligned(32)))`), щоб уникнути фальшивого розділення пам'яті (*False Sharing*) між DMA та звичайними змінними ядра.
4. **Захист від переповнення (Overrun Trap):**
   Регістр статусу АЦП та DMA повинен обов'язково перевірятися в обробнику пробудження ядра на наявність біта `OVR` (Overrun). Його поява сигналізує про те, що частота зовнішніх подій перевищила пропускну здатність АЦП або шини пам'яті, внаслідок чого частину відліків було втрачено.
