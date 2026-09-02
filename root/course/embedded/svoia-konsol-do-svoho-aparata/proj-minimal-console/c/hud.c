#include "hud.h"

#include <string.h>

#include "hal.h"
#include "sticks.h"

#define GLYPH_W  5
#define CELL_W   6
#define LINE_MAX 24

// Шрифт 5×8: кожен байт — вертикальний стовпчик пікселів, молодший біт зверху.
// Гліфи лише під ті символи, що трапляються в написах пульта, — кирилиці в
// такому шрифті немає, тому підписи латиницею.
static const char s_charset[] = " -.%0123456789ABCDEFGHIKLMNOPQRSTUVY";

static const uint8_t s_font[][GLYPH_W] = {
    {0x00, 0x00, 0x00, 0x00, 0x00},   // пробіл
    {0x08, 0x08, 0x08, 0x08, 0x08},   // -
    {0x00, 0x60, 0x60, 0x00, 0x00},   // .
    {0x23, 0x13, 0x08, 0x64, 0x62},   // %
    {0x3E, 0x51, 0x49, 0x45, 0x3E},   // 0
    {0x00, 0x42, 0x7F, 0x40, 0x00},   // 1
    {0x42, 0x61, 0x51, 0x49, 0x46},   // 2
    {0x21, 0x41, 0x45, 0x4B, 0x31},   // 3
    {0x18, 0x14, 0x12, 0x7F, 0x10},   // 4
    {0x27, 0x45, 0x45, 0x45, 0x39},   // 5
    {0x3C, 0x4A, 0x49, 0x49, 0x30},   // 6
    {0x01, 0x71, 0x09, 0x05, 0x03},   // 7
    {0x36, 0x49, 0x49, 0x49, 0x36},   // 8
    {0x06, 0x49, 0x49, 0x29, 0x1E},   // 9
    {0x7E, 0x11, 0x11, 0x11, 0x7E},   // A
    {0x7F, 0x49, 0x49, 0x49, 0x36},   // B
    {0x3E, 0x41, 0x41, 0x41, 0x22},   // C
    {0x7F, 0x41, 0x41, 0x22, 0x1C},   // D
    {0x7F, 0x49, 0x49, 0x49, 0x41},   // E
    {0x7F, 0x09, 0x09, 0x09, 0x01},   // F
    {0x3E, 0x41, 0x49, 0x49, 0x7A},   // G
    {0x7F, 0x08, 0x08, 0x08, 0x7F},   // H
    {0x00, 0x41, 0x7F, 0x41, 0x00},   // I
    {0x7F, 0x08, 0x14, 0x22, 0x41},   // K
    {0x7F, 0x40, 0x40, 0x40, 0x40},   // L
    {0x7F, 0x02, 0x0C, 0x02, 0x7F},   // M
    {0x7F, 0x04, 0x08, 0x10, 0x7F},   // N
    {0x3E, 0x41, 0x41, 0x41, 0x3E},   // O
    {0x7F, 0x09, 0x09, 0x09, 0x06},   // P
    {0x3E, 0x41, 0x51, 0x21, 0x5E},   // Q
    {0x7F, 0x09, 0x19, 0x29, 0x46},   // R
    {0x46, 0x49, 0x49, 0x49, 0x31},   // S
    {0x01, 0x01, 0x7F, 0x01, 0x01},   // T
    {0x3F, 0x40, 0x40, 0x40, 0x3F},   // U
    {0x1F, 0x20, 0x40, 0x20, 0x1F},   // V
    {0x07, 0x08, 0x70, 0x08, 0x07},   // Y
};

// Сторінка їде в дисплей теж через DMA, тож буфер статичний і вирівняний.
static HAL_DMA_ATTR uint8_t s_cols[HAL_LCD_COLS];
static hud_state_t s_state;

static const uint8_t *glyph(char c)
{
    for (uint8_t i = 0; s_charset[i] != '\0'; i++) {
        if (s_charset[i] == c) {
            return s_font[i];
        }
    }
    return s_font[0];
}

static size_t put_ch(char *dst, size_t pos, char c)
{
    if (pos + 1 < LINE_MAX) {
        dst[pos++] = c;
    }
    return pos;
}

static size_t put_str(char *dst, size_t pos, const char *src)
{
    while (*src) {
        pos = put_ch(dst, pos, *src++);
    }
    return pos;
}

static size_t put_num(char *dst, size_t pos, uint32_t value, uint8_t min_digits)
{
    char tmp[10];
    uint8_t n = 0;
    do {
        tmp[n++] = (char)('0' + (value % 10u));
        value /= 10u;
    } while (value != 0 && n < sizeof tmp);
    while (n < min_digits && n < sizeof tmp) {
        tmp[n++] = '0';
    }
    while (n > 0) {
        pos = put_ch(dst, pos, tmp[--n]);
    }
    return pos;
}

// Друкує мілівольти як «11.42»: ділити на 1000 у цілих дешевше за float,
// якого в цьому циклі не має бути взагалі.
static size_t put_volts(char *dst, size_t pos, uint16_t mv)
{
    pos = put_num(dst, pos, mv / 1000u, 1);
    pos = put_ch(dst, pos, '.');
    return put_num(dst, pos, (mv % 1000u) / 10u, 2);
}

static void build_line(uint8_t page, char *line)
{
    size_t p = 0;
    line[0] = '\0';

    switch (page) {
    case 0:
        p = put_str(line, p, "BAT ");
        p = put_volts(line, p, s_state.pack_mv);
        p = put_str(line, p, "V ");
        p = put_str(line, p, s_state.batt_level == BATT_CRITICAL ? "KRYT"
                           : (s_state.batt_level == BATT_LOW ? "MALO" : "OK"));
        break;
    case 1:
        p = put_str(line, p, "LQ ");
        p = put_num(line, p, s_state.link_pct, 3);
        p = put_str(line, p, "% RSSI -");
        p = put_num(line, p, (uint32_t)(-(int)s_state.air.rssi_air_dbm), 3);
        break;
    case 2:
        p = put_str(line, p, "APARAT ");
        p = put_volts(line, p, s_state.air.vbat_mv);
        p = put_ch(line, p, 'V');
        break;
    case 3:
        p = put_str(line, p, "STRUM ");
        p = put_num(line, p, s_state.air.current_da / 10u, 1);
        p = put_ch(line, p, '.');
        p = put_num(line, p, s_state.air.current_da % 10u, 1);
        p = put_ch(line, p, 'A');
        break;
    case 4:
        p = put_str(line, p, "MOS ");
        p = put_num(line, p, s_state.air.mos_temp_c, 2);
        p = put_str(line, p, "C SAT ");
        p = put_num(line, p, s_state.air.sats, 2);
        break;
    case 6:
        p = put_str(line, p, "MOD ");
        p = put_num(line, p, s_state.air.flight_mode, 2);
        p = put_str(line, p, s_state.armed ? " ARM" : " SAFE");
        break;
    case 7:
        // Найважливіший рядок: чому передачі немає. Він же й найнижчий,
        // бо саме туди падає погляд, коли апарат не реагує.
        if (s_state.safety_faults & SAFETY_AXIS_DEAD) {
            p = put_str(line, p, "BLOK DATCHYK");
        } else if (s_state.safety_faults & SAFETY_THROTTLE_UP) {
            p = put_str(line, p, "BLOK TAHA");
        } else if (s_state.safety_faults & SAFETY_ARM_ON) {
            p = put_str(line, p, "BLOK ARM");
        } else {
            p = put_str(line, p, "VTRATY ");
            p = put_num(line, p, s_state.lost_frames, 4);
        }
        break;
    default:
        break;
    }
    line[p] = '\0';
}

static void render_text(const char *text)
{
    memset(s_cols, 0, sizeof s_cols);
    size_t x = 0;
    for (const char *c = text; *c != '\0' && x + CELL_W <= HAL_LCD_COLS; c++) {
        const uint8_t *g = glyph(*c);
        for (uint8_t i = 0; i < GLYPH_W; i++) {
            s_cols[x + i] = g[i];
        }
        x += CELL_W;
    }
}

static void render_bar(uint8_t pct)
{
    memset(s_cols, 0, sizeof s_cols);
    size_t fill = ((size_t)pct * (HAL_LCD_COLS - 2u)) / 100u;
    s_cols[0] = 0x7E;
    s_cols[HAL_LCD_COLS - 1] = 0x7E;
    for (size_t x = 1; x < HAL_LCD_COLS - 1; x++) {
        s_cols[x] = (x <= fill) ? 0x7E : 0x42;   // залито або сама рамка
    }
}

void hud_set_state(const hud_state_t *state)
{
    s_state = *state;
}

void hud_service(void)
{
    static uint8_t page;

    if (page == 5) {
        render_bar(s_state.link_pct);
    } else {
        char line[LINE_MAX];
        build_line(page, line);
        render_text(line);
    }

    // Дисплей висить на тій самій шині SPI, що й трансивер: сюди ми
    // потрапляємо лише тоді, коли радіо шину не тримає.
    hal_cache_writeback(s_cols, sizeof s_cols);
    hal_display_page(page, s_cols, sizeof s_cols);
    page = (uint8_t)((page + 1u) & 7u);
}
