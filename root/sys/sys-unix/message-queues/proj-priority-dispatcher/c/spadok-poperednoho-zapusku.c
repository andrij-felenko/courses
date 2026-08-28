/* Стартове вичерпування: термінові з минулого життя відкидаємо, рутинні переносимо
   на полицю (shelf_put — кільцевий буфер на вісім записів, його код нижче). */
static void carry_over(mqd_t q, char *buf, size_t cap)
{
    long dropped = 0, kept = 0, spilled = 0;

    for (;;) {
        unsigned prio;
        ssize_t n = mq_receive(q, buf, cap, &prio);
        if (n == -1) {
            if (errno == EINTR)  continue;
            if (errno == EAGAIN) break;                /* порожньо — усе розібрано */
            perror("mq_receive"); exit(1);
        }
        if (prio >= PRIO_URGENT)                                 dropped++;
        else if (shelf_put(&routine, prio, buf, (size_t)n))      kept++;
        else                                                     spilled++;
    }
    fprintf(stderr, "старт: відкинуто %ld термінових, %ld рутинних; перенесено %ld\n",
            dropped, spilled, kept);
}
