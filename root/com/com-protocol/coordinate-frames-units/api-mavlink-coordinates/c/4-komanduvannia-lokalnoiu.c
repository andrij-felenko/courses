typedef struct __mavlink_set_position_target_local_ned_t {
    uint32_t time_boot_ms;    /* Час від старту польотного контролера (мс) */
    uint16_t type_mask;       /* Бітова маска вибору контурів керування */
    uint8_t  target_system;   /* SYS ID цільового апарата (зазвичай 1) */
    uint8_t  target_component;/* COMP ID цільового вузла (MAV_COMP_ID_AUTOPILOT1 = 1) */
    uint8_t  coordinate_frame;/* Базис: MAV_FRAME_LOCAL_NED або MAV_FRAME_BODY_NED */
    float    x;               /* Цільова координата X або зміщення (метри) */
    float    y;               /* Цільова координата Y або зміщення (метри) */
    float    z;               /* Цільова координата Z (метри, Z < 0 для польоту вгору) */
    float    vx;              /* Цільова лінійна швидкість X (м/с) */
    float    vy;              /* Цільова лінійна швидкість Y (м/с) */
    float    vz;              /* Цільова лінійна швидкість Z (м/с) */
    float    afx;             /* Цільове прискорення X (м/с^2) */
    float    afy;             /* Цільове прискорення Y (м/с^2) */
    float    afz;             /* Цільове прискорення Z (м/с^2) */
    float    yaw;             /* Цільовий кут курсу (радіани, 0 = Північ) */
    float    yaw_rate;        /* Цільова швидкість зміни курсу (rad/s) */
} mavlink_set_position_target_local_ned_t;
