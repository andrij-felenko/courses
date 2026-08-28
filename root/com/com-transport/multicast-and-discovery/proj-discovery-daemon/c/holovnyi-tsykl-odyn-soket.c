int main(int argc, char **argv)
{
    if (argc < 3) { fprintf(stderr, "вжиток: %s <ім'я> <порт-послуги>\n", argv[0]); return 2; }
    snprintf(me.name, sizeof me.name, "%s", argv[1]);
    me.port = (uint16_t)atoi(argv[2]);
    me.caps = 1;
    if (load_identity(STATE_PATH) < 0) { perror("тотожність"); return 1; }

    struct sigaction sa;
    memset(&sa, 0, sizeof sa);
    sa.sa_handler = on_signal;            /* без SA_RESTART: poll має вийти з EINTR */
    sigaction(SIGINT,  &sa, NULL);
    sigaction(SIGTERM, &sa, NULL);

    memset(&group, 0, sizeof group);
    group.sin_family = AF_INET;
    group.sin_port   = htons(DISC_PORT);
    inet_pton(AF_INET, DISC_GROUP, &group.sin_addr);

    sock = open_socket();
    if (sock < 0) { perror("сокет"); return 1; }
    nifs = join_all(sock, ifs, MAX_IFS);
    if (nifs <= 0) { fprintf(stderr, "жодного придатного інтерфейсу\n"); return 1; }

    srand((unsigned)(now_ms() ^ (uint64_t)getpid()));
    t_announce = now_ms();                /* оголоситися негайно, не чекаючи періоду */
    send_query(now_ms());                 /* і одразу спитати, хто вже тут */
    uint64_t t_rescan = now_ms() + RESCAN_MS;

    while (!stop) {
        uint64_t t = now_ms();
        uint64_t due = t_announce;
        if (t_answer && t_answer < due) due = t_answer;
        if (t_rescan < due) due = t_rescan;
        for (int i = 0; i < npeers; i++) {
            if (peers[i].probe_ms   < due) due = peers[i].probe_ms;
            if (peers[i].expires_ms < due) due = peers[i].expires_ms;
        }
        int wait = due > t ? (int)(due - t) : 0;

        struct pollfd pfd;
        pfd.fd = sock; pfd.events = POLLIN; pfd.revents = 0;
        int r = poll(&pfd, 1, wait);
        if (r > 0) receive_one();
        else if (r < 0 && errno != EINTR) break;

        t = now_ms();
        if (t >= t_announce) {
            announce(REC_TTL_S, PKT_ANNOUNCE);
            t_announce = t + jittered(ANN_PERIOD_S);
        }
        if (t_answer && t >= t_answer) {
            if (answered_ms <= asked_ms) announce(REC_TTL_S, PKT_ANNOUNCE);
            t_answer = 0;                    /* або надіслано, або скасовано */
        }
        probe_due(t);
        sweep(t);
        if (t >= t_rescan) {                 /* інтерфейси з'являються й зникають */
            nifs = join_all(sock, ifs, MAX_IFS);
            t_rescan = t + RESCAN_MS;
        }
    }

    announce(0, PKT_BYE);                    /* прощання: час життя нуль */
    close(sock);
    return 0;
}
