// Байт Real-Time Flags із повідомлення PPS_Status (USB PD 3.0):
//   біт 3     OMF (Operating Mode Flag): 0 = CV (тримає напругу), 1 = CL (тримає струм)
//   біти 2..1 PTF (Present Temperature Flag): 0=не підтр., 1=норма, 2=увага, 3=перегрів
//   біти 7..4, 0 — резерв
#define RTF_OMF_MASK    0x08
#define RTF_PTF_MASK    0x06
#define RTF_PTF_SHIFT   1
enum { PTF_NA = 0, PTF_NORMAL = 1, PTF_WARNING = 2, PTF_OVERTEMP = 3 };

static uint8_t g_rtf;   // останній прочитаний байт прапорців

bool pps_source_in_cl(void) { return (g_rtf & RTF_OMF_MASK) != 0; }
static int pps_source_temp(void) { return (g_rtf & RTF_PTF_MASK) >> RTF_PTF_SHIFT; }

// Раз на кілька секунд питаємо статус і реагуємо на перегрів адаптера.
void pps_poll_status(void) {
    pps_status_t st;
    if (!pd_get_pps_status(&st))    // Get_PPS_Status → PPS_Status
        return;                     // не відповів — лишаємо старі прапорці
    g_rtf = st.real_time_flags;

    switch (pps_source_temp()) {
    case PTF_WARNING:               // адаптер гріється — заздалегідь прибрати струм
        thermal_backoff(500);       //   −0.5 А з цілі, поки не охолоне
        break;
    case PTF_OVERTEMP:              // адаптер на межі зриву — прибрати сильно
        thermal_backoff(1500);      //   −1.5 А: краще повільніше, ніж hard reset
        break;
    default:
        break;
    }
}

// Знизити цільовий струм CC (не нижче розумного мінімуму). CC-крок підхопить нову ціль.
static void thermal_backoff(int drop_ma) {
    g_i_charge_ma -= drop_ma;
    if (g_i_charge_ma < 500) g_i_charge_ma = 500;
}
