#include "bus.h"

#include <stdio.h>
#include <string.h>

/* Фізична пам'ять та стан периферійного заліза. */
static uint8_t g_memory[MEMORY_SIZE];
static uint8_t g_gpio_out_latch;
static uint8_t g_gpio_in_pins;

static unsigned long g_cycles;
static unsigned      g_bus_errors;
static unsigned      g_button_polls;
static unsigned      g_button_press_after = BUTTON_NEVER;
static bool          g_trace = true;

void bus_init(void)
{
    memset(g_memory, 0, sizeof g_memory);
    g_gpio_out_latch = 0x00;
    g_gpio_in_pins   = 0x01;   /* кнопка відпущена: підтяжка тримає одиницю */
    g_cycles         = 0;
    g_bus_errors     = 0;
    g_button_polls   = 0;
}

bool bus_load_rom(const uint8_t *image, size_t length)
{
    if (image == NULL || length > ROM_LIMIT) {
        fprintf(stderr, "[LOAD] Образ на %zu байтів не влазить у ROM (%u байтів)\n",
                length, (unsigned)ROM_LIMIT);
        return false;
    }
    memcpy(g_memory, image, length);
    return true;
}

BusRegion bus_decode(uint16_t addr, uint16_t *offset)
{
    if (addr < ROM_LIMIT) {
        if (offset) *offset = addr;
        return REGION_ROM;
    }
    if (addr < RAM_LIMIT) {
        if (offset) *offset = (uint16_t)(addr - RAM_BASE);
        return REGION_RAM;
    }
    if (addr < MMIO_LIMIT) {
        /* Неповна дешифрація: кристал периферії вибирається старшими бітами,
           а всередині розібрано лише A0. Тому регістрів рівно два, і вони
           повторюються по всій області 0x8000–0xBFFF. */
        if (offset) *offset = (uint16_t)(addr & 0x0001u);
        return REGION_MMIO;
    }
    if (offset) *offset = 0;
    return REGION_NONE;
}

/* Читання регістра периферії. Порт вводу — єдине місце, де читання має
   побічну дію: кожне опитування наближає момент натискання кнопки. */
static uint8_t mmio_read(uint16_t addr, uint16_t reg)
{
    if (reg == 0) {
        /* Зворотне читання засувки виводу: реальний порт віддає те, що
           було записано, а не напругу на ніжці. */
        if (g_trace) {
            printf("  [BUS RD] MMIO 0x%04X (GPIO_OUT, зворотне читання) = 0x%02X\n",
                   addr, g_gpio_out_latch);
        }
        return g_gpio_out_latch;
    }

    ++g_button_polls;
    if (g_button_polls > g_button_press_after) {
        g_gpio_in_pins &= (uint8_t)~0x01u;   /* кнопку натиснуто: ніжка на землі */
    }
    if (g_trace) {
        printf("  [BUS RD] MMIO 0x%04X (GPIO_IN, опитування %u) = 0x%02X -> кнопка %s\n",
               addr, g_button_polls, g_gpio_in_pins,
               (g_gpio_in_pins & 0x01u) ? "відпущена" : "НАТИСНУТА");
    }
    return g_gpio_in_pins;
}

static void mmio_write(uint16_t addr, uint16_t reg, uint8_t data)
{
    if (reg == 0) {
        g_gpio_out_latch = data;
        if (g_trace) {
            printf("  [BUS WR] MMIO 0x%04X (GPIO_OUT) = 0x%02X -> Світлодіод: %s\n",
                   addr, data, (data & 0x01u) ? "УВІМКНЕНО (3.3 В)" : "ВИМКНЕНО (0 В)");
        }
        return;
    }

    /* Порт вводу — це буфер із трьома станами, повернутий до ядра.
       Запис у нього нікуди не потрапляє: записувати нема куди. */
    ++g_bus_errors;
    if (g_trace) {
        printf("  [BUS ERROR] Запис 0x%02X у GPIO_IN 0x%04X: регістр лише для читання\n",
               data, addr);
    }
}

/* Фантомні копії регістра: адреса потрапила в кристал периферії, але
   всередині кристала розібрано лише A0, тож 0x8003 — це той самий 0x8001. */
static void warn_alias(uint16_t addr, uint16_t reg)
{
    uint16_t canonical = (uint16_t)(MMIO_BASE | reg);
    if (addr != canonical && g_trace) {
        printf("  [ALIAS] 0x%04X — фантомна копія 0x%04X (дешифровано лише A0)\n",
               addr, canonical);
    }
}

uint8_t bus_read(uint16_t addr)
{
    uint16_t offset = 0;

    ++g_cycles;
    switch (bus_decode(addr, &offset)) {
        case REGION_ROM:
        case REGION_RAM:
            return g_memory[addr];

        case REGION_MMIO:
            warn_alias(addr, offset);
            return mmio_read(addr, offset);

        case REGION_NONE:
        default:
            /* Жоден /CS не активний: на шині лишається підтяжка. */
            if (g_trace) {
                printf("  [BUS RD] 0x%04X — кристала немає, шина віддає 0x%02X (open bus)\n",
                       addr, OPEN_BUS);
            }
            return OPEN_BUS;
    }
}

void bus_write(uint16_t addr, uint8_t data)
{
    uint16_t offset = 0;

    ++g_cycles;

    /* Найперша дія дешифратора запису. Область 0x0000–0x3FFF — кристал ROM,
       і лінія /WR до нього фізично не підведена: запис не має куди дійти. */
    if (addr < 0x4000) {
        ++g_bus_errors;
        if (g_trace) {
            printf("  [BUS ERROR] Спроба запису 0x%02X у ROM за адресою 0x%04X — цикл проігноровано\n",
                   data, addr);
        }
        return;
    }

    switch (bus_decode(addr, &offset)) {
        case REGION_RAM:
            g_memory[addr] = data;
            if (g_trace) {
                printf("  [BUS WR] SRAM 0x%04X = 0x%02X\n", addr, data);
            }
            break;

        case REGION_MMIO:
            warn_alias(addr, offset);
            mmio_write(addr, offset, data);
            break;

        case REGION_NONE:
            ++g_bus_errors;
            if (g_trace) {
                printf("  [BUS ERROR] Запис 0x%02X за адресою 0x%04X: кристала немає\n",
                       data, addr);
            }
            break;

        case REGION_ROM:
        default:
            break;   /* оброблено вище */
    }
}

uint8_t bus_peek(uint16_t addr)
{
    uint16_t offset = 0;

    switch (bus_decode(addr, &offset)) {
        case REGION_ROM:
        case REGION_RAM:
            return g_memory[addr];
        case REGION_MMIO:
            return (offset == 0) ? g_gpio_out_latch : g_gpio_in_pins;
        case REGION_NONE:
        default:
            return OPEN_BUS;
    }
}

void bus_set_button_press_after(unsigned polls)
{
    g_button_press_after = polls;
    g_button_polls       = 0;
    g_gpio_in_pins      |= 0x01u;   /* кнопку відпустили */
}

void bus_set_trace(bool on)
{
    g_trace = on;
}

unsigned long bus_cycles(void)
{
    return g_cycles;
}

unsigned bus_error_count(void)
{
    return g_bus_errors;
}

uint8_t bus_gpio_out_latch(void)
{
    return g_gpio_out_latch;
}
