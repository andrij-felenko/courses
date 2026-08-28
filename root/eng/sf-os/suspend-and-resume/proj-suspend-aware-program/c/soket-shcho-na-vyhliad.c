#include <netinet/in.h>
#include <netinet/tcp.h>
#include <sys/socket.h>

static int64_t answer_due_ns;          /* 0 — запиту в польоті немає */

static void set_link_deadline(int fd, unsigned ms)
{
    setsockopt(fd, IPPROTO_TCP, TCP_USER_TIMEOUT, &ms, sizeof ms);
}

static void probe_link(int fd)
{
    static const char ping[] = "PING\n";
    ssize_t k = write(fd, ping, sizeof ping - 1);
    if (k < 0 && errno != EAGAIN) {
        reconnect();                   /* тут смерть уже очевидна */
        return;
    }
    /* Байти щонайбільше лягли у власний буфер відправлення —
       чекаємо не на них, а на відповідь. */
    answer_due_ns = now_ns(CLOCK_BOOTTIME) + 5LL * 1000000000LL;
}
