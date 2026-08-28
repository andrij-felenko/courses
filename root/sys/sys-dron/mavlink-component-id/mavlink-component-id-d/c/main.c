#include <mavlink.h>

/* Кому адресовано пакет. Зсуви полів target_* беремо з таблиці,
   яку генератор зібрав із XML-опису: там же позначено, чи є вони взагалі. */
static void packet_target(const mavlink_message_t *msg,
                          uint8_t *tsys, uint8_t *tcomp)
{
    const mavlink_msg_entry_t *e = mavlink_get_msg_entry(msg->msgid);

    *tsys = *tcomp = 0;            /* нуль = «усім»: типове значення і для */
    if (!e) return;                /* незнайомого типу, і для оголошень    */

    if (e->flags & MAV_MSG_ENTRY_FLAG_HAVE_TARGET_SYSTEM)
        *tsys  = (uint8_t)_MAV_PAYLOAD(msg)[e->target_system_ofs];
    if (e->flags & MAV_MSG_ENTRY_FLAG_HAVE_TARGET_COMPONENT)
        *tcomp = (uint8_t)_MAV_PAYLOAD(msg)[e->target_component_ofs];
}

/* Чи обробляти пакет у себе. */
bool for_me(const mavlink_message_t *msg, uint8_t my_sys, uint8_t my_comp)
{
    uint8_t tsys, tcomp;
    packet_target(msg, &tsys, &tcomp);

    if (tsys == 0)      return true;    /* розсилання на всю мережу     */
    if (tsys != my_sys) return false;   /* чужий апарат — не наша справа */
    if (tcomp == 0)     return true;    /* усім вузлам мого апарата     */
    return tcomp == my_comp;            /* точно мені                   */
}
