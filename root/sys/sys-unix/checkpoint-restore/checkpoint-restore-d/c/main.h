int on = 1;
setsockopt(fd, SOL_TCP, TCP_REPAIR, &on, sizeof(on));

/* повернути номер послідовності, з яким партнер уже погодився */
int queue = TCP_SEND_QUEUE;
setsockopt(fd, SOL_TCP, TCP_REPAIR_QUEUE, &queue, sizeof(queue));
setsockopt(fd, SOL_TCP, TCP_QUEUE_SEQ, &send_seq, sizeof(send_seq));

/* номери ставлять до connect(); у режимі ремонту він не шле SYN,
   а одразу дає стан ESTABLISHED */
connect(fd, &peer, sizeof(peer));

/* «надіслати» те, що лежало у черзі: у режимі ремонту дані
   не йдуть у мережу, а кладуться назад у чергу сокета */
send(fd, unacked_bytes, unacked_len, 0);

on = 0;
setsockopt(fd, SOL_TCP, TCP_REPAIR, &on, sizeof(on));
/* з цієї миті сокет знову живий і продовжує розмову з того самого місця */
