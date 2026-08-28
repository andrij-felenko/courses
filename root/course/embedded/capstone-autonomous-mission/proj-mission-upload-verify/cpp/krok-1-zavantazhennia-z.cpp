// Пункт місії у зручному вигляді. Координати — ЦІЛІ, в одиницях 1e-7 градуса!
// (Чому цілі, а не float — див. пастку нижче; коротко: float дав би метрову
//  похибку ще на землі.)
typedef struct {
    uint16_t seq, command;
    uint8_t  frame, autocontinue;
    float    p1, p2, p3, p4, z;
    int32_t  x, y;                        // 1e-7 градуса — ЦІЛІ
} wp_t;

// Конструктор пункту: градуси → цілі 1e-7° рівно ОДИН раз, тут, при складанні.
static wp_t wp(uint16_t seq, uint16_t command, double lat_deg, double lon_deg, float alt_m) {
    wp_t w = {0};
    w.seq = seq; w.command = command;
    w.frame = MAV_FRAME_GLOBAL_RELATIVE_ALT_INT;
    w.autocontinue = 1;
    w.x = (int32_t)lround(lat_deg * 1e7);  // градуси → ціле 1e-7°, ОДИН раз
    w.y = (int32_t)lround(lon_deg * 1e7);
    w.z = alt_m;
    return w;
}

// Приклад місії для коптера: зліт 15 м → точка A → точка B → RTL.
#define N 4
static wp_t mission[N];
static void build_mission(void) {
    const double HL = 50.4501, HN = 30.5234;   // десь у Києві, для прикладу
    mission[0] = wp(0, MAV_CMD_NAV_TAKEOFF,          HL,          HN,          15.0f);
    mission[1] = wp(1, MAV_CMD_NAV_WAYPOINT,         HL + 0.0004, HN,          15.0f);
    mission[2] = wp(2, MAV_CMD_NAV_WAYPOINT,         HL + 0.0004, HN + 0.0006, 15.0f);
    mission[3] = wp(3, MAV_CMD_NAV_RETURN_TO_LAUNCH, 0,           0,           0.0f);
}
