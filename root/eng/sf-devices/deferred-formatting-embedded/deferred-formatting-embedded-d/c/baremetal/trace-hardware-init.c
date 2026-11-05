#include <stdint.h>
#include <stdbool.h>

/* Базові адреси та регістри налагоджувальних модулів ядра ARM Cortex-M */
#define DWT_CTRL             (*(volatile uint32_t *)0xE0001000)
#define DWT_CYCCNT           (*(volatile uint32_t *)0xE0001004)
#define DEMCR                (*(volatile uint32_t *)0xE000EDFC)
#define DEMCR_TRCENA         (1UL << 24)
#define DWT_CTRL_CYCCNTENA   (1UL << 0)

#define ITM_PORT0_U32        (*(volatile uint32_t *)0xE0000000)
#define ITM_PORT0_U16        (*(volatile uint16_t *)0xE0000000)
#define ITM_PORT0_U8         (*(volatile uint8_t  *)0xE0000000)
#define ITM_TER              (*(volatile uint32_t *)0xE0000E00)
#define ITM_TCR              (*(volatile uint32_t *)0xE0000E80)
#define ITM_TCR_ITMENA       (1UL << 0)

/* Розмір буфера логів у оперативній пам'яті */
#define LOG_RING_SIZE        512
#define LOG_RING_MASK        (LOG_RING_SIZE - 1)

typedef struct {
	uint8_t  storage[LOG_RING_SIZE];
	volatile uint32_t head;
	volatile uint32_t tail;
	volatile uint32_t last_timestamp;
	volatile uint32_t drop_count;
} trace_log_channel_t;

static trace_log_channel_t g_trace_channel;

/* Ініціалізація апаратного лічильника тактів DWT */
void trace_hardware_init(void) {
	DEMCR |= DEMCR_TRCENA;
	DWT_CYCCNT = 0;
	DWT_CTRL |= DWT_CTRL_CYCCNTENA;
}

/* Перевірка доступності порту ITM для запису без блокування ядра */
static inline bool itm_port_ready(void) {
	if ((ITM_TCR & ITM_TCR_ITMENA) && (ITM_TER & 1UL)) {
		return (ITM_PORT0_U32 != 0);
	}
	return false;
}

/* Швидкий вивід двійкового кадру через апаратний порт ITM */
void trace_emit_itm_fast(uint16_t event_id, uint32_t payload) {
	if (!itm_port_ready()) {
		return;
	}
	/* Відправлення 16-бітного ідентифікатора події */
	while (ITM_PORT0_U32 == 0);
	ITM_PORT0_U16 = event_id;

	/* Відправлення 32-бітного корисного навантаження */
	while (ITM_PORT0_U32 == 0);
	ITM_PORT0_U32 = payload;
}

/* Неблокувальний запис події у кільцевий буфер із дельта-міткою часу */
bool trace_log_record(uint16_t event_id, uint32_t payload) {
	uint32_t now = DWT_CYCCNT;
	uint32_t prev = g_trace_channel.last_timestamp;
	uint16_t delta_time = (uint16_t)((now - prev) & 0xFFFF);
	g_trace_channel.last_timestamp = now;

	uint32_t head = g_trace_channel.head;
	uint32_t tail = g_trace_channel.tail;
	uint32_t required = sizeof(uint16_t) + sizeof(uint16_t) + sizeof(uint32_t);

	if ((LOG_RING_SIZE - (head - tail)) < required) {
		g_trace_channel.drop_count++;
		return false;
	}

	/* Апаратний бар'єр пам'яті для впорядкування операцій запису */
	__asm volatile ("dmb" ::: "memory");

	uint32_t idx = head & LOG_RING_MASK;
	
	/* Запис ідентифікатора */
	g_trace_channel.storage[idx] = (uint8_t)(event_id & 0xFF);
	g_trace_channel.storage[(idx + 1) & LOG_RING_MASK] = (uint8_t)(event_id >> 8);

	/* Запис дельта-мітки часу */
	g_trace_channel.storage[(idx + 2) & LOG_RING_MASK] = (uint8_t)(delta_time & 0xFF);
	g_trace_channel.storage[(idx + 3) & LOG_RING_MASK] = (uint8_t)(delta_time >> 8);

	/* Запис 32-бітного аргументу */
	for (uint8_t i = 0; i < sizeof(uint32_t); ++i) {
		g_trace_channel.storage[(idx + 4 + i) & LOG_RING_MASK] = (uint8_t)(payload >> (i * 8));
	}

	__asm volatile ("dmb" ::: "memory");
	g_trace_channel.head = head + required;

	return true;
}
