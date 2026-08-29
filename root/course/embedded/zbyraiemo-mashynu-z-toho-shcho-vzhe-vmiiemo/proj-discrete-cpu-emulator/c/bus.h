/* bus.h — системна шина, адресний дешифратор і периферія.
 *
 * Модуль тримає весь «зовнішній світ» ядра: масив фізичної пам'яті,
 * засувку порту виводу та стан ніжок порту вводу. Ядро (cpu.c) не знає
 * про пам'ять нічого — воно вміє лише виставити адресу й смикнути /RD або /WR.
 */
#ifndef BUS_H
#define BUS_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#define MEMORY_SIZE 65536

/* Карта адрес. Дешифратор розбирає старші біти A[15:14]:
     00 -> ROM (кристал програм, /WR не підведено)
     01 -> SRAM
     10 -> MMIO (кристал периферії)
     11 -> нічого не підключено                                            */
#define ROM_BASE   0x0000u
#define ROM_LIMIT  0x4000u   /* перша адреса ПОЗА ROM */
#define RAM_BASE   0x4000u
#define RAM_LIMIT  0x8000u
#define MMIO_BASE  0x8000u
#define MMIO_LIMIT 0xC000u

#define MMIO_GPIO_OUT 0x8000u  /* біт 0 — світлодіод */
#define MMIO_GPIO_IN  0x8001u  /* біт 0 — кнопка з підтяжкою до живлення */

/* Що читає ядро, коли на адресу не відповів жоден кристал: шина даних
   лишається підтягнутою до логічної одиниці. */
#define OPEN_BUS 0xFFu

/* Кнопку не натискають ніколи. */
#define BUTTON_NEVER 0xFFFFFFFFu

typedef enum {
    REGION_ROM,
    REGION_RAM,
    REGION_MMIO,
    REGION_NONE
} BusRegion;

/* Скидання всієї периферії у стан після подачі живлення. */
void bus_init(void);

/* Заливка прошивки в область ROM. Повертає false, якщо образ не влазить
   у кристал програм — далі запускати нема сенсу. */
bool bus_load_rom(const uint8_t *image, size_t length);

/* Чистий адресний дешифратор: за адресою каже, який кристал вибрано,
   і повертає зміщення (для MMIO — номер регістра всередині кристала).
   Побічних дій не має, тому годиться і для налагодження. */
BusRegion bus_decode(uint16_t addr, uint16_t *offset);

/* Один шинний цикл читання і один запису. Саме ці дві функції моделюють
   лінії /RD і /WR разом із логікою вибору кристала. */
uint8_t bus_read(uint16_t addr);
void    bus_write(uint16_t addr, uint8_t data);

/* Погляд у пам'ять збоку — для трасування й підсумків. Лічильника циклів
   не крутить і кнопки не «натискає», тож нічого в моделі не змінює. */
uint8_t bus_peek(uint16_t addr);

/* Кнопку натискають після заданої кількості опитувань порту вводу:
   вхід перестає читати підтяжку й опускається в нуль. */
void bus_set_button_press_after(unsigned polls);

/* Чи друкувати кожен шинний цикл. */
void bus_set_trace(bool on);

unsigned long bus_cycles(void);
unsigned      bus_error_count(void);
uint8_t       bus_gpio_out_latch(void);

#endif /* BUS_H */
