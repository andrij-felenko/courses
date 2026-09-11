#define DISP_HOR_RES 240
#define DISP_VER_RES 240
#define BUFFER_ROWS  24 // 1/10 площі екрана

// Виділення пам'яті під два часткові буфери
static lv_color_t draw_buf_1[DISP_HOR_RES * BUFFER_ROWS];
static lv_color_t draw_buf_2[DISP_HOR_RES * BUFFER_ROWS];
static lv_disp_draw_buf_t disp_buf_desc;
static lv_disp_drv_t disp_drv;

// Переривання завершення DMA-транзакції шини SPI
void IRAM_ATTR spi_dma_complete_isr(void *arg)
{
    // Інформування графічного рушія про готовність каналу передачі
    lv_disp_flush_ready(&disp_drv);
}

// Функція оновлення прямокутної області екрана
static void disp_flush_dma_cb(lv_disp_drv_t *drv, const lv_area_t *area, lv_color_t *color_p)
{
    uint32_t pixel_count = (area->x2 - area->x1 + 1) * (area->y2 - area->y1 + 1);

    // Задання координат апаратного вікна на контролері ST7789
    st7789_set_address_window(area->x1, area->y1, area->x2, area->y2, drv->rotated);

    // Запуск асинхронної фонової передачі пікселів через контролер DMA
    spi_dma_transmit_async((const uint8_t *)color_p, pixel_count * sizeof(lv_color_t));

    // Важливо: lv_disp_flush_ready() тут НЕ викликається!
    // Його викличе переривання spi_dma_complete_isr після спустошення буфера.
}

void init_display_subsystem(void)
{
    // Реєстрація подвійної буферизації у структурі дескриптора
    lv_disp_draw_buf_init(&disp_buf_desc, draw_buf_1, draw_buf_2, DISP_HOR_RES * BUFFER_ROWS);

    lv_disp_drv_init(&disp_drv);
    disp_drv.hor_res = DISP_HOR_RES;
    disp_drv.ver_res = DISP_VER_RES;
    disp_drv.flush_cb = disp_flush_dma_cb;
    disp_drv.draw_buf = &disp_buf_desc;

    lv_disp_drv_register(&disp_drv);
}
