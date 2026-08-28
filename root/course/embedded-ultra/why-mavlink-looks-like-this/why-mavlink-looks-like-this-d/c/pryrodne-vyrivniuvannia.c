// Канонічна структура MAVLink ATTITUDE (ID 30) після сортування полів
typedef struct __mavlink_attitude_t {
    uint32_t time_boot_ms; // 4 байти (зсув 0x00)
    float    roll;         // 4 байти (зсув 0x04)
    float    pitch;        // 4 байти (зсув 0x08)
    float    yaw;          // 4 байти (зсув 0x0C)
    float    rollspeed;    // 4 байти (зсув 0x10)
    float    pitchspeed;   // 4 байти (зсув 0x14)
    float    yawspeed;     // 4 байти (зсув 0x18)
} mavlink_attitude_t; // Розмір: рівно 28 байтів. Паддинг = 0 байтів!
