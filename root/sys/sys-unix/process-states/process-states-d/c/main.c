DEFINE_WAIT(wait);
int ret = 0;

for (;;) {
    /* 1. стати в чергу об'єкта І одразу оголосити свій стан */
    prepare_to_wait(sk_sleep(sk), &wait, TASK_INTERRUPTIBLE);

    /* 2. перевірити умову ПІСЛЯ оголошення стану */
    if (skb_queue_len(&sk->sk_receive_queue) > 0)
        break;                       /* дані вже прийшли — спати нема потреби */

    if (signal_pending(current)) {   /* прийшов сигнал — виходимо з помилкою */
        ret = -ERESTARTSYS;
        break;
    }

    /* 3. власне сон: сюди керування більше не повернеться,
       поки задачу хтось не переведе назад у TASK_RUNNING */
    schedule();
}
finish_wait(sk_sleep(sk), &wait);    /* вийти з черги, стан = TASK_RUNNING */
