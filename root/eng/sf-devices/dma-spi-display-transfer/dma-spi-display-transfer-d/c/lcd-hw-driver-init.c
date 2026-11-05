#include <stdint.h>
#include <stdbool.h>

/* Базові адреси регістрів периферійних модулів мікроконтролера */
#define SPI1_BASE_ADDR        (0x40013000UL)
#define DMA1_BASE_ADDR        (0x40020000UL)
#define GPIOA_BASE_ADDR       (0x40010800UL)

/* Зсуви регістрів керування периферією */
#define SPI_CR1_OFFSET        (0x00UL)
#define SPI_CR2_OFFSET        (0x04UL)
#define SPI_SR_OFFSET         (0x08UL)
#define SPI_DR_OFFSET         (0x0CUL)

#define DMA_CCR_OFFSET        (0x08UL)
#define DMA_CNDTR_OFFSET      (0x0CUL)
#define DMA_CPAR_OFFSET       (0x10UL)
#define DMA_CMAR_OFFSET       (0x14UL)

/* Бітові маски конфігурації та стану */
#define SPI_CR2_TXDMAEN       (1UL << 1)
#define SPI_SR_BSY            (1UL << 7)
#define SPI_SR_TXE            (1UL << 1)

#define DMA_CCR_EN            (1UL << 0)
#define DMA_CCR_TCIE          (1UL << 1)
#define DMA_CCR_DIR_M2P       (1UL << 4)
#define DMA_CCR_MINC          (1UL << 7)
#define DMA_CCR_PSIZE_16      (1UL << 8)
#define DMA_CCR_MSIZE_16      (1UL << 10)
#define DMA_CCR_PL_VHIGH      (3UL << 12)

#define GPIO_BSRR_SET(pin)    (1UL << (pin))
#define GPIO_BSRR_RESET(pin)  (1UL << ((pin) + 16))

#define LCD_DC_PIN            (4U)
#define LCD_CS_PIN            (5U)

/* Тип дескриптора задачі операційної системи реального часу */
typedef void *rtos_task_handle_t;

typedef struct {
	volatile uint32_t *spi_sr;
	volatile uint32_t *spi_dr;
	volatile uint32_t *spi_cr2;
	volatile uint32_t *dma_ccr;
	volatile uint32_t *dma_cndtr;
	volatile uint32_t *dma_cpar;
	volatile uint32_t *dma_cmar;
	volatile uint32_t *gpio_bsrr;
	rtos_task_handle_t client_task_handle;
	volatile bool is_transfer_active;
} dma_spi_lcd_driver_t;

static dma_spi_lcd_driver_t g_lcd_drv;

/* Зовнішні прототипи функцій операційної системи реального часу */
extern void rtos_task_notify_give_from_isr(rtos_task_handle_t task_handle);
extern void rtos_task_notify_take(void);

/* Ініціалізація покажчиків на регістри апаратних блоків */
void lcd_hw_driver_init(rtos_task_handle_t task_to_notify) {
	g_lcd_drv.spi_sr = (volatile uint32_t *)(SPI1_BASE_ADDR + SPI_SR_OFFSET);
	g_lcd_drv.spi_dr = (volatile uint32_t *)(SPI1_BASE_ADDR + SPI_DR_OFFSET);
	g_lcd_drv.spi_cr2 = (volatile uint32_t *)(SPI1_BASE_ADDR + SPI_CR2_OFFSET);

	/* Канал 3 контролера DMA прив'язаний до передавального буфера SPI1 */
	g_lcd_drv.dma_ccr = (volatile uint32_t *)(DMA1_BASE_ADDR + DMA_CCR_OFFSET);
	g_lcd_drv.dma_cndtr = (volatile uint32_t *)(DMA1_BASE_ADDR + DMA_CNDTR_OFFSET);
	g_lcd_drv.dma_cpar = (volatile uint32_t *)(DMA1_BASE_ADDR + DMA_CPAR_OFFSET);
	g_lcd_drv.dma_cmar = (volatile uint32_t *)(DMA1_BASE_ADDR + DMA_CMAR_OFFSET);

	g_lcd_drv.gpio_bsrr = (volatile uint32_t *)(GPIOA_BASE_ADDR + 0x10UL);
	g_lcd_drv.client_task_handle = task_to_notify;
	g_lcd_drv.is_transfer_active = false;

	/* Прив'язка адреси регістра периферії як адреси призначення DMA */
	*g_lcd_drv.dma_cpar = (uint32_t)g_lcd_drv.spi_dr;
}

/* Синхронне надсилання одного байта команди без залучення DMA */
static void lcd_send_cmd_byte(uint8_t cmd) {
	while (*g_lcd_drv.spi_sr & SPI_SR_BSY);

	/* Переведення лінії D/C у низький стан (Command Mode) */
	*g_lcd_drv.gpio_bsrr = GPIO_BSRR_RESET(LCD_DC_PIN);

	/* Активація сигналу вибору мікросхеми CS */
	*g_lcd_drv.gpio_bsrr = GPIO_BSRR_RESET(LCD_CS_PIN);

	/* Запис байта команди в регістр даних SPI */
	*g_lcd_drv.spi_dr = cmd;

	while (!(*g_lcd_drv.spi_sr & SPI_SR_TXE));
	while (*g_lcd_drv.spi_sr & SPI_SR_BSY);

	/* Повернення лінії D/C у високий стан (Data Mode) */
	*g_lcd_drv.gpio_bsrr = GPIO_BSRR_SET(LCD_DC_PIN);
}

/* Налаштування координат вікна виведення у пам'яті GRAM дисплея */
void lcd_set_display_window(uint16_t x0, uint16_t y0, uint16_t x1, uint16_t y1) {
	/* Встановлення меж стовпчиків: Column Address Set (код 0x2A) */
	lcd_send_cmd_byte(0x2A);
	*g_lcd_drv.spi_dr = (x0 >> 8);
	while (!(*g_lcd_drv.spi_sr & SPI_SR_TXE));
	*g_lcd_drv.spi_dr = (x0 & 0xFF);
	while (!(*g_lcd_drv.spi_sr & SPI_SR_TXE));
	*g_lcd_drv.spi_dr = (x1 >> 8);
	while (!(*g_lcd_drv.spi_sr & SPI_SR_TXE));
	*g_lcd_drv.spi_dr = (x1 & 0xFF);
	while (!(*g_lcd_drv.spi_sr & SPI_SR_TXE));
	while (*g_lcd_drv.spi_sr & SPI_SR_BSY);

	/* Встановлення меж рядків: Page Address Set (код 0x2B) */
	lcd_send_cmd_byte(0x2B);
	*g_lcd_drv.spi_dr = (y0 >> 8);
	while (!(*g_lcd_drv.spi_sr & SPI_SR_TXE));
	*g_lcd_drv.spi_dr = (y0 & 0xFF);
	while (!(*g_lcd_drv.spi_sr & SPI_SR_TXE));
	*g_lcd_drv.spi_dr = (y1 >> 8);
	while (!(*g_lcd_drv.spi_sr & SPI_SR_TXE));
	*g_lcd_drv.spi_dr = (y1 & 0xFF);
	while (!(*g_lcd_drv.spi_sr & SPI_SR_TXE));
	while (*g_lcd_drv.spi_sr & SPI_SR_BSY);

	/* Переведення дисплея в режим прийому пікселів: Memory Write (код 0x2C) */
	lcd_send_cmd_byte(0x2C);
}

/* Запуск асинхронного передавання піксельного буфера через DMA */
bool lcd_transmit_buffer_async(const uint16_t *pixels, uint32_t pixel_count) {
	if (g_lcd_drv.is_transfer_active || pixels == 0 || pixel_count == 0) {
		return false;
	}

	g_lcd_drv.is_transfer_active = true;

	/* Вимкнення каналу DMA перед перезаписом параметрів */
	*g_lcd_drv.dma_ccr &= ~DMA_CCR_EN;

	/* Встановлення фізичної адреси джерела в пам'яті SRAM */
	*g_lcd_drv.dma_cmar = (uint32_t)pixels;

	/* Запис кількості 16-бітних слів передачі */
	*g_lcd_drv.dma_cndtr = pixel_count;

	/* Налаштування напрямку пам'ять-периферія, інкременту джерела та 16-бітних даних */
	*g_lcd_drv.dma_ccr = DMA_CCR_DIR_M2P | DMA_CCR_MINC |
	                     DMA_CCR_PSIZE_16 | DMA_CCR_MSIZE_16 |
	                     DMA_CCR_PL_VHIGH | DMA_CCR_TCIE;

	/* Дозвіл генерації запитів DMA від модуля SPI */
	*g_lcd_drv.spi_cr2 |= SPI_CR2_TXDMAEN;

	/* Активація каналу DMA для початку передавання */
	*g_lcd_drv.dma_ccr |= DMA_CCR_EN;

	return true;
}

/* Обробник апаратного переривання каналу DMA */
void DMA1_Channel3_Handler(void) {
	volatile uint32_t *dma_isr = (volatile uint32_t *)(DMA1_BASE_ADDR + 0x00UL);
	volatile uint32_t *dma_ifcr = (volatile uint32_t *)(DMA1_BASE_ADDR + 0x04UL);

	/* Перевірка прапорця завершення передачі каналу 3 */
	if (*dma_isr & (1UL << 9)) {
		/* Скидання прапорця переривання в регістрі IFCR */
		*dma_ifcr = (1UL << 9);

		/* Вимкнення генерації запитів DMA від SPI */
		*g_lcd_drv.spi_cr2 &= ~SPI_CR2_TXDMAEN;

		/* Очікування висування останнього біта зі зсувного регістра SPI */
		while (*g_lcd_drv.spi_sr & SPI_SR_BSY);

		/* Деактивація вибору мікросхеми CS у високий стан */
		*g_lcd_drv.gpio_bsrr = GPIO_BSRR_SET(LCD_CS_PIN);

		g_lcd_drv.is_transfer_active = false;

		/* Миттєве розблокування задачі графічного інтерфейсу */
		if (g_lcd_drv.client_task_handle != 0) {
			rtos_task_notify_give_from_isr(g_lcd_drv.client_task_handle);
		}
	}
}
