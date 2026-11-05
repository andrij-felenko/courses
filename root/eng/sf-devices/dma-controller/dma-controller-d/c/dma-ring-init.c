#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

/* Регістрова структура одного каналу контролера DMA */
typedef struct {
	volatile uint32_t CR;     /* Керуючий регістр конфігурації каналу */
	volatile uint32_t NDTR;   /* Лічильник кількості передач даних */
	volatile uint32_t PAR;    /* Фізична адреса периферійного пристрою */
	volatile uint32_t MAR;    /* Фізична адреса буфера в пам'яті */
	volatile uint32_t RESERVED;
} dma_channel_reg_t;

/* Регістри загального статусу та скидання прапорів контролера */
typedef struct {
	volatile uint32_t ISR;    /* Регістр статусу переривань каналів */
	volatile uint32_t IFCR;   /* Регістр очищення прапорів переривань */
} dma_common_reg_t;

/* Бітові маски керуючого регістра CR */
#define DMA_CR_EN         (1U << 0)   /* Дозвіл роботи каналу */
#define DMA_CR_TCIE       (1U << 1)   /* Дозвіл переривання повного завершення */
#define DMA_CR_HTIE       (1U << 2)   /* Дозвіл переривання половини передачі */
#define DMA_CR_TEIE       (1U << 3)   /* Дозвіл переривання помилки шини */
#define DMA_CR_DIR_P2M    (0U << 4)   /* Напрямок: периферія -> оперативна пам'ять */
#define DMA_CR_DIR_M2P    (1U << 4)   /* Напрямок: оперативна пам'ять -> периферія */
#define DMA_CR_CIRC       (1U << 5)   /* Циклічний кільцевий режим буфера */
#define DMA_CR_PINC       (1U << 6)   /* Автоінкремент адреси периферії */
#define DMA_CR_MINC       (1U << 7)   /* Автоінкремент адреси пам'яті */
#define DMA_CR_PSIZE_8    (0U << 8)   /* Розмірність периферії: 8 бітів */
#define DMA_CR_PSIZE_16   (1U << 8)   /* Розмірність периферії: 16 бітів */
#define DMA_CR_PSIZE_32   (2U << 8)   /* Розмірність периферії: 32 біти */
#define DMA_CR_MSIZE_8    (0U << 10)  /* Розмірність пам'яті: 8 бітів */
#define DMA_CR_MSIZE_16   (1U << 10)  /* Розмірність пам'яті: 16 бітів */
#define DMA_CR_MSIZE_32   (2U << 10)  /* Розмірність пам'яті: 32 біти */
#define DMA_CR_PL_VERY_HI (3U << 12)  /* Найвищий пріоритет арбітражу */

/* Маски зміщення прапорів для каналу у регістрах ISR та IFCR */
#define DMA_FLAG_GIF_POS  0U          /* Загальний прапор події */
#define DMA_FLAG_TCIF_POS 1U          /* Прапор повного завершення передачі */
#define DMA_FLAG_HTIF_POS 2U          /* Прапор половини передачі */
#define DMA_FLAG_TEIF_POS 3U          /* Прапор помилки шинної транзакції */

/* Бар'єри пам'яті процесорного ядра */
#define DMA_BARRIER_DATA()        __asm volatile("dmb 0xF" ::: "memory")
#define DMA_BARRIER_SYNC()        __asm volatile("dsb 0xF" ::: "memory")

/* Типи зворотних викликів драйвера */
typedef void (*dma_half_transfer_cb_t)(void *context);
typedef void (*dma_full_transfer_cb_t)(void *context);
typedef void (*dma_error_cb_t)(void *context);

/* Контекстний дескриптор кільцевого драйвера DMA */
typedef struct {
	dma_channel_reg_t *channel;
	dma_common_reg_t  *controller;
	uint8_t            channel_number; /* Номер каналу: 1..7 */
	uint8_t           *buffer;
	uint16_t           buffer_size;
	dma_half_transfer_cb_t on_half_complete;
	dma_full_transfer_cb_t on_full_complete;
	dma_error_cb_t         on_error;
	void                  *user_context;
} dma_ring_driver_t;

/* Ініціалізація каналу DMA у циклічному режимі прийому */
bool dma_ring_init(dma_ring_driver_t *drv,
                   dma_channel_reg_t *channel,
                   dma_common_reg_t  *controller,
                   uint8_t channel_number,
                   uint32_t periph_addr,
                   uint8_t *buffer,
                   uint16_t buffer_size,
                   dma_half_transfer_cb_t on_half,
                   dma_full_transfer_cb_t on_full,
                   dma_error_cb_t on_error,
                   void *context) {
	if (!drv || !channel || !controller || !buffer || (buffer_size == 0) || (buffer_size % 2 != 0)) {
		return false;
	}

	drv->channel = channel;
	drv->controller = controller;
	drv->channel_number = channel_number;
	drv->buffer = buffer;
	drv->buffer_size = buffer_size;
	drv->on_half_complete = on_half;
	drv->on_full_complete = on_full;
	drv->on_error = on_error;
	drv->user_context = context;

	/* Крок 1: Деактивація каналу та очікування завершення поточної транзакції */
	drv->channel->CR &= ~DMA_CR_EN;
	DMA_BARRIER_SYNC();
	while (drv->channel->CR & DMA_CR_EN) {
		/* Очікування переходу цифрового автомата у зупинений стан */
	}

	/* Крок 2: Очищення всіх прапорів переривань даного каналу */
	uint32_t flag_shift = (channel_number - 1U) * 4U;
	drv->controller->IFCR = (0xFU << flag_shift);
	DMA_BARRIER_SYNC();

	/* Кроки 3-5: Запис фізичних адрес периферії, пам'яті та лічильника */
	drv->channel->PAR = periph_addr;
	drv->channel->MAR = (uint32_t)(uintptr_t)buffer;
	drv->channel->NDTR = buffer_size;

	/* Крок 6: Конфігурація регістра CR: прийом, кільце, інкремент пам'яті, переривання */
	uint32_t cr_config = DMA_CR_DIR_P2M |
	                     DMA_CR_CIRC |
	                     DMA_CR_MINC |
	                     DMA_CR_PSIZE_8 |
	                     DMA_CR_MSIZE_8 |
	                     DMA_CR_PL_VERY_HI |
	                     DMA_CR_TCIE |
	                     DMA_CR_HTIE |
	                     DMA_CR_TEIE;

	drv->channel->CR = cr_config;
	DMA_BARRIER_DATA();

	return true;
}

/* Запуск прийому даних */
void dma_ring_start(dma_ring_driver_t *drv) {
	if (!drv || !drv->channel) return;
	DMA_BARRIER_SYNC();
	drv->channel->CR |= DMA_CR_EN;
	DMA_BARRIER_DATA();
}

/* Зупинка каналу */
void dma_ring_stop(dma_ring_driver_t *drv) {
	if (!drv || !drv->channel) return;
	drv->channel->CR &= ~DMA_CR_EN;
	DMA_BARRIER_SYNC();
	while (drv->channel->CR & DMA_CR_EN) {
		/* Очікування повної зупинки магістралі */
	}
}

/* Зчитування поточної позиції голови запису DMA у кільцевому масиві */
uint16_t dma_ring_get_head_index(const dma_ring_driver_t *drv) {
	if (!drv || !drv->channel) return 0;
	uint16_t remaining = (uint16_t)drv->channel->NDTR;
	if (remaining > drv->buffer_size) return 0;
	return (drv->buffer_size - remaining);
}

/* Обробник апаратного переривання каналу DMA */
void dma_ring_irq_handler(dma_ring_driver_t *drv) {
	if (!drv || !drv->channel || !drv->controller) return;

	uint32_t flag_shift = (drv->channel_number - 1U) * 4U;
	uint32_t isr_status = drv->controller->ISR;

	/* Перевірка помилки передачі на шині */
	if (isr_status & (1U << (flag_shift + DMA_FLAG_TEIF_POS))) {
		drv->controller->IFCR = (1U << (flag_shift + DMA_FLAG_TEIF_POS));
		DMA_BARRIER_SYNC();
		if (drv->on_error) {
			drv->on_error(drv->user_context);
		}
	}

	/* Перевірка заповнення першої половини кільцевого буфера */
	if (isr_status & (1U << (flag_shift + DMA_FLAG_HTIF_POS))) {
		drv->controller->IFCR = (1U << (flag_shift + DMA_FLAG_HTIF_POS));
		DMA_BARRIER_SYNC();
		if (drv->on_half_complete) {
			drv->on_half_complete(drv->user_context);
		}
	}

	/* Перевірка заповнення другої половини кільцевого буфера */
	if (isr_status & (1U << (flag_shift + DMA_FLAG_TCIF_POS))) {
		drv->controller->IFCR = (1U << (flag_shift + DMA_FLAG_TCIF_POS));
		DMA_BARRIER_SYNC();
		if (drv->on_full_complete) {
			drv->on_full_complete(drv->user_context);
		}
	}
}
