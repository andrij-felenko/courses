#include <stdint.h>
#include <stdbool.h>

typedef enum {
    EV_SYS_NONE             = 0x00, /* Порожня подія (відсутність сигналу) */
    EV_SYS_ENTRY            = 0x01, /* Вхід у стан (викликається диспетчером) */
    EV_SYS_EXIT             = 0x02, /* Вихід зі стану */
    EV_SYS_INIT             = 0x03, /* Внутрішня ініціалізація підстанів */
    EV_CMD_START_MISSION    = 0x10, /* Команда запуску виконання черги цілей */
    EV_CMD_PAUSE_MISSION    = 0x11, /* Команда тимчасової зупинки на місці */
    EV_CMD_RESUME_MISSION   = 0x12, /* Поновлення раніше зупиненого руху */
    EV_CMD_ABORT_MISSION    = 0x13, /* Примусове аварійне скасування місії */
    EV_NAV_WAYPOINT_REACHED = 0x20, /* Цільову точку маршруту досягнуто */
    EV_NAV_HEADING_LOCKED   = 0x21, /* Кут курсу стабілізовано в межах допуску */
    EV_NAV_OBSTACLE_NEAR    = 0x22, /* Попередження далекоміра: зона маневрування */
    EV_NAV_OBSTACLE_STOP    = 0x23, /* Критична дистанція: екстрене зупинення */
    EV_NAV_PATH_CLEAR       = 0x24, /* Перешкода зникла з поля зору сенсорів */
    EV_FAIL_BATTERY_LOW     = 0x40, /* Напруга акумулятора нижче робочого порогу */
    EV_FAIL_SENSOR_TIMEOUT  = 0x41, /* Сенсор не надав відліку у відведений слот */
    EV_FAIL_ACTUATOR_STALL  = 0x42, /* Перевантаження або зупинка мотора за струмом */
    EV_FAIL_CRITICAL        = 0x4F  /* Загальна фатальна відмова обладнання */
} EventId;

typedef struct {
    uint8_t id;             /* Ідентифікатор події (тип EventId) */
    uint8_t priority;       /* Пріоритет: 0 — найвищий (ISR), 255 — фоновий */
    uint16_t reserved;      /* Вирівнювання структури до межі 4 байтів */
    uint32_t timestamp_us;  /* Системна мітка часу в мікросекундах */
    union {
        int32_t  i32;       /* Знаковий 32-бітний параметр */
        float    f32;       /* Значення з рухомою комою */
        uint32_t u32;       /* Беззнаковий параметр або бітова маска */
        struct {
            int16_t x_mm;   /* Координата X у міліметрах */
            int16_t y_mm;   /* Координата Y у міліметрах */
        } nav_pt;
        struct {
            uint16_t sensor_id;
            uint16_t error_code;
        } fault;
    } param;
} Event;
