#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

/* Роздільник кадру COBS */
#define COBS_FRAME_DELIMITER 0x00

/* Кодування буфера даних за алгоритмом COBS */
size_t cobs_encode(const uint8_t *src, size_t src_len, uint8_t *dst) {
	size_t read_idx = 0;
	size_t write_idx = 1;
	size_t code_idx = 0;
	uint8_t code = 1;

	while (read_idx < src_len) {
		if (src[read_idx] == 0) {
			dst[code_idx] = code;
			code_idx = write_idx++;
			code = 1;
		} else {
			dst[write_idx++] = src[read_idx];
			code++;
			if (code == 0xFF) {
				dst[code_idx] = code;
				code_idx = write_idx++;
				code = 1;
			}
		}
		read_idx++;
	}

	dst[code_idx] = code;
	dst[write_idx++] = COBS_FRAME_DELIMITER;
	return write_idx;
}

/* Структура збереження регістрів ядра при аварійному виході HardFault */
typedef struct {
	uint32_t r0;
	uint32_t r1;
	uint32_t r2;
	uint32_t r3;
	uint32_t r12;
	uint32_t lr;
	uint32_t pc;
	uint32_t psr;
	uint32_t cfsr;
	uint32_t hfsr;
	uint32_t magic;
} __attribute__((packed)) crash_dump_t;

#define CRASH_DUMP_MAGIC 0xDEADBEEF

/* Розміщення у неініціалізованій секції пам'яті SRAM */
__attribute__((section(".noinit"))) static crash_dump_t g_crash_dump;

/* Аварійний синхронний вивід логу безпосередньо в регістр UART */
void panic_emergency_poll_flush(uint16_t event_id, const uint32_t *stack_frame) {
	volatile uint32_t *uart_dr = (volatile uint32_t *)0x40013804;
	volatile uint32_t *uart_sr = (volatile uint32_t *)0x40013800;

	/* Фіксація стану процесора у збереженій структурі */
	g_crash_dump.r0   = stack_frame[0];
	g_crash_dump.r1   = stack_frame[1];
	g_crash_dump.r2   = stack_frame[2];
	g_crash_dump.r3   = stack_frame[3];
	g_crash_dump.r12  = stack_frame[4];
	g_crash_dump.lr   = stack_frame[5];
	g_crash_dump.pc   = stack_frame[6];
	g_crash_dump.psr  = stack_frame[7];
	g_crash_dump.cfsr = (*(volatile uint32_t *)0xE000ED28);
	g_crash_dump.hfsr = (*(volatile uint32_t *)0xE000ED2C);
	g_crash_dump.magic = CRASH_DUMP_MAGIC;

	/* Побайтова синхронна передача ідентифікатора події */
	uint8_t packet[2] = { (uint8_t)(event_id & 0xFF), (uint8_t)(event_id >> 8) };
	for (size_t i = 0; i < sizeof(packet); ++i) {
		while (!(*uart_sr & (1UL << 7))); /* Очікування готовності TXE */
		*uart_dr = packet[i];
	}
}
