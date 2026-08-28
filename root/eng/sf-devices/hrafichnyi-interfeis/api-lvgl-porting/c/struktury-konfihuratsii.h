/* Структура дескриптора буферів рендерингу */
typedef struct {
    void *buf1;              /* Покажчик на перший буфер рендерингу */
    void *buf2;              /* Покажчик на другий буфер (NULL для одинарного режиму) */
    void *buf_act;           /* Покажчик на буфер, який зараз заповнює CPU */
    uint32_t size;           /* Розмір буфера в кількості пікселів */
    lv_area_t area;          /* Координати поточної області відрисовки */
    int rendering_in_prog;   /* Прапорець активного процесу малювання */
} lv_disp_draw_buf_t;

/* Головна структура конфігурації драйвера дисплея */
typedef struct _lv_disp_drv_t {
    lv_coord_t hor_res;          /* Горизонтальна роздільна здатність у пікселях */
    lv_coord_t ver_res;          /* Вертикальна роздільна здатність у пікселях */
    lv_coord_t physical_hor_res; /* Фізична ширина матриці (для апаратного масштабування) */
    lv_coord_t physical_ver_res; /* Фізична висота матриці */
    lv_coord_t offset_x;         /* Зсув вікна по осі X (для екранів із несиметричним контролером) */
    lv_coord_t offset_y;         /* Зсув вікна по осі Y */

    lv_disp_draw_buf_t *draw_buf;/* Покажчик на зв'язаний дескриптор буферів */

    /* Зворотні виклики (Callbacks) */
    void (*flush_cb)(struct _lv_disp_drv_t *disp_drv, const lv_area_t *area, lv_color_t *color_p);
    void (*rounder_cb)(struct _lv_disp_drv_t *disp_drv, lv_area_t *area);
    void (*set_px_cb)(struct _lv_disp_drv_t *disp_drv, uint8_t *buf, lv_coord_t buf_w,
                      lv_coord_t x, lv_coord_t y, lv_color_t color, lv_opa_t opa);
    void (*clean_dcache_cb)(struct _lv_disp_drv_t *disp_drv);

    /* Апаратні прапорці поведінки */
    uint32_t direct_mode : 1;    /* Рендеринг безпосередньо у повний подвійний фреймбуфер */
    uint32_t full_refresh : 1;   /* Примусове повне перемальовування всього екрана */

    void *user_data;             /* Довільний контекст користувача (покажчик на C++ об'єкт драйвера) */
} lv_disp_drv_t;
