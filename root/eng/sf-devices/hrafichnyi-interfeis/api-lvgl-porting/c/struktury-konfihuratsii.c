/* Типи пристроїв введення */
typedef enum {
    LV_INDEV_TYPE_NONE,     /* Не визначено */
    LV_INDEV_TYPE_POINTER,  /* Сенсорна панель, миша або тачпад (координати X, Y + натискання) */
    LV_INDEV_TYPE_KEYPAD,   /* Клавіатура (коди символів і навігаційні клавіші) */
    LV_INDEV_TYPE_BUTTON,   /* Фізичні кнопки, апаратно прив'язані до екранних точок */
    LV_INDEV_TYPE_ENCODER   /* Інкрементальний поворотний енкодер (+1 / -1 + клік) */
} lv_indev_type_t;

/* Фізичні стани пристрою */
typedef enum {
    LV_INDEV_STATE_RELEASED = 0,
    LV_INDEV_STATE_PRESSED  = 1
} lv_indev_state_t;

/* Структура передачі даних введення */
typedef struct {
    lv_point_t point;            /* Поточні координати {x, y} для типу POINTER */
    uint32_t key;                /* Код клавіші для типу KEYPAD / ENCODER */
    uint32_t btn_id;             /* Номер кнопки для типу BUTTON */
    int16_t enc_diff;            /* Відносний кут обертання енкодера (+1 / -1) */
    lv_indev_state_t state;      /* Стан: натиснуто (PRESSED) або відпущено (RELEASED) */
    bool continue_reading;       /* true, якщо в апаратному буфері є ще накопичені координати */
} lv_indev_data_t;

/* Дескриптор драйвера пристрою введення */
typedef struct _lv_indev_drv_t {
    lv_indev_type_t type;        /* Тип пристрою введення */
    void (*read_cb)(struct _lv_indev_drv_t *indev_drv, lv_indev_data_t *data);
    void *user_data;             /* Користувацький контекст */
    lv_disp_t *disp;             /* Дисплей, до якого прив'язаний пристрій */
    lv_timer_t *read_timer;      /* Системний таймер періодичного опитування */
    uint16_t long_press_time;    /* Час утримання до генерації події LONG_PRESSED (мс) */
    uint16_t long_press_repeat_time; /* Період генерації повторних подій LONG_PRESSED_REPEAT (мс) */
    uint16_t scroll_limit;       /* Мінімальний поріг зсуву в пікселях для старту скролінгу */
} lv_indev_drv_t;
