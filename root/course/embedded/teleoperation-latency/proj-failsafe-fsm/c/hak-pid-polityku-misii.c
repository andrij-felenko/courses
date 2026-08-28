// Гак політики місії — реалізацію обирає прошивка (як FS_ACTION у ArduPilot).
// Викликається ОДИН раз при вході в FS_RTL.
typedef enum {
    POLICY_HOLD,        // FS_ACTION=2: стій, де став
    POLICY_RTL,         // FS_ACTION=1: пряма траса до точки старту
    POLICY_SMART_RTL    // FS_ACTION=3: назад власним записаним слідом
} fs_policy_t;

extern fs_policy_t mission_policy(void);   // що задано на цю місію
extern void        mission_hold(void);     // лишитись у Hold
extern bool        mission_rtl_start(void);      // почати RTL; false якщо неможливо
extern bool        mission_smart_rtl_start(void);// почати SmartRTL; false якщо слід порожній/повний

// Виконати політику місії при вході в FS_RTL. Обережно: якщо активна
// дія неможлива — чесно падаємо назад у безпечне «стій».
static void fs_enter_policy(void)
{
    switch (mission_policy()) {
        case POLICY_SMART_RTL:
            // Спробувати слід; якщо буфер порожній/переповнений — RTL, а тоді Hold.
            if (mission_smart_rtl_start()) break;
            if (mission_rtl_start())       break;
            mission_hold();
            break;
        case POLICY_RTL:
            if (mission_rtl_start()) break;
            mission_hold();          // не вийшло — просто стій
            break;
        case POLICY_HOLD:
        default:
            mission_hold();          // найбезпечніше за замовчуванням
            break;
    }
}
