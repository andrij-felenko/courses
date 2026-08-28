typedef enum { ST_DETACHED, ST_SETTLE, ST_MEASURE, ST_LATCHED } state_t;

#define SETTLE_MS  100
#define MAX_TRIES  3

static state_t     st  = ST_DETACHED;
static src_class_t cls = SRC_UNKNOWN;
static uint32_t    t_mark;
static uint8_t     tries;

/* VBUS: є — вище 4.4 В, нема — нижче 4.0 В. Ті самі два пороги, що й у класі:
   рішення на межі мусить мати роздільну смугу. */
static bool vbus_present(void)
{
    static bool present = false;
    int mv = vbus_read_mv();

    if (!present && mv > 4400)      present = true;
    else if (present && mv < 4000)  present = false;
    return present;
}

static uint16_t limit_ma(src_class_t c)
{
    switch (c) {
    case SRC_500MA: return 500;
    case SRC_1A:    return 1000;
    case SRC_2A1:   return 2100;
    case SRC_2A4:   return 2400;
    default:        return 500;   /* чужий діалект — найнижче безпечне */
    }
}

/* Викликати раз на ~10 мс. */
void charger_tick(uint32_t now_ms)
{
    if (!vbus_present()) {
        if (st != ST_DETACHED) {
            set_input_limit_ma(0);
            cls = SRC_UNKNOWN;
            st  = ST_DETACHED;    /* тільки тут скидається засув */
        }
        return;
    }

    switch (st) {
    case ST_DETACHED:
        usb_phy_attach(false);    /* зняти з D+ підтяжку 1.5 кОм — інакше 3.27 В */
        dline_adc_init();         /* аналоговий режим + 239.5 такту вибірки */
        set_input_limit_ma(100);  /* поки не знаємо — беремо мінімум */
        tries  = 0;
        t_mark = now_ms;
        st     = ST_SETTLE;
        break;

    case ST_SETTLE:
        if (now_ms - t_mark >= SETTLE_MS)
            st = ST_MEASURE;
        break;

    case ST_MEASURE: {
        int dp = dline_read_mv(CH_DP);
        int dm = dline_read_mv(CH_DM);
        src_class_t c = class_of(lvl_enter(dp), lvl_enter(dm));

        if (c == SRC_UNKNOWN && ++tries < MAX_TRIES) {
            t_mark = now_ms;
            st     = ST_SETTLE;   /* дати ще вгамуватися й спробувати ще раз */
            break;
        }
        cls = c;
        set_input_limit_ma(limit_ma(cls));
        usb_phy_attach(want_usb_data());  /* аж тепер: підпис уже прочитано */
        st = ST_LATCHED;
        break;
    }

    case ST_LATCHED:
        /* Свідомо порожньо. Просадка під навантаженням — не привід
           перекласифіковувати: цим займається вхідний регулятор зарядника. */
        break;
    }
}
