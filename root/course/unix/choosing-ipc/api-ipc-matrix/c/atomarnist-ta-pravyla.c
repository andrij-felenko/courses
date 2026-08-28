#include <mqueue.h>
#include <stdio.h>
#include <fcntl.h>

void configure_queue(void) {
    struct mq_attr attr;
    attr.mq_flags = 0;             /* Блокуючий режим */
    attr.mq_maxmsg = 10;           /* Максимум 10 повідомлень у черзі */
    attr.mq_msgsize = 2048;        /* Максимальний розмір одного повідомлення */
    attr.mq_curmsgs = 0;

    mqd_t mq = mq_open("/telemetry_q", O_CREAT | O_RDWR, 0600, &attr);
    if (mq == (mqd_t)-1) {
        perror("mq_open");
        return;
    }
    mq_close(mq);
}
