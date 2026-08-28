typedef struct __mavlink_set_position_target_local_ned_t {
    uint32_t time_boot_ms; // Час від старту системи (мс)
    float x;               // Цільова позиція X (Північ, метри)
    float y;               // Цільова позиція Y (Схід, метри)
    float z;               // Цільова позиція Z (Вниз, від'ємна висота, метри)
    float vx;              // Цільова швидкість Vx (м/с)
    float vy;              // Цільова швидкість Vy (м/с)
    float vz;              // Цільова швидкість Vz (м/с)
    float afx;             // Цільове прискорення Ax (м/с^2)
    float afy;             // Цільове прискорення Ay (м/с^2)
    float afz;             // Цільове прискорення Az (м/с^2)
    float yaw;             // Цільовий кут курсу (радіани)
    float yaw_rate;        // Цільова кутова швидкість курсу (рад/с)
    uint16_t type_mask;    // Бітова маска ігнорування полів
    uint8_t target_system; // sysid автопілота (1)
    uint8_t target_component; // compid автопілота (1)
    uint8_t coordinate_frame; // Система координат (MAV_FRAME_LOCAL_NED)
} mavlink_set_position_target_local_ned_t;
