#include <mqueue.h>
#include <iostream>
#include <fcntl.h>
#include <system_error>

void configure_queue() {
    struct mq_attr attr{};
    attr.mq_flags = 0;
    attr.mq_maxmsg = 10;
    attr.mq_msgsize = 2048;

    mqd_t mq = ::mq_open("/telemetry_q", O_CREAT | O_RDWR, 0600, &attr);
    if (mq == (mqd_t)-1) {
        throw std::system_error(errno, std::generic_category(), "mq_open failed");
    }
    ::mq_close(mq);
}
