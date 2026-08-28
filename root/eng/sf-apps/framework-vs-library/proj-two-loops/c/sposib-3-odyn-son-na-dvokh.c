static int ep, tfd;                        // epoll і timerfd
static CURLM *multi;

/* libcurl: «за цим fd стеж ось на що» / «цей fd мені більше не потрібен» */
static int on_socket(CURL *easy, curl_socket_t s, int what, void *userp, void *sockp) {
    if (what == CURL_POLL_REMOVE) {
        epoll_ctl(ep, EPOLL_CTL_DEL, s, NULL);
        curl_multi_assign(multi, s, NULL);
        return 0;
    }
    struct epoll_event ev = {0};
    ev.data.fd = s;
    ev.events = ((what & CURL_POLL_IN)  ? EPOLLIN  : 0)
              | ((what & CURL_POLL_OUT) ? EPOLLOUT : 0);
    epoll_ctl(ep, sockp ? EPOLL_CTL_MOD : EPOLL_CTL_ADD, s, &ev);
    curl_multi_assign(multi, s, (void *)1);   // мітка «цей fd уже в наборі»
    return 0;
}

/* libcurl: «розбуди мене через ms мілісекунд» / «мій таймер більше не потрібен» */
static int on_timer(CURLM *m, long ms, void *userp) {
    struct itimerspec its = {0};              // усі нулі — таймер вимкнено
    if (ms >= 0) {
        if (ms == 0) ms = 1;                  // 0 = «негайно», а нуль у timerfd означає «вимкни»
        its.it_value.tv_sec  = ms / 1000;
        its.it_value.tv_nsec = (ms % 1000) * 1000000L;
    }
    timerfd_settime(tfd, 0, &its, NULL);
    return 0;
}
