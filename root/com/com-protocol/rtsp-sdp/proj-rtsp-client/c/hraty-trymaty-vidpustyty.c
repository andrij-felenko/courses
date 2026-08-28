int main(int argc, char **argv) {
    char host[128] = "", portstr[8] = "554";   /* типовий порт RTSP — 554 */
    char base[256], tr[128];
    struct addrinfo hints, *ai;
    struct sockaddr_in srv;
    rtsp_t r;
    track_t vid;
    int rtp = -1, rtcp = -1, cport = 0, srtp = 0, srtcp = 0, ping_gp = 1;
    unsigned seq0 = 0, ts0 = 0;
    const char *cb, *sp;
    time_t next_ping;

    if (argc < 2 || sscanf(argv[1], "rtsp://%127[^:/]:%7[0-9]", host, portstr) < 1) {
        fprintf(stderr, "usage: %s rtsp://host[:port]/path\n", argv[0]);
        return 2;
    }
    memset(&hints, 0, sizeof hints);
    hints.ai_family = AF_INET;
    hints.ai_socktype = SOCK_STREAM;
    if (getaddrinfo(host, portstr, &hints, &ai)) return 1;

    memset(&r, 0, sizeof r);
    r.timeout = 60;
    snprintf(r.base, sizeof r.base, "%s", argv[1]);
    r.ctl = socket(ai->ai_family, ai->ai_socktype, 0);
    if (r.ctl < 0 || connect(r.ctl, ai->ai_addr, ai->ai_addrlen)) return 1;
    memcpy(&srv, ai->ai_addr, sizeof srv);
    freeaddrinfo(ai);

    if (rtsp_send(&r, "OPTIONS", r.base, NULL) || rtsp_read(&r)) return 1;
    /* Public: перелічує методи камери — звідси й дізнаємось про GET_PARAMETER. */
    { const char *pub = hdr_find(r.hdr, "Public:");
      ping_gp = pub && strstr(pub, "GET_PARAMETER") != NULL; }

    if (rtsp_send(&r, "DESCRIBE", r.base, "Accept: application/sdp\r\n")
        || rtsp_read(&r)) return 1;
    if (r.status == 401) { fprintf(stderr, "потрібна автентифікація\n"); return 1; }
    if (r.status != 200) { fprintf(stderr, "DESCRIBE: %d\n", r.status); return 1; }

    /* Базова адреса для a=control: Content-Base, інакше Content-Location,
       інакше адреса запиту. */
    cb = hdr_find(r.hdr, "Content-Base:");
    if (!cb) cb = hdr_find(r.hdr, "Content-Location:");
    if (!cb || sscanf(cb, "%255[^\r\n]", base) != 1)
        snprintf(base, sizeof base, "%s", r.base);

    if (sdp_track(r.body, "video", base, &vid)) return 1;
    printf("video: pt=%d %s/%d Гц, control=%s\n",
           vid.pt, vid.codec, vid.clock, vid.control);

    if (bind_pair(&rtp, &rtcp, &cport)) return 1;
    snprintf(tr, sizeof tr,
             "Transport: RTP/AVP;unicast;client_port=%d-%d\r\n", cport, cport + 1);
    if (rtsp_send(&r, "SETUP", vid.control, tr) || rtsp_read(&r)) return 1;
    if (r.status != 200) { fprintf(stderr, "SETUP: %d\n", r.status); return 1; }
    parse_session(&r);
    sp = hdr_find(r.hdr, "Transport:");
    if (sp && (sp = strstr(sp, "server_port=")) != NULL)
        sscanf(sp, "server_port=%d-%d", &srtp, &srtcp);

    if (rtsp_send(&r, "PLAY", base, "Range: npt=0.000-\r\n") || rtsp_read(&r)) return 1;
    parse_rtp_info(r.hdr, vid.control, &seq0, &ts0);
    printf("сеанс %s, timeout=%d с, опора seq=%u rtptime=%u\n",
           r.session, r.timeout, seq0, ts0);

    /* Поштовх у бік камери з нашого порту — щоб відкрилося відображення. */
    if (srtp) {
        srv.sin_port = htons((unsigned short) srtp);
        for (int i = 0; i < 2; i++)
            sendto(rtp, "", 0, 0, (struct sockaddr *) &srv, sizeof srv);
    }

    next_ping = time(NULL) + r.timeout / 2;
    for (;;) {
        unsigned char pkt[2048];
        struct pollfd pf;
        long ms = (long) (next_ping - time(NULL)) * 1000;
        pf.fd = rtp; pf.events = POLLIN; pf.revents = 0;
        if (poll(&pf, 1, ms > 0 ? (int) ms : 0) > 0 && (pf.revents & POLLIN)) {
            ssize_t n = recv(rtp, pkt, sizeof pkt, 0);
            if (n >= 12)
                printf("RTP seq=%u ts=%u pt=%u len=%zd\n",
                       (unsigned) (pkt[2] << 8 | pkt[3]),
                       (unsigned) (pkt[4] << 24 | pkt[5] << 16 | pkt[6] << 8 | pkt[7]),
                       (unsigned) (pkt[1] & 0x7f), n);
        }
        if (time(NULL) >= next_ping) {
            if (rtsp_send(&r, ping_gp ? "GET_PARAMETER" : "OPTIONS", base, NULL)
                || rtsp_read(&r)) break;
            if (r.status >= 400 && ping_gp) {            /* камера не вміє — запасний хід */
                ping_gp = 0;
                if (rtsp_send(&r, "OPTIONS", base, NULL) || rtsp_read(&r)) break;
            }
            next_ping = time(NULL) + r.timeout / 2;
        }
    }

    rtsp_send(&r, "TEARDOWN", base, NULL);
    rtsp_read(&r);
    close(rtp); close(rtcp); close(r.ctl);
    return 0;
}
