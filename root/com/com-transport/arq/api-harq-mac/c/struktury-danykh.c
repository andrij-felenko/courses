#include <stdint.h>
#include <stdbool.h>

/* Версія надлишковості (Redundancy Version) */
typedef enum {
    HARQ_RV_0 = 0,  /* Систематичні біти + базовий паритет */
    HARQ_RV_2 = 2,  /* Перша порція додаткового паритету */
    HARQ_RV_3 = 3,  /* Друга порція додаткового паритету */
    HARQ_RV_1 = 1   /* Залишкова порція паритету / високі частоти */
} HarqRedundancyVersion;

/* Стан процесу HARQ */
typedef enum {
    HARQ_STATE_IDLE = 0,
    HARQ_STATE_ACTIVE_TX,
    HARQ_STATE_WAITING_FEEDBACK,
    HARQ_STATE_MAX_RETRIES_EXCEEDED
} HarqProcessState;

/* Результат декодування фізичного рівня */
typedef enum {
    HARQ_FEEDBACK_NACK = 0,
    HARQ_FEEDBACK_ACK  = 1,
    HARQ_FEEDBACK_DTX  = 2  /* Discontinuous Transmission: база не почула відповіді */
} HarqFeedback;

/* Дескриптор процесу HARQ передавача (TX) */
typedef struct {
    uint8_t process_id;             /* ID процесу: 0..15 */
    HarqProcessState state;         /* Поточний стан автомата */
    bool ndi;                       /* New Data Indicator (0 або 1) */
    HarqRedundancyVersion rv;       /* Поточний індекс RV */
    uint8_t transmission_count;     /* Лічильник спроб (1..MAX_HARQ_RETRIES) */
    uint8_t mcs_index;              /* Індекс модуляції та кодування (0..31) */
    uint32_t transport_block_size;  /* Розмір корисних даних у байтах (TBS) */
    uint32_t code_bits_len;         /* Довжина кодового блоку після кодера */
    uint8_t *payload_ptr;           /* Покажчик на корисне навантаження в пам'яті */
} HarqTxProcessDescriptor;

/* Дескриптор софт-буфера процесу HARQ приймача (RX) */
typedef struct {
    uint8_t process_id;             /* ID процесу: 0..15 */
    bool last_ndi;                  /* Останній зафіксований стан NDI */
    uint8_t combined_transmissions; /* Кількість об'єднаних копій у буфері */
    uint32_t soft_buffer_size;      /* Кількість виділених LLR комірок */
    int8_t *llr_buffer;             /* Масив логарифмічних відношень (8-біт квантування) */
    bool crc_pass;                  /* Прапорець успішного проходження CRC */
} HarqRxBufferDescriptor;
