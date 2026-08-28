// ── Стани кола зарядки ──────────────────────────────────────────────
typedef enum {
    ST_INIT,       // нема контракту; на порті безпечні 5 В
    ST_NEGOTIATE,  // шукаємо PPS-APDO і укладаємо перший запит
    ST_CC,         // сталий струм: женемо струм комірки до цілі
    ST_CV,         // стала напруга: тримаємо комірку на 4.40, струм спадає
    ST_DONE,       // струм упав нижче термінації — заряд завершено
    ST_FAULT,      // аварія (hard reset, перегрів) — усе спочатку
} charge_state_t;

static volatile charge_state_t g_state = ST_INIT;
static int g_vreq_mv;        // поточна запитана напруга ПОРТУ (сітка 20 мВ)
static int g_ilim_ma;        // поточна стеля струму APDO (сітка 50 мВ)
static int g_i_charge_ma;    // цільовий струм CC (може падати від перегріву)

// ── Числа задачі ────────────────────────────────────────────────────
#define PPS_VSTEP_MV      20      // крок напруги PPS
#define PPS_ISTEP_MA      50      // крок струму PPS
#define APDO_VMIN_MV      3300    // мінімум обраного APDO (тут 3.3 В — межа стандарту)
#define APDO_VMAX_MV      11000   // максимум обраного APDO
#define APDO_IMAX_MA      5000    // стеля струму обраного APDO
#define V_CELL_TARGET_MV  4400    // коліно CV
#define I_CHARGE_MA       3000    // цільовий струм CC
#define I_TERM_MA         150     // поріг термінації CV (≈ C/20)
#define R_PATH_MOHM       40      // опір шляху порт→комірка: кабель + конектор + ключ
#define CC_HEADROOM_MV    60      // запас над коміркою, щоб триматись у CL

// Оголошені наперед — тіла цих статичних функцій нижче, кожне у своєму блоці.
static void enter_cv(void);                  // перехід CC→CV
static void thermal_backoff(int drop_ma);    // тепловий відкат цільового струму

// Затиснути напругу в межі обраного APDO і лягти на 20 мВ-сітку (вниз — безпечно).
static int clamp_to_apdo_v(int mv) {
    if (mv < APDO_VMIN_MV) mv = APDO_VMIN_MV;   // ← ПАСТКА №2 живе саме тут
    if (mv > APDO_VMAX_MV) mv = APDO_VMAX_MV;
    return (mv / PPS_VSTEP_MV) * PPS_VSTEP_MV;   // округлення ВНИЗ до сітки
}

// Затиснути струм у стелю APDO і лягти на 50 мА-сітку.
static int clamp_to_apdo_i(int ma) {
    if (ma > APDO_IMAX_MA) ma = APDO_IMAX_MA;
    if (ma < 0) ma = 0;
    return (ma / PPS_ISTEP_MA) * PPS_ISTEP_MA;
}

// Скільки замовити на ПОРТІ, щоб на КОМІРЦІ вийшло v_cell_mv при струмі i_ma:
// порт вищий за комірку рівно на падіння I·R у кабелі (ще без затиску/сітки).
static int port_for_cell(int v_cell_mv, int i_ma) {
    return v_cell_mv + (i_ma * R_PATH_MOHM) / 1000;   // мА·мОм = мкВ, /1000 → мВ
}
