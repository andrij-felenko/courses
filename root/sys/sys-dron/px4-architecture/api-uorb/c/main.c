#include <uORB/uORB.h>
#include <uORB/topics/vehicle_attitude.h>
#include <drivers/drv_hrt.h>

/* ── видавець ─────────────────────────────────────────── */
struct vehicle_attitude_s att = {0};        /* {0} обов'язково: сміття в невживаних полях поїде на шину */
att.timestamp_sample = hrt_absolute_time();
att.q[0] = 1.0f;
att.timestamp = hrt_absolute_time();

orb_advert_t pub = orb_advertise(ORB_ID(vehicle_attitude), &att);
if (pub == NULL) {
    return PX4_ERROR;                        /* тема не оголосилася — далі публікувати нікуди */
}

att.timestamp = hrt_absolute_time();         /* далі — щоразу свіжа позначка */
orb_publish(ORB_ID(vehicle_attitude), pub, &att);

/* ── передплатник ─────────────────────────────────────── */
orb_sub_t sub = orb_subscribe(ORB_ID(vehicle_attitude));
if (!orb_sub_valid(sub)) {
    return PX4_ERROR;
}
orb_set_interval(sub, 10);                   /* не частіше ніж раз на 10 МІЛІсекунд */

px4_pollfd_struct_t fds[1];
fds[0].fd = sub;
fds[0].events = POLLIN;

if (px4_poll(fds, 1, 100) > 0) {             /* тайм-аут теж у мілісекундах */
    struct vehicle_attitude_s in;
    orb_copy(ORB_ID(vehicle_attitude), sub, &in);
    const hrt_abstime age = hrt_absolute_time() - in.timestamp_sample;
    /* age — вік виміру, а не час прийому; саме на ньому будують компенсацію запізнення */
}

orb_unsubscribe(sub);
