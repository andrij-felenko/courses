#include "blackbox.h"

void blackbox_init(BlackBox *bb)
{
    if (!bb) return;
    bb->head = 0;
    bb->count = 0;
    bb->dropped = 0;
}

/* Останній записаний елемент, або NULL, якщо буфер порожній. */
static BbEntry *blackbox_last(BlackBox *bb)
{
    if (bb->count == 0) return NULL;
    return &bb->items[(bb->head + BLACKBOX_CAPACITY - 1u) % BLACKBOX_CAPACITY];
}

void blackbox_record(BlackBox *bb, uint32_t tick, float time_s,
                     uint8_t status, uint8_t reason, float value)
{
    if (!bb) return;

    BbEntry *last = blackbox_last(bb);
    if (last && last->status == status && last->reason == reason) {
        /* Той самий інваріант тисне далі — подовжуємо епізод */
        last->t_end = time_s;
        last->value = value;
        last->repeats++;
        return;
    }

    BbEntry *slot = &bb->items[bb->head];
    slot->tick_begin = tick;
    slot->t_begin = time_s;
    slot->t_end = time_s;
    slot->status = status;
    slot->reason = reason;
    slot->value = value;
    slot->repeats = 1u;

    bb->head = (bb->head + 1u) % BLACKBOX_CAPACITY;
    if (bb->count < BLACKBOX_CAPACITY) {
        bb->count++;
    } else {
        bb->dropped++; /* затерли найстарішу подію */
    }
}

uint32_t blackbox_size(const BlackBox *bb)
{
    return bb ? bb->count : 0u;
}

const BbEntry *blackbox_at(const BlackBox *bb, uint32_t index)
{
    if (!bb || index >= bb->count) return NULL;
    /* Найстаріший запис лежить на head, коли буфер уже обернувся */
    uint32_t oldest = (bb->count == BLACKBOX_CAPACITY)
                    ? bb->head
                    : (bb->head + BLACKBOX_CAPACITY - bb->count) % BLACKBOX_CAPACITY;
    return &bb->items[(oldest + index) % BLACKBOX_CAPACITY];
}

const char *bb_reason_name(uint8_t reason)
{
    switch ((BbReason)reason) {
        case BB_REASON_NONE:        return "-";
        case BB_REASON_ESTOP:       return "кнопка-стоп";
        case BB_REASON_WATCHDOG:    return "сторож-плану";
        case BB_REASON_BAD_PLAN:    return "хибна-уставка";
        case BB_REASON_OBSTACLE:    return "дистанція";
        case BB_REASON_BATTERY:     return "напруга";
        case BB_REASON_TILT:        return "крен";
        case BB_REASON_SPEED_LIMIT: return "стеля-швидкості";
        case BB_REASON_YAW_LIMIT:   return "стеля-рискання";
        case BB_REASON_ACCEL_LIMIT: return "темп-розгону";
        case BB_REASON_SENSOR_LOST: return "давач-мовчить";
        default:                    return "?";
    }
}

const char *bb_status_name(uint8_t status)
{
    switch (status) {
        case 0:  return "ПРОПУЩЕНО";
        case 1:  return "ЗАТИСНУТО";
        case 2:  return "ГАЛЬМУВАННЯ";
        case 3:  return "АВАР.СТОП";
        default: return "?";
    }
}
