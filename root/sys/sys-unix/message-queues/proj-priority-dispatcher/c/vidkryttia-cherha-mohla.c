#define Q_NAME "/drived.cmd"

static mqd_t open_queue(long maxmsg, long msgsize)
{
    struct mq_attr want = { .mq_maxmsg = maxmsg, .mq_msgsize = msgsize };
    struct mq_attr have;
    mqd_t q;

    q = mq_open(Q_NAME, O_RDONLY | O_CREAT | O_EXCL | O_NONBLOCK, 0620, &want);
    if (q != (mqd_t)-1) return q;                 /* поле чисте */
    if (errno != EEXIST) return (mqd_t)-1;        /* EINVAL: maxmsg > msg_max
                                                     EMFILE: не влізли в rlimit */

    q = mq_open(Q_NAME, O_RDONLY | O_NONBLOCK);   /* attr тут не діяв би однаково */
    if (q == (mqd_t)-1) return (mqd_t)-1;
    if (mq_getattr(q, &have) == -1) { mq_close(q); return (mqd_t)-1; }

    if (have.mq_msgsize >= msgsize) {             /* чужа геометрія нам підходить */
        fprintf(stderr, "черга вже є: %ld × %ld\n",
                (long)have.mq_maxmsg, (long)have.mq_msgsize);
        return q;
    }

    /* слот вужчий за наш формат: розпорядження діставали б EMSGSIZE ще на відправленні */
    fprintf(stderr, "слот %ld замалий — створюю чергу заново\n", (long)have.mq_msgsize);
    mq_close(q);
    mq_unlink(Q_NAME);                            /* знімаємо ІМ'Я, а не об'єкт */
    return mq_open(Q_NAME, O_RDONLY | O_CREAT | O_EXCL | O_NONBLOCK, 0620, &want);
}
