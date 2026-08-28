/* Користувацькі сигнали */
enum DeviceSignals {
    BTN_UP_SIG = Q_USER_SIG,
    BTN_DOWN_SIG,
    BTN_ENTER_SIG,
    BTN_BACK_SIG,
    TIMEOUT_IDLE_SIG
};

/* Контекст меню приладу */
typedef struct {
    QHsm super;
    uint8_t brightness;
    bool is_calibrated;
} DeviceUI;

/* Прототипи функцій станів */
static QResult state_screen_saver(QHsm *me, const QEvt *e);
static QResult state_active(QHsm *me, const QEvt *e);
static QResult state_main_menu(QHsm *me, const QEvt *e);
static QResult state_settings(QHsm *me, const QEvt *e);
static QResult state_calibration(QHsm *me, const QEvt *e);

/* Початковий стан */
static QResult state_initial(QHsm *me, const QEvt *e) {
    (void)e;
    return Q_TRAN(state_screen_saver);
}

/* Стан збереження енергії / заставки */
static QResult state_screen_saver(QHsm *me, const QEvt *e) {
    switch (e->sig) {
        case BTN_ENTER_SIG:
        case BTN_BACK_SIG:
            return Q_TRAN(state_main_menu);

        default:
            return Q_SUPER(QHsm_top);
    }
}

/* Суперстан Active: керує активною підсвіткою та загальними таймаутами */
static QResult state_active(QHsm *me, const QEvt *e) {
    switch (e->sig) {
        case Q_ENTRY_SIG:
            // LCD_SetBacklight(100);
            return Q_HANDLED();

        case Q_EXIT_SIG:
            // LCD_SetBacklight(0);
            return Q_HANDLED();

        case TIMEOUT_IDLE_SIG:
            /* Глобальний таймаут: з будь-якого підменю йдемо в ScreenSaver */
            return Q_TRAN(state_screen_saver);

        default:
            return Q_SUPER(QHsm_top);
    }
}

/* Підстан: Головне меню */
static QResult state_main_menu(QHsm *me, const QEvt *e) {
    switch (e->sig) {
        case Q_ENTRY_SIG:
            // Draw_Icon_Menu();
            return Q_HANDLED();

        case BTN_ENTER_SIG:
            return Q_TRAN(state_settings);

        default:
            /* Усі невідомі події піднімаються до state_active */
            return Q_SUPER(state_active);
    }
}

/* Підстан: Налаштування */
static QResult state_settings(QHsm *me, const QEvt *e) {
    DeviceUI *dev = (DeviceUI *)me;

    switch (e->sig) {
        case Q_ENTRY_SIG:
            // Display_Settings_List();
            return Q_HANDLED();

        case BTN_UP_SIG:
            if (dev->brightness < 100) dev->brightness += 10;
            return Q_HANDLED();

        case BTN_ENTER_SIG:
            return Q_TRAN(state_calibration);

        case BTN_BACK_SIG:
            /* Повернення на головний екран */
            return Q_TRAN(state_main_menu);

        default:
            return Q_SUPER(state_active);
    }
}

/* Підстан: Калібрування (вкладений у state_settings) */
static QResult state_calibration(QHsm *me, const QEvt *e) {
    DeviceUI *dev = (DeviceUI *)me;

    switch (e->sig) {
        case Q_ENTRY_SIG:
            // ADC_Start_Calib();
            return Q_HANDLED();

        case Q_EXIT_SIG:
            // ADC_Stop_Calib();
            return Q_HANDLED();

        case BTN_ENTER_SIG:
            dev->is_calibrated = true;
            return Q_TRAN(state_settings);

        case BTN_BACK_SIG:
            /* Повернення на рівень налаштувань */
            return Q_TRAN(state_settings);

        default:
            /* Подія TIMEOUT_IDLE_SIG піде в state_settings -> state_active -> state_screen_saver */
            return Q_SUPER(state_settings);
    }
}

void device_ui_init(DeviceUI *ui) {
    ui->brightness = 80;
    ui->is_calibrated = false;
    QHsm_init(&ui->super, state_initial);
}
