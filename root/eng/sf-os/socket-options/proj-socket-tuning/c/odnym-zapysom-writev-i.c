/* до вже наявних включень додаються <sys/uio.h> (writev) і <time.h> (годинник) */

static long now_ms(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);   /* саме монотонний, див. нижче */
    return ts.tv_sec * 1000L + ts.tv_nsec / 1000000L;
}

/* УВАГА: змінює масив iov на місці — він робочий, а не константний.
   Повертає 0, або -1 і errno. -1 тут означає більше, ніж «не вдалося»:
   частина повідомлення вже пішла в дріт, тож потік байтів зіпсовано
   і з'єднання лишається тільки закрити. */
static int writev_all(int fd, struct iovec *iov, int cnt, long deadline)
{
    while (cnt > 0) {
        long left = deadline - now_ms();
        if (left <= 0) { errno = ETIMEDOUT; return -1; }

        struct timeval tv = { .tv_sec = left / 1000,
                              .tv_usec = (left % 1000) * 1000 };
        if (setsockopt(fd, SOL_SOCKET, SO_SNDTIMEO, &tv, sizeof tv) < 0)
            return -1;

        ssize_t n = writev(fd, iov, cnt);
        if (n < 0) {
            if (errno == EINTR) continue;     /* сигнал — не помилка */
            return -1;                        /* EAGAIN = час вичерпано */
        }

        /* writev міг узяти МЕНШЕ, ніж просили: викидаємо повністю віддані
           шматки, а перший недовіддений обрізаємо спереду. */
        while (cnt > 0 && (size_t)n >= iov->iov_len) {
            n -= (ssize_t)iov->iov_len;
            iov++;
            cnt--;
        }
        if (cnt > 0 && n > 0) {
            iov->iov_base = (char *)iov->iov_base + n;
            iov->iov_len -= (size_t)n;
        }
    }
    return 0;
}

int send_msg(int fd, const void *hdr, size_t hlen,
             const void *body, size_t blen, long budget_ms)
{
    struct iovec iov[2] = {
        { .iov_base = (void *)hdr,  .iov_len = hlen },
        { .iov_base = (void *)body, .iov_len = blen },
    };
    return writev_all(fd, iov, 2, now_ms() + budget_ms);
}
