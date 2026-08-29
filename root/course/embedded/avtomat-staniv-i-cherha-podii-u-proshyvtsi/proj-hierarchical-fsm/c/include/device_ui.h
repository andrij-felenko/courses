/*
 * device_ui.h — трирівневе ієрархічне меню портативного калібратора.
 *
 * Дерево станів:
 *   ScreenSaver           екран вимкнено, процесор спить
 *   Active                суперстан: підсвітка, аварії, таймаут бездіяльності
 *     MainMenu            типовий підстан Active
 *     Settings            яскравість і калібрування
 *       Calibration       вимірювання зміщення нуля АЦП
 */
#ifndef DEVICE_UI_H
#define DEVICE_UI_H

#include "qhsm.h"

/* Сигнали застосунку. Нумерація починається з Q_USER_SIG, бо перші
 * чотири номери зайняті службовими сигналами рушія. */
enum DeviceSignals {
    BTN_UP_SIG = Q_USER_SIG,
    BTN_DOWN_SIG,
    BTN_ENTER_SIG,
    BTN_BACK_SIG,
    TIMEOUT_IDLE_SIG,  /* хвилина без натискань */
    SENSOR_FAULT_SIG   /* давач відмовив: обробляється з будь-якого підменю */
};

/* Пункти головного меню */
enum MenuItems {
    MENU_MEASURE = 0U,
    MENU_SETTINGS,
    MENU_ABOUT,
    MENU_ITEM_COUNT
};

typedef struct {
    QHsm super;            /* автомат мусить бути ПЕРШИМ полем: рушій
                            * передає обробникам QHsm*, а той приводиться
                            * назад до DeviceUI* */
    uint8_t brightness;    /* яскравість підсвітки, відсотки */
    uint8_t menu_item;     /* виділений пункт головного меню */
    int16_t adc_offset;    /* збережене зміщення нуля АЦП */
    uint8_t error_count;   /* відмови давача від останнього скидання */
    bool is_calibrated;
    bool accept_calib;     /* чи приймати результат при виході з Calibration */
} DeviceUI;

void DeviceUI_ctor(DeviceUI *me);

/* Автомат усередині приладу — для QHsm_init і QHsm_dispatch. */
QHsm *DeviceUI_hsm(DeviceUI *me);

/* Чи спить прилад зараз (для головного циклу: чи можна вимикати тактування). */
bool DeviceUI_isAsleep(DeviceUI *me);

#endif /* DEVICE_UI_H */
