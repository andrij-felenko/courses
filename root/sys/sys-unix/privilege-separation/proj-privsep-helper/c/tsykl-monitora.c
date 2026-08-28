static void monitor(int sock)
{
    enum { ST_HELLO, ST_AUTHED, ST_SPENT } st = ST_HELLO;
    int tries = 0;
    char user[MAX_USER] = "";
    uid_t uid = 0; gid_t gid = 0;
    struct req rq;

    for (;;) {
        if (recv_req(sock, &rq) != REQ_OK) break;   /* EOF або будь-яка дивина */

        if (rq.op == OP_AUTH) {
            if (st != ST_HELLO || ++tries > 3) break;
            if (!pick_user(&rq, user, &uid, &gid)) { send_resp(sock, 1, -1); continue; }
            if (check_password(user, rq.pw, rq.pw_len)) {
                st = ST_AUTHED;
                send_resp(sock, 0, -1);
            } else {
                send_resp(sock, 1, -1);
            }
        } else if (rq.op == OP_LOGFD) {
            if (st != ST_AUTHED) break;             /* до автентифікації — ні */
            int fd = open_session_log(uid);
            if (fd < 0) { send_resp(sock, 1, -1); continue; }
            send_resp(sock, 0, fd);
            close(fd);                              /* своя копія моніторові не потрібна */
            st = ST_SPENT;                          /* удруге теж ні */
        } else {
            break;                                  /* невідома дія — розмова закінчена */
        }
    }
    close(sock);
}
