#include <stdint.h>
#include <stdbool.h>

// Команди керування дисплеєм за специфікацією MIPI DCS
#define CMD_VSCRDEF  0x33
#define CMD_VSCRSADD 0x37
#define CMD_RAMWR    0x2C

// Структура конфігурації апаратного скролера
typedef struct {
    uint16_t tfa;          // Висота верхньої фіксованої зони (TFA)
    uint16_t vsa;          // Висота зони вертикального скролінгу (VSA)
    uint16_t bfa;          // Висота нижньої фіксованої зони (BFA)
    uint16_t display_width;// Ширина дисплея в пікселях
    uint16_t current_vsp;  // Поточний зсув (Vertical Scroll Pointer)
} display_scroller_t;

// Зовнішні шинні функції низького рівня
extern void display_write_cmd(uint8_t cmd);
extern void display_write_data(const uint8_t *data, uint32_t length);
extern void display_set_address_window(uint16_t x0, uint16_t y0, uint16_t x1, uint16_t y1);

/**
 * @brief Ініціалізація апаратних зон вертикального скролінгу дисплея.
 */
void display_scroller_init(display_scroller_t *scroller, uint16_t tfa, uint16_t vsa, uint16_t bfa, uint16_t width) {
    scroller->tfa = tfa;
    scroller->vsa = vsa;
    scroller->bfa = bfa;
    scroller->display_width = width;
    scroller->current_vsp = tfa; // Початковий зсув вказує на початок зони VSA

    uint8_t params[6];
    params[0] = (uint8_t)(tfa >> 8);
    params[1] = (uint8_t)(tfa & 0xFF);
    params[2] = (uint8_t)(vsa >> 8);
    params[3] = (uint8_t)(vsa & 0xFF);
    params[4] = (uint8_t)(bfa >> 8);
    params[5] = (uint8_t)(bfa & 0xFF);

    display_write_cmd(CMD_VSCRDEF);
    display_write_data(params, 6);
}

/**
 * @brief Виконання крок прокрутки на dy пікселів вгору з записом нового рядка пікселів.
 * @param scroller Вказівник на структуру скролера
 * @param dy Кількість пікселів для зсуву
 * @param new_line_pixels Буфер із новими пікселями для запису у вивільнений рядок
 */
void display_scroller_scroll_up(display_scroller_t *scroller, uint16_t dy, const uint16_t *new_line_pixels) {
    for (uint16_t step = 0; step < dy; step++) {
        // Обчислення фізичного рядка в GRAM, куди буде записано новий рядок даних
        uint16_t write_gram_y = scroller->current_vsp;

        // Встановлення вікна запису в GRAM суворо для одного фізичного рядка
        display_set_address_window(0, write_gram_y, scroller->display_width - 1, write_gram_y);

        // Відправка нових пікселів у GRAM через командний інтерфейс або DMA
        display_write_cmd(CMD_RAMWR);
        display_write_data((const uint8_t *)new_line_pixels, scroller->display_width * sizeof(uint16_t));

        // Зсув вказівника прокрутки з кільцевим обгортанням у межах зони VSA
        scroller->current_vsp++;
        if (scroller->current_vsp >= (scroller->tfa + scroller->vsa)) {
            scroller->current_vsp = scroller->tfa;
        }
    }

    // Апаратне оновлення регістру зсуву в чипі дисплея
    uint8_t vsp_bytes[2];
    vsp_bytes[0] = (uint8_t)(scroller->current_vsp >> 8);
    vsp_bytes[1] = (uint8_t)(scroller->current_vsp & 0xFF);

    display_write_cmd(CMD_VSCRSADD);
    display_write_data(vsp_bytes, 2);
}
