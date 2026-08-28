/* Дії виконавчих механізмів */
static void on_overheat(void *ctx, int32_t param) {
    (void)ctx;
    (void)param;
    /* Безпосередній запис у регістри апаратного таймера/GPIO */
    /* Вимкнути ШІМ ТЕНу, увімкнути охолоджувач на 100% */
}

static void on_overpressure(void *ctx, int32_t param) {
    (void)ctx;
    (void)param;
    /* Відкрити електромагнітний клапан аварійного скидання */
}

static void on_estop(void *ctx, int32_t param) {
    (void)ctx;
    (void)param;
    /* Повне знеструмлення силової шини */
}

/* Статична таблиця правил у Flash */
static const rule_def_t g_system_rules[] = {
    {
        .rule_id = 1,
        .fact_id = FACT_ESTOP_PRESSED,
        .op = OP_EQUALS,
        .threshold_low = 1,
        .threshold_high = 1,
        .dwell_time_ms = 0,             /* Миттєва реакція без затримки */
        .interlock_mask = 0,            /* Ніщо не може заблокувати E-Stop */
        .set_interlock = 0xFFFFFFFF,    /* Блокує абсолютно всі інші правила */
        .action = on_estop,
        .action_param = 0
    },
    {
        .rule_id = 2,
        .fact_id = FACT_PRESSURE_KPA,
        .op = OP_GREATER_THAN,
        .threshold_low = 0,
        .threshold_high = 600,          /* Поріг 600 кПа */
        .dwell_time_ms = 50,            /* Витримка 50 мс для фільтрації гідроудару */
        .interlock_mask = 0x01,         /* Блокується, якщо активний E-Stop */
        .set_interlock = 0x02,          /* Блокує підсистеми нагріву */
        .action = on_overpressure,
        .action_param = 0
    },
    {
        .rule_id = 3,
        .fact_id = FACT_TEMP_C,
        .op = OP_GREATER_THAN,
        .threshold_low = 0,
        .threshold_high = 95,           /* Поріг 95 °C */
        .dwell_time_ms = 200,           /* Витримка 200 мс */
        .interlock_mask = 0x03,         /* Блокується аварією або перетиском */
        .set_interlock = 0x04,
        .action = on_overheat,
        .action_param = 0
    }
};
