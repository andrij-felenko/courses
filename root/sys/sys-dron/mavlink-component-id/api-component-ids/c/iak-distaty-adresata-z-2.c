#include <mavlink.h>
#include <stdio.h>

static void show(uint32_t msgid, const char *name)
{
    const mavlink_msg_entry_t *e = mavlink_get_msg_entry(msgid);
    if (!e) { printf("%-14s немає в таблиці цього діалекту\n", name); return; }

    printf("%-14s len %2u…%2u  crc_extra %3u  ",
           name, e->min_msg_len, e->max_msg_len, e->crc_extra);

    if (e->flags & MAV_MSG_ENTRY_FLAG_HAVE_TARGET_SYSTEM)
        printf("target_system@%u ", e->target_system_ofs);
    if (e->flags & MAV_MSG_ENTRY_FLAG_HAVE_TARGET_COMPONENT)
        printf("target_component@%u", e->target_component_ofs);
    if (!e->flags)
        printf("адресата немає");
    putchar('\n');
}

int main(void)
{
    show(MAVLINK_MSG_ID_COMMAND_LONG, "COMMAND_LONG");
    show(MAVLINK_MSG_ID_ATTITUDE,     "ATTITUDE");
    return 0;
}
