#include <stdint.h>
#include <stdbool.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/semphr.h"
#include "driver/gpio.h"
#include "driver/spi_master.h"
#include "esp_cache.h"

#define CMD_CASET    0x2A
#define CMD_RASET    0x2B
#define CMD_RAMWR    0x2C
#define CMD_VSCRDEF  0x33
#define CMD_VSCRSADD 0x37

#define DISPLAY_WIDTH  240
#define DISPLAY_HEIGHT 320
#define CACHE_LINE_SZ  32

// Структура конфігурації та стану асинхронного апаратного скролера
typedef struct {
	uint16_t tfa;                       // Висота верхньої фіксованої зони
	uint16_t vsa;                       // Висота рухомої зони
	uint16_t bfa;                       // Висота нижньої фіксованої зони
	uint16_t vsp;                       // Поточний фізичний покажчик зсуву
	spi_device_handle_t spi_dev;        // Дескриптор пристрою шини SPI
	gpio_num_t te_pin;                  // Номер виводу апаратного переривання TE
	SemaphoreHandle_t te_semaphore;     // Семафор синхронізації з гасінням TE
	SemaphoreHandle_t dma_semaphore;    // Семафор вивільнення каналу DMA
	uint8_t active_buf_idx;             // Поточний індекс буфера для малювання
	uint16_t *line_buffers[2];          // Вказівники на човникові буфери пікселів
} async_scroller_t;

// Човникові буфери в SRAM, вирівняні за межею лінії процесорного кешу
static uint16_t s_ping_buffer[DISPLAY_WIDTH] __attribute__((aligned(CACHE_LINE_SZ)));
static uint16_t s_pong_buffer[DISPLAY_WIDTH] __attribute__((aligned(CACHE_LINE_SZ)));

// Обробник апаратного переривання від сигнальної лінії TE
static void IRAM_ATTR scroller_te_isr_handler(void *arg) {
	async_scroller_t *scroller = (async_scroller_t *)arg;
	BaseType_t high_task_awoken = pdFALSE;
	xSemaphoreGiveFromISR(scroller->te_semaphore, &high_task_awoken);
	portYIELD_FROM_ISR(high_task_awoken);
}

// Зворотний виклик після завершення передачі блоку контролером DMA
static void IRAM_ATTR scroller_dma_post_callback(spi_transaction_t *trans) {
	async_scroller_t *scroller = (async_scroller_t *)trans->user;
	BaseType_t high_task_awoken = pdFALSE;
	xSemaphoreGiveFromISR(scroller->dma_semaphore, &high_task_awoken);
	portYIELD_FROM_ISR(high_task_awoken);
}

// Швидке надсилання байта команди через SPI
static void display_send_cmd_byte(spi_device_handle_t spi, uint8_t cmd) {
	spi_transaction_t trans = {
		.flags = SPI_TRANS_USE_TXDATA,
		.length = 8,
		.tx_data[0] = cmd
	};
	spi_device_polling_transmit(spi, &trans);
}

// Запис значення покажчика початкового рядка у контролер
static void display_write_vsp(spi_device_handle_t spi, uint16_t vsp) {
	uint8_t addr_bytes[2] = { (uint8_t)(vsp >> 8), (uint8_t)(vsp & 0xFF) };
	display_send_cmd_byte(spi, CMD_VSCRSADD);
	spi_transaction_t trans = {
		.length = 16,
		.tx_buffer = addr_bytes
	};
	spi_device_polling_transmit(spi, &trans);
}

// Налаштування прямокутного вікна запису для одного рядка пам'яті
static void display_set_row_window(spi_device_handle_t spi, uint16_t row) {
	uint8_t col_box[4] = { 0, 0, (uint8_t)((DISPLAY_WIDTH - 1) >> 8), (uint8_t)((DISPLAY_WIDTH - 1) & 0xFF) };
	uint8_t row_box[4] = { (uint8_t)(row >> 8), (uint8_t)(row & 0xFF), (uint8_t)(row >> 8), (uint8_t)(row & 0xFF) };

	display_send_cmd_byte(spi, CMD_CASET);
	spi_transaction_t col_trans = { .length = 32, .tx_buffer = col_box };
	spi_device_polling_transmit(spi, &col_trans);

	display_send_cmd_byte(spi, CMD_RASET);
	spi_transaction_t row_trans = { .length = 32, .tx_buffer = row_box };
	spi_device_polling_transmit(spi, &row_trans);
}

// Ініціалізація структури скролера та конфігурація апаратури
void async_scroller_init(async_scroller_t *scroller, spi_device_handle_t spi, gpio_num_t te_pin,
                         uint16_t tfa, uint16_t vsa, uint16_t bfa) {
	scroller->spi_dev = spi;
	scroller->te_pin = te_pin;
	scroller->tfa = tfa;
	scroller->vsa = vsa;
	scroller->bfa = bfa;
	scroller->vsp = tfa;
	scroller->active_buf_idx = 0;
	scroller->line_buffers[0] = s_ping_buffer;
	scroller->line_buffers[1] = s_pong_buffer;

	scroller->te_semaphore = xSemaphoreCreateBinary();
	scroller->dma_semaphore = xSemaphoreCreateBinary();
	xSemaphoreGive(scroller->dma_semaphore);

	// Передача параметрів сегментації зони скролінгу
	uint8_t def_bytes[6] = {
		(uint8_t)(tfa >> 8), (uint8_t)(tfa & 0xFF),
		(uint8_t)(vsa >> 8), (uint8_t)(vsa & 0xFF),
		(uint8_t)(bfa >> 8), (uint8_t)(bfa & 0xFF)
	};
	display_send_cmd_byte(spi, CMD_VSCRDEF);
	spi_transaction_t def_trans = { .length = 48, .tx_buffer = def_bytes };
	spi_device_polling_transmit(spi, &def_trans);

	display_write_vsp(spi, scroller->vsp);

	// Налаштування виводу переривання від лінії TE
	gpio_config_t io_conf = {
		.pin_bit_mask = (1ULL << te_pin),
		.mode = GPIO_MODE_INPUT,
		.pull_up_en = GPIO_PULLUP_ENABLE,
		.intr_type = GPIO_INTR_POSEDGE
	};
	gpio_config(&io_conf);
	gpio_isr_handler_add(te_pin, scroller_te_isr_handler, scroller);
}

// Отримання адреси буфера для малювання наступного рядка
uint16_t* async_scroller_get_render_buffer(async_scroller_t *scroller) {
	return scroller->line_buffers[scroller->active_buf_idx];
}

// Виконання кроку апаратного зсуву з фоновим виштовхуванням пікселів
void async_scroller_step(async_scroller_t *scroller) {
	// 1. Очікування настання вертикальної гасільної паузи кадру
	xSemaphoreTake(scroller->te_semaphore, portMAX_DELAY);

	// Фізична адреса вивільненого рядка пам'яті для нового запису
	uint16_t target_row = scroller->vsp;

	// Циклічний інкремент покажчика розгортки в межах рухомої зони VSA
	scroller->vsp++;
	if (scroller->vsp >= (scroller->tfa + scroller->vsa)) {
		scroller->vsp = scroller->tfa;
	}
	display_write_vsp(scroller->spi_dev, scroller->vsp);

	// 2. Очікування завершення попередньої фонової транзакції DMA
	xSemaphoreTake(scroller->dma_semaphore, portMAX_DELAY);

	// Налаштування вікна адресації для цільового рядка
	display_set_row_window(scroller->spi_dev, target_row);
	display_send_cmd_byte(scroller->spi_dev, CMD_RAMWR);

	// Очищення ліній кешу даних перед запуском контролера DMA
	uint16_t *buf_to_send = scroller->line_buffers[scroller->active_buf_idx];
	esp_cache_msync(buf_to_send, DISPLAY_WIDTH * sizeof(uint16_t), ESP_CACHE_MSYNC_FLAG_DIR_C2M);

	// 3. Запуск неблокувального перекачування масиву пікселів через DMA
	spi_transaction_t dma_trans = {
		.length = DISPLAY_WIDTH * 16,
		.tx_buffer = buf_to_send,
		.user = scroller
	};
	spi_device_queue_trans(scroller->spi_dev, &dma_trans, portMAX_DELAY);

	// Перемикання човникових буферів для підготовки наступного рядка
	scroller->active_buf_idx = 1 - scroller->active_buf_idx;
}
