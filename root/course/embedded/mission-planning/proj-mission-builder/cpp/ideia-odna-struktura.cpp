#include <stdint.h>
#include <math.h>
#include "mavlink.h"

// Перетворити градуси (як їх дає людина чи мапа) у масштабоване ціле:
// градуси × 10⁷. Саме цього очікують поля x/y у MISSION_ITEM_INT.
// lround, а не (int32_t)каст: каст відрізає дробову частину, а ми хочемо
// округлити до найближчого цілого, щоб не втратити пів сантиметра на кожній точці.
static inline int32_t deg_to_1e7(double deg) {
    return (int32_t)lround(deg * 1e7);
}

// Базова заготовка навігаційного пункта: спільні поля для всіх точок місії.
// Координати приходять у ГРАДУСАХ (double) і масштабуються тут, в одному місці.
static mavlink_mission_item_int_t make_nav_item(
        uint16_t seq, uint16_t command,
        double lat_deg, double lon_deg, float alt_m) {
    mavlink_mission_item_int_t it = {};          // обнулити ВСЕ — критично, див. пастки
    it.target_system    = TARGET_SYS;            // кому: SYS/COMP апарата з HEARTBEAT
    it.target_component  = TARGET_COMP;
    it.seq              = seq;                    // номер пункту в списку
    it.frame            = MAV_FRAME_GLOBAL_RELATIVE_ALT_INT;  // висота — від домівки
    it.command          = command;               // що робити (значення MAV_CMD)
    it.current          = 0;                      // не «поточний» (керує апарат у польоті)
    it.autocontinue     = 1;                      // виконав — переходь до наступного сам
    it.x                = deg_to_1e7(lat_deg);    // широта × 10⁷ (ціле!)
    it.y                = deg_to_1e7(lon_deg);    // довгота × 10⁷ (ціле!)
    it.z                = alt_m;                  // висота, м (у цьому frame — над домівкою)
    it.mission_type     = MAV_MISSION_TYPE_MISSION;  // це план польоту, не геозона/rally
    return it;
}
