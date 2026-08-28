/* дескриптор створено як timerfd_create(CLOCK_REALTIME, TFD_NONBLOCK | TFD_CLOEXEC) */
static void cal_arm(int fd)
{
    time_t now = time(NULL);
    struct tm t;
    localtime_r(&now, &t);
    t.tm_hour = 3; t.tm_min = 0; t.tm_sec = 0;
    t.tm_isdst = -1;                       /* перехід на літній час хай визначає mktime */
    time_t at = mktime(&t);
    if (at <= now) { t.tm_mday += 1; t.tm_isdst = -1; at = mktime(&t); }

    struct itimerspec its = { .it_value = { .tv_sec = at } };
    timerfd_settime(fd, TFD_TIMER_ABSTIME | TFD_TIMER_CANCEL_ON_SET, &its, NULL);
}

static void cal_ready(int fd)
{
    uint64_t ticks;
    if (read(fd, &ticks, sizeof ticks) == (ssize_t)sizeof ticks)
        rotate_daily();
    else if (errno == EAGAIN)
        return;                            /* нічого не сталося — і переозброювати нічого */
    cal_arm(fd);                           /* і після роботи, і після ECANCELED */
}
