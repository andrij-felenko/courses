#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <string.h>

#define STEP_DMA_BUFFER_HALF_SIZE   2048
#define STEP_DMA_BUFFER_TOTAL_SIZE  (STEP_DMA_BUFFER_HALF_SIZE * 2)
#define STEP_DRIVER_MAX_AXES        4

/* Конфігурація фізичних ліній осі приводу */
typedef struct {
	uint32_t step_pin_mask;    /* Бітова маска піна STEP (розряди 0..15 регістра BSRR) */
	uint32_t dir_pin_mask;     /* Бітова маска піна DIR (розряди 0..15 регістра BSRR) */
	bool current_direction;    /* Поточний логічний напрямок осі */
} StepAxisConfig;

/* Стан та структури подвійного буфера DMA */
typedef struct {
	uint32_t dma_buffer[STEP_DMA_BUFFER_TOTAL_SIZE];
	volatile bool segment_ready[2];    /* Прапорці валідності сегментів: 0 - Ping, 1 - Pong */
	volatile bool underrun_flag;       /* Аварійний прапорець спустошення буфера */
	uint32_t step_reset_mask;          /* Маска примусового скидання всіх ліній STEP у нуль */
	uint32_t dir_hold_mask;            /* Маска утримання поточних напрямків */
	StepAxisConfig axes[STEP_DRIVER_MAX_AXES];
	size_t axis_count;
} DmaStepDriver;

/* Ініціалізація структур даних драйвера */
void dma_step_driver_init(DmaStepDriver* driver, const StepAxisConfig* axes, size_t count) {
	if (!driver || !axes || count > STEP_DRIVER_MAX_AXES) return;

	driver->axis_count = count;
	driver->underrun_flag = false;
	driver->step_reset_mask = 0;
	driver->dir_hold_mask = 0;
	driver->segment_ready[0] = false;
	driver->segment_ready[1] = false;

	for (size_t i = 0; i < count; ++i) {
		driver->axes[i] = axes[i];
		/* Старші 16 бітів BSRR відповідають за скидання ліній у нуль */
		driver->step_reset_mask |= (axes[i].step_pin_mask << 16);
		if (axes[i].current_direction) {
			driver->dir_hold_mask |= axes[i].dir_pin_mask;
		} else {
			driver->dir_hold_mask |= (axes[i].dir_pin_mask << 16);
		}
	}

	/* Заповнення буфера початковими безпечними масками скидання кроків */
	uint32_t idle_pattern = driver->step_reset_mask | driver->dir_hold_mask;
	for (size_t i = 0; i < STEP_DMA_BUFFER_TOTAL_SIZE; ++i) {
		driver->dma_buffer[i] = idle_pattern;
	}
}

/* Заповнення розрахованого сегмента буфера масками керування */
void dma_step_driver_fill_segment(DmaStepDriver* driver, size_t segment_idx, const uint32_t* patterns, size_t len) {
	if (!driver || segment_idx > 1 || len > STEP_DMA_BUFFER_HALF_SIZE) return;

	uint32_t* dest = &driver->dma_buffer[segment_idx * STEP_DMA_BUFFER_HALF_SIZE];
	for (size_t i = 0; i < len; ++i) {
		dest[i] = patterns[i];
	}

	/* Якщо передано менше значень, решту сегмента заповнюємо безпечною маскою */
	uint32_t idle_pattern = driver->step_reset_mask | driver->dir_hold_mask;
	for (size_t i = len; i < STEP_DMA_BUFFER_HALF_SIZE; ++i) {
		dest[i] = idle_pattern;
	}

	/* Програмний бар'єр пам'яті перед передачею готовності сегмента */
	__asm__ volatile ("dmb 0xF" ::: "memory");
	driver->segment_ready[segment_idx] = true;
}

/* Обробник переривання контролера DMA (події Half-Transfer та Transfer-Complete) */
void dma_step_driver_isr(DmaStepDriver* driver, bool is_transfer_complete) {
	if (!driver) return;

	/* Визначаємо спожитий сегмент та наступний сегмент у кільці */
	size_t consumed_segment = is_transfer_complete ? 1 : 0;
	size_t next_segment = is_transfer_complete ? 0 : 1;

	/* Спожитий сегмент маркується як вільний для планувальника руху */
	driver->segment_ready[consumed_segment] = false;

	/* Перевірка готовності наступного блоку даних */
	if (!driver->segment_ready[next_segment]) {
		/* Спустошення буфера: підміна наступного сегмента безпечним холостим патерном */
		driver->underrun_flag = true;
		uint32_t* next_buf = &driver->dma_buffer[next_segment * STEP_DMA_BUFFER_HALF_SIZE];
		uint32_t idle_pattern = driver->step_reset_mask | driver->dir_hold_mask;

		for (size_t i = 0; i < STEP_DMA_BUFFER_HALF_SIZE; ++i) {
			next_buf[i] = idle_pattern;
		}
	}
}

/* Миттєва апаратна зупинка генерації імпульсів */
void dma_step_driver_abort(volatile uint32_t* bsrr_reg, uint32_t step_reset_mask) {
	/* Пряме скидання ліній кроків у BSRR */
	*bsrr_reg = step_reset_mask;
}
