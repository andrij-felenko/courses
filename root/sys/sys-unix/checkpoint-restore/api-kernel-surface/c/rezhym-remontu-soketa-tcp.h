/* ── знімок ────────────────────────────────────────────── */
int on = 1, q;
setsockopt(fd, SOL_TCP, TCP_REPAIR, &on, sizeof on);

q = TCP_SEND_QUEUE;
setsockopt(fd, SOL_TCP, TCP_REPAIR_QUEUE, &q, sizeof q);
socklen_t len = sizeof snd_seq;
getsockopt(fd, SOL_TCP, TCP_QUEUE_SEQ, &snd_seq, &len);
ssize_t unacked = recv(fd, sndbuf, sizeof sndbuf, MSG_PEEK | MSG_DONTWAIT);

struct tcp_repair_window win;
len = sizeof win;
getsockopt(fd, SOL_TCP, TCP_REPAIR_WINDOW, &win, &len);

/* ── відновлення ───────────────────────────────────────── */
fd = socket(AF_INET, SOCK_STREAM, 0);
setsockopt(fd, SOL_TCP, TCP_REPAIR, &on, sizeof on);

q = TCP_RECV_QUEUE;                       /* номери — до connect */
setsockopt(fd, SOL_TCP, TCP_REPAIR_QUEUE, &q, sizeof q);
setsockopt(fd, SOL_TCP, TCP_QUEUE_SEQ, &rcv_seq, sizeof rcv_seq);
q = TCP_SEND_QUEUE;
setsockopt(fd, SOL_TCP, TCP_REPAIR_QUEUE, &q, sizeof q);
setsockopt(fd, SOL_TCP, TCP_QUEUE_SEQ, &snd_seq, sizeof snd_seq);

bind(fd, &local, sizeof local);
connect(fd, &peer, sizeof peer);   /* SYN не летить: сокет одразу ESTABLISHED */

send(fd, unacked_bytes, unacked_len, 0);            /* назад у чергу відправлення */
q = TCP_RECV_QUEUE;
setsockopt(fd, SOL_TCP, TCP_REPAIR_QUEUE, &q, sizeof q);
send(fd, pending_in, in_len, 0);                    /* назад у чергу приймання */

setsockopt(fd, SOL_TCP, TCP_REPAIR_OPTIONS, opts, sizeof opts);
setsockopt(fd, SOL_TCP, TCP_REPAIR_WINDOW, &win, sizeof win);

on = 0;
setsockopt(fd, SOL_TCP, TCP_REPAIR, &on, sizeof on);  /* розмова триває далі */
