#ifndef LINK_H
#define LINK_H

#include <netinet/in.h>
#include <stdint.h>
#include <sys/socket.h>

#include <common/mavlink.h>

/* Зворотний зв'язок, без якого уставки надсилати наосліп не можна. */
typedef struct {
    int      have_heartbeat;
    uint64_t heartbeat_us;
    uint8_t  base_mode;
    uint32_t custom_mode;
    uint8_t  system_status;

    int      have_position;
    uint64_t position_us;
    float    x, y, z;          /* LOCAL_POSITION_NED, м */
    float    vx, vy, vz;       /* м/с */

    int      have_attitude;
    float    roll, pitch, yaw;             /* рад */
    float    rollspeed, pitchspeed, yawspeed;

    int      have_estimator;
    uint16_t estimator_flags;  /* ESTIMATOR_STATUS.flags */
} telemetry_t;

typedef struct {
    int                fd;
    struct sockaddr_in peer;
    socklen_t          peer_len;
    int                peer_known;

    uint8_t sys_id, comp_id;         /* наші ідентифікатори */
    uint8_t target_sys, target_comp; /* автопілота */

    telemetry_t tlm;

    int      ack_valid;
    uint16_t ack_command;
    uint8_t  ack_result;

    uint64_t our_heartbeat_us;
} link_t;

uint64_t now_us(void);

int  link_open(link_t *l, uint16_t local_port);
void link_close(link_t *l);

/* Надсилання можливе лише після того, як з'ясовано адресу автопілота
   з першого прийнятого кадру. */
int  link_send(link_t *l, const mavlink_message_t *msg);

/* Читає й розбирає все, що є в сокеті; timeout_ms стосується лише
   першого очікування. Повертає кількість зібраних повідомлень або -1. */
int  link_poll(link_t *l, int timeout_ms);

int  link_wait_heartbeat(link_t *l, int timeout_ms);
int  link_heartbeat_tick(link_t *l);   /* власний HEARTBEAT, не частіше 1 Гц */

int  link_command(link_t *l, uint16_t command, const float params[7], uint8_t confirmation);
int  link_take_ack(link_t *l, uint16_t command, uint8_t *result);

const char *mav_result_name(uint8_t result);

#endif /* LINK_H */
