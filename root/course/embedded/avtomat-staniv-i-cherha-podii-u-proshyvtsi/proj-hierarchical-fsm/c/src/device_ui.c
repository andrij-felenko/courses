/*
 * device_ui.c — стани трирівневого меню.
 *
 * Кожен обробник описує ЛИШЕ те, що унікальне для його рівня. Усе спільне —
 * підсвітка, аварії давача, таймаут бездіяльності — живе в суперстані Active
 * і працює однаково з будь-якої глибини вкладеності. Гілка default кожного
 * обробника обов'язково повертає Q_SUPER: саме вона і є ребром дерева.
 */
#include "device_ui.h"
#include "device_hal.h"

#define BRIGHTNESS_STEP 10U
#define BRIGHTNESS_MIN  10U
#define BRIGHTNESS_MAX  100U

static QResult state_initial(QHsm *me, const QEvt *e);
static QResult state_screen_saver(QHsm *me, const QEvt *e);
static QResult state_active(QHsm *me, const QEvt *e);
static QResult state_main_menu(QHsm *me, const QEvt *e);
static QResult state_settings(QHsm *me, const QEvt *e);
static QResult state_calibration(QHsm *me, const QEvt *e);

static void act_clear_errors(QHsm *me);

void DeviceUI_ctor(DeviceUI *me) {
    Q_ASSERT(me != NULL);
    me->brightness = 80U;
    me->menu_item = MENU_MEASURE;
    me->adc_offset = 0;
    me->error_count = 0U;
    me->is_calibrated = false;
    me->accept_calib = false;
    QHsm_ctor(&me->super, &state_initial);
}

QHsm *DeviceUI_hsm(DeviceUI *me) {
    Q_ASSERT(me != NULL);
    return &me->super;
}

bool DeviceUI_isAsleep(DeviceUI *me) {
    Q_ASSERT(me != NULL);
    return QHsm_isIn(&me->super, &state_screen_saver);
}

/* Дія, прив'язана до самого переходу «Settings -> MainMenu»: рушій виконає
 * її після виходу зі старої гілки і до входу в нову. */
static void act_clear_errors(QHsm *me) {
    DeviceUI *dev = (DeviceUI *)me;
    dev->error_count = 0U;
    hal_trace("дія переходу: лічильник відмов давача скинуто");
}

/* Початковий псевдостан: прилад прокидається із зануреним екраном. */
static QResult state_initial(QHsm *me, const QEvt *e) {
    (void)e;
    return Q_TRAN(&state_screen_saver);
}

static QResult state_screen_saver(QHsm *me, const QEvt *e) {
    switch (e->sig) {
        case Q_ENTRY_SIG:
            hal_enter_low_power();
            return Q_HANDLED();

        case Q_EXIT_SIG:
            hal_exit_low_power();
            return Q_HANDLED();

        case BTN_UP_SIG:
        case BTN_DOWN_SIG:
            /* Прокрутка на зануреному екрані не будить прилад — але й
             * суперстанові подію не віддаємо: це свідома глухота. */
            return Q_IGNORED();

        case BTN_ENTER_SIG:
        case BTN_BACK_SIG:
            /* Ціль складена: типовий підстан обере Q_INIT_SIG у Active. */
            return Q_TRAN(&state_active);

        case SENSOR_FAULT_SIG: {
            /* Уві сні відмову лише рахуємо, екран не піднімаємо. */
            DeviceUI *dev = (DeviceUI *)me;
            if (dev->error_count < 255U) {
                ++dev->error_count;
            }
            return Q_HANDLED();
        }

        default:
            return Q_SUPER(&QHsm_top);
    }
}

/* Суперстан: усе спільне для всіх екранів приладу. */
static QResult state_active(QHsm *me, const QEvt *e) {
    DeviceUI *dev = (DeviceUI *)me;

    switch (e->sig) {
        case Q_ENTRY_SIG:
            hal_lcd_backlight(dev->brightness);
            return Q_HANDLED();

        case Q_EXIT_SIG:
            /* Гарантія рушія: підсвітка згасне на БУДЬ-ЯКОМУ шляху назовні,
             * з якої б глибини меню користувач не вийшов. */
            hal_lcd_backlight(0U);
            return Q_HANDLED();

        case Q_INIT_SIG:
            /* Типовий підстан складеного стану. */
            return Q_TRAN(&state_main_menu);

        case SENSOR_FAULT_SIG:
            /* Одна реакція на аварію замість копії в кожному підменю. */
            if (dev->error_count < 255U) {
                ++dev->error_count;
            }
            hal_show_fault(dev->error_count);
            return Q_HANDLED();

        case TIMEOUT_IDLE_SIG:
            /* Глобальний таймаут: із будь-якої глибини — у заставку. */
            return Q_TRAN(&state_screen_saver);

        default:
            return Q_SUPER(&QHsm_top);
    }
}

static QResult state_main_menu(QHsm *me, const QEvt *e) {
    DeviceUI *dev = (DeviceUI *)me;

    switch (e->sig) {
        case Q_ENTRY_SIG:
            hal_menu_draw(dev->menu_item);
            return Q_HANDLED();

        case BTN_UP_SIG:
            dev->menu_item = (uint8_t)((dev->menu_item + MENU_ITEM_COUNT - 1U)
                                       % MENU_ITEM_COUNT);
            hal_menu_draw(dev->menu_item);
            return Q_HANDLED();

        case BTN_DOWN_SIG:
            dev->menu_item = (uint8_t)((dev->menu_item + 1U) % MENU_ITEM_COUNT);
            hal_menu_draw(dev->menu_item);
            return Q_HANDLED();

        case BTN_ENTER_SIG:
            switch (dev->menu_item) {
                case MENU_SETTINGS:
                    return Q_TRAN(&state_settings);
                case MENU_MEASURE:
                    hal_show_measurement(dev->adc_offset);
                    return Q_HANDLED();
                default:
                    hal_show_about();
                    return Q_HANDLED();
            }

        case BTN_BACK_SIG:
            /* З кореня меню виходити нікуди, і будити суперстан не треба. */
            return Q_IGNORED();

        default:
            return Q_SUPER(&state_active);
    }
}

static QResult state_settings(QHsm *me, const QEvt *e) {
    DeviceUI *dev = (DeviceUI *)me;

    switch (e->sig) {
        case Q_ENTRY_SIG:
            hal_settings_draw(dev->brightness, dev->adc_offset, dev->is_calibrated);
            return Q_HANDLED();

        case Q_EXIT_SIG:
            /* Запис у Flash трапиться і при звичайному «Назад», і при
             * таймауті з глибини калібрування — рушій не дає шансу цього
             * пропустити. */
            hal_flash_save_settings(dev->brightness, dev->adc_offset);
            return Q_HANDLED();

        case BTN_UP_SIG:
            if (dev->brightness <= (uint8_t)(BRIGHTNESS_MAX - BRIGHTNESS_STEP)) {
                dev->brightness = (uint8_t)(dev->brightness + BRIGHTNESS_STEP);
            }
            hal_lcd_backlight(dev->brightness);
            hal_settings_draw(dev->brightness, dev->adc_offset, dev->is_calibrated);
            return Q_HANDLED();

        case BTN_DOWN_SIG:
            if (dev->brightness >= (uint8_t)(BRIGHTNESS_MIN + BRIGHTNESS_STEP)) {
                dev->brightness = (uint8_t)(dev->brightness - BRIGHTNESS_STEP);
            }
            hal_lcd_backlight(dev->brightness);
            hal_settings_draw(dev->brightness, dev->adc_offset, dev->is_calibrated);
            return Q_HANDLED();

        case BTN_ENTER_SIG:
            return Q_TRAN(&state_calibration);

        case BTN_BACK_SIG:
            return Q_TRAN_ACT(&state_main_menu, &act_clear_errors);

        default:
            return Q_SUPER(&state_active);
    }
}

static QResult state_calibration(QHsm *me, const QEvt *e) {
    DeviceUI *dev = (DeviceUI *)me;

    switch (e->sig) {
        case Q_ENTRY_SIG:
            dev->accept_calib = false;
            hal_adc_calib_start();
            return Q_HANDLED();

        case Q_EXIT_SIG: {
            /* Генератор глушиться завжди, а результат приймається лише
             * тоді, коли користувач устиг його підтвердити. Аварійний
             * вихід за таймаутом мовчки викидає недомірене значення. */
            int16_t offset = hal_adc_calib_stop();
            if (dev->accept_calib) {
                dev->adc_offset = offset;
                dev->is_calibrated = true;
            }
            dev->accept_calib = false;
            return Q_HANDLED();
        }

        case BTN_ENTER_SIG:
            dev->accept_calib = true;
            return Q_TRAN(&state_settings);

        case BTN_BACK_SIG:
            /* Скасування: вихід зі стану сам зупинить генератор. */
            return Q_TRAN(&state_settings);

        case BTN_UP_SIG:
        case BTN_DOWN_SIG:
            /* Під час вимірювання яскравість не чіпаємо: зміна струму
             * підсвітки зсунула б нуль АЦП просто в ході калібрування.
             * Подію ковтаємо, щоб вона не дісталася Settings. */
            return Q_IGNORED();

        default:
            /* TIMEOUT_IDLE_SIG звідси піде вгору: Settings -> Active,
             * і Active поверне прилад у заставку. */
            return Q_SUPER(&state_settings);
    }
}
