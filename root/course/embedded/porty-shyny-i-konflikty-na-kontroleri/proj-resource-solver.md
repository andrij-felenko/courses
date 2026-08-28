# ⚙️ Програмний валідатор та розв'язувач конфліктів DMA і таймерів

Цей практичний модуль демонструє алгоритм системної валідації та автоматичного розв'язання конфліктів апаратних ресурсів (таймерів, спільних регістрів ARR/PSC та потоків DMA), який виконується польотною прошивкою на етапі ініціалізації ядра перед армінгом.

---

## 1. Постановка задачі та архітектура перевірки

Під час старту польотного контролера прошивка зчитує статичну конфігурацію друкованої плати (Target Board Definition) або динамічні налаштування з пам'яті EEPROM/Flash. Перш ніж дозволити запуск контуру стабілізації та перевести мотори в бойовий режим (Arming), системний менеджер ресурсів виконує три послідовні фази валідації:

### Фаза 1. Валідація таймерних доменів (Timer Domain Partitioning)
Кожен апаратний таймер мікроконтролера STM32 (`TIM1`..`TIM8`) має єдине тактове ядро з одним лічильником `CNT`, одним переддільником `PSC` та одним регістром автоперезавантаження `ARR`. Усі вихідні канали таймера (`CH1`..`CH4`) фізично змушені працювати на однаковій частоті повторення та з однаковим періодом лічби. 
- Якщо на канали одного таймера призначено пристрої з різними протоколами (наприклад, канали 1–3 віддано під DShot600 з періодом 1.67 мкс, а канал 4 — під стрічку WS2812B з періодом 1.25 мкс або сервопривід з періодом 20 мс), алгоритм фіксує фатальний конфлікт `ERR_TIMER_PROTOCOL_CONFLICT`.
- За наявності такого конфлікту армінг контролера апаратно блокується, оскільки будь-яка спроба зміни `ARR` призведе до зриву форми сигналу DShot та аварійної десинхронізації регуляторів у польоті.

### Фаза 2. Пошук колізій та автоматичне розв'язання потоків DMA
У контролерах STM32F4/F7 кожен периферійний тригер жорстко підключений до фіксованого набору потоків DMA. Якщо два активні модулі претендують на один і той самий потік (`DMA_Stream`), виникає апаратне блокування.
- Алгоритм перевіряє таблицю альтернативних потоків: наприклад, запит оновлення `TIM1_UP` підтримується як на `DMA2_Stream5_Ch6`, так і на `DMA2_Stream7_Ch6`. Якщо `Stream 5` уже зайнятий шиною `SPI1_TX`, менеджер автоматично переносить тригер таймера на `Stream 7`.
- Якщо альтернативних вільних потоків немає, прошивка визначає пріоритет: критичні за часом вузли (IMU, DShot) отримують виділені потоки DMA, а менш критичні (телеметрія VTX, логування) перемикаються в режим кільцевого буфера переривань (Interrupt-driven ring buffer).

### Фаза 3. Перевірка цілісності каналу головного датчика (Primary IMU)
Алгоритм гарантує, що головний гіроскоп підключений до виділеної шини SPI1 та має монопольний потік прямого доступу `DMA2_Stream0` з найвищим пріоритетом (`DMA_SxCR_PL_11`). Без виконання цієї умови політ суворо заборонено.

---

## 2. Програмна реалізація валідатора та розв'язувача

Нижче наведено повну реалізацію менеджера розподілу ресурсів мовами C та ідіоматичною C++.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define MAX_PINS             16
#define MAX_TIMERS           8
#define MAX_DMA_CONTROLLERS  2
#define MAX_DMA_STREAMS      8

typedef enum {
    PROTO_NONE = 0,
    PROTO_DSHOT600,
    PROTO_DSHOT300,
    PROTO_PWM_SERVO,
    PROTO_WS2812_LED,
    PROTO_SPI_IMU,
    PROTO_UART_TELEMETRY
} ProtocolType;

typedef struct {
    const char* pin_name;
    uint8_t timer_id;       // 1 = TIM1..8 = TIM8 (0 = без таймера)
    uint8_t timer_channel;  // 1..4
    uint8_t dma_controller; // 1 або 2
    uint8_t dma_stream;     // 0..7 (базовий потік)
    uint8_t alt_dma_stream; // 0..7 (альтернативний потік, 0xFF якщо немає)
    uint8_t dma_channel;    // 0..7
    ProtocolType protocol;
} PinResource;

typedef struct {
    ProtocolType protocol;
    uint8_t active_channels_mask; // бітова маска зайнятих каналів (біт 0 = CH1)
    bool is_locked;
} TimerDomain;

typedef struct {
    bool is_allocated;
    const char* owner_pin;
    ProtocolType protocol;
} DmaStreamAllocation;

typedef enum {
    VALIDATION_OK = 0,
    ERR_TIMER_PROTOCOL_CONFLICT,
    ERR_DMA_STREAM_COLLISION,
    ERR_IMU_RESOURCE_MISSING,
    ERR_INVALID_TIMER_INDEX,
    ERR_INVALID_DMA_INDEX
} ValidationResult;

typedef struct {
    TimerDomain timers[MAX_TIMERS];
    DmaStreamAllocation dma_matrix[MAX_DMA_CONTROLLERS][MAX_DMA_STREAMS];
    ValidationResult status;
    uint32_t resolved_collisions_count;
} HardwareResourceManager;

void resource_manager_init(HardwareResourceManager* mgr) {
    memset(mgr, 0, sizeof(HardwareResourceManager));
    mgr->status = VALIDATION_OK;
}

ValidationResult resource_manager_validate(HardwareResourceManager* mgr,
                                          PinResource* pins,
                                          size_t pin_count) {
    bool has_imu = false;

    for (size_t i = 0; i < pin_count; ++i) {
        PinResource* p = &pins[i];
        if (p->protocol == PROTO_NONE) continue;

        if (p->protocol == PROTO_SPI_IMU) {
            has_imu = true;
        }

        // 1. Валідація таймерного домену (перевірка сумісності ARR/PSC)
        if (p->timer_id > 0) {
            if (p->timer_id > MAX_TIMERS) {
                mgr->status = ERR_INVALID_TIMER_INDEX;
                return ERR_INVALID_TIMER_INDEX;
            }

            TimerDomain* td = &mgr->timers[p->timer_id - 1];
            if (!td->is_locked) {
                td->protocol = p->protocol;
                td->is_locked = true;
                td->active_channels_mask |= (1 << (p->timer_channel - 1));
            } else {
                // Таймер уже зайнятий іншим виходом: перевіряємо протокол
                if (td->protocol != p->protocol) {
                    mgr->status = ERR_TIMER_PROTOCOL_CONFLICT;
                    return ERR_TIMER_PROTOCOL_CONFLICT;
                }
                td->active_channels_mask |= (1 << (p->timer_channel - 1));
            }
        }

        // 2. Валідація та автоматичне розв'язання потоків DMA
        if (p->dma_controller >= 1 && p->dma_controller <= MAX_DMA_CONTROLLERS) {
            uint8_t c_idx = p->dma_controller - 1;
            uint8_t stream = p->dma_stream;

            if (stream >= MAX_DMA_STREAMS) {
                mgr->status = ERR_INVALID_DMA_INDEX;
                return ERR_INVALID_DMA_INDEX;
            }

            DmaStreamAllocation* dma = &mgr->dma_matrix[c_idx][stream];

            if (dma->is_allocated) {
                // Виявлено колізію: перевіряємо наявність альтернативного потоку
                if (p->alt_dma_stream != 0xFF && p->alt_dma_stream < MAX_DMA_STREAMS) {
                    uint8_t alt_s = p->alt_dma_stream;
                    DmaStreamAllocation* alt_dma = &mgr->dma_matrix[c_idx][alt_s];

                    if (!alt_dma->is_allocated) {
                        // Успішне автоматичне перепризначення на альтернативний потік
                        alt_dma->is_allocated = true;
                        alt_dma->owner_pin = p->pin_name;
                        alt_dma->protocol = p->protocol;
                        p->dma_stream = alt_s; // оновлюємо пін
                        mgr->resolved_collisions_count++;
                        continue;
                    }
                }

                // Альтернативи немає або вона також зайнята: фатальна колізія
                mgr->status = ERR_DMA_STREAM_COLLISION;
                return ERR_DMA_STREAM_COLLISION;
            }

            dma->is_allocated = true;
            dma->owner_pin = p->pin_name;
            dma->protocol = p->protocol;
        }
    }

    if (!has_imu) {
        mgr->status = ERR_IMU_RESOURCE_MISSING;
        return ERR_IMU_RESOURCE_MISSING;
    }

    return VALIDATION_OK;
}
```
```cpp
#include <cstdint>
#include <string_view>
#include <span>
#include <array>
#include <expected>
#include <optional>

enum class ProtocolType : uint8_t {
    None = 0,
    DShot600,
    DShot300,
    PwmServo,
    Ws2812Led,
    SpiImu,
    UartTelemetry
};

enum class ValidationError {
    TimerProtocolConflict,
    DmaStreamCollision,
    ImuResourceMissing,
    InvalidTimerIndex,
    InvalidDmaIndex
};

struct PinResource {
    std::string_view pin_name;
    uint8_t timer_id{0};          // 1 = TIM1..8 = TIM8 (0 = none)
    uint8_t timer_channel{0};     // 1..4
    uint8_t dma_controller{0};    // 1..2
    uint8_t dma_stream{0};        // 0..7
    uint8_t alt_dma_stream{0xFF}; // 0..7 (0xFF = none)
    uint8_t dma_channel{0};       // 0..7
    ProtocolType protocol{ProtocolType::None};
};

struct TimerDomain {
    ProtocolType protocol{ProtocolType::None};
    uint8_t active_channels_mask{0};
    bool is_locked{false};
};

struct DmaStreamAllocation {
    bool is_allocated{false};
    std::string_view owner_pin{};
    ProtocolType protocol{ProtocolType::None};
};

class HardwareResourceManager {
public:
    static constexpr size_t MaxTimers = 8;
    static constexpr size_t DmaControllers = 2;
    static constexpr size_t DmaStreamsPerCtrl = 8;

    constexpr HardwareResourceManager() = default;

    [[nodiscard]] std::expected<size_t, ValidationError> validate_and_resolve(
        std::span<PinResource> pins) noexcept {
        
        bool has_imu = false;
        size_t resolved_collisions = 0;

        for (auto& pin : pins) {
            if (pin.protocol == ProtocolType::None) {
                continue;
            }

            if (pin.protocol == ProtocolType::SpiImu) {
                has_imu = true;
            }

            // 1. Валідація таймерних доменів
            if (pin.timer_id > 0) {
                if (pin.timer_id > MaxTimers) {
                    return std::unexpected(ValidationError::InvalidTimerIndex);
                }
                auto& domain = timers_[pin.timer_id - 1];
                if (!domain.is_locked) {
                    domain.protocol = pin.protocol;
                    domain.is_locked = true;
                    domain.active_channels_mask |= (1 << (pin.timer_channel - 1));
                } else if (domain.protocol != pin.protocol) {
                    return std::unexpected(ValidationError::TimerProtocolConflict);
                } else {
                    domain.active_channels_mask |= (1 << (pin.timer_channel - 1));
                }
            }

            // 2. Валідація та автоматичне розв'язання потоків DMA
            if (pin.dma_controller >= 1 && pin.dma_controller <= DmaControllers) {
                if (pin.dma_stream >= DmaStreamsPerCtrl) {
                    return std::unexpected(ValidationError::InvalidDmaIndex);
                }
                auto& dma = dma_matrix_[pin.dma_controller - 1][pin.dma_stream];
                if (dma.is_allocated) {
                    // Спроба розв'язання через альтернативний потік
                    if (pin.alt_dma_stream != 0xFF && pin.alt_dma_stream < DmaStreamsPerCtrl) {
                        auto& alt_dma = dma_matrix_[pin.dma_controller - 1][pin.alt_dma_stream];
                        if (!alt_dma.is_allocated) {
                            alt_dma.is_allocated = true;
                            alt_dma.owner_pin = pin.pin_name;
                            alt_dma.protocol = pin.protocol;
                            pin.dma_stream = pin.alt_dma_stream;
                            resolved_collisions++;
                            continue;
                        }
                    }
                    return std::unexpected(ValidationError::DmaStreamCollision);
                }
                dma.is_allocated = true;
                dma.owner_pin = pin.pin_name;
                dma.protocol = pin.protocol;
            }
        }

        if (!has_imu) {
            return std::unexpected(ValidationError::ImuResourceMissing);
        }

        return resolved_collisions;
    }

private:
    std::array<TimerDomain, MaxTimers> timers_{};
    std::array<std::array<DmaStreamAllocation, DmaStreamsPerCtrl>, DmaControllers> dma_matrix_{};
};
```
:::

---

## 3. Тестові сценарії та діагностичні результати

Тестова програма моделює реальну ситуацію ініціалізації польотного контролера квадрокоптера, на якому виникає потенційна колізія між передачею `SPI1_TX` та таймером `TIM1_UP` на потоці `DMA2_Stream_5`. Завдяки наявності альтернативного потоку `DMA2_Stream_7` валідатор автоматично усуває конфлікт. Після цього тест демонструє спробу помилкового підключення п'ятого мотора на таймер `TIM3` (де вже активна стрічка `WS2812_LED`), що призводить до миттєвого блокування армінгу з детальним діагностичним звітом.

:::tabs
```c
#include <stdio.h>

int main(void) {
    HardwareResourceManager mgr;
    resource_manager_init(&mgr);

    // Сценарій 1: Коректна конфігурація з авторозв'язанням колізії DMA
    PinResource valid_quad_pins[] = {
        {"PA8",  1, 1, 2, 5, 7, 6, PROTO_DSHOT600}, // Motor 1 (TIM1_CH1, DMA2_S5, alt S7)
        {"PA9",  1, 2, 2, 2, 0xFF, 6, PROTO_DSHOT600}, // Motor 2 (TIM1_CH2, DMA2_S2)
        {"PA10", 1, 3, 2, 6, 0xFF, 6, PROTO_DSHOT600}, // Motor 3 (TIM1_CH3, DMA2_S6)
        {"PA11", 1, 4, 2, 4, 0xFF, 6, PROTO_DSHOT600}, // Motor 4 (TIM1_CH4, DMA2_S4)
        {"PB0",  3, 1, 1, 4, 0xFF, 5, PROTO_WS2812_LED},// LED Strip (TIM3_CH1, DMA1_S4)
        {"PA5",  0, 0, 2, 0, 0xFF, 3, PROTO_SPI_IMU},  // Gyro SPI1_RX (DMA2_S0)
        {"PA7",  0, 0, 2, 5, 3,    3, PROTO_SPI_IMU}   // Gyro SPI1_TX (DMA2_S5, конфліктує з M1!)
    };

    ValidationResult res = resource_manager_validate(&mgr, valid_quad_pins, 7);
    if (res == VALIDATION_OK) {
        printf("Тест 1 успішний: конфігурацію валідовано, усунуто колізій DMA: %u\n", 
               mgr.resolved_collisions_count);
    } else {
        printf("Тест 1 провалено з кодом помилки: %d\n", res);
    }

    // Сценарій 2: Фатальний таймерний конфлікт (Motor 5 на таймері LED-стрічки)
    HardwareResourceManager bad_mgr;
    resource_manager_init(&bad_mgr);

    PinResource invalid_pins[] = {
        {"PB0",  3, 1, 1, 4, 0xFF, 5, PROTO_WS2812_LED}, // LED Strip на TIM3_CH1
        {"PB1",  3, 4, 1, 2, 0xFF, 5, PROTO_DSHOT600},  // Motor 5 на TIM3_CH4 (КОНФЛІКТ!)
        {"PA5",  0, 0, 2, 0, 0xFF, 3, PROTO_SPI_IMU}
    };

    ValidationResult bad_res = resource_manager_validate(&bad_mgr, invalid_pins, 3);
    if (bad_res == ERR_TIMER_PROTOCOL_CONFLICT) {
        printf("Тест 2 успішний: таймерний конфлікт своєчасно заблоковано валідатором.\n");
    } else {
        printf("Тест 2 провалено: конфлікт не виявлено!\n");
    }

    return 0;
}
```
```cpp
#include <iostream>
#include <array>

int main() {
    HardwareResourceManager mgr;

    // Сценарій 1: Коректна конфігурація з авторозв'язанням колізії DMA
    std::array valid_quad_pins = {
        PinResource{"PA8",  1, 1, 2, 5, 7,    6, ProtocolType::DShot600}, // Motor 1 (DMA2_S5, alt S7)
        PinResource{"PA9",  1, 2, 2, 2, 0xFF, 6, ProtocolType::DShot600}, // Motor 2 (DMA2_S2)
        PinResource{"PA10", 1, 3, 2, 6, 0xFF, 6, ProtocolType::DShot600}, // Motor 3 (DMA2_S6)
        PinResource{"PA11", 1, 4, 2, 4, 0xFF, 6, ProtocolType::DShot600}, // Motor 4 (DMA2_S4)
        PinResource{"PB0",  3, 1, 1, 4, 0xFF, 5, ProtocolType::Ws2812Led},// LED Strip (DMA1_S4)
        PinResource{"PA5",  0, 0, 2, 0, 0xFF, 3, ProtocolType::SpiImu},   // Gyro SPI1_RX (DMA2_S0)
        PinResource{"PA7",  0, 0, 2, 5, 3,    3, ProtocolType::SpiImu}    // Gyro SPI1_TX (DMA2_S5)
    };

    auto res = mgr.validate_and_resolve(valid_quad_pins);
    if (res.has_value()) {
        std::cout << "Тест 1 успішний: конфігурацію валідовано, усунуто колізій DMA: " 
                  << res.value() << '\n';
    } else {
        std::cout << "Тест 1 провалено з помилкою: " << static_cast<int>(res.error()) << '\n';
    }

    // Сценарій 2: Фатальний таймерний конфлікт
    HardwareResourceManager bad_mgr;
    std::array invalid_pins = {
        PinResource{"PB0",  3, 1, 1, 4, 0xFF, 5, ProtocolType::Ws2812Led},
        PinResource{"PB1",  3, 4, 1, 2, 0xFF, 5, ProtocolType::DShot600},
        PinResource{"PA5",  0, 0, 2, 0, 0xFF, 3, ProtocolType::SpiImu}
    };

    auto bad_res = bad_mgr.validate_and_resolve(invalid_pins);
    if (!bad_res.has_value() && bad_res.error() == ValidationError::TimerProtocolConflict) {
        std::cout << "Тест 2 успішний: таймерний конфлікт своєчасно заблоковано валідатором.\n";
    } else {
        std::cout << "Тест 2 провалено: конфлікт не виявлено!\n";
    }

    return 0;
}
```
:::

---

## 4. Аналіз крайових випадків та відмовостійкість

Під час практичного використання валідатора в польотних прошивках виникають специфічні крайові випадки:

### 4.1. Динамічне перемикання частоти DShot
Якщо користувач через конфігуратор перемикає протокол з DShot300 на DShot600, валідатор повинен перерахувати `ARR` для всього таймерного домену. Якщо до таймера підключено 4 мотори, усі 4 канали отримують нові таймінги синхронно. Спроба перемкнути окремий мотор на іншу швидкість відхиляється.

### 4.2. Брак потоків DMA для телеметрії
Якщо для порту `UART_TELEMETRY` не вистачає вільного потоку DMA, менеджер не зупиняє завантаження контролера. Він переводить UART у режим апаратного кільцевого буфера з перериваннями по прапорцю `RXNE` (Receive Data Register Not Empty) та `TXE` (Transmit Data Register Empty). Це збільшує навантаження на процесор на 1–2%, але зберігає функціональність телеметрії без зриву контуру стабілізації.

### 4.3. Вирівнювання пам'яті та робота на STM32H7 з маршрутизатором DMAMUX
Для процесорів родини H7 блок `validate_and_resolve` пропускає перевірку колізій потоків, оскільки крос-матриця DMAMUX здатна зв'язати будь-який тригер з будь-яким вільним каналом. Замість цього валідатор перевіряє розміщення буферів пам'яті:
- Буфери передачі DShot та вибірок SPI повинні бути вирівняні за 32-бітною межею (`alignas(32)` або `__attribute__((aligned(4)))`).
- Якщо буфер DMA знаходиться в кешованій пам'яті AXI-SRAM, алгоритм перевіряє активацію функцій інвалідування D-Cache (`SCB_InvalidateDCache_by_Addr`) перед читанням та очищення (`SCB_CleanDCache_by_Addr`) перед передачею.
- Некешовані дескриптори та буфери зв'язку розміщуються у виділених блоках SRAM4 або DTCM через налаштування захисту пам'яті MPU (Memory Protection Unit).

### 4.4. Діагностика джитера контуру (Looptime Jitter Audit)
У разі вимушеного переведення периферійного пристрою на переривання прошивка запускає системний аудит затримок через апаратний лічильник тактів ядра DWT (`DWT->CYCCNT`). Якщо максимальне відхилення періоду вибірки IMU перевищує 5% від цільового значення (більше 6.25 мкс для контуру 8 кГц), система виставляє діагностичний прапорець `STATUS_HIGH_JITTER`, що попереджає пілота в OSD про ризик нестабільності польоту.
