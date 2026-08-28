#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

// ── Нижній шар: залежить від конкретного МК. Перепишіть під своє залізо. ──
// Ідентифікатори ніг — просто числа-псевдоніми; зіставте їх зі своїми пінами.
enum {
    PIN_NCONFIG,   // вихід: скидання конфігурації (активний 0). Xilinx: PROGRAM_B
    PIN_DCLK,      // вихід: такт конфігурації.                    Xilinx: CCLK
    PIN_DATA0,     // вихід: лінія даних, один біт за такт.        Xilinx: DIN
    PIN_NSTATUS,   // вхід : стан чипа (open-drain, активний 0).   Xilinx: INIT_B
    PIN_CONF_DONE  // вхід : готовність (open-drain, 1 = готово).  Xilinx: DONE
};

// Виставити вихідну ногу в 0 або 1.
static void gpio_write(int pin, int level);
// Прочитати вхідну ногу: повертає 0 або 1.
static int  gpio_read(int pin);
// Затримка приблизно на задану кількість мікросекунд.
static void delay_us(uint32_t us);
// Джерело бітстріму: заповнити buf до len байтів, повернути СКІЛЬКИ реально
// прочитано (0 — бітстрім скінчився). Може читати з SPI-флеш, SD, масиву…
static size_t bitstream_read(uint8_t *buf, size_t len);
