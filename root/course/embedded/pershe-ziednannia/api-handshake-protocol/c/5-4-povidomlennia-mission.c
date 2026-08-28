typedef struct __mavlink_mission_item_int_t {
    float   param1;           // Параметр 1 команди (наприклад, час зависання у секундах)
    float   param2;           // Параметр 2 (радіус прийняття точки в метрах)
    float   param3;           // Параметр 3 (радіус проходження по спіралі або 0)
    float   param4;           // Параметр 4 (бажаний курс / Yaw у градусах)
    int32_t x;                // Широта (Latitude) * 1e7 (наприклад, 504501000 = 50.4501000° N)
    int32_t y;                // Довгота (Longitude) * 1e7 (наприклад, 305234000 = 30.5234000° E)
    float   z;                // Висота в метрах (AMSL або відносна над точкою зльоту)
    uint16_t seq;             // Порядковий номер точки (0 .. N-1)
    uint16_t command;         // MAV_CMD (16=NAV_WAYPOINT, 20=NAV_RETURN_TO_LAUNCH, 21=NAV_LAND, 22=NAV_TAKEOFF)
    uint8_t target_system;    // SysID станції
    uint8_t target_component; // CompID станції
    uint8_t frame;            // Система координат (MAV_FRAME: 0=GLOBAL, 3=GLOBAL_RELATIVE_ALT, 6=GLOBAL_TERRAIN_ALT)
    uint8_t current;          // 1 = поточна активна точка навігації, 0 = неактивна
    uint8_t autocontinue;     // 1 = автоматично переходити до наступної точки після досягнення
    uint8_t mission_type;     // 0 = MAV_MISSION_TYPE_MISSION
} mavlink_mission_item_int_t;
