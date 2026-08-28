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
